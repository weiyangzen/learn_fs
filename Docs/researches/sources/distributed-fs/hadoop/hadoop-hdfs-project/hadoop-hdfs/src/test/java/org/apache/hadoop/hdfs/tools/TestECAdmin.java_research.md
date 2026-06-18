# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/tools/TestECAdmin.java

## Purpose
`TestECAdmin` covers `ECAdmin` command behavior that is difficult to express in the generic CLI suite, mainly cluster-topology validation and user-facing output for enabling or verifying erasure coding policies.

## Important APIs, Types, And Functions
The file uses `ECAdmin`, `DFSTestUtil.setupCluster`, `MiniDFSCluster`, system EC policies from `SystemErasureCodingPolicies`, and captured `System.out`/`System.err`. Helpers `assertNotEnoughDataNodesMessage`, `assertNotEnoughRacksMessage`, `resetOutputs`, and `runCommandWithParams` centralize command execution and output checks.

## Control Flow
Tests redirect standard streams in `setup()`, create clusters with specific DataNode and rack counts, enable or disable policies through the filesystem, run `-verifyClusterSetup` or `-enablePolicy`, and assert return codes plus stdout/stderr contents. They cover insufficient DataNodes, insufficient racks, successful topologies, no enabled EC policies, invalid policy names, too many positional arguments, and missing `-policy` values.

## State, Persistence, And Dependencies
State lives in cluster topology, enabled EC policy state, and captured stream buffers. There is no durable persistence outside the cluster. Teardown restores streams and shuts down clusters.

## Integration Points
The test connects `ECAdmin` CLI parsing with NameNode EC policy management and topology/rack validation logic.

## Risks
The assertions are message-substring based but still tied to exact policy names and wording. Shared `System.out`/`System.err` replacement can affect other tests if teardown is skipped. Cluster topology helper behavior determines whether rack counts are realistic.

## Test Signals
Signals are command return codes `0`, `2`, `1`, or `-1`, expected topology-warning messages, empty stderr on normal validation, and explicit RemoteException text for unknown policy names.
