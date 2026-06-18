# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/grpc/GrpcDataServer.java

## Purpose
`GrpcDataServer` starts and owns the worker data gRPC server for block operations. It configures Netty transport, RPC executor, service method overrides, flow control, keepalive, message size, and graceful shutdown.

## Important APIs, Types, and Functions
The constructor builds `BlockWorkerClientServiceHandler`, applies zero-copy descriptor overrides, starts a `GrpcServer`, and records domain-socket bind addresses. `createServerBuilder()` creates the worker RPC executor, registers queue/thread gauges, creates boss/worker event loop groups, chooses channel class, configures epoll mode, pooled allocator, and Netty watermarks. `close()` shuts down the filesystem context, server, event loops, and RPC executor. `getBindAddress()`, `isClosed()`, and `awaitTermination()` implement `DataServer`.

## Control Flow, State, and Persistence
Server state is process-local: socket address, event loop groups, gRPC server, optional domain socket address, and RPC executor. It does not store blocks, but all block IO reaches `DefaultBlockWorker` through the registered service.

## Dependencies and Integration Points
It integrates worker process services, `GrpcServerBuilder`, `GrpcSerializationUtils`, `BlockWorkerClientServiceHandler`, `ExecutorServiceBuilder`, Netty event loops/channels/options, metrics, `FileSystemContext`, and Alluxio network configuration.

## Risks and Test Signals
Risks include startup failures becoming runtime exceptions, shutdown ordering, event-loop shutdown timeouts, domain-socket address reporting, integer casts for configured byte sizes, and executor leak on partial construction failure. Tests should cover TCP and domain-socket startup, zero-copy service registration, close idempotence, bind-port reporting, and metric gauge registration.
