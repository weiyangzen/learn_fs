# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/service/rpc/RpcServerServiceTestBase.java

## Purpose
`RpcServerServiceTestBase` provides shared fixtures for RPC simple-service tests. It reserves a port, mocks an `AlluxioMasterProcess`, and supplies socket helpers for testing whether the gRPC endpoint is bound.

## Important APIs, Types, and Functions
The base exposes `mPort`, `mRegistry`, `mRpcAddress`, and `mMasterProcess`. `setUp` stubs `createBaseRpcServer`, `createRpcExecutorService`, and `getSafeModeManager`. Helper methods are `isGrpcBound`, `isBound`, and `waitForFree`.

## Control Flow, State, and Persistence
Before each subclass test, a reserved port is converted to an `InetSocketAddress`, and the mocked master process returns a `GrpcServerBuilder` for that address with global configuration. Socket checks attempt a TCP connection to the reserved address. `waitForFree` polls until no connection can be made or a one-second timeout expires. There is no persistence.

## Dependencies and Integration Points
The base integrates JUnit `PortReservationRule`, Mockito/PowerMockito, Alluxio `GrpcServerBuilder`, `GrpcServerAddress`, `MasterRegistry`, and `CommonUtils.waitFor`.

## Risks
The helper treats any non-`ConnectException` I/O error as a runtime failure. Address binding uses `address.getAddress()` and port, so unresolved or unusual host handling could affect socket checks. The one-second wait can be short on heavily loaded systems.

## Test Signals
The base is indirectly covered by both standby-disabled and standby-enabled RPC service tests. Reliable socket-free and socket-bound checks are required for those suites to be meaningful.
