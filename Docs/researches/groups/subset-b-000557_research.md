# Research: subset-b-000557

This grouped report covers the assigned BeeGFS metadata and storage-daemon files. Each section preserves the source path in its title and is bounded by reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/MetadataEx.h -->
## sources/distributed-fs/beegfs/meta/source/storage/MetadataEx.h

Purpose: Defines metadata-server storage constants shared by metadata serialization and on-disk extended-attribute handling. It names the temporary metadata update suffix, the BeeGFS metadata xattr, and the remote-storage-target xattr.

Important APIs/types/functions: The exported constants are `META_UPDATE_EXT_STR`, `META_XATTR_NAME`, `RST_XATTR_NAME`, `METADATA_XATTR_NAME_LIST`, and `META_SERBUF_SIZE`. `METADATA_XATTR_NAME_LIST` is the authoritative list of non-user metadata attributes that buddy metadata resync must copy.

Control flow: Header-only constants; no runtime control flow.

State and persistence: The constants describe persistent xattr names on metadata entries and the serialized metadata buffer size used for transfer/copy operations. The maintainer warning is important: adding a metadata xattr without extending `METADATA_XATTR_NAME_LIST` can leave mirrored metadata inconsistent.

Dependencies and integration: Includes common metadata definitions and is consumed by metadata storage/resync code that reads, writes, serializes, or mirrors dentries and inode metadata.

Risks and test signals: Primary risk is schema drift between persisted xattrs and the hard-coded resync list. Regression tests should exercise buddy metadata resync with every system metadata xattr and buffer-size limits around `META_SERBUF_SIZE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/MetadataEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/MkFileDetails.h -->
## sources/distributed-fs/beegfs/meta/source/storage/MkFileDetails.h

Purpose: Provides a compact value object carrying file-creation inputs through metadata create paths.

Important APIs/types/functions: `MkFileDetails` stores `newName`, optional `newEntryID`, `userID`, `groupID`, `mode`, `umask`, and `createTime`. The constructor initializes the normal create fields, while `setNewEntryID()` is used for mirrored secondary operations that must reuse the primary's entry ID.

Control flow: Header-only data carrier; callers build it before entering create logic.

State and persistence: It does not persist directly, but its fields become dentry/inode metadata and POSIX mode ownership on disk. `newEntryID` changes identity allocation behavior during mirroring.

Dependencies and integration: Used by metadata storage operations that create file dentries and inodes. It depends on standard strings and BeeGFS common typedefs via surrounding includes.

Risks and test signals: Misusing `newEntryID` on primaries or ignoring it on secondaries would break mirrored identity consistency. Tests should cover create on primary, mirrored replay on secondary, and mode/umask propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/MkFileDetails.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/NodeOfflineWait.h -->
## sources/distributed-fs/beegfs/meta/source/storage/NodeOfflineWait.h

Purpose: Implements a small timer gate used when a metadata node must delay reporting state so clients and mgmtd can observe it as offline before resync-sensitive work resumes.

Important APIs/types/functions: `NodeOfflineWait(Config*)` derives `waitTimeoutMS` from `OfflineWaitTimeoutTk<Config>`. `startTimer()` marks the wait active and resets `timer`. `hasTimeout()` returns whether the wait is still active, clears `active` once elapsed time reaches the configured timeout, and logs remaining seconds while active.

Control flow: Reads `active` under a read lock, then upgrades by taking a write lock to check elapsed time and possibly clear `active`. Logging happens outside the critical state update but after the write lock is released.

State and persistence: Maintains only in-memory state: `RWLock`, immutable timeout, `Time timer`, and `active`. It intentionally delays state reporting rather than persisting anything.

Dependencies and integration: Uses BeeGFS locking (`SafeRWLock`), timing, offline timeout calculation, `Config`, and `LogContext`. It integrates with metadata primary/buddy resync startup logic.

Risks and test signals: `hasTimeout()` is semantically inverted: true means the wait is still active, not expired. Race tests should cover concurrent `startTimer()` and `hasTimeout()` calls, timeout boundary behavior, and log throttling concerns if polled frequently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/NodeOfflineWait.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/PosixACL.cpp -->
## sources/distributed-fs/beegfs/meta/source/storage/PosixACL.cpp

Purpose: Implements POSIX ACL xattr serialization/deserialization and mode-bit reconciliation for metadata-created entries.

Important APIs/types/functions: `defaultACLXAttrName` and `accessACLXAttrName` name Linux POSIX ACL xattrs. `deserializeXAttr()` validates `POSIX_ACL_XATTR_VERSION` then deserializes `ACLEntry` objects. `serializeXAttr()` computes serialized size then fills the buffer. `modifyModeBits()` transforms ACL permissions using a requested file mode and reports whether an ACL xattr remains needed. `toString()` provides debug rendering.

Control flow: Deserialization reads a version first and then loops until the deserializer consumes the input. Serialization intentionally runs twice to size then write. `modifyModeBits()` scans all ACL entries, handling owner, named users/groups, group object, mask, and other entries; after the scan it resolves group bits through the mask if present, otherwise through the group object.

State and persistence: The class owns an in-memory vector of ACL entries. Serialized output is persisted as `system.posix_acl_default` or `system.posix_acl_access` xattrs elsewhere. `modifyModeBits()` mutates entries and updates the passed mode bits.

Dependencies and integration: Depends on BeeGFS `Serializer`/`Deserializer`, `FhgfsOpsErr`, `CharVector`, and the entry layout declared in `PosixACL.h`. It integrates with metadata create/inherit-ACL paths and xattr storage.

Risks and test signals: `deserializeXAttr()` takes `&xattr[0]`; empty input would be unsafe unless callers reject it. ACLs missing a group/mask entry return `FhgfsOpsErr_INTERNAL`. Tests should cover empty/malformed xattrs, version mismatch, named-user/group ACLs needing persistence, mask-vs-group interactions, and round-trip serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/PosixACL.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/PosixACL.h -->
## sources/distributed-fs/beegfs/meta/source/storage/PosixACL.h

Purpose: Declares the in-memory POSIX ACL representation used by metadata storage.

Important APIs/types/functions: `ACLEntry` mirrors Linux POSIX ACL xattr layout with `tag`, `perm`, and `id`, plus `POSIX_ACL_XATTR_VERSION` and tag constants. Its templated `serialize()` wires the struct into BeeGFS serialization. `PosixACL` exposes `deserializeXAttr()`, `serializeXAttr()`, `modifyModeBits()`, `toString()`, `empty()`, and xattr-name constants.

Control flow: No significant header-side flow beyond the serializer template and simple `empty()` check.

State and persistence: `PosixACL` stores private `ACLEntryVec entries`; serialized form maps to Linux ACL xattrs and affects persisted file mode bits.

Dependencies and integration: Pulls in BeeGFS serialization, common types, and storage errors. It is an adapter between Linux ACL xattr bytes and BeeGFS metadata create/update code.

Risks and test signals: The serialized struct layout must remain compatible with Linux `posix_acl_xattr_entry`. Tests should check endian/field-width assumptions through known byte vectors and compatibility with kernel-generated ACL xattrs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/PosixACL.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/SyncedDiskAccessPath.h -->
## sources/distributed-fs/beegfs/meta/source/storage/SyncedDiskAccessPath.h

Purpose: Extends `Path` with serialized disk-access helpers and a monotonically increasing storage version for metadata path updates.

Important APIs/types/functions: Constructors initialize version state. `storageUpdateBegin()`/`storageUpdateEnd()` lock and unlock `diskMutex`. `incStorageVersion()` increments a combined high/low version. `createSubPathOnDisk()` and `removeSubPathDirsFromDisk()` wrap `StorageTk` path creation/removal under the mutex.

Control flow: `incStorageVersion()` increments low bits cheaply until a threshold, then samples current seconds to advance the high part when time changes. Path methods lock, compose base and subpath, call the `StorageTk` operation, and unlock.

State and persistence: Maintains in-memory `storageVersion`, `highVersion`, `lowVersion`, and a mutex. Disk changes are serialized at this path object; version values can identify updates but are not persisted in this class.

Dependencies and integration: Inherits `Path`, uses `System::getCurrentTimeSecs`, `Mutex`, and metadata `StorageTkEx`/common `StorageTk` helpers. It is meant for metadata storage paths where directory updates must not race.

Risks and test signals: Manual begin/end locking is exception-unsafe if callers add throwing work between them. The low-version mask `((lowVersion << 10) >> 10)` assumes unsigned width behavior. Tests should cover concurrent create/remove, version monotonicity under same-second bursts, and low-version rollover.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/SyncedDiskAccessPath.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/toolkit/BuddyCommTk.cpp -->
## sources/distributed-fs/beegfs/meta/source/toolkit/BuddyCommTk.cpp

Purpose: Implements metadata-server mirror-buddy communication helpers, especially persistent "buddy needs resync" state and primary-side resync start decisions.

Important APIs/types/functions: Internal state uses `.buddyneedsresync` as a `PreallocatedFile<uint8_t>` with flags for required/not-required and unacknowledged changes. Public functions are `prepareBuddyNeedsResyncState()`, `checkBuddyNeedsResync()`, `setBuddyNeedsResync()`, and `getBuddyNeedsResync()`. Internal `setBuddyNeedsResyncComm()` sends `SetTargetConsistencyStatesMsg` to mgmtd and schedules retries through `TimerQueue`.

Control flow: `setBuddyNeedsResync()` writes an unacked state to disk, cancels pending retry, and immediately tries mgmtd communication. On failure, a five-second timer calls `retrySetBuddyNeedsResyncComm()`. `checkBuddyNeedsResync()` runs on primaries, confirms the local node is `GOOD`, reads the buddy state, and starts a metadata `BuddyResyncer` when the online buddy is `NEEDS_RESYNC`.

State and persistence: Persistent byte file survives restart and carries unacknowledged mgmtd updates. Global lock protects the file and retry handle. On restart, `prepareBuddyNeedsResyncState()` enqueues immediate retry if the file has an unacked flag.

Dependencies and integration: Uses `Program::getApp()` to reach mgmt nodes, meta buddy group mapping, meta state store, internode syncer, timer queue, and buddy resyncer. It sends management-node target consistency messages and depends on `PreallocatedFile`.

Risks and test signals: Global state makes tests/order sensitive. `setBuddyNeedsResync(const std::string& path, ...)` ignores `path`, which is harmless but misleading. Failure modes include stale unacked file state, retry callback lifetime issues, and incorrect local primary detection. Tests should simulate mgmtd failures/retries, restart with unacked state, primary/secondary role changes, and external resync completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/toolkit/BuddyCommTk.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/toolkit/BuddyCommTk.h -->
## sources/distributed-fs/beegfs/meta/source/toolkit/BuddyCommTk.h

Purpose: Declares metadata mirror-buddy communication utilities.

Important APIs/types/functions: `prepareBuddyNeedsResyncState(Node&, const MirrorBuddyGroupMapper&, TimerQueue&, NumNodeID)` initializes persistent resync state. `checkBuddyNeedsResync()` polls state and starts resyncs. `setBuddyNeedsResync(const std::string&, bool)` requests mgmtd state changes. `getBuddyNeedsResync()` returns the local persisted flag.

Control flow: Header only declares the operations implemented in the cpp.

State and persistence: API exposes operations around the `.buddyneedsresync` persistent file and mgmtd consistency states.

Dependencies and integration: Requires BeeGFS `Node`, `MirrorBuddyGroupMapper`, `TimerQueue`, `NumNodeID`, and storage error types. Used by metadata app startup, internode sync, and mirroring code.

Risks and test signals: The unused `path` parameter on `setBuddyNeedsResync()` suggests an API inherited from storage-side code. Tests should verify callers do not expect per-path behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/toolkit/BuddyCommTk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/toolkit/StorageTkEx.cpp -->
## sources/distributed-fs/beegfs/meta/source/toolkit/StorageTkEx.cpp

Purpose: Adds metadata-server-specific storage toolkit behavior: storage-format validation and incremental contained-directory ID listing for fsck.

Important APIs/types/functions: `createStorageFormatFile()` writes format properties including `xattr=true/false`. `checkStorageFormatFile()` loads/upgrades a format file and rejects missing or mismatched xattr settings. `getContDirIDsIncremental()` lists metadata dentry hash directories incrementally using `seekdir()`/`d_off`. `getNextContDirID()` is a one-entry wrapper.

Control flow: Format creation reads config from `Program::getApp()`. Format checking loads properties and throws `InvalidConfigException` on missing `xattr` or config mismatch. Directory iteration computes hash subdirs, opens the directory, seeks to the caller's offset, filters entries, skips the root dir on non-root MDS, and returns the next offset.

State and persistence: Reads/writes the metadata storage format file and scans persistent dentry directory names. Does not lock fsck listing paths, as noted by the source comment.

Dependencies and integration: Depends on metadata `App`, `Config`, `StorageTk`, `MetaStorageTk`, `StorageTkEx.h`, POSIX directory APIs, and root-node/mirror-group state from the app.

Risks and test signals: `seekdir()` offsets are filesystem-specific and can become stale if directories mutate during fsck. No locking means concurrent metadata changes may cause missing or duplicate IDs. Tests should cover xattr format mismatch, root-dir skip behavior for mirrored/non-mirrored paths, incremental pagination, and opendir/readdir error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/toolkit/StorageTkEx.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/toolkit/StorageTkEx.h -->
## sources/distributed-fs/beegfs/meta/source/toolkit/StorageTkEx.h

Purpose: Declares metadata-specific storage toolkit helpers and storage format versions.

Important APIs/types/functions: Defines `STORAGETK_FORMAT_MIN_VERSION` as 3 and current version as 4. Declares storage-format operations and contained-dir iteration helpers. Inline helpers `getMetaInodeHashDir()` and `getMetaDentriesHashDir()` build first/second-level hash directory paths.

Control flow: Header inlines only string path composition.

State and persistence: Constants govern accepted on-disk storage format versions. Path helpers reflect the persistent hash-directory layout.

Dependencies and integration: Includes metadata config, common path, mutex, meta storage, and storage toolkit headers. Used by metadata startup, fsck helpers, and path-walking code.

Risks and test signals: Version constants are migration-sensitive. Tests should check path formatting uses hex directory names and that older supported format versions are accepted only through the cpp validation path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/toolkit/StorageTkEx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/toolkit/XAttrTk.cpp -->
## sources/distributed-fs/beegfs/meta/source/toolkit/XAttrTk.cpp

Purpose: Wraps Linux xattr operations for metadata entries, translating user-visible xattrs into BeeGFS-internal names and mapping errno to `FhgfsOpsErr`.

Important APIs/types/functions: `UserXAttrPrefix` is `user.bgXA.`. `listXAttrs()` returns raw xattr names. `getXAttr()` reads bounded xattr data. `sanitizeForUser()` removes non-user metadata attrs and strips the prefix. `removeMetadataAttrs()` filters names. `setUserXAttr()` writes prefixed user xattrs and optionally enforces `XATTR_LIST_MAX`. `removeUserXAttr()` removes a prefixed xattr. `listUserXAttrs()` lists and sanitizes user-visible names.

Control flow: List uses a two-step `listxattr()` size/read sequence. Set first tries `setxattr()`; when list-length limiting is enabled and creation is needed, it locks one of 1024 path-hashed mutexes, checks current list length, and retries without forced replace. Errno is translated to BeeGFS errors with unexpected failures logged server-side.

State and persistence: Persists user xattrs under prefixed names on metadata files. The path-hashed static mutex array is in-memory concurrency control for list-length enforcement.

Dependencies and integration: Uses `Program::getApp()->getConfig()->getLimitXAttrListLength()`, BeeGFS logging, `StringTk`, `Mutex`, and POSIX xattr syscalls.

Risks and test signals: `listXAttrs()` allocates `new char[0]` when there are no xattrs and then builds a string from size 0; this is usually fine but worth guarding. The list-length check can still race with non-BeeGFS writers or hash collisions. Tests should cover errno mappings, prefix stripping, metadata filtering, list-limit NOSPACE behavior, and create-vs-replace flag semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/toolkit/XAttrTk.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/toolkit/XAttrTk.h -->
## sources/distributed-fs/beegfs/meta/source/toolkit/XAttrTk.h

Purpose: Declares the metadata xattr toolkit API.

Important APIs/types/functions: Exposes `UserXAttrPrefix`, raw `listXAttrs()` and `getXAttr()`, sanitizers, user-prefixed set/remove/list helpers, and inline `getUserXAttr()` which prefixes the requested name before calling `getXAttr()`.

Control flow: Header-side flow is limited to inline prefix composition for `getUserXAttr()`.

State and persistence: API abstracts persisted Linux xattrs and BeeGFS's `user.bgXA.` namespace convention.

Dependencies and integration: Depends on `FhgfsOpsErr` and STL containers. Used by metadata xattr request handlers and ACL/user-xattr storage paths.

Risks and test signals: Callers must not pass already-prefixed names to user helpers. Tests should verify raw vs user helper behavior and exact name translation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/toolkit/XAttrTk.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/tests/TestBuddyMirroring.cpp -->
## sources/distributed-fs/beegfs/meta/tests/TestBuddyMirroring.cpp

Purpose: Provides concurrency smoke tests for metadata entry lock stores used by buddy mirroring and metadata operations.

Important APIs/types/functions: Defines `ParentNameLockTestThread`, `FileIDLockTestThread`, and `DirIDLockTestThread`, each deriving from `PThread`. Tests `BuddyMirroring.simpleEntryLocks` and `BuddyMirroring.rwEntryLocks` start multiple lock/unlock threads against `EntryLockStore`.

Control flow: Each thread logs, obtains a lock, sleeps up to one second, then unlocks. The tests allocate thread objects, start all, join all, and delete them.

State and persistence: No disk persistence. Shared state is `EntryLockStore` plus lock data returned by `lock()`.

Dependencies and integration: Uses BeeGFS `PThread`, `EntryLockStore`, `Random`, logging, and GoogleTest. It exercises parent/name locks, file ID locks, and directory read/write lock paths.

Risks and test signals: The tests are nondeterministic timing smoke tests and contain no explicit assertions beyond absence of deadlock/crash. They may miss fairness, exclusivity, and ordering regressions. Stronger tests would instrument concurrent critical sections and assert mutual exclusion/read-sharing invariants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/tests/TestBuddyMirroring.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/tests/TestConfig.cpp -->
## sources/distributed-fs/beegfs/meta/tests/TestConfig.cpp

Purpose: Tests basic metadata daemon configuration-file handling.

Important APIs/types/functions: `TestConfig::SetUp()` sets dummy config paths. `TearDown()` removes a generated empty config file if present. `missingConfigFile` builds argv with `cfgFile=<missing>` and expects `InvalidConfigException`. `defaultConfigFile` locates the binary directory through `/proc/self/exe`, constructs `dist/etc/beegfs-meta.conf`, and attempts `Config` construction, accepting `ConnAuthFileException`.

Control flow: The missing-file test ensures the dummy path does not exist by appending an integer if needed. The default-config test fails on `readlink` errors or truncation, then constructs argv strings with explicit null terminators.

State and persistence: Uses `/tmp` dummy paths and reads the test-installed default config. It may delete `/tmp/emptyConfigFile.conf.meta` if created.

Dependencies and integration: Depends on metadata `Config`, BeeGFS `StorageTk`, logging, GoogleTest, `ConnAuthFileException`, and `dirname()`.

Risks and test signals: Tests depend on Linux `/proc/self/exe` and copied config layout. The default-config test treats auth-file failures as acceptable because parsing reached that stage. It does not validate individual config fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/tests/TestConfig.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/tests/TestConfig.h -->
## sources/distributed-fs/beegfs/meta/tests/TestConfig.h

Purpose: Declares the GoogleTest fixture and constants for metadata config tests.

Important APIs/types/functions: Defines dummy config paths, relative default config path, app name, and `TestConfig` with `SetUp()`/`TearDown()`, `LogContext`, and path members.

Control flow: Header only declares fixture lifecycle.

State and persistence: Fixture owns path strings used by tests and cleanup.

Dependencies and integration: Includes metadata config, logging, GoogleTest, connection-auth exception, and `libgen.h`.

Risks and test signals: Hard-coded `/tmp` paths can collide across parallel test runs. Tests should use unique temp paths to avoid environmental flakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/tests/TestConfig.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/tests/TestSerialization.cpp -->
## sources/distributed-fs/beegfs/meta/tests/TestSerialization.cpp

Purpose: Exercises serialization round trips for session stores and several metadata/storage value types.

Important APIs/types/functions: `sessionSerialization` serializes a populated `SessionStore`, deserializes into a clone, and compares equality. `initSessionStoreForTests()` builds many `FileInode`, `FileInodeStoreData`, `StatData`, `EntryInfo`, striping patterns, and `SessionFile` instances with edge and random values. Additional tests call `testObjectRoundTrip()` for `DynamicFileAttribs`, `ChunkFileInfo`, `EntryLockDetails`, and `RangeLockDetails`. Helpers fill target vectors and target chunk block maps.

Control flow: Session test first uses an unbuffered `Serializer` to compute size, then serializes to a buffer, deserializes, and compares. Object tests serialize, deserialize, reserialize, and compare byte buffers.

State and persistence: No disk persistence. It constructs heap-owned session/inode structures that become owned by session store/session files according to BeeGFS ownership conventions.

Dependencies and integration: Uses BeeGFS serialization framework, session store, inode/stat data, striping patterns (`Raid0`, `Raid10`, `BuddyMirror`), lock details, random utilities, and GoogleTest.

Risks and test signals: Random values improve range coverage but can make failures less reproducible. The large hand-built fixture tests backward-compatible field ordering indirectly, but does not use golden byte streams. Add fixed seed or golden compatibility vectors for migration-sensitive serialization changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/tests/TestSerialization.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/tests/TestSerialization.h -->
## sources/distributed-fs/beegfs/meta/tests/TestSerialization.h

Purpose: Declares the metadata serialization test fixture and generic round-trip helper.

Important APIs/types/functions: `TestSerialization` derives from `::testing::Test`, declares session-store initialization and random-fill helpers, and defines templated `testObjectRoundTrip(Obj&)`.

Control flow: `testObjectRoundTrip()` computes serialized size, writes to a buffer, deserializes to a default object, verifies consumption, serializes the result again, and asserts byte-for-byte equivalence.

State and persistence: All state is in-memory test data.

Dependencies and integration: Includes `NetMessage.h`, GoogleTest, and `SessionStore.h`. The helper works for BeeGFS types that support default construction and `%` serialization.

Risks and test signals: The helper checks self-consistency, not compatibility with previous releases. Types without meaningful default constructors or equality need separate tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/tests/TestSerialization.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/CMakeLists.txt -->
## sources/distributed-fs/beegfs/storage/CMakeLists.txt

Purpose: Builds and installs the BeeGFS storage server library, daemon executable, tests, and packaged runtime files.

Important APIs/types/functions: Defines static library `storage` with storage app, network message handlers, storage targets, sessions, benchmarker, buddy resyncer, chunk fetcher/balancer, quota, and toolkit sources. Links `beegfs-common`, `dl`, `pthread`, and `blkid`. Builds `beegfs-storage` from `source/program/Main.cpp`. Optionally builds `test-storage`.

Control flow: CMake includes `source`, declares source lists, links targets, copies default test config when tests are enabled, registers `test-storage --compiler`, and installs binary, systemd units, setup script, config, and wrapper script.

State and persistence: Controls installation paths under `usr/sbin`, systemd unit directory, `etc/beegfs`, and `opt/beegfs/sbin`. Test setup copies default config into the build tree.

Dependencies and integration: Integrates storage code with common BeeGFS library, GoogleTest, system libraries, and packaging components.

Risks and test signals: Manual source lists can omit new files and break link/test coverage. The library includes `source/program/Main.cpp` while the executable also compiles it, which should be checked for duplicate-symbol expectations. Test coverage currently only includes storage config tests in this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/app/App.cpp -->
## sources/distributed-fs/beegfs/storage/source/app/App.cpp

Purpose: Implements the BeeGFS storage daemon lifecycle: configuration, target preinitialization and registration, network setup, component startup/shutdown, session persistence, and auxiliary library handling.

Important APIs/types/functions: `run()` constructs `Config` and dispatches `runNormal()`. `runNormal()` performs NUMA binding, storage locking, logging, UUID checks, node/target registration, management-info download, component init/start/join, session restore/delete/store, and shutdown cleanup. Other key methods initialize logging/data/network/storage/components/workers/listeners, register with mgmtd (`waitForMgmtNode()`, `preregisterNode()`, `preregisterTargets()`, `registerAndDownloadMgmtInfo()`), and handle signals/components.

Control flow: Startup locks target dirs before logging, waits for mgmtd heartbeat, obtains node and target numeric IDs, creates `StorageTargets`, downloads mappings/states/pools, applies local resync decisions, starts components, deletes old session files after restore, waits for termination, then stores sessions. Shutdown stops workers, fetchers, syncers, listeners, benchmarker, and closes ZFS.

State and persistence: Persists node numeric ID files, target numeric ID files, target format/session files through `StorageTarget`/`StorageTk`, and session backup files on clean shutdown. It locks PID and target directories, checks filesystem UUIDs if configured, and manages in-memory stores for nodes, targets, states, sessions, quotas, work queues, and resync.

Dependencies and integration: Central integration point for `Config`, `StorageTargets`, `InternodeSyncer`, `DatagramListener`, `StorageStatsCollector`, `StorageBenchOperator`, `BuddyResyncer`, `ChunkFetcher`, `ChunkStore`, `SessionStore`, `NodeStoreServers`, `TargetMapper`, `MirrorBuddyGroupMapper`, `TimerQueue`, RDMA/NIC discovery, and mgmtd messages.

Risks and test signals: Startup ordering is critical: target locks and registration must precede worker traffic. `registerAndDownloadMgmtInfo()` mutates downloaded states with local resync decisions before syncing the state store and sets offline timeouts for primary targets needing resync. Signal handler logs from signal context, which the comment recognizes as potentially unsafe. Tests should cover restart with existing target IDs, first-run target initialization disabled, UUID mismatch, mgmtd retry interruption, per-target vs global queues, session restore/store, and offline-timeout state publication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/app/App.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/app/App.h -->
## sources/distributed-fs/beegfs/storage/source/app/App.h

Purpose: Declares the storage daemon application object and exposes shared runtime services to components.

Important APIs/types/functions: `App` derives from `AbstractApp` and overrides `run()`, `stopComponents()`, component exception/network failure handlers, and message/listener accessors. It owns config, node stores, target stores/mappers, work queues, sessions, stats, listeners, workers, timer queue, chunk/buddy/benchmark components, quota stores, storage pools, and ZFS handle.

Control flow: Header declares private lifecycle phases (`preinitStorage`, `initDataObjects`, `initBasicNetwork`, `initStorage`, `initComponents`, `startComponents`, `joinComponents`, registration helpers) and public getters used throughout storage code. `getWorkQueue(targetID)` falls back to the first queue for unknown targets or global mode.

State and persistence: Owns process-wide mutable state and persistent-resource handles: PID lock, target directory locks, session store, storage targets, and dynamic `libzfs` handle.

Dependencies and integration: Includes most storage component headers and common networking/storage abstractions. `Program::getApp()` users depend on these getters.

Risks and test signals: Wide ownership surface makes destruction order important. `getWorkQueue()` assumes `workQueueMap` is non-empty. Tests should instantiate enough app state to verify queue fallback, ZFS lazy load behavior, and safe stop/delete ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/app/App.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/app/config/Config.cpp -->
## sources/distributed-fs/beegfs/storage/source/app/config/Config.cpp

Purpose: Implements storage daemon configuration defaults, parsing, implicit value derivation, and default config-file lookup.

Important APIs/types/functions: `loadDefaults()` defines storage-specific keys for interfaces, target directories, filesystem UUIDs, worker/listener tuning, IO sizes, resync slave counts, quotas, offline/resync safety thresholds, daemonization, and PID file. `applyConfigMap()` parses typed values, validates `logType`, comma-splits storage directories and UUIDs, enforces `sysTargetOfflineTimeoutSecs >= 30`, and removes handled keys. `initImplicitVals()` derives read-ahead trigger size, interface list, socket buffers, sync-file-range support, and auth hash. `createDefaultCfgFilename()` returns `/etc/beegfs/beegfs-storage.conf` if present.

Control flow: Parsing delegates common settings to `AbstractConfig::applyConfigMap(false)` first, then iterates the remaining map and either consumes known storage keys or throws on unknown keys if enabled.

State and persistence: Holds parsed runtime configuration. It does not persist config; it reads files through the abstract config layer and checks default file existence.

Dependencies and integration: Uses `StringTk`, `UnitTk`, `Path`, POSIX `stat`, and `AbstractConfig`. Values are consumed by `App`, workers, storage targets, benchmarker, resyncer, quota logic, and internode syncer.

Risks and test signals: Comma-splitting storage paths means paths containing commas are unsupported. Distro-dependent `sync_file_range` validation changes behavior at compile time. Tests should cover invalid log type, missing/empty target dirs, UUID list parsing, offline timeout lower bound, human-size parsing, and unknown-key exception behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/app/config/Config.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/app/config/Config.h -->
## sources/distributed-fs/beegfs/storage/source/app/config/Config.h

Purpose: Declares storage daemon configuration fields and accessors.

Important APIs/types/functions: `Config` extends `AbstractConfig` with storage directories, filesystem UUIDs, first-run init policy, stream/worker counts, buffer sizes, NUMA and priority settings, file IO sizes, per-user/per-target queue toggles, cache limits, resync slave counts, aggressive polling, chunk balance queue limit, quota flags, resync/offline timing, daemonization, and PID file.

Control flow: Header declares overrides for defaults, parsing, implicit values, and default filename lookup. Getters expose parsed values; `setQuotaEnableEnforcement()` allows mgmtd quota policy to override local config at runtime.

State and persistence: Stores parsed configuration in memory. Some values control persistent safety behavior such as filesystem UUID checks and target initialization.

Dependencies and integration: Depends on common `AbstractConfig` and compile-time detection of `sync_file_range` support. Consumed broadly by `App`, `InternodeSyncer`, storage IO, benchmarker, and resyncer.

Risks and test signals: Runtime mutation of quota enforcement means config is not immutable after startup. Tests should verify getters reflect parsed values and mgmtd quota override behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/app/config/Config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/DatagramListener.cpp -->
## sources/distributed-fs/beegfs/storage/source/components/DatagramListener.cpp

Purpose: Handles UDP datagrams accepted by the storage daemon and dispatches only message types valid in this context.

Important APIs/types/functions: Constructor forwards network filters, NIC list, ack store, UDP port, and outbound-interface restriction to `AbstractDatagramListener`. `handleIncomingMsg()` resolves sender socket, builds `NetMessage::ResponseContext`, switches on message type, and invokes `processIncoming()` for allowed control/state messages.

Control flow: If no sender socket is found for the source IP, it logs and drops. Allowed messages include ack/dummy, heartbeat, target mapping/capacity/state refresh, remove node, storage pool refresh, and mirror buddy group changes. Disallowed message types are logged as invalid context.

State and persistence: No persistence. Uses inherited send buffer/socket state and ack machinery.

Dependencies and integration: Depends on common datagram listener, IP address handling, net message types, and BeeGFS logging. Created and owned by `App`; used by registration and internode sync operations.

Risks and test signals: Missing a valid UDP control message in the switch would cause runtime rejection. Tests should verify allowed/disallowed message dispatch and behavior when `findSenderSock()` returns null.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/DatagramListener.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/DatagramListener.h -->
## sources/distributed-fs/beegfs/storage/source/components/DatagramListener.h

Purpose: Declares the storage-specific datagram listener.

Important APIs/types/functions: `DatagramListener` derives from `AbstractDatagramListener`, exposes a constructor/destructor, and overrides protected `handleIncomingMsg()`.

Control flow: Header only defines the class shape.

State and persistence: Runtime network listener state is inherited; no persistent fields are added.

Dependencies and integration: Integrates storage `App` networking with BeeGFS common datagram infrastructure.

Risks and test signals: Behavior resides in cpp. Header risk is mainly API drift with `AbstractDatagramListener`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/DatagramListener.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/InternodeSyncer.cpp -->
## sources/distributed-fs/beegfs/storage/source/components/InternodeSyncer.cpp

Purpose: Implements the storage daemon's periodic synchronization with mgmtd and peers: registration, node/mapping/pool/state downloads, target-state publication, capacity publication, quota-list sync, network change detection, and client-session cleanup.

Important APIs/types/functions: `syncLoop()` schedules repeated work. `updateTargetStatesAndBuddyGroups()` downloads states/groups, marks resync jobs when a target was offline, syncs state store, asks `StorageTargets::decideResync()`, publishes local changes, and checks buddy resync needs. `publishTargetCapacities()`, `publishTargetState()`, `publishLocalTargetStateChanges()`, and `publishTargetStateChanges()` send state/capacity messages. Static helpers register nodes/targets, request buddy target states, download nodes/mappings/groups/pools/states, sync client sessions, and download exceeded quota lists.

Control flow: The thread wakes every three seconds and evaluates elapsed timers/force flags. State update publication retries up to ten times because mgmtd state may change between download and compare-and-set. `requestBuddyTargetStates()` is timer-requeued every 30 seconds and updates last-buddy-communication timestamps only when the buddy target reports `GOOD` and local state does not already need resync.

State and persistence: Maintains force flags under mutexes. Updates in-memory node stores, target mapper, mirror buddy mappers, target state store, storage pool store, exceeded quota stores, and session store. Indirectly updates storage target last-buddy-comm state and resync-needed state through `StorageTargets`.

Dependencies and integration: Central bridge to mgmtd via `MessagingTk`, `NodesTk`, heartbeat/map/target-state/capacity/quota messages, `Program::getApp()`, `StorageTargets`, `BuddyResyncer`, `DatagramListener`, and all node stores.

Risks and test signals: In `downloadAllExceededQuotaLists(uint16_t)`, the group inode quota request passes `QuotaDataType_USER` but updates `QuotaDataType_GROUP`, which looks like a copy/paste bug. `downloadAndSyncStoragePools()` returns true even when download fails. Network comparison uses `std::equal` without first checking lengths, which risks incorrect behavior if NIC list sizes differ. Tests should cover mgmtd conflict retries, offline target marking during resync, quota type correctness, storage-pool download failure, NIC add/remove, and state-publication skipping during offline timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/InternodeSyncer.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/InternodeSyncer.h -->
## sources/distributed-fs/beegfs/storage/source/components/InternodeSyncer.h

Purpose: Declares the PThread component responsible for cluster synchronization.

Important APIs/types/functions: Static download/register/session helpers, `publishTargetState()`, `publishLocalTargetStateChanges()`, `requestBuddyTargetStates()`, and force setters for target states, capacities, storage pools, and network checks. Private helpers implement `syncLoop()`, network checks, idle connection cleanup, target updates, capacity publishing, and mgmtd pool refresh.

Control flow: Header exposes force setters that lock a mutex, set a boolean, and are consumed by private get-and-reset methods in the sync loop.

State and persistence: Owns in-memory force flags and log context. It does not directly persist, but coordinates updates to persistent target/buddy/session-related state through other components.

Dependencies and integration: Extends `PThread`, uses BeeGFS node stores, datagram listener, storage target forward declaration, and common logging/component headers. Called by `App`, message handlers, and storage targets.

Risks and test signals: Force flags are boolean, so repeated requests coalesce. Tests should verify each force setter triggers one sync-loop action and is reset safely under concurrency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/InternodeSyncer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/StorageStatsCollector.cpp -->
## sources/distributed-fs/beegfs/storage/source/components/StorageStatsCollector.cpp

Purpose: Collects high-resolution storage worker stats across multiple per-target work queues.

Important APIs/types/functions: Overrides `collectStats()` to iterate `App::getWorkQueueMap()`, call `getAndResetStats()` on each queue, merge raw and incremental stats via `HighResolutionStatsTk`, stamp the current time, and maintain bounded history.

Control flow: It uses the first work queue as the base stats object, then merges remaining queues. The inherited `mutex` protects `statsList`.

State and persistence: Keeps in-memory stats history only; no persistence.

Dependencies and integration: Depends on `Program::getApp()`, `MultiWorkQueueMap`, `HighResolutionStatsTk`, `TimeAbs`, and common `StatsCollector`. Used by `App` as the storage stats component.

Risks and test signals: Assumes `workQueueMap` is non-empty. Tests should cover single global queue, multiple per-target queues, reset semantics, and history length trimming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/StorageStatsCollector.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/StorageStatsCollector.h -->
## sources/distributed-fs/beegfs/storage/source/components/StorageStatsCollector.h

Purpose: Declares the storage-specific stats collector.

Important APIs/types/functions: `StorageStatsCollector(unsigned collectIntervalMS, unsigned historyLength)` invokes the base `StatsCollector` with no single queue, and overrides `collectStats()`.

Control flow: Header contains only construction and override declaration.

State and persistence: Uses base collector state for interval and history.

Dependencies and integration: Inherits `StatsCollector`; `App` creates it with storage collector constants.

Risks and test signals: Behavior depends on cpp implementation. Constructor intentionally passes `NULL` because storage has multiple queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/StorageStatsCollector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/benchmarker/StorageBenchOperator.cpp -->
## sources/distributed-fs/beegfs/storage/source/components/benchmarker/StorageBenchOperator.cpp

Purpose: Thin facade around `StorageBenchSlave` for storage benchmark control.

Important APIs/types/functions: Forwards `initAndStartStorageBench()`, `cleanup()`, `stopBenchmark()`, `getStatusWithResults()`, `shutdownBenchmark()`, and `waitForShutdownBenchmark()` to its `slave` member.

Control flow: No additional logic beyond delegation.

State and persistence: State resides in `StorageBenchSlave`, including benchmark files and runtime status.

Dependencies and integration: Used by `App` and storage benchmark control message handlers to avoid exposing the slave directly.

Risks and test signals: Facade has little risk; tests should focus on slave behavior and verify the operator preserves return values/status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/benchmarker/StorageBenchOperator.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/benchmarker/StorageBenchOperator.h -->
## sources/distributed-fs/beegfs/storage/source/components/benchmarker/StorageBenchOperator.h

Purpose: Declares the storage benchmark frontend object.

Important APIs/types/functions: Owns a `StorageBenchSlave` and exposes benchmark lifecycle/control methods plus inline `getStatus()`, `getType()`, and `getLastRunErrorCode()`.

Control flow: Header inlines read-only delegation.

State and persistence: Encapsulates the slave's in-memory status and disk benchmark file operations.

Dependencies and integration: Includes `StorageBenchSlave.h`; owned by `App`.

Risks and test signals: Copying this object would be unsafe because it owns a thread-like slave, but copying is not explicitly disabled. Tests should avoid accidental copies and validate lifecycle shutdown through `App`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/benchmarker/StorageBenchOperator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/benchmarker/StorageBenchSlave.cpp -->
## sources/distributed-fs/beegfs/storage/source/components/benchmarker/StorageBenchSlave.cpp

Purpose: Implements storage benchmark execution by creating per-target files, dispatching read/write work to normal worker queues, tracking worker completions via a pipe, and reporting throughput.

Important APIs/types/functions: `initAndStartStorageBench()` validates inactive status, initializes, starts the thread, and transitions status. `initStorageBench()` stores parameters, initializes thread data/transfer buffer, validates read data or creates write dirs. `run()` opens files, enqueues `StorageBenchWork`, reads worker responses, handles abort/errors, closes files, frees buffers, and sets final status. Other helpers create/check benchmark dirs, open/close files, compute package sizes and throughput, cleanup files, stop/shutdown/wait, and return status/results.

Control flow: For each target/thread pair, `initThreadData()` creates a virtual thread record. `run()` enqueues one work item per record, then each worker response causes the next package to be queued until `size` is reached. Stop/error paths set `STOPPING`, collect outstanding responses while workers run, then map to `ERROR` or `STOPPED`.

State and persistence: Maintains benchmark status, type, block size, total size, thread count, target ID list, per-thread file descriptors/progress/time, aligned random transfer buffer, pipe, and start time. Persists benchmark data under `<targetPath>/benchmark/<targetThreadID>`; `cleanup()` deletes regular files in that directory.

Dependencies and integration: Uses `Program::getApp()` for targets, workers, and work queues; `StorageBenchWork` for actual IO; `StorageTk` and POSIX file APIs; BeeGFS benchmark enums/errors/status types.

Risks and test signals: `targetIDs` is overwritten with `new auto(*targetIDs)` without deleting any previous list, so repeated initializations after finished runs may leak. `threadData[threadID]` in `getNextPackageSize()` assumes valid IDs. O_DIRECT requires block-aligned size and offsets; only buffer alignment is enforced here. Tests should cover repeated benchmark runs, stop during active IO, worker error response, read-before-write validation, cleanup with non-regular files, unknown target handling, and O_DIRECT parameter validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/benchmarker/StorageBenchSlave.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/benchmarker/StorageBenchSlave.h -->
## sources/distributed-fs/beegfs/storage/source/components/benchmarker/StorageBenchSlave.h

Purpose: Declares the benchmark worker thread and per-virtual-thread data structures.

Important APIs/types/functions: `StorageBenchThreadData` tracks target, virtual thread ID, engaged bytes, file descriptor, and elapsed time. `TransferDataDeleter` frees aligned buffers. `StorageBenchSlave` derives from `PThread` and exposes benchmark start, cleanup, stop, status/result, shutdown, and wait methods. Private helpers implement initialization, IO file handling, package sizing, and result aggregation.

Control flow: Header defines `setStatus()` to update status under `statusMutex` and broadcast `statusChangeCond`. Inline getters expose last error, status, type, and target IDs.

State and persistence: Owns pipe, status mutex/condition, status fields, target list pointer, thread-data map, transfer buffer, and timing. Disk persistence occurs in cpp through benchmark files.

Dependencies and integration: Uses BeeGFS benchmark common definitions, `PThread`, `Condition`, `Pipe`, `TimeFine`, and logging. Driven by `StorageBenchOperator`.

Risks and test signals: Destructor deletes `targetIDs` but lifecycle reuse must manage previous allocations. Status access is partly locked (`getType()` is not), so concurrent reads during init may race. Tests should include thread-safety and lifecycle reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/benchmarker/StorageBenchSlave.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncJob.cpp -->
## sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncJob.cpp

Purpose: Implements a storage-target buddy resync job. It coordinates gather slaves, file sync slaves, directory sync slaves, target-state transitions, and final buddy notification.

Important APIs/types/functions: Constructor sizes slave vectors from config. `run()` is the main orchestration. `abort()` signals abort and disables idle-only termination. `startGatherSlaves()`, `startSyncSlaves()`, `joinGatherSlaves()`, `joinSyncSlaves()` manage worker threads. `getJobStats()` aggregates counters. `informBuddy()` sends final consistency state to the buddy. `checkTopLevelDir()` and `walkDirs()` discover sync candidates by mtime.

Control flow: `run()` guards against double running, marks target resync in progress, flushes all storage workers through `IncSyncedCounterWork`, notifies buddy with `StorageResyncStartedMsg`, starts slaves, computes last-buddy-comm threshold, scans top-level and shallow chunk dirs, queues deeper dirs to gather slaves, drains gather and sync slaves, evaluates abort/errors/offline flags, sets final job status, updates target last-buddy-comm/buddy-needs-resync state, informs buddy, clears resync-in-progress, and records end time.

State and persistence: Owns status, start/end times, sync candidate store, gather queue, slave pointers, discovered/matched counters, abort flag, and target-offline flag. It reads persistent target path/chunk mtime and target last-buddy-comm state; it may clear last-buddy-comm override and set buddy-needs-resync through `StorageTarget`.

Dependencies and integration: Depends on `App`, `StorageTargets`, `MirrorBuddyGroupMapper`, `TargetMapper`, `NodeStoreServers`, storage workers, resync slave classes, `MessagingTk`, `StorageResyncStartedMsg`, and target consistency messages.

Risks and test signals: `run()` dereferences `buddyNode` for `MessagingTk::requestResponse(*buddyNode, ...)` without a null check after `referenceNode()`. Failure cleanup waits on slave `isRunning` even if some start paths failed. Directory scan is mtime-based and applies a safety threshold; clock/filesystem timestamp issues can affect completeness. Tests should cover unknown buddy node, failed buddy notification, slave start failure, abort during walk, target offline during finalization, mtime threshold correctness, and status/stat aggregation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncJob.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncJob.h -->
## sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncJob.h

Purpose: Declares the storage buddy resync job thread and its coordination state.

Important APIs/types/functions: `BuddyResyncJob` derives from `PThread`, exposes `run()`, `abort()`, `getJobStats()`, `getTargetID()`, `getStatus()`, `isRunning()`, and `setTargetOffline()`. Private methods walk directories, start/join slaves, set status, and inform the buddy. Defines `GATHERSLAVEQUEUE_MAXSIZE` and `BuddyResyncJobMap`.

Control flow: Header inline methods lock status for reads and writes; `setTargetOffline()` atomically marks offline observation for the running job.

State and persistence: Holds target ID, status mutex/status, timing, sync candidate structures, slave vectors, counters, abort flag, and target-offline flag. Persistence is mediated by cpp through storage target state.

Dependencies and integration: Includes resync gather/file/dir slave headers and buddy resync stats type. Owned by `BuddyResyncer` and observed by debug/status message paths.

Risks and test signals: `GenericDebugMsgEx` friendship exposes internals for debugging. Tests should verify status locking and `setTargetOffline()` influence final job state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncJob.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncer.cpp -->
## sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncer.cpp

Purpose: Implements the frontend that starts and cleans up per-target buddy resync jobs.

Important APIs/types/functions: Destructor aborts and joins running jobs before deleting all jobs. `startResync(uint16_t)` obtains or creates a `BuddyResyncJob`, rejects if the existing job is running, otherwise starts it.

Control flow: `startResync()` calls `addResyncJob()`, checks `isNewJob` and `isRunning()`, starts the job thread, and returns `SUCCESS` or `INUSE`.

State and persistence: Owns an in-memory map of target ID to job. Resync job objects handle persistent target state.

Dependencies and integration: Uses `BuddyResyncJob` and is owned by `App`. Called by internode sync logic when mgmtd marks a buddy target `NEEDS_RESYNC`.

Risks and test signals: Completed jobs remain in the map and may be restarted; this depends on `BuddyResyncJob::run()` supporting repeated runs. Tests should cover repeated start after success/failure, destructor with running jobs, and concurrent `startResync()` calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncer.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncer.h -->
## sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncer.h

Purpose: Declares the storage buddy resync controller.

Important APIs/types/functions: `startResync(uint16_t)` starts a job for a target. `getResyncJob(uint16_t)` returns an existing job under lock. Private `addResyncJob()` creates or returns a job while reporting whether it is new.

Control flow: Map operations are protected by `resyncJobMapMutex`. The class itself is not a thread component; jobs are thread components.

State and persistence: Maintains only in-memory job map. Persistent resync effects are delegated to `BuddyResyncJob` and `StorageTarget`.

Dependencies and integration: Included by `App` and `InternodeSyncer`; depends on `BuddyResyncJob`.

Risks and test signals: Raw pointers require careful destructor cleanup and make ownership non-obvious. Tests should cover map locking under concurrent job lookup/start and no duplicate running jobs per target.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/components/buddyresyncer/BuddyResyncer.h -->
