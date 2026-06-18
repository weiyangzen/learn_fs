# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/rpc/RpcServerService.java

Purpose: primary-only master RPC service lifecycle manager. It binds a rejecting server while standby, starts the real gRPC server on promotion, and cleans up server/executor resources on demotion or stop.

Important APIs/types/functions: `start`, `promote`, `demote`, `stop`, `startGrpcServer`, `stopGrpcServer`, `stopRpcExecutor`, `startRejectingServer`, `stopRejectingServer`, `isServing`, `isServingLeader`, `isServingStandby`, static `waitFor`, and nested `Factory.create`.

Control flow: `start` launches a `RejectingServer` on the RPC bind address. `promote` stops the rejecting server, waits briefly for the port to become free, builds a gRPC server from `MasterProcess.createBaseRpcServer`, optionally installs the master RPC executor, registers all primary services from every master in `MasterRegistry`, starts the server, and notifies safe mode. `demote` shuts down gRPC and executor, waits for the port to free, then restarts the rejecting server. `stop` stops both possible server types and the executor.

State and persistence: guarded nullable fields hold `GrpcServer`, `AlluxioExecutorService`, and `RejectingServer`. No journal state. Runtime serving state is derived from server fields.

Dependencies/integration: integrates `MasterProcess`, `MasterRegistry`, `Master.getServices`, `SafeModeManager`, `GrpcServerBuilder`, `RejectingServer`, and master process service registration.

Risks: all lifecycle methods are synchronized but static socket polling can silently time out and proceed. `startGrpcServer` may partially create an executor before gRPC start fails; callers depend on later stop cleanup. Factory switches to `RpcServerStandbyGrpcService` when standby gRPC is enabled.

Test signals: `RpcServerServiceTest` and master process tests should cover rejecting-server binding, primary promotion service registration, safe-mode notification, executor shutdown, demote-to-rejecting behavior, stop idempotency, and port-free wait behavior.
