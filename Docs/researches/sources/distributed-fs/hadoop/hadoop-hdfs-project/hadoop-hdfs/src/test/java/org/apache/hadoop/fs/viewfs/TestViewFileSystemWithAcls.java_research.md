# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemWithAcls.java

## Purpose

`TestViewFileSystemWithAcls` verifies that `ViewFileSystem` correctly dispatches ACL operations to the mounted HDFS namespace. It uses two federated NameNodes and confirms ACL mutations on one mount do not leak to the other.

## Important APIs, types, and functions

Important APIs are `MiniDFSCluster`, `MiniDFSNNTopology.simpleFederatedTopology(2)`, `FileSystem`, `ConfigUtil.addLink`, `AclEntry`, `AclStatus`, `AclTestHelpers.aclEntry`, `setAcl`, `modifyAclEntries`, `removeDefaultAcl`, `removeAcl`, and `removeAclEntries`.

## Control flow, state, and persistence

`@BeforeAll` enables NameNode ACLs and starts a two-namespace cluster. Each test clears and recreates per-namespace target roots, mounts `/mountOnNn1` and `/mountOnNn2`, and opens `viewfs:///`. The test sets ACLs on namespace 1, verifies through both ViewFS and raw HDFS, modifies defaults, removes defaults and full ACLs, checks namespace 2 is still clean, then repeats mutation/removal on namespace 2.

## Dependencies and integration points

The test covers ViewFileSystem ACL method forwarding, federated mount resolution, HDFS ACL feature enablement, default ACL expansion, and isolation between mount targets.

## Risks and test signals

Risks are dispatching ACL operations to the wrong namespace, losing default ACL entries, incorrect mask/group expansion, or stale ACLs after removal. Signals are exact `AclEntry[]` arrays and zero-entry checks on the untouched namespace.
