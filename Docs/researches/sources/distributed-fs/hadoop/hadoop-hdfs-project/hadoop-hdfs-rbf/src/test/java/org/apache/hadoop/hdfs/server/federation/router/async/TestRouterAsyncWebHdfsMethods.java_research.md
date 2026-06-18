# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/async/TestRouterAsyncWebHdfsMethods.java

Purpose: runs WebHDFS Router method tests with async RPC enabled.

Important APIs/types/functions: extends `TestRouterWebHdfsMethods`; uses `StateStoreDFSCluster`, `RouterConfigBuilder`, `RouterContext`, and `DFS_ROUTER_ASYNC_RPC_ENABLE_KEY`. The superclass supplies HTTP request construction, file verification, mount table creation, namespace parsing, and invalid-path JSON checks.

Control flow: `globalSetUp()` creates a two-nameservice state-store cluster with RPC, HTTP, admin, and async RPC enabled, sets independent DNs, starts cluster/routers, waits for readiness, selects a router, and records the HTTP URI. Inherited tests then perform WebHDFS create operations and path validation through the async-enabled router.

State and persistence behavior: inherited tests create files in physical nameservices and mount entries in the state store. Integration points include HTTP/WebHDFS frontend, async router RPC backend, mount resolution, and invalid path exception serialization. Risks mirror the superclass plus the possibility that HTTP request handling hides async backend failures until response time. Test signals are inherited HTTP status codes, namespace file existence checks, network-location parsing, and JSON remote exception validation.
