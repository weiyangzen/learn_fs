# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestDistributedFileSystemWithECFileWithRandomECPolicy.java

## Purpose
Runs the full `TestDistributedFileSystemWithECFile` suite with a random non-default EC policy. This validates that block-location, HA replay, explicit EC policy, replicated-file override, and statistics assumptions are not hardcoded to the default striped policy.

## Important APIs and Types
The class extends `TestDistributedFileSystemWithECFile` and overrides `getEcPolicy()`. It uses `StripedFileTestUtil.getRandomNonDefaultECPolicy()`, `ErasureCodingPolicy`, and SLF4J logging.

## Control Flow
The constructor chooses a random non-default system EC policy once per test instance and logs the inherited test class plus policy name. All setup, assertions, and cluster lifecycle remain in the superclass; this subclass only changes the policy geometry used by those inherited tests.

## State, Persistence, Dependencies, Integration
State is the selected `ErasureCodingPolicy` field. Its integration point is the superclass setup path, which computes cell size, block-group size, DataNode count, and assertions from `getEcPolicy()`. Persistence behavior is therefore inherited and retested under a different policy ID and schema.

## Risks and Test Signals
The signal is polymorphic coverage of the same DFS APIs under non-default EC geometry. The primary risk is random selection causing intermittent exposure to policy-specific timing or layout behavior; failures are useful because they show hidden default-policy assumptions.
