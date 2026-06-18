# sources/distributed-fs/lustre-release/lustre/mdt/mdt_lproc.c

## Purpose

`mdt_lproc.c` implements the MDT-side sysfs/debugfs/lprocfs control and statistics surface. It publishes live administrative knobs for identity upcalls, root squash, nodemap resource-id checks, directory striping/restriping policy, DoM open-lock policy, checksum behavior, job xattr names, recovery timeouts, grant parameters, and per-operation counters. It also initializes and tears down MDT tunables and job/stat counters during target startup/shutdown.

The file is not request dispatch itself; it is the management and observability layer that mutates fields in `struct mdt_device`, `struct lu_target`, identity caches, and OBD statistics that are consumed by MDT open/reint/recovery paths elsewhere.

## Important APIs, Types, and Functions

- `display_rename_stats()`, `mdt_rename_stats_seq_show()`, `mdt_rename_stats_seq_write()`, and `lproc_mdt_attach_rename_seqstat()` implement a YAML-like debugfs report and reset path for rename-size histograms.
- `mdt_rename_counter_tally()` records rename latency counters and tallies source/target directory sizes for same-directory and cross-directory renames.
- `identity_*`, `identity_int_*`, `entry_expire_store()`, `acquire_expire_store()`, `flush_store()`, and `identity_info_store()` expose upcall-cache expiry, acquire timeout, executable path, flush, and downcall ingestion for external and internal identity caches.
- `mdt_evict_client_store()` extends normal client eviction with `nid:<nid>` handling and optional propagation to OST targets through `KEY_EVICT_BY_NID`.
- `commit_on_sharing_*`, `local_recovery_*`, `enable_resource_id_check_*`, `no_create_*`, `async_commit_count_*`, `sync_count_*`, `checksum_t10pi_enforce_*`, and `force_sync_store()` wire live MDT/target policy into sysfs attributes.
- `mdt_root_squash_seq_*` and `mdt_nosquash_nids_seq_*` expose root squash uid/gid and NID exception lists.
- `enable_cap_mask_*`, `MDT_ENABLE_GID_LUSTRE_RW_ATTR`, and `MDT_BOOL_RW_ATTR` generate policy toggles and GID controls for capabilities, remote/foreign/pinned directories, parallel rename, striped directory, HSM migration, strict SOM, DMV xattrs, and rename trylocks.
- `dom_lock_*`, `dir_split_count_*`, `dir_split_delta_*`, `max_mod_rpcs_in_flight_*`, and `job_xattr_*` expose DoM lock mode, directory auto-split thresholds, RPC concurrency, and job xattr naming.
- `ldebugfs_mdt_open_files_seq_open()` and `ldebugfs_mdt_print_open_files()` report open FIDs for a per-NID export.
- `mdt_counter_incr()` records MDT counters in device, per-NID, jobstats, and nodemap stats.
- `mdt_stats_counter_init()`, `mdt_tunables_init()`, and `mdt_tunables_fini()` own lifecycle of MDT lproc/debugfs stats and tunable registration.

## Control Flow

Startup calls `mdt_tunables_init()`, which assigns `mdt_groups` to the OBD ktype, registers OBD lproc/debugfs entries, initializes target and HSM coordinator tunables, creates `gss` and `exports` debugfs directories, allocates metadata stats, initializes MDT-specific counters after `LPROC_MD_LAST_OPC`, initializes jobstats, and attaches rename statistics. Shutdown calls `mdt_tunables_fini()`, which frees per-client stats, HSM tunables, target tunables, OBD lproc entries, MD stats, debugfs OBD stats, and jobstats.

Most attribute handlers follow the same pattern: recover the `struct obd_device` with `container_of(kobj, struct obd_device, obd_kset.kobj)`, convert to `struct mdt_device` through `mdt_dev(obd->obd_lu_dev)`, parse input with kernel helpers such as `kstrtobool()`, `kstrtoint()`, `kstrtouint()`, `kstrtoull()`, or `sysfs_memparse()`, validate bounds, then update a live field. Debugfs seq handlers usually receive either the OBD or MDT as private data and format current state into a `seq_file`.

Rename accounting begins in `mdt_rename_counter_tally()`: the generic rename latency counter is incremented, the source directory inode attributes are read with `mo_attr_get()`, an optional parallel-rename counter is incremented, and either same-directory or cross-directory histograms are updated. Cross-directory renames perform a second attribute read for the target directory before tallying target size.

Identity downcall handling is the most structured write path. `identity_info_store()` validates the fixed header, magic, permission count, and group count, reallocates a larger buffer when group data is present, copies the full payload from the sysfs buffer, and passes it to `upcall_cache_downcall()`.

## State and Persistence Behavior

State changed by this file is live kernel state, not standalone on-disk persistence. It mutates `mdt->mdt_identity_cache`, `mdt->mdt_identity_cache_int`, `mdt->mdt_squash`, `mdt->mdt_opts`, `mdt->mdt_lut`, `mdt->mdt_restriper`, `mdt->mdt_job_xattr`, `mdt->mdt_enable_cap_mask`, GID fields, policy booleans, and OBD/target counters. Some of those fields are later persisted indirectly by other target or backing-store code, but these handlers themselves are sysfs/debugfs front ends over active objects.

Counters persist only while the target instance is alive. `mdt_counter_incr()` fans a single event out to OBD metadata stats, per-NID stats, optional jobstats keyed by jobid, and nodemap stats. Rename histograms are protected internally by lprocfs histogram locks but the show path explicitly accepts racing samples.

Some writes are intentionally direct and not synchronized beyond the target field's primitive: booleans and counts are assigned directly, atomics are used for async/sync counts, `lut_cksum_t10pi_enforce` is protected by `lut_flags_lock`, and root-squash NID printing holds `rsi_lock`.

## Dependencies and Integration Points

This file depends on Lustre OBD, target, nodemap, identity upcall-cache, HSM coordinator, lprocfs, debugfs, LDLM/export, checksum, and capability helpers. It integrates with request paths through shared fields: DoM open behavior in `mdt_open.c` reads `mdt_opts.mo_dom_lock` and `mdt_dom_read_open`; open/create paths read `mdt_job_xattr`, `lut_no_create`, resource-id checking, remote/striped directory booleans, and strict SOM policy; rename paths call `mdt_rename_counter_tally()`; close paths and IO-like MDT paths call `mdt_counter_incr()`.

The debugfs open-files report walks export open-handle state maintained by `mdt_open.c` (`med_open_head`, `mfd_list`, `mfd_object`) under `med_open_lock`.

## Risks and Edge Cases

- Many sysfs stores directly mutate operational policy without a transaction or coordinated quiesce; concurrent request paths may observe changes immediately and partially relative to other tunables.
- `identity_info_store()` copies from a `const char *buffer` supplied by sysfs. Its two-pass variable-size parsing must remain aligned with the userspace downcall ABI or it can reject valid identity data or read incomplete payloads.
- `mdt_evict_client_store()` trims and splits the input in-place after assigning `tmpbuf = skip_spaces(buffer)`. This assumes the store buffer is mutable enough for `strsep()` use.
- `job_xattr_store()` restricts the post-namespace name to alphanumeric characters only and caps length tightly; new valid xattr naming schemes would need this validator updated.
- `enable_cap_mask_store()` accepts numeric or string masks but intersects with a locally built allow mask. Administrators may think unsupported capability bits were enabled when they were silently dropped.
- `dom_lock_store()` maps `always` to `trylock`, so the exposed mode vocabulary is wider than the behavior actually retained.
- Debugfs creation failures for optional directories are tolerated by setting pointers to `NULL`; later tooling must handle missing optional entries.

## Test Signals

Useful tests include sysfs parser tests for invalid booleans, negative expiry values, overlarge acquire timeouts, `max_mod_rpcs_in_flight` bounds, `job_xattr` namespace/name validation, `dir_split_count` memory suffixes, and `dom_lock` string/numeric compatibility. Runtime tests should verify rename histogram reset/tally output, per-NID open-file listing, identity upcall/downcall/flush behavior, NID eviction with and without OST propagation, nodemap stat increments, checksum enforcement locking, and tunable cleanup after target stop.
