# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/compress/bzip2/CRC.java

Purpose: package-private CRC-32 helper for Hadoop's BZip2 implementation. It stores the BZip2 polynomial lookup table and computes block/global CRC values used to sanity-check compressed data.

Important APIs and control flow: `initialiseCRC()` resets `globalCrc` to `0xffffffff`; `updateCRC(int)` and `updateCRC(int,int)` fold one byte or a repeated byte run through `crc32Table`; `getFinalCRC()` returns bitwise complement; `getGlobalCRC()` and `setGlobalCRC(int)` expose the current accumulator to the BZip2 encoder/decoder pipeline.

State and persistence: all state is in the instance field `globalCrc`; the static table is immutable in practice but declared as an array, so it is mutable from package code. No persistence or I/O.

Dependencies and integration: used inside the `org.apache.hadoop.io.compress.bzip2` package, based on Ant/Keiron Liddle BZip2 code. It is not public API and assumes callers pass byte values in the low 8 bits.

Risks and test signals: regression tests should compare CRCs against known BZip2 block vectors, including repeated-byte runs. Risks are accidental table mutation, signed-byte misuse by callers, and off-by-one errors in repeat updates.
