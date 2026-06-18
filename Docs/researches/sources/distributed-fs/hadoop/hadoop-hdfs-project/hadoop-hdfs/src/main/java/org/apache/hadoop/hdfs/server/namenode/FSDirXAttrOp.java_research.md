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
