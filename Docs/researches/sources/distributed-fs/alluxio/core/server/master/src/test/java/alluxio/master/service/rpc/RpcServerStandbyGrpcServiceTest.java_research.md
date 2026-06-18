# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/service/rpc/RpcServerStandbyGrpcServiceTest.java

## Purpose
`RpcServerStandbyGrpcServiceTest` verifies RPC service lifecycle when standby master gRPC is enabled. In this mode the real gRPC server remains serving in both standby and primary states.

## Important APIs, Types, and Functions
The class extends `RpcServerServiceTestBase` and uses `RpcServerService.Factory.create`, lifecycle methods, `isServing`, and socket helpers. `setUp` reloads configuration, sets `STANDBY_MASTER_GRPC_ENABLED=true`, then delegates to the base setup.

## Control Flow, State, and Persistence
`primaryOnlyTest` creates the service, starts it, and asserts the socket is bound and `isServing` is true immediately. Promote and demote cycles keep both the port binding and serving flag true. Stop clears serving state and releases the port. `doubleStartRpcServer` checks that double promotion and double demotion are rejected.

## Dependencies and Integration Points
This test integrates with the same mocked master-process gRPC builder as the base, but covers the always-on standby gRPC configuration branch.

## Risks
It relies on global configuration reload to isolate from other tests. Socket release timing remains a CI risk. Literal exception messages are part of the assertion contract.

## Test Signals
Passing tests show that standby gRPC keeps the server available across role transitions and that invalid duplicate promote/demote calls fail rather than silently corrupting lifecycle state.
