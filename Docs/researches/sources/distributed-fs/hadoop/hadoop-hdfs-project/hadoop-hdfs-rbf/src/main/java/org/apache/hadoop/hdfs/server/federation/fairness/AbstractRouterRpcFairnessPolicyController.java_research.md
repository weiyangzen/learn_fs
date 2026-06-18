# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/fairness/AbstractRouterRpcFairnessPolicyController.java

Purpose: base semaphore-backed implementation of Router RPC fairness permits by nameservice.

Important APIs and types: implements `RouterRpcFairnessPolicyController`; fields `Map<String, Semaphore> permits` and `acquireTimeoutMs`; methods `init`, `acquirePermit`, `releasePermit`, `shutdown`, `insertNameServiceWithPermits`, `getAvailablePermits`, `getAvailableHandlerOnPerNs`, and `contains`.

Control flow: `init` creates the permit map and reads `DFS_ROUTER_FAIRNESS_ACQUIRE_TIMEOUT`, falling back on invalid negative values. `acquirePermit` performs timed `Semaphore.tryAcquire`. `releasePermit` releases one permit. `shutdown` drains all semaphores. JSON reporting iterates permits and writes available counts with Jettison.

State and persistence: all state is in-memory semaphore counts. There is no persistence across Router restart; policy subclasses reconstruct permits from configuration.

Dependencies and integration points: used by static, proportional, and async fairness policies. Integrated with Router RPC client admission control and metrics/JMX available-handler reporting.

Risks: no null checks around `permits.get(nsId)` mean unknown nameservices cause `NullPointerException` unless subclasses handle them. Release without a matching acquire can over-increment permits. Tests should verify timeout behavior, shutdown drain, JSON output, invalid timeout config, and release/acquire balance under concurrency.
