# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/AbstractContractVectoredReadTest.java

Purpose: `AbstractContractVectoredReadTest` validates `FSDataInputStream.readVectored()` for both heap and direct buffers, including range validation, EOF behavior, buffer release semantics, interoperation with normal reads, and async result handling.

Important APIs and types: it uses `FileRange`, `FSDataInputStream`, `ByteBuffer`, `ElasticByteBufferPool`, `WeakReferencedElasticByteBufferPool`, `TrackingByteBufferPool`, `CompletableFuture`, `CountDownLatch`, and `HadoopExecutors`. It is parameterized by buffer type through `@ParameterizedClass` and `params()`. It uses open-file options `FS_OPTION_OPENFILE_LENGTH` and vector read policy.

Control flow: `setup()` writes a 128 KiB vector file. `openVectorFile()` opens it through `openFile()` with vector read policy. Tests read multiple ranges, whole files, disjoint and mergeable ranges, overlapping and same ranges according to `VECTOR_IO_OVERLAPPING_RANGES`, null range inputs, random non-overlapping ranges, consecutive ranges, empty range lists, EOF ranges with early or late failure according to `VECTOR_IO_EARLY_EOF_CHECK`, invalid negative length or offset, null release callbacks, normal read before/after vectored read, multiple vectored reads, and end-to-end async processing in a separate thread pool. `testBufferSlicing()` verifies whether returned buffers are from the pool or sliced according to `VECTOREDIO_BUFFERS_SLICED`.

State and persistence behavior: the dataset is static and deterministic. Buffer pool state is released in teardown, and many tests explicitly return buffers after validation. `bufferReleases` tracks release callback calls but is not asserted because implementations vary on failure cleanup.

Dependencies and integration points: this test suite integrates vectored IO, `openFile()` policy hints, stream capabilities, buffer pool ownership, async future completion, and contract flags controlling overlap and EOF timing.

Risks: asynchronous tests depend on timeout constants and correct executor shutdown. Buffer ownership is subtle when implementations slice larger buffers. Not all implementations release buffers on failure, so leak detection is intentionally limited.

Test signals: pass indicates vectored read returns exact requested bytes for many range layouts, rejects invalid input, reports EOF at the declared time, coexists with normal reads, completes futures reliably, handles direct and heap buffers, and accurately advertises sliced-buffer behavior.
