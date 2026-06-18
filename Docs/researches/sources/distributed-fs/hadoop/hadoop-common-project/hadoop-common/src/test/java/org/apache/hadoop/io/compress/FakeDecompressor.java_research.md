<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/FakeDecompressor.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/FakeDecompressor.java

Purpose: Package-private fake `Decompressor` that mirrors `FakeCompressor` with identity byte copying for decompression stream tests.

Important APIs/types/functions: implements `decompress`, `finished`, `needsDictionary`, `needsInput`, `reset`, `setDictionary`, `setInput`, `getRemaining`, `getBytesRead`, `getBytesWritten`, and `end`. It tracks finish flags, counters, and a current input slice.

Control flow: `setInput` stores a byte slice and increments `nread`. `decompress` copies up to requested length or remaining input, advances offsets, increments `nwrite`, and marks `finished` only if the internal `finish` flag is true and all data is consumed. Because no public method sets `finish`, most stream tests rely on input exhaustion/EOF rather than `finished()`.

State and persistence behavior: no persistent state; all state is object-local and resettable. `getRemaining` always returns zero, so it does not expose actual `userBufLen`.

Dependencies and integration points: used by `TestBlockDecompressorStream` and `TestDecompressorStream`. It implements Hadoop `Decompressor` without native or filesystem dependencies.

Risks and edge cases: it does not validate arguments like real decompressors and its `finished` semantics are incomplete. `getRemaining` always returning zero can hide remaining-input behavior if reused in broader tests.

Test signals: gives deterministic pass-through decompression for validating stream wrappers, skip/read loops, block EOF, and IO exception propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/FakeDecompressor.java -->
