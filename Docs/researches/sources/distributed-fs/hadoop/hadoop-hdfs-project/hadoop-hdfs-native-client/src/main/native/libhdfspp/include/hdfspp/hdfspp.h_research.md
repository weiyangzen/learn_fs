# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/hdfspp.h

## Purpose
This is the primary public C++ libhdfs++ API. It declares datanode exclusion rules, file handles, filesystem construction, connection, file IO, metadata, namespace mutation, find, snapshot, event callback, and option inspection contracts.

## Important APIs, Control Flow, and State
`FileHandle` exposes async positional reads, sync positional/current reads, seeking, cancellation, file event callbacks, and byte counters. `FileSystem::New` constructs instances with owned or shared `IoService` plus user/options. Connection can target explicit server/service or `Options::defaultFS`, synchronously or asynchronously, and pending connects can be canceled. Filesystem methods provide async and sync variants for open, preferred block size, replication, times, stat, content summary, fs stats, listing, block locations, mkdirs, delete, rename, permissions, owner, recursive find, and snapshot operations. Listing and find callbacks return a boolean to request more batches.

## Dependencies and Integration Points
It includes all public value/error/config headers and uses `std::function`, `std::memory`, and `IoService`. Implementations integrate with NameNode RPC, DataNode readers, HA/failover, and tools/C bindings.

## Risks and Test Signals
Ownership is critical: raw `FileSystem*`/`FileHandle*`, shared or owned `IoService`, and destructor deadlock warnings for destroying a filesystem from callbacks. Tests should cover sync/async parity, cancellation, callback batching, permission/replication validation, EOF/invalid offset handling, event callbacks, service lifetime, snapshot operations, HA default FS, and destroying objects from safe and unsafe contexts.
