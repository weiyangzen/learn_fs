<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/tools_common.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/tools_common.h

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/tools_common.h` declares shared libhdfs++ helper functions used by the native command-line tools. The source was read as a complete 37-line file for this report.

## Important APIs, Types, and Functions

The namespace `hdfs` exposes `doConnect(hdfs::URI&, bool)`, `readFile(std::shared_ptr<FileSystem>, std::string, off_t, std::FILE*, bool)`, and `parse_path_or_exit(const std::string&)`.

## Control Flow

The header has no executable flow, but defines the common path for URI parsing, FileSystem construction/connection, and HDFS-to-local/stdout streaming used by commands such as `tail`, `get`, and `moveToLocal`.

## State and Persistence Behavior

No state is declared here. Implementations may open HDFS files, write local file handles, or delete HDFS paths based on arguments.

## Dependencies and Integration Points

It includes `hdfspp/hdfspp.h` and `<mutex>`, making libhdfs++ types available to command implementations.

## Risks and Edge Cases

The helper API exits the process on several failures rather than returning status, which makes callers simpler but harder to unit-test and compose.

## Test Signals

Connection tests with explicit URI and defaultFS, malformed URI tests, and file-read smoke tests through commands that call these helpers are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/tools_common.h -->
