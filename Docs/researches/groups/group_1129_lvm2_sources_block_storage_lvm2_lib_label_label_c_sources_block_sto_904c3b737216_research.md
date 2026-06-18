# Group Research: group_1129_lvm2_sources_block_storage_lvm2_lib_label_label_c_sources_block_sto_904c3b737216

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/label/label.c -->
# File Research: sources/block-storage/lvm2/lib/label/label.c

## Purpose
Implements LVM2 label discovery, label writes/removal, scan-time bcache management, selected online/hints-based scan optimizations, and the public raw device byte I/O wrappers used by other LVM modules. It is the central bridge between block devices, format-specific labellers, `lvmcache`, filters, and the bcache-backed I/O layer.

## Main Responsibilities
- Maintains the registered labeller list and dispatches format-specific `can_handle`, `read`, `write`, label initialization, and destruction operations.
- Creates and owns the process-wide `scan_bcache`, sized from `io_memory_size`, using async I/O when configured and falling back to sync I/O.
- Opens devices for scans through validated dev-cache aliases, using `O_DIRECT`, `O_NOATIME`, read-only/read-write/exclusive modes, and bcache device indexes.
- Scans device headers, validates `LABELONE` headers, sector numbers, CRCs, and labeller compatibility, then calls labeller `read` to populate `lvmcache`.
- Runs normal full label scans, cached scans, read-write scans, exclusive scans, single-device rescans, and optimized `/run/lvm/pvs_online` VG scans.
- Uses hints and device ID validation to reduce unnecessary scans while falling back to complete scans if hints are stale.
- Provides `label_read_pvid` for quick PVID reads and `label_scan_for_pvid` for locating a PVID across filtered devices.
- Provides `dev_read_bytes`, `dev_write_bytes`, `dev_write_zeros`, `dev_set_bytes`, invalidation helpers, and last-byte helpers as bcache wrappers for metadata and signature I/O.

## Important Control Flow
`label_scan` sets up bcache, refreshes the DM UUID cache, builds an all-device list, applies nodata filters first, uses hints if possible, prepares the open-file limit, and calls `_scan_list`. After scan completion it warns if discovered metadata approaches bcache size, validates hints and devices-file entries, performs extra MD-component checks, and writes new hints when appropriate.

`_scan_list` batches bcache prefetches based on available cache blocks, opens devices as needed, reads the first bcache block, copies the first 4 KiB into a local header buffer, releases the bcache block, and calls `_process_block`. Non-LVM devices are invalidated and closed unless the caller explicitly wants to retain non-LVM devices for creation workflows.

`_process_block` reruns data-dependent filters after the header block is available, clears stale cache state for filtered or now-unlabelled devices, finds the label with `_find_lvm_header`, and invokes the format labeller. Duplicate PVIDs are treated differently from metadata summary failures: duplicate devices are logged without adding normal cache info, while metadata failures can still leave usable PV information in `lvmcache`.

`label_scan_vg_online` uses `/run/lvm` online PV files from `pvscan --cache` as startup hints. It maps dev_t values into dev-cache devices, temporarily relaxes device-id filtering for unstable devnames, reads PVIDs first, applies filters, scans the remaining devices, and falls back by reporting incomplete results when metadata says more PVs are required.

Write paths ensure bcache is writable or reopen devices read-write before writing. `dev_set_last_byte` chooses a 512-byte or 4096-byte boundary from direct block sizes so bcache writes respect the device's physical/logical block size.

## Dependencies
Depends on labeller implementations, `lvmcache`, device filters, dev-cache alias validation, bcache, command context configuration, DM UUID cache, hints, device ID matching, online PV files, activation helpers for LV-backed PV invalidation, and format text layout structures for PV headers.

## Risk Notes
- `scan_bcache` is global state; setup, invalidation, and destroy ordering affects all later metadata reads and writes in the process.
- `_scan_dev_open` mutates alias lists on failed opens and verifies major/minor after opening, so error handling must preserve dev-cache consistency.
- Header scanning intentionally scans only the first `LABEL_SCAN_SECTORS` sectors and treats extra labels as suspicious.
- The nodata filter and data-dependent filter split is subtle; stale persistent filter results must be wiped before full filtering.
- Hints and online PV optimizations are performance shortcuts, not authority. Their fallback behavior protects correctness.
- `dev_write_bytes` and `dev_set_bytes` flush bcache immediately and invalidate on failure; callers rely on this for metadata consistency.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/label/label.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/label/label.h -->
# File Research: sources/block-storage/lvm2/lib/label/label.h

## Purpose
Declares the LVM on-disk label header format, in-memory label/labeller interfaces, label scan entry points, and bcache-backed device byte I/O wrappers implemented in `label.c`.

## Main Contents
- Defines `LABEL_ID`, `LABEL_SIZE`, `LABEL_SCAN_SECTORS`, and `LABEL_SCAN_SIZE`.
- Defines packed `struct label_header`, whose 32-byte on-disk layout stores the label id, label sector, CRC, payload offset, and type.
- Defines in-core `struct label` with type, sector, labeller, device, and format-specific info pointer.
- Defines `struct label_ops`, the vtable for format-specific label detection, read, write, initialization, label destruction, and labeller destruction.
- Declares scan APIs for whole-system scans, selected device scans, cached/rw/exclusive scans, online VG scans, PVID lookup, invalidation, bcache setup/open/reopen, and bcache destroy/drop.
- Declares byte I/O wrappers used by other modules instead of calling bcache directly.

## Dependencies
Includes LVM IDs, `struct device`, and bcache definitions. Forward-declares command context, filters, labellers, and logical volumes to keep the header usable across label, metadata, device, and activation code.

## Risk Notes
`LABEL_SIZE` is deliberately one sector and the header warns to think carefully before changing it. The scan constants and packed on-disk layout are format compatibility boundaries. The byte I/O wrapper declarations make this header a broad dependency beyond label scanning.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/label/label.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/locking/file_locking.c -->
# File Research: sources/block-storage/lvm2/lib/locking/file_locking.c

## Purpose
Implements the file-locking backend for LVM metadata locks. It maps LVM lock resources to lock files under the configured locking directory and connects the generic locking dispatch table to flock-based helpers.

## Main Responsibilities
- Stores the configured lock directory in `_lock_dir`.
- Releases all or command-held flocks through `_fin_file_locking` and `_reset_file_locking`.
- Builds lock filenames with `P_` prefix for the global lock and `V_` prefix for VG locks.
- Calls `lock_file` with LVM lock flags to acquire, convert, or release file locks.
- Initializes flock support, fills `struct locking_type`, creates the lock directory with SELinux context handling, and rejects read-only lock directories.

## Important Control Flow
`init_file_locking` reads `global/locking_dir`, validates/copies it, prepares SELinux directory context, creates the directory, checks for read-only filesystem access failure, and installs `_file_lock_resource` plus reset/finalize callbacks in the generic locking backend.

## Dependencies
Depends on `locking.h`, `locking_types.h`, metadata constants such as `VG_GLOBAL`, config lookup, string helpers, directory creation helpers, SELinux context helpers, and `lib/misc/lvm-flock.h`.

## Risk Notes
Lock file path construction must remain bounded by `PATH_MAX`. The global lock uses `resource + 1` to strip the leading `#` from `#global`, so resource naming conventions are part of the backend contract.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/locking/file_locking.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/locking/locking.c -->
# File Research: sources/block-storage/lvm2/lib/locking/locking.c

## Purpose
Provides the generic LVM locking facade used by commands. It initializes file locking, applies command-mode policies such as `--readonly`, `--sysinit`, and `--ignorelockingfailure`, tracks held VG locks, coordinates signal/memlock behavior, and combines local file global locks with lvmlockd global locks.

## Main Responsibilities
- Holds the active `struct locking_type` backend and lock policy state.
- Tracks the number of VG locks held and whether any write VG lock has been acquired.
- Initializes file locking and records fallback behavior when initialization fails.
- Blocks signals while acquiring locks and keeps signals blocked while VG locks are held.
- Grants or rejects lock requests according to disabled locking, readonly mode, sysinit mode, ignore-locking-failure mode, and `global/metadata_read_only`.
- Updates `lvmcache` VG lock state after successful non-global locks.
- Provides global file-lock helpers for shared, exclusive, unlock, conversion, and nonblocking modes.
- Provides `lock_global` and `lock_global_convert`, which take the local file global lock and then the lvmlockd global lock.
- Provides `sync_local_dev_names`, which drops memlock and filesystem locks before VG unlock backup handling.

## Important Control Flow
`init_locking` reads `global/wait_for_locks`, records command flags, and calls `init_file_locking`. If file locking setup fails, `--sysinit` and `--ignorelockingfailure` allow the command to proceed in a readonly-like mode; otherwise initialization fails.

`lock_vol` is the main policy gate. It skips orphan VGs, forces nonblocking flags when blocking is disabled, copies the resource name safely, then handles disabled file locking, failed file-locking fallback, readonly/sysinit combinations, and `metadata_read_only`. Real backend locking happens through `_lock_vol`, after which non-global VG lock state is mirrored in `lvmcache`.

`_lockf_global` translates string modes `ex`, `sh`, and `un` into lock flags. It preserves `cmd->lockf_global_ex` so later process-each code does not accidentally downgrade an explicitly held exclusive file global lock.

## Dependencies
Depends on file-locking backend initialization, lvmlockd global locking, activation functions, command context policy flags, memlock and filesystem lock helpers, signal helpers, and `lvmcache` lock markers.

## Risk Notes
- `--readonly --sysinit` deliberately permits activation while refusing other write locks.
- Failed lock initialization with `--ignorelockingfailure` can still permit activation, so policy checks must stay aligned with command semantics.
- Unlock failure paths update lock counts differently from normal success paths; incorrect counts can leave signals blocked or unblocked at unsafe times.
- `lock_global` must unwind the file global lock if lvmlockd global lock acquisition fails.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/locking/locking.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/locking/locking.h -->
# File Research: sources/block-storage/lvm2/lib/locking/locking.h

## Purpose
Declares LVM's generic locking API, lock mode/flag constants, special lock resource names, VG unlock helper macros, LV activation helper, and global lock entry points.

## Main Contents
- Declares locking lifecycle functions: `init_locking`, `fin_locking`, `reset_locking`, and `vg_write_lock_held`.
- Declares `lock_vol`, the central VG/global lock function.
- Defines lock type bits for read, write, and unlock plus nonblocking and conversion flags.
- Defines special resource names `VG_ORPHANS` and `VG_GLOBAL`.
- Defines mode aliases for VG read/write/unlock operations.
- Defines `unlock_vg` and `unlock_and_release_vg` macros that sync local device names, trigger VG backup if needed, unlock, and optionally release the VG object.
- Declares file/lvmlockd global lock helpers.

## Dependencies
Includes LVM IDs and config definitions, and forward-declares `struct logical_volume` and `struct volume_group`.

## Risk Notes
The `unlock_vg` macro performs more than unlocking: it may sync device names and write backups. Call sites using it inherit those side effects. The comment requiring alphabetical acquisition of multiple VG locks is a deadlock prevention rule for callers.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/locking/locking.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/locking/locking_types.h -->
# File Research: sources/block-storage/lvm2/lib/locking/locking_types.h

## Purpose
Defines the small backend interface used by `locking.c` to call a concrete locking implementation, currently file/flock locking.

## Main Contents
- Declares `lock_resource_fn`, `fin_lock_fn`, and `reset_lock_fn` callback types.
- Defines `LCK_FLOCK` as the backend flag for flock-based locking.
- Defines `struct locking_type`, containing backend flags and lock/reset/final callbacks.
- Declares `init_file_locking`, which populates a `struct locking_type`.

## Dependencies
Only requires integer types and forward declarations for command context and logical volumes.

## Risk Notes
A zero `flags` value means locking is disabled to the generic layer. Any new backend must preserve this convention because `locking.c` uses it as a policy branch.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/locking/locking_types.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/locking/lvmlockd.c -->
# File Research: sources/block-storage/lvm2/lib/locking/lvmlockd.c

## Purpose
Implements the LVM command-side client for `lvmlockd`, covering shared VG lockspaces, global/VG/LV locks, sanlock internal LV management, DLM/IDM integration, persistent reservation support hooks, lock argument parsing, LV lifecycle lock allocation/freeing, rename/remove flows, and clustered LV refresh.

## Main Responsibilities
- Tracks lvmlockd socket configuration, enabled state, connection state, and initialization failures.
- Recognizes lockd lock types: `dlm`, `sanlock`, and `idm`.
- Parses user `--lockopt` and `--setlockargs` strings into internal bit flags and validates conflicting options.
- Builds daemon requests, optionally attaching PV path lists for IDM, and normalizes daemon replies into result codes, result flags, owner details, and generation values.
- Initializes and frees lockd VGs for DLM, IDM, and sanlock.
- Creates, activates, deactivates, extends, refreshes, and removes the hidden sanlock `lvmlock` LV.
- Starts, stops, waits for, and queries VG lockspaces.
- Acquires/releases global locks, VG metadata locks, and LV locks, with mode-specific error handling and retry behavior.
- Initializes and frees LV lock metadata during `lvcreate` and `lvremove`.
- Redirects locks for LV families whose synchronization is represented by another LV, such as thin volumes, VDO volumes, COW snapshots, and cache components.
- Handles shared-lock resize exceptions and remote LV refresh after `lvresize`.
- Coordinates VG rename and VG removal with lockspace state and sanlock lease state.

## Important Control Flow
The daemon protocol is centered on `_lockd_request`. It returns `0` only when no usable result could be obtained from lvmlockd; otherwise it returns `1` even if the daemon operation result is negative. Higher-level functions then decide whether a negative result is fatal, ignorable, or a warning based on the requested mode and command context.

Sanlock VG initialization creates a hidden `lvmlock` LV sized from PV sector size, configured sanlock alignment, local host id bounds, and existing LV lock count. The LV is activated before the `init_vg` request so sanlock can initialize leases. On failure it delays briefly, deactivates/removes the internal LV, and commits metadata cleanup.

`lockd_start_vg` joins a lockspace. For sanlock it activates the internal `lvmlock` LV and passes the local host id. For IDM it builds a PV path list. It handles already-started and starting states as success-like outcomes, reports lock-manager and lease repair errors, and updates persistent reservation generation keys when required.

`lockd_global_create` handles the first sanlock VG bootstrap case where no sanlock global lock can exist until the new VG exists. It allows creation without a global lock only when lvmlockd reports no global lockspace/no lockspaces and no existing sanlock VG is visible in `lvmcache`.

`lockd_global` enforces exclusive global lock failures as hard failures, while several shared global lock failures are downgraded to read-without-global-lock warnings. It also supports adopt and repair lock options and tracks `cmd->lockd_global_ex`.

`lockd_vg` records lock results into `struct lockd_state` because the caller may not yet know whether the VG is local or shared. Shared lock failures often allow a read path to continue with warning state, while exclusive failures generally stop the command.

`lockd_lv_name` performs the actual LV lock request. It handles disabled LV locking, readonly rejection, persistent locks, adoption/repair options, IDM PV list attachment, shared-lock incompatibility, already-held locks, inactive locks on unlock, sanlock lease space refresh, and detailed negative daemon results.

`lockd_lv` decides whether the LV itself owns a lock. Thin volumes and thin pool components use the thin pool lock; VDO volumes use the VDO pool lock; COW snapshots use the origin lock; cache pool/vol internals generally do not own independent locks.

LV creation/removal code allocates or frees locks only for LV types that need them. Thin and VDO creation lock the relevant pool; COW snapshot creation locks the origin; cache pools and thin volumes may not get their own lock args. LV removal queues lock frees until the command has decided to remove all requested LVs.

## Dependencies
Depends on command context lock options, metadata and LV type helpers, activation/deactivation/refresh routines, `lvmcache`, daemon client APIs, lvmlockd client protocol constants, persistent reservation helpers, device path/PV helpers, config values such as local host id and sanlock sizing, and mount table inspection for GFS2/OCFS2 resize exceptions.

## Risk Notes
- Many functions intentionally distinguish "lvmlockd unavailable" from "daemon returned a negative operation result"; collapsing those cases would break local VG fallback and shared VG safety.
- Sanlock uses real on-disk leases in the hidden `lvmlock` LV, so activation, sizing, zeroing, extension, and cleanup order are safety-critical.
- Some shared-lock failures permit read-only progress, but exclusive lock failures must remain strict to protect metadata and orphan PV state.
- `cmd->lockopt` flags such as `skipgl`, `skipvg`, `skiplv`, adopt, repair, `shupdate`, and `norefresh` deliberately weaken or alter default locking behavior and must be audited carefully in new call paths.
- Thin, VDO, cache, COW, mirror, and RAID LVs often use indirect or no LV locks; assuming every LV has independent `lock_args` is incorrect.
- VG removal and rename require other hosts to have stopped the lockspace; sanlock global lock removal can leave the command unable to safely remove later VGs.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/locking/lvmlockd.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/locking/lvmlockd.h -->
# File Research: sources/block-storage/lvm2/lib/locking/lvmlockd.h

## Purpose
Declares the public command-side lvmlockd integration API, lock state/result/option flags, lockd LV operation flags, and stub implementations used when LVM is built without lvmlockd support.

## Main Contents
- Defines `struct lockd_state`, carrying lock result flags and generation data from VG locking into later VG read validation.
- Defines the sanlock internal LV name `lvmlock`.
- Defines LV lock flags such as no-shared-mode, persistent lock, shared-exists-ok, and thin/snapshot creation context bits.
- Defines result flags reported by lvmlockd, including missing lockspaces, missing global lockspace, duplicate global lockspaces, missing lock manager, existing shared locks, and unknown host state.
- Defines lock state failure flags used by VG lock callers.
- Defines `--lockopt` flags for force, shupdate, norefresh, skip global/VG/LV, auto/nowait, adopt, nodelay, and repair variants.
- Declares APIs for lvmlockd connection management, VG init/free/start/stop/status, global/VG/LV locks, LV creation/removal lock handling, VG rename, running lock manager discovery, LV refresh, LV lock query, lock option parsing, and sanlock lock-args changes.
- Provides inline no-op or failure stubs when `LVMLOCKD_SUPPORT` is disabled.

## Dependencies
Includes LVM logging, daemon client utilities, and lvmlockd protocol client definitions. It forward-declares `lvresize_params` and `lvcreate_params`.

## Risk Notes
The stub behavior is part of the build-time contract: local VG operations usually become no-ops without lvmlockd, while creating or using shared lock types must fail. Callers should not assume lvmlockd functions always perform locking.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/locking/lvmlockd.h -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/log/log.c -->
# File Research: sources/block-storage/lvm2/lib/log/log.c

## Purpose
Implements LVM2's central logging engine. It routes formatted messages to stderr/stdout, optional command reports, optional custom file descriptors, optional log files, syslog, systemd journal, stored error buffers, and optional external library log callbacks.

## Main Responsibilities
- Maintains global logging configuration for syslog, file logging, journal fields, indentation, suppression, message prefix, debug field selection, and internal-error abort behavior.
- Supports custom output, error, and report streams from caller-provided file descriptors with line buffering.
- Reopens standard streams safely and updates custom stream references when standard `FILE *` objects change.
- Opens debug log files, including environment-controlled epoch suffixes based on PID and `/proc/self/stat` start time.
- Supports line-limited log files through `LVM_LOG_FILE_MAX_LINES` and conditional unlinking through `LVM_EXPECTED_EXIT_STATUS`.
- Stores the first LVM error number and an optional accumulated error-message buffer up to 512 KiB.
- Deduplicates `log_error_once` messages by hashing formatted message text.
- Converts log report context/object enums to names and writes command log rows through report infrastructure.
- Formats and emits log messages in `_vprint_log`, applying verbosity, debug classes, report routing, external callback routing, journald/syslog routing, and fatal internal-error abort handling.
- Sends command records to journald when configured.
- Converts journal option strings into bit flags.

## Important Control Flow
`_vprint_log` first checks whether internal errors should be fatal based on `DM_ABORT_ON_INTERNAL_ERRORS` or config. It formats the message early when needed for stored errors, reporting, external callbacks, or deduplication. Report logging temporarily clears `_log_report.report` to avoid recursion through logging.

Visible terminal output depends on `verbose_level`, stderr forcing, warning-vs-print semantics, debug class filters, and optional debug output field masks. Log-file output is separately gated by `debug_level`, debug class filters, and critical-section suspension rules. Syslog and journald receive messages only when configured and not suppressed by critical-section rules unless `log_while_suspended` is set.

`print_log_libdm` redirects normal libdm warning-level output to the report stream and bypasses report integration for common non-error output.

## Dependencies
Depends on LVM command/log helper functions, device headers for custom fd structures, memlock critical-section state, report command-log output, file helpers, syslog, optional systemd journal support, and `/proc/self/stat` parsing for log epoch file names.

## Risk Notes
- Logging is global mutable state; concurrent or nested use must avoid report recursion and unexpected stream replacement.
- Stored error messages can grow to 512 KiB and are manually reallocated; reset ownership matters.
- `log_once` deduplication keys on formatted message text, so variable data prevents deduplication.
- Fatal internal-error behavior can be enabled by environment and calls `abort` after logging.
- Critical sections suppress file/syslog output unless explicitly configured, which avoids unsafe logging while suspended.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/log/log.c -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/lvm2/lib/log/log.h -->
# File Research: sources/block-storage/lvm2/lib/log/log.h

## Purpose
Defines LVM's logging levels, debug classes, journal/debug field flags, user-facing logging macros, system-call logging macros, and common error-return convenience macros.

## Main Contents
- Defines internal log levels from fatal through debug, plus stderr-forcing, once-only, and report-bypass bits.
- Defines `INTERNAL_ERROR` prefix used by fatal internal-error handling.
- Defines debug output/file field masks for time, command, file/line, and message fields.
- Defines journald option bits for command, output, and debug logging.
- Defines debug classes for memory, devices, activation, allocation, metadata, cache, locking, lvmpolld, dbus, and I/O.
- Maps common macros such as `log_error`, `log_warn`, `log_print`, `log_verbose`, `log_debug_*`, and `stack` onto lower-level `LOG_LINE`/`LOG_LINE_WITH_ERRNO` primitives.
- Defines system-call error helpers that include `strerror(errno)`.
- Defines convenience macros such as `return_0`, `return_NULL`, `goto_out`, and `goto_bad` that log a debug backtrace before control transfer.

## Dependencies
Includes only errno/string headers directly, but expects lower-level logging primitives and mode helpers to be available through broader LVM logging includes.

## Risk Notes
The visible behavior of many LVM commands is shaped by these macros: `log_print` is warning-level without forced stderr, `log_warn` forces stderr, and `stack` is just a debug message. Changing level mappings affects terminal output, reports, syslog, journald, and tests that inspect command output.
<!-- END FILE RESEARCH: sources/block-storage/lvm2/lib/log/log.h -->