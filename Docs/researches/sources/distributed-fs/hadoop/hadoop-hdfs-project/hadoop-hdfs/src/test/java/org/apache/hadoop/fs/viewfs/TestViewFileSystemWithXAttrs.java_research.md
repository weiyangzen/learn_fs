# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFileSystemWithXAttrs.java

## Purpose

`TestViewFileSystemWithXAttrs` verifies that extended-attribute operations through `ViewFileSystem` resolve to the correct mounted HDFS namespace and remain isolated across federated NameNodes.

## Important APIs, types, and functions

The test uses `MiniDFSCluster`, `MiniDFSNNTopology.simpleFederatedTopology(2)`, `FileSystem`, `ConfigUtil.addLink`, `setXAttr`, `getXAttr`, `getXAttrs`, and `removeXAttr`. Test fixtures are `user.a1`/`user.a2` with small byte-array values.

## Control flow, state, and persistence

Each test clears two HDFS target roots, mounts them as `/mountOnNn1` and `/mountOnNn2`, and opens `viewfs:///`. It sets two XAttrs on the first mount, verifies them through ViewFS and raw namespace 1, checks namespace 2 remains empty, removes them, then repeats the same checks on namespace 2. State is temporary XAttr metadata in the MiniDFSCluster namespaces.

## Dependencies and integration points

This covers ViewFileSystem XAttr forwarding, HDFS XAttr storage, federated mount resolution, and namespace isolation. Unlike ACL tests, no explicit XAttr config is set here, so it relies on the cluster defaults used by the HDFS test environment.

## Risks and test signals

Risks include wrong namespace resolution, byte-array corruption, incomplete removal, and leakage between mounts with identical target-root shapes. Signals are exact byte-array equality and zero-sized XAttr maps after removal or on the untouched namespace.
