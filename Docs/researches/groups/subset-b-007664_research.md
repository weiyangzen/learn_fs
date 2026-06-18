# subset-b-007664 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_lproc.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_lproc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_lvb.c -->
# sources/distributed-fs/lustre-release/lustre/mdt/mdt_lvb.c

## Purpose

`mdt_lvb.c` implements MDT `ldlm_valblock_ops` for LDLM lock value blocks. It provides quota-resource delegation to QMT handlers, Data-on-MDT `struct ost_lvb` allocation/update/fill/free, and layout-lock LVB filling from the file LOV xattr. These callbacks let LDLM carry small pieces of MDT-side state in lock replies and glimpse callbacks.

## Important APIs, Types, and Functions

- `mdt_lvbo` is the exported `struct ldlm_valblock_ops` instance wired into the MDT namespace.
- `mdt_lvbo_init()`, `mdt_lvbo_update()`, `mdt_lvbo_size()`, `mdt_lvbo_fill()`, and `mdt_lvbo_free()` are the LDLM entry points.
- `mdt_dom_lvb_alloc()` allocates `res->lr_lvb_data` as `struct ost_lvb`, sets `res->lr_lvb_len`, and marks `lvb_blocks` with `-ENODATA` until real data is available.
- `mdt_dom_lvb_is_valid()` treats a missing LVB or error-coded `lvb_blocks` as invalid.
- `mdt_dom_disk_lvbo_update()` refreshes DoM LVB fields from MDT object inode attributes.
- `mdt_dom_lvbo_update()` merges an optional RPC-supplied `RMF_DLM_LVB` and a backing inode refresh into the resource LVB.

## Control Flow

Quota resources are detected first in each operation with `IS_LQUOTA_RES(res)` and delegated to `qmt_hdls` when `mdt->mdt_qmt_dev` exists. Non-quota resources use MDT-local handling.

DoM update begins in `mdt_dom_lvbo_update()`. It skips update during OBD failover, allocates the LVB if needed, extracts the FID from the LDLM resource name, optionally swabs and merges an RPC-provided `struct ost_lvb`, then finds the MDT object and calls `mdt_dom_disk_lvbo_update()`. Both RPC and disk merge paths update size, times, and blocks under the resource lock, honoring `increase_only` unless a full refresh is requested.

`mdt_lvbo_size()` chooses the reply LVB length. Quota resources ask QMT, DoM locks return `sizeof(struct ost_lvb)`, layout locks return `mdt->mdt_max_mdsize`, and other locks return zero. DoM is preferred over layout when bits are combined because the file layout is not returned in combined open/getattr LVB replies, while glimpse ASTs use the DoM LVB.

`mdt_lvbo_fill()` handles three cases. Quota fill delegates to QMT. DoM fill ensures the LVB is valid by forcing an update if needed, copies resource LVB bytes under the resource lock, and returns the `ost_lvb` length. Layout fill only runs for granted layout locks: it resolves the FID, finds a local existing object, queries `XATTR_NAME_LOV` length with `mo_xattr_get(..., LU_BUF_NULL, ...)`, updates `mdt_max_mdsize` if the EA has grown beyond the known maximum, returns `-ERANGE` with the required length for undersized buffers, or fills the caller buffer with the LOV EA.

## State and Persistence Behavior

The primary state is `ldlm_resource.lr_lvb_data` and `lr_lvb_len`. For DoM locks this is a heap `struct ost_lvb` whose fields cache size, blocks, and timestamps derived from client RPC LVBs and the backing MDT object. The state is in-memory and associated with the LDLM resource lifetime; `mdt_lvbo_free()` releases it.

The disk-persistent source of truth for DoM values is the MDT object's inode attributes read through `mo_attr_get()`. Layout LVB content is read from the persistent LOV xattr, but this file only copies it into reply buffers; it does not modify it. The file can adjust `mdt->mdt_max_mdsize` at runtime when it discovers a larger layout EA.

## Dependencies and Integration Points

This file depends on LDLM resource/lock APIs, resource-name-to-FID extraction, MDT object lookup/lifetime helpers, `mo_attr_get()`, `mo_xattr_get()`, request capsule swabbing for `RMF_DLM_LVB`, QMT quota handlers, and MDT thread-local buffers. It integrates with open/getattr/glimpse paths that request DoM or layout ibits, and with the MDS PTLRPC service through the current `lu_env`.

## Risks and Edge Cases

- `mdt_dom_lvbo_update()` asserts that `lu_env_find()` succeeds. Calling LDLM update without an MDT-capable environment would trip assertions or return `-ENOMEM` through missing thread info.
- The `increase_only` merge policy can preserve stale larger values after truncation unless a caller explicitly requests a non-increase-only refresh.
- `mdt_lvbo_fill()` converts most negative errors other than `-ERANGE` to zero, which avoids protocol failures but can hide object/xattr lookup problems from callers.
- `mdt_max_mdsize` is updated without explicit serialization in this file when a larger EA is discovered.
- `mdt_dom_lvb_is_valid()` overloads `lvb_blocks` as an error marker. Future code must not treat all bit patterns in `lvb_blocks` as valid block counts before checking `OST_LVB_IS_ERR()`.

## Test Signals

Tests should exercise quota delegation with and without `mdt_qmt_dev`, DoM LVB first allocation and `-ENODATA` marker, RPC-supplied LVB merge with swabbing, disk refresh after truncation with `increase_only` both true and false, layout fill with exact/undersized/oversized buffers, `mdt_max_mdsize` growth, remote or missing object behavior, and `lvbo_free()` cleanup for quota and DoM resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_lvb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_mds.c -->
# sources/distributed-fs/lustre-release/lustre/mdt/mdt_mds.c

## Purpose

`mdt_mds.c` is the Lustre Metadata Service LU/OBD type wrapper that owns PTLRPC service registration for MDT-related portals. It allocates `struct mds_device`, starts regular MDT, readpage, object update, sequence controller/server, FLD, and MDT I/O services, exposes health checks and nodemap ioctl handling, and registers/unregisters the `LUSTRE_MDS_NAME` device type.

## Important APIs, Types, and Functions

- `struct mds_device` embeds `struct md_device` and stores service pointers plus `mds_health_mutex`.
- Module parameters `mds_num_threads`, `mds_cpu_bind`, `mds_max_io_threads`, `mds_io_cpu_bind`, `mds_io_num_cpts`, `mds_num_cpts`, `mds_rdpg_num_threads`, `mds_rdpg_cpu_bind`, `mds_rdpg_num_cpts`, and `mdt_enable_flr_ec` control service thread placement and feature advertisement.
- `mds_start_ptlrpc_service()` registers all PTLRPC services with tailored `ptlrpc_service_conf` instances.
- `mds_stop_ptlrpc_service()` unregisters all services and frees the MDT I/O CPT table.
- `ldlm_enqueue_hpreq_check()` and `mds_hpreq_handler()` special-case resent LDLM enqueue requests so already-granted locks can be handled as high-priority requests.
- `mds_device_alloc()`, `mds_device_fini()`, and `mds_device_free()` implement LU device lifecycle.
- `mds_health_check()` aggregates service health.
- `mds_iocontrol()` currently accepts only `OBD_IOC_NODEMAP`.
- `mds_mod_init()` and `mds_mod_exit()` register and unregister the OBD/LU type.

## Control Flow

Device allocation creates `struct mds_device`, initializes the embedded MD device, resolves the named OBD from the Lustre config, links `ld_obd` and `obd_lu_dev`, registers lprocfs entries, initializes the health mutex, and calls `mds_start_ptlrpc_service()`. Any failure unwinds lprocfs setup, services, and allocated memory.

`mds_start_ptlrpc_service()` repeatedly populates a static `ptlrpc_service_conf` and calls `ptlrpc_register_service()`. The regular MDT service uses `MDS_REQUEST_PORTAL` and `MDC_REPLY_PORTAL`, dispatches to `tgt_request_handle()`, prints through `target_print_req()`, and uses `mds_hpreq_handler()`. Readpage uses `MDS_READPAGE_PORTAL`. OUT uses `OUT_PORTAL` and `OSC_REPLY_PORTAL`. Sequence controller/server and FLD use their own portals and smaller other-thread pools. The MDT I/O service uses OST-style I/O buffer sizing on `MDS_IO_PORTAL`, initializes/destroys I/O threads with `tgt_io_thread_init()`/`tgt_io_thread_done()`, and uses `tgt_hpreq_handler()`.

Before the I/O service registration, the code may build `mdt_io_cptable`: when the global CPT table has one CPT but the node mask has multiple NUMA nodes, it allocates a new table with one CPT per node for I/O service node affinity. If allocation or node insertion fails, it logs and falls back to the default CPT pattern.

Stopping services is serialized under `mds_health_mutex`: each non-NULL service pointer is unregistered and nulled. After unlocking, `mdt_io_cptable` is freed if present.

## State and Persistence Behavior

This file persists no on-disk metadata. Its state is live kernel service state: PTLRPC service registrations, thread pools, portal bindings, CPT affinity tables, OBD/LU type registration, and module parameters. The `mdt_enable_flr_ec` parameter is writable at module scope and influences advertised FLR EC behavior elsewhere.

Health state is derived from active service objects. Device finalization unregisters services before lproc cleanup; device free finalizes the embedded MD device and frees memory.

## Dependencies and Integration Points

The file depends on PTLRPC service infrastructure, target request dispatch (`tgt_request_handle`, `target_print_req`, high-priority handlers), LDLM lock lookup for resend prioritization, LU device type registration, OBD class lookup and type registration, lprocfs OBD setup/cleanup, libcfs CPT/NUMA helpers, nodemap server ioctl handling, and MDT thread-local key initialization through `LU_TYPE_INIT_FINI(mds, &mdt_thread_key)`.

It is the integration point that makes higher-level MDT request handlers reachable over LNet portals; request opcode routing after service receive is handled in target/MDT layers outside this file.

## Risks and Edge Cases

- `mds_start_ptlrpc_service()` uses a static local `ptlrpc_service_conf` but reassigns it before each registration. This is safe only because registration copies or consumes the data synchronously as expected.
- Partial service startup failure relies on `mds_stop_ptlrpc_service()` to unregister every service that succeeded earlier. Any new service added to startup must be added to stop and health checks.
- `ldlm_enqueue_hpreq_check()` initializes the request capsule and looks up the first client lock handle only for `MSG_RESENT` without `MSG_REPLAY`; mistakes here can change resend priority and recovery latency.
- The MDT I/O CPT-table fallback logs warnings but continues. Performance/NUMA locality can silently degrade.
- `mds_health_check()` assumes all service pointers are valid enough for `ptlrpc_service_health_check()` after allocation; stop/start races are guarded by `mds_health_mutex`.

## Test Signals

Tests should cover successful registration of all services, injected registration failures at each service and full unwind, health check aggregation, module parameter propagation into thread configs, I/O CPT table creation/fallback on multi-node single-CPT systems, LDLM resend high-priority detection for granted and non-granted locks, nodemap ioctl acceptance/rejection, and lifecycle ordering of alloc/fini/free/mod init/exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_mds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_open.c -->
# sources/distributed-fs/lustre-release/lustre/mdt/mdt_open.c

## Purpose

`mdt_open.c` implements MDT open, create-on-open, by-FID open, cross-reference open, open-lock/lease handling, per-export open-handle tracking, replay reconstruction for open, close handling, HSM release, layout swap/merge/split/resync close intents, Size-on-MDS updates, dirty-flag updates, and operation counters. It is one of the central metadata request files for translating client open/close RPCs into MDD/LOD object operations and LDLM locks.

## Important APIs, Types, and Functions

- `struct mdt_file_data` lifecycle helpers: `mdt_mfd_new()`, `mdt_open_handle2mfd()`, `mdt_mfd_free()`, `mdt_mfd_set_mode()`, `mdt_mfd_close()`, and `mdt_close_internal()`.
- Write/execute exclusion helpers: `mdt_write_get()`, `mdt_write_put()`, `mdt_write_deny()`, `mdt_write_allow()`, and `mdt_write_read()`, operating on `mot_write_count`.
- Transaction/replay helper `mdt_empty_transno()` creates or assigns transaction numbers and updates in-memory `lsd_client_data` last-reply fields.
- Open helpers: `mdt_create_data()`, `mdt_prep_ma_buf_from_rep()`, `mdt_mfd_open()`, `mdt_finish_open()`, `mdt_open_by_fid()`, `mdt_open_by_fid_lock()`, `mdt_cross_open()`, `mdt_lock_root_xattr()`, `mdt_open_lock_mode()`, `mdt_pack_attr_acl()`, and public `mdt_reint_open()`.
- Lock helpers: `mdt_object_open_lock()` and `mdt_object_open_unlock()` handle normal open locks, leases, layout locks, DoM ibits, and readdir update locks.
- Recovery entry `mdt_reconstruct_open()` rebuilds replies from last-reply data and may rerun by-FID or regular open paths.
- HSM/layout close helpers: `mdt_hsm_release_allow()`, `mdt_orphan_open()`, `mdt_hsm_set_released()`, `mdt_get_lmm_gen()`, `mdt_hsm_release()`, `mdt_close_handle_layouts()`, and `mdt_close_resync_done()`.
- Public close entry `mdt_close()` unpacks close data, handles resends, closes the handle, fixes replies, and records counters.

## Control Flow

Open starts in `mdt_reint_open()`. The handler validates EA presence for flags that claim client-provided EA/objects, rejects write opens for read-only clients, blocks unauthorized `.lustre/fid` by-FID operation, then dispatches cross-ref, replay, or explicit by-FID opens before the normal name-based path.

The normal path validates the name, locks root xattr if remote root defaults may be needed, finds and version-checks the parent, enforces fscrypt/resource-id/encryption policy, chooses parent lock mode with `mdt_open_lock_mode()`, takes a parent lock, and performs lookup. Missing names require `MDS_OPEN_CREAT`, non-read-only export, and possibly a retry with a write parent lock to close unlink/create races. Creation allocates a new child object with the requested FID, saves VBR versions, sets create disposition, copies the configured job xattr name, calls `mdo_create()`, and then fetches child attributes. Existing children handle remote-object referral, early `O_DIRECTORY` checks, complex attr/HSM fetch, security/encryption context packing, optional open/layout/DoM lock acquisition, and `mdt_finish_open()`.

`mdt_finish_open()` packs inode attributes into `RMF_MDT_BODY`, rejects unsupported mirrored/overstriped layouts for older clients, optionally packs ACLs, suppresses open handles for symlinks and special nodes when requested, enforces `O_EXCL|O_CREAT`, checks directory/open flag mismatches, handles resent opens by finding an existing `mfd` with the same XID, then calls `mdt_mfd_open()`. `mdt_mfd_open()` may create missing LOV data, updates reply EA size flags, enforces write-vs-exec exclusion, calls `mo_open()`, allocates and links `mfd`, takes an MDT object reference, updates open/lease counts, handles replay orphan handles, returns the open cookie, and records an empty transaction number for reply reconstruction.

Close starts in `mdt_close()`. It unpacks close/SOM data, packs a minimal reply, checks resend reconstruction, initializes `ma` buffers, calls `mdt_close_internal()` to resolve and remove the open handle, and then `mdt_mfd_close()`. `mdt_mfd_close()` handles close intents first: HSM release, layout merge/split/swap, or resync done. It then updates LSOM, releases write/exec exclusion, writes close time updates, adds dirty flags, decrements open counts, handles last unlink cleanup, calls `mo_close()`, discards DoM data if needed, decrements lease count, frees the `mfd`, and drops the object reference. `mdt_close()` assigns an empty transno unless the handle was stale, fixes client compatibility in the reply, and records the close counter.

HSM release and layout close intents take write access to `mot_open_sem`, cancel the server-side lease, check whether the lease was already broken, acquire exclusive layout/xattr locks, and mutate layouts through `mo_swap_layouts()`, `mo_xattr_set()` with merge/split flags, or `mdt_layout_change()`. HSM release creates a volatile orphan object, marks layouts as released, sets HSM xattrs, swaps layouts, updates SOM, and reports intent execution in the reply.

## State and Persistence Behavior

The main live state is per-export open handles in `med_open_head` plus the global class handle hash. Each `mfd` owns a reference to the opened `mdt_object`, the open cookie, old replay cookie, XID, owner export, and open flags. Object-level state includes `mot_open_count`, `mot_lease_count`, `mot_write_count`, `mot_open_sem`, LOV-created flag, SOM mutex/state, cached root attr flag, and DoM discard decisions.

Persistent metadata changes are delegated to lower layers: `mdo_create()`, `mdo_create_data()`, `mdo_unlink()`, `mo_open()`, `mo_close()`, `mo_attr_set()`, `mo_xattr_set()`, `mo_swap_layouts()`, and `mdt_layout_change()`. Replay state is maintained through transaction numbers in replies and in-memory `lsd_client_data` fields (`lcd_last_transno`, `lcd_last_xid`, close variants, result, data, and pre-versions). `mdt_empty_transno()` is critical for operations that need reconstructable reply state even when no lower transaction was otherwise generated.

Close updates may persist atime/mtime/ctime, LSOM/SOM, HSM attributes, LOV layout changes, dirty flags, and last-unlink cleanup. Create failure after a child was created attempts to unlink the child unless it was volatile, where an orphan may remain until reboot.

## Dependencies and Integration Points

This file integrates with MDT internal request records, request capsules, LDLM inodebit locks, target VBR/replay helpers, nodemap/resource-id checks, encryption/fscrypt context packing, ACL packing, HSM state, LOD/MDD object operations, lprocfs counters from `mdt_lproc.c`, DoM helpers from other MDT files, and recovery reconstruction in `mdt_recovery.c`.

Client protocol compatibility is handled through connect flags: ACL, FLR, overstriping, read-only, open readdir, layout, DoM, NODEVOH, jobstats, DNE, and PCC-related flags. The file also uses many fault-injection points under `OBD_FAIL_MDS_*`, which are important integration hooks for Lustre recovery tests.

## Risks and Edge Cases

- Open replay and resend handling is subtle: handles can be found by current cookie, old replay cookie, or XID, and `mdt_empty_transno()` must keep last-reply data coherent without advancing committed state incorrectly.
- Lock return policy in `mdt_object_open_unlock()` depends on requested ibits, result code, remote-open sentinel, and whether useful open/layout/DoM bits were granted. Small changes can leak locks or fail to return needed client locks.
- Write/execute exclusion relies on signed `mot_write_count` where positive means writers and negative means exec deny; every failure path must balance get/put or deny/allow.
- HSM release and layout operations intentionally continue to close even after intent errors. Callers must inspect reply flags/status to distinguish close success from intent failure.
- `mdt_get_lmm_gen()` appears to call `le32_to_cpu(lmm->lmm_magic == LOV_MAGIC_COMP_V1)`, which compares before endian conversion; this is suspicious and should be reviewed because it can affect PCC/HSM layout version reporting.
- Volatile create/open failure can leave an orphan in PENDING until reboot, explicitly logged by the code.
- Parent lock mode starts with a lookup to decide PR vs PW for create; races force retry, so tests must cover create/unlink interleavings.

## Test Signals

High-value tests include open existing, create-on-open, `O_EXCL`, `O_DIRECTORY`, symlink/special NODEVOH, by-FID, cross-ref, remote-open referral, fscrypt/resource-id rejection, unsupported FLR/overstriping client rejection, ACL hint on `-EACCES`, replay after create, resent open same XID, old-cookie replay cleanup, write-vs-exec exclusion, lease acquisition conflicts, DoM/layout open lock return, parent lock retry on create race, close stale handle, close with time/SOM/dirty updates, last-unlink close, HSM release success/failure/already released, layout swap/merge/split/resync done, read-only export failures, and fault-injection cases for pack/net reply loss.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_open.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_recovery.c -->
# sources/distributed-fs/lustre-release/lustre/mdt/mdt_recovery.c

## Purpose

`mdt_recovery.c` contains MDT replay/reconstruction helpers. It restores transaction numbers, statuses, version data, disposition data, and lock references from target last-reply data so resent or replayed metadata operations can receive a reply consistent with the originally committed operation. It also has specialized reconstruction for create and setattr replies that need current/fake attributes in the response body.

## Important APIs, Types, and Functions

- `mdt_steal_ack_locks()` transfers saved locks from a matching outstanding reply state to the current resent request.
- `mdt_req_from_lrd()` restores request/reply transno, status, pre-versions, and last-reply opaque data from `struct tg_reply_data`.
- `mdt_reconstruct_generic()` is the common reconstructor for operations whose saved last-reply data is enough.
- `mdt_fake_ma()` creates a minimal `MA_INODE` attribute set with `LA_NLINK` and regular-file mode for objects that disappeared after commit.
- `mdt_reconstruct_create()` restores create replies and repacks object attributes, LMV size, and remote-MDT indications.
- `mdt_reconstruct_setattr()` restores setattr replies and repacks current or fake attributes.
- `reconstructors[REINT_MAX]` maps reint opcodes to reconstruction handlers, including `mdt_reconstruct_open()` implemented in `mdt_open.c`.
- `mdt_reconstruct()` is the dispatcher used by MDT reint replay paths.

## Control Flow

Generic reconstruction calls `mdt_req_from_lrd()`, which copies `lrd_transno` and `lrd_result` into the request, writes pre-operation versions into the reply, clears the transno when the original result was an error, writes reply transno/status, steals any ACK locks from an outstanding reply with the same XID/opcode, and returns `lrd_data` for opcode-specific interpretation.

`mdt_steal_ack_locks()` walks `exp_outstanding_replies` under `exp_lock`, finds a reply state with matching XID, logs opcode mismatch if present, removes it from the export list under the service-part reply lock, copies each saved lock into the new request with `ptlrpc_save_lock()`, clears the old reply state's lock count, and schedules the old difficult reply. If the export is already disconnected, it decrefs stolen locks and clears the new reply state's lock count so disconnected clients do not retain transaction locks.

Create reconstruction first restores last-reply data. If the saved status is success, it finds the child by the requested FID. Lookup failure evicts the client because the server cannot reconstruct a committed create reply. It fetches current attributes, prepares LMV reply buffers for directory LMV creates, fakes attributes if the object was destroyed after commit, handles remote-created objects by returning `OBD_MD_MDS` and `-EREMOTE` or `-EIO` for old clients, packs LMV size flags, and packs attrs into `RMF_MDT_BODY`.

Setattr reconstruction similarly restores last-reply data, finds the target object, evicts the client if lookup fails, fetches current attributes, fakes them on `-ENOENT`, packs them into the reply, and drops the object.

## State and Persistence Behavior

The persistent source for reconstruction is target last-reply data (`tg_reply_data`/`lsd_reply_data`) maintained by the target recovery layer and updated by operation handlers such as `mdt_empty_transno()`. This file consumes that data to rebuild volatile reply fields. It also manipulates outstanding reply state and LDLM lock references so transaction locks survive resends correctly.

It does not change filesystem metadata except indirectly by evicting clients when reconstruction invariants fail. Attribute data packed during reconstruction reflects current object state when possible; if the object was already unlinked after the original commit, the fake attribute response deliberately reports `nlink=0` so clients invalidate cached state.

## Dependencies and Integration Points

This file depends on MDT thread info, request capsules, target last-reply data, PTLRPC reply-state lists and difficult replies, LDLM lock save/decref helpers, MDT object lookup/lifetime, complex attribute fetch, body packing, DNE client compatibility checks, and `mdt_reconstruct_open()` from `mdt_open.c`. The dispatcher is tied to reint opcode values (`REINT_SETATTR`, `REINT_CREATE`, `REINT_OPEN`, etc.).

## Risks and Edge Cases

- `mdt_steal_ack_locks()` uses nested spinlocks over export and service reply state; lock ordering must remain consistent with PTLRPC reply handling.
- Opcode mismatch on a matching XID is logged but does not stop lock stealing. That preserves progress but could mask a serious client/server replay confusion.
- Reconstruction evicts the client when an object lookup for a supposedly committed create/setattr cannot be performed, because returning a fabricated success for an unknown FID would corrupt client recovery.
- Fake attributes are intentionally minimal. Clients must honor `nlink=0` and not treat the object as a fully valid regular file.
- The `reconstructors` table assumes every replayable opcode has a non-NULL handler; adding a new `REINT_*` without updating the table will hit `LASSERT()`.

## Test Signals

Tests should cover generic reconstruction of successful and failed operations, transno clearing on saved errors, version restoration, ACK-lock stealing on resent requests, disconnected export lock decref, create reconstruction for existing child, child deleted after commit, remote-created object with old/new DNE clients, create lookup failure eviction, setattr reconstruction with existing/deleted target, open reconstruction delegation, and table coverage for every replayable reint opcode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lustre-release/lustre/mdt/mdt_recovery.c -->
