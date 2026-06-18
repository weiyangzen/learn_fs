# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/diskbalancer/planner/Step.java

Purpose: interface for one executable diskbalancer plan action.

Important APIs/types/functions: exposes bytes to move, source/destination `DiskBalancerVolume`, ideal storage, volume set ID, human-readable size formatting, maximum disk errors, tolerance percentage, bandwidth, and setters for tunable execution parameters.

Control flow: planners create `Step` instances, commands print and tune them, `NodePlan` serializes/deserializes them, and DataNode execution consumes them.

State and persistence behavior: none at interface level; implementations are expected to be JSON-serializable because `NodePlan` uses polymorphic typing.

Dependencies and integration points: implemented by `MoveStep`; test package includes `SampleStep` for deserialization validation.

Risks: interface exposes mutable settings but no validation policy; callers and DataNode execution must enforce ranges and semantics. Future step types must be permitted by `NodePlan` allowed-package configuration.

Test signals: plan serialization/security tests and `TestDiskBalancerCommand` exercise concrete `MoveStep` behavior.
