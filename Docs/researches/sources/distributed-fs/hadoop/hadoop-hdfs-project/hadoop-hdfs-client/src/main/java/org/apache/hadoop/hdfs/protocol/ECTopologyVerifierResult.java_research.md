# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/ECTopologyVerifierResult.java

## Purpose
`ECTopologyVerifierResult` reports whether the current cluster topology can support one or more erasure coding policies.

## APIs and Behavior
The constructor stores `isSupported` and a human-readable `resultMessage`. `isSupported()` and `getResultMessage()` are the only accessors.

## State, Dependencies, and Integration
The object is immutable and private to HDFS protocol use. It is returned by `ClientProtocol.getECTopologyResultForPolicies` and consumed by admin/client code before enabling or applying EC policies.

## Risks and Test Signals
There is no equality or validation. Tests should cover supported and unsupported results, null/empty messages, and propagation through EC policy verification RPCs.
