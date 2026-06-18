# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockMasterWorkerServiceTestUtils.java

## Purpose
`BlockMasterWorkerServiceTestUtils` provides test helpers for creating gRPC servers with a single service and channels to those servers.

## Important APIs, Types, and Functions
`createServerWithService(serviceType, handler, address)` uses global configuration; the overload accepts an explicit `AlluxioConfiguration`. Both build a `GrpcServer` with `GrpcServerAddress` and `GrpcService`. `createChannel(address)` and its overload build `GrpcChannel`s for a socket address and configuration.

## Control Flow, State, and Persistence
The helpers construct server/channel objects but do not start or close them automatically. Tests manage lifecycle.

## Dependencies and Integration Points
It integrates `GrpcServerBuilder`, `GrpcChannelBuilder`, `GrpcServerAddress`, `GrpcService`, `ServiceType`, Alluxio configuration, and gRPC `BindableService`.

## Risks and Test Signals
Risks include tests leaking servers/channels if callers do not close them, and helper defaults masking configuration-sensitive behavior. Useful tests assert callers start/shutdown servers and use explicit configs for auth or retry scenarios.
