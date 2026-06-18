# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/fairness/ProportionRouterRpcFairnessPolicyController.java

Purpose: fairness policy assigning per-nameservice permits as a configured proportion of the Router handler count.

Important APIs and types: extends the abstract semaphore controller; uses `DFS_ROUTER_HANDLER_COUNT_KEY`, `DFS_ROUTER_FAIR_HANDLER_PROPORTION_KEY_PREFIX`, default proportion config, `FederationUtil.getAllConfiguredNS`, special `CONCURRENT_NS`, and internal `DEFAULT_NS`.

Control flow: initialization gathers configured nameservices, adds concurrent and default namespaces, calculates `int(proportion * handlerCount)`, enforces at least one permit per entry, and inserts semaphores. `acquirePermit` and `releasePermit` route unknown namespaces to `DEFAULT_NS`.

State and persistence: in-memory semaphore counts derived from static configuration at initialization. No runtime persistence.

Dependencies and integration points: supports clusters where new or unregistered namespaces should share default permits instead of failing. Exposed through Router RPC fairness metrics.

Risks: proportions are not normalized, so total allocated permits can exceed handler count. Truncation can under-allocate small proportions, then the minimum-one rule can over-allocate. Tests should cover unknown namespaces, default fallback release symmetry, zero/negative proportions, and aggregate allocation expectations.
