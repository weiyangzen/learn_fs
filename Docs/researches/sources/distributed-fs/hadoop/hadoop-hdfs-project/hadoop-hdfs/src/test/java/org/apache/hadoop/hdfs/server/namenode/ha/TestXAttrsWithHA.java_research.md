# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestXAttrsWithHA.java

Purpose: verifies extended attributes are tailed by standby NameNodes and remain available after failover.

Important APIs and types: `MiniDFSCluster`, `HAUtil.setAllowStandbyReads`, `FileSystem.setXAttr`, `FileSystem.getXAttrs`, `NameNode.getRpcServer().getXAttrs`, `XAttr`, `XAttrSetFlag`, and `HATestUtil.waitForStandbyToCatchUp`.

Control flow: setup creates a two-NN HA cluster with standby reads enabled, one DN, short tailing period, and NN0 active. The test creates `/file`, sets two `user.*` xattrs with `CREATE`, waits for standby catch-up, and reads xattrs directly from NN1's RPC server to confirm two entries. It then shuts down NN0, transitions NN1 active, reads xattrs through the failover filesystem, checks both byte arrays exactly, and deletes the file.

State and persistence behavior: xattr namespace metadata is persisted via edit logs and reconstructed on standby; after failover, the former standby must serve the same byte values as active metadata.

Dependencies and integration points: integrates HA edit tailing, xattr feature enablement defaults, standby reads, NameNode RPC xattr retrieval, and failover FileSystem access.

Risks and test signals: risks include missing xattr edits on standby, xattr values corrupted during failover, or failover client not seeing metadata on new active. Signals are direct standby count assertions and byte-for-byte `assertArrayEquals` checks after activation.
