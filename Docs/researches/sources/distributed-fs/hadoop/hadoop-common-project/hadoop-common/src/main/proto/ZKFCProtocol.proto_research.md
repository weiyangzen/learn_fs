# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/proto/ZKFCProtocol.proto

## Purpose
`ZKFCProtocol.proto` defines the protobuf RPC contract for controlling a ZooKeeper Failover Controller. It supports ceding active leadership for a duration and requesting graceful failover.

## Important APIs, types, and functions
`CedeActiveRequestProto` has required `millisToCede`. `CedeActiveResponseProto`, `GracefulFailoverRequestProto`, and `GracefulFailoverResponseProto` are empty. `ZKFCProtocolService` exposes `cedeActive` and `gracefulFailover`.

## Control flow
Clients ask a ZKFC to step back from active election for the specified milliseconds or to coordinate graceful failover. The server performs coordination with HA state and ZooKeeper; success returns empty responses while failures surface as RPC exceptions.

## State and persistence
The proto carries a transient command. Actual failover coordination state lives in ZKFC and ZooKeeper, not in the message.

## Dependencies and integration points
It generates `org.apache.hadoop.ha.proto.ZKFCProtocolProtos` and integrates with Hadoop HA failover controllers, HA admin tooling, and `HAServiceProtocol`.

## Risks and test signals
Risks include invalid or extreme cede durations, unauthorized failover commands, race conditions with automatic election, and compatibility around empty messages. Test signals include ZKFC protocol translator tests, graceful failover integration tests, cede-active timing tests, and authorization checks.
