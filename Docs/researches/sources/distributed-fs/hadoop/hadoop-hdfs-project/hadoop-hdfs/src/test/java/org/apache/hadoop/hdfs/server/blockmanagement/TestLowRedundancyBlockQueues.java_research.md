# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestLowRedundancyBlockQueues.java

## Purpose
`TestLowRedundancyBlockQueues` validates priority queues and counters in `LowRedundancyBlocks` for contiguous replicated blocks and erasure-coded striped block groups. It is parameterized across EC policies.

## Important APIs, Types, and Functions
The test uses `LowRedundancyBlocks`, `BlockInfoContiguous`, `BlockInfoStriped`, `ErasureCodingPolicy`, `StripedFileTestUtil.getECPolicies`, queue constants such as `QUEUE_HIGHEST_PRIORITY`, and helper methods `verifyBlockStats`, `assertAdded`, and `assertInLevel`.

## Control Flow
The parameterized class receives an EC policy. `testDeletedBlocks` checks that deleted/corrupt block infos are skipped when choosing low-redundancy blocks and that queue positions advance and reset. `testQueuePositionCanBeReset` checks iterator cursor reset. `testBlockPriorities` adds blocks with different current and expected replica counts, updates expected counts, and checks queue levels and counters. `testRemoveWithWrongPriority` ensures removal decrements corrupt counts even with an incorrect priority. `testStripedBlockPriorities` checks EC group priority thresholds. `testRemoveBlockInManyQueues` verifies a block present in multiple queue levels is fully removed.

## State and Persistence Behavior
State is in-memory queue membership, queue cursors, per-category counters, corrupt block counters, badly-distributed counters, and block collection IDs used to distinguish deleted blocks.

## Dependencies and Integration Points
This test directly protects the block manager's reconstruction candidate queues. It covers both replicated and EC queues used by redundancy scheduling.

## Risks and Edge Cases
Risks include returning deleted blocks, cursor reset bugs, duplicate additions, incorrect priority classification, corrupt replication-one count drift, EC corrupt count drift, badly-distributed accounting, and incomplete removal from multiple queue levels.

## Test Signals
Signals include exact queue-level membership, exact counter assertions from `verifyBlockStats`, selected block IDs from `chooseLowRedundancyBlocks`, false duplicate additions, and final `contains` false after broad removal.
