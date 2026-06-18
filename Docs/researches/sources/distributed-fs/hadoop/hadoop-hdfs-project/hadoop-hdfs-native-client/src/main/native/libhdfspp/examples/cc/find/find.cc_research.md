# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/find/find.cc

## Purpose
This example implements a parallel-capable HDFS find tool using libhdfs++ synchronous and asynchronous `FileSystem::Find`.

## Important APIs, Control Flow, and State
`SyncFind` calls `fs->Find(path, name, defaultDepth, &results)` and prints `StatInfo::full_path`. `AsyncFind` creates a promise/future, captures status and a found flag, and registers a callback that prints batches, records the first error, resolves the promise on the final batch, and returns whether more results are wanted. `main` parses path, name, and `use_async`, connects with `doConnect(uri, true)`, dispatches sync or async, and shuts down protobuf.

## Dependencies and Integration Points
It uses `hdfspp/hdfspp.h`, `tools_common.h`, `std::future`, and protobuf cleanup. It demonstrates the batched callback contract for `Find`, including the callback's boolean continuation result.

## Risks and Test Signals
`std::stoi` can throw for invalid async flags. Async state is captured by reference and relies on the callback finishing before locals leave, enforced by `future.get`. Tests should cover no results, multiple batches, callback stop behavior, errors after partial results, invalid arguments, wildcard paths/names, and max-depth defaults.
