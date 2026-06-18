# Research: subset-b-007398

Grouped source research for Hadoop erasure-code and TFile tests. Each section is source-tree aligned and intended for deterministic splitting into `Docs/researches/<source>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/TestCodecRegistry.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/TestCodecRegistry.java

Purpose: Verifies the singleton erasure-code `CodecRegistry` exposes the expected built-in codec names, raw-coder factory ordering, factory lookup by coder name, and user-defined update behavior.

Important APIs and types: Exercises `CodecRegistry.getInstance()`, `getCodecNames()`, `getCoders()`, `getCoderNames()`, `getCoderByName()`, and `updateCoders()`. It checks `ErasureCodeConstants` codec names and factory types for native RS, Java RS, legacy RS, native XOR, and Java XOR.

Control flow: Each JUnit test queries the registry and asserts exact sizes, names, order, and null behavior for bad codec or coder names. `testUpdateCoders()` injects an inner factory with a duplicate `rs_java` coder name and confirms built-ins remain authoritative.

State and persistence: The registry is process-global, so `updateCoders()` mutates shared registry state during the JVM. The test relies on duplicate filtering preserving canonical factory ordering.

Dependencies and integration points: Connects public registry lookup to `CodecUtil` configuration paths and raw coder factory implementations.

Risks: Order-sensitive assertions will fail on intentional provider-priority changes. Global registry mutation can leak across tests if update semantics are broadened.

Test signals: Strong coverage of default codec discovery, bad-name nulls, and duplicate user factory rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/TestCodecRegistry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/TestCoderBase.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/TestCoderBase.java

Purpose: Provides shared test utilities for both block-level and raw erasure coder tests, especially ByteBuffer allocation, chunk generation, erasure simulation, cloning, comparison, and diagnostics.

Important APIs and types: Defines `prepare()`, `setChunkSize()`, `prepareBufferAllocator()`, `prepareDataChunksForEncoding()`, `prepareParityChunksForEncoding()`, `prepareOutputChunksForDecoding()`, `backupAndEraseChunks()`, `cloneChunksWithData()`, `compareAndVerify()`, `markChunks()`, `restoreChunksFromMark()`, and corruption helpers. It uses `ECChunk`, `BufferAllocator.SimpleBufferAllocator`, `SlicedBufferAllocator`, `Configuration`, and `DumpUtil`.

Control flow: Tests call `prepare()` to set data/parity counts, erased indexes, configuration, and fixed-data mode. Encoding inputs and decoding outputs are generated with alternating zero-offset and nonzero-position buffers. Erased chunks are backed up, nulled in the input arrays, then later compared against recovered chunks.

State and persistence: Holds mutable per-test settings such as chunk size, allocator, direct-buffer mode, fixed data, erased indexes, and `allowChangeInputs`. No durable state exists, but static `Random` and fixed-data generator affect reproducibility.

Dependencies and integration points: Used by `TestErasureCoderBase`, `TestRawCoderBase`, and decoder validation tests.

Risks: Alternating buffer offsets catches position/limit bugs, but random data and static generator state make failures less deterministic unless fixed data is enabled. Corruption helpers choose random chunks.

Test signals: Enables broad checks for direct versus heap buffers, input mutation, erased index translation, and output equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/TestCoderBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/TestECSchema.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/TestECSchema.java

Purpose: Tests construction and value semantics for `ECSchema`, including option-map parsing, extra options, equality, and hash-code consistency.

Important APIs and types: Uses `ECSchema.NUM_DATA_UNITS_KEY`, `NUM_PARITY_UNITS_KEY`, `CODEC_NAME_KEY`, `new ECSchema(Map)`, `new ECSchema(codec, data, parity, extraMap)`, getters, `getExtraOptions()`, `equals()`, and `hashCode()`.

Control flow: `testGoodSchema()` builds a schema from a `HashMap`, validates fields, then compares it to an equivalent constructor-based schema. `testEqualsAndHashCode()` creates schemas varying codec, data units, parity units, and extras, then checks identity copies and pairwise inequality.

State and persistence: Only local immutable schema objects are used. Extra options are copied into schema state and participate in equality.

Dependencies and integration points: Guards the schema object consumed by erasure codec options, filesystem policy definitions, and codec factories.

Risks: The test is sensitive to whether extra options are normalized or preserved. It checks inequality against another object's hash code as a negative case, which is unusual but harmless.

Test signals: Confirms constructor equivalence and stable value-object behavior under a 300-second class timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/TestECSchema.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/TestErasureCodingEncodeAndDecode.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/TestErasureCodingEncodeAndDecode.java

Purpose: End-to-end smoke test for raw Reed-Solomon encoding and decoding over byte-array inputs for a 6 data, 3 parity layout.

Important APIs and types: Uses `CodecUtil.createRawEncoder()`, `CodecUtil.createRawDecoder()`, `ErasureCoderOptions`, `RawErasureEncoder.encode(byte[][], byte[][])`, and `RawErasureDecoder.decode(byte[][], int[], byte[][])`.

Control flow: The test generates 6 KB of random data, splits it into six 1 KB data blocks, encodes three parity blocks, composes all nine blocks, then iterates all single, double, and triple erasure combinations by nulling selected blocks and asserting decoded bytes equal the backed-up originals.

State and persistence: Mutates the shared `all` block array inside nested loops, restoring erased entries after each decode. No filesystem or durable state is touched.

Dependencies and integration points: Exercises the default RS raw coder selected through `CodecUtil` and `Configuration`, not a specific factory class.

Risks: The misspelled constants are cosmetic. Triple nested loops create broad coverage but can be slow if native or Java coder performance regresses.

Test signals: Strong signal that the configured RS raw coder can recover any erasure set up to parity width.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/TestErasureCodingEncodeAndDecode.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/codec/TestHHXORErasureCodec.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/codec/TestHHXORErasureCodec.java

Purpose: Verifies that `HHXORErasureCodec` creates encoder and decoder instances using the schema's data and parity unit counts.

Important APIs and types: Uses `ECSchema("hhxor", 10, 4)`, `ErasureCodecOptions`, `HHXORErasureCodec`, `createEncoder()`, `createDecoder()`, and `ErasureCoder.getNumDataUnits()/getNumParityUnits()`.

Control flow: A single JUnit test constructs the codec with a fresh `Configuration`, creates both coder directions, and asserts each exposes 10 data units and 4 parity units.

State and persistence: The schema and options are instance fields. There is no external state, file IO, or coder execution.

Dependencies and integration points: Connects the codec factory layer to `HHXORErasureEncoder` and `HHXORErasureDecoder` constructors through `HHXORErasureCodec`.

Risks: This is only a construction/configuration test; it does not validate HHXOR math, raw coder selection, buffer handling, or decoding outcomes.

Test signals: Useful smoke coverage for codec wiring and schema propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/codec/TestHHXORErasureCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/coder/TestErasureCoderBase.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/coder/TestErasureCoderBase.java

Purpose: Shared block-level erasure coder harness that simulates `ECBlockGroup` encoding and decoding without HDFS block IO.

Important APIs and types: Extends `TestCoderBase`. Defines `TestBlock extends ECBlock`, `testCoding()`, `performCodingStep()`, `prepareBlockGroupForEncoding()`, `backupAndEraseBlocks()`, `createEncoder()`, and `createDecoder()`. It reflects constructors accepting `ErasureCoderOptions`.

Control flow: Concrete tests set encoder and decoder classes, then `testCoding()` runs direct or heap buffers over three chunk sizes. It creates data and parity blocks, calculates an encoding step, iterates chunks through `performCoding()`, clones data, erases configured blocks, calculates a decoding step, performs it, and compares recovered blocks with backups.

State and persistence: Caches encoder and decoder instances for reuse checks. `TestBlock` stores an in-memory `ECChunk[]`; erasure is represented by nulling chunks and marking the block erased.

Dependencies and integration points: Exercises block-level `ErasureCoder`, `ErasureCodingStep`, `ECBlock`, and `ECBlockGroup` abstractions that sit above raw coders.

Risks: Reflection hides constructor errors until runtime. Reusing coder instances intentionally stresses shared internal buffers.

Test signals: Covers variable chunk sizes, direct/heap buffers, data/parity erasures, and block-group step integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/coder/TestErasureCoderBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/coder/TestHHErasureCoderBase.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/coder/TestHHErasureCoderBase.java

Purpose: Specializes the block-level harness for Hitchhiker-style coders that process multiple sub-packets per coding step.

Important APIs and types: Extends `TestErasureCoderBase`, adds `subPacketSize`, and overrides `performCodingStep(ErasureCodingStep)`. It works with `ECBlock`, `ECChunk`, and `ErasureCodingStep.performCoding()`.

Control flow: For each block chunk index advanced by `subPacketSize`, the override flattens chunks for all input blocks across each sub-packet into a single input array, allocates matching output chunks, writes them back into output blocks, then invokes `performCoding()` once per sub-packet group. The step is finished after all grouped chunks are processed.

State and persistence: Uses inherited block/chunk state and mutable `subPacketSize`, defaulting to 2. No persistent state exists.

Dependencies and integration points: Provides the test execution model for `HHXORErasureEncoder` and `HHXORErasureDecoder`, whose steps expect sub-packeted input and output arrays.

Risks: `numChunksInBlock` must be a multiple of `subPacketSize`; otherwise chunk indexing would overrun. IOException is converted to test failure.

Test signals: Validates that Hitchhiker steps handle batched sub-packet buffer ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/coder/TestHHErasureCoderBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/coder/TestHHXORErasureCoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/coder/TestHHXORErasureCoder.java

Purpose: Concrete block-level HHXOR coder tests across direct and heap buffers, coder reuse, configuration-driven raw RS selection, and multiple erasure layouts.

Important APIs and types: Inherits `TestHHErasureCoderBase`; sets `HHXORErasureEncoder`, `HHXORErasureDecoder`, `numChunksInBlock = 10`, and `subPacketSize = 2`. Uses `CodecUtil.IO_ERASURECODE_CODEC_RS_RAWCODERS_KEY` to force `RSRawErasureCoderFactory` in one case.

Control flow: Each JUnit test calls `prepare()` with a 10x4 or 6x3 layout and selected erased data/parity indexes, then runs `testCoding()` one or more times. Some tests alternate direct and heap buffers to stress reused coder state.

State and persistence: Encoder/decoder instances may be reused within inherited harness calls; all data is in-memory chunks.

Dependencies and integration points: Integrates the HHXOR block coder with raw RS coder configuration and the sub-packet harness.

Risks: Native/default raw coder choices can change behavior unless configuration pins Java RS. Complex multi-erasure cases can expose sub-packet ordering bugs.

Test signals: Covers data erasures, parity erasures, combined erasures, repeated calls, and mixed buffer modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/coder/TestHHXORErasureCoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/coder/TestRSErasureCoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/coder/TestRSErasureCoder.java

Purpose: Tests block-level Reed-Solomon encoder and decoder behavior under several data/parity widths, erasure patterns, buffer types, and raw-coder configuration.

Important APIs and types: Uses `RSErasureEncoder`, `RSErasureDecoder`, inherited `TestErasureCoderBase`, `CodecUtil.IO_ERASURECODE_CODEC_RS_RAWCODERS_KEY`, and `RSRawErasureCoderFactory.CODER_NAME`.

Control flow: `setup()` chooses coder classes and ten chunks per synthetic block. Tests prepare layouts such as 10x4, 6x3, and 3x3, erase data blocks, parity blocks, or mixed sets, and invoke inherited encode/decode/compare flow. Some tests call `testCoding()` repeatedly or alternate direct and heap buffers.

State and persistence: Per-test in-memory block groups are mutated through erased flags and null chunk arrays. Class timeout is 300 seconds.

Dependencies and integration points: Exercises block-level RS over the raw-coder selection path, including configuration that forces the Java RS raw coder.

Risks: The matrix is order- and reuse-sensitive, so shared internal buffers in RS coders are a key failure point. It does not test invalid constructor options.

Test signals: Strong regression coverage for recoverability and buffer compatibility across RS layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/coder/TestRSErasureCoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/coder/TestXORCoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/coder/TestXORCoder.java

Purpose: Tests block-level XOR erasure coding for a 10 data, 1 parity layout.

Important APIs and types: Uses `XORErasureEncoder`, `XORErasureDecoder`, inherited `TestErasureCoderBase`, and JUnit timeout coverage.

Control flow: `setup()` sets coder classes, 10 data units, 1 parity unit, and 10 chunks per block. One test erases the parity block with heap buffers and repeats to validate reuse. Another erases data block 5 and alternates direct and heap buffers across repeated calls.

State and persistence: All data is generated in memory by the inherited harness. Encoder and decoder reuse is intentional inside repeated calls.

Dependencies and integration points: Validates the block-level XOR coder facade above raw XOR coding primitives.

Risks: XOR can recover only one missing unit; the test matrix is appropriately narrow but does not cover invalid multi-erasure paths at the block level.

Test signals: Confirms parity reconstruction, data reconstruction, and mixed ByteBuffer compatibility for XOR block coders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/coder/TestXORCoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/RawErasureCoderBenchmark.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/RawErasureCoderBenchmark.java

Purpose: Command-line and test-callable benchmark driver for raw erasure coder throughput. It measures encode/decode speed only and does not validate output correctness.

Important APIs and types: Exposes `main()` and `performBench()`. Defines `CODER`, `BenchData`, and `BenchmarkCallable`. Uses `DummyRawErasureCoderFactory`, legacy RS, Java RS, native RS, `RawErasureEncoder`, `RawErasureDecoder`, `ErasureCoderOptions`, `ByteBuffer`, `ExecutorService`, and `StopWatch`.

Control flow: Arguments choose encode/decode, coder index, thread count, data size, and chunk size. `performBench()` configures buffer sizes, warms the selected coder, generates a shared test buffer, starts worker callables with duplicate buffers, waits for durations, prints throughput and percentile statistics, and releases the coder.

State and persistence: `BenchData` static fields hold chunk and total sizes for the run. Coders are shared across worker threads, making thread safety part of the benchmark stress. No files are written.

Dependencies and integration points: Connects factory implementations to ad hoc performance tests and `TestRawErasureCoderBenchmark`.

Risks: Shared coder instances may not be safe for all implementations. Native coder availability can affect failures. Because correctness is not checked, corruption can go unnoticed.

Test signals: Useful for throughput, multi-thread stress, argument validation, release paths, and chunk-size bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/RawErasureCoderBenchmark.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestCoderUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestCoderUtil.java

Purpose: Unit tests for raw-coder utility routines around zero-buffer caching, buffer zeroing, valid/null index discovery, and first-valid-input lookup.

Important APIs and types: Exercises `CoderUtil.getEmptyChunk()`, `resetBuffer(ByteBuffer,int)`, `resetBuffer(byte[],int,int)`, `getValidIndexes()`, `getNullIndexes()`, and `findFirstValidInput()`. Uses reflection to reset private static `emptyChunk` and concurrency primitives for a cache race test.

Control flow: `@BeforeEach` resets the empty chunk cache. Tests verify zero-filled chunks and buffers, expected index arrays, exception behavior with no valid inputs, and a synchronized race where a blocked small request must return the larger concurrently cached chunk.

State and persistence: Mutates `CoderUtil.emptyChunk`, a process-global cache, under `CoderUtil.class` synchronization. No durable state.

Dependencies and integration points: Guards utility behavior used by raw encoder/decoder state classes.

Risks: The concurrency test depends on observing `Thread.State.BLOCKED` within ten seconds, which can be timing-sensitive. Reflection ties the test to private field names.

Test signals: Strong regression coverage for HADOOP-style cache shrink races and index helper correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestCoderUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestDecodingValidator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestDecodingValidator.java

Purpose: Parameterized tests for `DecodingValidator`, ensuring decoded outputs can be independently validated across RS, native RS, XOR, and native XOR raw decoders.

Important APIs and types: Extends `TestRawCoderBase`; uses `DecodingValidator.validate()`, `getNewValidIndexes()`, `getNewErasedIndex()`, `InvalidDecodingException`, `CoderUtil.getValidIndexes()`, and JUnit parameter sources. Native cases are gated by `ErasureCodeNative.isNativeCodeLoaded()`.

Control flow: For each factory/layout/erasure set, it encodes data, erases chunks, decodes with least required inputs, restores marks, clones inputs and outputs, validates, then asserts input positions advance, recovered chunks and erased indexes are unchanged, and validator-selected indexes are consistent. A bad-decoding test pollutes recovered output and expects `InvalidDecodingException`.

State and persistence: Reuses an optional validator around a decoder and all chunk data is in memory.

Dependencies and integration points: Validates the safety layer that can detect silent decoder corruption.

Risks: Native parameter cases are skipped without native libraries. An empty non-parameter `testIdempotentReleases()` shadows the inherited test name but does nothing.

Test signals: Strong signal for validator correctness, immutability of caller data, and failure detection on polluted output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestDecodingValidator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestDummyRawCoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestDummyRawCoder.java

Purpose: Tests the dummy raw erasure coder, whose expected behavior is to produce zero-filled parity and recovered chunks rather than real erasure recovery.

Important APIs and types: Extends `TestRawCoderBase`, selects `DummyRawErasureCoderFactory`, uses `ECChunk`, `ByteBuffer.wrap()`, inherited buffer allocation, and zero chunk bytes from `TestCoderBase`.

Control flow: Setup selects the dummy factory, disables dumps, and sets the base chunk size. Two tests prepare 6x3 layouts with data-only and data-plus-parity erasures, then run a custom `testCoding()`: encode generated data, compare parity chunks against zero chunks, erase inputs, decode, and compare recovered chunks against zero chunks.

State and persistence: All data is in memory. The custom test marks data chunks before encode and restores them before decode.

Dependencies and integration points: Provides coverage for the no-op raw coder used by benchmark and testing paths.

Risks: It intentionally does not validate reconstruction of original bytes. `getEmptyChunks()` wraps the same zero byte array repeatedly, so mutation by a coder would couple expected chunks.

Test signals: Confirms dummy coder output contract for direct and heap buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestDummyRawCoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestNativeRSRawCoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestNativeRSRawCoder.java

Purpose: Concrete test class for native ISA-L Reed-Solomon raw encoder and decoder behavior.

Important APIs and types: Extends `TestRSRawCoderBase`, selects `NativeRSRawErasureCoderFactory`, gates setup with `ErasureCodeNative.isNativeCodeLoaded()`, and uses inherited RS erasure matrix tests plus an explicit release test.

Control flow: Setup skips when native code is unavailable and enables dumps. It inherits most RS raw-coder cases but redeclares them, preparing 6x3 or 10x4 layouts and running mixed direct/heap buffer tests twice. `testAfterRelease63()` prepares a 6x3 coder, releases encoder and decoder, and expects subsequent calls to fail with closed IOExceptions.

State and persistence: Native coder instances may allocate native resources and are released by tests. Chunk data remains in memory.

Dependencies and integration points: Covers Hadoop native erasure-code loading and native RS raw factory integration.

Risks: Test coverage depends on native library availability. Duplicate inherited test definitions increase maintenance cost.

Test signals: Strong native RS recoverability, buffer compatibility, too-many-erasure failure, and release semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestNativeRSRawCoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestNativeXORRawCoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestNativeXORRawCoder.java

Purpose: Concrete test class for native XOR raw erasure coder behavior.

Important APIs and types: Extends `TestXORRawCoderBase`, selects `NativeXORRawErasureCoderFactory`, checks `ErasureCodeNative.isNativeCodeLoaded()`, and adds `testAfterRelease63()`.

Control flow: Setup skips the class when native code is absent and enables verbose dumps. It inherits XOR raw-coder tests for data erasure, parity erasure, too-many-erasure failure, and bad input/output cases. The release test prepares a 6x3 configuration and verifies encode/decode after `release()` fail.

State and persistence: Native coder resources are created and released; test data is in-memory chunks.

Dependencies and integration points: Exercises the native XOR factory and native-code load path.

Risks: Native availability controls whether meaningful tests run. The release test uses a 6x3 layout even though inherited normal XOR tests use 10x1, so it stresses configuration acceptance differently.

Test signals: Covers native XOR compatibility with the shared XOR matrix and resource lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestNativeXORRawCoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestRSLegacyRawCoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestRSLegacyRawCoder.java

Purpose: Binds the shared RS raw-coder test matrix to the legacy Java Reed-Solomon implementation.

Important APIs and types: Extends `TestRSRawCoderBase` and selects `RSLegacyRawErasureCoderFactory` for both encoder and decoder factories.

Control flow: `@BeforeEach` sets factories and disables verbose dumps. All actual encode/decode, erasure, buffer, negative, and input-position tests are inherited from `TestRSRawCoderBase` and `TestRawCoderBase`.

State and persistence: No additional state beyond inherited coder and chunk fields. All data is in memory.

Dependencies and integration points: Ensures the older Java RS factory remains compatible with the same public raw-coder contracts as newer Java and native implementations.

Risks: Because this class only configures the base, any inherited test gaps apply here. Legacy-specific edge cases are not isolated.

Test signals: Provides regression signal that legacy RS still handles the standard 6x3 and 10x4 erasure matrix, mixed buffers, too-many erasures, and input position advancement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestRSLegacyRawCoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestRSRawCoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestRSRawCoder.java

Purpose: Binds the shared RS raw-coder test matrix to the newer Java Reed-Solomon implementation.

Important APIs and types: Extends `TestRSRawCoderBase` and selects `RSRawErasureCoderFactory` for both encoder and decoder factories.

Control flow: Setup assigns factories and disables dumps. The inherited matrix generates chunks, encodes parity, erases data/parity combinations, decodes with least required inputs, checks unchanged inputs when required, validates recovered bytes, and tests input positions.

State and persistence: Uses inherited in-memory chunk state and newly created raw coders per test flow.

Dependencies and integration points: Verifies the default Java RS raw coder used by registry and configuration paths.

Risks: The class contains no Java-RS-specific assertions beyond the inherited contract. If factory fields diverge, note that `TestRawCoderBase.createDecoder()` currently instantiates `encoderFactoryClass`, so asymmetric tests may not behave as named.

Test signals: Standard RS recoverability and buffer-contract coverage for the Java implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestRSRawCoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestRSRawCoderBase.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestRSRawCoderBase.java

Purpose: Shared Reed-Solomon raw-coder matrix covering many erasure patterns and buffer contracts.

Important APIs and types: Extends `TestRawCoderBase` and defines JUnit tests that call `prepare()`, `testCodingDoMixAndTwice()`, `testCodingWithErasingTooMany()`, and `testInputPosition()`.

Control flow: Tests cover 6x3 erasures of all data units, single data units, mixed data/parity units, all parity units, multiple parity units, and 10x4 data/parity erasure. Most run direct then heap buffers twice. A negative case erases more units than parity width and expects failure. Input-position coverage asserts consumed buffers have no remaining bytes after encode/decode.

State and persistence: Relies on inherited mutable erased-index arrays, buffer mode, chunk size, coders, and generated chunks.

Dependencies and integration points: Inherited by legacy Java, new Java, native, and intended interoperability RS test classes.

Risks: Method names prefixed with `testCodingNegative` can still expect success in one case; only the too-many-erasure case is negative. Factory asymmetry may be masked by base decoder creation.

Test signals: Broad RS contract coverage across recovery combinations and ByteBuffer modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestRSRawCoderBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestRSRawCoderInteroperable1.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestRSRawCoderInteroperable1.java

Purpose: Intended interoperability test with Java RS encoding and native RS decoding over the shared RS matrix.

Important APIs and types: Extends `TestRSRawCoderBase`, gates on `ErasureCodeNative.isNativeCodeLoaded()`, sets `encoderFactoryClass = RSRawErasureCoderFactory.class`, and sets `decoderFactoryClass = NativeRSRawErasureCoderFactory.class`.

Control flow: Setup runs before inherited RS tests, enabling verbose dumps and selecting asymmetric factories. The inherited tests then encode, erase, decode, and compare for many 6x3 and 10x4 layouts.

State and persistence: Uses in-memory chunks and potentially native decoder resources if instantiated.

Dependencies and integration points: Should verify wire-format compatibility between Java RS parity generation and native RS decoding.

Risks: `TestRawCoderBase.createDecoder()` instantiates `encoderFactoryClass` rather than `decoderFactoryClass`, so this class may currently run Java-to-Java instead of Java-to-native, weakening the interoperability signal.

Test signals: Native availability gate and inherited RS matrix exist, but factory-instantiation behavior should be checked before relying on this as true interoperability coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestRSRawCoderInteroperable1.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestRSRawCoderInteroperable2.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestRSRawCoderInteroperable2.java

Purpose: Intended interoperability test with native RS encoding and Java RS decoding over the shared RS matrix.

Important APIs and types: Extends `TestRSRawCoderBase`, requires `ErasureCodeNative.isNativeCodeLoaded()`, sets `encoderFactoryClass = NativeRSRawErasureCoderFactory.class`, and sets `decoderFactoryClass = RSRawErasureCoderFactory.class`.

Control flow: Setup selects asymmetric factories and verbose dumps. Inherited RS tests prepare erasure layouts, run mixed direct/heap buffers, encode, decode, and verify recovered chunks.

State and persistence: May allocate native encoder resources through the selected factory; all buffers are in-memory.

Dependencies and integration points: Intended to guard parity format compatibility from native RS output to Java RS decoder input.

Risks: The base `createDecoder()` uses `encoderFactoryClass`, so this class may currently instantiate native for both encode and decode, not native-to-Java. That undermines the named interoperability purpose.

Test signals: Provides inherited RS coverage under native-code gating, but the asymmetric decoder field should be fixed or audited for true interop validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestRSRawCoderInteroperable2.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestRawCoderBase.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestRawCoderBase.java

Purpose: Shared raw erasure coder harness for byte-buffer and chunk-level encode/decode correctness, negative input/output cases, release semantics, and input-position contracts.

Important APIs and types: Extends `TestCoderBase`; manages `RawErasureCoderFactory`, `RawErasureEncoder`, and `RawErasureDecoder`. Provides `testCoding()`, `performTestCoding()`, `ensureOnlyLeastRequiredChunks()`, `testAfterRelease()`, `testInputPosition()`, `createEncoder()`, and `createDecoder()`.

Control flow: Tests configure factories and erasure indexes, generate data chunks, optionally corrupt inputs/outputs, encode parity, check input mutation rules, erase chunks, remove redundant inputs, decode, compare recovered chunks, and validate input buffer positions. Negative paths expect too many erasures or bad buffers to fail.

State and persistence: Mutable factory classes, coders, buffer mode, `allowChangeInputs`, chunk size, and erased indexes are inherited per test instance. No filesystem persistence.

Dependencies and integration points: Underpins all raw RS/XOR/native/dummy/interoperability tests and uses `LambdaTestUtils` for closed-coder assertions.

Risks: `createDecoder()` instantiates `encoderFactoryClass` instead of `decoderFactoryClass`, which can invalidate asymmetric interoperability tests. Random corruption may make failures variable.

Test signals: Central contract coverage for raw coder correctness, resource release idempotence, and ByteBuffer semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestRawCoderBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestRawErasureCoderBenchmark.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestRawErasureCoderBenchmark.java

Purpose: JUnit smoke tests for the raw erasure coder benchmark driver across dummy, legacy RS, Java RS, and native ISA-L coders.

Important APIs and types: Calls `RawErasureCoderBenchmark.performBench()` with `CODER.DUMMY_CODER`, `LEGACY_RS_CODER`, `RS_CODER`, and `ISAL_CODER`. Native benchmark is gated by `ErasureCodeNative.isNativeCodeLoaded()`.

Control flow: Each test invokes encode and decode benchmark runs with different thread counts, total data sizes, and chunk sizes. The driver handles warmup, worker execution, timing, and release.

State and persistence: Benchmark static configuration is updated per run. No output files are created, but the tests print throughput data.

Dependencies and integration points: Ensures the benchmark tool can be called in-process and that supported factories do not throw under representative parameters.

Risks: These are performance smoke tests, not correctness tests. They can be slow and machine-dependent, especially with larger data sizes and native library availability.

Test signals: Confirms benchmark argument-free API paths, thread fan-out, coder release, and native skip behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestRawErasureCoderBenchmark.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestXORRawCoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestXORRawCoder.java

Purpose: Binds the shared XOR raw-coder test matrix to the pure Java XOR implementation.

Important APIs and types: Extends `TestXORRawCoderBase` and selects `XORRawErasureCoderFactory` for both encoder and decoder factory fields.

Control flow: Setup assigns factories. Inherited tests cover 10x1 data erasure, parity erasure, data unit 5 erasure, too-many-erasure failure, bad input, and bad output cases across mixed direct and heap buffers.

State and persistence: Uses inherited in-memory chunk and coder state only.

Dependencies and integration points: Validates the Java XOR raw coder factory used by codec registry fallback paths.

Risks: The class has no custom assertions; all behavior is inherited. Factory asymmetry issue in the base does not affect this symmetric class.

Test signals: Standard Java XOR coverage for recoverability, invalid erasures, corruption handling, and buffer compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestXORRawCoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestXORRawCoderBase.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestXORRawCoderBase.java

Purpose: Shared XOR raw-coder matrix for one-parity recovery and negative cases.

Important APIs and types: Extends `TestRawCoderBase` and defines tests using `prepare()`, `testCodingDoMixAndTwice()`, `testCodingWithErasingTooMany()`, `testCodingWithBadInput()`, and `testCodingWithBadOutput()`.

Control flow: Positive tests cover 10 data plus 1 parity with erased data index 0, erased parity index 0, and erased data index 5. The too-many-erasure test removes one data and one parity unit and expects failure. The bad-input/output test corrupts buffers around data index 5 and expects failures.

State and persistence: Uses inherited mutable erased indexes, chunk data, coders, and direct/heap buffer modes.

Dependencies and integration points: Inherited by Java XOR, native XOR, and intended Java/native interoperability wrappers.

Risks: XOR's single-parity contract means this base should stay limited to one recoverable erasure in positive tests. Random corruption can affect exact failure location.

Test signals: Covers single-erasure XOR recovery, error handling, and mixed ByteBuffer operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestXORRawCoderBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestXORRawCoderInteroperable1.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestXORRawCoderInteroperable1.java

Purpose: Intended interoperability test with Java XOR encoding and native XOR decoding.

Important APIs and types: Extends `TestXORRawCoderBase`, requires `ErasureCodeNative.isNativeCodeLoaded()`, sets `encoderFactoryClass = XORRawErasureCoderFactory.class`, and sets `decoderFactoryClass = NativeXORRawErasureCoderFactory.class`.

Control flow: Setup selects asymmetric factories and enables dumps. Inherited XOR tests perform single-erasure recovery and negative scenarios with mixed buffer modes.

State and persistence: In-memory chunks only; native decoder resources would be used if the decoder factory field is honored.

Dependencies and integration points: Intended to ensure Java XOR parity can be consumed by native XOR decoder.

Risks: Because `TestRawCoderBase.createDecoder()` uses `encoderFactoryClass`, this class may currently instantiate the Java factory for decoding too, reducing true interoperability coverage.

Test signals: Useful inherited XOR matrix under native availability, but asymmetric factory behavior should be audited.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestXORRawCoderInteroperable1.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestXORRawCoderInteroperable2.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestXORRawCoderInteroperable2.java

Purpose: Intended interoperability test with native XOR encoding and Java XOR decoding.

Important APIs and types: Extends `TestXORRawCoderBase`, gates on `ErasureCodeNative.isNativeCodeLoaded()`, sets `encoderFactoryClass = NativeXORRawErasureCoderFactory.class`, and sets `decoderFactoryClass = XORRawErasureCoderFactory.class`.

Control flow: Setup selects factories and verbose dumps, then inherited XOR tests encode, erase, decode, and compare under direct/heap buffer modes and negative cases.

State and persistence: In-memory test chunks and potentially native encoder resources; no filesystem state.

Dependencies and integration points: Intended to prove native XOR output is decodable by Java XOR implementation.

Risks: The base decoder factory bug means this may currently run native-to-native rather than native-to-Java. Native library absence skips the class.

Test signals: Provides native-gated XOR matrix coverage, but true interop signal depends on fixing or confirming base factory use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/rawcoder/TestXORRawCoderInteroperable2.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/KVGenerator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/KVGenerator.java

Purpose: Test utility that generates pseudo-random `BytesWritable` key/value pairs for TFile seek and benchmark workloads.

Important APIs and types: Constructor accepts `Random`, sorted flag, key/value/word-length `RandomDistribution.DiscreteRNG` instances, and dictionary size. Public `next(BytesWritable key, BytesWritable value, boolean dupKey)` emits a key and value.

Control flow: The constructor builds a random dictionary and initializes `lastKey`. `fillKey()` chooses a key length, fills bytes after a 4-byte prefix with dictionary words, increments the prefix if sorted ordering would otherwise regress, copies the prefix, and stores `lastKey`. `fillValue()` fills values similarly. `dupKey` reuses the previous key.

State and persistence: Maintains random dictionary, prefix bytes, and last key across calls. No file persistence.

Dependencies and integration points: Used by TFile seek/performance tests with `RandomDistribution` and Hadoop `BytesWritable`.

Risks: Prefix overflow throws at runtime. Sorted ordering depends on comparing bytes after the fixed prefix only.

Test signals: Supports realistic repeated-word key/value generation for compression and seek behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/KVGenerator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/KeySampler.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/KeySampler.java

Purpose: Generates random seek keys whose first four bytes fall between a TFile reader's first and last keys.

Important APIs and types: Constructor accepts `Random`, first and last `RawComparable` keys, and a key-length `DiscreteRNG`. Public `next(BytesWritable key)` fills a sampled key.

Control flow: The constructor converts first and last key prefixes to integers. `next()` chooses a length of at least four bytes, fills random bytes, then overwrites the first four bytes with a random integer in `[min, max)`, encoded big-endian.

State and persistence: Holds prefix bounds, random source, and length generator. No durable state.

Dependencies and integration points: Used by `TestTFileSeek` to drive `Scanner.lowerBound()` with keys likely to hit the TFile key range.

Risks: `random.nextInt(max - min)` fails if first and last prefixes are equal. It only constrains the prefix, so sampled suffixes may miss exact keys.

Test signals: Provides randomized seek workload with bounded key distribution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/KeySampler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/NanoTimer.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/NanoTimer.java

Purpose: Small nanosecond-resolution stopwatch and formatting helper used by TFile performance-style tests.

Important APIs and types: Provides `start()`, `stop()`, `read()`, `reset()`, `isStarted()`, `toString()`, and static `nanoTimeToString(long)`. Uses `System.nanoTime()`.

Control flow: `start()` records the current time only when not already started. `stop()` accumulates elapsed time only when started. `read()` and `toString()` return error indicators if never started. Formatting scales nanoseconds through microseconds, milliseconds, seconds, minutes, hours, and days.

State and persistence: Maintains `last`, `started`, and cumulative elapsed nanoseconds in memory. It is not thread-safe and has no persistence.

Dependencies and integration points: Used by `TestTFileSeek` for file creation and seek timing.

Risks: `read()` does not include an active interval until `stop()` is called. The class is intended for tests, not production metrics.

Test signals: Enables human-readable timing output for benchmark tests; no assertions directly target it in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/NanoTimer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/RandomDistribution.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/RandomDistribution.java

Purpose: Test helper library for discrete random distributions used by TFile key/value workload generators.

Important APIs and types: Defines `DiscreteRNG` plus implementations `Flat`, `Zipf`, and `Binomial`. `Flat` samples uniformly from `[min,max)`. `Zipf` builds compressed cumulative probability tables. `Binomial` builds a cumulative binomial distribution.

Control flow: Constructors validate ranges and precompute distribution tables. `nextInt()` methods draw a random double or integer and map it through direct arithmetic or binary search over cumulative probabilities.

State and persistence: Each distribution stores a `Random` and immutable parameters/tables. No durable state.

Dependencies and integration points: Consumed by `KVGenerator`, `KeySampler`, and TFile seek/comparison tests to vary key, value, and dictionary word lengths.

Risks: Zipf table approximation depends on epsilon and may be imprecise for large ranges. Binomial probability math can suffer floating-point limits. Invalid argument handling is constructor-only.

Test signals: Provides repeatable workload shaping when seeded; not directly asserted here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/RandomDistribution.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestCompression.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestCompression.java

Purpose: Regression tests for configurable LZO codec loading in TFile compression support, including valid alternate codec and invalid class behavior.

Important APIs and types: Uses `Compression.Algorithm.LZO.conf`, `Compression.Algorithm.CONF_LZO_CLASS`, `Compression.Algorithm.LZO.getCodec()`, `LambdaTestUtils.intercept()`, and JUnit lifecycle hooks.

Control flow: `@BeforeAll` enables test reload behavior for the LZO codec and `@AfterAll` disables it. One test sets the configured LZO class to Hadoop `DefaultCodec` and asserts the loaded codec class name. The other sets an invalid class, expects an `IOException` containing the class name, and rethrows if the cause is not `ClassNotFoundException`.

State and persistence: Mutates static compression configuration shared by the JVM, then resets reload flag after all tests.

Dependencies and integration points: Guards HADOOP-11418 behavior in the TFile compression layer.

Risks: Static configuration mutation can leak if lifecycle cleanup fails. The test uses DefaultCodec as a dummy LZO substitute.

Test signals: Covers custom codec class resolution and misconfiguration diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestCompression.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFile.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFile.java

Purpose: Broad functional tests for TFile writer/reader basics, sorted and unsorted modes, duplicate keys, empty records, large values, prepared append streams, seeks, ranges, and metablocks.

Important APIs and types: Uses `TFile.Writer`, `TFile.Reader`, `Reader.Scanner`, `prepareAppendKey()`, `prepareAppendValue()`, `append()`, `createScanner()`, `createScannerByKey()`, `seekTo()`, `lowerBound()`, `upperBound()`, `prepareMetaBlock()`, and `getMetaBlock()`.

Control flow: Helpers write empty records, duplicated sorted records, a large 3 MB value, known-length stream records, and unknown-length stream records. Read helpers validate keys/values and seek/range behavior. `basicWithSomeCodec()` runs sorted tests for none and gz. `unsortedWithSomeCodec()` scans unsorted files. `testMetaBlocks()` writes named metadata blocks, rejects duplicates, reads them back, and rejects missing names.

State and persistence: Creates local filesystem TFiles under a temp root and deletes them after each scenario. Writers and readers own stream state.

Dependencies and integration points: Exercises Hadoop `FileSystem`, compression, TFile scanner locations, and metadata block APIs.

Risks: `readPrepWithUnknownLength()` has a loop condition `i < start`, so unknown-length read validation is effectively skipped. Large values stress memory and local disk.

Test signals: Strong format-level smoke coverage, with a noted gap around unknown-length reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileByteArrays.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileByteArrays.java

Purpose: Base byte-array TFile test suite for sorted files, parameterized by compression and comparator subclasses.

Important APIs and types: Uses `TFile.Writer.append(byte[],...)`, `TFile.Reader`, `Reader.Scanner`, `Scanner.entry()`, `seekTo()`, `lowerBound()`, `createScannerByKey()`, metadata block APIs, and static helpers `writeRecords()`, `readRecords()`, and `composeSortedKey()`.

Control flow: Setup creates a sorted writer with a configured codec and comparator. Tests cover empty files, one/two/multiple block boundaries, locate/seek behavior, reading key/value in different orders, repeated key reads, writer-not-closed failures, duplicate metablocks, missing metablocks, write-after-metablock rejection, single-read value behavior, bad codecs, empty/random file open failures, oversized keys, out-of-order keys, negative offsets/lengths, compression effectiveness, and nonzero output stream position.

State and persistence: Writes temp files named by subclass, tracks expected records per block, and deletes unless `skip` is set.

Dependencies and integration points: Base for gz, none, LZO, and jclass comparator variants; uses `ZlibFactory` to adjust expected block counts.

Risks: Many negative tests catch broad `Exception`, reducing diagnostic precision. Block-count expectations depend on native zlib presence and compression output.

Test signals: High-value regression coverage for TFile byte-array API, scanner behavior, validation, and format errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileByteArrays.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileComparator2.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileComparator2.java

Purpose: Verifies TFile can use a Java class comparator for serialized `LongWritable` keys and preserve comparator-defined sorted order.

Important APIs and types: Uses comparator string `jclass:` plus `LongWritable.Comparator`, `TFile.Writer.prepareAppendKey()`, `prepareAppendValue()`, `LongWritable.write()`, `TFile.Reader.Scanner`, and `BytesWritable`.

Control flow: The test writes 10,000 entries with keys equal to `(i - NENTRY/2)^3`, which are sorted numerically by `LongWritable.Comparator`, and values `value-i`. It reads sequentially and asserts values appear in the original loop order.

State and persistence: Creates a gzip-compressed temp TFile and reads it back. The file is not explicitly deleted in this test.

Dependencies and integration points: Exercises jclass comparator loading and Writable binary comparator semantics inside TFile sorted writing.

Risks: Missing cleanup can leave temp files. The test validates values rather than decoded keys, so comparator order is inferred from successful write/read sequencing.

Test signals: Covers non-memcmp comparator integration with serialized Hadoop Writable keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileComparator2.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileComparators.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileComparators.java

Purpose: Negative tests for invalid TFile comparator specifications.

Important APIs and types: Uses `TFile.Writer` construction with comparator strings, Hadoop `FileSystem`, and JUnit `fail()`.

Control flow: Setup opens a temp output stream. Tests attempt to construct writers with an unsupported comparator name, a nonexistent `jclass`, and an existing class that is not a `RawComparator`. Each expects an exception and fails if writer construction succeeds.

State and persistence: Creates a temp path and deletes it after each test. Output stream and writer fields are mutable; `closeOutput()` exists but is unused by the tests.

Dependencies and integration points: Guards comparator-name parsing and reflection-based comparator loading in TFile writer construction.

Risks: Tests catch broad exceptions and print stack traces, so they do not assert exact exception types or messages. The output stream may remain open until filesystem cleanup.

Test signals: Ensures invalid comparator configurations are rejected early.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileComparators.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileJClassComparatorByteArrays.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileJClassComparatorByteArrays.java

Purpose: Runs the byte-array TFile base suite with gzip compression and a custom Java class comparator.

Important APIs and types: Extends `TestTFileByteArrays`, calls `init(GZ, "jclass: org.apache.hadoop.io.file.tfile.MyComparator")`, and defines package-local `MyComparator implements RawComparator<byte[]>, Serializable`.

Control flow: `setUp()` configures the inherited writer to use the custom comparator before delegating to the base setup. All test methods are inherited from `TestTFileByteArrays`. `MyComparator` delegates both raw and object comparisons to `WritableComparator.compareBytes()`.

State and persistence: Uses the inherited temp file lifecycle and compression/block-count settings.

Dependencies and integration points: Exercises TFile jclass comparator reflection against a comparator defined in the test source file.

Risks: The comparator string includes whitespace after `jclass:`, so parser trimming behavior is implicitly tested. The package-local comparator class is shared by none-codec jclass tests too.

Test signals: Confirms custom comparator loading works with the full byte-array behavior matrix.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileJClassComparatorByteArrays.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileLzoCodecsByteArrays.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileLzoCodecsByteArrays.java

Purpose: Runs the byte-array TFile base suite with LZO compression when LZO support is available.

Important APIs and types: Extends `TestTFileByteArrays`, uses `Compression.Algorithm.LZO.isSupported()`, and configures `init(LZO, "memcmp", 2605, 2558)`.

Control flow: `setUp()` sets `skip` if LZO is unsupported and prints `Skipped`; otherwise it initializes LZO compression, memcmp comparator, sampled block record counts, and delegates to base setup. Inherited tests then cover sorted byte-array behavior, negative cases, metadata, seeks, and compression checks.

State and persistence: Uses inherited temp file handling. If skipped, setup avoids writer creation and teardown avoids deletion.

Dependencies and integration points: Guards optional LZO integration in TFile without failing environments lacking the codec.

Risks: Expected records-per-block values are hard-coded and may drift with codec implementation changes. Skip is manual rather than JUnit assumptions.

Test signals: Full byte-array TFile behavior matrix under LZO when supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileLzoCodecsByteArrays.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileLzoCodecsStreams.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileLzoCodecsStreams.java

Purpose: Runs the streaming TFile API base suite with LZO compression when supported.

Important APIs and types: Extends `TestTFileStreams`, uses `Compression.Algorithm.LZO.isSupported()`, and configures inherited writer with LZO plus `memcmp`.

Control flow: `setUp()` sets `skip` when LZO is unavailable; otherwise it initializes compression/comparator and calls the base streaming setup. Inherited tests write keys and values through `prepareAppendKey()` and `prepareAppendValue()` with known and unknown lengths, then exercise negative stream-state and size validation cases.

State and persistence: Uses inherited temp file and writer lifecycle. Skipped tests return early via the inherited `skip` flag.

Dependencies and integration points: Covers optional LZO support in TFile's streaming append APIs.

Risks: Manual skip prints output rather than reporting an assumption. Coverage is absent on hosts without LZO.

Test signals: Streaming API regression coverage under LZO compression when the codec is installed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileLzoCodecsStreams.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileNoneCodecsByteArrays.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileNoneCodecsByteArrays.java

Purpose: Runs the byte-array TFile base suite with no compression and memcmp ordering.

Important APIs and types: Extends `TestTFileByteArrays` and configures `Compression.Algorithm.NONE.getName()`, `memcmp`, and expected records per block of 24 and 24.

Control flow: `setUp()` initializes the inherited compression/comparator/block-count settings and delegates to base setup. All behavior comes from `TestTFileByteArrays`, including sorted scans, seeks, block index checks, metadata, negative input cases, and compression effectiveness checks adjusted for none compression.

State and persistence: Uses inherited local temp file lifecycle and writer/reader state.

Dependencies and integration points: Provides baseline TFile behavior without codec effects, useful for isolating format and scanner logic.

Risks: Small expected block counts are tied to the fixed test key/value payload and block size. No custom tests beyond inherited suite.

Test signals: Baseline no-codec coverage for the full byte-array TFile contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileNoneCodecsByteArrays.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileNoneCodecsJClassComparatorByteArrays.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileNoneCodecsJClassComparatorByteArrays.java

Purpose: Runs the byte-array TFile base suite with no compression and the custom `MyComparator` jclass comparator.

Important APIs and types: Extends `TestTFileByteArrays`, uses `Compression.Algorithm.NONE`, comparator string `jclass: org.apache.hadoop.io.file.tfile.MyComparator`, and expected block counts 24 and 24.

Control flow: `setUp()` configures inherited writer settings and calls the base setup. Inherited tests then exercise all byte-array sorted file, metadata, scanner, and negative behavior with a reflection-loaded comparator instead of direct memcmp.

State and persistence: Uses the inherited temp file named by subclass and deletes after each test.

Dependencies and integration points: Reuses the `MyComparator` class declared in `TestTFileJClassComparatorByteArrays.java`, so compilation/package visibility matter.

Risks: The comparator class lives in another test file; moving or renaming it breaks this test. No compression makes block sizing deterministic but still tied to payload sizes.

Test signals: Validates custom comparator behavior independent of compression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileNoneCodecsJClassComparatorByteArrays.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileNoneCodecsStreams.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileNoneCodecsStreams.java

Purpose: Runs the streaming TFile API base suite without compression.

Important APIs and types: Extends `TestTFileStreams` and configures `Compression.Algorithm.NONE` with `memcmp`.

Control flow: `setUp()` initializes inherited compression and comparator settings, then delegates to stream base setup. Inherited tests write records through prepared key/value streams with known, unknown, and mixed lengths; read them with byte-array helpers; and assert failures for missing values, value-before-key, length mismatches, oversized keys, repeated close, negative offsets, and compression checks.

State and persistence: Uses inherited temp file creation, writer state, and deletion in teardown.

Dependencies and integration points: Provides baseline coverage for TFile stream append semantics without codec buffering effects.

Risks: No custom assertions beyond base suite. Compression-not-working tests skip compressed-size comparison for none codec.

Test signals: Baseline streaming API regression coverage for uncompressed TFiles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileNoneCodecsStreams.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileSeek.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileSeek.java

Purpose: Performance-style test and command-line tool for TFile creation and random lower-bound seeking.

Important APIs and types: Uses `KVGenerator`, `KeySampler`, `RandomDistribution.Zipf/Flat`, `NanoTimer`, Commons CLI `Options`, `TFile.Writer`, `TFile.Reader`, and `Reader.Scanner.lowerBound()`.

Control flow: `setUp()` parses default or supplied options, configures FS buffer sizes, random distributions, and generators. `createTFile()` writes sorted random records until target file size. `seekTFile()` samples keys between first and last keys, performs lower-bound seeks, reads hit entries, and prints timing and hit/miss statistics. `testSeeks()` skips unsupported compression, then creates and reads according to options.

State and persistence: Writes a temp TFile under configurable root and deletes it in teardown. Options hold seed, codec, sizes, and operation mode.

Dependencies and integration points: Exercises TFile indexing, scanner lower bounds, compression support detection, and local filesystem buffering.

Risks: Timing output is environment-dependent. Random seed defaults to `System.nanoTime()`, reducing reproducibility. Miss-rate math divides by hits.

Test signals: Useful for seek performance smoke and scanner behavior under generated sorted data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileSeek.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileSeqFileComparison.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileSeqFileComparison.java

Purpose: Performance comparison tool and JUnit smoke test that writes and reads similar random workloads through TFile and SequenceFile under none, LZO, and gzip compression.

Important APIs and types: Defines `KVAppendable`, `KVReadable`, `TFileAppendable`, `TFileReadable`, `SeqFileAppendable`, `SeqFileReadable`, and option parser `MyOptions`. Uses `TFile.Writer/Reader`, `SequenceFile.Writer/Reader`, `Compression.Algorithm`, `BytesWritable`, Commons CLI, and Hadoop `Time`.

Control flow: Setup configures filesystem buffers and a random dictionary. `timeWrite()` generates random key/value lengths and dictionary-filled payloads until target file size. `timeRead()` scans all records. `compareRun()` runs SequenceFile write/read, TFile write/read twice, then SequenceFile again for each supported compression. `main()` supports standalone single-format create/read operations.

State and persistence: Creates performance files under a temp root and deletes them when read after creation. Options and dictionary are per test instance.

Dependencies and integration points: Bridges TFile, SequenceFile, Hadoop compression codecs, and filesystem buffering.

Risks: It is benchmark-like and prints timing rather than asserting throughput. CLI option definitions reuse `-o` for output buffer and key length, which may confuse parsing.

Test signals: Smoke coverage that both formats can write/read generated data with configured codecs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileSeqFileComparison.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileSplit.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileSplit.java

Purpose: Tests TFile split scanning by byte range and by record number, plus record-number/location conversion symmetry.

Important APIs and types: Uses `TFile.Writer`, `TFile.Reader`, `Reader.createScannerByByteRange()`, `createScannerByRecordNum()`, `getRecordNumNear()`, `getLocationByRecordNum()`, `getRecordNumByLocation()`, and `Reader.Scanner.getRecordNum()`.

Control flow: `createFile()` writes sorted records with a chosen compression. `readFile()` divides the file into ten byte ranges, scans each, asserts each split has records, and checks total rows equal reader entry count. `readRowSplits()` divides by record numbers and checks scanner record numbers before and after entry reads. `checkRecNums()` validates offset edge cases and random record/location symmetry. The test runs uncompressed 100k records and gzip 500k records.

State and persistence: Creates temp TFiles per compression and deletes them after each scenario.

Dependencies and integration points: Exercises TFile indexing used by MapReduce-style input splits and record-based scanners.

Risks: Large record counts can be slow. Random begin/end selection is nondeterministic.

Test signals: Strong coverage for split boundary correctness and record-number APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileSplit.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileStreams.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileStreams.java

Purpose: Base streaming API suite for TFile prepared key/value append streams, parameterized by compression subclasses.

Important APIs and types: Uses `TFile.Writer.prepareAppendKey()`, `prepareAppendValue()`, `TFile.Reader.Scanner`, `TestTFileByteArrays.readRecords()`, `WritableUtils`, and stream exceptions such as `EOFException`.

Control flow: Setup creates a writer with configured compression and comparator. Tests write no entries, one/two entries with known, unknown, and mixed key/value lengths, then read through byte-array helpers. Negative tests cover key without value, value without key, length mismatches, key/value too long or short, idempotent close, oversized 64K keys, negative read offsets, and compressed size checks.

State and persistence: Maintains writer/output stream fields and temp file path, closing and deleting in teardown unless skipped by subclasses.

Dependencies and integration points: Base for none and LZO stream variants, and indirectly validates TFile stream-state machine.

Risks: Many negative tests catch broad exceptions. Unknown-length read behavior has a TODO noting inconsistency around `getValueLength()`.

Test signals: High-value coverage of streaming writer state transitions and validation errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileStreams.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileUnsortedByteArrays.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileUnsortedByteArrays.java

Purpose: Tests TFile behavior when created without a comparator, so records are unsorted and searchable key operations are disallowed.

Important APIs and types: Uses `TFile.Writer` with `null` comparator, `TFile.Reader`, `Reader.Scanner`, AssertJ assertions, `createScanner()`, `createScannerByKey()`, `lowerBound()`, `upperBound()`, and `seekTo()`.

Control flow: Setup writes four deliberately out-of-order records and closes the file. Tests assert `reader.isSorted()` is false and entry count is four. Full scans verify insertion order and that key/value can be read in either order. Creating a scanner by key and performing lower-bound, upper-bound, or seek operations are expected to throw.

State and persistence: Creates a gzip-compressed temp file and deletes it after each test.

Dependencies and integration points: Guards the distinction between unsorted scan-only TFiles and sorted indexed TFiles.

Risks: Some unused fields and duplicate scan-range logic remain. Exceptions are broad, not type-specific.

Test signals: Confirms unsorted files remain sequentially readable while search APIs fail fast.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/file/tfile/TestTFileUnsortedByteArrays.java -->
