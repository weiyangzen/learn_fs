# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/fairness/StaticRouterRpcFairnessPolicyController.java

Purpose: static fairness policy that assigns fixed handler permits per nameservice from configuration and divides remaining handlers equally.

Important APIs and types: extends abstract semaphore controller; reads `DFS_ROUTER_HANDLER_COUNT_KEY` and `DFS_ROUTER_FAIR_HANDLER_COUNT_KEY_PREFIX`; uses `FederationUtil.getAllConfiguredNS` and `CONCURRENT_NS`; exposes `ERROR_MSG` for insufficient handler allocation.

Control flow: initialization gets total handler count, adds concurrent namespace, validates that dedicated counts plus one minimum for unassigned namespaces fit within total handlers, inserts dedicated permits, divides remaining permits among unassigned namespaces, and assigns leftovers to `CONCURRENT_NS`.

State and persistence: in-memory semaphore counts derived from configuration. The assignment is static until controller refresh/restart.

Dependencies and integration points: used by Router RPC fairness admission control when operators want predictable per-namespace handler pools.

Risks: unknown nameservices are not supported by the base class. If `CONCURRENT_NS` receives dedicated permits and leftovers, it is reinserted with a combined permit count. Integer division can allocate zero only after validation prevents impossible minimums. Tests should verify validation failures, dedicated counts, equal split, leftover assignment, and available-permit metrics.
