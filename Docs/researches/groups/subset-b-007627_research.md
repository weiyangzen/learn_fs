# subset-b-007627 grouped research

Work item: `subset-b-007627`

Scope: LizardFS master filesystem metadata, node, checksum, dump, freenode, operation, and periodic maintenance code under `sources/distributed-fs/lizardfs/src/master/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem.cc -->
# sources/distributed-fs/lizardfs/src/master/filesystem.cc

## Purpose
`filesystem.cc` owns the lifecycle of the master filesystem metadata subsystem. It defines the global `FilesystemMetadata *gMetadata`, master-only configuration flags, goal definitions, metadata dumper, and checksum background updater, then wires metadata load, lock handling, periodic dumping, event-loop callbacks, master promotion, reload, unload, and termination behavior. The same file also has the `METARESTORE` personality path for opening, dumping, and closing metadata from recovery tools.

## Important APIs and control flow
Public lifecycle functions include `fs_init`, `fs_loadall`, `fs_unload`, `fs_term`, `fs_unlock`, `fs_reload`, `fs_become_master`, `fs_storeall` for metarestore, and `fs_disable_metadata_dump_on_exit`. `fs_init(bool doLoad)` reads config, opens the metadata lockfile, initializes changelog handling, loads metadata for master or requested shadow startup, registers reload/promotion/timer/poll/destructor callbacks, and starts master-specific periodic loops when the process is master. `fs_loadall()` allocates metadata, initializes chunk state, migrates old changelogs, rejects dirty `metadata.mfs.tmp`, loads `metadata.mfs`, and optionally applies changelogs for auto-recovery or shadow mode. `metadataPollServe()` commits or rolls back asynchronous metadata dumps and broadcasts the result to clients.

## State and persistence
Global state includes `gMetadata`, `gStoredPreviousBackMetaCopies`, `gDisableChecksumVerification`, `gChecksumBackgroundUpdater`, and master-only `gGoalDefinitions`, `metadataDumper`, `gAtimeDisabled`, `gMagicAutoFileRepair`, and operation delay timers. Persistence is managed through metadata lockfiles, changelogs, foreground dumps on shutdown, periodic background dumps, and optional metarestore-assisted dumping. A clean shutdown removes the lockfile only after a successful metadata store. A quick stop writes a `quick_stop` lockfile message so later startup knows changelogs are required; a no-metadata stop writes `no_metadata`.

## Dependencies and integration points
This file coordinates `cfg`, `event_loop`, `Lockfile`, `changelog`, `chunks`, `datacachemgr`, `goal_config_loader`, `filesystem_store`, `filesystem_periodic`, `filesystem_snapshot`, `MetadataDumper`, `restore`, client sessions, metaloggers, and metadataserver personality promotion. Goal config loading prefers a configured file, then `/etc` default, then default built-in goals.

## Risks and test signals
The highest-risk behavior is startup and shutdown ordering: dirty temp metadata files, stale lockfile handling, and the distinction between master, shadow, and metarestore personalities decide whether metadata is trusted or changelogs are replayed. Background dump failure can trigger checksum recalculation only when the dumper used metarestore. Useful tests are clean shutdown/removal of lockfiles, quick stop lockfile messages, auto-recovery from changelogs, shadow-to-master promotion with loaded metadata, malformed goal config rejection, disabled checksum verification, and failed background dump result broadcasts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem.h -->
# sources/distributed-fs/lizardfs/src/master/filesystem.h

## Purpose
`filesystem.h` is the broad public interface to the LizardFS master filesystem layer. It declares metadata lifecycle, checksum, load/store, changelog-apply, client-visible filesystem operations, metadata-only trash/reserved operations, quota, ACL, xattr, lock, chunk, tape, and task APIs. It is the contract used by master server modules, shadow/metarestore replay code, and protocol handlers.

## Important APIs and types
The file exposes lifecycle functions such as `fs_getversion`, `fs_checksum`, `fs_start_checksum_recalculation`, `fs_load_changelogs`, `fs_loadall`, `fs_storeall`, `fs_unload`, and `fs_unlock`. Mutating operations include create-like calls (`fs_mknod`, `fs_mkdir`, `fs_symlink`, `fs_link`), namespace calls (`fs_rename`, `fs_unlink`, `fs_rmdir`, `fs_recursive_remove`), file content calls (`fs_writechunk`, `fs_try_setlength`, `fs_do_setlength`, `fs_writeend`), attribute calls (`fs_setattr`, `fs_setgoal`, `fs_settrashtime`, `fs_seteattr`, ACL and xattr calls), and detached-node calls (`fs_settrashpath`, `fs_undel`, `fs_purge`). Read APIs include lookup, getattr, readlink, statfs, readdir, checkfile, goal/trashtime/eattr summaries, quota queries, chunk info, and tape copy locations. The apply namespace mirrors changelog entries for shadow masters and metarestore.

## Control flow and persistence behavior
The header makes the split between direct client/master operations and changelog application explicit. Normal master operations validate context, update in-memory metadata, and append/broadcast changelog entries. Apply functions consume changelog payloads, increment `gMetadata->metaversion`, and verify deterministic replay through mismatch returns. `METARESTORE` excludes server-only APIs and exposes `fs_dump`, `fs_term(fname, noLock)`, `fs_init(fname, ignoreflag, noLock)`, and checksum verification toggling.

## Dependencies and integration points
The interface depends on shared protocol and common types: `FsContext`, `Attributes`, `HString`, ACL/RichACL, goals, quota entries, named inode entries, tape keys, checksum mode, metadata dumper, and async task stats for setgoal/settrashtime. It is the central include point for master request handlers and changelog parsing.

## Risks and test signals
Because this header is a wide ABI within the master, signature drift or personality guards can break many call sites. Tests should exercise both master and shadow replay paths for each changelog-producing operation, verify return codes match protocol expectations, instantiate both legacy and current `fs_readdir` templates, and build both normal and `METARESTORE` targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_checksum.cc -->
# sources/distributed-fs/lizardfs/src/master/filesystem_checksum.cc

## Purpose
`filesystem_checksum.cc` computes and maintains the metadata checksum components for filesystem nodes, xattrs, quota data, and chunk metadata. It supports both incremental updates during metadata mutation and forced full recalculation for verification or recovery.

## Important APIs and functions
The local `fsnodes_checksum(FSNode *node, bool full_update)` hashes stable node fields: type, id, goal, mode, ownership, timestamps, trash time, directory `entries_hash`, device `rdev`, symlink target hash, or file length plus first and last chunk ids. `fsnodes_update_checksum` removes the old node contribution from aggregate checksums, recomputes the node checksum, and re-adds it, also adjusting the background updater aggregate if the node was already scanned. `fsnodes_checksum_add_to_background` does the same for nodes encountered by the background recalculation pass. `fsnodes_recalculate_checksum` rebuilds `gMetadata->fsNodesChecksum` from all node hash buckets and refreshes directory `entries_hash`. `fs_checksum(ChecksumMode mode)` combines max inode, metadata version, next session id, node checksum, xattr checksum, quota checksum, and `chunk_checksum(mode)`.

## Control flow and state behavior
Incremental mutation paths call `fsnodes_update_checksum` after changing nodes. Force recalculation rebuilds node, xattr, and quota checksums before composing the final checksum. The background updater keeps a separate node and xattr checksum while scanning, then replaces global aggregates if a mismatch is found.

## Dependencies and integration points
This code depends on `hashCombine`, `FSNode` variants, `FilesystemMetadata`, `filesystem_xattr`, chunk checksum support, and `ChecksumBackgroundUpdater`. Master builds expose `fs_start_checksum_recalculation`, which starts the background updater and makes the next event-loop poll nonblocking.

## Risks and test signals
The node checksum is intentionally compact and does not hash every chunk id, only first and last chunk ids plus length. Bugs in directory `entries_hash` maintenance or missed `fsnodes_update_checksum` calls can create false checksum mismatches. Tests should compare incremental and forced checksums after create, rename, link/unlink, chmod/chown, ACL/xattr changes, sparse writes, truncation, trash/reserved transitions, quota changes, and concurrent background recalculation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_checksum.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_checksum.h -->
# sources/distributed-fs/lizardfs/src/master/filesystem_checksum.h

## Purpose
`filesystem_checksum.h` declares the filesystem checksum entry points shared by metadata mutation code, periodic background workers, and public filesystem APIs.

## Important APIs
`fsnodes_checksum_add_to_background(FSNode *node)` contributes a node to the background checksum pass. `fsnodes_update_checksum(FSNode *node)` is the normal post-mutation hook for refreshing node checksum state and aggregate checksum values. `fs_checksum(ChecksumMode mode)` returns the current or force-recalculated metadata checksum. `fs_start_checksum_recalculation()` starts the asynchronous checksum recalculation pass in normal master builds.

## Control flow and dependencies
The header includes checksum primitives, metadata, node types, version/personality helpers, and master status macros. It is consumed by node mutation, filesystem operation, periodic maintenance, and lifecycle code. The API intentionally hides the exact node hashing algorithm from callers, so callers only need to remember to invoke update hooks around metadata changes.

## State and persistence behavior
The functions operate on `gMetadata` aggregate checksum fields and, when relevant, `gChecksumBackgroundUpdater`. Checksum values are persisted indirectly through changelog `CHECKSUM` entries and metadata dumps; this header provides the hooks but not changelog emission.

## Risks and test signals
The main risk is missing this hook from a metadata mutation path. Static or review tests should flag direct changes to `FSNode` fields, directory entries, file chunks, or xattr/quota state that lack checksum updates. Build tests should include `METARESTORE` and master personalities because availability of `fs_start_checksum_recalculation` depends on compile mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_checksum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_checksum_background_updater.cc -->
# sources/distributed-fs/lizardfs/src/master/filesystem_checksum_background_updater.cc

## Purpose
`filesystem_checksum_background_updater.cc` implements the state machine used to recalculate metadata checksums incrementally in the event loop without blocking the master for a full scan.

## Important APIs and control flow
`ChecksumBackgroundUpdater::start()` moves the updater from `kNone` to the first recalculation step and rejects duplicate starts. `end()` compares newly calculated node and xattr checksums with global metadata values, replaces globals on mismatch, resets state, and logs completion. `inProgress`, `getStep`, `incStep`, `getPosition`, and `incPosition` expose the cursor used by `fs_background_checksum_recalculation_a_bit`. `isNodeIncluded` and `isXattrIncluded` decide whether a live mutation must also update the background aggregate by comparing the current step and hash-bucket position. `setSpeedLimit` and `getSpeedLimit` control how much work each event-loop slice performs. `reset()` returns to `kNone`, position zero, and checksum seeds.

## State behavior
The updater stores `step_`, `position_`, `speedLimit_`, and separate aggregate `fsNodesChecksum` and `xattrChecksum`. During node or xattr mutation, callers remove/add the old and new contributions from the background aggregate only if the object has already been scanned by this run. This prevents live mutations from being lost while the recalculation cursor is moving through hash buckets.

## Dependencies and integration points
The class integrates with `filesystem_checksum`, `filesystem_periodic`, global `gMetadata`, xattr hash functions, and logging. It is kicked off by `fs_start_checksum_recalculation` and advanced by the periodic each-loop callback.

## Risks and test signals
The cursor logic is subtle: off-by-one bucket inclusion or step transition mistakes can produce self-healing checksum replacements that hide real mutation-order bugs. Tests should start recalculation, mutate nodes before and after the current bucket, mutate xattrs before and after their hash bucket, and verify the final checksum equals a forced recalculation. Also test duplicate `start()` returns false and `end()` resets all state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_checksum_background_updater.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_checksum_background_updater.h -->
# sources/distributed-fs/lizardfs/src/master/filesystem_checksum_background_updater.h

## Purpose
`filesystem_checksum_background_updater.h` declares the background checksum recalculation state machine and its step enum.

## Important APIs and types
`ChecksumRecalculatingStep` enumerates `kNone`, `kNodes`, `kXattrs`, `kChunks`, and `kDone`. The overloaded prefix `operator++` advances the enum and asserts that `kDone` is not incremented. `ChecksumBackgroundUpdater` exposes lifecycle methods (`start`, `end`, `reset`), status accessors (`inProgress`, `getStep`, `getPosition`, `getSpeedLimit`), cursor mutation (`incStep`, `incPosition`), inclusion tests (`isNodeIncluded`, `isXattrIncluded`), and checksum values (`fsNodesChecksum`, `xattrChecksum`).

## Control flow and integration
The header documents that actual scanning is performed outside the class by `fs_background_checksum_recalculation_a_bit()`. The class is a small state holder used by filesystem checksum code, xattr checksum code, periodic chunk checksum logic, and live metadata mutations.

## State and persistence behavior
The class does not persist data directly. Its public checksum fields are transient recalculation aggregates that can replace `gMetadata` checksum fields at the end of a run. The `speedLimit_` value comes from config and controls latency versus convergence time.

## Risks and test signals
Because `operator++` relies on enum ordering, adding a new step requires auditing all switch statements and inclusion checks. Tests should verify step ordering, reset seeds, position reset on `incStep`, and compile coverage for any new enum value in the periodic recalculation switch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_checksum_background_updater.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_checksum_updater.cc -->
# sources/distributed-fs/lizardfs/src/master/filesystem_checksum_updater.cc

## Purpose
`filesystem_checksum_updater.cc` provides storage for `ChecksumUpdater` static state in normal master builds.

## Important APIs and state
The implementation defines `ChecksumUpdater::period_` and initializes `ChecksumUpdater::lastEntry_` to zero when `METARESTORE` is not defined. The class itself is declared inline in the header; this file exists so the static variables have exactly one definition.

## Control flow and persistence behavior
Runtime behavior happens through the header-defined RAII destructor: metadata operations create a `ChecksumUpdater`, mutate metadata, and when the object is destroyed it may emit a `CHECKSUM` changelog entry if the metadata version advanced far enough since `lastEntry_`. This `.cc` file participates by holding the period and last-emitted version.

## Dependencies and integration points
It includes `filesystem_checksum_updater.h` and is compiled only for normal master/shadow builds, not metarestore. `period_` is configured in `filesystem.cc` via `ChecksumUpdater::setPeriod`.

## Risks and test signals
The risk here is linkage/configuration rather than algorithmic behavior. Tests should ensure there is one definition in normal builds, none in metarestore builds, `lastEntry_` starts at zero after process start, and changing `METADATA_CHECKSUM_INTERVAL` updates `period_`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_checksum_updater.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_checksum_updater.h -->
# sources/distributed-fs/lizardfs/src/master/filesystem_checksum_updater.h

## Purpose
`filesystem_checksum_updater.h` defines the RAII helper that periodically emits metadata checksum changelog entries after filesystem mutations.

## Important APIs and control flow
In normal builds, `ChecksumUpdater(uint32_t ts)` captures the operation timestamp. Its destructor checks whether `gMetadata->metaversion > lastEntry_ + period_`; if so, `writeToChangelog(ts_)` records the current metadata version, calculates `fs_checksum(ChecksumMode::kGetCurrent)`, converts the LizardFS version to a string, and writes a `CHECKSUM(version):value` changelog entry. Entries are emitted only when the process is master and no background checksum recalculation is in progress. `setPeriod` configures the version interval. In `METARESTORE`, `ChecksumUpdater` is an empty stub.

## State and persistence behavior
The static `period_` throttles checksum entries and `lastEntry_` stores the metadata version of the last emitted entry. Checksum entries become part of changelog persistence and are later verified by `fs_apply_checksum`, unless checksum verification is disabled.

## Dependencies and integration points
This header pulls in version formatting, checksum APIs, metadata globals, background updater state, filesystem operations for `fs_changelog`, and personality checks. It is used broadly at the start of mutating operations so the destructor runs after the mutation body.

## Risks and test signals
RAII means early returns still run the destructor, which is desired but requires care because failed operations may not have advanced `metaversion`. Tests should verify no checksum changelog is written while recalculation is active, no entry is written before the interval threshold, entries are master-only, and metarestore builds do not reference master-only symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_checksum_updater.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_dump.cc -->
# sources/distributed-fs/lizardfs/src/master/filesystem_dump.cc

## Purpose
`filesystem_dump.cc` implements human-readable metadata dumping for the `METARESTORE` build. It prints nodes, edges, free inode records, and xattrs in a line-oriented diagnostic format.

## Important APIs and control flow
All functions are under `#ifdef METARESTORE`. `fs_dumpnode` prints one node with type, inode, goal, extra mode bits, permissions, uid/gid, timestamps, trash time, and type-specific payload: device major/minor, symlink path, or file length/chunk/session lists. `fs_dumpedge` prints directory, trash, reserved, or null edges. `fs_dumpnodes` walks all node hash buckets. `fs_dumpedgelist` overloads dump normal directory entries, trash entries, and reserved entries. `fs_dumpedges` recursively walks directory edges from root. `fs_dumpfree` iterates `gMetadata->inode_pool`. `xattr_dump` walks xattr hash buckets. `fs_dump` calls these in node, edge, trash/reserved, free-inode, and xattr order.

## State and persistence behavior
The dump is read-only with respect to metadata state. It exposes transient in-memory structures after metadata load or changelog replay, including detached trash/reserved paths and active open session ids stored on file nodes.

## Dependencies and integration points
The file depends on freenode/inode pool iteration, metadata globals, node lookup helpers, name escaping, and xattr hash tables. It is a recovery/debugging surface rather than a master runtime dependency.

## Risks and test signals
The output format is likely consumed by humans or recovery tests, so changing delimiters, escaping, or type letters can break tooling. Tests should run metarestore dumps for each node type, long or escaped names, sparse file chunk lists, reserved/trash entries, free inode records, and xattr entries. Because traversal is recursive for directory edges, corrupt cycles would be dangerous and should be caught earlier by metadata validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_dump.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_freenode.cc -->
# sources/distributed-fs/lizardfs/src/master/filesystem_freenode.cc

## Purpose
`filesystem_freenode.cc` allocates inode numbers from `gMetadata->inode_pool` and preserves compatibility with old changelog free-inode entries.

## Important APIs and control flow
`fsnodes_get_next_id(uint32_t ts, uint32_t req_inode)` first attempts to mark a requested inode as acquired when a nonzero requested id is supplied. If no request is provided or the requested id is unavailable, it acquires the next free id from the pool. A zero result aborts the process with `mabort("Out of free inode numbers")`. Successful allocation updates `gMetadata->maxnodeid` if the id is the largest seen. `fs_apply_freeinodes` ignores old free-inode changelog payloads and increments `metaversion` for compatibility.

## State and persistence behavior
Allocation mutates the inode pool and the max inode counter. Inode release happens elsewhere during node removal. Requested inode handling is important during changelog replay because shadow/metarestore must recreate specific ids.

## Dependencies and integration points
The code depends on `FilesystemMetadata`, `IdPoolDetainer`, checksum updater includes, and filesystem operation status conventions. `fsnodes_create_node` is the main caller.

## Risks and test signals
The fatal behavior on exhausted inode pool is intentional but high impact. Tests should cover requested id success, requested id collision fallback, monotonic `maxnodeid`, release-and-reacquire delay semantics through the pool, replay creation with exact inode ids, and compatibility replay of old `FREEINODES` entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_freenode.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_freenode.h -->
# sources/distributed-fs/lizardfs/src/master/filesystem_freenode.h

## Purpose
`filesystem_freenode.h` declares the inode allocation helper used by node creation and changelog replay.

## Important API
`fsnodes_get_next_id(uint32_t ts, uint32_t req_inode)` returns an allocated inode id. `req_inode == 0` asks for any free id; a nonzero request asks for a specific inode but may fall back to another id if that id is already acquired.

## State and persistence behavior
The function works against `gMetadata->inode_pool` and `gMetadata->maxnodeid`. The timestamp is passed into the inode pool so reuse delay and detainer behavior remain deterministic.

## Dependencies and integration points
The header includes node types and is consumed by `filesystem_node.cc`, `filesystem_dump.cc`, and filesystem load/apply paths.

## Risks and test signals
Callers that require exact replay ids must compare the requested id with the returned id and report mismatch, as `fs_apply_create` does. Tests should assert that behavior and verify the API returns nonzero or aborts on exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_freenode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_metadata.h -->
# sources/distributed-fs/lizardfs/src/master/filesystem_metadata.h

## Purpose
`filesystem_metadata.h` defines `FilesystemMetadata`, the central in-memory state container for LizardFS master filesystem metadata, plus the global metadata and configuration symbols shared across the master.

## Important types and fields
`FilesystemMetadata` holds tape copy records, xattr inode/data hash tables, the inode pool, ACL storage, trash and reserved detached path containers, root directory pointer, node hash table, task manager, flock and POSIX lock databases, max inode id, next session id, node counters, metadata version, trash/reserved space and node counters, file/dir counters, quota database, and aggregate checksums for nodes, xattrs, and quotas. The constructor zero-initializes pointer arrays and counters, initializes `inode_pool` with reuse delay/capacity settings, and seeds quota checksum from the quota database. The destructor frees xattr linked lists and destroys every node in the node hash table with type-aware `FSNode::destroy`.

## State and persistence behavior
This struct is the authoritative mutable metadata loaded from `metadata.mfs` and changelogs and later dumped back to persistent metadata. `metaversion` is the changelog version cursor. Aggregate checksum fields are updated by mutation paths and verified through checksum changelog entries.

## Dependencies and integration points
It integrates storage for ACLs, chunks, xattrs, quota, locks, tasks, free inode detaining, tape copy tracking, background checksum updating, and node types. Globals include `gMetadata`, `gChecksumBackgroundUpdater`, `gDisableChecksumVerification`, and master-only goal definitions, dumper, atime, and auto-repair flags.

## Risks and test signals
Because it owns raw pointer hash tables and C-style linked lists, destructor coverage and ownership boundaries matter. Tests should load and unload metadata under ASAN/Valgrind, exercise xattr and node allocation/deletion, verify no double frees after trash/reserved transitions, and check that newly constructed metadata starts with consistent counters and checksum seeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_metadata.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_node.cc -->
# sources/distributed-fs/lizardfs/src/master/filesystem_node.cc

## Purpose
`filesystem_node.cc` implements the low-level metadata invariants for filesystem nodes. It creates and destroys typed nodes, maintains directory entries, parent vectors, subtree statistics, quotas, chunks, ACLs, checksums, paths, detached trash/reserved state, permission checks, and recursive property changes.

## Important APIs and functions
Creation and ownership functions include `FSNode::create`, `FSNode::destroy`, `fsnodes_create_node`, `fsnodes_link`, `fsnodes_remove_edge`, `fsnodes_unlink`, `fsnodes_remove_node`, `fsnodes_purge`, and `fsnodes_undel`. Statistics and size helpers include `fsnodes_get_stats`, `fsnodes_add_stats`, `fsnodes_add_sub_stats`, file chunk/size/realsize helpers, and `fsnodes_get_size`. Directory and path APIs include `fsnodes_lookup`, `fsnodes_getpath_size`, `fsnodes_getpath_data`, `fsnodes_getdirsize`, legacy and current `fsnodes_getdir`, and detached trash/reserved listing helpers. Attribute and security APIs include `fsnodes_fill_attr`, `fsnodes_access`, `fsnodes_sticky_access`, `verify_session`, `fsnodes_get_node_for_operation`, ACL setters/getters/deleters, `fsnodes_namecheck`, and recursive goal/trashtime/eattr functions.

## Control flow and state behavior
Node creation allocates an inode, inherits goal/trash time/mode/eattrs from parent, optionally inherits RichACL/default ACL, inserts into the global node hash, updates checksums, links into the parent directory, propagates stats, and charges inode/file quota. Link and unlink paths update directory `entries_hash`, parent vectors, stats, nlink, timestamps, and checksums. Last unlink of a file moves it to trash if `trashtime > 0`, reserved if still open, or deletes it; purge moves trash to reserved when sessions remain or frees it fully. Length and append operations update chunk ownership, detached space counters, stats, quotas, and checksums.

## Dependencies and integration points
The file depends on chunk metadata, datacache invalidation, quota helpers, checksum helpers, metadata globals, periodic defective-node cleanup, FsContext/session flags, ACL storage, goals, tape server enqueueing, and personality assertions. Higher-level `filesystem_operations.cc` calls these primitives after validating protocol semantics.

## Risks and test signals
This is a high-risk invariant hub. Missed stat, quota, checksum, or parent-vector updates cause persistent metadata divergence. Tests should cover create/unlink/rename/link across directories, hard links, recursive stats after file size changes, quota deltas after chown and truncate, directory hash changes, ACL inheritance and equivalent-mode collapse, trash/reserved/undel/purge paths, session-scoped reserved deletion, permission checks with rootinode and meta sessions, current versus legacy readdir indexes, and chunk reference counts on append/truncate/delete.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_node.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_node.h -->
# sources/distributed-fs/lizardfs/src/master/filesystem_node.h

## Purpose
`filesystem_node.h` declares the low-level node utility API used by filesystem operations, load/store code, periodic scanners, and metarestore diagnostics.

## Important APIs
Inline helpers include `fsnodes_hash`, `fsnodes_lookup`, `fsnodes_id_to_node`, `fsnodes_id_to_node_verify`, and `fsnodes_update_ctime`. The non-inline API covers escaping names, purging/undeletion, detached trash/reserved serialization, path construction, attribute filling, session verification, operation-context node lookup, name/access checks, length and ownership changes, node creation, stats propagation, link/unlink/remove-edge operations, append/chunk/goal/trashtime/eattr recursion, ACL operations, directory serialization, file check summaries, tape enqueueing, and size/parent helpers.

## Control flow and state behavior
The API separates fast inline lookup/check helpers from mutation helpers that maintain global metadata invariants. `fsnodes_update_ctime` has special trash handling: changing ctime affects `TrashPathKey`, so it removes and reinserts the trash path entry around the timestamp update.

## Dependencies and integration points
The header depends on node types, metadata globals, protocol directory entry types, named inode entries, and FsContext. It is included by operations, dump, checksum, periodic, freenode, and metadata code.

## Risks and test signals
Typed lookup verification uses `assert`, so production builds can still receive null or wrong-type pointers if callers misuse unchecked functions. Tests should use debug builds to catch type invariants, and operation-level tests should validate public status-code behavior for missing/wrong-type inodes. Any new node mutation helper should be checked for checksum, stats, quota, xattr, ACL, chunk, and detached-container side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_node.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_node_types.h -->
# sources/distributed-fs/lizardfs/src/master/filesystem_node_types.h

## Purpose
`filesystem_node_types.h` defines the core in-memory node types, hash constants, session/operation enums, stats records, and detached-container key types used by the filesystem metadata layer.

## Important types and fields
Constants define node and edge hash sizes, checksum seeds, and `MAX_INDEX`. Enums include `AclInheritance`, `SessionType`, `OperationMode`, and `ExpectedNodeType`. `statsrecord` stores recursive counts and sizes. `FSNode` stores common inode metadata, parent ids, hash-chain link, and per-node checksum, with factory/destructor methods. `FSNodeFile` adds file length, open session ids, and chunk ids with `chunkCount()`. `FSNodeSymlink` stores a string handle and path length. `FSNodeDevice` stores `rdev`. `FSNodeDirectory` stores an ordered/flat/Judy entry map, subtree stats, nlink, and `entries_hash`, with name and node lookup helpers. `TrashPathKey` sorts trash by expiration timestamp and inode id, with endian-aware field order.

## State and persistence behavior
These structs are the shape of loaded metadata in memory. Directory entries use `hstorage::Handle` for names and compact vectors for parent/session/chunk storage to reduce memory footprint. Trash and reserved containers map detached files to their original paths and are persisted through metadata/changelogs.

## Dependencies and integration points
The file integrates common access-control, attributes, goals, compact vector, Judy/flat maps, FsContext, and string-handle storage. It is foundational for checksum, operations, dumping, load/store, and quota code.

## Risks and test signals
Memory layout and container choice affect master scalability. `FSNodeDirectory::find` scans the equal-name-hash range, so hash collisions must be handled correctly. Tests should cover name hash collisions, directory ordering/readdir indexes, `chunkCount` with trailing zero chunks, endian behavior for trash key ordering, and correct factory/destructor pairing for every node type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_node_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_operations.cc -->
# sources/distributed-fs/lizardfs/src/master/filesystem_operations.cc

## Purpose
`filesystem_operations.cc` implements the high-level filesystem API declared in `filesystem.h` and `filesystem_operations.h`. It translates protocol-level requests into validated metadata mutations or reads, emits changelog records on the master, applies changelog records on shadow/metarestore, updates operation statistics, and coordinates locks, quotas, chunks, ACLs, xattrs, tape copies, and background tasks.

## Important APIs and control flow
The file starts with `fs_changelog`, which prepends timestamps, increments `metaversion`, writes changelog records, and broadcasts them to metaloggers/shadows. Namespace operations include lookup/path lookup/getattr, create (`fs_mknod`, `fs_mkdir`, `fs_symlink`, `fs_apply_create`), unlink/rmdir/recursive remove/apply unlink, rename, hard link, and append. File content operations include set length/truncate/unlock, readchunk/writechunk/writeend, repair/apply repair, and next chunk id. Metadata operations include setattr/apply attr, ACL and RichACL set/delete/get/apply, xattr list/get/set/apply, goal/trashtime/eattr get/set/apply/deprecated recursive paths, quota-related checks through node helpers, and detached trash/reserved operations. Lock APIs wrap flock and POSIX `FileLocks` for lock, probe, clear session, list, unlock inode, and remove pending. End-of-file APIs expose tape copy updates, chunk info, task cancellation/id reservation, version, and rebuilding chunk file references.

## State and persistence behavior
Master operations usually create `ChecksumUpdater`, validate `FsContext` and permissions, mutate nodes through `fsnodes_*` helpers, then write a changelog entry. Shadow/apply variants mutate deterministically, increment `gMetadata->metaversion`, and return mismatch when replayed ids, chunk ids, counters, ACL data, or task results differ from the master. Operation counters in `gFsStatsArray` are incremented for common request classes and retrieved/reset by `fs_retrieve_stats`.

## Dependencies and integration points
This file is the integration hub for protocol handlers. It depends on event-loop time, changelog broadcasting, chunks, filesystem checksum, node helpers, quota helpers, locks, master-client and metalogger services, recursive remove/setgoal/settrashtime task manager, tape server metadata, and protocol constants.

## Risks and test signals
The highest risks are divergent master versus shadow replay, missed changelog entries, stale checksums after early returns, quota deltas around rename/truncate/append, and permissions around rootinode, meta sessions, sticky directories, ACLs, and open file flags. Tests should replay every changelog verb, check mismatch detection, exercise delayed truncation and write locks, test quota failure boundaries, verify lock queue wakeups after unlock/release, validate xattr/ACL string parsing, cover tape-goal write denial, and run metadata checksum comparison after operation sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_operations.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_operations.h -->
# sources/distributed-fs/lizardfs/src/master/filesystem_operations.h

## Purpose
`filesystem_operations.h` declares lower-level operation support shared by the public filesystem API, lock management code, and statistics/reporting modules.

## Important APIs and types
It defines defaults `DEFAULT_GOAL` and `DEFAULT_TRASHTIME`, the `FsStats` enum for operation counters, and `gFsStatsArray`. Declared functions include `fs_retrieve_stats`, goal definition accessors, metadata saved broadcasting, `fs_changelog`, `fs_add_files_to_chunks`, `fs_getversion`, a legacy repair signature, flock/POSIX lock operations and probes, session lock clearing, lock listing, inode unlock, and pending lock removal.

## Control flow and state behavior
The header separates helper operations from the broad client API in `filesystem.h`. Lock functions operate on `gMetadata->flock_locks` or `posix_locks`, can emit changelog entries, and return owners whose pending locks became active. Statistics retrieval copies then clears the counter array.

## Dependencies and integration points
It depends on goals, FsContext, lock types, setgoal task declarations, and protocol lock info. It is included by checksum updater, node code, periodic code, and operations implementation.

## Risks and test signals
Because some declarations are master-only behavior but not all are guarded by `METARESTORE`, compile matrices matter. Tests should build normal and metarestore targets, verify stats reset semantics, and exercise lock APIs through both active and pending queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_operations.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_periodic.cc -->
# sources/distributed-fs/lizardfs/src/master/filesystem_periodic.cc

## Purpose
`filesystem_periodic.cc` implements event-loop maintenance work for the master filesystem: async task processing, background checksum recalculation, file/chunk health scanning, defective-node reporting, trash expiry, and periodic configuration.

## Important APIs and control flow
`fs_background_task_manager_work` processes queued metadata tasks in batches and makes the next poll nonblocking while work remains. `fs_background_checksum_recalculation_a_bit` advances `gChecksumBackgroundUpdater` through nodes, xattrs, chunks, and done states, calling node/xattr/chunk checksum functions and broadcasting completion. File test logic uses `fs_periodic_file_test` and `fs_background_file_test` to scan node hash buckets over a configured loop time, count files/chunks/under-goal/missing/unavailable states, and maintain `gDefectiveNodes`. `fs_test_getdata` returns the last scan counters and a capped textual error report. `fs_get_defective_nodes_info` pages through defective nodes with requested error flags. Trash maintenance uses `fs_periodic_emptytrash`, `fs_do_emptytrash`, and deprecated apply helpers to purge expired trash entries.

## State and persistence behavior
Static counters store the last completed scan and current scan accumulators. `gFileTestLoopIndex` and `gFileTestLoopBucketLimit` implement incremental scanning with watchdog-limited slices. `gDefectiveNodes` stores inode to error-flag mappings, capped at one million entries. Empty-trash operations mutate metadata, call `fsnodes_purge`, and emit `PURGE` changelog entries in master mode; deprecated apply variants verify historical free/reserved counts.

## Dependencies and integration points
The file depends on config, event loop, loop watchdogs, checksum/xattr/chunk recalculation, node helpers, metadata globals, task manager, client broadcasts, chunk health APIs, and changelog emission. `fs_periodic_master_init` registers timers and each-loop callbacks.

## Risks and test signals
The periodic code must avoid blocking the event loop while still converging. Risks include defective-node map staleness, watchdog bucket adjustment errors, checksum recalculation never reaching done, and trash iteration invalidation after purges. Tests should simulate large node hash scans, unavailable/missing chunks, structure errors in parent vectors, expired trash with and without open sessions, task-manager backlog, checksum background completion broadcast, and config bounds for `FILE_TEST_LOOP_MIN_TIME`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_periodic.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_periodic.h -->
# sources/distributed-fs/lizardfs/src/master/filesystem_periodic.h

## Purpose
`filesystem_periodic.h` declares the public hooks for master periodic filesystem maintenance and reporting.

## Important APIs
`fs_get_defective_nodes_info` returns paginated defective file information filtered by requested flags. `fs_read_periodic_config_file` loads periodic scan configuration. `fs_periodic_master_init` registers maintenance callbacks. `fs_test_getdata` returns scan timing, file/chunk counters, and a report string. `fsnodes_periodic_remove` removes an inode from the defective-node map when a node is deleted.

## Control flow and integration
The header exposes only the reporting/config/init/remove surface; the actual scanning and checksum work stays private in the `.cc` file. It depends on `DefectiveFileInfo` and is included by lifecycle code, node removal, and status/report handlers.

## State and persistence behavior
The declared functions operate on static in-memory periodic scan state. They do not persist data directly, but `fs_periodic_master_init` starts maintenance paths that can mutate metadata through trash purge and async tasks.

## Risks and test signals
Callers depend on stable pagination semantics for defective nodes and stable report counters. Tests should call `fs_get_defective_nodes_info` with different flag masks and entry indexes, confirm `fsnodes_periodic_remove` clears stale entries, and verify init registers all expected event-loop callbacks in master builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_periodic.h -->
