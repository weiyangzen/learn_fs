# sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/DataServer.java

Purpose: `DataServer` defines the minimal lifecycle and address contract for a worker data protocol server.

Important APIs are `getBindAddress`, `isClosed`, `awaitTermination`, and inherited `Closeable.close`. Implementations may bind either an `InetSocketAddress` or Netty `DomainSocketAddress`, as documented by `getBindAddress`. Control flow is implementation-specific; `AlluxioWorkerProcess` uses it to expose data host/port, optional domain socket path, block on server termination during `start`, and close servers during shutdown.

State and persistence are implementation-owned network server resources. Dependencies are Java networking and closeable APIs. Integration points include `GrpcDataServer` and worker lifecycle code. Risks include callers casting bind addresses based on which server is being queried; misuse can cause `ClassCastException`. No direct tests in this subset cover the interface.
