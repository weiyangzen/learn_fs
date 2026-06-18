# Group Research: group_1420_openzfs_sources_cow_pools_openzfs_lib_libzfs_libzfs_sendrecv_c_sour_0c46cdfa08c9

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/cow-pools/openzfs`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/libzfs_sendrecv.c -->
# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs_sendrecv.c

This is the main userland implementation behind `zfs send` and `zfs receive` in libzfs. It bridges CLI-level send/receive flags, dataset traversal, stream metadata construction, resume-token handling, redaction-bookmark handling, property preservation, encryption-root fixups, and kernel `libzfs_core` send/receive ioctls.

Primary responsibilities:
- Build compound send stream headers containing filesystem, snapshot, property, hold, clone-origin, and encryption-root metadata.
- Generate full, incremental, recursive, replication, raw, redacted, saved, and resumable send streams.
- Estimate send sizes and report progress through a background progress thread using `lzc_send_progress()`.
- Decode and validate send resume tokens.
- Receive single or compound streams, including recursive replication streams.
- Reconcile local dataset topology with incoming stream topology using GUID matching, renames, destroys, promotions, and second-pass retries.
- Apply received properties, command-line `-o` overrides, `-x` exclusions, snapshot properties, and snapshot holds.
- Handle encryption constraints for raw sends, key material, encryption roots, clone origins, and keylocation restoration.
- Translate stream/kernel errors into libzfs errors with actionable auxiliary messages.

Important data structures:
- `progress_arg_t` carries the dataset handle, send fd, output formatting flags, progress mode, and expected size into the send progress thread.
- `fsavl_node_t` indexes snapshots by GUID in an AVL tree so stream/local metadata can be matched independently of names.
- `send_data_t` is used while walking source datasets to build the large send-header nvlist. It tracks recursive traversal state, from/to snapshot txgs, parent snapshot GUIDs, property/hold collection, flags, and optional snapshot filters.
- `send_dump_data_t` controls actual stream dumping after metadata collection. It tracks from/to snapshots, previous snapshot object ids, replication/doall state, feature flags, hold tags, debug nvlists, progress settings, output fd, and accumulated size.
- `guid_to_name_data_t` supports GUID lookup over datasets and bookmarks, including redaction bookmark matching.
- Small wrapper structs such as `zfs_send`, `zfs_send_one`, and `zfs_send_resume_impl` adapt internal callbacks for `lzc_send_wrapper()`.

Send-side flow:
- `gather_nvlist()` opens the source dataset and drives `send_iterate_fs()`.
- `send_iterate_fs()` recursively builds per-filesystem metadata keyed by filesystem GUID. It records names, clone origins, parent-from-snapshot GUIDs, dataset properties, encryption-root markers, snapshots, snapshot properties, and optional holds.
- `send_iterate_snap()` records snapshot GUIDs and collects snapshot properties/holds while enforcing from/to snapshot windows.
- `send_iterate_prop()` filters out read-only, inherited, unsupported, unknown, snapshot space-limit, and inappropriate properties before adding sendable property values.
- `fsavl_create()`, `fsavl_find()`, and `fsavl_destroy()` provide fast GUID lookup over collected stream metadata.
- `send_prelim_records()` writes a compound `DRR_BEGIN` header carrying packed nvlist metadata when replication/properties/holds require it, then writes a checksum-protected `DRR_END` for that header.
- `dump_snapshot()` sends one snapshot, deciding whether it is included, whether it is incremental from the previous accepted snapshot, whether clone-origin snapshots must be preserved, and which `LZC_SEND_FLAG_*` flags apply.
- `dump_filesystem()` validates source snapshots and iterates either the full snapshot range or just from/to snapshots.
- `dump_filesystems()` orders recursive replication sends so parent datasets and clone origins are sent before dependent children.
- `zfs_send_cb_impl()` is the main recursive send coordinator. It validates inputs, emits preliminary metadata, optionally performs a dry-run pass for size/holds, installs temporary holds for destructive safety, sends the stream payloads, and writes the final compound end record.
- Public `zfs_send()` wraps `zfs_send_cb_impl()` with `lzc_send_wrapper()`.

Single-stream and redacted send:
- `zfs_send_one_cb_impl()` handles one dataset/snapshot stream, including optional properties/holds/backup headers.
- `snapshot_is_before()` validates that an incremental source is actually earlier in the target timeline, following clone origins recursively.
- Redacted send validation ensures the requested redaction bookmark exists on the target snapshot’s dataset and has redaction-snapshot metadata.
- `zfs_send_one()` is the public wrapper.

Resume/saved send:
- `zfs_send_resume_token_to_nvlist()` decodes tokens of the form version/checksum/uncompressed-length/hex-compressed-payload, verifies Fletcher checksum, inflates with zlib, and unpacks the nvlist.
- `lzc_flags_from_sendflags()` and `lzc_flags_from_resume_nvl()` merge user-requested and token-preserved send features.
- Redaction helpers `get_bookmarks()`, `find_redact_pair()`, `find_redact_book()`, and GUID-array comparison functions find a complete redaction bookmark matching the resumed stream.
- `zfs_send_resume_impl_cb_impl()` validates token fields, resolves original to/from GUIDs to names, estimates size if needed, starts progress reporting, and calls `lzc_send_resume_redacted()`.
- `zfs_send_resume()` decodes the token and dispatches the resumed send.
- `zfs_send_saved()` uses a dataset’s `receive_resume_token`, optionally combines it with a supplied resume token position, and sends saved partially received state.

Progress and reporting:
- `zfs_send_progress()` calls `lzc_send_progress()`.
- `send_progress_thread()` uses signals/timers to poll bytes and block counts while a send or size estimate is active.
- `send_progress_thread_exit()` cancels and joins the progress thread and restores the parent signal mask.
- `send_print_verbose()` formats human-readable or parsable size/progress output.
- Progress can also update process title when `progressastitle` is enabled.

Receive-side flow:
- `zfs_receive()` is the public entry point. It validates the fd, extracts optional clone origin from props, calls `zfs_receive_impl()`, then mounts/shares newly received filesystem trees through a changelist if appropriate.
- `zfs_receive_impl()` reads and validates the first `DRR_BEGIN`, detects byteswapped streams, rejects unsupported/deprecated stream features, propagates the holds feature, and dispatches to either `zfs_receive_one()` or `zfs_receive_package()`.
- `zfs_receive_package()` reads the compound header nvlist, verifies the header checksum, builds stream AVL metadata, runs pre-receive topology reconciliation for recursive incrementals, receives each contained substream, then reruns reconciliation and encryption hierarchy repair.
- `zfs_receive_one()` is the central single-stream receive routine. It computes the destination snapshot name according to exact, prefix `-d`, or tail `-e` receive semantics; resolves clone origins; validates stream feature compatibility; checks destination existence and overwrite rules; handles resume/newfs cases; prepares command-line property overrides/exclusions; calls `lzc_receive_with_cmdprops()` or `lzc_receive_with_heal()`; applies snapshot properties and holds; maps ioctl errors; and sets mount intent.
- `recv_skip()` consumes a stream after a recoverable duplicate/error case, parsing record payload sizes for object/write/spill/embedded records.
- `recv_read()` and `recv_read_nvlist()` are stream readers with optional checksum update and nvlist size protection.

Receive topology reconciliation:
- `recv_incremental_replication()` compares local dataset/snapshot GUID metadata with stream metadata. With `-F`, it deletes local snapshots/filesystems missing from the stream, renames snapshots/datasets whose GUIDs match but names differ, and promotes clones when stream/local origins differ.
- It uses multi-pass retry logic because renames, deferred destroys, and parent GUID changes can temporarily block later operations.
- `recv_rename()`, `recv_destroy()`, and `recv_promote()` wrap dataset mutations with changelist unmount/remount handling and encryption-root workarounds.
- `guid_to_name_redact_snaps()` and `guid_to_name()` resolve GUIDs to local names by searching progressively broader dataset hierarchy portions. This avoids choosing a less-local duplicate GUID when replicated trees are received piecemeal.
- `created_before()` compares snapshot creation txgs by GUID to decide promotion direction.

Encryption behavior:
- Send-side metadata marks encrypted datasets and encryption roots. Non-raw encrypted sends with properties are rejected unless `no_preserve_encryption` is explicitly set.
- Receive-side raw streams preserve encryption. Non-raw property streams infer `encryption=off` for new filesystems when appropriate.
- `zfs_setup_cmdline_props()` forbids overriding encryption properties for raw streams, restricts encryption settings for incremental streams, validates overrides via `zfs_valid_proplist()`, and uses `zfs_crypto_create()` to prepare wrapping key data.
- `recv_fix_encryption_hierarchy()` runs after recursive raw receive to force datasets into or out of encryption-root status to match the stream and restore keylocation values that were temporarily removed before the receive ioctl.
- Rename/promote helpers force grand origins to become encryption roots when EACCES indicates an encryption-root boundary conflict.

Property and hold handling:
- Dataset properties are sent in the compound header when `-p`, replication, backup mode, or recursive metadata collection requires them.
- Snapshot properties are stored under per-snapshot `snapprops`.
- Holds are collected under `snapholds` and reapplied after receive unless skipped.
- Command-line receive properties use boolean nvpairs for exclusions and strings for overrides. Exclusions may delete received non-inheritable properties or force explicit inheritance.
- Property errors returned from the receive ioctl are reported individually, with truncation summaries via `trunc_prop_errs()`.

Error handling notes:
- Send errors distinguish cross-target incrementals, missing incremental sources, unloaded encryption keys, stream feature mismatch, large microzap requirements, busy targets, and generic kernel errors.
- Receive errors distinguish bad magic, malformed nvlist, unsupported feature flags, deprecated dedup streams, wrong incremental parent, modified destination, destination exists, crypto/key failures, checksum/truncation, incompatible large-block/raw stream state, quota exhaustion, resume conflicts, and oversized kernel allocation.
- `recv_ecksum_set_aux()` enhances resumable checksum/truncation failures with the command needed to resume from the receive token.

External dependencies:
- Kernel/userland interfaces: `zfs_ioctl()`, `lzc_send_*`, `lzc_receive_*`, `lzc_hold()`, `lzc_destroy*()`, `lzc_rename()`, `lzc_change_key()`.
- Metadata libraries: nvlist/fnvlist, AVL trees, ZFS props/features, DMU replay records.
- Checksums/compression: Fletcher-4, zlib.
- Dataset/property helpers from other libzfs files: `zfs_open()`, `zfs_close()`, `zfs_iter_*`, `changelist_*`, `zfs_valid_proplist()`, `zfs_crypto_create()`, error helpers from `libzfs_util.c`.

Research relevance:
- This file is one of the densest userland sources for understanding OpenZFS copy-on-write replication semantics. It shows how snapshot GUIDs, clone origins, redaction bookmarks, raw encryption, resumable receive state, and recursive dataset trees are represented and reconciled across machines.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/libzfs_sendrecv.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/libzfs_share.c -->
# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs_share.c

This file is the protocol-neutral libshare dispatcher used by libzfs for ZFS dataset sharing. It presents a small common API over protocol-specific NFS and SMB implementations.

Primary responsibilities:
- Validate share protocol enum values.
- Dispatch enable, disable, status, commit, truncate, and option-validation operations to the selected protocol backend.
- Provide lower-case protocol names for NFS and SMB.
- Convert internal `SA_*` share errors into localized strings.

Key definitions:
- `sa_protocol_names[]` maps `SA_PROTOCOL_NFS` to `"nfs"` and `SA_PROTOCOL_SMB` to `"smb"`.
- `fstypes[]` maps protocol ids to `libshare_nfs_type` and `libshare_smb_type`.
- `init_share()` initializes the small internal share descriptor with dataset name, mountpoint, and share options.
- `VALIDATE_PROTOCOL()` rejects protocol ids outside `[0, SA_PROTOCOL_COUNT)`.

Main functions:
- `sa_enable_share()` validates the protocol and share options, then calls the backend `enable_share`.
- `sa_disable_share()` constructs a share descriptor from the mountpoint and calls backend `disable_share`.
- `sa_is_shared()` checks backend sharing state for a mountpoint.
- `sa_commit_shares()` lets a backend commit pending share changes.
- `sa_truncate_shares()` calls optional backend truncation, if present.
- `sa_validate_shareopts()` rejects control characters/newlines and delegates protocol-specific validation.
- `sa_errorstr()` maps `SA_*` integer errors to human-readable localized text, falling back to `"unknown %d"`.

Important behavior:
- This file does not implement NFS or SMB mechanics itself. It is a stable dispatch layer.
- `sa_validate_shareopts()` assumes `options` is non-NULL and checks for `\a\b\f\n\r`.
- `sa_commit_shares()` and `sa_truncate_shares()` return void and silently ignore invalid protocols via the macro expansion.
- Many `SA_*` values are listed in the header as never returned by current libshare, but `sa_errorstr()` still preserves their strings for compatibility.

Dependencies:
- `libzfs_share.h` for protocol types, errors, and backend vtables.
- `libzfs_impl.h` and `libzfs.h` for libzfs integration and protocol enum definitions.
- Protocol backend objects are defined in NFS/SMB implementation files.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/libzfs_share.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/libzfs_share.h -->
# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs_share.h

This header defines the internal libzfs share abstraction used to support ZFS `sharenfs` and `sharesmb` behavior without binding the common code to one protocol.

Primary responsibilities:
- Declare share error constants.
- Declare protocol-neutral share-control functions.
- Define the backend vtable shape for NFS/SMB share implementations.
- Declare internal NFS helper functions and constants.
- Declare internal SMB constants and share-list data structure.

Public/common declarations:
- `sa_errorstr(int)` returns a localized string for an `SA_*` error.
- `sa_protocol_names[]` exposes lower-case protocol names.
- `sa_enable_share()`, `sa_disable_share()`, `sa_is_shared()`, `sa_commit_shares()`, `sa_truncate_shares()` are the protocol-neutral share API.
- `sa_validate_shareopts()` validates protocol-specific option strings.

Error constants:
- Active errors include `SA_OK`, `SA_SYSTEM_ERR`, `SA_SYNTAX_ERR`, `SA_NO_MEMORY`, `SA_INVALID_PROTOCOL`, and `SA_NOT_SUPPORTED`.
- Many compatibility errors are defined but documented as never returned by current libshare, including duplicate name, bad path, no permission, invalid security, section/resource errors, and share-exists cases.

Core internal types:
- `sa_share_impl_t` points to a const structure containing:
  - `sa_zfsname`
  - `sa_mountpoint`
  - `sa_shareopts`
- `sa_fstype_t` is the backend vtable with function pointers:
  - `enable_share`
  - `disable_share`
  - `is_shared`
  - `validate_shareopts`
  - `commit_shares`
  - `truncate_shares`

Backend symbols:
- `libshare_nfs_type`
- `libshare_smb_type`

NFS internals:
- `NFS_FILE_HEADER` is the generated exports-file warning header.
- `nfs_escape_mountpoint()` escapes mountpoints for `/etc/exports`-style matching.
- `nfs_is_shared_impl()` scans exports content for a mountpoint.
- `nfs_toggle_share()` performs locked temporary-file update of exports content.
- `nfs_reset_shares()` truncates generated exports state under lock.

SMB internals:
- Defines `SMB_NAME_MAX`, `SMB_COMMENT_MAX`, `SMB_SHARE_DIR`, `SMB_NET_CMD_PATH`, and `SMB_NET_CMD_ARG_HOST`.
- `smb_share_t` stores Samba usershare metadata: name, path, comment, guest flag, and next pointer.

Research relevance:
- This header is the small contract between generic ZFS sharing code and protocol-specific share backends.
- Its vtable design keeps `libzfs_share.c` protocol-independent while allowing NFS and SMB to use very different persistence mechanisms.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/libzfs_share.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/libzfs_share_nfs.c -->
# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs_share_nfs.c

This file implements common NFS exports-file update helpers used by the NFS sharing backend. It provides locking, temporary-file replacement, mountpoint escaping, exports scanning, and reset behavior.

Primary responsibilities:
- Serialize updates to an exports file with `flock()`.
- Rewrite generated exports content atomically using a temporary file plus `rename()`.
- Escape mountpoints containing whitespace or backslashes for NFS exports syntax.
- Scan exports files and identify entries matching a mountpoint.
- Copy exports entries while omitting an entry for a target mountpoint.
- Truncate generated exports state under lock.

Important functions:
- `nfs_exports_lock()` opens/creates the lockfile and obtains an exclusive flock, retrying on `EINTR`.
- `nfs_exports_unlock()` releases the flock, closes the fd, and resets the fd to `-1`.
- `nfs_init_tmpfile()` optionally creates the exports directory, creates a `mkostemp()` temp file based on the exports path, and wraps it in `FILE *`.
- `nfs_abort_tmpfile()` unlinks and closes a temp file after failure.
- `nfs_fini_tmpfile()` flushes, renames the temp file over the exports file, chmods it to `0644`, and closes it.
- `nfs_escape_mountpoint()` returns either the original mountpoint or a newly allocated escaped string where whitespace/backslash characters become octal escapes.
- `nfs_process_exports()` opens the exports file, escapes the target mountpoint, reads lines with `getline()`, skips blank/comment lines, and invokes a callback with a match flag.
- `nfs_copy_entries_cb()` writes through nonmatching lines.
- `nfs_copy_entries()` emits `NFS_FILE_HEADER`, then copies all existing entries except the target mountpoint.
- `nfs_toggle_share()` is the core update routine: create temp file, lock exports, copy old entries minus target, invoke caller callback to add/remove/update target entry, rename temp file, unlock.
- `nfs_reset_shares()` locks and truncates the exports file.
- `nfs_is_shared_impl()` scans exports and returns true if the mountpoint exists.

Data structures:
- `struct tmpfile` stores a short temp filename buffer and the open `FILE *`.

Important behavior:
- Temporary filename buffer is fixed at 64 bytes, based on the comment that the target exports path plus suffix is bounded in this usage.
- Exports parsing matches the mountpoint only as the first token ending at whitespace/newline.
- `nfs_process_exports()` ignores callback output for blank/comment lines; those lines are not passed to callbacks.
- File update uses `rename()` for atomic replacement after writing.
- If `fdopen()` fails after `mkostemp()`, the fd is closed but the temp path is not unlinked in that local failure path.

Dependencies:
- `libzfs_impl.h` and `libzfs_share.h` declarations.
- `libzutil` for `zfs_strerror()`.
- POSIX file APIs: `open`, `flock`, `mkostemp`, `fdopen`, `getline`, `rename`, `truncate`, `fchmod`.

Research relevance:
- This file shows the userland persistence pattern for generated NFS shares: lock, rewrite filtered exports, atomically replace, and commit/reset through backend-specific hooks.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/libzfs_share_nfs.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/libzfs_status.c -->
# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs_status.c

This file computes high-level pool health/status classifications for `zpool status` and pool import reporting. It maps detailed pool/vdev configuration state into `ZPOOL_STATUS_*` values and optional FMA-style message ids.

Primary responsibilities:
- Inspect active or import-time pool configuration nvlists.
- Detect resilvering, rebuilding, rebuild-needs-scrub, hostid/MMP conflicts, unsupported versions/features, suspended I/O, bad logs, corrupt metadata, missing/faulted devices, failing devices, offline/removed devices, non-native ashift, errata, legacy versions, disabled features, and compatibility mismatches.
- Map selected statuses to stable `ZFS-8000-*` message ids.

Important data:
- `zfs_msgid_table[]` maps early `ZPOOL_STATUS_*` enum values to message ids. Later informational/status values intentionally have no message id.
- `NMSGID` is the table size guard.

Vdev predicate helpers:
- `vdev_missing()` detects `VDEV_STATE_CANT_OPEN` plus `VDEV_AUX_OPEN_FAILED`.
- `vdev_faulted()` detects `VDEV_STATE_FAULTED`.
- `vdev_errors()` detects degraded state or nonzero read/write/checksum errors.
- `vdev_broken()` detects `VDEV_STATE_CANT_OPEN`.
- `vdev_offlined()` detects `VDEV_STATE_OFFLINE`.
- `vdev_removed()` detects `VDEV_STATE_REMOVED`.
- `vdev_non_native_ashift()` detects configured ashift below physical ashift, with optional pool ashift filtering.

Traversal:
- `find_vdev_problem()` recursively walks the vdev tree and optional L2 cache devices, applying a predicate to leaves.
- It can ignore children under replacing vdevs.
- It has dRAID failure-domain awareness: if all members of a dRAID failure group are problematic, it returns `EDOM`; otherwise leaf problems return `ENXIO`.

Status algorithm:
- `check_status()` performs ordered checks from most severe or most actionable to least:
  - active resilvering
  - active rebuild or rebuild completed after last scrub
  - multihost/MMP active/hostid-required/hostid-mismatch cases
  - pool last accessed by another host
  - newer on-disk version
  - unsupported features, read-only vs unreadable
  - bad GUID sum
  - suspended I/O and MMP suspend reason
  - bad log
  - non-replicated missing/faulted/corrupt-label devices
  - corrupt pool metadata
  - persistent data errors
  - replicated missing/faulted/corrupt-label devices, including dRAID fault domains
  - failing devices
  - offline devices
  - removed devices
  - non-native ashift, unless disabled via `ZPOOL_STATUS_NON_NATIVE_ASHIFT_IGNORE`
  - pool errata
  - older but supported pool version
  - feature compatibility and disabled/superfluous feature checks
  - otherwise `ZPOOL_STATUS_OK`

Public entry points:
- `zpool_get_status()` gets pool compatibility and ashift properties from a live `zpool_handle_t`, calls `check_status()`, and returns optional msgid.
- `zpool_import_status()` runs the same status logic for import configs and returns optional msgid.

Important behavior:
- Import checks skip persistent data error and failing-device checks that depend on live pool state.
- Compatibility logic calls `zpool_load_compat()` and compares enabled features against requested compatibility feature sets.
- The `"legacy"` compatibility value suppresses old-version reporting.
- Feature checks skip unsupported-by-module and no-upgrade feature entries.

Dependencies:
- Pool/vdev config nvlist keys from OpenZFS.
- `zfeature_common.h` and `spa_feature_table`.
- `libzutil` and `libzfs_impl.h`.
- System hostid through `get_system_hostid()`.

Research relevance:
- This file is the policy layer that turns raw COW pool topology and scan/device state into user-visible health statuses.
- The ordering in `check_status()` is significant because only one status is returned even when multiple issues are present.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/libzfs_status.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/libzfs_util.c -->
# File Research: sources/cow-pools/openzfs/lib/libzfs/libzfs_util.c

This file provides broad internal utility support for libzfs: handle lifecycle, error reporting, ioctl nvlist packing, external process execution, property-list printing/parsing, numeric parsing, version reporting, color output, script environment construction, and disk preparation helpers.

Primary responsibilities:
- Maintain and expose libzfs error state.
- Convert system and ZFS kernel errors to libzfs `EZFS_*` errors.
- Allocate memory with libzfs error handling.
- Initialize and finalize `libzfs_handle_t`.
- Run external helper programs and capture stdout.
- Pack/unpack nvlists into `zfs_cmd_t` ioctl structures.
- Print property data in table or JSON form.
- Parse user-facing numeric property values.
- Build/expand property lists for zfs/zpool/vdev commands.
- Report userland/kernel versions.
- Control optional ANSI color output.
- Prepare script environments for vdev helper scripts.
- Run optional disk preparation scripts before labeling.

Error-state API:
- `libzfs_errno()` returns the current libzfs error.
- `libzfs_error_action()` returns the current action string.
- `libzfs_error_description()` returns an explicit auxiliary description or a default string for `EZFS_*`.
- `zfs_error_aux()` stores formatted auxiliary text.
- `zfs_error()` and `zfs_error_fmt()` set libzfs error/action state and return `-1`.
- `zfs_standard_error()` / `zfs_standard_error_fmt()` map errno and ZFS-specific kernel errors to dataset-oriented `EZFS_*`.
- `zpool_standard_error()` / `zpool_standard_error_fmt()` do the same for pool operations.
- `zfs_setprop_error()` specializes property-setting failures such as quota/reservation space semantics, read-only datasets, too-long values, unsupported pool features, boot/root-pool restrictions, and keylocation restrictions.

Handle lifecycle:
- `libzfs_init()` loads the module, allocates the handle, compiles the URI regex, opens `ZFS_DEV`, initializes libzfs_core, property tables, feature tables, mount-table state, and Fletcher-4.
- It reads `ZFS_SENDRECV_MAX_NVLIST` to override the maximum send/receive metadata nvlist size, defaulting to `SPA_MAXBLOCKSIZE * 4`.
- It supports test behavior through `ZFS_PROP_DEBUG` and `ZFS_SYSFS_PROP_SUPPORT_TEST`.
- `libzfs_fini()` closes the fd, frees pool handles and namespace state, finalizes mnttab/libzfs_core/Fletcher, releases regex state, optionally unloads dynamic libfetch, and frees the handle.
- Accessors include `zpool_get_handle()`, `zfs_get_handle()`, and `zfs_get_pool_handle()`.

Memory/process helpers:
- `no_memory()`, `zfs_alloc()`, `zfs_realloc()`, `zfs_strdup()`, and `zfs_asprintf()` provide checked allocation patterns.
- `libzfs_print_on_error()` controls automatic stderr reporting.
- `libzfs_run_process_impl()` forks, sets a new process group, redirects stdout/stderr to `/dev/null` or a pipe depending on flags, supports `execv/execvp/execve/execvpe`, waits, and returns child exit status.
- `libzfs_run_process()`, `libzfs_run_process_get_stdout()`, and `_nopath()` are public wrappers.
- `libzfs_read_stdout_from_fd()` reads child stdout into a heap array of newline-trimmed strings.
- `libzfs_free_str_array()` frees those arrays.
- `libzfs_envvar_is_set()` treats numeric nonzero, `YES`, and `ON` as enabled.

Dataset/path and ioctl nvlist helpers:
- `zfs_path_to_zhandle()` treats non-path input as a dataset name, otherwise resolves a mounted ZFS filesystem through mnttab device matching.
- `zfs_ioctl()` calls `lzc_ioctl_fd()` using the handle fd.
- `zcmd_alloc_dst_nvlist()`, `zcmd_expand_dst_nvlist()`, `zcmd_free_nvlists()`, `zcmd_write_conf_nvlist()`, `zcmd_write_src_nvlist()`, and `zcmd_read_dst_nvlist()` manage packed nvlist buffers in `zfs_cmd_t`.
- `zcmd_print_json()` prints an nvlist as JSON and frees it.

Property display:
- `zprop_print_headers()` computes column widths and prints non-scripted headers.
- `zprop_nvlist_one_property()` adds one property to a JSON nvlist, preserving value and source metadata.
- `zprop_print_one_property()` prints one property row according to selected columns and source filters.
- `zprop_collect_property()` dispatches either JSON collection or table printing.

Numeric and property parsing:
- `str2shift()` validates binary suffixes such as `K`, `M`, `G`, optional `B`/`iB`, and computes base-2 shifts.
- `zfs_nicestrtonum()` parses integer or decimal numeric strings plus suffixes, rejects invalid suffixes and overflow, and returns a `uint64_t`.
- `zprop_parse_value()` converts string/uint64/index property values into DSL-compatible nvlist values. It handles special values such as quota `none`, pool DDT quota `none`/`auto`, filesystem/snapshot limit `none`, vdev checksum/io limit `none`, and volume refreservation `auto`.
- `zprop_get_list()` parses comma-separated property lists, including the synthetic `space` group.
- `addlist()` validates native and user-defined property names by type.
- `zprop_expand_list()` expands `all` into every native property plus leading `name`.
- `zprop_free_list()` frees property-list chains.
- `zprop_iter()` delegates to common property iteration.

Version/color:
- `zfs_version_userland()` returns `ZFS_META_ALIAS`.
- `zfs_version_print()` prints userland and kernel module versions.
- `zfs_version_nvlist()` returns both versions in an nvlist.
- `use_color()` caches whether color output is allowed based on `ZFS_COLOR`, `NO_COLOR`, stdout TTY status, and `TERM`.
- `color_start()`, `color_end()`, and `printf_color()` wrap ANSI-colored output.

Vdev script/disk preparation:
- `zpool_vdev_script_alloc_env()` builds a limited environment for helper scripts with `PATH`, `POOL_NAME`, `VDEV_PATH`, `VDEV_UPATH`, `VDEV_ENC_SYSFS_PATH`, and optional key/value.
- `zpool_vdev_script_free_env()` frees that environment.
- `zpool_prepare_disk()` runs `ZFSEXECDIR/zfs_prepare_disk` if executable, passing vdev environment and capturing stdout.
- `zpool_prepare_and_label_disk()` runs preparation and then labels the disk via `zpool_label_disk()`.

Important behavior:
- Error helpers centralize translation from kernel/userland errno into stable libzfs error categories used throughout the library, including `libzfs_sendrecv.c`.
- `libzfs_init()` must succeed in several stages; failure paths close/free only the resources acquired so far.
- The nvlist write helpers allocate packed buffers owned by `zfs_cmd_t` and released by `zcmd_free_nvlists()`.
- Process execution closes over stdout/stderr behavior with flags; stdout capture uses a nonblocking close-on-exec pipe.
- Numeric parsing uses binary units, not decimal SI units.

Research relevance:
- This file is foundational support code for almost every libzfs module in this group. It explains how libzfs reports failures, communicates nvlists to kernel ioctls, interprets user property values, initializes feature/property state, and invokes external helper scripts.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/lib/libzfs/libzfs_util.c -->