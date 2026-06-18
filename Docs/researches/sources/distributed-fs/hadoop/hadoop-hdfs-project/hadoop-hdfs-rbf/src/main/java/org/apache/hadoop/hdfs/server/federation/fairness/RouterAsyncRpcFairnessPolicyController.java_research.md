# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/fairness/RouterAsyncRpcFairnessPolicyController.java

Purpose: async-RPC-oriented fairness policy that limits outstanding async calls per configured nameservice.

Important APIs and types: extends the abstract semaphore controller; reads `DFS_ROUTER_ASYNC_RPC_MAX_ASYNCCALL_PERMIT_KEY`; uses configured nameservices plus `CONCURRENT_NS`; overrides `acquirePermit` and `releasePermit`.

Control flow: initialization validates the max-permit value, falling back to default when nonpositive, then inserts that permit count for every configured namespace and for the concurrent namespace. `CONCURRENT_NS` acquire/release is a no-op allowed path; all other namespaces use normal semaphore acquisition.

State and persistence: in-memory semaphore permits only. Counts are reconstructed from configuration on controller creation/refresh.

Dependencies and integration points: recommended when Router async RPC is enabled and consumed by Router RPC client permit checks plus metrics reporting.

Risks: unknown non-concurrent nameservices are not handled and can NPE in the base class. Concurrent fan-out calls bypass permit limiting by design. Tests should cover invalid permit config, configured namespaces, concurrent namespace bypass, and missing namespace behavior.
