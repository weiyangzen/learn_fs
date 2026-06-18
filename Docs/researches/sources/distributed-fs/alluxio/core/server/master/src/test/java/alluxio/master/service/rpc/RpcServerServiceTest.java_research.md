# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/service/rpc/RpcServerServiceTest.java

## Purpose
`RpcServerServiceTest` verifies RPC service lifecycle when standby master gRPC is disabled. In this mode, standby binds a rejecting server while the real RPC server only serves in primary state.

## Important APIs, Types, and Functions
The suite extends `RpcServerServiceTestBase` and uses `RpcServerService.Factory.create`, `start`, `promote`, `demote`, `stop`, `isServing`, `isGrpcBound`, and `waitForFree`. It configures `STANDBY_MASTER_GRPC_ENABLED=false`.

## Control Flow, State, and Persistence
`before` disables standby gRPC. `primaryOnlyTest` creates a service on a reserved port, confirms the socket is free, starts the service, and asserts the port is bound but not serving. Repeated promote/demote cycles toggle `isServing` while the port remains bound. Stop unbinds the port. Double-start tests assert that starting the rejecting server twice and promoting the RPC server twice throw `IllegalStateException`.

## Dependencies and Integration Points
The test uses PowerMock/Mockito through the base class to mock `AlluxioMasterProcess`, create a `GrpcServerBuilder`, and avoid real master services. It touches master registry, port reservation, sockets, and gRPC server lifecycle.

## Risks
Socket probing can be flaky on slow CI or systems with delayed port release. The asserted exception messages are literal and can drift with implementation wording.

## Test Signals
Passing tests show that standby-without-gRPC still occupies the RPC port with a rejecting server, primary promotion swaps into serving mode, demotion stops serving without freeing the socket, and duplicate lifecycle calls are rejected.
