
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestCoderUtil.java

Purpose: Unit tests for raw-coder utility routines around zero-buffer caching, buffer zeroing, valid/null index discovery, and first-valid-input lookup.

Important APIs and types: Exercises `CoderUtil.getEmptyChunk()`, `resetBuffer(ByteBuffer,int)`, `resetBuffer(byte[],int,int)`, `getValidIndexes()`, `getNullIndexes()`, and `findFirstValidInput()`. Uses reflection to reset private static `emptyChunk` and concurrency primitives for a cache race test.

Control flow: `@BeforeEach` resets the empty chunk cache. Tests verify zero-filled chunks and buffers, expected index arrays, exception behavior with no valid inputs, and a synchronized race where a blocked small request must return the larger concurrently cached chunk.

State and persistence: Mutates `CoderUtil.emptyChunk`, a process-global cache, under `CoderUtil.class` synchronization. No durable state.

Dependencies and integration points: Guards utility behavior used by raw encoder/decoder state classes.

Risks: The concurrency test depends on observing `Thread.State.BLOCKED` within ten seconds, which can be timing-sensitive. Reflection ties the test to private field names.

Test signals: Strong regression coverage for HADOOP-style cache shrink races and index helper correctness.
