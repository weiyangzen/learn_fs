# subset-b-007628 research

This grouped report covers LizardFS master metadata persistence, quota, snapshot, chunk placement, goal parsing, name storage, ID detention, interval tree, and locking files. Each source file has its own marked section for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_quota.cc -->
# sources/distributed-fs/lizardfs/src/master/filesystem_quota.cc

Purpose: implements quota query, mutation, replay, enforcement, and accounting helpers for the master filesystem. It handles user, group, and inode-directory quotas, including synthetic "used" values for directory quota owners based on live directory statistics.

Important APIs/types/functions: `fs_quota_get_all()` returns quota entries with current stats and filters inode quotas outside the caller's mounted root; `fs_quota_get()` enforces owner-level permissions and expands each requested owner into soft, hard, and used entries; `fs_quota_get_info()` resolves inode owners to paths; `fs_quota_set()` validates permissions, applies limits, updates quota checksum, and emits `SETQUOTA` changelog records; `fs_apply_setquota()` replays changelog quota changes; `fsnodes_quota_exceeded_ug()`, `fsnodes_quota_exceeded_dir()`, and `fsnodes_quota_exceeded()` check hard limits; `fsnodes_quota_update()` increments used counters for user and group ownership; `fsnodes_quota_remove()` deletes an owner quota.

Control flow: client-visible quota operations first check `FsContext` permissions and session flags. Get operations read `gMetadata->quota_database`, synthesize live directory usage for inode owners, then remove entries hidden by a chroot-like session root. Set operations reject read-only sessions and non-root callers without `SESFLAG_ALLCANCHANGEQUOTA`, validate inode owners, update the quota database per entry, recompute `quota_checksum`, and log changelog records. Replay decodes compact changelog chars into enum values and mutates metadata without the live permission path.

State and persistence behavior: quota state lives in `gMetadata->quota_database` and is persisted by the metadata store's `QUOT 1.1` section. Live directory quota "used" values are derived from `FSNodeDirectory::stats`; user/group used counters are maintained by `fsnodes_quota_update()`. `fs_apply_setquota()` increments `metaversion`, while client `fs_quota_set()` relies on `ChecksumUpdater` and changelog output.

Dependencies/integration: depends on `FsContext`, session flags, `QuotaDatabase`, `FSNode` lookup and ancestry helpers, metadata checksums, `eventloop_time()`, and changelog formatting. It is called from filesystem operations that create, delete, move, or resize nodes and from metadata restore.

Risks and test signals: ancestor checks follow the first parent for path construction and common-ancestor move checks, so hard-linked files and multi-parent relationships are subtle. Negative deltas are accepted in resource lists and rely on unsigned arithmetic around live stats and database behavior. `fsnodes_quota_adjust_space()` is a stub, so statfs quota reporting is not implemented here. Tests should cover permission combinations, subtree filtering by `rootinode`, invalid inode quota owners, changelog replay char decoding, directory move common-ancestor cases, and quota checksum stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_quota.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_quota.h -->
# sources/distributed-fs/lizardfs/src/master/filesystem_quota.h

Purpose: declares the quota enforcement and accounting helpers used by the master filesystem outside the quota RPC implementation.

Important APIs/types/functions: exposes user/group checks by ids and by `FSNode *`, directory quota checks by node and by move destination/source directories, combined checks, quota usage updates, quota owner removal, and statfs-space adjustment.

Control flow: callers are expected to check quota with `fsnodes_quota_exceeded*()` before applying a metadata change, then call `fsnodes_quota_update()` after the change to keep user/group used counters in sync. Move callers can use the overload that accepts destination and previous directories to skip quotas already covered by a common ancestor.

State and persistence behavior: the header has no state. The declared functions mutate or read `gMetadata->quota_database`; quota persistence is handled by metadata store code, not by this interface.

Dependencies/integration: includes `filesystem_freenode.h` for `FSNode` and `FSNodeDirectory` and `quota_database.h` for `QuotaResource` and `QuotaOwnerType`. It is integrated by node, chunk, snapshot, and restore paths that need quota decisions.

Risks and test signals: the API takes initializer lists of signed deltas, so caller-side unit consistency matters. Tests should assert that every metadata operation that changes inode count or size uses matching check/update pairs, and that the unimplemented `fsnodes_quota_adjust_space()` behavior is accounted for by higher-level statfs tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_quota.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_snapshot.cc -->
# sources/distributed-fs/lizardfs/src/master/filesystem_snapshot.cc

Purpose: provides the public master entry points for creating filesystem snapshots and cloning individual nodes. It validates operation context and delegates actual copy work to `SnapshotTask`.

Important APIs/types/functions: `fs_read_snapshot_config_file()` reads `SNAPSHOT_INITIAL_BATCH_SIZE` and `SNAPSHOT_INITIAL_BATCH_SIZE_LIMIT`; `fs_snapshot()` validates source and destination, prevents recursive directory snapshots into descendants, builds a `SnapshotTask`, computes human-readable source/destination paths, clamps batch size, and submits the task to `gMetadata->task_manager`; `fs_clone_node()` builds a non-queued `SnapshotTask` and calls `cloneNode()`.

Control flow: snapshot requests enter with `FsContext`, session mode validation, destination directory write validation, and source read validation. After validation, the function asserts master personality, builds a task configured with overwrite and missing-source flags, derives paths for the job description, resolves default/clamped batch size, and submits asynchronously with callback and job id. The clone helper skips submission and invokes immediate clone logic for restore/task internals.

State and persistence behavior: uses `ChecksumUpdater` around `fs_snapshot()`, but most persistent metadata changes occur inside `SnapshotTask` and its changelog/task-manager integration. Batch-size globals are process configuration state.

Dependencies/integration: depends on config, `FsContext`, node operation helpers, quota header, `SnapshotTask`, `TaskManager`, and metadata singleton. It integrates with client snapshot requests and background task processing.

Risks and test signals: destination path construction assumes first-parent paths; batch limit reads from a similarly named config key and can silently clamp caller input. Tests should cover source/destination permission failures, directory ancestor rejection, overwrite/missing flags, default and explicit batch sizes, and callback/job-id submission behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_snapshot.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_snapshot.h -->
# sources/distributed-fs/lizardfs/src/master/filesystem_snapshot.h

Purpose: declares snapshot configuration loading and snapshot/clone entry points for the master filesystem.

Important APIs/types/functions: `fs_read_snapshot_config_file()` loads process-level snapshot batching; `fs_snapshot()` registers a snapshot task from source inode to destination parent/name with overwrite, missing-source, initial batch, callback, and job id parameters; `fs_clone_node()` clones a single node to a destination inode/name.

Control flow: callers use the header to enter the validated asynchronous snapshot path or lower-level clone path. The callback signature receives task status as an integer.

State and persistence behavior: no direct state in the header; implementations use metadata task state and changelogs.

Dependencies/integration: includes `filesystem.h` for node types and `fs_context.h` for authenticated operation context. Used by client request handlers and restore/task code.

Risks and test signals: the API exposes byte-sized booleans rather than strong types for overwrite and ignore-missing flags. Tests should verify flag interpretation and that clone callers pass already-validated contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_snapshot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_store.cc -->
# sources/distributed-fs/lizardfs/src/master/filesystem_store.cc

Purpose: owns master metadata serialization, deserialization, new filesystem initialization, changelog replay after load, foreground/background dump coordination, metadata rotation, and emergency saves.

Important APIs/types/functions: `fs_store_fd()` writes signature and format version; `fs_store()` writes header and metadata sections; `fs_loadall()` opens and validates signatures, calls `fs_load()`, reconnects chunks, and recalculates checksums; `fs_load()` handles legacy linear formats and modern labeled sections; `fs_storenode()/fs_loadnode()` serialize inode records; `fs_storeedge()/fs_loadedge()` serialize directory/trash/reserved name edges; `xattr_store()/xattr_load()` serialize xattrs; `fs_storefree()/fs_loadfree()` persist detained inode IDs; `fs_storequotas()/fs_loadquotas()` persist quota entries; `fs_storelocks()/fs_loadlocks()` persist flock and POSIX locks; `fs_new()` creates root metadata; `fs_storeall()` rotates changelogs and writes `metadata.mfs.tmp`; `fs_commit_metadata_dump()` rotates backups and renames the dump; `fs_load_changelogs()` and `fs_load_changelog()` apply changelog files.

Control flow: storing writes a fixed header, then nodes, edges, free IDs, optional labeled sections for xattrs, ACLs, quotas, locks, chunks, and EOF marker. Section headers reserve length, write content, seek back to fill length, then advance to the next section. Loading reads the metadata signature, chooses a version, loads either old fixed order or modern section stream, validates root consistency, attaches or rejects orphan nodes depending on `ignoreflag`, links files to chunks, and forces checksum recalculation. Dumping rotates changelogs, starts `MetadataDumper`, writes the temp file in foreground paths, fsyncs, commits or creates emergency alternatives, then broadcasts save status.

State and persistence behavior: this file is the durable metadata contract for `gMetadata`: node hash, root, inode pool, trash/reserved paths, xattr hashes, ACL storage, quota database/checksum, lock sets, chunk state, max node id, metadata version, and session id counter. It preserves compatibility with MooseFS/LizardFS legacy signatures and skips older unsupported quota/lock sections where needed.

Dependencies/integration: depends on low-level serialization helpers, `FSNode` classes, chunk persistence, xattr, ACL, quota, locks, metadata dumper, changelog restore, master/client/metalogger broadcasts, file rotation, and setup constants. It is central to master startup, shutdown, periodic dump, metarestore, and shadow recovery.

Risks and test signals: fixed stack buffers for nodes include large chunk arrays and rely on bounded loop writes. `ignoreflag` salvages missing parents by attaching to root, which can alter namespace shape. Section length mismatches are warning-or-fatal depending on `ignoreflag`. Store/load must maintain exact ordering for dependent structures: nodes before edges, then checks before chunks. Tests should perform round-trip metadata dumps across format versions, corrupt/truncated section handling, unknown section handling, ACL/xattr/quota/lock persistence, orphan recovery, changelog replay boundaries, fsync/rename error paths, and root-node validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_store.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_store.h -->
# sources/distributed-fs/lizardfs/src/master/filesystem_store.h

Purpose: declares metadata persistence exceptions and top-level load/store helpers for the master filesystem.

Important APIs/types/functions: defines `MetadataException`, `MetadataFsConsistencyException`, and `MetadataConsistencyException`; exposes `fs_commit_metadata_dump()`, `fs_emergency_saves()`, `fs_broadcast_metadata_saved()`, changelog load helpers, `fs_loadall()`, and `fs_store_fd()`.

Control flow: callers use `fs_loadall()` during startup/metarestore, `fs_store_fd()` for writing to an already opened stream, and `fs_commit_metadata_dump()`/`fs_emergency_saves()` around dump commit failures.

State and persistence behavior: the header itself has no state; declared functions read and write the complete metadata image and changelogs.

Dependencies/integration: includes the shared exception base and `MetadataDumper` type. It is included by initialization, dump, restore, and storage modules.

Risks and test signals: exception taxonomy is broad and consumers need to distinguish structure/read consistency errors from lower-level I/O. Tests should assert thrown exception classes/messages for bad headers, missing files, and corrupted metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_store.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_store_acl.cc -->
# sources/distributed-fs/lizardfs/src/master/filesystem_store_acl.cc

Purpose: serializes and deserializes ACL metadata, including migration from legacy extended/default ACL encodings to current `RichACL` storage.

Important APIs/types/functions: `fs_store_acls()` iterates all nodes and writes present `RichACL` entries followed by a zero marker; `fs_load_legacy_acls()` loads old combined extended/default ACL records and converts them; `fs_load_posix_acls()` loads separate access and default POSIX ACL streams; `fs_load_acls()` loads current `RichACL` records. Helper loaders validate entry size, inode existence, and default-ACL directory constraints.

Control flow: each loader repeatedly reads a serialized-size prefix; size zero ends the stream. For legacy/POSIX entries it resolves the inode, deserializes ACL content, merges with any existing `RichACL`, and updates node mode for access ACLs. Current ACL loading directly sets `gMetadata->acl_storage`.

State and persistence behavior: ACLs are persisted in the metadata `ACLS` section. Loading mutates `gMetadata->acl_storage` and may mutate `FSNode::mode` during legacy/POSIX conversion. It does not emit changelog entries because it is part of metadata image loading.

Dependencies/integration: depends on serialization, `FSNode` lookup, `RichACL`, POSIX/legacy ACL classes, metadata singleton, and the store section dispatcher in `filesystem_store.cc`.

Risks and test signals: bad entry sizes above 10,000,000 are rejected; ignore mode can skip recoverable exceptions. Setting a default ACL on a non-directory is fatal unless ignored. Header/API mismatch risk exists because the header declares `fs_store_acls()` as `int` while the implementation returns `void`. Tests should cover all three section versions, mode recalculation, merge ordering of access/default ACLs, missing inode behavior, and the header/implementation type contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_store_acl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_store_acl.h -->
# sources/distributed-fs/lizardfs/src/master/filesystem_store_acl.h

Purpose: declares ACL metadata section load/store functions used by `filesystem_store.cc`.

Important APIs/types/functions: exposes `fs_load_legacy_acls()`, `fs_load_posix_acls()`, `fs_load_acls()`, and `fs_store_acls(FILE *)`.

Control flow: the metadata section dispatcher chooses one of the load functions based on section label `ACLS 1.0`, `ACLS 1.1`, or `ACLS 1.2`; storing uses the current ACL writer.

State and persistence behavior: no state in the header; the declared functions mutate/persist `gMetadata->acl_storage` and sometimes node modes during migration.

Dependencies/integration: includes platform, `FILE`, exceptions, and `MetadataDumper`, though the actual ACL interface mostly needs file I/O and metadata types from implementation includes.

Risks and test signals: the declaration says `int fs_store_acls(FILE *fd)` while the implementation defines `void fs_store_acls(FILE *fd)`, a compile/link contract risk if both are included consistently. Tests/builds should compile the implementation with its header and verify store error signaling expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_store_acl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_xattr.cc -->
# sources/distributed-fs/lizardfs/src/master/filesystem_xattr.cc

Purpose: implements in-memory extended attribute storage operations and checksum maintenance for master metadata.

Important APIs/types/functions: `xattr_setattr()` creates, replaces, or removes an xattr with create-only/replace-only/remove modes; `xattr_getattr()` returns a pointer and length for an attribute value; `xattr_listattr_leng()` returns list size and an inode-entry cookie; `xattr_listattr_data()` copies null-terminated names; `xattr_removeinode()` removes all xattrs for an inode; `xattr_recalculate_checksum()` rebuilds global xattr checksum; `xattr_checksum_add_to_background()` participates in background checksum updates.

Control flow: set operations validate value/name lengths, find or create the inode hash entry, find the data entry by `(inode,name)`, enforce mode semantics, update linked lists and aggregate name/value lengths, and adjust checksums. Removal unlinks from both inode-local and global data hash chains and deletes the entry. Listing first locates inode aggregate data, then copies each name plus null terminator.

State and persistence behavior: state lives in `gMetadata->xattr_inode_hash`, `gMetadata->xattr_data_hash`, per-entry allocation, per-entry checksum, and `gMetadata->xattrChecksum`. Persistence is handled by `xattr_store()`/`xattr_load()` in `filesystem_store.cc`.

Dependencies/integration: depends on checksum helpers, `gChecksumBackgroundUpdater`, hash combine logic, LizardFS xattr size constants, and metadata singleton. Filesystem operations call these helpers when servicing xattr client requests or deleting inodes.

Risks and test signals: values returned by `xattr_getattr()` are internal pointers, so callers must not outlive mutation/removal. `xattr_listattr_leng()` adds to `*xasize` rather than resetting it, so callers must initialize the output. Manual memory and two linked-list indexes require exact unlinking. Tests should cover create/replace/remove modes, empty values, max-name/list/value bounds, checksum changes and recalculation equality, inode deletion cleanup, and list buffer content.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_xattr.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_xattr.h -->
# sources/distributed-fs/lizardfs/src/master/filesystem_xattr.h

Purpose: defines xattr hash-table structures, hash functions, validation helpers, and the public xattr manipulation API.

Important APIs/types/functions: constants define inode/data hash sizes and checksum seed; `xattr_data_entry` stores one attribute with links in both hash indexes and frees name/value in its destructor; `xattr_inode_entry` aggregates an inode's attributes and list/value lengths; `xattr_data_hash_fn()` and `xattr_inode_hash_fn()` compute table indexes; public functions cover checksum integration, list/get/set/remove, and checksum recalculation.

Control flow: callers use hash helpers indirectly through implementation functions. `xattr_namecheck()` rejects embedded nulls outside metarestore builds.

State and persistence behavior: the structs are the in-memory persisted model loaded from metadata sections. The header also declares `void free(xattr_data_entry *)` to prevent accidental C-style freeing of entries that need destructors.

Dependencies/integration: used by filesystem xattr operations and metadata store load/save. It depends on platform constants such as `MFS_XATTR_SIZE_MAX`, `MFS_XATTR_LIST_MAX`, and xattr set modes.

Risks and test signals: fixed hash sizes assume power-of-two masks; manual ownership is split between `new/delete` for data entries and `malloc/free` for inode entries. Tests should include memory-safety paths and hash collision behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/filesystem_xattr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/flocks_unittest.cc -->
# sources/distributed-fs/lizardfs/src/master/flocks_unittest.cc

Purpose: tests BSD-style whole-file lock behavior using the shared `FileLocks` implementation over range `[0,1)`.

Important APIs/types/functions: helper functions wrap `exclusiveLock()`, `sharedLock()`, `unlock()`, `gatherCandidates()`, and `apply()`; `SharedAndExclusive` exercises shared stacking, owner overwrite, queued exclusive locks, and queued shared locks; `Nonblocking` verifies nonblocking failures are not enqueued.

Control flow: tests apply locks, gather pending candidates after each potentially releasing operation, and flush candidates back through `apply()` to mimic server lock-wakeup behavior.

State and persistence behavior: uses in-memory `FileLocks`; no persistence is tested here.

Dependencies/integration: depends on GoogleTest and `master/locks.h`. It signals expected behavior for client flock handling layered on `FileLocks`.

Risks and test signals: tests focus on one inode and a one-byte interval, so they do not cover range splitting or serialization. They are strong signals for pending-queue semantics and nonblocking behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/flocks_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/fs_context.h -->
# sources/distributed-fs/lizardfs/src/master/fs_context.h

Purpose: defines `FsContext`, the immutable operation context carrying timestamp, process personality, optional session data, and optional remapped/original user and group credentials for filesystem operations.

Important APIs/types/functions: static factories create contexts for restore/shadow, master without session, master with session, and master with secondary groups. Accessors expose `ts()`, `personality()`, `isPersonalityMaster()`, `isPersonalityShadow()`, `rootinode()`, `sesflags()`, `uid()`, `gid()`, `groups()`, `hasGroup()`, `auid()`, `agid()`, and booleans indicating whether permission checks are possible.

Control flow: operation code receives a context and asserts/accesses only the fields relevant to its path. `canCheckPermissions()` is true only for master contexts that have both session and credential data.

State and persistence behavior: no persistence; it is per-operation in-memory state. Timestamp is used for metadata changelog/checksum operations.

Dependencies/integration: depends on protocol credential containers, session flags from client/master protocol, special inode constants, and master personality. Used broadly by filesystem operation modules.

Risks and test signals: many accessors use `assert()` rather than runtime errors, so release builds can hide misuse only if fields are read incorrectly elsewhere. The overload taking `const GroupsContainer &` uses `std::move(gids)` in the factory call but copies in the constructor, which is harmless but confusing. Tests should cover factory field presence, `hasGroup()`, meta-root contexts, and permission-check gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/fs_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/get_servers_for_new_chunk.cc -->
# sources/distributed-fs/lizardfs/src/master/get_servers_for_new_chunk.cc

Purpose: implements the server selection algorithm for placing new chunk copies or slice parts across chunkservers while respecting labels, minimum version, prior selections, weights, load factors, and optional IP spreading.

Important APIs/types/functions: `prepareData()` synchronizes and resets `ChunkCreationHistory`, copies previous created-counts into local server counters, randomizes equal cases, stable-sorts by relative usage/weight/load, and optionally calls `sortAvoidingSameIp()`; `sortAvoidingSameIp()` groups servers by per-IP occurrence count to avoid adjacent same-IP selections; `chooseServersForLabels()` first satisfies explicit non-wildcard label counts, then fills remaining expected copies with any eligible unused servers, and increments history for selected servers.

Control flow: callers add candidate servers, call `prepareData(history)`, then call `chooseServersForLabels()` for each goal slice/part while passing a shared `used` vector. The method skips servers below `min_version` or already used in the chunk.

State and persistence behavior: history is caller-owned process memory, not persistent metadata. It resets when server list length, pointer identity, label, weight, or created-count threshold changes.

Dependencies/integration: depends on `Goal::Slice`, media labels, `matocsserventry`, global `gAvoidSameIpChunkservers`, `matocsserv_get_servip()`, and randomization utilities. Integrated into chunk creation in the master.

Risks and test signals: raw server pointers are used as identity in history and `used`, so lifetime/order changes reset balance. `std::random_shuffle` is legacy and affects determinism. Sorting multiplies counts by weights and relies on the million-chunk reset to avoid overflow. Tests should cover min-version filtering, label shortages, wildcard fill, used-vector exclusion across slices, weighted distribution, same-IP reordering, and history resets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/get_servers_for_new_chunk.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/get_servers_for_new_chunk.h -->
# sources/distributed-fs/lizardfs/src/master/get_servers_for_new_chunk.h

Purpose: declares data structures and class API for selecting chunkservers for a newly created chunk.

Important APIs/types/functions: `ChunkserverChunkCounter` records server pointer, media label, weight, version, created-count history, and load factor; `ChunkCreationHistory` is a vector of those counters; `GetServersForNewChunk::addServer()` appends candidates; `prepareData()` orders candidates and syncs history; `chooseServersForLabels()` selects servers for a goal part while honoring min version and already-used servers.

Control flow: build one selector per placement attempt, add candidate servers, prepare with persistent history, then call choose for goal label parts.

State and persistence behavior: `servers_` is per-selector transient state. History is persistent only across calls in memory to smooth placement distribution.

Dependencies/integration: depends on `common/goal.h`, `MediaLabel`, and `matocsserventry`. It is integrated by the chunk creation path.

Risks and test signals: `addServer()` accepts weights as signed integers; callers must avoid zero/negative nonsensical weights. Tests should assert default construction and that `used` is mutated as part of selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/get_servers_for_new_chunk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/get_servers_for_new_chunk_unittest.cc -->
# sources/distributed-fs/lizardfs/src/master/get_servers_for_new_chunk_unittest.cc

Purpose: validates chunkserver selection for label satisfaction and long-run weighted distribution across many goal definitions.

Important APIs/types/functions: `createProxy()` builds a `Goal::Slice::ConstPartProxy`; `GetServersForNewChunkTests` maps string server names to labels and reinterprets map entries as fake `matocsserventry *`; `ChooseServers0..5` cover shortages and label constraints; `testScenario()` parses goal definitions, simulates many chunk placements, and verifies per-weight usage spread; `ChunkDistribution` enumerates standard, XOR, and erasure-code scenarios.

Control flow: each scenario repeatedly constructs a selector, adds servers with labels/weights, prepares shared history, chooses servers for every goal slice part with a shared `used` list, accumulates counts, and compares normalized usage.

State and persistence behavior: tests use in-memory `ChunkCreationHistory` to verify balancing over repeated placements; no disk persistence.

Dependencies/integration: depends on GoogleTest, media labels, goal config parser, and the chunk placement API.

Risks and test signals: tests use fake pointer identities and version/load factor zero, so they do not cover min-version or load-factor prioritization. Random shuffle can make distribution tests sensitive, though high iteration counts reduce variance. These tests are the main signal for preserving weighted placement behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/get_servers_for_new_chunk_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/goal_cache.h -->
# sources/distributed-fs/lizardfs/src/master/goal_cache.h

Purpose: defines an LRU cache mapping chunk goal-counter summaries to resolved `Goal` objects.

Important APIs/types/functions: `CountersHasher` hashes only each `GoalCounter::goal`; `CountersComparator` compares counter-vector size and goal ids, also ignoring counts; `GoalCache` aliases `GenericLruCache<ChunkGoalCounters, Goal, 0x10000, ...>`.

Control flow: callers can cache goal resolution keyed by the set/order of goal ids present in `ChunkGoalCounters`.

State and persistence behavior: cache state is transient in memory and capped at 65,536 entries. It is not persisted.

Dependencies/integration: depends on `GenericLruCache` and `ChunkGoalCounters`. Used by master chunk/goal computation paths to avoid rebuilding goals for repeated counter patterns.

Risks and test signals: comparator ignores counts and only compares goal ids, which is correct only if resolved `Goal` depends solely on the goal-id sequence rather than counts. Tests should verify cache hits/misses for same goal ids with different counters and confirm that this intentional key reduction is valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/goal_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/goal_config_loader.cc -->
# sources/distributed-fs/lizardfs/src/master/goal_config_loader.cc

Purpose: parses LizardFS goal configuration lines into `Goal` objects, supporting legacy standard-copy syntax and newer typed slice syntax for standard, XOR, and erasure-code goals.

Important APIs/types/functions: token helpers validate allowed characters and split on whitespace or `{ } $ : #`; `parseGoalId()` validates `GoalId` range; `parseGoalName()` validates name and colon; `parseSliceType()` handles `$std`, `$xor2..$xor9`, and `$ec(k,m)` plus optional braces; `parseLabels()` populates standard or per-part labels; `defaultGoal()` creates wildcard goals for unspecified ids; `parseLine()` parses one line; `load()` parses a stream, rejects duplicate ids, reports line-numbered parse errors, and fills defaults.

Control flow: `load()` reads line-by-line, skips empty/comment-only lines through tokenization, parses non-empty entries, stores them by id, checks stream errors, then adds default goals for every valid missing id.

State and persistence behavior: no persistent state. The returned map is process configuration used by goal management.

Dependencies/integration: depends on `Goal`, `GoalId`, `MediaLabelManager`, slice traits for erasure-code bounds/type conversion, and `ParseException`. Integrated by master goal configuration loading and tests.

Risks and test signals: the tokenizer rejects unexpected punctuation early, so config compatibility depends on allowed character maintenance. Standard goals check raw token count before label aggregation, while typed non-standard goals validate part count in `parseLabels()`. Tests should cover comments, whitespace/braces variants, duplicate ids, invalid names/labels, erasure bounds, default fill, stream I/O errors, and line-numbered errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/goal_config_loader.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/goal_config_loader.h -->
# sources/distributed-fs/lizardfs/src/master/goal_config_loader.h

Purpose: declares the goal configuration parser API and compatibility default constant.

Important APIs/types/functions: `goal_config::kMaxCompatibleGoal` caps old-style default wildcard copies at five; `load(std::istream &)`, `load(std::istream &&)`, `parseLine()`, and `defaultGoal()` are the exposed parser helpers.

Control flow: callers load a stream or parse individual lines, then consume the returned id-to-`Goal` map.

State and persistence behavior: no state. Parsed goals become runtime configuration elsewhere.

Dependencies/integration: includes `common/goal.h` and standard containers/character helpers. Used by master config loading and chunk placement tests.

Risks and test signals: parser functions throw `ParseException`, so callers must surface configuration failures clearly. Tests should confirm rvalue/lvalue stream overload parity and default goal cap behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/goal_config_loader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/goal_config_loader_unittest.cc -->
# sources/distributed-fs/lizardfs/src/master/goal_config_loader_unittest.cc

Purpose: verifies default goal generation, old-format parsing, new-format typed parsing, and error detection for malformed goal configuration lines.

Important APIs/types/functions: `createSlice()` builds expected `Goal::Slice` values; `EXPECT_GOAL` checks size, name, and slice; `Defaults`, `OldFormat`, and `NewFormat` cover accepted syntax; `IncorrectLines` covers malformed structure, invalid ids/names/labels/types, bad erasure definitions, too many labels, and duplicates.

Control flow: tests load synthetic config strings through `goal_config::load()` and compare every significant parsed field, including default-filled goals.

State and persistence behavior: no persistent state; only in-memory parser outputs.

Dependencies/integration: depends on GoogleTest, `ParseException`, media labels, slice traits, and the parser API.

Risks and test signals: the suite is comprehensive for syntax but does not test `stream.bad()` I/O failures or localized character behavior of `std::isalnum`/`std::isspace`. It is the primary regression signal for config compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/goal_config_loader_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/hstorage_init.cc -->
# sources/distributed-fs/lizardfs/src/master/hstorage_init.cc

Purpose: initializes and owns the process-global `hstorage::Storage` backend used by `hstorage::Handle` name strings.

Important APIs/types/functions: `hstorage_init()` reads storage config, chooses Berkeley DB or memory backend, registers reload/destruct callbacks, and returns success; `hstorage_reload()` warns when storage-related options change at runtime and require restart; `hstorage_term()` resets the global storage.

Control flow: initialization reads `USE_BDB_FOR_NAME_STORAGE`, `DATA_PATH`, and `BDB_NAME_STORAGE_CACHE_SIZE`; if BDB is requested and compiled in it opens `name_storage.db`, otherwise it logs and falls back to `MemStorage`. Reload compares new config values with saved globals and logs non-reloadable changes.

State and persistence behavior: globals store selected backend flag, BDB path, and cache size. `Storage::reset()` installs or destroys the backend. BDB name storage writes a heap database under the data path; memory storage is volatile.

Dependencies/integration: depends on config/event loop, `MemStorage`, optional `BDBStorage`, setup path constants, and syslog. `init.h` requires this module to run first because directory-entry handles depend on an active storage implementation.

Risks and test signals: config key mismatch exists between reload (`USE_BDB_NAME_STORAGE`) and init (`USE_BDB_FOR_NAME_STORAGE`), so reload warnings may not reflect the real init option. Resetting storage while handles still exist would break destructors. Tests should cover backend selection with/without libdb, fallback logging, restart-required warnings, and init ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/hstorage_init.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/hstorage_init.h -->
# sources/distributed-fs/lizardfs/src/master/hstorage_init.h

Purpose: declares `hstorage_init()`, the startup hook for global name storage.

Important APIs/types/functions: `hstorage_init()` returns an integer status for the master run table.

Control flow: called early from `RunTab` before metadata structures that create `hstorage::Handle` values.

State and persistence behavior: no direct state in the header; implementation installs the storage backend.

Dependencies/integration: included by `init.h` and linked with the name storage implementations.

Risks and test signals: no term/reload declarations are exposed, so lifecycle is event-loop registered internally. Tests should verify the run table calls this before filesystem initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/hstorage_init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/hstring.h -->
# sources/distributed-fs/lizardfs/src/master/hstring.h

Purpose: defines `HString`, a `std::string` subclass with a cached 32-bit hash used to speed dominant name comparisons in filesystem lookup paths.

Important APIs/types/functions: constructors from C string, `std::string`, iterators, copy, and move all call `computeHash()`; assignment operators recompute hash; `hash()` exposes the cached value; equality/inequality operators compare hashes first and only compare full strings on hash match.

Control flow: instances behave like strings but keep hash synchronized after construction/assignment through the provided API.

State and persistence behavior: stores only in-memory string content and cached hash. Directory-entry persistence stores names through `hstorage::Handle`, not `HString` itself.

Dependencies/integration: used by filesystem node names, quota path output, snapshot names, and `hstorage` backends. It uses `std::hash<std::string>`.

Risks and test signals: inheriting from `std::string` means base mutating methods can be called without recomputing `hash_`, producing stale hashes. Move constructor recomputes after move rather than preserving source hash, which is safe. Tests should avoid or explicitly cover mutation through base APIs and verify hash-first comparison still handles collisions through full compare.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/hstring.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/hstring_bdbstorage.cc -->
# sources/distributed-fs/lizardfs/src/master/hstring_bdbstorage.cc

Purpose: implements Berkeley DB-backed storage for `hstorage::Handle` string names.

Important APIs/types/functions: constructor creates a DB handle, sets optional page size and cache size, and opens a truncating heap database; destructor closes DB with `DB_NOSYNC`; `compare()` checks encoded hash before retrieving; `get()` decodes record id and reads the string; `copy()` rebinds a copy; `bind()` appends a null-terminated string to DB and encodes record id plus hash; `unbind()` deletes the DB record; `encode()` and `decode()` pack/unpack `DB_HEAP_RID` and hash into a 64-bit handle.

Control flow: handle creation inserts a string into DB and stores a compact encoded reference. Comparisons avoid DB reads unless the 16-bit hash matches. Destruction deletes the corresponding heap record.

State and persistence behavior: stores transient name strings in a Berkeley DB heap file opened with `DB_CREATE | DB_TRUNCATE`; it is storage-backed but recreated on master start, not a durable metadata authority. Handle values encode a salted page number and index plus hash.

Dependencies/integration: depends on libdb C API and the `hstorage::Storage` virtual interface. Selected by `hstorage_init()` when compiled with DB support.

Risks and test signals: DB is truncated on open, so all existing handles must be loaded after initialization. `get()` returns `data.data` as a C string from DB memory, which relies on libdb allocation semantics and null termination from `bind()`. Hash is only 16 bits, so collisions must fall back to full retrieval. Tests should cover open failures, cache/page parameters, copy/delete lifecycle, hash collision behavior, and cleanup of temp DB files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/hstring_bdbstorage.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/hstring_bdbstorage.h -->
# sources/distributed-fs/lizardfs/src/master/hstring_bdbstorage.h

Purpose: declares the Berkeley DB implementation of the name-string storage interface.

Important APIs/types/functions: `BDBStorage` overrides `compare()`, `get()`, `copy()`, `bind()`, `unbind()`, and `name()`; static `hash()` extracts the top 16 bits from a handle; private `encode()`, `decode()`, and overload `bind()` handle DB record IDs and cached hashes.

Control flow: callers interact through the `Storage` base; implementation manages a `DB *` and heap record ids.

State and persistence behavior: owns a DB handle and path string. The encoded handle stores DB heap record coordinates plus hash.

Dependencies/integration: depends on `<db.h>`, `hstring_storage.h`, and compile-time checks for expected DB record-id field sizes.

Risks and test signals: compile-time static assertions constrain supported libdb ABI. Tests should validate behavior only when `LIZARDFS_HAVE_DB` is enabled and should ensure handle salt prevents a valid record with hash zero from looking empty.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/hstring_bdbstorage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/hstring_memstorage.cc -->
# sources/distributed-fs/lizardfs/src/master/hstring_memstorage.cc

Purpose: implements in-memory `hstorage::Storage` using heap-allocated C strings encoded directly into `Handle` values with cached hashes.

Important APIs/types/functions: `compare()` uses the encoded 16-bit hash before comparing against decoded C string; `get()` returns the decoded string; `copy()` duplicates another handle's C string; `bind()` allocates and copies a null-terminated string; `encode()` packs pointer and hash; `unbind()` frees the pointer; `name()` returns `MemStorage`.

Control flow: binding allocates one C string per handle and stores pointer bits plus hash in the handle. Copy creates a deep duplicate; move is handled by `Handle`. Unbind frees the decoded pointer.

State and persistence behavior: all state is volatile heap memory. Debug builds track raw pointers in `debug_ptr_` for validation/Valgrind friendliness.

Dependencies/integration: depends on `hstring_memstorage.h`, allocation functions, and the `Storage` interface. It is the default name backend.

Risks and test signals: pointer obfuscation assumes user-space pointers fit in the low bits after reserving 16 hash bits, which is documented as 48-bit virtual address behavior. `Handle` move assignment overwrites without unbinding existing data in the destination, so callers must avoid assigning over a bound handle by move or tests should catch leaks. Tests should cover copy/deep-copy, empty strings, hash extraction, debug pointer tracking, and pointer-width assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/hstring_memstorage.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/hstring_memstorage.h -->
# sources/distributed-fs/lizardfs/src/master/hstring_memstorage.h

Purpose: declares the in-memory implementation of `hstorage::Storage`.

Important APIs/types/functions: `MemStorage` overrides storage operations; static `hash()` extracts cached hash from a handle; static `c_str()` decodes const and mutable pointers; private `encode()` packs pointer and hash; debug builds keep a static set of unobfuscated pointers.

Control flow: used through `Storage::instance()` and installed by `hstorage_init()` or tests.

State and persistence behavior: stores per-handle heap allocations only; no disk persistence.

Dependencies/integration: depends on `hstring_storage.h` and `<set>` for debug tracking.

Risks and test signals: `static_assert(sizeof(void *) <= 8)` is necessary but not sufficient for every 64-bit address layout. Tests should run under sanitizers/Valgrind with pointer obfuscation enabled when possible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/hstring_memstorage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/hstring_storage.h -->
# sources/distributed-fs/lizardfs/src/master/hstring_storage.h

Purpose: defines the abstract storage interface for filesystem name strings and the RAII `Handle` wrapper used in directory entries and trash/reserved path containers.

Important APIs/types/functions: `Storage::instance()`, `reset()`, and virtual `compare()`, `get()`, `copy()`, `bind()`, `unbind()`, `name()` define backend operations. `Handle` stores a 64-bit backend-defined value, copies by deep storage copy, moves by stealing data, binds from `HString`/`std::string`, unbinds in destructor, converts to string/HString, exposes `hash()`, and supports comparison operators with `HString`.

Control flow: a backend must be installed before any non-empty `Handle` construction/destruction. Copy assignment unbinds current data then copies; `set()` replaces current binding. Equality uses backend hash/full comparison, while ordering converts to `std::string`.

State and persistence behavior: global storage backend is a static unique pointer hidden behind `Storage::static_wrapper<0>`. Handles themselves are persisted only indirectly by serializing string values from storage, not by saving raw handle data.

Dependencies/integration: used by filesystem directory maps, metadata store edge serialization, hstorage init, and tests.

Risks and test signals: `Storage::instance()` dereferences without null checks; initialization and teardown ordering are critical. Move assignment does not unbind an already-bound destination before overwriting `data_`, creating a potential leak. `unlink()` intentionally drops ownership without unbinding and must be used carefully. Tests should cover lifecycle order, copy/move assignment over bound handles, comparison semantics, and reset behavior after handles are destroyed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/hstring_storage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/hstring_unittest.cc -->
# sources/distributed-fs/lizardfs/src/master/hstring_unittest.cc

Purpose: tests `HString` and `hstorage::Handle` behavior for memory storage and, when compiled in, Berkeley DB storage.

Important APIs/types/functions: `Name` checks backend name; `MemComparison`, `MemGet`, `MemHash`, and `MemCopy` cover comparison, retrieval, hash extraction, copy/move assignment for `MemStorage`; BDB variants repeat comparison/get/hash/copy behavior with a temporary DB file.

Control flow: each test installs a storage backend with `Storage::reset()`, creates `HString` and `Handle` objects, performs comparisons or assignments, and resets/removes BDB files after handles leave scope.

State and persistence behavior: tests manipulate the process-global storage singleton and temporary `/tmp/db.db` for BDB.

Dependencies/integration: depends on GoogleTest, `MemStorage`, optional `BDBStorage`, and standard functional utilities.

Risks and test signals: BDB copy test appears to install `MemStorage`, so it does not actually exercise BDB copy semantics. Tests use a fixed `/tmp/db.db` path, which can collide across parallel runs. They do not cover move assignment over an already-bound destination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/hstring_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/id_pool_detainer.h -->
# sources/distributed-fs/lizardfs/src/master/id_pool_detainer.h

Purpose: implements an ID pool wrapper that detains released IDs for at least a configured time before reuse, reducing quick inode/id reuse hazards.

Important APIs/types/functions: `detail::SparseBitset` has a Judy-backed implementation when available and a deque fallback otherwise; `IdPoolDetainer` extends `IdPool`, stores detained IDs in timestamped buckets, exposes `acquire()`, `acquire(ts)`, `release(id,ts)`, `markAsAcquired()`, `detain()`, `releaseDetained()`, `detainedCount()`, `size()`, iteration over detained entries, and `maxSize()`.

Control flow: timestamped acquire/release calls first release a bounded number of expired detained IDs. Releasing an acquired id inserts it into the current/recent bucket unless detention is full, in which case oldest detained IDs are forced back to the base pool. Plain `acquire()` uses base pool first; if exhausted, it pulls an oldest detained ID early. `markAsAcquired()` can remove an ID from detention when metadata loading discovers it is actually in use.

State and persistence behavior: detention state is in-memory buckets of ID sets and timestamps. The metadata store persists detained IDs and timestamps through `fs_storefree()`/`fs_loadfree()` for inode pools.

Dependencies/integration: depends on `IdPool`, optional Judy arrays, STL containers, and assertions. Used by master inode allocation/free persistence.

Risks and test signals: deque fallback has O(n) test/unset and `set()` does not reject duplicates, so skip-check misuse can corrupt counts. `bucket_time_ = detain_time / bucket_count` can be zero if misconfigured. Early reuse occurs when base pool is exhausted or detention cap forces release. Tests should cover expiry boundary, bucket_count zero/large cases, duplicate detention protection, metadata load via `markAsAcquired()`, iterator correctness, Judy and fallback behavior, and forced release policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/id_pool_detainer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/id_pool_detainer_unittest.cc -->
# sources/distributed-fs/lizardfs/src/master/id_pool_detainer_unittest.cc

Purpose: verifies basic `IdPoolDetainer` allocation, release, null-id behavior, mark-as-acquired, detention, iteration, and expiry.

Important APIs/types/functions: `TestGet` drains the pool; `TestPut` repeatedly acquire/releases; `TestIdIsNull` and `TestPutNull` check null id handling; `TestIfAllDifferent` checks uniqueness and immediate reuse when release count is zero/base behavior; `TestMarkAsAcquired` reserves specific ids; `TestIfDetained` releases a set into detention, verifies later acquires avoid them, iterates detained ids, then releases expired detention.

Control flow: tests instantiate `IdPoolDetainer<uint32_t,uint32_t>` with small pool sizes and deterministic timestamps, then assert pool counts and returned ids.

State and persistence behavior: no disk persistence tested; in-memory detention only.

Dependencies/integration: depends on GoogleTest and the detainer template.

Risks and test signals: tests do not cover detention cap overflow, Judy backend, bucket boundary exactness, duplicate release into detention, or `detain()` API. They provide good coverage for common inode-pool behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/id_pool_detainer_unittest.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/init.h -->
# sources/distributed-fs/lizardfs/src/master/init.h

Purpose: defines master initialization run tables and version identifier for the LizardFS master process.

Important APIs/types/functions: `RunTab` lists startup functions and display names; `EarlyRunTab` validates personality before main initialization; `LateRunTab` is empty. The run order starts with `hstorage_init`, then personality, random generator, data cache, sessions, exports, topology, filesystem, charts, master/metalogger/chunkserver/taperserver/client networking.

Control flow: the master main framework iterates these tables to initialize subsystems. Comments document ordering constraints, especially name storage first, personality second, data cache/sessions before filesystem, and client network after filesystem.

State and persistence behavior: no persistent state here, but startup order determines when metadata/session/export state is loaded and when name storage handles are safe.

Dependencies/integration: includes subsystem headers for every initialization function and exposes the `id` version string.

Risks and test signals: order is critical and mostly encoded by comments plus table position. Tests or startup checks should catch accidental reordering of `hstorage_init`, personality validation/init, session load, and filesystem init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/itree.cc -->
# sources/distributed-fs/lizardfs/src/master/itree.cc

Purpose: implements a simple interval tree mapping inclusive `uint32_t` ranges to nonzero ids, with id zero used as deletion.

Important APIs/types/functions: internal `itnode` stores `from`, `to`, `id`, left, and right; `itree_add_interval()` adds or deletes a normalized interval; `itree_find()` returns id for a point or zero; `itree_rebalance()` converts tree to list, simplifies adjacent same-id intervals, and rebuilds a more balanced tree; `itree_freeall()` frees all nodes. Helpers split, overwrite, delete, and remove tree nodes.

Control flow: adding overlaps recursively splits existing ranges, deletes covered subranges, or overwrites ids. Deleting removes or trims intervals. Rebalance performs in-order flattening using `left` as next pointer, merges adjacent same-id intervals, then recursively chooses midpoints.

State and persistence behavior: state is caller-owned opaque tree pointer. No direct persistence; callers must serialize their interval meanings elsewhere.

Dependencies/integration: C-style module using `malloc/free` and `passert`. It is likely used for mapping numeric ranges in master configuration or metadata helpers.

Risks and test signals: deletion/addition use inclusive endpoints and swap reversed inputs; off-by-one at `from-1`/`to+1` can overflow around 0 or `UINT32_MAX`. The rebalance is documented as square-time and not a production-grade balanced tree. Tests should cover overlapping replaces, deletes that split intervals, reversed inputs, adjacent merge, endpoint extremes, and repeated rebalance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/itree.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/itree.h -->
# sources/distributed-fs/lizardfs/src/master/itree.h

Purpose: declares the opaque C-style interval tree API.

Important APIs/types/functions: `itree_rebalance(void *)`, `itree_add_interval(void *, uint32_t, uint32_t, uint32_t)`, `itree_find(void *, uint32_t)`, and `itree_freeall(void *)`.

Control flow: callers keep the returned opaque pointer after add/rebalance calls and pass it back for lookups or freeing. Passing id zero to add deletes an interval.

State and persistence behavior: the tree is heap state hidden behind `void *`. No persistence.

Dependencies/integration: includes platform only; deliberately avoids exposing `itnode`.

Risks and test signals: type erasure means callers can pass invalid pointers without compile-time protection. Tests should include null roots and ensure callers always store returned roots after mutations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/itree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/locks.cc -->
# sources/distributed-fs/lizardfs/src/master/locks.cc

Purpose: implements byte-range lock normalization, collision detection, pending lock queues, lock listing, and lock persistence for flock/POSIX lock state.

Important APIs/types/functions: `LockRanges::findCollision()` finds incompatible overlaps; `fits()` wraps collision check; `insert()` splits, merges, overwrites, stacks shared owners, and removes unlock ranges; `FileLocks::sharedLock()`, `exclusiveLock()`, `unlock()`, `apply()`, `findCollision()`, `gatherCandidates()`, `removePending()` manage per-inode active and queued locks; copy helpers export locks to `lzfs_locks::Info`; `load()`/`store()` serialize active and pending maps.

Control flow: `FileLocks::apply()` creates an inode entry, inserts immediately if the range fits, or enqueues blocking non-unlock requests. Unlock is represented as a lock range of type `kUnlock` and is inserted through the same range-splitting machinery. After unlocks, callers gather overlapping pending candidates and retry them. Serialization writes counts and one `Info` per owner.

State and persistence behavior: active locks and pending locks are stored in unordered maps by inode. Metadata persistence writes both active and pending queues in the `FLCK 1.0` metadata section through `filesystem_store.cc`.

Dependencies/integration: depends on `compact_vector`, protocol `lock_info`, serialization helpers, and syslog for write errors. Used by client lock operations and metadata load/store.

Risks and test signals: `LockRanges::insert()` mutates iterators while inserting and later erases unlocking ranges over a saved range, so vector iterator math is delicate. Shared lock owner sets must remain sorted for binary search and merge. `FileLocks::clear()` only clears active locks, leaving pending locks untouched, which may be intentional or a bug depending on caller expectations. Pending load uses `push_back()` without sorting, while enqueue keeps sorted order. Tests should cover range splitting/merging, stacked shared locks, owner removal, pending queue gather/reapply, nonblocking semantics, serialization round trips, clear behavior, and loaded pending order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/locks.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/locks.h -->
# sources/distributed-fs/lizardfs/src/master/locks.h

Purpose: defines lock range types, owner identity, range-set container, and per-inode file lock manager API.

Important APIs/types/functions: `LockRange::Owner` compares only FUSE owner and session id for lock identity while retaining request/message ids for interrupts; `LockRange` represents half-open `[start,end)` shared/exclusive/unlock ranges with sorted owner sets; `LockRanges` stores normalized active ranges; `FileLocks` manages active and pending locks by inode, collision probes, lock/unlock operations, candidate gathering, pending removal, vector export, load/store, and clear.

Control flow: callers request locks through `FileLocks`; failed blocking locks enter pending queues; unlocks should be followed by `gatherCandidates()` and retry via `apply()`.

State and persistence behavior: state is in active and pending maps. `load()`/`store()` persist both maps to metadata sections.

Dependencies/integration: depends on compact vectors and protocol lock info. Integrated by master client lock handling and metadata store.

Risks and test signals: owner comparisons ignore `reqid` and `msgid`, so interrupt handling must not confuse identity with request tracking. Range end is half-open, unlike `itree` inclusive intervals. Template `unlock(predicate)` returns `{UINT64_MAX,0}` when no lock matched, so callers must check for empty result. Tests should cover owner ordering, half-open endpoint behavior, and predicate unlock effects on candidate ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/locks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/locks_unittest.cc -->
# sources/distributed-fs/lizardfs/src/master/locks_unittest.cc

Purpose: tests byte-range lock normalization and `FileLocks` pending queue behavior.

Important APIs/types/functions: helper functions add shared/exclusive/unlock ranges; tests cover exclusive overwrite, same-owner overwrites and splitting, overlapping reads, removals, adjacent range merge, stacked read locks, read hole punching, partial unlock, stress transitions, collision probe, pending unqueue, and candidate gathering.

Control flow: low-level tests call `LockRanges::fits()` then `insert()` directly. `FileLocks` tests use public APIs, remove pending locks by owner predicates, unlock ranges, gather candidates, and apply candidates.

State and persistence behavior: in-memory lock state only; persistence load/store is not tested in this file.

Dependencies/integration: depends on GoogleTest and `locks.h`.

Risks and test signals: this is strong coverage for normalization semantics but lacks serialization round trips, `copyActiveToVector()`/`copyPendingToVector()` checks, loaded pending queue sorting, `clear()` pending behavior, and predicate unlock return ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/master/locks_unittest.cc -->
