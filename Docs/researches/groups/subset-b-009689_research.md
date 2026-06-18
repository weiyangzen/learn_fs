# Group Research: subset-b-009689

Work item `subset-b-009689` covers GPFS FSAL source files under `sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS`. Each section is wrapped for reconciliation and has a matching tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_ds.c -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_ds.c

- **Purpose:** Implements GPFS pNFS data-server operations: create DS handles from wire handles, read, READ_PLUS, write, commit, permission checks, and DS handle release.
- **Important APIs/types/functions:** `pnfs_ds_ops_init`, `make_ds_handle`, `ds_read`, `ds_read_plus`, `ds_write`, `ds_commit`, `ds_handle_release`, `pds_permissions`, `struct gpfs_ds`, `struct gpfs_file_handle`, GPFS ioctl argument types `dsread_arg`, `dswrite_arg`, and `fsync_arg`.
- **Control flow:** `pnfs_ds_ops_init` starts from default pNFS DS ops and installs GPFS callbacks. `make_ds_handle` validates serialized handle size, endian-adjusts handle metadata, extracts the GPFS fsid, verifies that the fsid maps to this FSAL, allocates `struct gpfs_ds`, and copies the wire handle. Read/write/commit callbacks recover the private `gpfs_ds`, fill GPFS ioctl argument blocks using the current export fd and optional client IP, call `gpfs_ganesha`, and translate POSIX errors to NFSv4 status.
- **State and persistence behavior:** DS handles are heap allocations containing the wire GPFS handle, owning `gpfs_filesystem`, and a lazy `connected` flag. Reads do not persist Ganesha state. Writes return a verifier and invalidate the export cache for the handle key. Commits call GPFS fsync by handle. Durable data movement and synchronization are delegated to the GPFS kernel interface.
- **Dependencies and integration points:** Depends on Ganesha FSAL/pNFS APIs, `op_ctx`, export upcall invalidation, `lookup_fsid`, `gpfs_extract_fsid`, `gpfs_ganesha`, `pnfs_utils`, and NFS credential/client context. The callbacks plug into NFSv4.1/v4.2 pNFS DS paths and bypass normal mdcache object loading.
- **Risks:** `ds_commit` records `errno` but always returns `NFS4_OK`, so fsync failures can be masked. `ds_read_plus` hole handling depends on GPFS `ENODATA` and `filesize` semantics. The code relies on global `op_ctx` and fatal-stops on `EUNATCH`. Handle endian conversion mutates the supplied descriptor buffer.
- **Test signals:** Exercise pNFS READ/READ_PLUS over data and holes, DS WRITE with cache invalidation, COMMIT failure injection, stale/non-GPFS wire handles, endian-flagged handles, and GPFS-unmounted `EUNATCH` behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_ds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_fileop.c -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_fileop.c

- **Purpose:** Provides low-level opened-file operations for GPFS: open by handle, read, write, and allocation/deallocation.
- **Important APIs/types/functions:** `GPFSFSAL_open`, `GPFSFSAL_read`, `GPFSFSAL_write`, `GPFSFSAL_alloc`, GPFS ioctl argument types `read_arg`, `write_arg`, and `alloc_arg`.
- **Control flow:** `GPFSFSAL_open` converts a GPFS object handle to an fd through `fsal_internal_handle2fd` under caller credentials, then retries without credential switching if the first open fails because upper layers perform permission checks elsewhere. `GPFSFSAL_read` and `GPFSFSAL_write` populate fd-based GPFS ioctl arguments, set client IP when available, switch to NFS caller credentials, call `gpfs_ganesha`, restore Ganesha credentials, and return FSAL errors. `GPFSFSAL_alloc` similarly wraps `OPENHANDLE_ALLOCATE_BY_FD`.
- **State and persistence behavior:** The file stores no module-global state. It creates kernel file descriptors for object handles and mutates caller-provided read/write lengths and EOF/stability outputs. Actual file contents, allocation state, and write stability are persisted by GPFS.
- **Dependencies and integration points:** Used by higher-level open2/read2/write2/fallocate paths declared in `gpfs_methods.h` and implemented in neighboring GPFS FSAL code. It depends on `op_ctx`, `struct gpfs_fsal_export.export_fd`, credential helpers, `fsal_internal_handle2fd`, `gpfs_ganesha`, and POSIX-to-FSAL error conversion.
- **Risks:** The root-retry open path may hide credential-specific open failures if upper-layer permission checks drift. Negative read values other than `-1` are treated as encoded errno values, which couples behavior to the GPFS ioctl contract. `EUNATCH` is fatal. EOF is only set true, so callers must initialize it before calling.
- **Test signals:** Cover open success/failure under user and root retry, partial/zero reads, write stability reporting, allocation and deallocation, negative ioctl return variants, and client-IP propagation where GPFS auditing depends on it.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_fileop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_internal.c -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_internal.c

- **Purpose:** Central GPFS FSAL helper layer around GPFS openhandle ioctls, covering close, handle lookup/open/create/link/stat/unlink/rename/readlink, version probing, xstat/ACL get/set, truncate, and FSAL error log classification.
- **Important APIs/types/functions:** `fsal_internal_close`, `fsal_internal_handle2fd`, `fsal_internal_get_handle_at`, `fsal_internal_get_fh`, `fsal_internal_fd2handle`, `fsal_internal_link_fh`, `fsal_internal_stat_name`, `fsal_internal_unlink`, `fsal_internal_create`, `fsal_internal_mknode`, `fsal_internal_rename_fh`, `fsal_readlink_by_handle`, `fsal_internal_version`, `fsal_get_xstat_by_handle`, `fsal_set_xstat_by_handle`, `fsal_trucate_by_handle`, `fsal_error_is_event`, and `fsal_error_is_info`.
- **Control flow:** Most helpers validate pointer/name arguments, initialize a GPFS ioctl argument struct with mount fd, handle, name length, output buffers, and optional client IP, call `gpfs_ganesha`, and map errno through `FSAL_INTERNAL_ERROR` or explicit switch logic. Mutating operations such as unlink, rename, and set-xstat switch to caller credentials around the ioctl. `fsal_get_xstat_by_handle` has richer ACL/stat behavior, including ACL header initialization, `ENODATA` stat-only success, ACL buffer-too-small success on `ENOSPC`, and ACE-count validation.
- **State and persistence behavior:** The helpers do not keep durable state, but they open and close GPFS file descriptors, produce persistent filesystem changes for create/mknode/link/unlink/rename/setattr/truncate, and fill caller-owned GPFS handles/stat/ACL buffers. They normalize a known GPFS 40-byte handle-size bug to 48 bytes during name lookup.
- **Dependencies and integration points:** Used by nearly all GPFS object, export, metadata, symlink, lookup, file, and pNFS paths. Depends on `gpfs_ganesha`, `include/gpfs.h`, `include/gpfs_nfs.h`, `op_ctx`, Ganesha credentials, `fsal_convert`, and FSAL logging/error conventions.
- **Risks:** The entire FSAL relies on exact ioctl ABI structs and errno semantics. The `fsal_trucate_by_handle` symbol appears misspelled, so external references must match the typo. ACL retry callers must honor the success-with-larger-required-length convention. The fd assertion in `fsal_internal_handle2fd` assumes GPFS never returns stdin/stdout/stderr fds.
- **Test signals:** Validate each openhandle opcode path, credential-switching mutation calls, handle-size normalization, ACL success/retry/ENODATA/ENOSPC paths, version fallback from v4 to v2, EUNATCH fatal behavior, and POSIX-to-FSAL error mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_internal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_internal.h -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_internal.h

- **Purpose:** Declares internal GPFS FSAL module structures, private handle/FD/state types, supported attribute masks, ACL limits, helper prototypes, operation wrappers, pNFS hooks, statistics hooks, and upcall entry points.
- **Important APIs/types/functions:** Defines `struct gpfs_fsal_module`, `struct gpfs_ds`, `struct gpfs_fd`, `struct gpfs_state_fd`, `gpfsfsal_xstat_t`, `GPFS_SUPPORTED_ATTRIBUTES`, `GPFS_MAX_FH_SIZE`, `GPFS_ACL_BUF_SIZE`, `GPFS_ACL_MAX_RETRY`, `GPFS_ACL_MAX_NACES`, `GPFS_FSID_TYPE`, and the prototypes for internal helpers and GPFSFSAL operation wrappers.
- **Control flow:** This header has no runtime control flow. It shapes compile-time coupling by making GPFS helper and operation entry points visible across `handle.c`, file I/O code, export code, pNFS files, upcalls, and stats.
- **State and persistence behavior:** Defines in-memory state layout for DS handles, global/shared file descriptors, open-state-associated GPFS fds, and combined stat/fsid/ACL buffers. The `GPFS_SUPPORTED_ATTRIBUTES` mask advertises POSIX, ACL, space reservation, fs_locations, and xattr support to the broader FSAL.
- **Dependencies and integration points:** Includes GPFS NFS kernel headers, Ganesha FSAL common types, config/upcall headers, and list/config helpers. It is the main internal contract for the GPFS FSAL directory.
- **Risks:** Struct layout matters: `gpfs_state_fd.state` must remain first for default state free behavior. ACL constants encode GPFS-specific limits. Prototype drift between this header and implementation files will break method table wiring or hide missing implementations at link time.
- **Test signals:** Build/link coverage is the primary signal. Runtime coverage should verify advertised attributes, ACL buffer retry behavior, pNFS DS/MDS initialization, and regular-file fd lifecycle using `gpfs_fd` and `gpfs_state_fd`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_lock.c -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_lock.c

- **Purpose:** Implements GPFS-backed lock, lock-test, blocking-lock, and delegation-lock operations for the FSAL.
- **Important APIs/types/functions:** `GPFSFSAL_lock_op`, `fsal_lock_op_t`, `fsal_lock_param_t`, `struct set_get_lock_arg`, `struct glock`, and GPFS opcodes `OPENHANDLE_SET_DELEGATION`, `OPENHANDLE_GET_LOCK`, and `OPENHANDLE_SET_LOCK`.
- **Control flow:** The function chooses a GPFS ioctl based on the requested lock type and operation: leases use delegation, lock-test uses get-lock, and all other operations use set-lock. On success it populates `confl_lock` for lock-test conflicts or clears it. On failure it may run a follow-up `GET_LOCK` to populate conflict owner details for lock requests, handles GPFS queued-blocked-lock return `1`, maps `EGRACE` to `ERR_FSAL_IN_GRACE`, and otherwise maps errno to FSAL status.
- **State and persistence behavior:** Persistent lock/delegation state lives in GPFS and Ganesha state owners. This file mutates caller-provided conflict-lock output and may update `glock->cmd` to `F_GETLK` after a failed set-lock.
- **Dependencies and integration points:** Integrated through the object `lock_op2` implementation in neighboring file I/O code and ultimately through NFS lock/delegation handling. It depends on GPFS lock ABI structures from `gpfs_nfs.h`, FSAL lock types, `gpfs_ganesha`, and POSIX lock constants.
- **Risks:** `_FILE_OFFSET_BITS` is intentionally undefined because the GPFS kernel module expects plain `F_GETLK/SETLK/SETLKW` values, making this file sensitive to platform and build flags. Conflict reporting after a failed set-lock can itself fail. `EUNATCH` is fatal.
- **Test signals:** Cover nonblocking and blocking locks, lock-test conflicts and no-conflict responses, delegation locks, grace-period errors, queued-blocked-lock return `1`, and conflict detail retrieval after failed lock acquisition.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_lock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_lookup.c -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_lookup.c

- **Purpose:** Resolves child names under GPFS directory handles into GPFS file handles and attributes, including filesystem-boundary handling and GPFS-specific dotdot workarounds.
- **Important APIs/types/functions:** `GPFSFSAL_lookup`, `get_handle2inode`, `GPFS_ROOT_INODE`, `fsal_internal_handle2fd`, `fsal_internal_get_handle_at`, `gpfs_extract_fsid`, `lookup_fsid`, and `GPFSFSAL_getattrs`.
- **Control flow:** The lookup path validates parent/name, opens the parent handle as a directory, rejects non-directory parents, asks GPFS for the child handle, closes the parent fd, handles special `..` failures at the GPFS root, detects a GPFS bug where dotdot returns the same handle as the parent and returns `ERR_FSAL_DELAY`, extracts fsid for XDEV detection, switches `new_fs` when crossing to another GPFS filesystem, and finally fetches attributes for the correct filesystem.
- **State and persistence behavior:** No durable state is changed. Temporary fds are opened and closed; the caller receives a GPFS file handle, attributes, and possibly a changed `new_fs` pointer.
- **Dependencies and integration points:** Used by `handle.c` object lookup and readdir-plus paths. It depends on the GPFS handle binary layout for inode extraction, FSAL filesystem registry lookup, and attribute conversion from `GPFSFSAL_getattrs`.
- **Risks:** `get_handle2inode` casts opaque GPFS handle bytes to a local struct layout, so GPFS handle format changes can break root/dotdot logic. XDEV detection compares only fsid major to the parent object fsid major. The dotdot delay workaround depends on retry behavior above this layer.
- **Test signals:** Test regular lookup, non-directory parent, missing names, `..` at root, GPFS same-handle dotdot bug, cross-GPFS filesystem traversal, cross-non-GPFS traversal, and stale/unknown fsid handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_lookup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_mds.c -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_mds.c

- **Purpose:** Implements pNFS metadata-server export and object callbacks for GPFS layouts, device info, layout grant/return/commit, layout sizing, and write verifier retrieval.
- **Important APIs/types/functions:** `export_ops_pnfs`, `handle_ops_pnfs`, `fs_layouttypes`, `fs_layout_blocksize`, `fs_maximum_segments`, `fs_loc_body_size`, `fs_da_addr_size`, `getdeviceinfo`, `getdevicelist`, `fs_verifier`, `layoutget`, `layoutreturn`, and `layoutcommit`.
- **Control flow:** Export callbacks report file-layout support only if GPFS `OPENHANDLE_LAYOUT_TYPE` returns `LAYOUT4_NFSV4_1_FILES`, expose static sizing limits, fetch encoded device information by letting GPFS write into an XDR inline buffer, and return no device list. `layoutget` validates layout type, copies the object handle to a DS handle, asks GPFS for layout data, constructs a whole-file single-segment response with return-on-close, encodes the NFSv4.1 file layout, and returns the GPFS layout reservation if encoding fails. `layoutreturn` and `layoutcommit` validate type and forward return/commit arguments to GPFS.
- **State and persistence behavior:** Layout reservations, commits, recalls, and verifier data are maintained by GPFS. The file mutates NFS layout result structures and XDR streams, and may trigger GPFS layout return on encode failure.
- **Dependencies and integration points:** Hooks into export ops and object ops when pNFS MDS is enabled. Depends on `FSAL_encode_file_layout`, `pnfs_deviceid`, Ganesha export IDs, `op_ctx`, GPFS pNFS ioctl ABI, and NFSv4.1/v4.2 layout structures.
- **Risks:** `getdeviceinfo` uses `device_id4` as `mountdirfd`, so device IDs must carry a valid export/root fd. `layoutcommit` maps `posix2nfs4_error(-rc)` even though `errno` was captured separately, making non-errno rc conventions important. Only one segment and files layout are supported. XDR buffer accounting is delicate.
- **Test signals:** Cover layout type discovery disabled/enabled, successful layoutget and encoded file layout, `maxcount` too-small handling with relinquish, layoutreturn dispose behavior, layoutcommit with size/time changes, getdeviceinfo XDR output, and unsupported layout type errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_mds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_rename.c -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_rename.c

- **Purpose:** Implements GPFS rename/move of a named object between directory handles.
- **Important APIs/types/functions:** `GPFSFSAL_rename`, `fsal_internal_stat_name`, `fsal_internal_rename_fh`, `struct gpfs_fsal_obj_handle`, and `struct gpfs_fsal_export`.
- **Control flow:** Converts old and new public directory handles to GPFS private handles, stats the old name in the old directory to validate existence and collect metadata, then calls `fsal_internal_rename_fh` with old and new directory handles plus names. Any FSAL error from stat or rename is returned directly.
- **State and persistence behavior:** The persistent namespace mutation is performed by GPFS through `OPENHANDLE_RENAME_BY_FH` in the internal helper. This wrapper stores no state and does not update cached attributes directly.
- **Dependencies and integration points:** Called by `handle.c` `renamefile`, then by Ganesha object operation dispatch. Depends on current export fd from `op_ctx`, private GPFS object handles, internal stat/rename helpers, and FSAL error conversion.
- **Risks:** The pre-stat introduces an existence/type check but does not eliminate rename races. Parent pre/post attribute outputs are ignored in the caller path. Cache invalidation is not explicit here and depends on upper layers or GPFS upcalls.
- **Test signals:** Cover same-directory rename, cross-directory rename, missing source, existing destination replacement semantics, permission failures under caller credentials in `fsal_internal_rename_fh`, and cache/upcall visibility after rename.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_rename.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_stats_gpfs.c -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_stats_gpfs.c

- **Purpose:** Provides GPFS FSAL operation statistics storage, initialization, optional DBus export, opcode naming, and reset support.
- **Important APIs/types/functions:** Global `gpfs_op_stats`, global `gpfs_stats`, `prepare_for_stats`, `fsal_gpfs_extract_stats` under `USE_DBUS`, `fsal_gpfs_reset_stats`, and private `gpfs_opcode_to_name`.
- **Control flow:** `prepare_for_stats` sets the module stats pointer and pre-fills each stats slot with its GPFS opcode using `gpfs_op2index`. When DBus is enabled, `fsal_gpfs_extract_stats` emits a GPFS stats structure, skipping placeholder indexes and zero-count ops, computing average/min/max response times in seconds from stored nanosecond/microsecond-scaled counters, and appending a dummy row if there are no stats. `fsal_gpfs_reset_stats` atomically zeros counters for all physical indexes.
- **State and persistence behavior:** The file owns in-memory process-wide stats arrays. Stats are updated by `gpfs_ganesha` in `gpfsext.c` when FSAL stats are enabled; reset clears counters but not opcode mappings.
- **Dependencies and integration points:** Integrated with the FSAL module stats pointer, `nfs_param.core_param.enable_FSALSTATS`, DBus status reporting, atomic helpers, and GPFS opcode constants from `gpfs_nfs.h`.
- **Risks:** DBus extraction only compiles under `USE_DBUS`; non-DBus builds rely on reset/init only. Placeholder indexes must remain aligned with `gpfs_op2index`. Direct non-atomic comparisons of min/max update fields happen in `gpfsext.c`, so concurrent stats accuracy may be approximate.
- **Test signals:** Verify stats initialization maps every opcode, ioctl calls increment counters when stats are enabled, DBus extraction emits named rows and dummy `None` row with zero operations, reset clears all counters, and placeholder indexes are skipped.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_stats_gpfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_symlinks.c -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_symlinks.c

- **Purpose:** Implements symlink read and symlink creation for GPFS object handles.
- **Important APIs/types/functions:** `GPFSFSAL_readlink`, `GPFSFSAL_symlink`, `fsal_readlink_by_handle`, `fsal_internal_handle2fd`, `fsal_internal_get_handle_at`, `GPFSFSAL_getattrs`, and POSIX `symlinkat`.
- **Control flow:** `GPFSFSAL_readlink` unwraps the private GPFS handle and delegates to `fsal_readlink_by_handle`. `GPFSFSAL_symlink` checks export symlink support, opens the parent directory by handle, switches to caller credentials, creates the link using `symlinkat`, restores credentials, fetches the new GPFS handle, fetches attributes, verifies the resulting object is actually a symlink, closes the directory fd, and returns status.
- **State and persistence behavior:** Creation persists a new symlink in GPFS via the opened parent directory fd. The function fills caller-provided handle and attribute outputs. It stores no module-level state.
- **Dependencies and integration points:** Used by `handle.c` `makesymlink` and `readsymlink`. Depends on export capability checks, credentials, POSIX directory-fd symlink creation, GPFS handle lookup, and attribute conversion.
- **Risks:** There is a race between `symlinkat` and handle lookup by name; comments acknowledge a similar lower-level race. If creation succeeds but lookup or attrs fail, the symlink may remain. Mode bits are effectively ignored for symlinks. Type verification maps a non-symlink result to `ERR_FSAL_EXIST`.
- **Test signals:** Cover readlink buffer termination, symlink support disabled, successful create/read, permission and existing-name failures, race-like replacement between create and lookup, non-symlink type verification failure, and fd close on every error path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_symlinks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_unlink.c -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_unlink.c

- **Purpose:** Implements removal of a named filesystem object from a GPFS directory handle.
- **Important APIs/types/functions:** `GPFSFSAL_unlink`, `fsal_internal_stat_name`, `fsal_internal_unlink`, `gpfsfsal_xstat_t`, and `struct gpfs_fsal_obj_handle`.
- **Control flow:** The wrapper unwraps the parent directory private handle, stats the target name under the export fd to validate and collect metadata, then calls `fsal_internal_unlink` with the parent handle, name, and stat buffer. Errors from either step are returned directly.
- **State and persistence behavior:** Persistent namespace deletion occurs in GPFS through `OPENHANDLE_UNLINK_BY_NAME` in the internal helper under caller credentials. The wrapper keeps no state and does not explicitly invalidate caches.
- **Dependencies and integration points:** Called by `handle.c` `file_unlink` as the object op implementation. Depends on `op_ctx`, export fd, GPFS private handles, and internal stat/unlink helpers.
- **Risks:** The pre-stat and unlink are race-prone if the name changes between operations. The same path handles file and directory removal according to GPFS/openhandle semantics, so caller expectations for unlink vs rmdir must match the lower layer. Cache consistency depends on GPFS upcalls or higher layers.
- **Test signals:** Cover file unlink, directory removal if supported by the opcode, missing target, permission errors under caller credentials, target replaced between stat and unlink, and post-unlink cache/upcall behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_unlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_up.c -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_up.c

- **Purpose:** Runs the GPFS FSAL upcall thread that receives kernel/filesystem events and translates them into Ganesha cache, lock, delegation, layout, and device notifications.
- **Important APIs/types/functions:** `GPFSFSAL_UP_Thread`, `callback_arg`, `pnfs_deviceid`, `glock`, `fsal_up_vector`, `up_async_lock_avail`, `up_async_lock_grant`, `up_async_delegrecall`, `up_async_layoutrecall`, `up_async_notify_device`, `up_async_update`, `invalidate`, and `invalidate_close`.
- **Control flow:** The thread registers with RCU, names itself by fsid, waits for NFS init completion unless stopped, then repeatedly initializes a GPFS callback request and calls `OPENHANDLE_INODE_UPDATE`. It handles version mismatch, interrupts, retry/fatal behavior for `EUNATCH`, thread stop, and flag masking. For each event it acquires an export reference, initializes a minimal op context, dispatches by reason to lock, delegation, layout recall, device notification, attribute update, invalidation, pause, or unknown-event handling, releases op context, and logs non-ENOENT failures.
- **State and persistence behavior:** Long-lived per-filesystem thread state is held in `struct gpfs_filesystem` (`root_fd`, `stop_thread`, `up_thread`). The thread mutates Ganesha caches asynchronously and does not persist filesystem data itself. Attribute updates can either invalidate cache or apply selected stat-derived attributes with expire-time metadata.
- **Dependencies and integration points:** Depends on GPFS callback ioctl ABI, RCU, Ganesha init/fridge/upcall APIs, export manager lookup, FSAL attr conversion, and pNFS layout/device notification types. It is the main bridge from GPFS kernel events to mdcache and NFS client callbacks.
- **Risks:** The event stream is asynchronous; comments note stale attribute races. `LAYOUT_RECALL_ANY` is not implemented beyond logging. Device notification zeroes and rebuilds the deviceid before notifying, which assumes delete-all semantics. Missing exports cause events to be skipped. Fatal behavior after repeated `EUNATCH` can terminate the process.
- **Test signals:** Cover thread startup/shutdown, init wait timeout loop, each event reason, size-change invalidation vs selective attr update, nlink-zero async update, lock grant/again notifications, delegation recall, layout recall, device delete notify, unknown events, no-export cases, and repeated GPFS detach errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/fsal_up.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/gpfs_methods.h -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/gpfs_methods.h

- **Purpose:** Defines the private GPFS export, filesystem, and object-handle structures plus method prototypes used to wire the GPFS FSAL into Ganesha.
- **Important APIs/types/functions:** `struct gpfs_fsal_export`, `struct gpfs_filesystem`, `struct gpfs_fsal_obj_handle`, `gpfs_lookup_path`, `gpfs_create_handle`, `gpfs_extract_fsid`, `gpfs_merge`, `alloc_handle`, `gpfs_open2`, `gpfs_read2`, `gpfs_write2`, `gpfs_lock_op2`, `gpfs_close2`, `gpfs_seek2`, `gpfs_io_advise`, `gpfs_share_op`, `gpfs_fallocate`, and `gpfs_create_export`.
- **Control flow:** This header has no runtime flow, but it defines the private method surface consumed by export setup and object operation tables. The object handle layout embeds `fsal_obj_handle`, a pointer to a GPFS wire handle, and a union for regular-file share/fd state or symlink content cache.
- **State and persistence behavior:** `gpfs_fsal_export` tracks root filesystem, filesystem list, export fd, pNFS DS/MDS enablement, ACL usage, and mode-change policy. `gpfs_filesystem` tracks registered FSAL filesystem, root fd, upcall stop flag, and upcall thread. `gpfs_fsal_obj_handle` tracks per-object wire handle, open file/share state, or symlink cached content.
- **Dependencies and integration points:** Included by most GPFS FSAL implementation files. It depends on GPFS NFS headers, FSAL object/export types, and neighboring implementations in `handle.c`, `file.c`, `export.c`, `fsal_mds.c`, and related operation wrappers.
- **Risks:** Because this is the central private ABI, structure changes affect allocation, container casts, method dispatch, and state lifecycle. The union requires callers to respect object type. Export pNFS flags control whether object handles use pNFS-enabled ops.
- **Test signals:** Build coverage plus runtime coverage for export creation, filesystem registration, object allocation/release for regular files and symlinks, pNFS-enabled vs non-pNFS method table selection, and open/share/fd lifecycle.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/gpfs_methods.h -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/gpfsext.c -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/gpfsext.c

- **Purpose:** Implements `gpfs_ganesha`, the single userspace bridge from the GPFS FSAL to the GPFS kernel module through the `kGanesha` ioctl, plus opcode-to-stats-index mapping and Valgrind memory annotations.
- **Important APIs/types/functions:** `gpfs_ganesha`, `gpfs_op2index`, private `struct kxArgs`, optional `valgrind_kganesha`, static `gpfs_fd`, `GPFS_DEVNAMEX`, `kGanesha`, and global stats from `fsal_stats_gpfs.c`.
- **Control flow:** On first call, `gpfs_ganesha` opens the GPFS device. If containerization support is active and the device is missing, it scans `/proc/mounts` for a `gpfs` mount and opens that directory instead. It marks the fd close-on-exec, builds a two-argument ioctl wrapper containing opcode and argument pointer, optionally marks output buffers defined for Valgrind, and issues the ioctl. If FSAL stats are enabled it times the ioctl and updates per-op counters.
- **State and persistence behavior:** Maintains a process-static GPFS ioctl fd initialized lazily. It does not persist filesystem data directly, but every caller's GPFS filesystem operation passes through this function. Stats updates mutate in-memory global counters.
- **Dependencies and integration points:** Used by all GPFS FSAL operation files. Depends on GPFS kernel headers, `/dev/ss0` style GPFS device naming, ioctl ABI, `/proc/mounts` fallback in containers, Ganesha core params, atomic stats, and logging/fatal behavior.
- **Risks:** If opening GPFS fails after a prior failure, the function calls `_exit(1)` to avoid recursive logging/deadlock paths. The static fd is shared across threads without explicit initialization locking. Container fallback parses `/proc/mounts` with a transient line buffer pointer and opens the discovered mount. Stats min/max updates are not fully atomic compound operations.
- **Test signals:** Cover first-call device open, container fallback mount open, no-device fatal path, representative ioctl success/failure, stats-enabled counter/timing updates, Valgrind-defined buffer paths for key opcodes, and `gpfs_op2index` placeholder handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/gpfsext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/handle.c -->
# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/handle.c

- **Purpose:** Owns GPFS FSAL object-handle allocation, object operation wiring, namespace operations, readdir, xattrs, wire/key conversion, release, export path lookup, and wire-handle reconstruction.
- **Important APIs/types/functions:** `alloc_handle`, `gpfs_handle_ops_init`, `gpfs_lookup_path`, `gpfs_create_handle`, static object callbacks `lookup`, `makedir`, `makenode`, `makesymlink`, `readsymlink`, `linkfile`, `read_dirents`, `renamefile`, `getattrs`, `getxattrs`, `setxattrs`, `removexattrs`, `listxattrs`, `gpfs_setattr2`, `file_unlink`, `handle_to_wire`, `handle_to_key`, and `release`.
- **Control flow:** `alloc_handle` creates a private object handle, copies and normalizes the GPFS file handle, stores type-specific regular-file or symlink state, initializes the public FSAL handle, and selects pNFS-aware ops when enabled. Operation callbacks validate object types, delegate core work to GPFSFSAL/internal helpers, allocate new handles and copy attrs for lookup/create paths, and handle post-create setattr for attributes not handled by the create mode. `read_dirents` opens a directory by handle, seeks to the cookie, calls `getdents64`, skips dot entries, looks up each child to build object handles/attrs, calls the mdcache callback, and stops on callback readahead/stop requests. Xattr callbacks call GPFS xattr opcodes and adapt NFS xattr list/value structures. `gpfs_lookup_path` opens a path, converts fd to handle, fetches xstat/ACLs with retry, resolves fsid to a registered filesystem, and allocates the root object handle. `gpfs_create_handle` reconstructs an object from a wire handle, validates fsid/FSAL ownership, fetches attrs, eagerly reads symlink content, and allocates the object.
- **State and persistence behavior:** Per-object state includes the GPFS wire handle, FSAL object metadata, regular-file global fd/share state, and optional symlink target cache. Release closes any regular-file fd, destroys fd state, finalizes the public handle, frees symlink cache, and frees the allocation. Namespace, xattr, and getattr/setattr persistence is delegated to GPFS helpers.
- **Dependencies and integration points:** This is the main GPFS object implementation registered into Ganesha via `gpfs_handle_ops_init`. It integrates with `fsal_internal.c`, `fsal_lookup.c`, create/link/rename/unlink/symlink wrappers, `file.c` I/O methods declared in `gpfs_methods.h`, pNFS object ops from `fsal_mds.c`, FSAL common fd helpers, mdcache readdir callbacks, and GPFS xattr ioctls.
- **Risks:** `read_dirents` performs lookup per entry, so directory iteration can skip entries that disappear or cross unknown filesystems and can be expensive. Symlink content cache must be refreshed correctly when requested. `handle_to_key` returns a pointer into the object, so users must not retain it after release. Xattr listing currently requires GPFS to return EOF because cookies are not supported. `gpfs_create_handle` declares `link_buff` uninitialized for non-symlinks but passes it to `alloc_handle`; `alloc_handle` only reads it for symlink type, so the implicit type guard is important.
- **Test signals:** Cover handle allocation/release for files, dirs, symlinks, pNFS ops selection, lookup and create variants, readdir cookies and disappearing entries, xattr get/set/remove/list including ERANGE/ENODATA, wire handle digest sizing, key lifetime assumptions, path lookup with ACL retry, stale/non-GPFS wire handle reconstruction, symlink cache refresh, and release-time close errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GPFS/handle.c -->
