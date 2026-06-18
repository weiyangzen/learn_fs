# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/fairness/RouterRpcFairnessConstants.java

Purpose: constants holder for Router RPC fairness.

Important APIs and types: exposes `CONCURRENT_NS = "concurrent"` and has a protected hidden constructor.

Control flow: no runtime logic.

State and persistence: no state.

Dependencies and integration points: `CONCURRENT_NS` is shared by static, proportional, and async policies to represent fan-out/concurrent Router calls.

Risks: string changes would break configuration, metrics, and policy special cases. Tests indirectly verify this through fairness policy allocation and metrics keys.
