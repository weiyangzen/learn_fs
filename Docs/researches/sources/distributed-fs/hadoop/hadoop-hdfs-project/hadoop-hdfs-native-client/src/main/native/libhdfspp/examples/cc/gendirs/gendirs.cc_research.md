# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/gendirs/gendirs.cc

## Purpose
This C++ example asynchronously creates a generated HDFS directory tree with specified depth and fanout.

## Important APIs, Control Flow, and State
`GenerateDirectories` recursively descends until `level == depth`; at leaves it creates a `std::promise<hdfs::Status>`, stores the future in a vector, and calls `fs->Mkdirs(path, 0755, true, handler)`. `main` parses path/depth/fanout, connects through `doConnect(uri, true)`, starts generation at `path + "/"`, waits for every future, reports the first non-OK status by exiting, prints completion, and shuts down protobuf.

## Dependencies and Integration Points
It uses `FileSystem::Mkdirs` async callbacks, futures/promises, URI parsing/connection helpers, and protobuf cleanup.

## Risks and Test Signals
Unbounded fanout/depth can create exponential futures and RPCs; invalid numeric args throw. Path concatenation can produce duplicate slashes. Tests should cover depth 0, fanout 0/1/N, invalid args, creation failure, partial failures, and resource behavior under moderate parallelism.
