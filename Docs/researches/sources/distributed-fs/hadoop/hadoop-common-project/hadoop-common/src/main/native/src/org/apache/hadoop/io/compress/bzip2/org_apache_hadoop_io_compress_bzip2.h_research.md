<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/bzip2/org_apache_hadoop_io_compress_bzip2.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/bzip2/org_apache_hadoop_io_compress_bzip2.h

## Purpose
This header defines common bzip2 JNI plumbing for Hadoop native compression.

## Important APIs, Types, and Functions
It includes libbz2 and JNI headers, defines a default `HADOOP_BZIP2_LIBRARY` of `libbz2.so.1` when not configured, and provides `BZSTREAM()`/`JLONG()` pointer conversion macros.

## Control Flow
There is no runtime flow. The include guard and conditional library-name definition are compile-time only.

## State and Persistence
No state is stored here. The pointer conversion macros define the representation of native `bz_stream *` handles in Java `long` fields.

## Dependencies and Integration Points
It is consumed by the bzip2 compressor and decompressor C files and aligns them with Java stream-handle fields.

## Risks and Edge Cases
The header is Unix-oriented because it includes `dlfcn.h` and uses a Unix-style default library name. Pointer round-tripping assumes the native pointer width fits in `jlong`.

## Test Signals
Build tests should verify configured and default libbz2 names, and runtime codec tests validate stream-handle conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/bzip2/org_apache_hadoop_io_compress_bzip2.h -->
