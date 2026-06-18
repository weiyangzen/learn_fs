## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/ByteBufferReadable.java

Purpose: evolving stream interface for sequential reads into a `ByteBuffer` instead of a byte array.

Important APIs and types: single `read(ByteBuffer buf)` method with standard read return values and buffer position advancement.

Control flow: interface only. Contract leaves buffer state undefined on exception and requires zero-length requests to be accepted.

State and persistence behavior: no interface state; implementations advance the underlying stream position as a sequential read.

Dependencies and integration points: used by `FSDataInputStream`, zero-copy/fallback code, and capability `StreamCapabilities.READBYTEBUFFER`.

Risks: callers must check capability; unsupported streams can throw. Exception handling must assume partial buffer mutation.

Test signals: implementation tests should cover heap/direct buffers, empty buffers, EOF, partial reads, exception buffer state expectations, and capability advertisement.
