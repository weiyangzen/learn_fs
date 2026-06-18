# subset-b-007690 MooseFS mfsmaster research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/posixacl.c -->
# sources/distributed-fs/moosefs/mfsmaster/posixacl.c

## Purpose
`posixacl.c` is the MooseFS master-side in-memory POSIX ACL table. It stores access and default ACL records by `(inode, acltype)`, computes effective access modes for clients, copies inherited default ACLs during file creation, serializes ACL metadata, and reloads ACLs during metadata import.

## Important APIs, Types, And Functions
The file defines private `acl_entry` records with `id` and `perm`, and `acl_node` records with inode, ACL type, base user/group/other permissions, mask, named-user count, named-group count, dynamic ACL entry table, and hash-chain link. Hashing is generated through `hash_begin.h`/`hash_end.h` with `LOHASH_BITS 20` and the `posix_acl_xxx` prefix.

Important exported functions are `posix_acl_getmode()`, `posix_acl_setmode()`, `posix_acl_accmode()`, `posix_acl_copydefaults()`, `posix_acl_set()`, `posix_acl_remove()`, `posix_acl_get_blobsize()`, `posix_acl_get_data()`, `posix_acl_getall()`, `posix_acl_check()`, `posix_acl_copy()`, `posix_acl_store()`, `posix_acl_load()`, `posix_acl_cleanup()`, and `posix_acl_init()`.

`posix_acl_create()` is the internal allocator. It initializes an empty node and inserts it into the generated hash table.

## Control Flow
ACL lookups use the generated hash table. `posix_acl_getmode()` derives the mode bits from access ACL user permission, mask, and other permission. `posix_acl_setmode()` updates those low permission bits when chmod changes a file mode.

Permission evaluation flows through `posix_acl_accmode()`. UID 0 receives full access. The owner uses `userperm`. Named users are masked by `mask`. Group membership checks both the owning GID and named groups and ORs matching access modes. If no group entry matches, the function falls back to `otherperm`.

Inheritance is handled by `posix_acl_copydefaults()`. If the parent default ACL is simple, it only adjusts the new inode mode. Otherwise it creates or updates the child access ACL, clamps permissions by the parent default ACL, copies named entries, and, for directories, also copies the parent's default ACL onto the child.

Mutation flows through `posix_acl_set()` and `posix_acl_remove()`. A simple access ACL with no named entries and `mask == 0xFFFF` is represented by no explicit ACL node, and the filesystem ACL flag is cleared. Non-simple ACLs are inserted or resized and set `fs_set_aclflag()`.

## State, Persistence, And Dependencies
The module owns all ACL nodes in memory. Each node owns an optional `acltab` array sized to `namedusers + namedgroups`. `posix_acl_cleanup()` frees every table and node and destroys the generated hash state.

Persistent storage is a stream of fixed headers plus optional 6-byte named entries. Each record stores inode, ACL type, four permission fields, and two counts, followed by `(id, perm)` pairs. An all-zero header terminates the stream. `posix_acl_load()` skips ACLs for missing inodes, validates ACL type, optionally ignores duplicate/bad records, sets filesystem ACL flags, and contains a compatibility repair for metadata version `0x10` entries with zero masks.

Dependencies include `MFSCommunication.h` for `POSIX_ACL_ACCESS`, `POSIX_ACL_DEFAULT`, and mode mapping, `datapack.h` for binary packing, `filesystem.h` for inode/mode/ACL-flag integration, `bio.h` via the header for metadata I/O, and MooseFS logging/assertion helpers.

## Integration Points
`filesystem.c` uses these APIs for FACL get/set, chmod mode synchronization, ACL inheritance when creating inodes, ACL copy on snapshot/link-like operations, and metadata load/store. The restore path parses `SETACL` changelog records into `fs_mr_setacl()`, which then reaches this module through filesystem code.

## Risks
`posix_acl_getmode()` assumes an access ACL node exists; callers must only call it when the inode ACL flag is present or after a lookup has been validated.

The header declares `posix_acl_set()` as returning `int`, but this C file implements it as `void`. Existing callers ignore the return value, but the mismatch is a compile-time/interface risk.

`posix_acl_copy()` assumes the source ACL exists and dereferences `sacn` without a null check. Callers must prove the source ACL flag/record exists.

ACL entry order is not canonicalized by `posix_acl_set()`. `posix_acl_check()` compares named users within the user range and named groups within the group range, but duplicates could make equality checks ambiguous.

## Test Signals
Useful tests include mode extraction and chmod synchronization, root/owner/named-user/group/other access resolution, named group OR behavior, default ACL inheritance for files and directories, simple ACL elision, duplicate and invalid metadata load handling with and without ignore mode, version `0x10` zero-mask repair, ACL copy/remove cleanup, and round-trip store/load with multiple named users and groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/posixacl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/posixacl.h -->
# sources/distributed-fs/moosefs/mfsmaster/posixacl.h

## Purpose
`posixacl.h` declares the master ACL API used by filesystem metadata code, restore/load code, and permission checks. It intentionally hides the ACL table layout behind opaque `void *` handles for get-data workflows.

## Important APIs, Types, And Functions
The header includes `<inttypes.h>` and `bio.h`. It exports mode synchronization (`posix_acl_getmode`, `posix_acl_setmode`), permission checks (`posix_acl_accmode`), lifecycle operations (`posix_acl_set`, `posix_acl_remove`, `posix_acl_copy`, `posix_acl_copydefaults`), serialization helpers (`posix_acl_get_blobsize`, `posix_acl_get_data`, `posix_acl_getall`, `posix_acl_store`, `posix_acl_load`), comparison (`posix_acl_check`), and lifecycle (`posix_acl_cleanup`, `posix_acl_init`).

## Control Flow
Callers usually set or remove ACLs through filesystem-level operations rather than manipulating nodes directly. Query paths ask for blob size and opaque node pointer first, then call `posix_acl_get_data()` to fill permissions and the packed named-entry blob. Metadata load/store paths pass a `bio` stream to the module.

## State, Persistence, And Dependencies
The header exposes no concrete state. Persistence is delegated to the implementation through `bio *` streams. ACL type and permission constants are expected from `MFSCommunication.h` in callers and implementation.

## Integration Points
`filesystem.c` is the main caller for ACL flags, permission checks, FACL packets, and metadata mutations. `restore.c` indirectly feeds ACL mutations by parsing `SETACL`. Metadata loaders/storers call `posix_acl_load()` and `posix_acl_store()`.

## Risks
The declaration of `posix_acl_set()` returns `int`, but the implementation returns `void`. That is the main header-level risk.

The opaque pointer returned by `posix_acl_get_blobsize()` is only valid while the ACL node remains present and unmodified. Callers should not cache it across mutations.

## Test Signals
Compile warnings or errors around `posix_acl_set()` are important. API tests should also confirm callers tolerate missing ACLs (`posix_acl_get_blobsize()` returns `-1`) and use `posix_acl_get_data()` only after a successful size query.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/posixacl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/posixlocks.c -->
# sources/distributed-fs/moosefs/mfsmaster/posixlocks.c

## Purpose
`posixlocks.c` implements MooseFS master-side POSIX byte-range locks. It normalizes closed-open lock ranges, stores active locks by inode/session/owner, queues blocking lock requests, wakes clients when conflicts clear, writes lock changes to the changelog, and persists active locks in metadata.

## Important APIs, Types, And Functions
The common internal `range` type stores `[start,end)` and lock type. In normal master builds, `alock` stores active lock owner/session/pid and a normalized range list; `wlock` stores a waiting request plus connection/message identifiers; `inodelocks` groups active and waiting locks for one inode. `inodehash` is a 1024-bucket table keyed by inode.

Core range helpers are `posix_lock_test_wlock()` and `posix_lock_apply_range()`. Master helpers include `posix_lock_inode_find/new/remove()`, waiting-list removal/interruption, conflict detection, active lock application, and `posix_lock_check_waiting()`.

Exported APIs are `posix_lock_cmd()`, `posix_lock_file_closed()`, `posix_lock_disconnected()`, `posix_lock_list()`, `posix_lock_mr_change()`, `posix_lock_store()`, `posix_lock_load()`, `posix_lock_cleanup()`, and `posix_lock_init()`.

## Control Flow
`posix_lock_cmd()` is the client command entry point. `GET` returns the first conflicting active lock or reports unlocked. `TRY` returns `MFS_ERROR_EAGAIN` on conflict. Blocking `SET` appends a `wlock` and returns `MFS_ERROR_WAITING`. `INT` interrupts a waiting request by connection and request id. Non-unlock SET/TRY commands first verify the session has the inode open through `of_checknode()`.

When a lock is applied, `posix_lock_apply_lock()` writes a `POSIXLOCK` changelog record and calls `posix_lock_do_apply_lock()`. Range application merges adjacent same-type ranges, splits ranges around changed intervals, and removes empty active lock owners. Unlocking a range can wake queued requests through `posix_lock_check_waiting()`.

`posix_lock_file_closed()` removes all waiting requests and active ranges for the closing session on one inode, then wakes newly unblocked waiters. `posix_lock_disconnected()` removes waiting locks tied to a lost client connection but does not remove active locks; active lock lifetime follows open-file/session cleanup.

Metadata replay uses `posix_lock_mr_change()`, which applies a recorded read/write/unlock without writing another changelog and increments metadata version.

## State, Persistence, And Dependencies
Active and waiting locks live only in memory during runtime. Only active locks are stored by `posix_lock_store()` as 37-byte records: inode, owner, sessionid, pid, start, end, type, terminated by an all-zero record.

`posix_lock_load()` only accepts metadata version `0x10`. It validates that the owning session still has the inode open, expects records grouped by inode/session/owner with ordered non-overlapping ranges, optionally ignores bad records, and reconstructs active lock lists. Waiting locks are not persisted.

Dependencies include `MFSCommunication.h` for lock command/type/status constants, `openfiles.h` for open-file validation, `matoclserv.h` for waking blocked FUSE requests, `changelog.h`, `metadata.h`, `main.h`, `cfg.h`, `datapack.h`, `bio.h`, and logging/assertion helpers. Under `MFSTEST`, only the range engine and a standalone randomized/manual test harness are compiled.

## Integration Points
Client lock requests enter through `matoclserv` and call `posix_lock_cmd()`. Open-file/session cleanup calls `posix_lock_file_closed()` and `posix_lock_disconnected()`. `restore.c` parses `POSIXLOCK` changelog lines into `posix_lock_mr_change()`. Metadata store/load includes active POSIX locks.

## Risks
The range algorithm is compact and branch-heavy. Boundary mistakes around adjacent versus overlapping closed-open intervals would cause silent lock leaks or over-unlocks.

Waiting locks hold raw `connptr` values. Disconnection cleanup must be called reliably, or stale waiters could remain and receive wakeups through invalid connections.

`posix_lock_load()` depends on stored range ordering. If the store order or future format changes, replay can reject otherwise valid locks.

The debug/info path is gated by config and traverses all locks. Large lock tables can produce substantial info output.

## Test Signals
Range tests should cover all `posix_lock_apply_range()` cases, adjacent merge behavior, full unlock to empty list, read/read compatibility, read/write and write/write conflicts, blocking wake-up order, interrupting a waiter, close cleanup, disconnect cleanup, metadata store/load round trips, replay mismatch handling, and `MFSTEST` randomized range runs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/posixlocks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/posixlocks.h -->
# sources/distributed-fs/moosefs/mfsmaster/posixlocks.h

## Purpose
`posixlocks.h` declares the POSIX byte-range lock service used by MooseFS master connection, open-file, metadata, and restore code.

## Important APIs, Types, And Functions
The header includes `<inttypes.h>` and `bio.h`. It exports the client command API `posix_lock_cmd()`, cleanup hooks `posix_lock_file_closed()` and `posix_lock_disconnected()`, listing API `posix_lock_list()`, metadata replay API `posix_lock_mr_change()`, persistence APIs `posix_lock_store()` and `posix_lock_load()`, cleanup, and initialization.

## Control Flow
Callers pass lock operation, session, inode, owner, requested type/range, pid, and optionally message/request identifiers into `posix_lock_cmd()`. The command may mutate type/start/end/pid for conflict reporting. Metadata replay bypasses client waiting logic and calls `posix_lock_mr_change()` directly.

## State, Persistence, And Dependencies
The header hides lock state. Store/load functions serialize active locks through `bio` streams; waiting locks are runtime-only and have no public type.

## Integration Points
`matoclserv` uses the command API for FUSE lock requests and wakeups. `openfiles`/session cleanup use the close/disconnect hooks. `restore.c` uses the replay API for changelog records. Metadata load/store uses the `bio` persistence API.

## Risks
The pointer parameters in `posix_lock_cmd()` are in-out fields, so callers must preserve requested values separately if needed. `connptr` is opaque and lifetime-sensitive. The API also exposes no explicit destroy hook for an individual inode; cleanup is event-driven.

## Test Signals
Header-level tests should compile all major callers and verify operation constants match `MFSCommunication.h`. Runtime tests should assert the `posix_lock_cmd()` return statuses and in-out conflict fields for GET, TRY, SET, INT, and unlock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/posixlocks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/restore.c -->
# sources/distributed-fs/moosefs/mfsmaster/restore.c

## Purpose
`restore.c` is the MooseFS master changelog replay interpreter. It parses textual changelog operations, validates separators and encoded fields, dispatches to `*_mr_*` metadata mutation APIs, enforces metadata-version sequencing, and supports both network replication replay and merged changelog-file restore.

## Important APIs, Types, And Functions
The parser is macro-heavy. `EAT` validates exact separators. `GETNAME`, `GETPATH`, `GETDATA`, `GETARRAYU32`, and `GETHEX` decode escaped names, paths, arbitrary binary blobs, integer arrays, and hex label expressions. `GETU8/16/32/64` and `GETX32` parse numeric values with basic range checks.

There is one `do_*` handler for each changelog operation family: filesystem mutations (`do_create`, `do_link`, `do_move`, `do_unlink`, `do_attr`, `do_length`, `do_write`, `do_trunc`, `do_snapshot`, trash operations), chunks (`do_chunkadd`, `do_chunkdel`, `do_setversion`, `do_nextchunkid`), open files (`do_acquire`, `do_release`), locks (`do_flock`, `do_posixlock`), sessions (`do_sesadd`, `do_seschanged`, `do_sesdel`, connect/disconnect), patterns, storage classes, quotas, xattrs, ACLs, and metadata id changes.

The exported functions are `restore_net()` and `restore_file()`. `restore_line()` is the central dispatcher and uses a four-byte hash of the operation prefix before confirming exact strings.

## Control Flow
Each changelog line starts with a timestamp, `|`, an operation name, parenthesized arguments, and often a `:` result section. `restore_line()` parses the timestamp, selects a handler, and returns the handler status. Unknown entries log a warning and return mismatch.

Handlers parse only their operation syntax and delegate actual state changes to other modules. For example, `do_setacl()` validates ACL blob length and calls `fs_mr_setacl()`, `do_posixlock()` calls `posix_lock_mr_change()`, `do_sesadd()` calls `sessions_mr_sesadd()`, and `do_scset()` builds four `storagemode` values before calling `sclass_mr_set_entry()`.

`restore_net()` is strict for live replication: the incoming changelog version must equal `meta_version()`, the operation must parse and return `MFS_STATUS_OK`, and the metadata version must increase exactly once.

`restore_file()` is merge-oriented. It tracks static `v`, `lastv`, and `lastshfn` state, ignores older entries, tolerates exact duplicates, reports holes with `-2`, applies new entries, and verifies that each applied line advances metadata version by one. It retains the last filename through the shared-pointer helper.

## State, Persistence, And Dependencies
The file itself persists no metadata. It reconstructs metadata by calling module-specific replay APIs that increment metadata version. Several handlers keep static reusable buffers for variable-length decoded fields, so the parser is not reentrant.

Dependencies include `sharedpointer.h`, `filesystem.h`, `sessions.h`, `openfiles.h`, `flocklocks.h`, `posixlocks.h`, `csdb.h`, `chunks.h`, `storageclass.h`, `patterns.h`, `metadata.h`, `mfsstrerr.h`, and logging/assertion helpers.

## Integration Points
`merger.c` calls `restore_file()` while merging changelog files. Master replication code calls `restore_net()` for live changelog packets. Every `*_mr_*` callee is part of the metadata consistency surface: filesystem, chunk database, chunk placement, sessions, open files, locks, storage classes, patterns, and csdb.

## Risks
The parser uses macros that return from the enclosing function; any added handler must follow the same error convention carefully. `GETU32` and `GETU64` rely on `strtoul/strtoull` and do not check that at least one digit was consumed in every call.

Static buffers and static merge state make the implementation single-threaded. Concurrent restores would corrupt parse buffers and version tracking.

`restore_file()` ignores parse errors (`status < 0`) but stops on positive operation errors. This is intentional for corrupted lines but can hide repeated syntax problems during low-verbosity restores.

Storage-class parsing supports several historic formats, so changes to `sclass_make_changelog()` or `do_scset()` must stay in lockstep.

## Test Signals
Good tests include one changelog line per `do_*` handler, malformed separator and escape handling, missing line/hole detection, duplicate changelog entries, version-not-incremented and incremented-more-than-once detection, strict `restore_net()` desync behavior, ACL blob length mismatch, session syntax variants with and without export checksum/umask/disables, storage-class legacy and current formats, and snapshot GID formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/restore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/restore.h -->
# sources/distributed-fs/moosefs/mfsmaster/restore.h

## Purpose
`restore.h` exposes the changelog replay entry points for live network replay and changelog-file merge replay.

## Important APIs, Types, And Functions
The header includes `<inttypes.h>` and declares `restore_net(uint64_t lv, const char *ptr, uint32_t *rts)` and `restore_file(void *shfilename, uint64_t lv, const char *ptr, uint8_t verblevel)`.

## Control Flow
`restore_net()` is for one strict operation at the current metadata version. `restore_file()` is for ordered or merged changelog streams and accepts a shared-pointer filename object for diagnostics.

## State, Persistence, And Dependencies
The header does not expose state. `restore_file()` requires its filename argument to be compatible with `sharedpointer.c` (`shp_get/inc/dec`) because the implementation retains the most recent filename.

## Integration Points
`merger.c` calls `restore_file()`. Network replication code calls `restore_net()`. Both functions drive metadata replay through the implementation's module-specific dependencies.

## Risks
The `void *shfilename` type hides the shared-pointer requirement. Passing a raw string would compile but fail at runtime when `shp_get()` treats it as a shared-pointer object.

## Test Signals
Compile and integration tests should cover both entry points. `restore_file()` tests should pass real `shp_new()` filename objects and verify reference counts are balanced after filename changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/restore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/sessions.c -->
# sources/distributed-fs/moosefs/mfsmaster/sessions.c

## Purpose
`sessions.c` owns MooseFS master client session records. It creates and changes sessions, tracks connection/disconnection and close state, stores export/root/UID/GID/trash/storage-class limits, exposes session info/statistics packets, expires sustained disconnected sessions, and persists session metadata.

## Important APIs, Types, And Functions
The private `session` struct contains session id, export checksum, client info string, peer IP, close/disconnect/socket counters, mount flags, umask, allowed storage-class groups, trash-retention limits, root and map-all identities, disabled operation mask, root inode, info peer/version, and four operation-stat arrays.

The exported lifecycle APIs are `sessions_new_session()`, `sessions_chg_session()`, `sessions_attach_session()`, `sessions_close_session()`, `sessions_disconnection()`, `sessions_force_remove()`, and `sessions_find_session()`. Metadata replay APIs are `sessions_mr_sesadd()`, `sessions_mr_seschanged()`, `sessions_mr_sesdel()`, `sessions_mr_connected()`, `sessions_mr_disconnected()`, and deprecated `sessions_mr_session()`.

Query/enforcement APIs include session id/export/root/flag/umask/disables getters, `sessions_check_sclass()`, `sessions_check_trashretention()`, `sessions_is_root_remapped()`, and `sessions_ugid_remap()`. Reporting APIs include `sessions_datasize()`, `sessions_datafill()`, `sessions_inc_stats()`, `sessions_add_stats()`, and `sessions_info()`.

## Control Flow
New sessions are allocated by `sessions_create_session()`, assigned `nextsessionid` below `0x80000000`, trimmed of trailing NUL bytes in the info field, inserted into a 256-bucket hash, and changelogged as `SESADD` unless created during metadata restore.

Session changes compare all meaningful fields with `sessions_not_changed()`. Real changes update the record, replace the info string, and changelog `SESCHANGED` unless running as metarestore.

Connection attach increments `nsocks`, updates info peer/version, clears disconnection timestamp, and changelogs `SESCONNECTED` when reconnecting. Disconnection decrements `nsocks`; when it reaches zero, it records `main_time()` and changelogs `SESDISCONNECTED`. Close marks a one-socket session as closed so expiration can remove it.

Periodic `sessions_check()` waits until master uptime exceeds two minutes, then removes sessions with no sockets that are closed or disconnected longer than `SESSION_SUSTAIN_TIME`. Removal notifies open-file code through `of_session_removed()` and changelogs `SESDEL`.

## State, Persistence, And Dependencies
Runtime state is `sessionshashtab[256]`, `nextsessionid`, and `SessionSustainTime`. Session statistics are explicitly not stored in current metadata.

`sessions_store()` writes `nextsessionid`, zero stats count, then one 61-byte record plus info bytes for each non-closed session, terminated by a zero session id record. `sessions_load()` reads multiple metadata versions, converting older min/max goal fields to `sclassgroups`, absent export checksums/disables/umasks to defaults, and old disconnected semantics to current timestamps.

`sessions_import_data()` imports legacy `sessions.mfs` files with several signatures and older record layouts. `sessions_reload()` clamps `SESSION_SUSTAIN_TIME` to one minute through one week.

Dependencies include `filesystem.h` for path reporting, `openfiles.h` for cleanup and opened-file counts, `storageclass.h` for export-group checks, `changelog.h`, `metadata.h`, `datapack.h`, `cfg.h`, `main.h`, socket IP formatting, and logging/assertions.

## Integration Points
Client mount/login paths create, attach, change, and disconnect sessions. Filesystem permission code calls UID/GID remapping, root/session flags, storage-class permission, trash-retention permission, and disables checks. Open-file cleanup is notified when sessions are removed. `restore.c` maps `SES*` changelog entries into the metadata replay functions. Master info and admin packet code use `sessions_datasize()`/`sessions_datafill()`.

## Risks
The header declares several open-file-related functions that are not implemented in this file, suggesting stale API drift.

`sessions_not_changed()` calls `memcmp(sesdata->info, info, ileng)` after checking nullness. With `ileng == 0` and both pointers NULL this is usually harmless in C libraries, but it is still a sensitive pattern for sanitizers.

`sessions_mr_sesadd()` creates a session before checking that the generated id equals the changelog id. A mismatch returns an error after mutation, relying on restore abort semantics.

Session id wrap skips the high bit range. Tests should include wrap and collision assumptions, although the code does not search for existing ids on wrap.

## Test Signals
Tests should cover session create/change/no-change, attach/disconnect reconnect changelog behavior, close and timed expiration, forced removal active versus inactive, store/load across supported metadata versions, import of legacy `sessions.mfs`, operation-stat shifts, UID/GID remapping, storage-class group permission, trash-retention bounds, and admin packet size/data agreement for all `vmode` variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/sessions.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/sessions.h -->
# sources/distributed-fs/moosefs/mfsmaster/sessions.h

## Purpose
`sessions.h` declares session operation identifiers and the master session-management API.

## Important APIs, Types, And Functions
The header defines `SES_OP_*` constants for 28 operation-stat slots and `SES_OP_STRINGS` in the same order. It declares session lifecycle, lookup, reporting, creation/change, getters, permission helpers, statistics helpers, cleanup/init, metadata replay, store/load, and legacy import functions.

## Control Flow
Connection code receives opaque session pointers from `sessions_new_session()` or `sessions_find_session()` and passes them back into getters, attach/disconnect, stats, permission, and change functions. Restore code uses the `sessions_mr_*` family. Metadata code uses `sessions_store()` and `sessions_load()`.

## State, Persistence, And Dependencies
No state is exposed. `bio.h` is required for store/load. Operation constants must remain synchronized with `SESSION_STATS` and the implementation's `opname` array.

## Integration Points
The header is consumed by client serving code, filesystem permission paths, restore, metadata storage, and open-file cleanup paths.

## Risks
`sessions_open_file()`, `sessions_connect_session_with_inode()`, `sessions_get_statscnt()`, and `sessions_sync_open_files()` are declared here but not implemented in `sessions.c`; at least `sessions_sync_open_files()` is only seen as a commented caller. This stale surface can confuse new integration work.

Any insertion into the `SES_OP_*` list requires updating `SESSION_STATS`, `SES_OP_STRINGS`, packet compatibility expectations, and statistics consumers.

## Test Signals
Build/link tests should confirm only implemented declarations are referenced. Packet tests should verify stats count and operation-name ordering remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/sessions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/sharedpointer.c -->
# sources/distributed-fs/moosefs/mfsmaster/sharedpointer.c

## Purpose
`sharedpointer.c` is a tiny reference-counted wrapper for a raw pointer plus destructor callback. In this subset it is used by changelog restore/merge code to keep filename strings alive across calls.

## Important APIs, Types, And Functions
The private `shp` struct stores `pointer`, `freefn`, and `refcnt`. `shp_new()` allocates a wrapper with refcount 1. `shp_get()` returns the wrapped pointer. `shp_inc()` increments the count. `shp_dec()` decrements and, at zero, calls `freefn(pointer)` and frees the wrapper.

## Control Flow
Users create a wrapper around an already allocated payload and a destructor function. Ownership is shared by explicit increments and decrements. The module does not copy the payload and does not know its type.

## State, Persistence, And Dependencies
State lives entirely in heap-allocated wrapper objects. There is no persistence and no global registry. Dependencies are only standard allocation and integer headers.

## Integration Points
`restore.c` calls `shp_get()`, `shp_inc()`, and `shp_dec()` for the last processed changelog filename. `merger.c` is the likely creator of filename shared pointers passed to `restore_file()`.

## Risks
There are no null checks, no overflow checks on `refcnt`, and no atomic operations. The helper is single-threaded/manual-lifetime infrastructure. Passing a raw pointer instead of a `shp_new()` result will corrupt memory.

`shp_dec()` silently allows decrement calls when `refcnt` is already zero, then frees again if the wrapper is still reachable, so double-decrement after free remains unsafe.

## Test Signals
Tests should cover creation, get, increment/decrement ordering, destructor invocation exactly once, and integration with `restore_file()` filename switching. Threaded tests are not appropriate unless the implementation is changed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/sharedpointer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/sharedpointer.h -->
# sources/distributed-fs/moosefs/mfsmaster/sharedpointer.h

## Purpose
`sharedpointer.h` declares a minimal opaque shared-pointer API used by master restore helpers.

## Important APIs, Types, And Functions
The header exports `shp_new(void *pointer, void (*freefn)(void*))`, `shp_get(void *vs)`, `shp_inc(void *vs)`, and `shp_dec(void *vs)`.

## Control Flow
Callers receive and pass around `void *` handles. The wrapped pointer is retrieved with `shp_get()`, and lifetime is managed manually with `shp_inc()` and `shp_dec()`.

## State, Persistence, And Dependencies
The header exposes no concrete struct and has no include dependencies. State is heap-owned by the C file.

## Integration Points
The restore file API accepts shared-pointer filename handles but types them as `void *`; this header supplies the required operations.

## Risks
The API is not type-safe. The destructor callback is required and must match the payload allocation method. The reference count is not thread-safe.

## Test Signals
Compile tests should include this header from C and C++-like strict contexts if applicable. Runtime tests should check destructor pairing with the payload allocator used by callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/sharedpointer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/storageclass.c -->
# sources/distributed-fs/moosefs/mfsmaster/storageclass.c

## Purpose
`storageclass.c` owns MooseFS master storage-class policy. It maps class ids to names/descriptions and create/keep/archive/trash placement modes, validates label expressions and erasure-coding settings, changelogs policy changes, serves class info/list packets, persists class definitions, and supplies chunk-placement policy to filesystem/chunk code.

## Important APIs, Types, And Functions
The private `storageclass` struct contains name/description, priority, export group, admin-only flag, archive mode/delay/min-size, min trash retention, global labels mode, four `storagemode` values, and file/directory reference counters.

Important public functions include class CRUD (`sclass_create_entry`, `sclass_change_entry`, duplicate/rename/delete variants and `sclass_mr_*` replay variants), class lookup/accessors, reference counters, placement-mode getters, storage-size/goal-equivalent helpers, joining-priority calculation, info/list serializers, store/load, new/default initialization, cleanup, reload, and init.

Compatibility helpers convert old mask-or-group label masks to expression bytecode and back. EC compatibility is tracked by `ec_current_version`, checked through `sclass_check_ec()`, and replayed through `sclass_mr_ec_version()`.

## Control Flow
Create/change validate names, labels, EC compatibility, archive mode, and count limits before updating `sclasstab`. Normal mutations write `SCSET`, `SCDUP`, `SCREN`, `SCDEL`, or `SCECVERSION` changelog records. Metadata-replay mutations validate expected ids and increment metadata version without writing new changelog entries.

Placement lookup chooses a create mode or keep/archive/trash mode depending on file flags. When runtime `MaxECRedundancyLevel` is lower than a stored EC redundancy count, getters return a temporary adjusted `storagemode`.

Info/list serializers are versioned. Older formats convert label expressions back to mask-or-group representation when possible and mask incompatible classes with `*` names. Newer formats include ids, descriptions, priorities, export groups, archive options, per-mode label modes, EC byte fields, unique masks, label expressions, fulfillment flags, and chunk counters.

`sclass_fix_matching_servers_fields()` periodically refreshes label-expression matching-server counters by calling chunk labelset helpers.

## State, Persistence, And Dependencies
The main state is `sclasstab[MAXSCLASS]`, `firstneverused`, `ec_current_version`, `MaxECRedundancyLevel`, `DefaultECMODE`, and a reusable `tmp_storagemode`.

`sclass_store()` writes expression size, EC version, then one variable-size record per active class with id, name/description, priority/export/admin/label/archive fields, four modes, and label expressions. A zero id terminates the stream.

`sclass_load()` supports pre-expression 3.x formats and newer expression formats from metadata versions `0x17` through `0x1C`. It skips old label descriptions, converts old mask groups, repairs or rejects malformed EC data depending on `ignoreflag`, derives missing defaults, clamps/normalizes older archive modes, and updates `firstneverused`.

`sclass_new()` creates default classes `2CP`, `3CP`, `EC4+1`, and `EC8+1` and enables EC version 2. `sclass_reload()` reads `DEFAULT_EC_DATA_PARTS`, allowing only 4 or 8.

Dependencies include `MFSCommunication.h` for constants and packet limits, `patterns.h` for class deletion side effects, `matocsserv.h`/`matoclserv.h` for EC feature compatibility and label matching, `chunks.h` indirectly through chunk labelset and counters, metadata/changelog/bio/datapack/config/main utilities, and logging/assertions.

## Integration Points
Filesystem code stores a storage-class id on files/directories and calls reference, permission, and policy getters. Chunk replication/placement code consumes `storagemode`, goal-equivalent, EC, label, and priority helpers. Client/admin code consumes `sclass_list_entries()` and `sclass_info()`. Export/session permission uses export groups through `sessions_check_sclass()`. Restore parses `SC*` changelog records into the `sclass_mr_*` functions.

## Risks
This file encodes many versioned wire and metadata formats. Any change to `storagemode`, label expression size, EC byte semantics, or changelog syntax must update store/load, list/info, restore parsing, and compatibility conversions together.

`tmp_storagemode` is a shared static returned by getter functions when EC redundancy is clamped. Callers must not retain it across later calls.

Reference counters are simple increments/decrements with no underflow checks. Incorrect filesystem integration could allow deletion of in-use classes or counter wrap.

`storageclass.h` declares `sclass_is_predefined()`, but this C file does not implement it.

## Test Signals
Tests should cover class create/change/delete/rename/duplicate, in-use delete rejection, changelog/replay id mismatch, EC version gating with simulated client/chunkserver minimum versions, `DEFAULT_EC_DATA_PARTS` reload, old metadata load conversions, malformed EC repair under ignore mode, store/load round trips, list/info packet size agreement for every format version, label-expression conversion compatibility, reference counters, and placement-mode selection for normal/archive/trash flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/storageclass.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/storageclass.h -->
# sources/distributed-fs/moosefs/mfsmaster/storageclass.h

## Purpose
`storageclass.h` defines the public storage-class policy surface for MooseFS master code, including the `storagemode` layout shared with chunk placement and client/admin serializers.

## Important APIs, Types, And Functions
`storagemode` contains unique-server mask, EC data/checksum byte, internal label/matching/counter fields, labels mode, label count, and label expression bytecode array. The header declares compatibility conversion helpers, EC version APIs, info/list serializers, class mutation and replay APIs, lookup/accessors, reference counters, mode getters, storage-size/goal helpers, policy attributes, persistence, cleanup, defaults, and initialization.

## Control Flow
Normal callers create or change classes through the non-`mr` functions so changes are changelogged. Restore calls the `sclass_mr_*` variants. Placement code obtains `storagemode *` pointers from the getter functions and should treat them as borrowed, possibly pointing to a shared temporary.

## State, Persistence, And Dependencies
The header includes `MFSCommunication.h` for class and label constants and `bio.h` for persistence. Internal state is held by `storageclass.c`.

## Integration Points
Filesystem, chunk placement, sessions/export checks, admin packet generation, restore, metadata load/store, and patterns all depend on this API.

## Risks
`storagemode` exposes internal fields such as matching-server and EC counters. External code can accidentally rely on or corrupt fields that are meant to be maintained by chunk labelset refresh code.

The declaration `sclass_is_predefined()` has no implementation in `storageclass.c`, indicating stale API drift unless another translation unit supplies it.

Changing `SCLASS_EXPR_MAX_SIZE`, `MAXLABELSCNT`, or struct layout affects metadata parsing, packet sizes, and compatibility code.

## Test Signals
Build/link checks should catch stale declarations. ABI-like tests should verify packet sizes and metadata round-trip behavior whenever `storagemode` or label constants change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/storageclass.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/topology.c -->
# sources/distributed-fs/moosefs/mfsmaster/topology.c

## Purpose
`topology.c` loads the master network topology configuration and maps IP address intervals to rack/path ids. It provides rack id lookup and a distance metric used by chunk placement/read selection to prefer closer or more failure-independent chunkservers.

## Important APIs, Types, And Functions
The module stores IP intervals in an `itree` and maps rack names to numeric ids through a local hash table plus id array. `rackhashentry` stores rack name, id, hash, and chain link.

Key internal functions include `topology_parsenet()`, rack-name hash/id helpers, stash/restore/cleanup helpers for safe reload, `topology_parseline()`, `topology_load()`, `topology_reload()`, and `topology_term()`.

Exported APIs are `topology_get_rackid()`, `topology_distance()`, and `topology_init()`.

## Control Flow
`topology_reload()` chooses `TOPOLOGY_FILENAME` or the default `ETC_PATH "/mfs/mfstopology.cfg"`, with a compatibility check for the older `ETC_PATH "/mfstopology.cfg"`. It then calls `topology_load()`.

`topology_load()` opens the file, stashes the current rack-name map, parses non-empty non-comment lines, adds intervals to a new tree, and only swaps the live tree after a successful read. On read error it frees the new tree and restores the previous rack-name map, leaving the current topology active.

`topology_parsenet()` accepts `*`, single IPv4 addresses, CIDR bit counts, dotted masks, and address ranges. `topology_parseline()` expects `network rack_path`, where the rack path is a non-whitespace token and path hierarchy is represented by `|`.

`topology_distance()` returns 0 for identical IPs, 1 for different IPs with the same rack id, and higher values based on divergent rack-path hierarchy depth for different rack ids.

## State, Persistence, And Dependencies
Runtime state is `racktree`, `TopologyFileName`, `rackhashtab`, `rackidtab`, and stash copies used during reload. The topology file is external configuration, not MooseFS metadata. No changelog or metadata persistence is involved.

Dependencies include `itree.h` for interval lookup/storage, `hashfn.h` for rack-name hashing, `cfg.h` for configuration, `main.h` lifecycle hooks, `mfsalloc.h` for realloc, POSIX file APIs, and logging/assertions.

## Integration Points
`chunks.c` calls `topology_get_rackid()` and `topology_distance()` for chunk placement, rack-awareness, and client/server distance ranking. `init.h` registers `topology_init()` as the net topology module. `main_reload_register()` enables runtime reloads and `main_destruct_register()` cleans up at shutdown.

## Risks
`topology_rackid_to_rackname()` returns `rackidtab[rackid]->rackname` without checking for a null slot when `rackid < rackidnext`. The current allocation path fills ids densely, but corrupted state would crash distance calculation.

Overlapping intervals are delegated to `itree_add_interval()` semantics; the file does not explicitly detect or warn about overlap conflicts.

Rack ids are assigned in file-parse order and are not persisted. They are safe for runtime comparisons but should not be treated as stable external identifiers across reloads.

## Test Signals
Tests should cover every accepted network syntax, malformed IP/mask/range handling, comments and trailing garbage, missing file behavior with and without existing topology, reload read-error rollback, overlap behavior, default path fallback warning, rack hierarchy distance values, and chunk placement behavior using same host/same rack/different rack inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/topology.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/topology.h -->
# sources/distributed-fs/moosefs/mfsmaster/topology.h

## Purpose
`topology.h` declares the master network-topology lookup API and public distance constants.

## Important APIs, Types, And Functions
It defines `TOPOLOGY_DIST_SAME_IP`, `TOPOLOGY_DIST_SAME_RACKID`, and `TOPOLOGY_DIST_MAX`, and declares `topology_get_rackid()`, `topology_distance()`, and `topology_init()`.

## Control Flow
Callers initialize the module through `topology_init()`, then query rack ids and pairwise distances for IP addresses. Reload/destruction are registered internally and are not exposed here.

## State, Persistence, And Dependencies
The header includes only `<inttypes.h>`. All topology state and file parsing live in `topology.c`.

## Integration Points
Chunk placement and read selection consume the lookup functions. Startup code uses `topology_init()`.

## Risks
`TOPOLOGY_DIST_MAX` is defined as 2, but `topology_distance()` can return values greater than 2 for hierarchical rack paths. Callers should not treat it as a hard maximum for all possible return values; it is better read as the base "different rack" distance.

## Test Signals
Caller tests should accept distances above 2 and only rely on 0 for same IP and 1 for same rack id.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/topology.h -->
