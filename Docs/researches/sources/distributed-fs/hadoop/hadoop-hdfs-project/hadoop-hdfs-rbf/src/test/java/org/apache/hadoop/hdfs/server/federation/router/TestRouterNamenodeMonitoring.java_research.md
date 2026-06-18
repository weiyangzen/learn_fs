# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterNamenodeMonitoring.java

## Purpose

`TestRouterNamenodeMonitoring.java` tests Router monitoring of configured namenodes, JMX URL scheme/frequency behavior, and the router's merged datanode view across namespaces. It uses `MockNamenode` instances for two namespaces with two namenodes each. The source was read as a complete 437-line JUnit 5 test.

## Important APIs, Types, and Functions

Important APIs include `MockNamenode`, `Router`, `NamenodeHeartbeatService`, `MembershipNamenodeResolver`, `NamenodeStatusReport`, `LogVerificationAppender`, `HttpConfig.Policy`, `DatanodeInfoBuilder`, `DatanodeStorageReport`, `DFSClient.getDatanodeStorageReport`, and `DatanodeReportType.ALL`. Helpers are `getNamenodesConfig`, `testConfig`, `assertNamenodeHeartbeatService`, and overloaded `verifyUrlSchemes`.

## Control Flow

Setup creates mock namenodes and sets `nn0` active, `nn1` standby. `testNamenodeMonitoring` configures state store and resolver classes, monitors explicit `ns1` namenodes plus local `ns0.nn1`, starts a router, manually invokes all heartbeat services, reloads resolver cache, and asserts monitored records have newer modification times while unmonitored `ns0.nn0` does not. Config tests parse variations of the monitor-namenode list. JMX tests attach a log appender, build heartbeat services, call `getNamenodeStatusReport` one or more times, and count logged HTTP/HTTPS JMX URLs based on policy and configured interval. `testDatanodesView` registers mock subclusters, injects datanode views with conflicting admin states and timestamps, then asserts the router reports the most recent state per datanode UUID.

## State and Persistence Behavior

Mock namenode state, router state-store cache, heartbeat timestamps, and injected datanode reports are all in memory. The root log appender is modified during JMX tests. Cleanup stops all mock namenodes and the router after each test.

## Dependencies and Integration Points

This suite integrates router heartbeat configuration, membership resolver cache, state-store membership records, DFS HTTP policy, JMX status fetching frequency, datanode report aggregation, and mock namenode registration.

## Risks and Edge Cases

Modification-time assertions compare to `initializedTime`, so startup timing matters. Log appender assertions depend on debug log messages. JMX frequency tests infer requests from log counts rather than network calls. Datanode view merging depends on `lastUpdate` timestamps and duplicate UUID handling.

## Test Signals

Signals include expected monitored namenode set, newer timestamps only for monitored nodes, exact heartbeat service sets for config strings, HTTP versus HTTPS log counts, suppression of JMX when interval is negative, and merged datanode admin states (`dn0` decommissioned, `dn1` normal) based on newest reports.
