# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsWithAcls.java

## Purpose

`TestViewFsWithAcls` is the FileContext/ViewFs counterpart to the ViewFileSystem ACL test. It verifies ACL operations route to the correct HDFS namespace through `FileContext`.

## Important APIs, types, and functions

Important APIs are `FileContext`, `MiniDFSCluster`, `MiniDFSNNTopology.simpleFederatedTopology(2)`, `ConfigUtil.addLink`, `AclEntry`, `AclStatus`, `FsPermission`, `AclTestHelpers.aclEntry`, and FileContext ACL methods: `setAcl`, `modifyAclEntries`, `removeDefaultAcl`, `removeAcl`, and `removeAclEntries`.

## Control flow, state, and persistence

Setup enables HDFS ACLs, creates two HDFS `FileContext` targets, recreates per-namespace target roots with `0750`, mounts `/mountOnNn1` and `/mountOnNn2`, and opens `viewfs:///`. The test sets, modifies, and removes ACLs on the first mount, confirms raw namespace 1 matches, confirms namespace 2 stays empty, then repeats mutation/removal on namespace 2.

## Dependencies and integration points

This covers ViewFs ACL forwarding, HDFS ACL default-entry expansion, mount isolation, FileContext permission state, and federated namespace resolution.

## Risks and test signals

Risks mirror the FileSystem ACL variant: wrong namespace dispatch, default ACL loss, incorrect mask/group entries, or incomplete cleanup. Signals are exact `AclEntry[]` expectations and zero-entry checks on raw and ViewFs status.
