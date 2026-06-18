# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/ioservice.h

## Purpose
`IoService` is the public async execution abstraction for libhdfs++, wrapping Boost.Asio `io_service` and documenting lifecycle/concurrency constraints.

## Important APIs, Control Flow, and State
Factory methods create raw or shared instances. Worker APIs initialize default or specified thread counts, add workers, and report count. `PostTask`/`PostLambda` enqueue deferred work, `Run` processes tasks, `Stop` stops workers, and `GetRaw` exposes the underlying `boost::asio::io_service` for Asio calls. The header explicitly warns that tasks and dependencies must outlive pending work, callbacks must avoid blocking IO/sleep and long-held locks, exceptions should not escape, and TLS should not be relied on for affinity.

## Dependencies and Integration Points
`FileSystem` can own or share an `IoService`, and nearly all async operations run through it. It depends on Boost.Asio, functional, memory, and `enable_shared_from_this`.

## Risks and Test Signals
Dangling references, blocked worker threads, callback exception handling, and stopped service behavior are central risks. Tests should cover worker counts, posting before/after stop, shared lifetime, exception capture/logging, direct raw Asio use, and async operation completion under concurrent workers. The `DISABLE_CONCURRENT_WORKERS` define should be validated or removed intentionally.
