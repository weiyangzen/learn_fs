# Research: subset-b-007397

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestVersionedWritable.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestVersionedWritable.java

Purpose: JUnit coverage for Hadoop `VersionedWritable` serialization, inheritance, nested writable payloads, and version mismatch handling. The file defines local `VersionedWritable` fixtures and verifies that version bytes written by `VersionedWritable.write()` are enforced by `VersionedWritable.readFields()`.

Important APIs/types/functions: `SimpleVersionedWritable` extends `VersionedWritable` with random `int state`, static `VERSION = 1`, `write`, `readFields`, `read`, and `equals`. `AdvancedVersionedWritable` extends the simple fixture and adds UTF strings, `WritableUtils.writeString`, `writeCompressedString`, nested `SimpleVersionedWritable`, and string-array serialization. `SimpleVersionedWritableV2` overrides `getVersion()` to return `2`. Tests call `TestWritable.testWritable(...)` for round trips and `testVersionedWritable(before, after)` for mismatch assertions.

Control flow: round-trip tests serialize a fixture into `DataOutputBuffer`, reset a `DataInputBuffer` over the bytes, instantiate the same type through `ReflectionUtils` indirectly via `TestWritable`, and compare equality. The mismatch test serializes a V1 object, attempts to read it into a V2 object, expects `VersionMismatchException`, and fails if no exception is thrown.

State and persistence behavior: all state is in-memory test fixture state. Serialized format is version byte, then fixture fields. The advanced fixture persists multiple string encodings and a nested writable in sequence; ordering must match exactly on read. The random fields make object contents unpredictable but same-object round trip remains deterministic.

Dependencies and integration points: integrates with `VersionedWritable`, `VersionMismatchException`, `DataOutputBuffer`, `DataInputBuffer`, `WritableUtils`, and `TestWritable.testWritable`. It exercises Hadoop's binary Writable contract rather than filesystem or service state.

Risks and edge cases: `AdvancedVersionedWritable.equals()` calls `super.equals(o)` but ignores its return value, so a mismatch in inherited `state` would not fail equality if all subclass fields match. Tests print compression details to stdout. Because fixture version fields are static and mutable package-private/private, future tests that modify them could cross-contaminate if added.

Test signals: `testSimpleVersionedWritable` and `testAdvancedVersionedWritable` validate compatible serialization. `testSimpleVersionedWritableMismatch` validates exception behavior for incompatible versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestVersionedWritable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestWeakReferencedElasticByteBufferPool.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestWeakReferencedElasticByteBufferPool.java

Purpose: Parameterized JUnit coverage for `WeakReferencedElasticByteBufferPool`, validating direct and heap `ByteBuffer` pooling, capacity selection, insertion ordering, weak-reference pruning, and release behavior.

Important APIs/types/functions: `params()` returns `"direct"` and `"array"` modes. `initTestWeakReferencedElasticByteBufferPool` maps mode to `isDirect`. Tests call `getBuffer(boolean direct, int len)`, `putBuffer(ByteBuffer)`, `getCurrentBuffersCount(boolean)`, and `release()`. Helpers `createByteArray` and `validateBufferContent` fill and verify buffers.

Control flow: each parameterized test initializes a new pool and requests buffers of different capacities. The basic test writes random bytes into a buffer, flips it, reads bytes back, then returns the buffer and asserts `position()` resets to zero. Size-order tests return buffers to the pool and request smaller sizes to ensure the pool chooses the smallest suitable greater-or-equal capacity. Insertion-time tests request equal-size buffers and assert identity ordering with AssertJ `isSameAs`. GC tests null strong references, call `System.gc()`, then assert weakly referenced buffers are pruned or skipped.

State and persistence behavior: pool state is process-local. The test observes the pool's internal counts through public test-support API `getCurrentBuffersCount`. Weak references mean GC timing affects expected behavior; tests try to remove strong refs before collection.

Dependencies and integration points: depends on Java NIO `ByteBuffer`, AssertJ assertions, JUnit parameterization, and `HadoopTestBase`. It integrates directly with Hadoop's byte-buffer pool used by I/O paths that recycle direct or array-backed buffers.

Risks and edge cases: GC-sensitive assertions can be timing-sensitive on unusual JVMs. The local variable `buffer1`/`buffer2` nulling relies on the JIT not preserving hidden strong references. Tests do not cover mixed direct and array pools in the same method beyond parameterization.

Test signals: verifies initial type/capacity/position, count changes after `putBuffer` and `getBuffer`, FIFO ordering among equal capacities, clearing through `release`, and behavior after weak-reference collection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestWeakReferencedElasticByteBufferPool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestWritable.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestWritable.java

Purpose: Unit coverage for Hadoop `Writable`, primitive writable wrappers, comparator lookup/configuration, and `WritableComparator.newKey()` configuration propagation.

Important APIs/types/functions: `SimpleWritable` persists a random `int state` through `write` and `readFields`. `SimpleWritableComparable` adds `WritableComparable` and `Configurable` behavior. Static `testWritable(Writable before, Configuration conf)` serializes via `DataOutputBuffer`, deserializes through `ReflectionUtils.newInstance`, and asserts equality. `FrobComparator` and `Frob` register a custom comparator through `WritableComparator.define`.

Control flow: primitive and custom Writable tests call `testWritable`. Comparator tests fetch comparators with and without explicit `Configuration`, assert registered comparator type, and assert that configuration is retained or replaced as expected. `testShortWritableComparator` compares positive, negative, and equal cases both directly and through `WritableComparator.get`. `testConfigurableWritableComparator` gets a comparator for a configurable key, calls `newKey`, and checks the key inherits the comparator configuration.

State and persistence behavior: state is serialized in memory only. Comparator definitions are global static registry state inside `WritableComparator`; this file deliberately exercises cached comparator configuration behavior.

Dependencies and integration points: integrates with `DataInputBuffer`, `DataOutputBuffer`, `ReflectionUtils`, `WritableComparator`, `ByteWritable`, `ShortWritable`, `DoubleWritable`, `Configuration`, and the `Configurable` interface.

Risks and edge cases: static comparator cache state may interact with other tests for the same key class, though `Frob` is local. The method `testGetComparator` lacks `@Test`, so it may not run unless called elsewhere. `testShortWritable` constructs `ShortWritable((byte)256)`, which truncates to zero and may be intentional legacy behavior but is not a strong boundary check for `short`.

Test signals: confirms Writable round trips, short comparator semantics, comparator configuration caching/replacement, and propagation of config into configurable key instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestWritable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestWritableName.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestWritableName.java

Purpose: Unit coverage for `WritableName`, which maps short aliases to classes and resolves names with Hadoop serialization support.

Important APIs/types/functions: local `SimpleWritable` supplies a Writable target class. `SimpleSerializable` and `SimpleSerializer` provide a non-Writable class plus `Serialization` implementation. Tests exercise `WritableName.getClass`, `WritableName.setName`, `WritableName.addName`, and `SerializationFactory.getSerialization`.

Control flow: `testGoodName` resolves built-in alias `"long"`. `testSetName` assigns a canonical test alias to `SimpleWritable` and resolves it. `testAddName` adds an alternate alias while checking the original alias still works. `testAddNameSerializable` configures `io.serializations`, adds an alias for a serializable non-Writable type, and verifies `SerializationFactory` can resolve it both by alias and class name. `testBadName` expects an `IOException` mentioning the unknown name.

State and persistence behavior: alias mappings are process-local static state inside `WritableName`. There is no filesystem persistence; only `Configuration` controls serialization class discovery.

Dependencies and integration points: depends on `CommonConfigurationKeys.IO_SERIALIZATIONS_KEY`, `SerializationFactory`, `Serialization`, and `WritableName`. It validates that Writable-style aliases and generic serialization lookup coexist.

Risks and edge cases: static alias registration can leak between tests if names collide. The custom serializer returns null serializer/deserializer because only serializer discovery is tested. `assertTrue(false)` is used instead of `fail`.

Test signals: verifies built-in alias lookup, explicit name setting, alternate aliases, serializable class aliasing, and useful exception messages for missing names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestWritableName.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestWritableUtils.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestWritableUtils.java

Purpose: Boundary tests for variable-length integer encoding and `readVIntInRange`.

Important APIs/types/functions: `testValue(int val, int vintlen)` writes a value with `WritableUtils.writeVInt`, reads with `readVInt`, and compares expected byte length through buffer length, `getVIntSize`, and `decodeVIntSize`. `testReadInRange(long val, int lower, int upper, boolean expectSuccess)` writes a VLong and verifies `readVIntInRange` succeeds or throws.

Control flow: `testVInt` enumerates positive and negative thresholds around one-byte and multi-byte vint encodings: 12, 127, -112, -113, -128, 128, -129, 255, -256, 256, -257, 65535, -65536, 65536, -65537. It then checks inclusive range success, above-range failure, lower-bound zero success, negative failure, and too-large long failure.

State and persistence behavior: all state is in-memory `DataOutputBuffer`/`DataInputBuffer` byte arrays. Logging prints buffer bytes only under debug.

Dependencies and integration points: depends on `WritableUtils`, `BytesWritable`, `DataOutputBuffer`, `DataInputBuffer`, SLF4J, and JUnit assertions. This is core coverage for Hadoop's compact binary integer encoding shared by many Writables.

Risks and edge cases: `testReadInRange` catches any `IOException` as expected when `expectSuccess` is false and does not inspect message or exception subtype. The suite covers ints and one large long but does not exercise all long encoding boundaries.

Test signals: confirms byte-size calculation and decoding agree with actual serialized size, and that range enforcement rejects out-of-range and overflow values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/TestWritableUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/CompressDecompressTester.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/CompressDecompressTester.java

Purpose: Shared test harness for compressor/decompressor pair implementations. It defines reusable strategies for error handling, single-block round trips, empty block streams, and multi-block round trips.

Important APIs/types/functions: generic `CompressDecompressTester<T extends Compressor,E extends Decompressor>` stores immutable raw data, a builder of `TesterPair`, selected `CompressionTestStrategy` values, and a `PreAssertionTester` availability filter. Fluent APIs are `of`, `withCompressDecompressPair`, `withTestCases`, and `test`. Nested `TesterPair` owns compressor/decompressor instances and calls `reinit`, `end` on cleanup. `CompressionTestStrategy` contains `COMPRESS_DECOMPRESS_ERRORS`, `COMPRESS_DECOMPRESS_SINGLE_BLOCK`, `COMPRESS_DECOMPRESS_WITH_EMPTY_STREAM`, and `COMPRESS_DECOMPRESS_BLOCK`.

Control flow: `test()` finalizes pair list, filters unavailable native-dependent pairs through `isAvailable`, then runs each selected strategy against a defensive copy of the original data. Error strategy verifies `NullPointerException` and `ArrayIndexOutOfBoundsException` for both set-input and compress/decompress APIs. Single-block strategy drives `finish()`/`finished()` loops and verifies bytes. Empty-stream strategy closes a `BlockCompressorStream` without writes, checks codec-specific empty output sizes, and verifies decompression EOF. Block strategy chunks input into zlib-sized blocks, compresses each independently, then decompresses each stored compressed segment.

State and persistence behavior: no persistent state. Compressor and decompressor instances are stateful and are reset between strategy phases; `endAll` terminates them after testing.

Dependencies and integration points: integrates with `Compressor`, `Decompressor`, `BlockCompressorStream`, `BlockDecompressorStream`, codec-specific native availability checks for LZ4, Snappy, built-in zlib, native zlib, and Guava immutable collections.

Risks and edge cases: `isAvailable` uses `compressor.getClass().isAssignableFrom(Lz4Compressor.class)` style checks, which are reversed from the more common `X.class.isAssignableFrom(compressor.getClass())`; exact classes pass but subclasses may behave unexpectedly. Empty stream expected sizes are hard-coded by compressor class. The block strategy only exercises block mode when original data length exceeds the threshold.

Test signals: downstream tests use this harness to assert API contract failures, data integrity after compression/decompression, EOF for empty streams, and cleanup through `end()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/CompressDecompressTester.java -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestBZip2Codec.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestBZip2Codec.java

Purpose: Focused tests for `BZip2Codec.createInputStream` with explicit start/end offsets and `SplittableCompressionCodec.READ_MODE` behavior.

Important APIs/types/functions: test fixture creates `Configuration`, `FileSystem`, `BZip2Codec`, pooled `Decompressor`, and a temporary `.bz2` path. Helpers include `newCompressionStream`, `newAlternatingByteArray`, `assertCasesWhereReadDoesNotAdvanceStream`, `assertReadingAtPositionZero`, `assertReadingPastEndOfBlock`, `assertReadingWithContinuousMode`, and `assertRead`.

Control flow: setup creates local test path and obtains a decompressor from `CodecPool`; teardown returns it and deletes the file. The main test writes three BZip2 blocks with `BZip2TextFileWriter`, finds later block marker offsets through `BZip2Utils`, then opens split streams over different starts. In `BYBLOCK` mode it asserts initial position, read argument validation, unchanged positions on invalid/zero reads, block-boundary position reporting, and EOF. In `CONTINUOUS` mode it verifies reading from 0 or header length produces all data and leaves position at the header.

State and persistence behavior: writes a temporary compressed file under `test.build.data` or `target/data/TestBZip2Codec/input/test.txt.bz2`. Decompressor is pooled and explicitly returned. No long-lived persistence remains if teardown succeeds.

Dependencies and integration points: integrates with `BZip2Codec`, `SplitCompressionInputStream`, `SplittableCompressionCodec.READ_MODE`, `CodecPool`, `FSDataInputStream`, Hadoop `Path`/`FileSystem`, `BZip2TextFileWriter`, `BZip2Utils`, Guava `Bytes.concat`, Commons IO `IOUtils`, and AssertJ exception assertions.

Risks and edge cases: relies on deterministic block sizes from the test writer. Position semantics differ between `BYBLOCK` and `CONTINUOUS`, and the test documents current behavior including continuous mode not updating position after reads. Teardown assumes `tempFile` exists.

Test signals: validates split alignment, block marker positions, EOF, invalid read arguments, zero-length read behavior, and continuous-mode compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestBZip2Codec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestBlockDecompressorStream.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestBlockDecompressorStream.java

Purpose: Tests block decompression stream EOF and IO exception behavior using fake identity compressor/decompressor implementations.

Important APIs/types/functions: `testRead1`, `testRead2`, helper `testRead(int bufLen)`, and `testReadWhenIoExceptionOccure`. Uses `BlockCompressorStream`, `BlockDecompressorStream`, `FakeCompressor`, and `FakeDecompressor`.

Control flow: `testRead` optionally prefixes a 4-byte block-size header, closes a `BlockCompressorStream` without writing payload, asserts compressed output length is `bufLen + 4`, then reads through `BlockDecompressorStream` and expects `-1`. The IO exception test creates a file and wraps a `FileInputStream` whose `read()` always throws, then asserts `BlockDecompressorStream.read()` propagates an IOException containing `"File blocks missing"` rather than returning EOF.

State and persistence behavior: mostly in-memory byte arrays. One temporary file named `testReadWhenIOException` is created in the working directory and deleted in `finally`.

Dependencies and integration points: tests Hadoop block compression stream framing and read behavior independent of real codecs. Uses Java `ByteBuffer` to encode an integer prefix.

Risks and edge cases: fixed working-directory file name may collide in parallel test execution. The test name has a typo. Fake decompressor behavior is not representative of all decompressor state machines.

Test signals: ensures empty block streams return EOF cleanly and underlying IO errors are not swallowed as `-1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestBlockDecompressorStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestCodec.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestCodec.java

Purpose: Broad integration test suite for Hadoop compression codecs and their interaction with Writable data, SequenceFile, MapFile, split reads, gzip interoperability, native zlib toggles, and `CodecPool` reuse.

Important APIs/types/functions: `codecTest` is the core round-trip helper for a codec class name and random `RandomDatum` records. `testSplitableCodec` plus `writeSplitTestFile` validate splittable BZip2 reads. `gzipReinitTest` and `codecTestWithNOCompression` verify compression-level propagation. `sequenceFileCodecTest` validates block-compressed SequenceFiles. `codecTestMapFile` covers MapFile seek/read with Snappy. Gzip-specific helpers include `GzipConcatTest`, `testGzipCodecWrite`, `verifyGzipFile`, and `uncompressGzipOutput`.

Control flow: codec round-trip tests instantiate codecs through `ReflectionUtils`, generate deterministic key/value bytes from a seed, compress through `CompressionOutputStream`, assert leased compressor counts return to baseline, decompress through `CompressionInputStream`, compare original and decoded `RandomDatum` objects and hash behavior, then repeat byte-at-a-time reads. Codec-specific tests cover Default, Gzip with native and built-in paths, BZip2 Java and native, Snappy, LZ4 normal/high-compression setting, Deflate, and Gzip zlib parameters. Split tests write a BZip2 file with numbered records and sample random split starts, verifying two sequential full lines. SequenceFile tests write/read block-compressed records at multiple record counts and block sizes. Gzip tests compare Hadoop Gzip output and input with `java.util.zip` streams, concatenated gzip members, long decompressed streams, empty input, and `CodecPool` separation from zlib raw compressor/decompressor classes.

State and persistence behavior: creates local temporary files with `GenericTestUtils.getTempPath`, SequenceFile paths, MapFile paths, and gzip files. Most helpers delete files on success; a few rely on verify helpers or local FS cleanup. It toggles global `ZlibFactory` native-loaded state and restores native zlib in `@AfterEach`.

Dependencies and integration points: uses `CompressionCodecFactory`, `CodecPool`, `DefaultCodec`, `GzipCodec`, `BZip2Codec`, `SnappyCodec`, `Lz4Codec`, `DeflateCodec`, `ZStandardCodec`, zlib built-in/native classes, `SequenceFile`, `MapFile`, `RandomDatum`, `LineReader`, Hadoop `FileSystem`, Java `GZIPInputStream`/`GZIPOutputStream`, and native availability assumptions.

Risks and edge cases: global native zlib toggling can affect concurrently running tests. Random seeds are logged but not fixed in many cases. Some file names are relative (`SequenceFileCodecTest.<codecClass>`). Native-dependent branches may skip significant behavior on machines without native libraries. Long gzip overflow test writes over 4 GiB of decompressed characters and can be expensive.

Test signals: validates data integrity for major codecs, no compressor/decompressor leaks, split-compatible BZip2 positioning, SequenceFile/MapFile compressed storage, codec factory selection, gzip compatibility with Java streams, native and built-in gzip class selection, compressor reinitialization, and pool separation for gzip versus raw zlib.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestCodecFactory.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestCodecFactory.java

Purpose: Tests `CompressionCodecFactory` discovery, extension matching, class/name lookup, service-loaded defaults, configured codec lists, and override precedence.

Important APIs/types/functions: local `BaseCodec` implements `CompressionCodec` with stub stream/compressor/decompressor methods and default extension `.base`. Subclasses define `BarCodec` (`bar`), `FooBarCodec` (`.foo.bar`), `FooCodec` (`.foo`), and `NewGzipCodec` (`.gz`). Helper `setClasses` configures codec classes through `CompressionCodecFactory.setCodecClasses`; `checkCodec` asserts expected class or null.

Control flow: `testFinding` first checks default factory behavior for unknown `.bar`, built-in gzip/bzip2/deflate by extension, class name, short name, and case variants. It then configures an empty explicit list and verifies service-loaded codecs still include gzip, bzip2, snappy, and lz4 but not `BarCodec`. It configures custom classes and checks longest extension match (`.foo.bar` before `.bar`/`.foo`), case-insensitive extensions, name lookup, and class lookup. Finally it overrides `.gz` with `NewGzipCodec` and checks whitespace-padded `io.compression.codecs` parsing does not throw.

State and persistence behavior: configuration-local state only; no files are written. Factory instances build in-memory mappings from configuration and service loader state.

Dependencies and integration points: integrates with `CompressionCodecFactory`, `CommonConfigurationKeys.IO_COMPRESSION_CODECS_KEY`, Hadoop `Path`, and default codec service discovery.

Risks and edge cases: stub codecs return null for stream creation and should only be used for factory lookup. Raw extension `"bar"` lacks a leading dot, exercising factory normalization. Service loader contents must include expected built-ins or assertions fail.

Test signals: verifies default and configured lookup paths, case-insensitivity, custom extension precedence, short-name matching, override behavior, and robust config parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestCodecFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestCodecPool.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestCodecPool.java

Purpose: Unit and concurrency coverage for `CodecPool` leasing, returning, duplicate returns, configuration reinitialization, and `@DoNotPool` compressor/decompressor behavior.

Important APIs/types/functions: setup creates a configured `DefaultCodec`. Tests call `CodecPool.getCompressor`, `returnCompressor`, `getLeasedCompressorsCount`, `getDecompressor`, `returnDecompressor`, and leased decompressor counts. Reflection inspects compressor field `level`. Gzip built-in compressor/decompressor tests use `AlreadyClosedException` interception through `LambdaTestUtils`.

Control flow: pool count tests lease two instances, return them one by one, and verify counts including duplicate return. duplicate-return tests return the same instance twice, then request 10 instances and assert they are all unique, preventing same object from being checked out multiple times. Configuration test returns a compressor created with one compression level, then gets a compressor for another codec configuration and reflects its level. Multi-threaded tests use producer/consumer callables and a blocking queue to lease and return compressors/decompressors across threads, then assert no leases remain. `@DoNotPool` tests return built-in gzip compressor/decompressor and assert later use through gzip streams throws `AlreadyClosedException`.

State and persistence behavior: global/static pool state is exercised and mutated; tests reset by returning leased objects. In-memory gzip data is generated for decompressor tests.

Dependencies and integration points: depends on `DefaultCodec`, `GzipCodec`, zlib built-in gzip classes, `ZlibFactory`, `ReflectionUtils`, Java executors/queues, and Hadoop `LambdaTestUtils`.

Risks and edge cases: pool state is global, so parallel tests involving same codec types could interact. Reflection over field name `level` is implementation-sensitive. Timeouts protect against deadlock but the multi-thread tests use a long await.

Test signals: validates lease accounting, thread-safe return paths, duplicate return defense, configuration reinitialization, and enforcement that non-poolable gzip wrappers are closed after return.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestCodecPool.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestCompressionStreamReuse.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestCompressionStreamReuse.java

Purpose: Tests whether compression output streams can be reset and reused for fresh compressed members across BZip2, Gzip, and ZStandard codecs.

Important APIs/types/functions: public tests call `resetStateTest` for `BZip2Codec`, `GzipCodec`, `ZStandardCodec`, and Gzip with zlib compression level/strategy parameters. `resetStateTest` uses `RandomDatum.Generator`, `CompressionOutputStream.resetState`, and matching `CompressionInputStream`.

Control flow: helper instantiates a codec by class name, generates `count` key/value records into `DataOutputBuffer`, writes them through a compression stream, calls `finish`, `flush`, and `resetState`, regenerates the same bytes from the same seed, resets the compressed buffer, creates a new output stream, writes/compresses again, then decompresses and compares every decoded key/value pair with the regenerated original data.

State and persistence behavior: all buffers are in memory. The method creates a new output stream after reset rather than reusing the same Java object for the second write, but the test still targets codec reset behavior and multi-member correctness.

Dependencies and integration points: integrates with `BZip2Codec`, `GzipCodec`, `ZStandardCodec`, `ZlibFactory`, `RandomDatum`, Hadoop data buffers, and Java buffered data streams.

Risks and edge cases: streams are not consistently closed with try-with-resources, so failures could leak in-memory stream state. It does not assert exact compressed framing, only decompressed equality. The spelling "reseting" appears in logs only.

Test signals: confirms compressed output after reset can be decompressed and matches regenerated deterministic Writable records for all targeted codecs and Gzip parameterized configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestCompressionStreamReuse.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestCompressorDecompressor.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestCompressorDecompressor.java

Purpose: Shared compressor/decompressor coverage for Snappy, LZ4, and built-in zlib implementations through `CompressDecompressTester`.

Important APIs/types/functions: `testCompressorDecompressor`, `testCompressorDecompressorWithExceedBufferLimit`, and static `generate(int size)`. It uses pairs `SnappyCompressor/SnappyDecompressor`, `Lz4Compressor/Lz4Decompressor`, and `BuiltInZlibDeflater/BuiltInZlibInflater`.

Control flow: first test generates 44 KiB of low-entropy bytes and runs single-block, block, error-contract, and empty-stream strategies. Second test generates 100 KiB and creates Snappy/LZ4 pairs with 64 KiB internal buffers, then runs block, error, and empty-stream strategies to exercise inputs larger than the internal buffer.

State and persistence behavior: deterministic static `Random(12345L)` supplies data; compressor objects are terminated by the shared harness. No file persistence.

Dependencies and integration points: depends on the generic harness in `CompressDecompressTester`, codec-specific compressor/decompressor classes, Guava `ImmutableSet`, and `GenericTestUtils.assertExceptionContains` in catch blocks.

Risks and edge cases: catch blocks call `GenericTestUtils.assertExceptionContains` with a message that likely is not contained in thrown exceptions, causing failures to surface but with odd semantics. Static random data advances between tests, so exact bytes depend on test order.

Test signals: validates common compressor API contracts and round-trip behavior for built-in non-native compressor paths and large-buffer scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestCompressorDecompressor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestCompressorStream.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestCompressorStream.java

Purpose: Regression test for `CompressorStream.close()` ensuring the stream marks itself closed even when `finish()` throws an `IOException`.

Important APIs/types/functions: the test class itself extends `CompressorStream`, creates static file/output stream resources for `tmp.txt`, overrides `finish()` to throw, and tests `close()`.

Control flow: static initializer creates `tmp.txt` and a `FileOutputStream`. Constructor calls `super(fop)`. `testClose` creates the subclass, calls `close`, catches the expected IOException, then asserts the inherited `closed` flag is true and deletes the file.

State and persistence behavior: creates a file named `tmp.txt` in the working directory and deletes it at test end. Static stream/file state is shared for the class lifetime.

Dependencies and integration points: directly exercises protected/internal state of `CompressorStream` via subclassing in the same package.

Risks and edge cases: static file output stream may remain open; deletion can be platform-sensitive. Fixed file name is unsafe under parallel execution. The test only checks `closed` flag, not whether the underlying `FileOutputStream` is closed.

Test signals: verifies `close()` handles exceptional `finish()` by still transitioning to closed state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestCompressorStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestDecompressorStream.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestDecompressorStream.java

Purpose: Tests `DecompressorStream` read and skip behavior using an identity fake decompressor over a known ASCII string.

Important APIs/types/functions: fixture fields are `ByteArrayInputStream bytesIn`, `Decompressor decompressor`, and `DecompressorStream decompressorStream`. Tests are `testReadOneByte`, `testReadBuffer`, and `testSkip`.

Control flow: setup wraps the test string in a byte stream and creates `DecompressorStream(bytesIn, new FakeDecompressor(), 20, 13)`. One-byte test reads each character and expects `EOFException` after content. Buffer test reads chunks up to 32 bytes, validates substrings, and expects EOF on further read. Skip test skips 12 bytes, reads expected characters, skips 10 more, reads another expected character, then expects EOFException when skipping past end.

State and persistence behavior: all state is in memory and recreated before each test.

Dependencies and integration points: integrates `DecompressorStream` with `FakeDecompressor`, AssertJ assertions, and JUnit. It tests stream wrapper behavior independent from actual codec algorithms.

Risks and edge cases: `new String(buf, 0, bytesRead)` uses platform default charset, but data is ASCII. Fake decompressor returns pass-through data and does not model all production decompressor edge cases.

Test signals: validates byte reads, buffer reads, skip semantics, and EOF exception behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestDecompressorStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestGzipCodec.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestGzipCodec.java

Purpose: Focused tests for resettable `GzipCodec` output streams, gzip member concatenation via reset, write overload coverage, and idempotent finish/reset behavior.

Important APIs/types/functions: fixture creates `GzipCodec` with `new Configuration(false)`. Constants `DATA1` and `DATA2` are small UTF-8 strings. Tests use `CompressionOutputStream`, `CompressionInputStream`, `GZIPInputStream`, `DataOutputBuffer`, and `DataInputBuffer`.

Control flow: `testSingleCompress` writes one string, finishes/closes, and verifies Java `GZIPInputStream` reads it. `testResetCompress` writes `DATA1`, finishes, calls `resetState`, writes `DATA2`, finishes/closes, then reads through Hadoop `CompressionInputStream` and expects concatenated content. `testWriteOverride` writes a full byte array, a random slice, and a single byte, then replays the random seed while reading to verify all output. `testIdempotentResetState` calls `finish` and `resetState` repeatedly without extra data and asserts only the original payload appears.

State and persistence behavior: in-memory buffers only. Random seed is logged and immediately reused for verification in `testWriteOverride`.

Dependencies and integration points: integrates `GzipCodec`, Hadoop compression streams, Java gzip stream compatibility, UTF-8 encoding, and Hadoop data buffers.

Risks and edge cases: `testWriteOverride` relies on a random slice length that may be zero; the assertion still follows generated length. The tests do not cover native zlib path selection directly; broader `TestCodec` handles that.

Test signals: verifies Hadoop gzip output is Java-readable, reset creates readable multi-member gzip data, write overloads are implemented, and repeated finish/reset calls do not emit empty extra members.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/TestGzipCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/bzip2/BZip2TextFileWriter.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/bzip2/BZip2TextFileWriter.java

Purpose: Test utility for generating BZip2-compressed text data with predictable block boundaries.

Important APIs/types/functions: public constant `BLOCK_SIZE` derives from `CBZip2OutputStream.getAllowableBlockSize(MIN_BLOCKSIZE) + 1`. Constructors accept a Hadoop `Path`/`Configuration` or raw `OutputStream`. Public methods are `writeManyRecords`, `writeRecord`, `write(String)`, `write(byte[])`, and `close`.

Control flow: the raw-output constructor writes the Hadoop BZip2 header via `BZip2Codec.writeHeader`, then wraps the stream in `CBZip2OutputStream` with minimum block size. If construction fails, it closes the raw stream and rethrows. `writeManyRecords` validates record count and delimiter, divides total size evenly, and writes all records with any remainder in the last record. `writeRecord` writes alternating `'a'` and `'b'` bytes until delimiter space remains, then writes the delimiter. Alternation prevents run-length encoding from collapsing the intended block-boundary size.

State and persistence behavior: owns a single `CBZip2OutputStream` and writes compressed data to caller-provided file/stream. No static mutable state beyond constants.

Dependencies and integration points: used by `TestBZip2Codec` and `TestBZip2TextFileWriter`. Integrates with Hadoop `Path`/`FileSystem`, `BZip2Codec`, and low-level `CBZip2OutputStream`.

Risks and edge cases: the block-size logic depends on CBZip2 internals and comments document that the extra byte is required by allowable-block offset checks. It closes only the compressed wrapper in `close`, which should close the underlying stream through wrapper semantics.

Test signals: enables precise tests around BZip2 block marker offsets and split stream behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/bzip2/BZip2TextFileWriter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/bzip2/BZip2Utils.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/bzip2/BZip2Utils.java

Purpose: Test utility for locating BZip2 block marker offsets after the first block in a compressed file or stream.

Important APIs/types/functions: final utility class with private constructor. Public overloads `getNextBlockMarkerOffsets(Path, Configuration)` and `getNextBlockMarkerOffsets(InputStream)` return `List<Long>` offsets.

Control flow: path overload resolves the filesystem, opens the file, and delegates to stream overload. Stream overload wraps raw input in `CBZip2InputStream` with `READ_MODE.BYBLOCK`, repeatedly calls `skipToNextBlockMarker`, records `getProcessedByteCount`, and returns offsets.

State and persistence behavior: no persistent state. It closes the input wrapper and path-opened stream through try-with-resources.

Dependencies and integration points: integrates with `CBZip2InputStream`, `SplittableCompressionCodec.READ_MODE.BYBLOCK`, Hadoop `Path`/`FileSystem`, and test writer-generated data.

Risks and edge cases: intended for tests and exposes offsets according to CBZip2 processed-byte accounting. It omits the first block by design and returns only following block markers.

Test signals: used by BZip2 tests to assert expected number and positions of block boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/bzip2/BZip2Utils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/bzip2/TestBZip2TextFileWriter.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/bzip2/TestBZip2TextFileWriter.java

Purpose: Unit coverage for `BZip2TextFileWriter` block-boundary behavior.

Important APIs/types/functions: fixture owns `ByteArrayOutputStream rawOut` and `BZip2TextFileWriter writer`; delimiter is a single NUL byte. Helper `getNextBlockMarkerOffsets` delegates to `BZip2Utils`.

Control flow: setup creates the in-memory writer. Teardown nulls `rawOut` and closes writer. Tests write records of size `BLOCK_SIZE`, `BLOCK_SIZE + 1`, `2 * BLOCK_SIZE`, and `2 * BLOCK_SIZE + 1`, close the writer, then assert the number of following block markers is 0, 1, 1, and 2 respectively.

State and persistence behavior: in-memory compressed bytes only. Writer is explicitly closed in tests and again in teardown.

Dependencies and integration points: tests `BZip2TextFileWriter` plus `BZip2Utils` and indirectly `CBZip2OutputStream`/`CBZip2InputStream`.

Risks and edge cases: double close may rely on idempotent stream close behavior. It checks marker count, not exact offsets. The delimiter prevents zero-length record content ambiguity.

Test signals: validates the writer's exported `BLOCK_SIZE` corresponds to actual BZip2 block creation thresholds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/bzip2/TestBZip2TextFileWriter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/bzip2/TestBzip2CompressorDecompressor.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/bzip2/TestBzip2CompressorDecompressor.java

Purpose: Native bzip2 compressor/decompressor round-trip and multi-thread smoke coverage.

Important APIs/types/functions: `before()` assumes `Bzip2Factory.isNativeBzip2Loaded`. `testCompressDecompress` uses `Bzip2Compressor` and `Bzip2Decompressor`. `generate` creates deterministic low-entropy data. `testBzip2CompressDecompressInMultiThreads` uses `MultithreadedTestUtil`.

Control flow: single-thread test generates 64 KiB, asserts compressor not finished, sets input, checks `getBytesRead` before compression, calls `finish`, compresses into a same-size buffer, asserts bytes read and compressed size smaller than original, decompresses into original-size output, compares arrays, and resets both objects. Multi-thread test starts 10 testing threads, each running the same method, and waits up to 60 seconds.

State and persistence behavior: no persistent state. Static random generator is shared, including across multi-threaded calls, which can interleave data generation.

Dependencies and integration points: depends on native bzip2 availability, Hadoop bzip2 compressor/decompressor classes, JUnit assumptions, and Hadoop multithreaded test utility.

Risks and edge cases: static `Random` is shared across threads and not synchronized. Tests are skipped when native bzip2 is unavailable. Compressed output buffer assumes compressed data is smaller than raw low-entropy input.

Test signals: validates native bzip2 basic state counters, compression ratio, byte equality after decompression, reset behavior, and concurrent use of separate compressor/decompressor instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/bzip2/TestBzip2CompressorDecompressor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/lz4/TestLz4CompressorDecompressor.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/lz4/TestLz4CompressorDecompressor.java

Purpose: LZ4 compressor/decompressor API contract, round-trip, stream integration, multithread, and backwards compatibility tests.

Important APIs/types/functions: tests cover `Lz4Compressor`, `Lz4Decompressor`, `BlockCompressorStream`, `BlockDecompressorStream`, `SequenceFile.Reader`, and `MultithreadedTestUtil`. Helper `generate` produces deterministic low-entropy byte arrays.

Control flow: early tests assert null input and invalid index/length exceptions for compressor and decompressor `setInput`, `compress`, and `decompress`. Size tests feed input larger than the default buffer and assert nonzero compressed output. `testCompressDecompress` compresses 54 KiB, checks byte counters, decompresses by compressed size, asserts finished and byte equality, resets, and checks no remaining bytes. Empty stream test closes a block compressor without writes and expects 4 bytes of framing and EOF on decompression. Stream test writes 100 KiB through block compression streams and reads back through block decompression. Multithread test runs the core round trip in 10 threads. Compatibility test opens a resource `/lz4/sequencefile` created by the old native codec and verifies 2000 key/value records.

State and persistence behavior: mostly in-memory. Compatibility test reads a classpath resource and does not write. Static random generator is shared.

Dependencies and integration points: covers LZ4 codec primitives, Hadoop block compression streams, SequenceFile compatibility, Hadoop filesystem access for resource path, and multithreaded testing.

Risks and edge cases: static random is shared across threads. Some tests use broad `try/catch` with `fail` messages instead of `assertThrows`. Stream read uses a single `read(result)` call, which assumes the full buffer is filled in one call.

Test signals: validates argument validation, state counters, compression/decompression equality, empty block framing, stream wrappers, concurrent instances, and compatibility with pre-HADOOP-17292 LZ4 sequence files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/lz4/TestLz4CompressorDecompressor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/snappy/TestSnappyCompressorDecompressor.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/snappy/TestSnappyCompressorDecompressor.java

Purpose: Snappy compressor/decompressor contract, direct decompression, stream integration, multi-thread, and native-format compatibility tests.

Important APIs/types/functions: tests use `SnappyCompressor`, `SnappyDecompressor`, `SnappyDirectDecompressor`, `BlockCompressorStream`, `BlockDecompressorStream`, direct `ByteBuffer`s, and nested `BytesGenerator`.

Control flow: validation tests assert null and array-bound exceptions for input and output APIs. Main round trip compresses 54 KiB with max compressed length `32 + size + size / 6`, verifies byte counters, decompresses and compares bytes, then resets. Empty stream test checks 4-byte empty block output and EOF. Block compression test manually compresses input in chunks sized for block overhead. Small-buffer test drains compressor and decompressor loops with 512-byte output buffers. Direct block tests compress data, feed direct input/output buffers to `SnappyDirectDecompressor`, and compare byte-by-byte for sizes from 4 KiB to 1 MiB. Stream test uses block compressor/decompressor streams over 100 KiB. Multithread test runs the main round trip in 10 threads. Compatibility test decodes a hard-coded hex payload compressed by the previous native Snappy codec and verifies raw bytes with the current direct decompressor.

State and persistence behavior: all data is in memory. `BytesGenerator` has static `Random(12345L)` and a fixed nibble-byte cache; generated data depends on call order and may interleave in multi-threaded tests.

Dependencies and integration points: integrates with Snappy codec primitives, block compression stream framing, Commons Codec `Hex`, Java direct buffers, and Hadoop multithreaded utilities.

Risks and edge cases: static random is shared and not synchronized. Some manual block compression writes full block arrays instead of exact compressed lengths, so it mainly asserts nonempty output. Several tests use broad exception handling rather than precise assertions.

Test signals: validates Snappy API error behavior, byte counters, finish/remaining state, empty stream framing, direct decompression, small output buffers, stream wrappers, concurrent use, and compatibility with legacy native Snappy bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/snappy/TestSnappyCompressorDecompressor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/zlib/TestZlibCompressorDecompressor.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/zlib/TestZlibCompressorDecompressor.java

Purpose: Native zlib compressor/decompressor tests for generic compressor contracts, configuration, compression levels, direct decompression, dictionaries, factory settings, gzip built-in error handling, and multithreaded operation.

Important APIs/types/functions: class-level `before()` assumes `ZlibFactory.isNativeZlibLoaded`. Tests use `ZlibCompressor`, `ZlibDecompressor`, `ZlibDirectDecompressor`, `ZlibFactory`, `BuiltInGzipDecompressor`, generic `CompressDecompressTester`, and helper `compressDecompressZlib`.

Control flow: generic harness tests run zlib pair through single-block, block, error, and empty-stream strategies, including a large-buffer constructor path. Configuration tests obtain compressors/decompressors from `ZlibFactory`, run repeated round trips, and reinitialize. Compression-level test sets `zlib.compress.level` to `FOUR`. Direct test compresses with Java `DeflaterOutputStream`, then verifies direct-buffer decompression for sizes from 1 byte to 1 MiB. Dictionary test checks null and invalid-range exceptions. Factory test verifies default and set compression level/strategy values. Built-in gzip decompressor test checks argument exceptions, counters, reset/end, and invalid gzip header bytes. Multi-thread test runs the core zlib round trip in 10 threads.

State and persistence behavior: in-memory only. Native availability is global. Static random generator is shared across tests and threads. Factory configuration lives in `Configuration` objects.

Dependencies and integration points: integrates native zlib, Java zlib streams, Hadoop compression interfaces, `DecompressorStream`, `DataInputBuffer`, and multithread test utilities.

Risks and edge cases: class-level native assumption skips all tests without native zlib. Static random is unsynchronized in threaded tests. Helper predicates for dictionary exceptions return booleans but the test does not assert their return values, weakening coverage. Some branches assert native zlib loaded in `else`, producing failure instead of skip if assumption were bypassed.

Test signals: validates zlib round trips, API error contracts, native direct decompression, config-driven level/strategy, gzip header validation errors, counter behavior, reset/reinit, and multi-threaded independent instances.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/zlib/TestZlibCompressorDecompressor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/zstd/TestZStandardCompressorDecompressor.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/zstd/TestZStandardCompressorDecompressor.java

Purpose: Comprehensive tests for ZStandard codec compression/decompression, stream wrappers, direct decompression, reset-after-error behavior, worker configuration, and bundled test-resource compatibility.

Important APIs/types/functions: static setup loads `/zstd/test_file.txt` and `/zstd/test_file.txt.zst` and configures file buffer size. Tests use `ZStandardCodec`, `ZStandardCompressor`, `ZStandardDecompressor`, `ZStandardDirectDecompressor`, `CompressorStream`, `DecompressorStream`, `CompressionInputStream`, `CompressionOutputStream`, `FileUtils`, and `ZstdException`. Helpers are `generate`, `compressDecompressLoop`, and `bytesToHex`.

Control flow: resource-based compression test reads an uncompressed file, writes each byte through codec output stream, asserts compressor counters/finished state, then decompresses and compares bytes. Exception tests use `assertThrows` for null and invalid bounds on compressor/decompressor APIs. Large input test drives `compress` in a loop until finished. Stream tests compress/decompress 100 KiB through generic compressor/decompressor streams and verify equality. Finish/reset test writes three segments separated by `finish`/`resetState` and reads the concatenated result. Multi-thread test runs core round trip in 10 threads. Direct tests compress through `CompressorStream`, use direct byte buffers, and verify output for several sizes. Resource decompression tests read known `.zst` resource through codec streams. Corrupted-data regression drops the first 10 compressed bytes, expects `ZstdException`, resets the decompressor, and ensures valid input can be set and decompressed without `BufferOverflowException`. Worker tests verify workers > 0 round-trip, negative workers rejected, default workers zero, and `reinit` picks up a new worker count.

State and persistence behavior: reads bundled resources; otherwise uses in-memory buffers. Static `Configuration`, `File` references, and `Random` are shared. Compression worker settings are per-configuration and can be applied through compressor `reinit`.

Dependencies and integration points: integrates Hadoop `ZStandardCodec`, luben zstd Java library exceptions, Hadoop common file buffer keys, generic compression interfaces, direct buffers, test resources, and multithreaded testing.

Risks and edge cases: static random is shared across tests and threaded calls. Several stream reads use a single `read(result)` for full data, which assumes enough bytes are returned at once. Hex string comparisons are less direct than array comparisons and can be expensive for large data. Worker behavior depends on zstd-jni support.

Test signals: validates byte-for-byte round trips, API argument validation, finish/reset multi-frame behavior, direct-buffer decompression, decompression of known fixture files, recovery after corrupted input, compression worker configuration, and compressor reinitialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/compress/zstd/TestZStandardCompressorDecompressor.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/BufferAllocator.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/BufferAllocator.java

Purpose: Test utility abstraction for allocating direct or heap `ByteBuffer`s for erasure-code tests, with simple and sliced allocation strategies.

Important APIs/types/functions: abstract `BufferAllocator` stores `usingDirect` and exposes protected `isUsingDirect()` plus abstract `allocate(int bufferLen)`. `SimpleBufferAllocator` allocates a fresh heap or direct buffer each time. `SlicedBufferAllocator` owns one large `overallBuffer` and returns slices until capacity is exhausted, then falls back to fresh allocation.

Control flow: simple allocator delegates directly to `ByteBuffer.allocateDirect` or `ByteBuffer.allocate`. Sliced allocator checks remaining capacity as `overallBuffer.capacity() - overallBuffer.position()`, sets limit to `position + bufferLen`, creates a slice, advances position, and returns the slice. If insufficient capacity remains, it allocates a new independent buffer of requested type.

State and persistence behavior: `SlicedBufferAllocator` persists cursor state in `overallBuffer.position()` and mutates its limit during allocation. No external persistence.

Dependencies and integration points: used by erasure-code tests that need controlled direct/heap buffers and sometimes contiguous sliced views to exercise raw coder behavior.

Risks and edge cases: after setting `overallBuffer.limit(position + bufferLen)`, the allocator does not restore the limit to capacity. The next available-space check uses capacity, but setting position beyond current limit can be sensitive unless previous operations permit it; current pattern advances to the limit each time. The class is not thread-safe.

Test signals: provides deterministic direct/heap allocation and fallback behavior for higher-level erasure coder tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/BufferAllocator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/TestCodecRawCoderMapping.java -->
## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/TestCodecRawCoderMapping.java

Purpose: Tests mapping from erasure-code codec names to raw encoder/decoder implementations, including defaults, dedicated config keys, fallback lists, invalid coder names, and native enable/disable behavior.

Important APIs/types/functions: uses `CodecUtil.createRawEncoder`, `createRawDecoder`, codec names from `ErasureCodeConstants`, coder options `(6 data, 3 parity)`, config keys like `IO_ERASURECODE_CODEC_RS_RAWCODERS_KEY`, `IO_ERASURECODE_CODEC_RS_LEGACY_RAWCODERS_KEY`, `IO_ERASURECODE_CODEC_XOR_RAWCODERS_KEY`, and `IO_ERASURECODE_CODEC_NATIVE_ENABLED_KEY`. It asserts concrete raw coder classes for RS, RS legacy, XOR, and native variants.

Control flow: setup creates a fresh `Configuration`. Default test creates RS encoder/decoder and expects native RS coders when native erasure code is loaded, otherwise Java RS coders; RS legacy always maps to legacy Java coders. Dedicated-key test sets dummy factory names for RS and RS legacy and expects creation failures with message fragments. Fallback test sets RS coder list to Java RS then native RS and expects Java RS chosen. Legacy fallback confirms RS legacy defaults. Invalid-codec test sets XOR list to invalid name then valid XOR factory and expects valid XOR coders. Native-enabled test assumes native code, verifies RS/XOR native coders by default, then disables native in configuration and expects Java RS/XOR coders.

State and persistence behavior: configuration-local only. Native availability is process/global but only read through `ErasureCodeNative.isNativeCodeLoaded`.

Dependencies and integration points: integrates with Hadoop erasure-code `CodecUtil`, raw coder factories/classes, `GenericTestUtils`, JUnit assumptions, and configuration keys. This is a contract test for how HDFS/client erasure coding selects raw implementations.

Risks and edge cases: one expected exception message for RS legacy contains `"codec: rs"` rather than `"rs-legacy"`, reflecting current behavior or a brittle message check. Native-enabled test is skipped without native erasure-code support. It does not call `release()` on created raw coder instances, if those implementations allocate resources.

Test signals: validates default and configured raw coder selection, fallback order, invalid factory skipping, native disable override, and useful failure when only invalid factories are configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/io/erasurecode/TestCodecRawCoderMapping.java -->
