# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/HAServiceProtocol.proto

## Purpose
`HAServiceProtocol.proto` defines Hadoop's protobuf RPC contract for high-availability service control and health/status checks. It is used by HA admin tooling and failover controllers.

## Important APIs, types, and functions
Enums are `HAServiceStateProto` (`INITIALIZING`, `ACTIVE`, `STANDBY`, `OBSERVER`) and `HARequestSource` (`REQUEST_BY_USER`, forced user request, and `REQUEST_BY_ZKFC`). Messages include `HAStateChangeRequestInfoProto`, health monitor request/response, transition request/response pairs for active, standby, and observer, and `GetServiceStatusResponseProto` with state, readiness, and not-ready reason. The service exposes `monitorHealth`, `transitionToActive`, `transitionToStandby`, `transitionToObserver`, and `getServiceStatus`.

## Control flow
Clients issue health checks, status requests, or state transition requests carrying request-source metadata. Servers enforce HA semantics and return empty responses for successful transitions or status metadata for queries. Generated protobuf service stubs carry this contract over Hadoop IPC.

## State and persistence
The schema represents transient control-plane calls. Actual HA state is persisted or coordinated by the HA implementation, not by the proto. Required fields make transition request source and status state mandatory on the wire.

## Dependencies and integration points
It generates `org.apache.hadoop.ha.proto.HAServiceProtocolProtos` and integrates with `HAServiceProtocol`, `HAAdmin`, health monitors, and ZK failover controller code.

## Risks and test signals
Risks include changing enum values, missing observer support in older clients, incorrect handling of forced requests, and readiness fields being absent. Test signals include HA protocol translator tests, mixed-version clients, transitions from user and ZKFC sources, observer transition coverage, and health-monitor failure propagation.
