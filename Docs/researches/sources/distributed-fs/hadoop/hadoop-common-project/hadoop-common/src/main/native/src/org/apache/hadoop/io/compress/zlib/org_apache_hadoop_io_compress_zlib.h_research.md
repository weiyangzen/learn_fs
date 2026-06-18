<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/zlib/org_apache_hadoop_io_compress_zlib.h -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/zlib/org_apache_hadoop_io_compress_zlib.h

## Purpose
This header provides shared zlib JNI definitions for Hadoop's native zlib compressor and decompressor.

## Important APIs, Types, and Functions
It includes zlib/zconf and JNI headers, sets `HADOOP_ZLIB_LIBRARY` to `L"zlib1.dll"` on Windows, and defines `ZSTREAM()` and `JLONG()` for native pointer and Java long conversion.

## Control Flow
Compile-time platform branches select Unix dynamic loading or Windows library naming. No runtime logic exists in the header.

## State and Persistence
No state is stored here. The macros define how `z_stream *` state is represented in Java fields.

## Dependencies and Integration Points
It is included by both zlib native implementation files and must stay compatible with Java stream handle fields.

## Risks and Edge Cases
Pointer conversion assumes safe pointer-to-`jlong` round trips. Windows and Unix library naming differ, so build configuration must provide the correct `HADOOP_ZLIB_LIBRARY` when defaults are not sufficient.

## Test Signals
Cross-platform build tests and zlib codec round trips validate this header's contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/native/src/org/apache/hadoop/io/compress/zlib/org_apache_hadoop_io_compress_zlib.h -->
