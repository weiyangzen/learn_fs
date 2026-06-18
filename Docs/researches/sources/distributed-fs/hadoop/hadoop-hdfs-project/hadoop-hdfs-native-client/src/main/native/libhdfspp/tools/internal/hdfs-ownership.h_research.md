<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/hdfs-ownership.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/hdfs-ownership.h

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/hdfs-ownership.h` declares shared ownership helper types for native HDFS ownership-changing commands. The source was read as a complete 88-line file for this report.

## Important APIs, Types, and Functions

`Ownership` parses a `user[:group]` string and exposes `GetUser()`, `GetGroup()`, and equality comparison. `OwnerState` stores username, group, callback handler, outstanding request counter, completion flag, final status, and mutex for recursive async owner updates.

## Control Flow

The header defines data contracts only. Implementations parse CLI ownership specifications into `Ownership`; recursive ownership commands use `OwnerState` similarly to the replication and content-summary state structs.

## State and Persistence Behavior

The parsed user/group and callback counters are transient in-memory state. Durable HDFS ownership changes are performed by the commands that consume these types.

## Dependencies and Integration Points

It depends on optional strings, function callbacks, mutexes, and `hdfspp/status.h`, and integrates with chown/chgrp-style command implementations.

## Risks and Edge Cases

Empty users, trailing colons, absent groups, and equality semantics between optional and non-optional groups are the main parser risks.

## Test Signals

Unit tests should cover `user`, `user:group`, `user:`, `:group`, equality with and without group values, and recursive callback completion behavior in ownership commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/hdfs-ownership.h -->
