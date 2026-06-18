# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeAttributes.java

## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeAttributes.java

Purpose: `INodeAttributes` is the read-only metadata contract used by permission checking, snapshots, and namespace code when the caller needs inode metadata without necessarily mutating or holding the live inode object directly.

Important APIs and types: the interface exposes directory status, local name bytes, user, group, `FsPermission`, permission short/long, ACL feature, XAttr feature, modification time, and access time. The abstract nested `SnapshotCopy` implements immutable copies of common attributes, storing name bytes, packed permission status, optional de-duplicated ACL feature, modification/access times, and XAttr feature.

Control flow: `SnapshotCopy` constructors either pack a provided `PermissionStatus` or copy fields from an `INode`. If an ACL feature is present, it is passed through `AclStorage.addAclFeature` for feature de-duplication/reference management. Accessors unpack user/group/mode through `INodeWithAdditionalFields.PermissionStatusFormat` and construct `FsPermission` from the stored short.

State and persistence behavior: `SnapshotCopy` is read-only except for its private XAttr field reference and represents metadata captured for snapshot/history use. Packed permissions mirror the compact in-memory/on-disk encoding used by live inodes. ACL feature references participate in shared ACL storage accounting; XAttr features are referenced as captured.

Dependencies and integration points: it is consumed by `FSPermissionChecker`, snapshot diff classes, directory/file attribute copies, and external attribute providers. It depends on `PermissionStatus`, `FsPermission`, `AclFeature`, `AclStorage`, `XAttrFeature`, and permission status packing.

Risks: name bytes and XAttr feature references are not defensively copied in this class, so callers must treat supplied data as immutable. ACL reference accounting must be balanced by cleanup paths elsewhere. Constructing new `FsPermission` on each call is simple but not allocation-free. Attribute providers can return implementations with different behavior, so consumers should rely only on the interface.

Test signals: tests should cover copying from live inodes and explicit fields, permission packing/unpacking, ACL feature de-duplication, null local names, XAttr retention, snapshot read-only behavior, and permission-checker use against provider-supplied attributes.
