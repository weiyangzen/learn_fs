<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/FakeCompressor.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/FakeCompressor.java

Purpose: Package-private fake `Compressor` for stream tests. It performs identity "compression" by copying input bytes directly to output and tracking simple counters.

Important APIs/types/functions: implements `compress`, `finish`, `finished`, `needsInput`, `reset`, `setInput`, `getBytesRead`, `getBytesWritten`, `setDictionary`, `reinit`, and `end`. Fields include `finish`, `finished`, `nread`, `nwrite`, `userBuf`, `userBufOff`, and `userBufLen`.

Control flow: `setInput` stores caller buffer slice and increments `nread` by length. `compress` copies up to `min(len,userBufLen)` bytes, advances offsets, increments `nwrite`, and marks `finished` when `finish` has been requested and all input is consumed. `reset` clears flags, counters, and buffer references.

State and persistence behavior: state is held only in the object. `end`, `setDictionary`, and `reinit` are no-ops, which keeps tests lightweight but not representative of native resources.

Dependencies and integration points: used by `TestBlockDecompressorStream` and other stream-level tests that need a deterministic compressor without real compression. Implements Hadoop `Compressor` and accepts Hadoop `Configuration` in `reinit`.

Risks and edge cases: it does not validate null buffers or negative ranges; tests using it should not infer production compressor argument validation. `compress` copies only if both source and destination are non-null but still advances counters, which differs from real implementations.

Test signals: provides controlled identity behavior to test block framing, EOF, close semantics, and decompressor stream behavior independently from compression algorithms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/FakeCompressor.java -->
