# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/ha/DummyHAService.java

Purpose: test-only `HAServiceTarget` implementation used by failover and health-monitor tests. It can operate as an in-process Mockito-spied protocol implementation or through protobuf RPC, and exposes knobs for injected failures.

Important APIs and types: `HAServiceTarget`, `HAServiceProtocol`, `ZKFCProtocol`, `NodeFencer`, `FenceMethod`, `HAServiceState`, `HAServiceStatus`, `StateChangeRequestInfo`, `ServiceFailedException`, `HealthCheckFailedException`, `RPC.Builder`, `ProtobufRpcEngine2`, `HAServiceProtocolServerSideTranslatorPB`, and `DummySharedResource`.

Control flow: constructors set initial state, optionally start protobuf RPC servers, create protocol spies, create a spy `NodeFencer`, and register the instance in a static list. `getProxy` and `getHealthMonitorProxy` return spies or refresh RPC proxies. `MockHAProtocolImpl` implements health checks, transitions to active/standby/observer, service status, and simulated unreachable behavior. Active transition increments `activeTransitionCount`, may take a shared resource, and changes state. Standby transition may release the shared resource. `DummyFencer.tryFence` increments `fenceCount`, optionally fails, and releases the shared resource.

State and persistence: volatile HA state, failure flags, counters, static instance registry, optional RPC servers, and shared-resource ownership are all test state.

Dependencies and integration: central test double for HA admin, failover controller, fencing, health monitor, observer support, and protobuf RPC paths.

Risks and test signals: important risks are static instance leakage across tests, RPC server lifecycle not explicitly closed, failure flags masking real behavior, and `getHealthMonitorProxy` assigning to `proxy` rather than `healthMonitorProxy`. Shared resource assertions catch split-brain style active ownership.
