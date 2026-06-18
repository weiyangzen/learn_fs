# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterNamenodeWebScheme.java

## Purpose

`TestRouterNamenodeWebScheme.java` verifies that namenode web schemes reported through the Router honor `dfs.http.policy`, specifically HTTP-only and HTTPS-only configurations. The source was read as a complete 204-line JUnit 5 test.

## Important APIs, Types, and Functions

The test uses `MockNamenode`, `Router`, `NamenodeHeartbeatService`, `MembershipNamenodeResolver`, `FederationNamenodeContext`, `HttpConfig.Policy`, `RouterConfigBuilder`, and state-store resolver configuration. Key methods are `setup`, `cleanup`, `getNamenodesConfig`, `testWebSchemeHttp`, `testWebSchemeHttps`, and `testWebScheme`.

## Control Flow

Setup creates two namespaces with active/standby mock namenodes. `testWebScheme` builds namenode configuration, configures router heartbeat/state-store/RPC with the requested HTTP policy, monitors `ns1` plus local `ns0.nn1`, starts the router, manually invokes heartbeat services, reloads the membership resolver cache, gathers all namespace reports, and asserts every report has the expected web scheme string.

## State and Persistence Behavior

Membership reports are written to the router's in-memory/state-store-backed resolver cache during heartbeat invocation. Mock namenodes and router are stopped after each test.

## Dependencies and Integration Points

This checks the integration between DFS HTTP policy, namenode heartbeat status reports, membership resolver records, and web address scheme rendering in router-visible namespace metadata.

## Risks and Edge Cases

Only `HTTP_ONLY` and `HTTPS_ONLY` are covered, not mixed policies. The test does not open actual web URLs; it validates reported scheme fields. All reports are expected to share the same scheme regardless of namespace or active/standby role.

## Test Signals

Signals are resolver reports for all configured namespaces and exact `getWebScheme()` equality to `http` or `https` depending on policy.
