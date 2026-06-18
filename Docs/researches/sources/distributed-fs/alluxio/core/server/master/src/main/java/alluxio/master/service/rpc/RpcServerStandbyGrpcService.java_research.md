# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/service/rpc/RpcServerStandbyGrpcService.java

Purpose: always-bound RPC service variant for standby gRPC mode. It serves standby endpoints while standby and restarts the server with primary endpoints on promotion.

Important APIs/types/functions: overrides `isServingLeader`, `isServingStandby`, `start`, `stop`, `promote`, and `demote`; owns boolean `mIsPromoted`.

Control flow: `start` immediately starts a gRPC server using `Master::getStandbyServices` and no rejecting server. `promote` rejects double promotion, stops current server and executor, waits for the port to free, starts primary services with `Master::getServices`, then marks promoted. `demote` performs the inverse and restarts standby services. `stop` shuts down server/executor and clears the promoted flag.

State and persistence: serving mode is in `mIsPromoted` plus inherited `mGrpcServer`. No persistence.

Dependencies/integration: selected by `RpcServerService.Factory` when `STANDBY_MASTER_GRPC_ENABLED` is true. Uses the same `MasterProcess` and registry server construction as the base class.

Risks: every promotion/demotion restarts the server, so active standby RPCs are interrupted during state changes. Preconditions reject repeated state transitions rather than making them idempotent. Safe-mode notification occurs inside inherited `startGrpcServer` for both standby and primary starts.

Test signals: `RpcServerStandbyGrpcServiceTest` should cover standby serving after start, leader serving after promote, restart back to standby after demote, double transition failures, and stop cleanup.
