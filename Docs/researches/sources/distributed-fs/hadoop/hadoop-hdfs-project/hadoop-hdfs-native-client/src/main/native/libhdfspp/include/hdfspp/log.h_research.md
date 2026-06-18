# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/log.h

## Purpose
This header defines the C-facing log data contract and numeric log levels/components for libhdfs++.

## Important APIs, Control Flow, and State
Log levels range from trace to error. Component masks cover unknown, RPC, block reader, file handle, and filesystem. `LogData` carries component, level, file, line, function, and message-style fields used by C callbacks and copy/free helpers declared in `hdfs_ext.h`.

## Dependencies and Integration Points
The header is wrapped for C linkage where needed and is included by `hdfs_ext.h`. Internal logging code maps C++ log events to this stable C structure and component/level identifiers.

## Risks and Test Signals
The integer constants and struct layout are ABI-sensitive for C consumers. Logging callbacks may be concurrent and callback users do not own the incoming `LogData`. Tests should validate component masks, level filtering, copy/free deep-copy behavior, null/long messages, and callback concurrency.
