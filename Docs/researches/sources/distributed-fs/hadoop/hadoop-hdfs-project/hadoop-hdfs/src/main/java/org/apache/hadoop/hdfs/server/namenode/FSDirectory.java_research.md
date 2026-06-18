# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirectory.java

## Purpose

`FSDirectory.java` is the NameNode's in-memory namespace directory manager. Its class comment draws the key boundary: `FSDirectory` keeps namespace state in memory, while `FSNamesystem` persists operations through the edit log. The file owns the root `INodeDirectory`, inode ID allocation, the `INodeMap`, reserved path resolution, quota accounting, filesystem limit checks, access-control integration, encryption-zone indexing, storage-policy satisfier hooks, and helper APIs used by operation-specific classes such as `FSDirWriteFileOp`, `FSDirDeleteOp`, `FSDirRenameOp`, and `FSDirAttrOp`.

The source was read as a complete 2104-line file for this report.

## Important APIs, Types, and Functions

Core type/state: `FSDirectory implements Closeable`; `DirOp` controls path resolution behavior for read/write/create and symlink-following variants; `rootDir`, `namesystem`, `inodeMap`, `inodeId`, `editLog`, `ezManager`, `nameCache`, `protectedDirectories`, permission/ACL/xattr/quota configuration flags, and reserved path constants for `/.reserved`, `/.reserved/raw`, and `/.reserved/.inodes`.

Initialization and configuration APIs: `FSDirectory(FSNamesystem, Configuration)` builds the root inode, reads NameNode config, initializes `INodeMap`, permissions, ACL/xattr limits, list/content-summary limits, protected directories, access-time precision, quota-by-storage-type support, name cache, edit-log pointer, encryption-zone manager, quota init threads, and external attribute-provider bypass users. `createReservedStatuses`, `parseProtectedDirectories`, `setProtectedDirectories`, `setMaxDirItems`, and feature getters expose this configuration.

Path and inode APIs: `resolvePath`, `unprotectedResolvePath`, static `resolvePath`, `getINodesInPath`, `getINode`, `getINode4Write`, `resolveComponents`, `resolveDotInodesPath`, `constructRemainingPath`, `getINode4DotSnapshot`, and `resolveLastINode`. These are central to all namespace operations.

Mutation and quota APIs: `addINode`, `addLastINode`, `addLastINodeNoQuotaCheck`, `removeLastINode`, `updateCountForQuota`, `updateSpaceConsumed`, the overloaded `updateCount` methods, `updateCountForDelete`, `unprotectedUpdateCount`, `verifyQuota`, `updateSpaceForCompleteBlock`, and `getStorageTypeDeltas`.

Validation/security APIs: `verifyINodeName`, `verifyMaxComponentLength`, `verifyMaxDirItems`, `isValidToCreate`, `verifyParentDir`, `getPermissionChecker`, `checkOwner`, `checkPathAccess`, `checkParentAccess`, `checkAncestorAccess`, `checkTraverse`, `checkPermission`, `checkUnreadableBySuperuser`, and `getAttributes`.

Indexing and lifecycle APIs: `addToInodeMap`, `removeFromInodeMap`, `getInode(long)`, `reset`, `cacheName`, `shutdown`, `allocateNewInodeId`, `getLastInodeId`, `resetLastInodeId`, and `resetLastInodeIdWithoutChecking`.

## Control Flow

Construction initializes a root directory with default quota and snapshottable feature, loads configuration gates, records the owning `FSNamesystem`, and grabs the edit-log instance from it. `readLock`, `writeLock`, and matching unlock methods are now assertions over `FSNamesystem`'s FS lock, so callers are expected to hold the appropriate `FSNamesystem` lock before mutating or reading namespace state.

Client-visible path resolution flows through `resolvePath(pc, src, dirOp)`: create operations first validate path syntax; components are converted from the string path; reserved raw or inode paths are rewritten by `resolveComponents`; `INodesInPath.resolve` builds the inode chain; raw write/create operations require superuser privilege; `checkTraverse` enforces ancestry, symlink, snapshot, and optional permission checks according to `DirOp`.

Internal replay and helper paths often use `getINodesInPath` or `unprotectedResolvePath`, which deliberately skip reserved-path expansion or permission checks as documented. This split matters because edit-log replay must rebuild exact namespace state while normal RPC paths must enforce user permissions and snapshot read-only behavior.

Adding an inode goes through name caching, filesystem limit checks, reserved-name checks, quota calculation, `updateCount`, `parent.addChild`, default ACL inheritance, and `addToInodeMap`. If `parent.addChild` fails, quota deltas are rolled back. Removing a last inode delegates child removal to the parent and then handles snapshot/reference semantics with `INodeReference.tryRemoveReference`.

Quota initialization is parallelized by `InitQuotaTask` over the directory tree. Runtime quota changes build `QuotaCounts`, optionally verify each quota-bearing ancestor, then update cached counts. Deletion and block-completion paths adjust namespace, storage-space, and storage-type quotas to reflect snapshots, erasure coding, and replication.

## State and Persistence Behavior

`FSDirectory` itself is memory-resident. Persistent durability is indirect: operation classes mutate this structure under `FSNamesystem` locks and separately log durable edits through `FSEditLog`. During image/edit loading, `skipQuotaCheck`, `namesystem.isImageLoaded()`, and `resetLastInodeId` alter behavior so old or partially loaded persisted state can be reconstructed before runtime checks become strict.

The persistent identity state is the inode ID counter. `allocateNewInodeId` advances it for new namespace objects, while loader code calls `resetLastInodeId` as edit-log inode IDs are replayed. The `INodeMap` is the runtime lookup index for inode IDs and supports reserved `/.reserved/.inodes/<id>` paths.

Encryption-zone and storage-policy satisfier state is discovered from inode xattrs when inodes enter the map. `addEncryptionZone` parses the crypto xattr protocol buffer and registers the zone and optional re-encryption status with `EncryptionZoneManager`; `removeFromInodeMap` removes associated encryption-zone entries. This means xattr changes and inode-map changes must stay coordinated.

Name caching is an in-memory heap optimization for file local-name byte arrays. It is initialized after load with `markNameCacheInitialized` and reset on namespace reset/shutdown.

## Dependencies and Integration Points

Primary integration is with `FSNamesystem`, which owns locking, persistence orchestration, block management, lease management, audit state, and external invocation context. `FSEditLog` is retained for operation classes that need to log after directory mutation.

Namespace model dependencies include `INode`, `INodeDirectory`, `INodeFile`, `INodeMap`, `INodesInPath`, `DirectoryWithQuotaFeature`, `QuotaCounts`, snapshot classes, ACL and xattr storage, and HDFS protocol status/exception classes.

Storage dependencies include `BlockManager`, `BlockStoragePolicySuite`, `BlockStoragePolicy`, `BlockInfo`, `BlockInfoStriped`, storage type counters, erasure-coding policy lookup, and storage-policy satisfier manager.

Security dependencies include `FSPermissionChecker`, `INodeAttributeProvider`, `UserGroupInformation`, `FsAction`, ACL support, superuser checks, `SECURITY_XATTR_UNREADABLE_BY_SUPERUSER`, and external authorization provider compatibility detection.

Reserved path handling integrates with HDFS semantics for `/.reserved/raw` encryption-zone raw access and `/.reserved/.inodes` inode-ID lookup. Audit status generation integrates with `FileStatus`, symlink targets, file size/replication, and snapshot attributes.

## Risks and Edge Cases

Locking is assertion-based in this class; real exclusion depends on correct `FSNamesystem` lock discipline by every caller. Missing a write lock can corrupt inode trees, quota caches, or inode maps.

Reserved path rewriting is subtle. `/.reserved/raw/.reserved` intentionally does not strip the raw prefix, `/.reserved/.inodes/<id>/..` supports NFS parent lookup, and invalid inode IDs throw `FileNotFoundException`. Changes here risk security bypasses or broken compatibility.

Quota behavior differs during startup/replay versus runtime. Several filesystem limit violations log instead of throw before image load completes. Bugs in `skipQuotaCheck`, rollback after failed add, or snapshot-aware delete accounting can leave quota caches inconsistent.

`addToInodeMap` has side effects beyond indexing: it registers encryption zones and storage-policy satisfier xattrs. Bypassing it, or removing inodes without `removeFromInodeMap`, can leak security/storage state.

Permission checks intentionally treat superusers specially by calling external enforcers for audit and by respecting `unreadableBySuperuser` xattrs. Any shortcut around `resolvePath`/`checkPermission` can miss external provider policy or audit behavior.

## Test Signals

Useful coverage includes path-resolution tests for normal paths, symlinks, snapshots, `/.reserved/raw`, `/.reserved/.inodes`, invalid IDs, and NFS-style `..`; lock/assertion tests around callers that mutate namespace; quota initialization and delta tests for create/delete/rename/snapshot/replication/erasure-coded files; ACL default inheritance tests with masked/unmasked create modes; xattr/encryption-zone registration and removal tests; protected-directory parsing and delete behavior; permission and external attribute-provider tests, including bypass users, superuser audit, and unreadable-by-superuser denial; and edit-log replay tests that confirm startup leniency does not persist after `isImageLoaded`.
