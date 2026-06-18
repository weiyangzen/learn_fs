<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/tools_common.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/tools_common.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/tools_common.cc` implements shared native helper routines for connecting to HDFS, streaming file contents, and parsing URIs. The source was read as a complete 140-line file for this report.

## Important APIs, Types, and Functions

`doConnect` loads default Hadoop resources, validates `core-site.xml` and `hdfs-site.xml`, builds `hdfs::Options`, optionally maximizes RPC timeout, creates an `IoService` and `FileSystem`, and connects to either the URI host/port or defaultFS. `readFile` opens an HDFS file, repeatedly `PositionRead`s into a static 1 MiB buffer, writes to a `FILE*`, and optionally deletes the source after EOF. `parse_path_or_exit` wraps `URI::parse_from_string` and exits on parse errors.

## Control Flow

Commands parse a path, call `doConnect`, then either invoke FileSystem metadata/mutation APIs or call `readFile` for data transfer. EOF is detected by `Status::is_invalid_offset()` in `readFile`.

## State and Persistence Behavior

The helper owns transient `ConfigParser`, `Options`, `IoService`, `FileSystem`, and `FileHandle` objects. `readFile` can persist bytes to a local file handle and can delete the HDFS source when `to_delete` is true.

## Dependencies and Integration Points

It integrates libhdfs++ configuration loading, URI handling, HDFS file IO, stderr diagnostics, and process termination for all native tools.

## Risks and Edge Cases

The static read buffer is not thread-safe, many failures call `exit(EXIT_FAILURE)` instead of returning errors, `IoService` lifetime is hidden behind `FileSystem`, and treating invalid offset as EOF depends on libhdfs++ behavior.

## Test Signals

MiniDFSCluster connection tests, defaultFS and explicit host/port tests, malformed configuration tests, partial read failure tests, stdout/local file transfer tests, and move-to-local delete-after-copy checks validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/tools_common.cc -->
