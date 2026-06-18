# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/fairness/NoRouterRpcFairnessPolicyController.java

Purpose: pass-through fairness policy that disables admission limiting.

Important APIs and types: implements `RouterRpcFairnessPolicyController`; constructor accepts `Configuration` only for reflection/configuration compatibility.

Control flow: `acquirePermit` always returns true; `releasePermit` and `shutdown` do nothing; reporting returns `"N/A"`, `0` permits, and `contains` always true.

State and persistence: no state.

Dependencies and integration points: selected when Router fairness should not limit downstream namespace calls, while still satisfying the controller interface used by RPC client and metrics.

Risks: metrics can show zero available permits while all calls are allowed, which must be understood by operators. Tests should verify it is safe for arbitrary ns IDs and does not throw on release or shutdown.
