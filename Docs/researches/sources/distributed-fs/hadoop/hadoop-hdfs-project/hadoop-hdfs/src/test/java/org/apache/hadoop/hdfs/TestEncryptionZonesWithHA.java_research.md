# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestEncryptionZonesWithHA.java

## Purpose
Tests encryption-zone metadata replication across HDFS HA failover. The intended guarantee is that a standby NameNode catches up on encryption-zone edits and can serve correct zone metadata and decrypted file reads after becoming active.

## Important APIs and Types
Uses `MiniDFSNNTopology.simpleHATopology`, `HATestUtil.configureFailoverFs`, `HATestUtil.waitForStandbyToCatchUp`, `HAUtil.setAllowStandbyReads`, `HdfsAdmin`, `JavaKeyStoreProvider`, `KeyProviderCryptoExtension`, and `DFSTestUtil.createKey`.

## Control Flow
`setupCluster()` enables fast edit tailing, creates a two-NameNode HA cluster, transitions NameNode 0 active, configures a failover filesystem, creates the same test key on both NameNodes, and points the DFS client at NameNode 0's provider. The test creates `/enc` as an encryption zone, adds a child directory and file, records file contents, waits for standby catch-up, shuts down NameNode 0, transitions NameNode 1 active, then verifies zone lookup for the root and child plus file content preservation.

## State, Persistence, Dependencies, Integration
State is HA-shared namespace edits for encryption-zone creation and encrypted-file metadata, plus both NameNodes' key providers. The test integrates failover client configuration, standby edit tailing, `HdfsAdmin` against each NameNode URI, and encrypted read paths after failover.

## Risks and Test Signals
The main signal is successful lookup and read on the new active after the original active is shut down. Risks include false failures if standby edit tailing lags; the explicit catch-up wait reduces this.
