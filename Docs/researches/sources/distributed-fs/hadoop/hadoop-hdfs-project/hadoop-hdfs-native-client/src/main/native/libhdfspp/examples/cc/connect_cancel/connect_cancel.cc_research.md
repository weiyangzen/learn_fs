# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/connect_cancel/connect_cancel.cc

## Purpose
This C++ example demonstrates canceling libhdfs++ filesystem connection attempts from a SIGINT handler while preserving orderly cleanup.

## Important APIs, Control Flow, and State
A global `std::shared_ptr<hdfs::FileSystem> fs` is visible to the signal handler. `main` loads default HDFS configuration into `Options`, creates an `IoService`, starts default workers, constructs `FileSystem::New(service, "", options)`, and calls `ConnectToDefaultFs`. The signal handler writes directly to stdout and calls `fs->CancelPendingConnect`, which should cause pending connect callbacks to complete with cancellation. Cleanup resets `fs`, stops the service, clears optional config, and shuts down protobuf.

## Dependencies and Integration Points
It uses public `hdfspp.h`, internal configuration loader headers, x-platform syscall wrappers, threads/signals, and protobuf cleanup. It models the async runtime lifecycle even though connect is invoked synchronously.

## Risks and Test Signals
The comments acknowledge signal-handler reentrancy hazards. Cancellation from an async signal while C++ objects are mutating is risky. Tests should cover no args, worker initialization failure, missing/default config, connection success/failure, SIGINT during connect, service stop after cancellation, and leak checks.
