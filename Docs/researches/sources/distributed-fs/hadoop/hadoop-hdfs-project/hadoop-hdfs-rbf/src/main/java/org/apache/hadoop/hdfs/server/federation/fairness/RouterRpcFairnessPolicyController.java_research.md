# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/fairness/RouterRpcFairnessPolicyController.java

Purpose: policy interface for Router RPC downstream nameservice admission control.

Important APIs and types: declares `acquirePermit`, `releasePermit`, `shutdown`, `getAvailableHandlerOnPerNs`, `getAvailablePermits`, and `contains`.

Control flow: implementations decide whether a Router handler may proceed to a downstream NameNode for a namespace. Callers are expected to acquire before proxying and release afterward.

State and persistence: interface has no state. Implementations may keep in-memory semaphores or be pass-through.

Dependencies and integration points: used by Router RPC client code and exposed in JMX/RPC metrics for available handler and permit rejection/acceptance reporting.

Risks: the contract relies on balanced acquire/release calls and consistent namespace IDs. Tests for implementations should include success, rejection, unknown namespace, shutdown, and metrics-reporting behavior.
