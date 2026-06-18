# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestLeaseRecoveryStriped.java

## Purpose
Tests lease recovery for erasure-coded striped files, safe-length calculation, stale datanode handling, and zero-length internal replica cases.

## APIs and Control Flow
`setup` configures block/cell sizes for the default EC policy, starts data+parity DNs, enables the policy, and applies it to the test directory. `BlockLengths` wraps internal block lengths and computes `StripedBlockUtil.getSafeLength`. `testLeaseRecovery` runs generated block-length suites through `runTest`; `runTest` writes partial internal blocks, recovers the lease as another user, validates data to safe length, restarts the NameNode, waits for first block report, and validates again. `testLeaseRecoveryWithStaleDataNode` marks a DN stale, recomputes safe length without that block, recovers, and checks data. `testSafeLength` checks known safe-length values. `testLeaseRecoveryWithManyZeroLengthReplica` writes one cell, waits for all streamers to ack, replaces their block streams with null outputs, and recovers. Helpers compute stop positions, wait for streamer acks/bytes sent, abort streams, and call `DistributedFileSystem.recoverLease`.

## State, Dependencies, Integration
State spans EC policy metadata, striped data streamers, internal block lengths, block streams, stale DN timestamps, old generation stamps, and block reports after NN restart. Dependencies include `DFSStripedOutputStream`, `StripedDataStreamer`, `StripedBlockUtil`, `Whitebox`, `BlockRecoveryWorker`, `StripedFileTestUtil`, and `DataNodeTestUtils`. It integrates striped client writing, DN recovery, and safe-length math.

## Risks and Test Signals
Signals are safe-length equality, successful data validation before and after restart, and recoverLease completion. Risks include randomized block-length suites, heavy internal reflection through `Whitebox`, timing on streamer ack waits, and a duplicated `StripedFileTestUtil.checkData` argument line in the displayed source would be a compile risk if present; the actual checked file should be verified before relying on this test.
