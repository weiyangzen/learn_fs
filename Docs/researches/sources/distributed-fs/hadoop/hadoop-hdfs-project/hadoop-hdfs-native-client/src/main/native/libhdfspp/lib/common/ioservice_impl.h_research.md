<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/ioservice_impl.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/ioservice_impl.h

## Purpose
Declares `IoServiceImpl`, the concrete libhdfspp `IoService` implementation backed by Boost.Asio and owned worker threads.

## Important APIs, Types, And Functions
The class overrides worker initialization, task posting, run/stop, raw Asio access, worker addition, and worker count. It uses `MEMCHECKED_CLASS`, `state_lock_`, `io_service_`, and `WorkerPtr` with `WorkerDeleter`.

## Control Flow
Runtime behavior is implemented in `ioservice_impl.cc`; this header establishes the inheritance and ownership model.

## State And Persistence
State is in-memory Asio runtime and worker thread ownership. No durable state exists.

## Dependencies And Integration Points
Included by components that need the concrete `GetRaw()` Asio service for sockets/resolvers. The public base interface lives in `hdfspp/ioservice.h`.

## Risks
Because `GetRaw()` exposes the underlying service, callers can post operations that bypass wrapper invariants. Worker-thread lifetime is tied to object destruction and must be coordinated with filesystem shutdown.

## Test Signals
Compile and integration tests should instantiate through both `New` and `MakeShared`, use raw Asio sockets/resolvers, and validate worker shutdown behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/ioservice_impl.h -->
