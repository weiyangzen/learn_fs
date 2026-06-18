<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/statinfo.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/statinfo.cc

## Purpose
Implements human-readable formatting for HDFS `StatInfo`, analogous to an `ls -l` line.

## Important APIs, Types, And Functions
The constructor zero-initializes file metadata fields. `StatInfo::str()` formats file type, permission bits, replication, owner, group, length, modification time, and full path.

## Control Flow
`str()` builds a 10-character permissions string from POSIX mode bits, converts modification time from milliseconds to seconds, formats local time, and writes aligned columns to a stream.

## State And Persistence
State is per-object file metadata populated from namenode responses. No persistence exists.

## Dependencies And Integration Points
Used by listing/stat display code and C API conversion in `hdfs.cc`. Depends on x-platform stat permission constants.

## Risks
`localtime` is not thread-safe. Unknown file types are rendered as regular-file style unless handled elsewhere. Formatting width choices can truncate or misalign unusual values.

## Test Signals
Tests should cover files, directories, zero replication, permissions, time formatting, long owner/group/path values, and concurrent formatting if used from multiple threads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/common/statinfo.cc -->
