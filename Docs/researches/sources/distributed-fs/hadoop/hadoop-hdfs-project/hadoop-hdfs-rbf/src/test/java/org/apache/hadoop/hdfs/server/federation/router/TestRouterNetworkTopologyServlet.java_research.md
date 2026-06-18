# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterNetworkTopologyServlet.java

## Purpose

`TestRouterNetworkTopologyServlet.java` verifies the Router HTTP `/topology` endpoint in synchronous and asynchronous RPC modes, for text and JSON responses, with and without datanodes. It also defines a JUnit extension that starts and tears down the appropriate test clusters for nested parameterized classes. The source was read as a complete 319-line JUnit 5 test.

## Important APIs, Types, and Functions

Important APIs include `StateStoreDFSCluster`, `MultipleDestinationMountTableResolver`, `RouterConfigBuilder`, `DFS_ROUTER_HTTP_ENABLE`, `DFS_ROUTER_ASYNC_RPC_ENABLE_KEY`, `HttpURLConnection`, Jackson `ObjectMapper`/`JsonNode`, `IOUtils.copyBytes`, nested test classes, and `RouterServerHelper` implementing `BeforeEachCallback` and `AfterAllCallback`. Core helper methods are `setUp`, `testPrintTopologyTextFormat`, `testPrintTopologyJsonFormat`, `testPrintTopologyNoDatanodesTextFormat`, and `testPrintTopologyNoDatanodesJsonFormat`.

## Control Flow

For each RPC mode, `RouterServerHelper.beforeEach` inspects the parameterized method's `ValueSource` and calls `setUp` once. Setup builds one federated cluster with nine datanodes per nameservice and explicit racks, and another with zero datanodes. Text tests call `/topology` and assert rack path strings and the count of `127.0.0.1` occurrences. JSON tests send `Accept: application/json`, parse the response, assert six racks, and count datanode entries. No-datanode tests call the same endpoint on the empty cluster and assert `"No DataNodes"` in text or JSON-response content. `afterAll` shuts down both clusters and clears thread-local state.

## State and Persistence Behavior

Static cluster fields hold the active topology clusters for each nested class run. Router HTTP state is in-process. The helper stores itself in an inheritable thread-local but removes it at teardown. There is no durable persistence.

## Dependencies and Integration Points

This test integrates Router HTTP server, network topology servlet, router sync/async RPC modes, datanode rack metadata aggregation across namespaces, JSON serialization, and JUnit 5 nested parameterized extension behavior.

## Risks and Edge Cases

URL construction uses `"http:/" + httpAddress + "/topology"`, relying on `httpAddress` string formatting. Static clusters require reliable `afterAll` cleanup. JSON no-datanode output is checked as text rather than parsed JSON. The datanode count assertion in text mode depends on host string repetition.

## Test Signals

Signals include expected rack labels `/ns0/rack1` through `/ns1/rack6`, eighteen datanode entries for populated clusters, six JSON rack nodes, `"No DataNodes"` for empty clusters, and identical behavior under async and sync router RPC.
