<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/PendingRecoveryBlocks.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/PendingRecoveryBlocks.java

## Purpose

`PendingRecoveryBlocks` rate-limits lease/block recovery attempts. It ensures only one recovery attempt for a block is active until its timeout expires.

## Important APIs and types

The class stores `BlockRecoveryAttempt` entries in a `LightWeightHashSet`. Main APIs are `add`, `remove`, `isUnderRecovery`, `setRecoveryTimeoutInterval`, and test-overridable `getTime`. `BlockRecoveryAttempt` equality and hashing are based only on `BlockInfo`, while `timeoutAt` is mutable.

## Control flow

`add` checks for an existing attempt. If none exists, it inserts one with `now + recoveryTimeoutInterval`. If an existing attempt has timed out, it refreshes the timeout and returns true. If not timed out, it logs the remaining time and rejects the new recovery. `remove` clears an attempt after recovery finishes or is abandoned.

## State and persistence behavior

State is in-memory and all public mutations are synchronized. There is no persistence; recovery-in-progress state is reconstructed from runtime lease/block recovery flows after restart.

## Dependencies and integration points

It depends on `BlockInfo`, `LightWeightHashSet`, monotonic time, and BlockManager logging. It integrates with NameNode block recovery scheduling and lease recovery.

## Risks and edge cases

Timeout comparison uses `currentTime > timeoutAt`, so equality is still considered active. If callers forget `remove`, entries remain until a later retry after timeout. Mutating `timeoutAt` inside a hash-set element is safe only because hash/equality ignore that field.

## Test signals

Useful tests cover first add, duplicate before timeout, retry after timeout, remove-and-readd, `isUnderRecovery`, custom timeout interval, and monotonic time boundary equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/PendingRecoveryBlocks.java -->
