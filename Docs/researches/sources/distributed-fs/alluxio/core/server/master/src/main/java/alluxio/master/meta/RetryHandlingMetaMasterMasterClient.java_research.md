# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/meta/RetryHandlingMetaMasterMasterClient.java

## Purpose
`RetryHandlingMetaMasterMasterClient` is the standby master's retrying gRPC client for leader meta-master master-service RPCs. It wraps ID allocation, heartbeat, and registration calls with `AbstractMasterClient` retry/reconnect behavior.

## Important APIs and Types
- Extends `AbstractMasterClient`.
- Creates `MetaMasterMasterServiceGrpc.MetaMasterMasterServiceBlockingStub` in `afterConnect`.
- `getRemoteServiceType`, `getServiceName`, and `getServiceVersion` identify the target service.
- `getId(Address)` calls `getMasterId`.
- `heartbeat(long)` sends journal checkpoint metrics when available and returns `MetaCommand`.
- `register(long, List<ConfigProperty>)` sends config, version, revision, start time, and last lose-primacy time when gauges exist.

## Control Flow
Each public RPC uses `retryRPC`, so connection failures are retried according to `AbstractMasterClient` policy. `heartbeat` reads Dropwizard gauges from `MetricsSystem.METRIC_REGISTRY` and conditionally populates `MasterHeartbeatPOptions`. `register` similarly reads start/lose-primacy gauges and includes build metadata from `ProjectConstants`.

## State and Persistence
The client keeps only the current blocking stub. All persisted/cluster state is updated remotely on the leader meta master.

## Dependencies and Integration Points
Used by `MetaMasterSync`. Depends on generated gRPC stubs, `MasterClientContext`, `MetricsSystem`, metric keys, Alluxio constants, and wire addresses.

## Risks and Edge Cases
- Gauge values are cast to `long`; unexpected gauge value types would fail at runtime.
- Missing gauges are tolerated and omitted.
- Thread-safety follows `AbstractMasterClient`; the stub field is replaced after connect.

## Test Signals
Tests should mock the blocking stub/retry layer and verify request payloads, optional metric fields, service identity values, retries on transient failures, and registration metadata.
