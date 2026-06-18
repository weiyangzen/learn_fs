# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/CoderUtil.java

Purpose: shared raw-coder helper methods for zeroing buffers, converting `ECChunk` wrappers, cloning arrays into direct buffers, and finding null/valid indexes.

Important APIs/types/functions: `getEmptyChunk()`, `resetBuffer()` overloads, `resetOutputBuffers()` overloads, `toBuffers(ECChunk[])`, `cloneAsDirectByteBuffer()`, `getNullIndexes()`, `findFirstValidInput()`, and `getValidIndexes()`.

Control flow: zeroing uses a shared cached zero-filled `byte[]`, growing it under a class lock when a larger request arrives. `toBuffers` unwraps chunk buffers and materializes all-zero chunks by zeroing their buffer range. Index helpers compact matching positions into freshly sized arrays.

State and persistence: only static in-memory `emptyChunk` cache persists. No file or durable state.

Dependencies and integration: used throughout raw coder state validation, Java coders, legacy RS, native conversion, and `DecodingValidator`.

Risks: `resetBuffer(ByteBuffer)` temporarily advances then restores position but requires enough remaining capacity; `getEmptyChunk` cache growth can retain a large array for process lifetime. Test signals should cover all-zero ECChunk conversion, null and valid index extraction, first-valid failure, position preservation after reset, and concurrent zero-cache growth.
