# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/include/hdfspp/content_summary.h

## Purpose
This header defines `ContentSummary`, the C++ representation of HDFS content summary results.

## Important APIs, Control Flow, and State
The struct stores length, file count, directory count, quota, space consumed, space quota, and path. Its constructor initializes defaults in the implementation. `str(bool include_quota)` formats in `hdfs_count` style, while `str_du()` formats in `hdfs_du` style.

## Dependencies and Integration Points
`FileSystem::GetContentSummary` fills this struct for async and sync callers. CLI tools or bindings can use the formatting helpers for Hadoop-compatible output.

## Risks and Test Signals
Formatting compatibility is externally visible. Tests should validate zero/default values, quota-included and quota-omitted output, large 64-bit counts, path handling, and mapping from NameNode proto fields into every member.
