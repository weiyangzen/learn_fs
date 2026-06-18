# subset-b-007496 research

Grouped research for HDFS Namenode `FSDir*Op` helpers. Each section preserves the source path and is intended to be split into the source-tree-aligned per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirAttrOp.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirAttrOp.java

## Purpose
`FSDirAttrOp` centralizes Namenode namespace attribute mutations for permissions, owners, timestamps, replication, quotas, storage policies, and preferred block size reads. It is a static helper around `FSDirectory`, `FSPermissionChecker`, and `BlockManager`, separating checked client-facing operations from `unprotected*` edit-log replay or already-locked mutation routines.

## Important APIs, Types, And Functions
- Public/static operation entry points include `setPermission`, `setOwner`, `setTimes`, `setReplication`, `setStoragePolicy`, `unsetStoragePolicy`, `getStoragePolicies`, `getStoragePolicy`, `getPreferredBlockSize`, and `setQuota`.
- Replay/internal helpers include `unprotectedSetPermission`, `unprotectedSetOwner`, `unprotectedSetTimes`, `unprotectedSetQuota`, `unprotectedSetReplication`, and `unprotectedSetStoragePolicy`.
- The implementation works with `INodesInPath`, `INode`, `INodeFile`, `INodeDirectory`, `QuotaCounts`, `StorageType`, `BlockStoragePolicy`, `BlockInfo`, and directory XAttrs for inherited storage policy state.

## Control Flow
Checked mutators reject reserved paths when relevant, resolve the path with a write `DirOp`, run owner/write/superuser checks, mutate while holding `FSDirectory`'s write lock, then log the corresponding edit record if state changed. `setOwner` has nuanced owner/group authorization: non-superusers may not change owner and may only set groups they belong to. `setReplication` verifies the target replication with `BlockManager`, skips non-files and striped files, updates quotas before increasing and after decreasing replication, and updates each block's replication in the block manager. Storage policy changes validate the policy ID/name, reject copy-on-create policies on existing files, and store directory policies through `BlockStoragePolicySuite` XAttrs.

## State And Persistence Behavior
Persistent state changes are inode permission bits, user/group fields, mtime/atime, directory quota features, file replication, block manager replication metadata, and storage policy IDs or storage-policy XAttrs. Edit-log records are emitted with `logSetPermissions`, `logSetOwner`, `logTimes`, `logSetReplication`, `logSetStoragePolicy`, `logSetQuota`, and `logSetQuotaByStorageType`. Snapshot-aware mutation uses `iip.getLatestSnapshotId()` and `recordModification` where required.

## Dependencies And Integration Points
This file integrates with `FSDirectory` locking/path resolution/quota accounting, `BlockManager` replication and storage policy suites, `FSDirXAttrOp` for directory storage policy XAttr replacement/removal, `SnapshotManager` access-time capture policy, and `FSEditLog` persistence. It is called by higher-level `FSNamesystem` RPC handlers and edit-log loading code.

## Risks And Edge Cases
Important risks are quota deltas during replication changes, copy-on-create storage policies being incorrectly changed after creation, access-time precision skipping needed updates, storage-type quota feature gating, and mutation of snapshot-protected paths. Replication explicitly returns `null` for striped files, so callers must not interpret that as a successful EC replication update.

## Test Signals
Useful tests cover chmod/chown edit logging only on real changes, non-superuser owner/group denial, timestamp precision behavior, quota reset/don't-set semantics including root quota reset, storage-type quota disabled errors, setting/unsetting directory storage policies through XAttrs, copy-on-create policy rejection, and replication quota/block-manager updates for increasing/decreasing replication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirAttrOp.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirConcatOp.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirConcatOp.java

## Purpose
`FSDirConcatOp` implements HDFS file concat: append the blocks of multiple source files to a target file and remove the sources from the namespace. It enforces the concat contract that sources and target live in the same directory and are compatible in snapshots, construction state, block size, encryption, and erasure coding.

## Important APIs, Types, And Functions
- `concat` is the checked entry point and returns audit `FileStatus`.
- `validatePath`, `verifyTargetFile`, `verifySrcFiles`, `computeQuotaDeltas`, and `verifyQuota` implement preconditions.
- `unprotectedConcat` performs the locked namespace/block mutation.
- Key types are `INodeFile`, `INodeDirectory`, `INodesInPath`, `QuotaCounts`, `BlockStoragePolicy`, `StorageType`, and `FSDirEncryptionZoneOp`.

## Control Flow
The entry point rejects reserved concat paths, resolves the target, checks write permission on the target, verifies the target is a closed file outside an encryption zone, validates each source with read permission and parent write permission, rejects duplicate sources, sources in snapshots or multi-reference snapshot state, under-construction/empty sources, larger preferred block sizes, and EC policy mismatch. It then takes the directory write lock and calls `unprotectedConcat`. That routine computes namespace/storage quota deltas, records target modification for snapshots, concatenates source blocks into the target, clears and removes source files from their parent and inode map, updates target and parent modification time, and applies quota deltas.

## State And Persistence Behavior
The operation persists through `logConcat(target, srcs, timestamp, logRetryCache)` after in-memory mutation. Source inodes are removed, source blocks are transferred/cleared, target block list and mtime change, parent mtime changes, namespace quota drops by source count, and storage/type quota may change if source replication differs from target replication.

## Dependencies And Integration Points
It depends on `FSDirectory` for path resolution, quota verification, inode-map removal, and locks; `INodeFile.concatBlocks` and `BlockManager` for block ownership; `FSDirEncryptionZoneOp` to disallow encrypted concat; snapshot reference classes to reject unsafe sources; and edit-log replay via `unprotectedConcat`.

## Risks And Edge Cases
Quota accounting must reflect replication and storage type transitions, not only namespace removal. Snapshot references are especially sensitive because source files are deleted while their blocks move. Encryption zones are disallowed entirely, and EC policy mismatches are rejected to avoid mixed block layouts in one file.

## Test Signals
Tests should cover duplicate sources, target equal to source, cross-directory rejection, under-construction/empty sources, snapshot-held sources, encryption-zone target rejection, EC policy mismatch, quota delta behavior when replication differs, edit-log replay, and successful concat preserving block order while removing source inodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirConcatOp.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirDeleteOp.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirDeleteOp.java

## Purpose
`FSDirDeleteOp` owns namespace deletion for files and directories, including permission checks, recursive/protected-descendant checks, snapshot constraints, block/inode reclamation, lease cleanup, quota updates, metrics, and edit-log replay.

## Important APIs, Types, And Functions
- Client-facing `delete(FSNamesystem, FSPermissionChecker, String, boolean, boolean)` validates path and permissions.
- Internal `delete(FSDirectory, INodesInPath, BlocksMapUpdateInfo, List<INode>, List<Long>, long)` unlinks and collects reclaim work.
- `deleteInternal` coordinates edit logging, metrics, and lease/inode cleanup under the FSNamesystem write lock.
- `deleteForEditLog` is replay-only.
- `unprotectedDelete` performs the direct inode tree mutation.

## Control Flow
The checked entry point rejects exact reserved names, resolves with `WRITE_LINK`, checks delete permissions, rejects non-recursive deletion of non-empty directories, and checks protected descendants. `deleteInternal` creates block/inode/UC-file collectors, calls the lower-level delete, logs `logDelete`, increments deletion metrics, and removes leases/inodes. The locked delete path rejects missing paths and root deletion, checks snapshottable descendants through `FSDirSnapshotOp`, builds an `INode.ReclaimContext`, removes the last inode, updates parent mtime, and either destroys blocks immediately or cleans the subtree against the latest snapshot.

## State And Persistence Behavior
Deletion changes the namespace tree, inode map, parent modification time, quota counts, block replication metadata, safemode block totals, leases, and snapshottable directory registry. Client deletes persist through `logDelete`; replay deletes call `deleteForEditLog` and directly remove blocks through the block manager.

## Dependencies And Integration Points
The operation is tightly integrated with `FSNamesystem` global write locking, `FSDirectory` write locking and quota updates, `FSDirSnapshotOp` snapshot safety checks, `LeaseManager`, `BlockManager`, `NameNode` metrics, and `DFSUtil.checkProtectedDescendants`.

## Risks And Edge Cases
Root and missing paths must be non-mutating. Snapshot-held files require `cleanSubtree` rather than unconditional destruction. Large directory deletion relies on collected reclaim state, so callers must drain blocks and leases in the right lock context. Protected descendants and non-recursive directories prevent accidental destructive deletes.

## Test Signals
Tests should verify root/missing delete behavior, non-empty directory recursive flag handling, protected descendant rejection, snapshot-root rejection and snapshottable-dir cleanup, lease removal for under-construction files, quota updates, block collection/safemode total updates on replay, and edit-log retry-cache logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirDeleteOp.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirEncryptionZoneOp.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirEncryptionZoneOp.java

## Purpose
`FSDirEncryptionZoneOp` implements encryption-zone management and per-file encryption metadata handling. It creates/list zones, resolves zone information, maintains re-encryption progress XAttrs, saves file EDEKs, warms KMS EDEK caches, and coordinates file creation with key generation outside Namenode locks.

## Important APIs, Types, And Functions
- Zone APIs: `ensureKeyIsInitialized`, `createEncryptionZone`, `getEZForPath`, `listEncryptionZones`, `listReencryptionStatus`, `getCurrentKeyVersion`, and `getKeyNameForZone`.
- Re-encryption APIs: `reencryptEncryptionZone`, `cancelReencryptEncryptionZone`, `updateReencryptionSubmitted`, `updateReencryptionProgress`, `updateReencryptionFinish`, and `generateNewXAttrForReencryptionFinish`.
- File encryption APIs: `setFileEncryptionInfo`, `getFileEncryptionInfo`, `isInAnEZ`, `getEncryptionKeyInfo`, and `saveFileXAttrsForBatch`.
- Helper types include `EncryptionZone`, `ZoneReencryptionStatus`, `FileEncryptionInfo`, `KeyProviderCryptoExtension`, `EncryptedKeyVersion`, protobuf zone/file encryption records, and `EncryptionKeyInfo`.

## Control Flow
Zone creation converts cipher/protocol information, resolves the target under the write lock, asks `EncryptionZoneManager` to create the zone XAttr, then logs it as a set-XAttrs edit. File creation first checks whether the path is in a zone, chooses a supported crypto protocol, releases the FS write lock, generates an EDEK as the login user through the configured key provider, then reacquires the lock and requires the caller to re-resolve/revalidate before use. Re-encryption status updates parse the zone XAttr protobuf, build a replacement protobuf with submitted/progress/finish fields, and apply it via `FSDirXAttrOp.unprotectedSetXAttrs`. File encryption info reads the per-file XAttr plus zone cipher/protocol/key name and returns a consolidated `FileEncryptionInfo`.

## State And Persistence Behavior
Encryption-zone and re-encryption state is persisted as crypto XAttrs and mirrored in `EncryptionZoneManager` in-memory maps. Per-file encryption info is stored as `CRYPTO_XATTR_FILE_ENCRYPTION_INFO`. Re-encryption batch saves emit `logSetXAttrs` for updated file XAttrs. Metrics record EDEK generation and warm-up latency. Some methods intentionally require callers to log/sync after XAttr mutation.

## Dependencies And Integration Points
The file integrates with KMS/key provider APIs, `SecurityUtil.doAsLoginUser`, `EncryptionZoneManager`, `ReencryptionUpdater`, `FSDirXAttrOp`, `PBHelperClient`, `FSNamesystem` lock modes, `NameNode` metrics/logging, and file creation in `FSDirWriteFileOp`.

## Risks And Edge Cases
Key generation must not run under FS read/write locks. Zone changes between lock release and reacquire are handled by retry exceptions and key-name revalidation. Raw paths intentionally suppress encryption info. Missing or unparsable XAttrs degrade to warnings or IOExceptions depending on context. Re-encryption XAttr updates must preserve existing zone cipher/protocol/key fields while changing only re-encryption state.

## Test Signals
Tests should cover missing provider/key errors, EDEK generation outside locks, zone/key mismatch retry during file creation, raw path returning no encryption info, malformed per-file/zone XAttr parsing, re-encryption submitted/progress/finish XAttr replacements, list batching, cache warm-up retry behavior, and edit-log replay rebuilding EZ state from XAttrs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirEncryptionZoneOp.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirErasureCodingOp.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirErasureCodingOp.java

## Purpose
`FSDirErasureCodingOp` manages erasure-coding policy lookup, directory policy XAttr mutation, system policy add/remove/enable/disable, and effective policy resolution for paths and files.

## Important APIs, Types, And Functions
- Policy lookup: `getEnabledErasureCodingPolicyByName`, `getErasureCodingPolicyByName`, `getErasureCodingPolicy`, `unprotectedGetErasureCodingPolicy`, `getErasureCodingPolicies`, and `getErasureCodingCodecs`.
- Policy mutation: `setErasureCodingPolicy`, `unsetErasureCodingPolicy`, `addErasureCodingPolicy`, `removeErasureCodingPolicy`, `enableErasureCodingPolicy`, and `disableErasureCodingPolicy`.
- Internal helpers serialize policy names into `XATTR_ERASURECODING_POLICY` using `WritableUtils` and apply/remove XAttrs through `FSDirXAttrOp`.

## Control Flow
Setting a policy requires the FS write lock, validates the named policy is enabled, resolves the path with `WRITE_LINK`, checks write access, requires the target inode to be a directory, serializes the policy name into an XAttr, and creates or replaces the XAttr depending on whether one exists. Unset follows the same path and removes only a directly set directory EC XAttr, throwing `NoECPolicySetException` when absent. Effective lookup walks from the target toward root, returning a file's encoded EC policy ID first, then directory XAttrs, and stopping at symlinks.

## State And Persistence Behavior
Directory EC policies persist as XAttrs, while system-wide policy state is managed by `ErasureCodingPolicyManager` and logged with dedicated edit-log records. Set/unset directory operations log `logSetXAttrs` or `logRemoveXAttrs`. Effective file layout is also stored on `INodeFile` as an EC policy ID used by write/block code.

## Dependencies And Integration Points
The operation depends on `FSNamesystem` read/write lock assertions, `FSDirectory` path checks, `ErasureCodingPolicyManager`, `FSDirXAttrOp`, `CodecRegistry`, `WritableUtils`, and `XAttrHelper`. It feeds `FSDirWriteFileOp` for striped file creation and `FSDirStatAndListingOp` for status/block location metadata.

## Risks And Edge Cases
Only enabled policies can be set through the user API, but valid disabled/removed policies matter for admin state transitions and replay. Symlink traversal is not supported for inherited EC policy resolution. Returning `null` for REPLICATION policy is intentional in the external `getErasureCodingPolicy(String)` path. XAttr serialization must remain compatible with edit logs.

## Test Signals
Tests should cover invalid/disabled policy errors, set/replace on directory, unset absent policy, file target rejection, symlink inheritance stop, inherited parent policy lookup, file policy ID lookup, REPLICATION suppression in API results, admin add/remove/enable/disable edit logging, and codec registry exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirErasureCodingOp.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirMkdirOp.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirMkdirOp.java

## Purpose
`FSDirMkdirOp` creates HDFS directories for `mkdirs`, implicit parent creation used by file and symlink creation, and edit-log replay of directory creation.

## Important APIs, Types, And Functions
- `mkdirs` is the checked user operation.
- `createAncestorDirectories` and `createParentDirectories` create missing ancestors.
- `mkdirForEditLog` replays mkdir edits.
- `createSingleDirectory`, `addImplicitUwx`, and `unprotectedMkdir` allocate and insert `INodeDirectory` instances.

## Control Flow
`mkdirs` resolves with `DirOp.CREATE`, rejects an existing file at the target, checks ancestor write access, optionally verifies parent existence, checks FS object limits, creates missing parents with implicit user write/execute bits, creates the final directory, logs each created directory, increments file-created metrics, and returns audit status. Ancestor creation finds existing prefix inodes, computes how many components are missing, and creates each missing component under the write lock.

## State And Persistence Behavior
The operation allocates inode IDs, inserts `INodeDirectory` objects into the namespace, optionally applies ACLs on replay, updates quotas through `FSDirectory.addLastINode`, and logs each created directory with `logMkDir`. Directory creation increments the files-created metric to balance delete metrics.

## Dependencies And Integration Points
It integrates with `FSDirectory` path resolution, object-limit checks through `FSNamesystem`, ACL storage for replay, `Snapshot.CURRENT_STATE_ID`, and callers such as `FSDirWriteFileOp` and `FSDirSymlinkOp` that need implicit ancestors.

## Risks And Edge Cases
The implicit `u+wx` behavior is required so users can traverse auto-created ancestors. `createParent=false` must reject missing parents. Existing target directories are treated as success for `mkdirs`, while existing target files fail. Replay assumes parent exists and must preserve inode IDs, permissions, ACLs, and timestamps.

## Test Signals
Tests should cover existing file rejection, existing directory idempotence, parent creation on/off, implicit ancestor permissions with masked/unmasked modes, object-limit failure, ACL replay, edit-log inode ID preservation, and metrics/edit-log records per created directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirMkdirOp.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirRenameOp.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirRenameOp.java

## Purpose
`FSDirRenameOp` implements old and POSIX-style HDFS rename semantics, including overwrite behavior, trash-specific permission checks, quota and FS-limit validation, encryption-zone move validity, snapshot/reference handling, block cleanup for overwritten destinations, leases, metrics, and edit-log replay.

## Important APIs, Types, And Functions
- Entry points are deprecated `renameToInt(FSDirectory, ..., String, String, boolean)`, POSIX `renameToInt(..., Options.Rename...)`, and `renameTo`.
- Replay paths are deprecated `renameForEditLog(String,String,long)` and current `renameForEditLog(..., Options.Rename...)`.
- `unprotectedRenameTo` has old and current variants.
- Validation helpers include `verifyQuotaForRename`, `verifyFsLimitsForRename`, `dstForRenameTo`, `validateDestination`, `validateOverwrite`, `validateRenameSource`, `validateNestSnapshot`, and `checkUnderSameSnapshottableRoot`.
- `RenameOperation` is the transaction-like helper that removes, adds, restores, cleans, and quota-adjusts source/destination inodes.

## Control Flow
The checked path resolves source as `WRITE_LINK` and destination as `CREATE_LINK`, checks protected descendants for non-empty source directories, applies write/delete permissions depending on normal rename or rename-to-trash, then under the write lock calls `unprotectedRenameTo`. The current unprotected path validates source existence/non-root/snapshots, rejects same source/destination and descendant destination moves, rejects reserved paths, checks destination root/parent/type/overwrite semantics, verifies encryption-zone move validity, nested snapshot constraints, same snapshottable root constraints when ordered snapshot deletion/trash are enabled, FS limits, and quota. It then removes source, optionally removes destination, adds the source under the destination name, updates mtimes and leases, cleans overwritten destination blocks/inodes if needed, removes deleted snapshottable directories, updates quota in source snapshot trees, and returns a `RenameResult`.

## State And Persistence Behavior
Rename mutates parent child lists, inode local names, inode references for snapshot-aware moves, parent mtimes, quotas in source and destination trees, leases, block collections for overwritten destinations, and snapshottable-directory registry. Successful checked renames log `logRename`; replay removes blocks immediately if the edit overwrote a destination. `RenameResult` carries audit status, deletion flag, and collected blocks.

## Dependencies And Integration Points
The file depends on `FSDirectory`, `INodeReference`, `SnapshotManager`, `FSDirSnapshotOp`, `FSDirDeleteOp`, `BlockStoragePolicySuite`, `BlockManager`, `LeaseManager`, `DFSUtil.checkProtectedDescendants`, `Options.Rename`, and `DistributedFileSystem` rename semantics.

## Risks And Edge Cases
Snapshot references are the most complex part: source in snapshot can be replaced by `WithName`, destination additions may need `DstReference`, and failure rollback must restore reference counts and names. Quota verification needs destination-parent storage policy and subtracts overwritten destination quota. Old rename returns null on several validation failures, while current rename throws. Edit logging currently occurs after `unprotectedRenameTo`; callers rely on exceptions to avoid logging failed current renames.

## Test Signals
Tests should cover old vs current rename behavior, overwrite flag semantics, file/directory type mismatch, non-empty destination directory rejection, source/destination root rejection, rename into descendant rejection, symlink-to-target rejection, encryption zone boundary moves, same snapshottable root enforcement, nested snapshot denial, quota and max directory item limits, rollback on add failure, overwritten destination block/lease cleanup, and edit-log replay.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirRenameOp.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirSatisfyStoragePolicyOp.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirSatisfyStoragePolicyOp.java

## Purpose
`FSDirSatisfyStoragePolicyOp` marks files/directories for asynchronous storage-policy satisfaction and feeds the Storage Policy Satisfier queue.

## Important APIs, Types, And Functions
- `satisfyStoragePolicy` is the checked entry point.
- `unprotectedSatisfyStoragePolicy` queues an inode during replay/XAttr application.
- `removeSPSXattr` removes the marker XAttr after SPS processing.
- `inodeHasSatisfyXAttr` detects duplicate file requests.

## Control Flow
The checked path asserts the FS write lock, resolves the path under the directory write lock, checks write permission, skips zero-block files, warns on duplicate satisfy XAttr for files, otherwise builds `XATTR_SATISFY_STORAGE_POLICY`, inserts it through `FSDirXAttrOp.setINodeXAttrs`, logs `logSetXAttrs`, and adds the inode ID to `StoragePolicySatisfyManager` if present. Replay/helper flow avoids empty files and only queues the path ID. Removal reads inode XAttrs, removes the SPS marker, updates XAttr storage, and logs `logRemoveXAttrs`.

## State And Persistence Behavior
The persistent request marker is an inode XAttr. In-memory state is the SPS manager pending path queue. Completion/removal persists by removing the XAttr. The operation itself does not move blocks; it schedules asynchronous movement.

## Dependencies And Integration Points
It depends on `FSDirectory`, `BlockManager.getSPSManager`, `StoragePolicySatisfyManager`, `FSDirXAttrOp`, `XAttrStorage`, `XAttrHelper`, and HDFS server constants. `FSDirXAttrOp.unprotectedSetXAttrs` also queues SPS when it sees the marker XAttr during replay.

## Risks And Edge Cases
Zero-block files are skipped because there is nothing to move. Duplicate detection only checks files in `inodeHasSatisfyXAttr`; directories can be re-marked according to the current helper behavior. SPS manager may be null, so persisted XAttrs can exist without immediate queueing if SPS is disabled. Removal mutates a list returned from storage, so tests should catch list mutability assumptions.

## Test Signals
Tests should cover permission checks, zero-block file skip, duplicate marker warning/no duplicate create, directory queueing, null SPS manager behavior, replay queueing from XAttr, marker removal edit logging, and eventual XAttr cleanup after SPS completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirSatisfyStoragePolicyOp.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirSnapshotOp.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirSnapshotOp.java

## Purpose
`FSDirSnapshotOp` owns snapshot administration and query operations for the Namenode: allowing/disallowing snapshot roots, creating/renaming/deleting snapshots, listing snapshottable directories and snapshots, producing diff reports, finding snapshot paths for a file, and enforcing snapshot delete/rename safety checks.

## Important APIs, Types, And Functions
- Mutators: `allowSnapshot`, `disallowSnapshot`, `createSnapshot`, `renameSnapshot`, and `deleteSnapshot`.
- Readers: `getSnapshottableDirListing`, `getSnapshotListing`, `getSnapshotDiffReport`, `getSnapshotDiffReportListing`, and `getSnapshotFiles`.
- Validators: `verifySnapshotName`, private recursive `checkSnapshot(INode, ...)`, and package-visible `checkSnapshot(FSDirectory, INodesInPath, ...)`.

## Control Flow
Snapshot name verification rejects path separators, invalid inode names, and overlong components. Allow/disallow set or reset snapshottable status under the write lock and then log edits. Create/rename resolve the root, require owner permissions, validate names, mutate `SnapshotManager` under the write lock with current time, and log. Listings and diffs run under read locks, with diff checking subtree read permission for both endpoints. Delete resolves and owner-checks the root, builds reclaim collectors, calls `snapshotManager.deleteSnapshot`, updates quotas, removes reclaimed inodes, updates block replication info, logs deletion, and returns collected blocks.

## State And Persistence Behavior
Snapshot state lives in `SnapshotManager`, directory snapshottable features, snapshot roots, snapshot diffs, quota deltas, inode map, and block collections. Edit-log records are `logAllowSnapshot`, `logDisallowSnapshot`, `logCreateSnapshot`, `logRenameSnapshot`, and `logDeleteSnapshot`. Delete returns blocks for later physical removal by callers.

## Dependencies And Integration Points
It integrates with `FSDirectory`, `SnapshotManager`, `DirectorySnapshottableFeature`, `LeaseManager`, `FSNamesystem.getFileInfo`, `BlockManager` replication updates, permission checking, and callers such as delete/rename that need `checkSnapshot` to prevent removal of snapshottable directories containing snapshots.

## Risks And Edge Cases
Recursive `checkSnapshot` can be expensive but is skipped when no snapshottable directories exist. Snapshot diff permissions require read access to snapshot subtrees, not only the root. Deleting a snapshot must update quotas and inode maps consistently with collected block reclamation. A log message in `deleteSnapshot` prints `snapshotName` for both snapshot and root, which is worth noticing in diagnostics.

## Test Signals
Tests should cover invalid snapshot names, owner permission enforcement, allow/disallow edit replay, create default names, rename modification time/logging, listing filtered by user/superuser, snapshot diff permission checks, deleting snapshots with removed inode/block collection, quota updates, and delete/rename rejection when a subtree contains snapshottable directories with snapshots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirSnapshotOp.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirStatAndListingOp.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirStatAndListingOp.java

## Purpose
`FSDirStatAndListingOp` builds read-side HDFS metadata responses: directory listings, file status, file-closed checks, content summaries, quota usage, and block location responses.

## Important APIs, Types, And Functions
- Entry points include `getListingInt`, `getFileInfo`, `isFileClosed`, `getContentSummary`, `getBlockLocations`, and `getQuotaUsage`.
- Status builders include `createFileStatusForEditLog` and private `createFileStatus` overloads.
- Listing helpers include `getListing`, `getSnapshotsListing`, and `getReservedListing`.
- `GetBlockLocationsResult` returns located blocks plus whether atime should be updated.

## Control Flow
Listings resolve the path, normalize reserved `startAfter` inode paths, check read/execute permission on directories, and under a read lock return reserved, snapshot, single-file, or partial directory listings. Directory listing enforces `lsLimit` and a location budget when locations are requested. File info handles a superuser compatibility case where permission exceptions become null, resolves symlinks according to the caller flag, and builds an `HdfsFileStatus`. Block locations validate nonnegative ranges, resolve without early access checks, check unreadable-by-superuser and read permission, computes snapshot/non-UC file size, gets encryption info and EC policy, asks `BlockManager` for located blocks, and signals atime update if precision allows.

## State And Persistence Behavior
Most functions are read-only. The only state effect is indirect: `getBlockLocations` returns `updateAccessTime=true` so the caller can persist access-time changes elsewhere. Status creation reads inode attributes, ACL flags, encryption-zone membership, EC policy, symlinks, children count, and optionally block locations with a block-manager read lock.

## Dependencies And Integration Points
The file ties together `FSDirectory`, `BlockManager`, `FSDirEncryptionZoneOp`, `FSDirErasureCodingOp`, snapshot features, `ContentSummaryComputationContext`, `HdfsFileStatus.Builder`, `LocatedBlocks`, `DirectoryListing`, and permission enforcement. It is a central response builder for `FSNamesystem` RPCs and edit-log status generation.

## Risks And Edge Cases
Nested read locks occur because status creation calls encryption/EC helpers that also read-lock; the code relies on lock reentrancy/ordering. Snapshot paths must not expose UC state beyond snapshot file size. Location-budget logic must account for EC internal block count, not just block count. Content summary can yield locks based on configured limits, so callers must tolerate long-running computations.

## Test Signals
Tests should cover reserved and `.snapshot` listings, `startAfter` reserved inode normalization, lsLimit/location budget behavior including EC files, superuser null compatibility path, unreadable-by-superuser block-location denial, snapshot block ranges, encrypted file status including `FileEncryptionInfo`, ACL/encrypted/EC/snapshottable flags, quota usage fallback to content summary, and atime update signaling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirStatAndListingOp.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirSymlinkOp.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirSymlinkOp.java

## Purpose
`FSDirSymlinkOp` creates HDFS symbolic links and replays symlink creation edits.

## Important APIs, Types, And Functions
- `createSymlinkInt` is the checked operation.
- `unprotectedAddSymlink` constructs and inserts an `INodeSymlink`.
- `addSymlink` handles parent creation, inode ID allocation, edit logging, and metrics/logging.

## Control Flow
The checked path validates the link name, rejects reserved or empty targets, resolves the link with `WRITE_LINK`, optionally verifies the parent exists, rejects existing/invalid targets for creation, checks ancestor write access, checks object limits, then calls `addSymlink` under the directory write lock. Parent directories may be created through `FSDirMkdirOp.createAncestorDirectories`. The created symlink gets default symlink permission with user from directory permissions and no group.

## State And Persistence Behavior
The operation allocates an inode ID, inserts `INodeSymlink`, sets local name/target/mtime/atime, logs `logSymlink`, and increments create-symlink metrics. Replay uses `unprotectedAddSymlink` with supplied inode ID and timestamps.

## Dependencies And Integration Points
It depends on `DFSUtil` name validation, `FSDirectory` path/create checks and quota insertion, `FSNamesystem` object-limit checks, `FSDirMkdirOp` for implicit ancestors, `INodeSymlink`, and `FSEditLog`.

## Risks And Edge Cases
The target is a string and is not resolved, but reserved or empty target names are rejected. The link path uses `WRITE_LINK` so the link itself is created rather than following a symlink. Parent creation must use directory permissions while the symlink inode itself gets default symlink permissions. Failure to add after parent creation returns null from the helper, but the checked wrapper still returns audit info for the original IIP.

## Test Signals
Tests should cover invalid link names, reserved/empty targets, createParent true/false, existing path rejection, ancestor permission denial, object-limit failure, edit-log replay preserving ID/times/target, symlink metrics, and link creation in paths containing symlink components.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirSymlinkOp.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirTruncateOp.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirTruncateOp.java

## Purpose
`FSDirTruncateOp` implements file truncation, including validation, lease recovery, snapshot-aware block collection, quota adjustment, edit-log replay, and scheduling block recovery when truncation cuts through the last block.

## Important APIs, Types, And Functions
- `truncate` is the checked operation returning `TruncateResult`.
- `unprotectedTruncate` has replay/public internal and private mutation variants.
- `prepareFileForTruncate` converts a file to under-construction and prepares copy-on-truncate or in-place truncate recovery.
- Helpers include `verifyQuotaForTruncate` and `shouldCopyOnTruncate`.

## Control Flow
The checked path asserts global FS write lock, resolves with `WRITE`, checks write permission, rejects striped files and lazy-persist files, detects an existing identical truncate recovery, recovers the lease, rejects expansion, calls private `unprotectedTruncate` to record snapshot modification and collect blocks beyond the new length, and if truncating inside a block calls `prepareFileForTruncate`. It updates quota deltas, logs `logTruncate`, and returns whether the client must wait for recovery. Replay applies the same truncation, prepares the truncate block from the edit, deletes obsolete old blocks if needed, and removes collected blocks from the block manager.

## State And Persistence Behavior
Truncate changes file length/block list immediately, collects removed blocks, updates mtime, may convert the file to under construction, creates a lease, creates or updates a truncate block with a new generation stamp, updates block maps, and adjusts quotas. Persistence is the truncate edit containing path/client/new length/mtime/truncate block; recovery completion is driven later by block recovery reports.

## Dependencies And Integration Points
It uses `FSNamesystem` global lock and lease recovery, `FSDirectory` write/read locks and quota checks, `BlockManager` block map/generation stamp/recovery APIs, `INodeFile` snapshot-aware block retention, `BlockUnderConstructionFeature`, and `RecoverLeaseOp.TRUNCATE_FILE`.

## Risks And Edge Cases
Truncating on a block boundary returns immediate success; truncating inside a block makes the file under recovery. Copy-on-truncate is mandatory during rolling/unfinished upgrades or when the last block is in the latest snapshot. Replay must match the stored truncate block exactly. Lazy-persist and striped files are unsupported. Duplicate truncate requests with the same target length are treated idempotently.

## Test Signals
Tests should cover equal length idempotence, expansion rejection, striped/lazy-persist rejection, on-boundary vs in-block return values, duplicate truncate under recovery, lease recovery interactions, quota deltas, snapshot last-block copy-on-truncate, rolling upgrade copy behavior, edit-log replay block matching, and block map removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirTruncateOp.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirWriteFileOp.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirWriteFileOp.java

## Purpose
`FSDirWriteFileOp` owns Namenode namespace/block operations for file creation, block allocation, block abandonment, open-file persistence, add-block retry handling, file completion, and edit-log file-add replay.

## Important APIs, Types, And Functions
- Creation: `resolvePathForStartFile`, `startFile`, `addFileForEditLog`, private `addFile`, and `newINodeFile`.
- Block lifecycle: `validateAddBlock`, `chooseTargetForNewBlock`, `storeAllocatedBlock`, `saveAllocatedBlock`, `addBlock`, `abandonBlock`, `unprotectedRemoveBlock`, `persistBlocks`, and `persistNewBlock`.
- Completion: `completeFile` and `completeFileInternal`.
- Supporting types: `ValidateAddBlockResult`, `FileState`, `BlockInfoContiguous`, `BlockInfoStriped`, `DatanodeStorageInfo`, `ErasureCodingPolicy`, and `FileEncryptionInfo`.

## Control Flow
Start-file resolution checks ancestor write permission, existing directory/file state, overwrite permission, create-parent requirements, and create/overwrite flags. `startFile` deletes an existing inode on overwrite or attempts lease recovery before throwing on non-overwrite, checks object limits, creates missing parents, chooses contiguous or striped layout based on EC policy and `shouldReplicate`, creates an under-construction `INodeFile`, adds a lease, writes encryption info if present, applies lazy-persist or copy-on-create storage policy, logs `logOpenFile`, and returns status. Add-block is split into validation and storage: validation under read lock checks lease, safe mode, object/block limits, previous block identity, retry cases, replication progress, block size/type/targets, and EC layout; target choice calls block placement; storage rechecks state under write lock, commits the previous block, creates a new block, adds it to inode and block map, logs `logAddBlock`, and returns a write-token `LocatedBlock`. Completion validates lease and retry close cases, checks file progress, commits/completes the last block, queues committed blocks, and finalizes the under-construction inode.

## State And Persistence Behavior
The file mutates namespace inodes, under-construction file features, leases, block lists, block maps, scheduled block counters, quotas, encryption XAttrs, storage policy IDs, and pending replication/commit state. Edit-log records include open-file, update-blocks, add-block, and replayed file creation. Block tokens are generated for returned write locations.

## Dependencies And Integration Points
It is one of the densest integration points: `FSNamesystem`, `FSDirectory`, `BlockManager`, `DatanodeManager`, `LeaseManager`, `FSDirDeleteOp`, `FSDirMkdirOp`, `FSDirEncryptionZoneOp`, `FSDirErasureCodingOp`, `FSDirStatAndListingOp`, ACL/XAttr storage, network topology resolution, and HDFS client create/addBlock/complete protocols all meet here.

## Risks And Edge Cases
Add-block retry detection is subtle and protects against duplicate empty blocks, HA retries, and bogus previous-block IDs. Validation must be repeated after block placement because locks were released. Overwrite must clean leases and collect blocks correctly. Striped files use EC target counts and `BlockInfoStriped`; contiguous files use replication. Lazy-persist storage policy can be disabled. Encryption info must be written after inode creation and before open-file edit persistence semantics are relied on.

## Test Signals
Tests should cover create/overwrite flag matrix, parent creation, lease recovery on existing files, encrypted file creation and retry when zone changes, EC striped file creation/add-block, lazy-persist disabled behavior, add-block retry cases for previous/penultimate/empty block, target choice with excluded/favored/locality flags, abandon block quota/scheduled-counter updates, complete-file retry after successful close, max blocks per file, edit-log replay of open files with ACL/XAttrs/storage/EC policy, and quota updates on add/remove block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirWriteFileOp.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirXAttrOp.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirXAttrOp.java

## Purpose
`FSDirXAttrOp` implements extended attribute set/get/list/remove for HDFS inodes and provides shared unprotected XAttr mutation helpers used by encryption zones, erasure coding, storage policy, snapshot deletion, and SPS features.

## Important APIs, Types, And Functions
- User operations: `setXAttr`, `getXAttrs`, `listXAttrs`, and `removeXAttr`.
- Internal helpers: `unprotectedSetXAttrs`, `unprotectedRemoveXAttrs`, `filterINodeXAttrs`, `setINodeXAttrs`, `getXAttrByPrefixedName`, and `unprotectedGetXAttrByPrefixedName`.
- Access/config helpers: `checkXAttrChangeAccess`, `checkXAttrSize`, `checkXAttrsConfigFlag`, and `isUserVisible`.

## Control Flow
Set checks the global xattr feature flag, size limit, API namespace permission filter, resolves with `WRITE`, checks mutation access for user XAttrs, applies create/replace semantics via `unprotectedSetXAttrs`, logs `logSetXAttrs`, and returns audit status. Get/list check config, permission-filter requested or returned XAttrs, resolve with `READ`, enforce read access, and filter hidden namespaces. Remove checks config and API permission, resolves with `WRITE`, checks mutation access, filters matching XAttrs out while preventing deletion of encryption-zone and unreadable-by-superuser markers, updates storage, logs removed XAttrs, or errors when absent. `unprotectedSetXAttrs` also triggers feature-specific side effects when setting encryption zone, re-encryption, SPS, unreadable-by-superuser, and snapshot-deleted XAttrs.

## State And Persistence Behavior
XAttrs are stored on inode `XAttrFeature`s through `XAttrStorage.updateINodeXAttrs` at the latest snapshot ID. Edits persist set/remove lists. Setting crypto zone XAttrs updates `EncryptionZoneManager` and re-encryption status in memory; setting SPS XAttrs queues the inode; special validation restricts unreadable-by-superuser to files and snapshot-deleted marker to snapshot roots.

## Dependencies And Integration Points
This helper is a cross-cutting integration point for `XAttrPermissionFilter`, `XAttrStorage`, `XAttrHelper`, `FSDirEncryptionZoneOp`, `FSDirSatisfyStoragePolicyOp`, protobuf parsing, snapshot roots, HDFS security constants, and edit-log replay. Other `FSDir*Op` classes rely on `setINodeXAttrs` and `filterINodeXAttrs` for storage policy and EC/SPS state.

## Risks And Edge Cases
XAttr equality ignores value for replace/remove matching in several paths, so duplicate and deletion semantics must remain consistent. User-visible limit counts `USER` and `TRUSTED` namespaces only. Sticky directories require owner or superuser for user-XAttr changes. Reserved raw paths affect permission filtering. Feature-specific side effects mean replay order and validation failures can impact encryption-zone/SPS state reconstruction.

## Test Signals
Tests should cover disabled xattrs, max size, create/replace flags, duplicate input rejection, user-visible count limit, namespace permission filtering for raw/non-raw paths, sticky directory access checks, remove absent error, protected XAttr deletion rejection, encryption-zone XAttr manager side effects, re-encryption status updates, SPS queueing, unreadable-by-superuser file-only rule, snapshot-deleted root-only rule, and get/list filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirXAttrOp.java -->
