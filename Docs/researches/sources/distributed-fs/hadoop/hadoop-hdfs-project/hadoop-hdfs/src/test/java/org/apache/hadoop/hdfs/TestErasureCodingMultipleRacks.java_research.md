# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestErasureCodingMultipleRacks.java

## Purpose
Tests rack-aware placement for erasure-coded block groups when racks have skewed DataNode counts. The goal is to ensure placement succeeds and, where possible, remains rack-failure tolerant even in unbalanced topologies.

## Important APIs and Types
Uses `DFSTestUtil.setupCluster`, `DistributedFileSystem.setErasureCodingPolicy`, `DFSTestUtil.writeFile`, `getFileBlockLocations`, `DFSTestUtil.waitForReplication`, `ExtendedBlock`, and topology path parsing. It enables trace/debug logging for `BlockPlacementPolicy`, `BlockPlacementPolicyDefault`, `BlockPlacementPolicyRackFaultTolerant`, and `NetworkTopology`.

## Control Flow
`setup()` selects the EC policy and disables load consideration so placement behavior dominates. `setupCluster` creates a cluster with requested DataNode/rack skew and applies the EC policy to `/`. `testSkewedRack1` covers a two-rack extreme with one single-DN rack. `testSkewedRack2` covers many single-DN racks plus one larger rack. `testSkewedRack3` writes several files in a topology where two racks have enough nodes and asserts no rack receives more blocks than the parity-unit count.

## State, Persistence, Dependencies, Integration
State is block-placement metadata and rack topology strings. The tests depend on MiniDFSCluster topology construction and the rack-fault-tolerant placement policy. There is no restart persistence coverage.

## Risks and Test Signals
Signals are full block-group host counts and rack-count bounds. Risks are topology parsing assumptions and possible flakiness if placement behavior changes with load consideration, which the test disables.
