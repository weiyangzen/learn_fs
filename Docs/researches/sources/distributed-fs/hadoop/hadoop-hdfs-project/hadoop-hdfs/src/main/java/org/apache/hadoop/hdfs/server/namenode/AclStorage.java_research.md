# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/AclStorage.java

Purpose: utility class defining how HDFS logical ACLs are stored on inodes by splitting data between `FsPermission` bits and `AclFeature` entries.

Important APIs/types/functions: `copyINodeDefaultAcl()` inherits parent default ACLs to new files/directories, filtering by child mode and copying default ACLs only to directories. `readINodeAcl()` reads explicit feature entries for an inode or inode attributes. `getEntriesFromAclFeature()` decodes packed ints. `readINodeLogicalAcl()` reconstructs full logical ACL from permission bits plus feature access/default entries. `updateINodeAcl()` stores a new full ACL, validating default ACLs only on directories, replacing/removing features, and updating permissions. Private `createAclFeature()` stores named access entries and all defaults while omitting owner/mask/other entries represented in permission bits. Permission constructors preserve sticky bit and map ACL mask to group permission. `addAclFeature()` and `removeAclFeature()` intern features in `UNIQUE_ACL_FEATURES`.

Control flow: ACL modification code first uses `AclTransformation` to produce sorted validated logical ACLs, then calls `updateINodeAcl()`. Reads reconstruct logical views for API responses. New inode creation calls `copyINodeDefaultAcl()` to inherit directory defaults.

State and persistence behavior: extended ACL presence is represented by an inode ACL feature plus permission bits. Minimal ACLs remove the feature. Identical `AclFeature`s are reference-counted in a static map to reduce memory. Snapshot-aware updates pass `snapshotId` to inode feature/permission mutation methods.

Dependencies and integration points: central to NameNode ACL APIs, `INode`, `INodeDirectory`, `INodeAttributes`, snapshots, quota checks, `FsPermission`, `AclUtil`, and `AclTransformation`.

Risks: methods assume ACL lists are already validated and sorted; bypassing `AclTransformation` can corrupt storage layout. Default ACLs on files are rejected only in update. Feature interning depends on immutable entry arrays. Copying default ACLs uses child creation mode to mask permissions, so subtle POSIX inheritance behavior must stay covered by tests.

Test signals: `TestAclTransformation`, `TestNameNodeAcl`, `TestExtendedAcls`, `TestAclsEndToEnd`, `TestAclWithSnapshot`, `TestFSImageWithAcl`, WebHDFS/ViewFS ACL tests, and CLI ACL tests cover transformations, inheritance, persistence, snapshots, and API views.
