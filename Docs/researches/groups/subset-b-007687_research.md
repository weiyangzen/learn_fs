# subset-b-007687 Research

Grouped research for the listed MooseFS master files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/filesystem.h -->
# sources/distributed-fs/moosefs/mfsmaster/filesystem.h

## Purpose
`filesystem.h` is the public contract for the MooseFS master metadata filesystem engine. It exposes the operations that client service code, metadata load/store, changelog replay, chunk management, quota/xattr/ACL subsystems, trash/sustained handling, and diagnostic tooling use to inspect and mutate the in-memory filesystem namespace.

This header is broad by design: it does not implement behavior, but it defines the master-side API surface for regular namespace operations, metadata-replication replay (`fs_mr_*`), metadata serialization, consistency checking, and runtime reporting.

## Important APIs, Types, And Constants
The header depends on `bio.h` for binary metadata I/O and `MFSCommunication.h` for shared protocol constants such as `MFS_NAME_MAX`, `MFS_PATH_MAX`, `ATTR_RECORD_SIZE`, `MAXSCLASS`, and `EATTR_BITS`.

The `fs_mr_*` family is the metadata-replay surface. These functions apply already-authorized, logged mutations such as create, symlink, unlink, move, link, length/truncate/write/rollback, lock unlocks, storage-class changes, trash-retention changes, extended attributes, ACLs, quotas, archiving status, trash operations, and free-inode housekeeping. Many accept a timestamp and exact inode/checksum/counter values, indicating that they are replaying deterministic changelog records rather than making policy decisions.

The live namespace API includes lookup and permission operations (`fs_path_lookup`, `fs_lookup`, `fs_getattr`, `fs_access`, `fs_opencheck`), creation/mutation operations (`fs_mknod`, `fs_mkdir`, `fs_symlink`, `fs_unlink`, `fs_rmdir`, `fs_rename`, `fs_link`, `fs_snapshot`, `fs_append_slice`), and chunk/length operations (`fs_try_setlength`, `fs_end_setlength`, `fs_do_setlength`, `fs_readchunk`, `fs_writechunk`, `fs_writeend`, `fs_filechunk`, `fs_rollback`, `fs_repair`). These functions typically take a `rootinode`, session flags, caller uid/gid/group list information, and output buffers for attributes or resulting chunk IDs.

Metadata feature APIs cover storage classes (`fs_getsclass`, `fs_setsclass`), trash retention (`fs_gettrashretention_prepare`, `fs_gettrashretention_store`, `fs_settrashretention`), extra attributes (`fs_geteattr`, `fs_seteattr`), xattrs (`fs_listxattr_leng`, `fs_listxattr_data`, `fs_setxattr`, `fs_getxattr`), ACLs (`fs_setfacl`, `fs_getfacl_size`, `fs_getfacl_data`), archive markers (`fs_archget`, `fs_archchg`), quotas (`fs_quotacontrol`, `fs_getquotainfo`), and additional attributes (`fs_set_additional_attributes` and replay counterpart `fs_mr_additionalattr`).

The metadata lifecycle API includes `fs_new`, `fs_afterload`, `fs_check_consistency`, `fs_importnodes`, `fs_loadnodes`, `fs_loadedges`, `fs_loadfree`, `fs_loadquota`, `fs_storenodes`, `fs_storeedges`, `fs_storefree`, `fs_storequota`, `fs_cleanup`, `fs_get_memusage`, and `fs_strinit`. These are the hooks used by the metadata manager for startup, restore, persistence, validation, and shutdown.

## Control Flow
The header separates policy-time operations from replay-time operations. Client-facing paths usually receive root/session context, user identity, group lists, and output buffers, then return MooseFS status codes. Replay paths generally receive exact mutation data and are expected to reproduce prior metadata changes while preserving versioning and consistency.

Several APIs use two-step buffer construction: a `*_size` or `*_prepare` call computes size and stores an opaque cursor pointer, followed by a `*_data` or `*_store` call that serializes records into the caller-provided buffer. This pattern appears for directory reads, xattr listing, trash/sustained directory views, ACL retrieval, parent/path retrieval, and trash retention reporting.

Chunk modification flows are explicitly staged. `fs_try_setlength` prepares a length change and returns indexes/chunk IDs, `fs_end_setlength` completes chunk-side coordination, and `fs_do_setlength` commits metadata and returns the previous length. Similarly, write flow starts with `fs_writechunk`, finishes with `fs_writeend`, and can use `fs_rollback` if chunk allocation/write coordination fails.

## State And Persistence Behavior
This header represents the master filesystem's authoritative in-memory namespace state and its serialized metadata image. Persistence is exposed through `bio`-based load/store functions for nodes, edges, free inode state, and quota state. Changelog replay is represented by the `fs_mr_*` entry points, and emergency version synchronization from the chunks module is exposed via `fs_incversion`.

The API also tracks derived state such as statistics, charts data, memory usage, trash/sustained views, quota counters, xattr/ACL flags, and detached metadata for trash and sustained nodes. Functions like `fs_set_xattrflag`, `fs_del_xattrflag`, `fs_set_aclflag`, and `fs_del_aclflag` show that auxiliary subsystems update inode-level feature flags in the core filesystem structures.

## Dependencies And Integration Points
Primary integration points are the master client protocol service (`matoclserv`), metadata manager (`metadata.c`), restore/changelog handling, chunkserver/chunk modules, open-file/session modules, quota and ACL/xattr modules, and master tools that list trash/sustained/quota/path information.

The API is protocol-shaped: many functions serialize into `ATTR_RECORD_SIZE` records or lists defined by `MFSCommunication.h`, and return `uint8_t` status values from the MooseFS error/status code space. It also integrates with `bio` for binary metadata persistence rather than plain file descriptors.

## Risks
The main risk is contract drift. Because this header is a large central API with many output buffers and pointer parameters, mismatched buffer sizes, wrong ownership expectations for returned pointers, or inconsistent replay/live semantics can corrupt metadata or expose protocol bugs.

Authorization and root/session scoping are also sensitive. Many live operations accept both effective and auxiliary identities (`uid`, `gids`, `gid`, `auid`, `agid`) plus session flags, so callers must pass the correct identity model for permission checks, setuid/setgid clearing, and trash/snapshot behavior.

Metadata replay functions are high risk because they bypass normal user-facing decision paths and rely on exact logged inputs. Any caller that invokes `fs_mr_*` outside restore/replication semantics could skip validation or desynchronize counters/checksums.

## Test Signals
Useful tests include metadata save/load round trips, changelog replay equivalence against live operations, permission/ACL/xattr/quota behavior at protocol boundaries, chunk write/truncate rollback scenarios, trash/sustained lifecycle tests, and consistency checks through `fs_check_consistency`. Fuzzing or property tests around path lookup, rename/link/unlink, and staged chunk-length flows would be especially valuable because those paths combine namespace state, permissions, persistence, and external chunk IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/filesystem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/flocklocks.c -->
# sources/distributed-fs/moosefs/mfsmaster/flocklocks.c

## Purpose
`flocklocks.c` implements MooseFS master-side whole-file advisory locks for FUSE `flock` semantics. It tracks active reader/writer locks by inode, queues blocking lock attempts, wakes client requests when locks become available or are interrupted, persists active locks into metadata, and replays lock changes from changelogs.

The implementation models three wake/fairness modes: `MODE_CORRECT`, `MODE_BSD`, and `MODE_LINUX`, controlled by the `FLOCK_MODE` configuration option. It also has optional debug dumping through `EXTRA_DEBUG_INFO`.

## Important APIs, Types, And Functions
The core data structures are `instance`, `lock`, and `inodelocks`. `instance` stores waiting request identifiers (`msgid`, `reqid`) for a blocking lock owner. `lock` stores owner, connection pointer, session id, active/waiting state, reader/writer type, waiting instances, parent inode record, and intrusive-list links. `inodelocks` stores one inode's active lock list and FIFO waiting queue.

`inodehash` is a 1024-bucket hash table keyed by inode through `FLOCK_INODE_HASH`. Each bucket chains `inodelocks` records. Active locks are held as an intrusive list, while waiting locks use `waiting_head` plus a tail pointer-to-pointer for append.

Public entry points are `flock_locks_cmd`, `flock_file_closed`, `flock_disconnected`, `flock_list`, `flock_mr_change`, `flock_store`, `flock_load`, `flock_cleanup`, and `flock_init`.

Important internal helpers include `flock_check` for conflict/fairness detection, `flock_lock_new` for active-or-waiting creation, `flock_lock_check_waiting` for promotion/wakeup after unlocks, `flock_lock_wake_up_one` and `flock_lock_wake_up_all` for client notifications, `flock_lock_append_req` for coalescing waiting request instances by `reqid`, and `flock_lock_remove`/`flock_do_lock_remove` for cleanup with or without changelog emission.

## Control Flow
`flock_locks_cmd` is the main client command path. For all operations except interrupt and release, it first checks `of_checknode(sessionid, inode)` so only opened files can receive locks. Missing inode lock records are created lazily for lock operations and ignored for unlock/interrupt/release.

Interrupt handling scans waiting locks for the same connection/session/owner, wakes only the matching request id with `MFS_ERROR_EINTR`, and removes the waiting lock if it no longer has any instances. Active locks are not interrupted.

For active locks owned by the same session/owner, unlock and release remove the lock, emit a `FLOCK(...,U)` changelog through `flock_lock_remove`, promote waiters if possible, and remove the inode record if empty. Shared/exclusive conversion is handled in place when possible, or by unlocking and requeueing when a blocking conversion may need to wait. Try-lock conversions return `MFS_ERROR_EAGAIN` instead of queueing.

For existing waiting locks by the same connection/session/owner, repeated blocking requests append or replace `instance` records. Changing the requested type cancels existing waiters with `MFS_ERROR_ECANCELED`, switches the waiting lock type, appends the new request, and continues waiting. Unlock while waiting is ignored for OS compatibility except in `MODE_CORRECT`, where it cancels/removes the waiting lock.

New try locks run `flock_check` and return `MFS_ERROR_EAGAIN` on conflict. New blocking locks use `flock_lock_new`; if conflicted, the lock is queued and returns `MFS_ERROR_WAITING`, otherwise it is attached active and logged.

`flock_lock_check_waiting` performs waiter promotion after unlocks. A writer at the queue head is promoted only when no active locks remain. Readers can be promoted when there are no active locks or active locks are readers. Linux mode scans the whole waiting queue and promotes all reader waiters it finds, while BSD/classic mode promotes only the reader prefix at the queue head.

## State And Persistence Behavior
Only active locks are persistent. Active lock creation/removal via the normal path emits changelog records like `FLOCK(inode,sessionid,owner,R/W/U)`. Waiting requests are connection-local transient state and are neither stored nor replayed.

`flock_store` writes metadata chunk version `0x10` records of 17 bytes: inode, owner, session id, and lock type, followed by an all-zero terminator. `flock_load` accepts only version `0x10`, validates that the referenced open-file record exists with `of_checknode`, verifies there is no conflicting existing active lock, then reconstructs active locks. With `ignoreflag`, invalid closed-file or conflicting records are logged and skipped; otherwise load fails.

`flock_mr_change` is the changelog/restore application path. It removes active locks for unlock commands, or attaches active reader/writer locks for lock commands after checking for conflicts. It increments metadata version with `meta_version_inc` when it successfully mutates state, and intentionally uses non-logging helpers so replay does not emit a second changelog.

## Dependencies And Integration Points
The module depends on `MFSCommunication.h` for flock operation and lock-type constants, `matoclserv_fuse_flock_wake_up` for waking blocked FUSE requests, `openfiles.c` through `of_checknode` and `flock_file_closed`, `metadata.c` for `meta_version_inc` and FLCK metadata chunk load/store, `restore.c` for changelog replay through `flock_mr_change`, `changelog.h` and `main_time` for durable log emission, `cfg.h` for runtime options, and `main.h` for reload/info registration.

`matoclserv.c` calls `flock_locks_cmd`, `flock_list`, and `flock_disconnected`. `openfiles.c` calls `flock_file_closed` when an open-file record closes. `metadata.c` stores and loads the `FLCK` chunk after open-file state, as noted by its dependency comment.

## Risks
Intrusive list pointer maintenance is delicate. In `flock_do_lock_inode_attach`, the active-list insertion sets the old head's `prev` to `&(l->next)`, which is correct for this intrusive pattern but easy to break in future edits. Waiting queue tail updates similarly rely on pointer-to-pointer invariants.

Mode comments and values are inconsistent: `MODE_BSD` is `1` and `MODE_LINUX` is `2`, but `flock_reload` comments say `1 - LINUX , 2 - BSD`. That can cause operator confusion even if behavior follows the constants.

`flock_disconnected` removes only waiting locks for a connection. Active locks are tied to open-file/session cleanup, so disconnect paths must reliably close open files or active locks can persist until session cleanup/recovery handles them.

Load/replay depends on open-file state being loaded first. The metadata integration comment says FLCK depends on OPEN; violating this order will either fail load or skip locks under `ignoreflag`.

Fairness differs by configured mode. `MODE_LINUX` can promote later readers around a waiting writer, while `MODE_CORRECT` blocks new readers behind any waiter to avoid writer starvation. Compatibility changes here can alter client-visible blocking behavior.

## Test Signals
High-value tests include shared/shared coexistence, exclusive conflicts, try-lock `EAGAIN`, blocking wakeups, interrupt by request id, release of waiting locks, conversion between shared and exclusive, close-triggered cleanup, disconnect cleanup of waiters, and metadata store/load with valid and invalid open-file dependencies.

Replay tests should compare changelog `FLOCK` records to live command behavior, ensuring active locks are reconstructed without duplicate changelog emission. Configuration tests should exercise all three `FLOCK_MODE` values with a writer queued behind readers and readers queued behind a writer to catch fairness regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/flocklocks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/flocklocks.h -->
# sources/distributed-fs/moosefs/mfsmaster/flocklocks.h

## Purpose
`flocklocks.h` declares the master-side advisory whole-file lock subsystem used by client protocol handling, open-file cleanup, metadata persistence, and changelog restore. It hides the internal inode hash, lock queues, and wakeup logic behind a compact API.

## Important APIs
`flock_locks_cmd` is the primary command entry point. It takes the client connection pointer, session id, message id, request id, inode, lock owner, and protocol operation, then returns a MooseFS status code such as OK, WAITING, EAGAIN, EINTR, ECANCELED, NOTOPENED, or EINVAL depending on lock state.

`flock_file_closed` releases/removes all locks and waiters for a session/inode pair when the open-file layer closes a file. `flock_disconnected` removes waiting locks tied to a disconnected client connection. `flock_list` serializes active locks for all inodes or one inode into the protocol buffer format, returning the required byte count when called with `buff == NULL`.

`flock_mr_change` applies changelog/metadata-restore lock changes without going through the client wait path. `flock_store` and `flock_load` serialize active locks to/from metadata using `bio`. `flock_cleanup` frees all module state, and `flock_init` allocates and registers runtime hooks.

## Control Flow And State
The header exposes no structs, so callers cannot inspect or mutate lock queues directly. Client operations flow through `flock_locks_cmd`; lifecycle notifications flow through close/disconnect hooks; persistence flows through store/load and replay.

Only active locks are part of persisted state. Waiting lock attempts are represented internally by message/request instances and are expected to be resolved by wakeups, interruption, release, disconnect, or process restart loss.

## Dependencies And Integration Points
The header includes `bio.h`, making metadata persistence part of the public contract. It is consumed by `matoclserv.c`, `openfiles.c`, `metadata.c`, and `restore.c` in the master process.

The `void *connptr` API keeps the header independent of the client service connection type but makes pointer identity part of the subsystem contract. The `message_id` and `req_id` parameters are important for asynchronous FUSE wakeup behavior.

## Risks
Because the command API uses raw protocol operation bytes and a raw `void *` connection pointer, misuse is easy to compile. Callers must pass the exact connection object later used for disconnect cleanup and wakeups.

Persistence callers must obey load ordering: open-file/session state needs to exist before `flock_load`, otherwise validation fails or locks are ignored depending on `ignoreflag`.

## Test Signals
Header-level integration tests should verify that client command handling, open-file close handling, metadata store/load, and restore replay all link against this API and agree on status-code semantics. ABI-sensitive tests should cover the `flock_list` size-then-fill protocol because consumers rely on exact serialized byte counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/flocklocks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/init.h -->
# sources/distributed-fs/moosefs/mfsmaster/init.h

## Purpose
`init.h` defines master-process module startup wiring and command-line option macros for `mfsmaster`. It centralizes the ordered initialization tables for normal startup and metadata restore mode.

## Important APIs, Types, And Macros
`MODULE_OPTIONS_GETOPT` declares short options `i`, `a`, and `x`. `MODULE_OPTIONS_SWITCH` maps those flags to metadata-manager behavior: `-i` calls `meta_setignoreflag`, `-a` calls `meta_allowautorestore`, and `-x` calls `meta_incverboselevel`. `MODULE_OPTIONS_SYNOPSIS` and `MODULE_OPTIONS_DESC` provide user-facing usage text.

The local `runfn` typedef describes module init functions returning `int`. `RunTab`, `LateRunTab`, and `RestoreRunTab` are sentinel-terminated arrays of `{fn, name}` pairs. The sentinel uses a null function pointer and `"****"`.

`RunTab` normal startup order is: random generator, background saver, glob cache, multilan map, changelog, missing log, data cache manager, exports, topology, metadata, charts, metalogger service, chunkserver service, and client service. Inline comments note important ordering: missing log and data cache manager must be before filesystem/client initialization.

`LateRunTab` is currently empty except for the sentinel. `RestoreRunTab` initializes the data cache manager and then runs `meta_restore`.

## Control Flow
The main master program is expected to include this header and iterate `RunTab` during normal startup, `LateRunTab` for any late initialization phase, and `RestoreRunTab` when restoring metadata. Command-line parsing is expected to splice the macro switch into a larger option handler.

This style makes module ordering compile-time static. Adding a module requires editing the table and selecting the correct position relative to dependencies.

## State And Persistence Behavior
The header does not own state directly, but its option macros mutate metadata restore/load state before initialization. `-i` enables ignoring some metadata structure errors, `-a` enables automatic changelog restore, and `-x` increases restore/load verbosity.

Persistence integration is indirect but critical: `meta_init` and `meta_restore` are the gates for loading metadata, replaying logs, and building filesystem state. `bgsaver_init`, `changelog_init`, and `missing_log_init` also participate in durable master behavior.

## Dependencies And Integration Points
The header includes each module whose init function appears in the tables: topology, exports, data cache manager, master-to-metalogger service, master-to-chunkserver service, master-to-client service, metadata, random, changelog, charts, missing log, glob engine, background saver, and multilan.

It integrates with the master executable's option parsing and generic run-table executor. The restore table integrates with metadata recovery tools/paths rather than normal network service startup.

## Risks
Initialization order is the main risk. The ordering comments are sparse, and dependency constraints are encoded only by array position. Moving `missing_log_init`, `dcm_init`, or `meta_init` can create startup bugs that compile cleanly.

The `-i` option is intentionally dangerous because it can ignore metadata structural errors. The description text says not to use it unless restoration alternatives are exhausted, so tests and operational docs should treat it as emergency-only.

The usage description contains a typo (`absoluttely`), which is harmless but user-visible.

## Test Signals
Useful tests include normal startup run-table execution order, restore-mode execution order, command-line option parsing for `-i`, `-a`, `-x`, and `-xx`, and failure injection where an init function returns an error. Startup smoke tests should verify that metadata loads after its prerequisites and network services start only after metadata-dependent modules initialize.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/iptosesid.c -->
# sources/distributed-fs/moosefs/mfsmaster/iptosesid.c

## Purpose
`iptosesid.c` implements a tiny transient IP-to-session-id cache used as a compatibility patch for older MooseFS clients. It allows a session id observed on one request from an IP address to be recovered by a near-immediate follow-up request from the same IP.

## Important APIs, Types, And Functions
The internal `iptosesid` struct stores `ip`, `sessionid`, insertion `time`, and a singly linked `next` pointer. The module uses one static list head, `head`.

`iptosesid_add` allocates a new entry, stamps it with `monotonic_seconds`, and pushes it at the list head. `iptosesid_check` returns whether a non-expired entry exists for an IP. `iptosesid_get` returns and removes the first non-expired matching session id, or returns `0` if none exists.

`I2S_TIMEOUT` is fixed at one second. Expiration uses monotonic time, not wall-clock time, so clock jumps do not affect the cache.

## Control Flow
Both `iptosesid_check` and `iptosesid_get` opportunistically garbage-collect expired entries while walking the list. Expired entries are unlinked and freed. `check` leaves a matching entry in the list, while `get` consumes the matching entry by unlinking and freeing it before returning the session id.

There is no initialization or explicit cleanup function. The list starts as `NULL` and is only bounded by the one-second timeout plus opportunistic scans.

## State And Persistence Behavior
All state is process-local, in-memory, and intentionally short-lived. Entries are not persisted to metadata or changelog. Restarting the master clears the cache, and stale entries disappear only when a later check/get traverses them.

Duplicate IP entries are allowed. Because `add` prepends, the newest matching entry is found first. A `get` removes only one matching entry; older duplicates may remain until consumed or expired.

## Dependencies And Integration Points
The module depends on `clocks.h` for `monotonic_seconds` and `massert.h` for `passert`. Reference searches show `matoclserv.c` uses `iptosesid_get`, `iptosesid_check`, and `iptosesid_add` in code comments marked as a patch for clients older than 3.0.

The API uses IPv4-style `uint32_t ip` values and `uint32_t sessionid` values, matching the master client service's peer/session representation.

## Risks
The cache is keyed only by IP address, not by port, connection, or authentication context. Behind NAT or proxies, two clients from the same IP within the one-second window could collide. The short timeout reduces but does not eliminate this ambiguity.

Because cleanup is opportunistic, a burst of `add` calls without later checks/gets can grow the list temporarily. In normal protocol use, follow-up requests should trigger cleanup, but there is no hard cap.

The module is not synchronized. It assumes the master event loop accesses it serially or under external synchronization.

## Test Signals
Tests should cover immediate `add`/`check`/`get`, consuming behavior of `get`, expiration after more than one second of monotonic time, duplicate IP entries returning newest first, and cleanup of expired entries encountered before live entries. Integration tests in `matoclserv` should verify old-client compatibility does not leak session ids across distinct clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/iptosesid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/iptosesid.h -->
# sources/distributed-fs/moosefs/mfsmaster/iptosesid.h

## Purpose
`iptosesid.h` declares the transient IP-to-session-id compatibility cache used by the MooseFS master client service. It gives callers a minimal add/check/get API without exposing list storage or timeout behavior.

## Important APIs
`iptosesid_add(uint32_t ip, uint32_t sessionid)` records a short-lived mapping. `iptosesid_check(uint32_t ip)` reports whether a currently valid mapping exists. `iptosesid_get(uint32_t ip)` returns and consumes a valid session id for that IP, or returns `0` when no valid mapping exists.

The header includes only `<inttypes.h>`, so the public contract is pure fixed-width integer values.

## Control Flow And State
The implementation keeps all state internally. Callers use `check` when they need to know whether an old-client patch path is available, and `get` when they want to consume the mapping.

There is no init, reload, store/load, or cleanup API. The cache is expected to be process-local and self-cleaning on access.

## Dependencies And Integration Points
`matoclserv.c` is the known consumer, using the functions for pre-3.0 client compatibility during session handling. The API assumes the caller already has the peer IP in the same 32-bit representation used by the master network layer.

## Risks
Since `0` is the miss value for `iptosesid_get`, session id `0` cannot be distinguished from a miss at this interface. That is acceptable only if real session ids are never zero.

The absence of a cleanup API is fine for event-loop usage but can complicate deterministic unit testing unless tests expose or reset module state by process isolation.

## Test Signals
Tests should compile consumers against the header, verify that `get` consumes entries while `check` does not, and assert that the old-client compatibility path handles a zero return as a miss.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/iptosesid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/itree.c -->
# sources/distributed-fs/moosefs/mfsmaster/itree.c

## Purpose
`itree.c` implements a compact interval tree for mapping unsigned 32-bit ranges to nonzero ids. In the MooseFS master it is used by `topology.c` to map IP address ranges to rack/location ids.

The implementation is a binary-search tree over non-overlapping intervals. Adding an interval with an id overwrites any overlapping existing intervals; adding with id `0` deletes the interval. Lookup returns the id associated with a point or `0` when no interval covers it.

## Important APIs, Types, And Functions
The internal `itnode` stores inclusive `from` and `to` bounds, an `id`, and left/right child pointers. Public API uses `void *` root handles so consumers do not see `itnode`.

`itree_add_interval` normalizes reversed endpoints, then either calls `itree_add` for nonzero ids or `itree_delete` for id `0`. It returns the possibly changed root pointer.

`itree_find` walks the tree comparing the point to interval bounds and returns the matched id or `0`. `itree_freeall` recursively frees the whole tree. `itree_rebalance` converts the tree to a sorted linked list, merges adjacent intervals with the same id, and rebuilds a more balanced tree.

Internal `itree_add` handles overwriting overlaps by splitting existing intervals around the new range or deleting covered child ranges. `itree_delete` removes an interval by shrinking, splitting, or removing nodes. `itree_remove` removes a single node and chooses either predecessor or successor based on local branch-chain lengths, using endpoint parity as a tie breaker. `itree_tolist`, `itree_simplify`, and `itree_totree` implement the simple rebalance pass.

## Control Flow
The tree invariant is that left intervals are strictly below the current interval and right intervals are strictly above it. `itree_add` and `itree_delete` preserve non-overlap by recursively deleting or moving covered ranges before replacing the current node's bounds/id.

When a new interval lies inside an existing node, the existing node can split into up to three regions: preserved left remainder, new middle interval, and preserved right remainder. The code chooses which side to allocate first depending on overlap shape and parity to keep behavior deterministic.

Rebalance is intentionally simple and documented as square-time. It flattens the tree in sorted order by reusing the `left` pointer as a next-list pointer, merges adjacent same-id intervals, and recursively selects midpoint-ish list elements to rebuild.

## State And Persistence Behavior
The module owns only heap-allocated tree nodes under a caller-held root pointer. It has no global state, no persistence, and no serialization. Callers are responsible for keeping the root returned by `itree_add_interval` and `itree_rebalance`, and for calling `itree_freeall`.

The special id `0` means absence/delete and is also the lookup miss value. Valid mappings must therefore use nonzero ids.

## Dependencies And Integration Points
The module includes `massert.h` for `passert` allocation checks and its own `itree.h`. Reference searches show `topology.c` uses `itree_add_interval` while loading topology ranges, `itree_find` to compare or classify IP addresses, `itree_rebalance` after reload, and `itree_freeall` during cleanup or reload failure.

The 32-bit bounds align naturally with IPv4 addresses. There is no IPv6 support in this data structure as written.

## Risks
Worst-case unbalanced trees can degrade add/delete/find performance, and the rebalance routine is documented as square-time. Very large topology files or adversarial insertion orders could be expensive.

The code uses recursive add/delete/free/rebuild operations. Deeply skewed trees can risk stack growth before rebalance runs.

The `void *` API hides type details but also removes compile-time type safety. Callers must not mix this root pointer with unrelated data.

Endpoint arithmetic around `n->from - 1`, `n->to + 1`, `t + 1`, and `f - 1` relies on branch conditions preventing underflow/overflow in normal cases. Boundary ranges at `0` or `UINT32_MAX` deserve tests because they are natural IP range endpoints.

## Test Signals
Useful unit tests include adding non-overlapping intervals, overwriting partial overlaps, overwriting complete coverage, deleting middle segments, deleting ranges that span multiple nodes, reversed endpoint normalization, lookup misses returning zero, adjacent same-id merge after rebalance, and boundary ranges at `0.0.0.0` and `255.255.255.255`.

Topology integration tests should load a representative topology map, rebalance it, and verify rack lookup and same-rack comparisons for IPs at range starts, middles, ends, and outside all ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/itree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/itree.h -->
# sources/distributed-fs/moosefs/mfsmaster/itree.h

## Purpose
`itree.h` declares an opaque interval-tree API for mapping inclusive `uint32_t` ranges to nonzero ids. The MooseFS master uses it for topology IP-range classification.

## Important APIs
`itree_add_interval(void *o, uint32_t f, uint32_t t, uint32_t id)` returns a new root after adding or replacing a range. If `id` is `0`, the range is deleted. Reversed endpoints are accepted by the implementation.

`itree_find(void *o, uint32_t v)` returns the id for the interval containing `v`, or `0` if no interval matches. `itree_rebalance(void *o)` returns a rebalanced root and may also merge adjacent same-id intervals. `itree_freeall(void *o)` frees the whole tree.

## Control Flow And State
The root pointer is opaque and caller-owned. Every mutating call can change the root pointer, so callers must assign the return value. The API is deliberately small: no iterator, serialization, or count interface is exposed.

The id value `0` is reserved for deletion/miss semantics. Consumers must use positive/nonzero ids for meaningful mappings.

## Dependencies And Integration Points
The header includes fixed-width integer definitions and is consumed by `topology.c`. Its `void *` API avoids exposing the implementation type across files, but it also means the compiler cannot validate root pointer provenance.

## Risks
Misusing the returned root pointer is the main integration risk. A caller that ignores the return value from add or rebalance can leak nodes or continue searching stale tree state.

Because no const-qualified find signature is exposed, read-only consumers cannot express immutability through the type system.

## Test Signals
Header-level tests should verify callers update roots after add/rebalance, use id `0` only for deletion/miss, and free trees during topology reload or shutdown. Build tests should catch accidental exposure of the internal `itnode` representation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/moosefs/mfsmaster/itree.h -->
