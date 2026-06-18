# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/router/TestRouterNamenodeHeartbeat.java

## Purpose

`TestRouterNamenodeHeartbeat.java` validates the service that heartbeats namenode status into the Router's active namenode resolver. It covers service lifecycle, local namenode heartbeat creation, HA active/standby updates, HA service-protocol address selection, DNS resolution expansion, and secure heartbeat registration. The source was read as a complete 365-line JUnit 5 test.

## Important APIs, Types, and Functions

Important APIs include `MiniRouterDFSCluster`, `NamenodeHeartbeatService`, `ActiveNamenodeResolver`, `MockResolver`, `FederationNamenodeContext`, `Router.createLocalNamenodeHeartbeatService`, `Router.createNamenodeHeartbeatServices`, `DFSUtil`, `MockDomainNameResolver`, and `SecurityConfUtil`. Helpers include `globalSetUp`, `testNamenodeHeartbeatServiceHAServiceProtocol`, and `generateNamenodeConfiguration`.

## Control Flow

Global setup starts an HA mini-cluster with two nameservices, creates a `MockResolver`, and starts one heartbeat service per namenode. Lifecycle tests instantiate a service and assert INITED/STARTED/STOPPED transitions. Local heartbeat tests check no service without a local nameservice and a service description when local HA keys are configured. `testHearbeat` forces `nn0` active, waits for periodic heartbeats, checks active/standby order, performs a failover in one namespace, waits again, and validates only that namespace changes. Address-selection tests generate configs with RPC, service RPC, and lifeline RPC ports and assert chosen health monitor addresses. Secure heartbeat test starts a secure mini-cluster and verifies resolver namespaces are populated.

## State and Persistence Behavior

Heartbeat services write in-memory resolver records in `MockResolver` or router resolver state. Global services are started once and closed at teardown. Secure test resets `UserGroupInformation` and destroys security config in `finally`.

## Dependencies and Integration Points

This file integrates HA namenode state, router heartbeat services, local namenode detection, domain-name resolution, health monitor target construction, Java-version-sensitive unresolved address formatting, and secure MiniRouterDFSCluster registration.

## Risks and Edge Cases

`testHearbeat` uses fixed five-second sleeps, which can be slow or timing-sensitive. Address string expectations branch on Java 14+ unresolved-address formatting. Secure test must reset global UGI state. The typo in `testHearbeat` is harmless but visible in method naming.

## Test Signals

Signals include service state transitions, null/non-null local heartbeat creation, correct active/standby ordering before and after failover, expected health monitor address precedence from lifeline/service/RPC ports, resolved namenode descriptions for multiple host expansions, and non-empty resolver namespaces under security.
