# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractUnbufferTest.java

Purpose: `AbstractContractUnbufferTest` validates `FSDataInputStream.unbuffer()` behavior for filesystems declaring `SUPPORTS_UNBUFFER`.

Important APIs and types: it uses `FSDataInputStream`, `Path`, AssertJ, `ContractTestUtils.createFile`, `dataset`, and `readNBytes`. The class is annotated `@FlakyTest("buffer underflow")`, acknowledging that some valid `InputStream.read(byte[])` implementations may return fewer bytes than requested.

Control flow: `setup()` creates a deterministic file and byte array after skipping unsupported filesystems. Tests call `unbuffer()` after full reads, before reads, on empty files, after stream close, repeatedly, and between multiple partial reads. The private `unbuffer()` helper captures `getPos()`, calls `stream.unbuffer()`, and asserts the position is unchanged. Content validation reads expected byte ranges and compares against the original dataset.

State and persistence behavior: the main file and an empty file are created under contract paths. The stream's logical position is the critical mutable state; unbuffering must release internal buffers without changing position or corrupting later reads.

Dependencies and integration points: this file exercises the `CanUnbuffer` behavior exposed through `FSDataInputStream`. It depends on accurate `getPos()` and deterministic file content from `ContractTestUtils`.

Risks: tests assume `readNBytes()` can retrieve the exact requested length in one validation step; the class-level flaky annotation documents risk from short reads. Calling unbuffer on a closed stream is expected not to fail, which may be stricter than some implementations.

Test signals: pass indicates unbuffer can be called before reads, after reads, on empty or closed streams, and multiple times without changing position or breaking subsequent reads.
