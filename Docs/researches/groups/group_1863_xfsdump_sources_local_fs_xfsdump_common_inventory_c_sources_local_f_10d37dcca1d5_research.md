# Group Research: group_1863_xfsdump_sources_local_fs_xfsdump_common_inventory_c_sources_local_f_10d37dcca1d5

Scope: `Docs/research_subset_a.md` only. Files read completely: all listed `sources/local-fs/xfsdump` common, build, and packaging files in this group.

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/inventory.c -->
# File Research: sources/local-fs/xfsdump/common/inventory.c

## Role

This file is the public inventory API implementation used by xfsdump/xfsrestore callers to open the inventory database, query previous dump sessions, create new session records, add streams, add media-file records, and close inventory tokens.

It is a facade over the private inventory implementation in `inventory_priv.h` and related inventory modules.

## Major Responsibilities

- Open an inventory database for a filesystem by UUID, mount point, or device path via `inv_open()`.
- Select or create a storage object for session records.
- Close inventory database tokens and the session lock descriptor in `inv_close()`.
- Query the latest previous dump time or session at a level less than or equal to a requested dump level.
- Create a write session with filesystem/session UUIDs, label, level, stream count, timestamp, mount point, and device path.
- Create per-stream records under a session.
- Add per-media-file records to a stream.
- Close streams and sessions while updating end times and interrupted status.

## Key Flows

`inv_open()` initializes the inventory index with `init_idb()`, obtains the current storage object with `get_storageobj()`, checks session-counter capacity, and creates a new storage object/index entry when full. The returned token contains the inventory index descriptor, storage-object descriptor, and index header offset.

`inv_writesession_open()` ensures the fstab-style inventory entry is present, allocates an on-disk session record, fills session identity and label/path fields, creates a session header, serializes the session under an exclusive storage-object lock, and updates inventory start time for a newly created index entry.

`inv_stream_open()` allocates a stream token, locks the session file, reads the session header and session record, reserves the next stream slot if below `s_max_nstreams`, writes the updated session, then writes an empty stream header.

`inv_put_mediafile()` builds an `invt_mediafile_t` and delegates insertion to `put_mediafile()` under an exclusive storage-object lock. The most recent media-file copy remains owned by the stream token until `inv_stream_close()`.

## Query Behavior

The last-time and last-session functions all use `search_invt()` with callback predicates:

- `tm_level_lessthan`
- `lastsess_level_lessthan`
- `lastsess_level_equalto`

They return `BOOL_FALSE` only for search errors. A successful search that finds nothing is represented by a null output pointer.

## Locking And State

- Uses file locks through `INVLOCK()` for storage-object serialization.
- Uses `sess_lock()`/`sess_unlock()` around stream slot allocation.
- Uses a global `sesslock_fd`, closed by `inv_close()` and on some `inv_open()` failure paths.
- Session and stream tokens are heap-allocated private descriptor structures.

## Notable Gaps

`inv_get_inolist()` is effectively disabled under `#ifdef NOTDEF` and currently returns `1` without filling an inode list.

`inv_get_session()` contains assertions and comments but no implementation or return value in this file.

The file uses fixed-size `strcpy()` into inventory label/path fields, relying on callers to respect `INV_STRLEN`.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/inventory.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/inventory.h -->
# File Research: sources/local-fs/xfsdump/common/inventory.h

## Role

This header declares xfsdump's abstract inventory subsystem API and public inventory data structures.

The inventory records every dump session unless explicitly removed and exposes filesystem/session/media queries without exposing the private on-disk database layout.

## Public Types

- `inv_predicate_t`: lookup selector for UUID, mount point, or device path.
- `inv_stream_t`: public stream summary, including interruption state, start/end inode positions, and media-file count.
- `inv_session_t`: public dump-session summary with filesystem UUID, session UUID, stream array, time, level, label, mount point, and device path.
- `inv_mediafile_t`: public media-file descriptor with media object UUID, inode range, and label.
- `inv_inolist_t`: linked list of inventory-related inode numbers.
- Opaque token types:
  - `inv_idbtoken_t`
  - `inv_sestoken_t`
  - `inv_stmtoken_t`

## API Surface

The header declares lifecycle functions:

- `inv_open()` / `inv_close()`
- `inv_writesession_open()` / `inv_writesession_close()`
- `inv_stream_open()` / `inv_stream_close()`
- `inv_put_mediafile()`

It also declares query and reconstruction functions:

- `inv_lasttime_level_lessthan()`
- `inv_lastsession_level_lessthan()`
- `inv_lastsession_level_equalto()`
- `inv_get_inolist()`
- `inv_get_session()`
- `inv_put_session()`

## Path Helpers

The inventory path macros resolve through functions:

- `INV_DIRPATH` -> `inv_dirpath()`
- `INV_FSTAB` -> `inv_fstab()`
- `inv_lockfile()`

This lets the implementation decide the active inventory directory and compatibility paths.

## Constraints

`INV_STRLEN` is fixed at 128 bytes for labels, mount points, and device paths. Public structs expose fixed buffers matching that size.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/inventory.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/lock.c -->
# File Research: sources/local-fs/xfsdump/common/lock.c

## Role

This file implements a simple global critical-region lock for xfsdump/xfsrestore.

It wraps the ordered `qlock` abstraction with a single process-wide lock handle.

## Behavior

- `lock_init()` asserts the lock has not already been initialized and allocates a `QLOCK_ORD_CRIT` qlock.
- `lock()` acquires the global critical lock.
- `unlock()` releases it.

## Dependencies

The implementation depends on `qlock_alloc()`, `qlock_lock()`, and `qlock_unlock()`. The ordering ordinal is defined in `qlock.h`.

## Assumptions

The file does not expose a destroy path. The global lock is expected to live for the lifetime of the process.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/lock.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/lock.h -->
# File Research: sources/local-fs/xfsdump/common/lock.h

## Role

This header declares the global critical-region lock API.

## API

- `lock_init()`
- `lock()`
- `unlock()`

It is used by shared components such as stream tracking to serialize updates without exposing the underlying `qlock` implementation.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/lock.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/main.c -->
# File Research: sources/local-fs/xfsdump/common/main.c

## Role

This is the shared `main()` implementation for xfsdump and xfsrestore, compiled under `DUMP` or `RESTORE`.

It coordinates process bootstrap, command-line preprocessing, logging, resource limits, inventory setup, drive/media/content initialization, signal handling, worker thread supervision, progress reporting, and interactive interrupt control.

## Startup Sequence

`main()` performs these steps:

- Verifies basic integer type sizes.
- Initializes locale/gettext.
- Initializes message logging in multiple phases.
- Records the parent pthread ID and registers `mlog_exit_flush()` with `atexit()`.
- Expands an option file if `GETOPT_OPTFILE` is present.
- Parses common options for help, progress reports, and stack limits.
- Initializes stream tracking.
- Adjusts process resource limits.
- Initializes the global lock and remote-tape warning behavior.
- Determines system page size.
- Captures the current working directory.
- Initializes the inventory base path.
- Handles help/version and inventory-print-only modes.
- For dump builds, requires effective UID root after inventory-print handling.
- Initializes dialog, child manager, drive manager, global headers, content, and media/drive streams.

## Execution Modes

Pipeline mode is detected when the first drive is an unnamed pipe. In pipeline mode, the program avoids the full multi-threaded signal/dialog supervisor and runs a single content stream directly.

Non-pipeline mode initializes all drives, creates one child thread per stream via `cldmgr_create()`, and enters a parent loop that joins child exits, processes signal flags, emits progress reports, and requests orderly stop/abort when needed.

## Signal Handling

`main.c` ignores `SIGPIPE` and treats write errors as normal I/O failures.

In non-pipeline mode it blocks and handles:

- `SIGINT`: optional status/control dialog; can request stop.
- `SIGHUP`: disables dialogs and requests stop.
- `SIGTERM`: disables dialogs and requests stop.
- `SIGQUIT`: requests abort/core behavior.
- `SIGALRM` and `SIGUSR1`: wakeups/progress handling.

`preemptchk()` is the cooperative preemption hook used by content code. It briefly releases pending signals at safe points, handles progress-only checks, and returns whether interruption was requested.

## Interactive Dialog

`sigint_dialog()` presents status/control choices through `dlog`:

- Interrupt the session.
- Change verbosity per subsystem or globally.
- Display I/O metrics.
- Restore-only inventory/remaining-object displays.
- Confirm media changes.
- Enable, disable, or change progress reports.
- Toggle log message levels, subsystems, and timestamps.

The dialog also prints content status lines and has timeout/default behavior.

## Option File Parsing

`loadoptfile()` scans for one option-file argument, opens and validates a regular file, concatenates executable name, option-file contents, and remaining command-line args into one buffer, tokenizes with quote/backslash awareness, strips quotes/escapes, and replaces `argc`/`argv`.

Supporting helpers are `strpbrkquotes()`, `stripquotes()`, and `shiftleftby1()`.

## Resource Limits

`set_rlimits()` normalizes resource limits:

- Ensures stack soft limit is within configured min/max bounds.
- Raises or lowers `RLIMIT_STACK` when possible.
- Sets file size and CPU soft limits toward hard/infinite limits.
- Restore builds also derive available virtual memory for tree/content budgeting.

## Shutdown And Exit Status

The parent loop requests stop through `cldmgr_stop()` and uses deadlines to escalate stuck shutdowns to abort/core. After all children exit, `content_complete()` determines whether the dump/restore completed, was interrupted, or remained incomplete. Final exit is recorded through `mlog_exit()` with richer RV hints where possible.

## Usage Output

`usage()` prints option summaries for dump or restore builds, with many options conditionally exposed under `REVEAL`.

## Important Globals

The file owns shared process state including:

- `progname`
- `homedir`
- `pipeline`
- `stdoutpiped`
- `parenttid`
- `sistr`
- `pgsz`
- `pgmask`
- progress-report timers
- signal-received flags
- stop/interruption state
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/main.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/media.c -->
# File Research: sources/local-fs/xfsdump/common/media.c

## Role

This file selects and initializes the media strategy used by xfsdump/xfsrestore and creates one `media_t` manager descriptor per drive stream.

It sits between the drive layer and media strategy implementations.

## Strategy Selection

The file declares two external strategies:

- `media_strategy_simple`
- `media_strategy_rmvtape`

`media_create()` builds generic media descriptors for every drive, lends them to each strategy in precedence order, and selects the first strategy whose `ms_match()` callback accepts the current command line and drive setup.

## Media Label Handling

For dump builds, `media_create()` scans command-line options for a media label option and rejects duplicates or missing values. If none is provided, it uses an empty label.

Each write media header receives the selected label and, for dump builds, a new media UUID. Restore builds clear the media UUID.

## Initialization Flow

After strategy selection:

- The chosen strategy is assigned to each `media_t`.
- Each media write header receives the selected strategy ID.
- `ms_create()` is called for full strategy initialization.
- `media_init()` and `media_complete()` dispatch to strategy callbacks.

## Header Bridging

`media_get_upper_hdrs()` returns pointers to:

- global read/write headers
- media-header upper-layer read/write buffers
- their sizes

This lets upper layers place their own headers inside the media header reserved area.

## Allocation

`media_alloc()` obtains read/write media-header storage from `drive_get_upper_hdrs()`, verifies expected sizes, records drive/header pointers in `media_t`, sets the media label, and initializes the media ID.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/media.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/media.h -->
# File Research: sources/local-fs/xfsdump/common/media.h

## Role

This header defines the common media-file header layout and media strategy IDs.

The header is embedded in the drive header's upper area and is read/written at media-file boundaries.

## `media_hdr_t`

The fixed media header records:

- current and previous media labels
- current and previous media UUIDs
- media object index
- media file index
- dump file index
- dump/media combined indexes
- dump index within media
- media strategy ID
- strategy-specific 128-byte area
- upper-layer private area

`MEDIA_HDR_SZ` is derived from the drive header upper area size, and `media.c` asserts that the layout fits.

## Terminator Macros

`MEDIA_TERMINATOR_CHK()` and `MEDIA_TERMINATOR_SET()` mark media files as terminators using the first byte of `mh_specific`. This is noted as an artifact of the original removable-tape strategy.

## Strategy IDs

- `MEDIA_STRATEGY_SIMPLE`
- `MEDIA_STRATEGY_RMVTAPE`
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/media.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/media_rmvtape.h -->
# File Research: sources/local-fs/xfsdump/common/media_rmvtape.h

## Role

This header defines removable-tape media-specific header and context structures.

It is used by the `rmvtape` media strategy to interpret the `media_hdr_t.mh_specific` region.

## Structures

`media_rmvtape_spec_t` overlays the 128-byte media-specific header area. It contains:

- `mrmv_flags`
- padding to fill the reserved region

`media_context_t` records media/dump UUIDs and media/dump labels for the removable-tape strategy.

## Flags And Capability Macros

- `RMVMEDIA_TERMINATOR_BLOCK` marks a terminator block.
- `TERM_IS_SET()` checks that flag.
- `CAN_OVERWRITE()`, `CAN_APPEND()`, and `CAN_BSF()` test drive capabilities needed by removable tape behavior.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/media_rmvtape.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/mlog.c -->
# File Research: sources/local-fs/xfsdump/common/mlog.c

## Role

This file implements xfsdump/xfsrestore message logging, verbosity parsing, thread-aware log prefixes, structured exit recording, and final dump/restore status summaries.

It is shared by dump and restore builds.

## Initialization

`mlog_init0()` chooses the default output stream and initializes all subsystem verbosity levels to verbose.

`mlog_init1()` parses verbosity-related options:

- general or per-subsystem verbosity through `GETOPT_VERBOSITY`
- show log level
- show log subsystem
- timestamp messages

It supports numeric and symbolic levels: silent, verbose, trace, debug, and nitty.

`mlog_init2()` allocates the ordered `QLOCK_ORD_MLOG` lock.

## Logging Behavior

`mlog()` wraps `mlog_va()`. `mlog_va()`:

- Extracts message level and subsystem.
- Filters messages above the configured subsystem level.
- Optionally locks the mlog qlock.
- Prints prefixes including program name, optional timestamp, subsystem, level, and stream/drive index when applicable.
- Adds NOTE, WARNING, or ERROR labels when requested.
- Writes the formatted message and flushes the log file.

`MLOG_NOLOCK` is supported for contexts where locking is unsafe or already protected.

## Subsystems

The file defines names for general, process, drive, media, inventory, dump inomap or restore tree, and excluded files. The exact fifth subsystem depends on build mode.

## Exit Recording

`mlog_exit()` and `mlog_exit_hint()` are implemented through file/line-aware macros. They record:

- traditional exit code
- internal `rv_t` reason code
- optional late hint reason

The parent thread stores process-level exit data. Worker/content threads store exit status through the `stream` subsystem.

The first exit value is preserved because deeper callers often have the most specific reason. Hints use the last value because they are intended to improve final diagnosis near the final failure point.

## Return-Code Mapping

The file maps every `rv_t` value to a displayed code and human-readable description, including media, drive, corruption, interrupt, incomplete, permission, compatibility, inventory, and usage conditions.

## Final Summary

`mlog_exit_flush()` emits final per-stream and overall status unless logging is silent or the run only printed usage. It scans running/zombie streams, combines each stream's return and hint, reports drive path and reason, and derives an overall status such as INTERRUPT, QUIT, INCOMPLETE, or the traditional exit-code string.

## Utility

`fold_init()` builds fixed-width fold/separator strings used by the interrupt dialog.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/mlog.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/mlog.h -->
# File Research: sources/local-fs/xfsdump/common/mlog.h

## Role

This header declares the message logging interface, log levels, subsystem selectors, modifier flags, and exit-summary helpers.

## Log Levels And Modifiers

Levels are encoded in the low byte:

- silent/normal
- verbose
- trace
- debug
- nitty

Modifier flags include bare output, NOTE/WARNING/ERROR labels, and no-lock logging.

## Subsystems

The header assigns subsystem IDs and bit-shifted subsystem flags for general, process, drive, media, inventory, dump/restore-specific subsystem, and excluded files.

## Exported State

The logging configuration exposes:

- `mlog_level_ss[]`
- `mlog_showlevel`
- `mlog_showss`
- `mlog_timestamp`
- `mlog_ss_names[]`

These are mutable from the interactive signal dialog.

## API

The header declares staged initialization, stream-count reporting, level override, formatted logging, exit recording/hinting, final exit flush, explicit lock/unlock for dialog integration, and fold-line generation.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/mlog.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/openutil.c -->
# File Research: sources/local-fs/xfsdump/common/openutil.c

## Role

This file provides small helpers for constructing paths and opening or creating temporary/housekeeping files.

## Path Construction

`open_pathalloc()` allocates a pathname from directory, basename, and optional PID suffix. It special-cases `/` so generated paths do not contain a double slash.

PID suffixes use `.<pid>`, with room for a 64-bit PID representation.

## File Helpers

- `open_trwp()` creates/truncates a read-write file with user read/write permissions.
- `open_erwp()` creates a read-write file exclusively.
- `open_rwp()` opens an existing file read-write.
- `mkdir_tp()` creates a user-only directory.

The create helpers log failures through `mlog()`.

## Directory/Basename Helpers

`open_trwdb()`, `open_erwdb()`, and `open_rwdb()` combine path allocation with the corresponding pathname-based open helper and free the temporary path buffer.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/openutil.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/openutil.h -->
# File Research: sources/local-fs/xfsdump/common/openutil.h

## Role

This header declares utility functions for constructing pathnames and opening or creating support files.

## API

- `open_pathalloc()`
- `open_trwdb()` / `open_trwp()`
- `open_rwdb()` / `open_rwp()`
- `open_erwdb()` / `open_erwp()`
- `mkdir_tp()`

The API is centered on read-write temporary or housekeeping files with optional PID-suffixed names.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/openutil.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/path.c -->
# File Research: sources/local-fs/xfsdump/common/path.c

## Role

This file implements pathname helper functions for relative-to-absolute conversion, normalization, prefix tests, and path difference extraction.

## Public Functions

`path_beginswith()` checks whether `path` begins with `base`.

`path_diff()` returns a newly allocated suffix of an absolute path relative to an absolute base, or null if the path does not begin with the base or has no suffix.

`path_reltoabs()` converts a local relative path into `basedir/path`, normalizes local paths, and preserves remote-style paths containing `:`.

`path_normalize()` canonicalizes absolute paths by removing empty components and `.`, and resolving `..` unless it would escape above root.

## Internal Model

The implementation tokenizes a path with `pem_t`, stores accepted path elements in a fixed-size `pa_t` array, peels entries for `..`, then generates a normalized absolute pathname.

## Limits And Assumptions

- `path_normalize()` asserts paths are absolute.
- The element array has a fixed maximum of 1024 components.
- Returned strings are heap allocated.
- Remote paths are detected only by the presence of `:`.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/path.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/path.h -->
# File Research: sources/local-fs/xfsdump/common/path.h

## Role

This header declares pathname utility functions.

## API

- `path_reltoabs()`
- `path_normalize()`
- `path_diff()`
- `path_beginswith()`

The functions return allocated normalized paths where applicable and are used by higher-level command/path handling.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/path.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/qlock.c -->
# File Research: sources/local-fs/xfsdump/common/qlock.c

## Role

This file implements ordered mutex locks and counting semaphores used by xfsdump's multithreaded components.

## Ordered Locks

`qlock_alloc()` creates a pthread mutex associated with an ordinal. A process-wide bitmap ensures each ordinal is allocated only once.

`qlock_lock()` enforces two invariants per thread using a thread-local ordinal bitmap:

- the same lock ordinal is not already held
- no lower ordinal lock is currently held when acquiring this lock

Violations are logged and asserted. This implements deadlock-detection/order enforcement according to the project's ordinal scheme.

`qlock_unlock()` verifies ownership in the thread-local bitmap, clears it, and unlocks the pthread mutex.

## Semaphores

The qsem API wraps POSIX semaphores:

- `qsem_alloc()`
- `qsem_free()`
- `qsemP()`
- `qsemV()`
- `qsemPwouldblock()`
- `qsemPavail()`

These are used by the ring buffer implementation to coordinate ready and active message queues.

## Assumptions

The implementation relies heavily on `assert()` for allocation, pthread, and semaphore success. It does not provide runtime recovery for misuse or failed synchronization primitives.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/qlock.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/qlock.h -->
# File Research: sources/local-fs/xfsdump/common/qlock.h

## Role

This header defines the ordered lock and counting semaphore abstraction.

## Lock Ordering

The lock ordinals are:

- `QLOCK_ORD_CRIT`
- `QLOCK_ORD_WIN`
- `QLOCK_ORD_PI`
- `QLOCK_ORD_MLOG`

The comments state that subsequent lock acquisitions must have lower ordinals than currently held locks, and the implementation checks this through per-thread bitmaps.

## API

Lock API:

- `qlock_alloc()`
- `qlock_lock()`
- `qlock_unlock()`

Semaphore API:

- `qsem_alloc()`
- `qsem_free()`
- `qsemP()`
- `qsemV()`
- `qsemPwouldblock()`
- `qsemPavail()`

Handles are opaque `void *` values.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/qlock.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/rec_hdr.h -->
# File Research: sources/local-fs/xfsdump/common/rec_hdr.h

## Role

This header defines the drive-specific tape record header used by tape-oriented drive strategies.

The structure is embedded in the drive header's `dh_specific` area for the first record and appears at the start of subsequent records.

## `rec_hdr_t`

The header records:

- magic and format version
- tape block size
- record size
- drive capability flags
- record file offset
- first mark offset within the record
- used byte count
- checksum and checksum-enabled flag
- dump UUID
- padding to match the drive-specific header region

## Semantics

The comments document that the first page of every record is reserved for the header and that the first record of a media file contains only header information, with user data beginning in the second record.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/rec_hdr.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/ring.c -->
# File Research: sources/local-fs/xfsdump/common/ring.c

## Role

This file implements the read-ahead/write-ahead ring abstraction used by drive managers.

A ring is a fixed set of aligned buffers and messages circulating between a client thread and one worker thread.

## Creation

`ring_create()` allocates:

- a ring descriptor
- ready and active semaphores
- message descriptors
- page-aligned buffers via `memalign(PGSZ, bufsz)`

It optionally pins buffers with `mlock()`, maps pinning failures to `E2BIG` or `EPERM`, and starts a worker thread with `cldmgr_create()`.

## Queue Model

Messages move in strict order:

ready queue -> client -> active queue -> worker -> ready queue

`ring_get()` removes the next ready message for the client. `ring_put()` places the client's message on the active queue. Both sides track exactly one held message and assert queue order and message indexes.

## Worker Behavior

`ring_worker_entry()` blocks selected signals, then processes active messages:

- `RING_OP_READ`: invokes client read callback.
- `RING_OP_WRITE`: invokes client write callback.
- `RING_OP_NOP`: acknowledges without I/O.
- `RING_OP_TRACE`: returns ignored status.
- `RING_OP_RESET`: leaves ignore mode and acknowledges reset.
- `RING_OP_DIE`: acknowledges shutdown and exits.

On read/write callback error, the worker enters ignore mode and returns subsequent I/O messages with `RING_STAT_IGNORE` until reset.

## Reset And Destroy

`ring_reset()` sends a reset message, drains ready messages until `RING_STAT_RESETACK`, asserts all messages have returned, reinitializes indexes/statuses, and refills the ready semaphore.

`ring_destroy()` sends a die message, waits for `RING_STAT_DIEACK`, frees semaphores, and frees the ring descriptor.

## Metrics

The ring tracks message attempts, blocking counts, first I/O time, and total I/O count for client and worker performance reporting.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/ring.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/ring.h -->
# File Research: sources/local-fs/xfsdump/common/ring.h

## Role

This header declares the ring buffer/message protocol for asynchronous read-ahead and write-ahead I/O.

## Message Protocol

`ring_msg_t` contains:

- operation
- status
- callback return value
- caller-owned 64-bit user field
- buffer pointer
- private message index and location

Operations include read, write, nop, trace, reset, and die. Status values include init, ok, error, nop ack, ignore, reset ack, and die ack.

## Ring State

`ring_t` exposes performance counters and keeps private queue indexes, semaphores, message array, callback pointers, and client context.

## API

- `ring_create()`
- `ring_get()`
- `ring_put()`
- `ring_reset()`
- `ring_destroy()`

The header comments fully document the required message circulation order, error/ignore behavior, reset semantics, and worker shutdown behavior.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/ring.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/stream.c -->
# File Research: sources/local-fs/xfsdump/common/stream.c

## Role

This file tracks stream/thread lifecycle and exit status for xfsdump/xfsrestore.

It maps pthread IDs to stream indexes, running/zombie/free states, and recorded exit code/return/hint values.

## Data Model

A static `spm` array contains up to `STREAM_SIMMAX * 3` entries, allowing multiple threads to be associated with the same stream index, such as a content thread and a drive worker thread.

Each entry stores:

- stream state
- pthread ID
- stream index
- exit code
- exit return code
- exit hint code

## Lifecycle

- `stream_init()` clears the table.
- `stream_register()` finds a free entry and records a running thread.
- `stream_dead()` marks a matching thread zombie; caller must hold the global lock.
- `stream_free()` clears an entry.

## Queries

- `stream_find_all()` returns tids whose entries match requested states.
- `stream_getix()` returns the running stream index for a tid and is intentionally lock-free because it is called from logging paths.
- `stream_get_exit_status()` returns selected status fields under lock.
- `stream_cnt()` counts unique running stream indexes.

## Exit Status Updates

`stream_set_code()`, `stream_set_return()`, and `stream_set_hint()` are generated through a macro that only allows the owning pthread to update its own running stream entry. Foreign updates are logged and ignored.

## Locking

Most table mutation and snapshot access uses the global `lock()`/`unlock()` critical section. `stream_find()` itself does not lock and is used by callers that already hold the lock or by special logging contexts.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/stream.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/stream.h -->
# File Research: sources/local-fs/xfsdump/common/stream.h

## Role

This header declares stream tracking constants, states, exit codes, and APIs.

## Constants

- `STREAM_SIMMAX` is 20 simultaneous streams.
- Stream exit codes distinguish success, stop, abort, and core request.
- `stream_state_t` has free, running, and zombie states.

## API

The header declares initialization, registration, death/freeing, lookup, exit-status setters, exit-status query, and active stream counting.

One declaration, `stream_exists()`, appears in the header but is not implemented in the read `stream.c`.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/stream.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/timeutil.c -->
# File Research: sources/local-fs/xfsdump/common/timeutil.c

## Role

This file provides `time32_t` wrappers around C library time formatting routines.

## Functions

- `ctime32()` casts a `time32_t` to `time_t` and calls `ctime()`.
- `ctime32_r()` casts a `time32_t` to `time_t` and calls `ctime_r()`.
- `ctimennl()` formats time with `ctime32()` and removes the trailing newline from the returned static buffer.

## Assumptions

The conversion assumes the current platform `time_t` can represent the supplied 32-bit time value.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/timeutil.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/timeutil.h -->
# File Research: sources/local-fs/xfsdump/common/timeutil.h

## Role

This header declares helper functions for formatting `time32_t` values.

## API

- `ctime32()`
- `ctime32_r()`
- `ctimennl()`

The API exists to keep xfsdump's on-disk or compatibility time type separate from platform `time_t` at call sites.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/timeutil.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/ts_mtio.h -->
# File Research: sources/local-fs/xfsdump/common/ts_mtio.h

## Role

This header carries SGI/IRIX-style magnetic tape ioctl compatibility definitions used by xfsdump tape support.

It supplements Linux `<sys/mtio.h>` with historical tape operation codes, status structures, capability flags, and vendor-specific tape command structures.

## Operation Codes

The header aliases and defines tape operation subcodes for:

- retention
- reserve/release/persistent reservation operations
- append-to-file behavior
- setmark skipping
- audio/data mode switching
- SCSI-specific special operations
- legacy ABI operation mappings

## Status Structures

Defined status/accounting structures include:

- `mtget_sgi`
- `old_mtget`
- `mt_prsv`
- `mtgetext_t`
- `mtacct_t`
- `mtvid`
- `mtblkinfo`

These provide tape status, position, residuals, partition information, capabilities, byte/read/write counters, persistent reservation state, and block-size metadata.

## SCSI And Audio Structures

The header defines structures for SCSI log reads, audio DAT positioning/timecode, drive capability reporting, front-panel messages, vendor-specific position payloads, and tape attributes.

Audio support includes BCD timecode fields and positioning modes for program, absolute, running, and program-relative time.

## Ioctl Numbers

`MTIOCODE()` constructs ioctl numbers. The header defines many SGI-style ioctls such as:

- `MTIOCGET_SGI`
- `MTIOCGETBLKSIZE`
- `MTSCSIINQ`
- `MTSPECOP`
- `MTIOCGETBLKINFO`
- `MTANSI`
- `MTCAPABILITY`
- `MTSETAUDIO`
- `MTGETAUDIO`
- `MTSCSI_SENSE`
- `MTSCSI_RDLOG`
- `MTIOCGETEXT`
- `MTACCT`
- `MTSETVID`
- `MTPRSV`

## Capability And Status Flags

The file defines drive position/status bits, error-register bits, and many `MTCAN_*` capability bits covering backspacing, append, setmarks, partitions, media removal, sync, EOD handling, variable/fixed block sizes, density/speed, compression, fast seek, load behavior, and audio support.

## User Request Codes

The final section defines `MTR_*` request codes used in extended tape status to identify the last user request, including read, write, filemark operations, seeking, erase, unload, persistent reservation operations, load, and filemark-positioning variants.

## Compatibility Nature

This header is primarily a compatibility surface for old SGI tape-driver behavior. Much of it documents device-specific or historical behavior that xfsdump's tape paths may still need to compile against.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/ts_mtio.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/types.h -->
# File Research: sources/local-fs/xfsdump/common/types.h

## Role

This header defines common project-wide scalar types, limits, booleans, return codes, and miscellaneous compatibility typedefs.

## Types And Macros

It includes standard integer types, defines member-size/offset helpers, fixed page-size constants, aliases such as `size32_t`, `size64_t`, `time32_t`, `xfs_ino_t`, `ix_t`, and `bool_t`.

It also provides `constpp` for `getsubopt()` token arrays.

## Limits

The `MKMAX`, `MKSMAX`, and `MKUMAX` macros derive signed/unsigned maximums for many project types, including 32-bit, 64-bit, size, offset, inode, time, and index types.

## Booleans

Boolean values are integer constants:

- true
- false
- unknown
- error

## Return Codes

`rv_t` enumerates internal result reasons used across dump/restore and by `mlog` final summaries. Values cover success, media conditions, EOD/EOF/EOM, resource errors, interruption, corruption, quit, drive timeout/media/protection problems, core, option/init/permission/compatibility errors, incomplete runs, inventory errors, usage-only, already-exists, none, and unknown.

## Compatibility Typedefs

The header aliases system/XFS structures such as `stat_t`, `stat64_t`, `getbmapx_t`, and `fsdmidata_t`.

## Preemption Flags

Defines `PREEMPT_FULL` and `PREEMPT_PROGRESSONLY` for cooperative preemption/progress checks.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/types.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/util.c -->
# File Research: sources/local-fs/xfsdump/common/util.c

## Role

This file implements general-purpose buffer, XFS bulkstat, inode-group, directory iteration, and numeric parsing utilities.

## Buffer Helpers

`write_buf()` adapts a manager-style get-buffer/write-buffer interface to write an existing caller buffer or a zero-filled logical buffer in chunks.

`read_buf()` adapts a manager-style read/return-buffer interface to fill or discard a caller buffer in chunks and reports the first read status.

`strncpyterm()` wraps `strncpy()` and always null-terminates the destination when size is nonzero.

## XFS Bulkstat Iteration

`bigstat_iter()` repeatedly calls `XFS_IOC_FSBULKSTAT`, filters directory/non-directory entries according to selector flags, retries unstable entries with `bigstat_one()`, invokes a caller callback per selected inode, supports optional seek and preemption callbacks, and returns syscall/preemption errors separately from callback status.

`bigstat_one()` retrieves one inode's `xfs_bstat` via `XFS_IOC_FSBULKSTAT_SINGLE`.

## Inode Group Iteration

`inogrp_iter()` uses `XFS_IOC_FSINUMBERS` to enumerate inode groups in batches and invokes a caller callback for each `xfs_inogrp`.

## Directory Iteration

`diriter()` opens a directory by filesystem handle and inode stat, reads directory entries through `getdents_wrap()`, skips `.` and `..`, calls `bigstat_one()` for each entry, skips too-large inode numbers when large-file directory entries are unavailable, and invokes the caller's callback with stat data and name.

It returns distinct states for syscall failure, callback stop, and normal completion.

## Numeric Parsing

`cvtnum()` parses integer strings with optional suffixes:

- no suffix: raw integer
- `b`: multiply by supplied block size
- `k`: multiply by 1024
- `m`: multiply by 1024 * 1024

Invalid strings return `-1`.

## Error Handling

The utility functions log many recoverable directory/stat iteration warnings and continue where possible, especially for transient inode state or unreadable directory entries.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/util.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/common/util.h -->
# File Research: sources/local-fs/xfsdump/common/util.h

## Role

This header declares general utility APIs for manager-buffer I/O, string copying, XFS inode iteration, directory iteration, and pointer alignment.

## Buffer API

Declares callback typedefs and helpers:

- `write_buf()`
- `read_buf()`

These bridge manager zero-copy-ish buffer interfaces with simple caller-owned buffers.

## XFS Iteration API

Defines selector flags:

- `BIGSTAT_ITER_DIR`
- `BIGSTAT_ITER_NONDIR`
- `BIGSTAT_ITER_ALL`

Declares callback types and functions:

- `bigstat_iter()`
- `bigstat_one()`
- `inogrp_iter()`
- `diriter()`

These are central helpers for walking XFS filesystem metadata by inode and directory entry.

## Miscellaneous

- `strncpyterm()` guarantees null termination.
- `COPY_LABEL()` copies fixed global label buffers.
- `ALIGN_PTR()` aligns a pointer upward to an alignment boundary.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/common/util.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/configure.ac -->
# File Research: sources/local-fs/xfsdump/configure.ac

## Role

This is the Autoconf input for configuring the xfsdump build.

## Package Setup

It initializes package metadata as `xfsdump` version `3.3.0`, requires Autoconf 2.50, sets auxiliary and macro directories, selects `common/main.c` as a source probe, generates `include/config.h`, and defaults prefix to `/usr`.

## Feature Options

It defines configure options for:

- shared library use
- gettext support
- lib64 support

It avoids appending `64` when the configured library directory already ends in `lib64`.

## Install Directories

It chooses root install directories. For default `/usr`-style installs, important tools go to `/sbin` and root libraries to `/<base_libdir>`. Nonstandard prefixes use normal `sbindir` and `libdir`.

## Localization

It builds `LOCALIZED_FILES` by finding all `.c` files under the source tree and substituting them for localization tooling.

## Dependency Checks

The script uses package macros to require or check:

- UUID headers and uuid compare
- pthread headers and mutex initialization
- ncurses headers and working ncurses
- XFS headers and file-handle support
- attribute headers/macros and libattr attrget
- `fallocate`
- manual page format

## Output

It generates `include/builddefs`.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/configure.ac -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/debian/Makefile -->
# File Research: sources/local-fs/xfsdump/debian/Makefile

## Role

This makefile supports Debian packaging installation of package metadata.

## Behavior

It includes top-level build definitions, lists Debian package source files, and defines cleanup patterns.

The `install` target creates the package documentation directory and installs `debian/changelog` as `changelog.Debian` when `PKG_DISTRIBUTION` is `debian`.

`default` and `install-dev` are empty/simple targets.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/debian/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/debian/rules -->
# File Research: sources/local-fs/xfsdump/debian/rules

## Role

This is the Debian package build rules makefile.

## Build Flow

- `build` depends on `built`.
- `built` depends on `config`, runs `make default`, and stamps `built`.
- `config` depends on `.census`.
- `.census` updates autotools config files, builds `include/config.h` with Debian-specific build options, and stamps `.census`.

## Clean Flow

`clean` removes build stamps, runs `make distclean`, removes the package staging directory and debhelper artifacts, restores autotools config files, and runs `dh_clean`.

## Binary Package Flow

`binary-arch` requires root and a completed build, removes/recreates staging, installs into `debian/xfsdump`, runs distribution packaging, and invokes standard debhelper steps such as docs, changelog, strip, compress, fix permissions, shlibs, shlibdeps, control generation, md5sums, and package build.

`binary-indep` is empty, and `binary` depends on both arch and indep targets.

## Environment

The rules export verbose debhelper output and define build options including `DEBUG=-DNDEBUG`, `DISTRIBUTION=debian`, and root install ownership.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/debian/rules -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsdump/dump/Makefile -->
# File Research: sources/local-fs/xfsdump/dump/Makefile

## Role

This makefile builds and installs the `xfsdump` executable from dump-local sources plus common and inventory sources.

## Source Organization

It links shared common headers/sources from `../common` and inventory headers/sources from `../inventory` into the dump build directory.

Source groups:

- `COMMINCL`: common headers used by dump.
- `INVINCL`: inventory headers.
- `INVCOMMON`: inventory implementation files.
- `COMMON`: common implementation files.
- `LOCALS`: dump-specific files such as `content.c`, `inomap.c`, and `var.c`.
- `LOCALINCL`: dump-specific headers.

## Build Settings

- Command target: `xfsdump`
- Local C files: dump-specific files
- Linked common C files: common and inventory implementation files
- Link libraries: UUID, handle, attr, remote tape, pthread
- `LCFLAGS = -DDUMP`

## Targets

`default` builds dependencies and the command.

`install` installs the command into the root sbin directory and also creates a symlink or second install in normal sbin when root sbin and sbin are distinct.

`install-dev` is empty.

The makefile also defines symlink rules for common and inventory files and includes generated dependencies from `.dep`.
<!-- END FILE RESEARCH: sources/local-fs/xfsdump/dump/Makefile -->