# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/fs/viewfs/TestViewFsWithXAttrs.java

## Purpose

`TestViewFsWithXAttrs` verifies FileContext/ViewFs extended-attribute operations against federated HDFS mount targets. It confirms XAttrs are written to, read from, and removed from the correct namespace.

## Important APIs, types, and functions

The test uses `FileContext`, `MiniDFSCluster`, `MiniDFSNNTopology.simpleFederatedTopology(2)`, `ConfigUtil.addLink`, `FsPermission`, and FileContext XAttr methods: `setXAttr`, `getXAttr`, `getXAttrs`, and `removeXAttr`. Fixtures are `user.a1`, `user.a2`, and byte values `{0x31,0x32,0x33}` and `{0x37,0x38,0x39}`.

## Control flow, state, and persistence

Each test recreates target roots in both HDFS namespaces with `0750`, configures two ViewFs mounts, and opens `viewfs:///`. It sets two XAttrs on mount 1, verifies values through ViewFs and raw namespace 1, checks namespace 2 is empty, removes both attributes, then repeats on mount 2 and verifies cleanup.

## Dependencies and integration points

This integrates ViewFs XAttr forwarding, HDFS XAttr metadata, federated mount resolution, and byte-array preservation through FileContext APIs.

## Risks and test signals

Risks include namespace leakage, value corruption, stale attributes after removal, or API divergence between FileContext and FileSystem variants. Signals are exact byte-array equality and empty XAttr maps on untouched and cleaned namespaces.
