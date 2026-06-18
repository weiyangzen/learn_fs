# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestErasureCodingPolicyWithSnapshotWithRandomECPolicy.java

## Purpose
Runs `TestErasureCodingPolicyWithSnapshot` with a random non-default EC policy. It ensures snapshot metadata preservation and restart behavior are not tied to the default EC policy.

## Important APIs and Types
Extends `TestErasureCodingPolicyWithSnapshot`, overrides `getEcPolicy()`, and uses `StripedFileTestUtil.getRandomNonDefaultECPolicy()`, `ErasureCodingPolicy`, and logging.

## Control Flow
The constructor selects and logs a random non-default policy. The inherited setup uses that policy to choose DataNode count and enable the policy; all inherited snapshot, copy, and restart tests then run with the alternate policy.

## State, Persistence, Dependencies, Integration
Local state is the selected policy. Snapshot metadata, fsimage persistence, and file-status behavior are inherited from the superclass and exercised under a different policy ID/schema.

## Risks and Test Signals
The main signal is policy-agnostic snapshot behavior. Randomness can make results policy-specific, but the log records the policy name.
