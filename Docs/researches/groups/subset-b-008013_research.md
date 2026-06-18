# subset-b-008013 Research

Grouped source research for Apache Ozone HDDS erasure-code raw coders, their focused test harnesses, and selected HDDS framework configuration/runtime support files. Each source file is represented by a marker-delimited section so the reconciliation lane can split the report into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/ECChunk.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/ECChunk.java

## Purpose
`ECChunk` is the lightweight chunk wrapper used by the erasure-code layer to pass either full buffers or slices of buffers into raw encoders and decoders. It normalizes byte arrays into `ByteBuffer` and carries an `allZero` flag used by lower-level coder utilities to avoid depending on caller-filled data for known-zero chunks.

## Important APIs, Types, and Functions
The class exposes constructors for `ByteBuffer`, `ByteBuffer` plus offset/length, `byte[]`, and `byte[]` plus offset/length. Important methods are `getBuffer()`, `isAllZero()`, `setAllZero(boolean)`, static `toBuffers(ECChunk[])`, and test-oriented `toBytesArray()`. The offset/length ByteBuffer constructor duplicates the source, sets position and limit, and slices to isolate the visible range.

## Control Flow
Construction is a direct wrapping flow with no background work. `toBuffers` iterates through chunks, preserving `null` entries for erased or unused inputs, while `toBytesArray` marks, drains remaining bytes into a new array, and resets the position.

## State and Persistence Behavior
State is only the wrapped `ByteBuffer` reference and the mutable `allZero` flag. There is no persistence; buffer content and position are owned by the caller/coder interaction and may advance during encode/decode calls.

## Dependencies and Integration Points
The class depends only on `java.nio.ByteBuffer` and integrates with `RawErasureEncoder`, `RawErasureDecoder`, `CoderUtil.toBuffers`, and the erasure-code tests that compare `ECChunk` payloads.

## Risks and Test Signals
Risks include shared mutable ByteBuffer state, callers expecting `toBytesArray()` to consume without position changes, and offset/length errors causing `IllegalArgumentException` from ByteBuffer bounds. Tests should cover byte-array wrapping, sliced ByteBuffer wrapping, `null` preservation in arrays, all-zero flag handling through `CoderUtil`, and position stability after `toBytesArray()`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/ECChunk.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/package-info.java

## Purpose
This package descriptor documents `org.apache.ozone.erasurecode` as Apache Ozone erasure-coding utilities imported initially from Apache Hadoop.

## Important APIs, Types, and Functions
It has no executable API. It applies `@InterfaceAudience.Private` and `@InterfaceStability.Unstable` to the package.

## Control Flow
There is no runtime control flow.

## State and Persistence Behavior
No state is owned. The file affects generated documentation and compile-time package annotations.

## Dependencies and Integration Points
It depends on HDDS annotation classes and declares that the erasure-code package is internal and unstable for downstream API consumers.

## Risks and Test Signals
Risk is limited to annotation drift: changing audience or stability would alter the intended compatibility contract. Build and javadoc/package annotation checks are sufficient signals.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/AbstractNativeRawDecoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/AbstractNativeRawDecoder.java

## Purpose
`AbstractNativeRawDecoder` is the shared base for native raw decoders. It adapts Ozone's `RawErasureDecoder` state objects to the Hadoop native erasure-code accessor shape and enforces read-lock protection around native decoder state.

## Important APIs, Types, and Functions
The class extends `RawErasureDecoder`, owns a protected `ReentrantReadWriteLock decoderLock`, implements `doDecode(ByteBufferDecodingState)` and `doDecode(ByteArrayDecodingState)`, declares `performDecodeImpl(...)`, and returns `true` from `preferDirectBuffer()`.

## Control Flow
The direct-buffer path records input and output positions into offset arrays, acquires `decoderLock.readLock()`, calls subclass `performDecodeImpl` with buffers, offsets, decode length, erased indexes, and outputs, then releases the lock. The byte-array path logs a `PerformanceAdvisory`, converts byte arrays into direct buffers, delegates to the ByteBuffer path, and copies direct output bytes back into caller arrays.

## State and Persistence Behavior
Persistent state is the lock; native coder state is held by subclasses. There is no disk persistence. The lock protects native structures against concurrent release and decode, although only read-side locking is in this base.

## Dependencies and Integration Points
It depends on `ECReplicationConfig`, `ByteBufferDecodingState`, `ByteArrayDecodingState`, Hadoop `PerformanceAdvisory`, and subclass implementations such as `NativeRSRawDecoder` and `NativeXORRawDecoder`.

## Risks and Test Signals
Risks include copy-back mistakes in byte-array conversion, direct buffer allocation overhead, native release races if subclasses do not use the write lock, and offset/position mismatch with Hadoop native accessors. Tests should cover direct and heap inputs, sliced buffers, decode after release, native fallback behavior, and concurrent release/decode stress where available.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/AbstractNativeRawDecoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/AbstractNativeRawEncoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/AbstractNativeRawEncoder.java

## Purpose
`AbstractNativeRawEncoder` is the shared base for native raw encoders. It converts Ozone encode state into native-accessor arguments and protects native encoder state with a read/write lock.

## Important APIs, Types, and Functions
The class extends `RawErasureEncoder`, owns protected `ReentrantReadWriteLock encoderLock`, implements `doEncode(ByteBufferEncodingState)` and `doEncode(ByteArrayEncodingState)`, declares `performEncodeImpl(ByteBuffer[], int[], int, ByteBuffer[], int[])`, and prefers direct buffers.

## Control Flow
The direct path records input and output positions, locks `encoderLock.readLock()`, invokes the subclass native implementation, and unlocks. The byte-array path logs a performance advisory, clones heap arrays to direct buffers, encodes through the direct path, and copies each direct output back into its caller-provided output array.

## State and Persistence Behavior
Only lock state is owned by the base class. Native resources live in concrete Hadoop native encoder wrappers and are released by subclasses.

## Dependencies and Integration Points
It integrates with `NativeRSRawEncoder`, `NativeXORRawEncoder`, `ByteBufferEncodingState`, `ByteArrayEncodingState`, and Hadoop native ISA-L accessors through subclass hooks.

## Risks and Test Signals
The main risks are native lifecycle races, missing output copy-back, and performance surprises when heap arrays silently allocate direct buffers. Test signals include native RS/XOR parity correctness, direct and heap paths, sliced buffers, release idempotence, and fallback to Java coders when native construction fails.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/AbstractNativeRawEncoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/ByteArrayDecodingState.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/ByteArrayDecodingState.java

## Purpose
`ByteArrayDecodingState` stores all per-call decode metadata for byte-array based raw decoders.

## Important APIs, Types, and Functions
It extends `DecodingState` and owns `byte[][] inputs`, `int[] inputOffsets`, `int[] erasedIndexes`, `byte[][] outputs`, and `int[] outputOffsets`. Constructors either validate caller arrays and initialize zero offsets or accept precomputed offsets from a ByteBuffer conversion. Key methods are `convertToByteBufferState()`, `checkInputBuffers(byte[][])`, and `checkOutputBuffers(byte[][])`.

## Control Flow
Construction finds the first non-null input to define `decodeLength`, validates counts and erased/output shape through `DecodingState`, then enforces equal input/output lengths. Conversion clones non-null inputs into direct buffers and allocates direct outputs for native-friendly decoding.

## State and Persistence Behavior
The state is per decode call and not retained beyond the caller's stack except during method execution. Output arrays are caller-owned and mutated by decoders.

## Dependencies and Integration Points
It depends on `CoderUtil.cloneAsDirectByteBuffer` and `ByteBufferDecodingState`. It is used by `RawErasureDecoder` heap-array decode and by native decoders converting heap arrays to direct buffers.

## Risks and Test Signals
Risks include assuming full array length instead of logical offsets in public constructors, insufficient valid inputs, and output length mismatch. Tests should cover erased/null inputs, redundant null inputs, too few valid inputs, mismatched lengths, and heap-to-direct native conversion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/ByteArrayDecodingState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/ByteArrayEncodingState.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/ByteArrayEncodingState.java

## Purpose
`ByteArrayEncodingState` stores per-call encode metadata for heap-array raw encoders.

## Important APIs, Types, and Functions
It extends `EncodingState`, owns input/output arrays plus input/output offsets, and implements `convertToByteBufferState()` and `checkBuffers(byte[][])`. The public constructor uses the first input's length as `encodeLength` and initializes offsets to zero.

## Control Flow
Construction validates data/parity buffer counts and equal lengths. Conversion clones every input array range into a direct ByteBuffer and allocates direct output buffers for native encoders.

## State and Persistence Behavior
All state is transient per encode call. Encoder implementations mutate caller output arrays and may read from caller input arrays.

## Dependencies and Integration Points
It is created by `RawErasureEncoder.encode(byte[][], byte[][])` and by `ByteBufferEncodingState.convertToByteArrayState()` for heap-backed ByteBuffers.

## Risks and Test Signals
Risks include `null` inputs being rejected for encode, full-array length assumptions, and output offsets only being honored by conversion/internal constructors. Tests should cover bad counts, length mismatches, heap ByteBuffer offset conversions, and native heap-array fallback.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/ByteArrayEncodingState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/ByteBufferDecodingState.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/ByteBufferDecodingState.java

## Purpose
`ByteBufferDecodingState` is the per-call decode state for ByteBuffer inputs and outputs.

## Important APIs, Types, and Functions
It extends `DecodingState` and records `ByteBuffer[] inputs`, `ByteBuffer[] outputs`, `int[] erasedIndexes`, `decodeLength`, and `usingDirectBuffer`. It implements `convertToByteArrayState()`, `checkInputBuffers(ByteBuffer[])`, and `checkOutputBuffers(ByteBuffer[])`.

## Control Flow
The constructor finds the first non-null input, adopts its remaining bytes as decode length and direct/heap mode, validates parameter counts, checks all non-null inputs for identical remaining length and directness, and requires all outputs to be non-null with matching length/directness. Conversion exposes heap-backed arrays with `arrayOffset() + position()` offsets.

## State and Persistence Behavior
State exists for one decode call. The top-level decoder advances non-null input positions after decoding; state methods themselves mostly use absolute reads and offset metadata.

## Dependencies and Integration Points
It is instantiated by `RawErasureDecoder.decode(ByteBuffer[], int[], ByteBuffer[])` and feeds Java and native decoder implementations. Heap conversion assumes buffers are array-backed.

## Risks and Test Signals
Risks include mixing direct and heap buffers, using read-only or non-array heap buffers with conversion, too few valid inputs, and output count mismatch with erased indexes. Tests should include direct/heap parity, sliced buffers, position advancement, redundant null inputs, and invalid buffer shapes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/ByteBufferDecodingState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/ByteBufferEncodingState.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/ByteBufferEncodingState.java

## Purpose
`ByteBufferEncodingState` stores per-call encode metadata for ByteBuffer raw encoders.

## Important APIs, Types, and Functions
It extends `EncodingState`, owns `ByteBuffer[] inputs`, `ByteBuffer[] outputs`, and `usingDirectBuffer`, and implements `convertToByteArrayState()` plus `checkBuffers(ByteBuffer[])`.

## Control Flow
Construction uses the first input's remaining length and directness as the contract for all buffers, validates input/output counts, and rejects null, length-mismatched, or mixed directness buffers. Conversion maps heap-backed ByteBuffers to underlying arrays with offsets.

## State and Persistence Behavior
The state is transient per encode call. `RawErasureEncoder` advances input positions after the actual encode, while encoder implementations write outputs using absolute puts.

## Dependencies and Integration Points
It feeds `RSRawEncoder`, `XORRawEncoder`, and native encoder base classes. It integrates with `ByteArrayEncodingState` when heap ByteBuffers need byte-array Java implementations.

## Risks and Test Signals
Risks include non-array heap ByteBuffers failing conversion, direct/heap mixing, and callers expecting outputs to be flipped automatically. Test signals include direct and heap encoding, sliced buffers with non-zero positions, bad count/length failures, and final input positions at end.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/ByteBufferEncodingState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/CoderUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/CoderUtil.java

## Purpose
`CoderUtil` contains package-private helper routines shared by raw coder implementations and state converters.

## Important APIs, Types, and Functions
Important helpers include `getEmptyChunk(int)`, `resetBuffer(ByteBuffer,int)`, `resetBuffer(byte[],int,int)`, `resetOutputBuffers(...)`, `toBuffers(ECChunk[])`, `cloneAsDirectByteBuffer(byte[],int,int)`, `findFirstValidInput(T[])`, and `getValidIndexes(T[])`. It owns a grow-only static zero-filled `emptyChunk` cache.

## Control Flow
Output reset methods copy zeros from the cached empty chunk. `getEmptyChunk` returns the existing cache if large enough, otherwise synchronizes and grows it with a second length check. `toBuffers` unwraps chunks and zeroes buffers marked `allZero`. Conversion helpers allocate direct buffers and copy source data.

## State and Persistence Behavior
The only persistent state is the process-local static `emptyChunk` array. It is intentionally reused and can grow but should not shrink.

## Dependencies and Integration Points
It integrates with all raw coders, `ECChunk`, and state conversion classes. The tests include a concurrency-focused check that the zero cache does not shrink when requests race.

## Risks and Test Signals
Risks include exposing a shared mutable zero array inside the package, concurrency regressions in cache growth, position changes while zeroing ByteBuffers, and failing to honor `ECChunk.allZero`. Test signals are `TestCoderUtil`, raw coder output reset behavior, all-zero chunk decoding, and concurrent calls to `getEmptyChunk`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/CoderUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/DecodingState.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/DecodingState.java

## Purpose
`DecodingState` is the shared base for decode state validation across byte-array and ByteBuffer decoders.

## Important APIs, Types, and Functions
It stores `RawErasureDecoder decoder` and `int decodeLength`. Its `checkParameters(T[] inputs, int[] erasedIndexes, T[] outputs)` validates total input count, erased output count, and maximum erasures.

## Control Flow
Validation checks that `inputs.length` equals data plus parity units, `erasedIndexes.length` equals `outputs.length`, and erasures do not exceed parity units.

## State and Persistence Behavior
No persistent state exists. Subclasses fill fields for one decode invocation.

## Dependencies and Integration Points
It is used by `ByteArrayDecodingState` and `ByteBufferDecodingState`, and its rules are relied on by `RawErasureDecoder` before concrete coders run.

## Risks and Test Signals
Risks are incomplete validation: erased index bounds and duplicate indexes are not checked here. Test signals include bad input count, too many erasures, output count mismatches, and invalid erased indexes surfaced by concrete coders.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/DecodingState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/DummyRawDecoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/DummyRawDecoder.java

## Purpose
`DummyRawDecoder` is a no-op decoder used for plumbing and negative/placeholder tests.

## Important APIs, Types, and Functions
It extends `RawErasureDecoder`, exposes only a constructor, and overrides both `doDecode` overloads with empty bodies.

## Control Flow
All normal validation and input position advancement happen in `RawErasureDecoder`; the concrete decode operation intentionally writes nothing.

## State and Persistence Behavior
It has no mutable state beyond inherited replication config.

## Dependencies and Integration Points
It is created by `DummyRawErasureCoderFactory` and used by `TestDummyRawCoder` to verify framework behavior around no-op coders.

## Risks and Test Signals
Risk is accidental production selection if registry/provider configuration treats `dummy` as a usable codec. Test signals ensure dummy outputs remain empty/zero and that dummy factory names do not collide with real coders.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/DummyRawDecoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/DummyRawEncoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/DummyRawEncoder.java

## Purpose
`DummyRawEncoder` is the no-op encoder paired with the dummy raw coder factory.

## Important APIs, Types, and Functions
It extends `RawErasureEncoder`, provides a constructor, and overrides `doEncode(ByteArrayEncodingState)` and `doEncode(ByteBufferEncodingState)` with no work.

## Control Flow
Framework validation and input position advancement still occur in `RawErasureEncoder`; only parity generation is skipped.

## State and Persistence Behavior
It owns no state.

## Dependencies and Integration Points
It integrates with `DummyRawErasureCoderFactory` and dummy coder tests.

## Risks and Test Signals
Risk is accidental use as a real encoder, which would produce unchanged parity outputs. Tests should keep dummy usage explicit and verify no-op behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/DummyRawEncoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/DummyRawErasureCoderFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/DummyRawErasureCoderFactory.java

## Purpose
This factory registers/creates the dummy raw coder pair for tests or placeholder codec wiring.

## Important APIs, Types, and Functions
It implements `RawErasureCoderFactory`, defines `CODER_NAME = "dummy_dummy"` and `DUMMY_CODEC_NAME = "dummy"`, and implements `createEncoder`, `createDecoder`, `getCoderName`, and `getCodecName`.

## Control Flow
Factory methods instantiate new dummy encoder/decoder instances using the provided `ECReplicationConfig`.

## State and Persistence Behavior
No mutable state is kept; all instances are created on demand.

## Dependencies and Integration Points
It is visible to the registry if included as a service provider and is directly used by dummy coder tests.

## Risks and Test Signals
Risks include coder-name conflicts in `CodecRegistry` and accidental production exposure. Test signals include registry conflict handling, factory type assertions, and dummy encode/decode no-op tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/DummyRawErasureCoderFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/EncodingState.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/EncodingState.java

## Purpose
`EncodingState` is the shared base for raw encoder per-call validation.

## Important APIs, Types, and Functions
It stores `RawErasureEncoder encoder` and `int encodeLength`. Its generic `checkParameters(T[] inputs, T[] outputs)` validates data input count and parity output count.

## Control Flow
Validation compares input length to `encoder.getNumDataUnits()` and output length to `encoder.getNumParityUnits()` before subclass buffer checks.

## State and Persistence Behavior
The state is transient per encode call.

## Dependencies and Integration Points
It is extended by `ByteArrayEncodingState` and `ByteBufferEncodingState` and gates every public encode entry point.

## Risks and Test Signals
Risks are limited validation scope: this class does not check nulls or lengths. Tests should cover bad input/output counts and subclass-specific buffer validation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/EncodingState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/ErasureCodeNative.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/ErasureCodeNative.java

## Purpose
`ErasureCodeNative` centralizes native erasure-code library availability checks, currently relying on Hadoop native code and ISA-L native entry points.

## Important APIs, Types, and Functions
It owns static `LOADING_FAILURE_REASON`, evaluates native loading in a static initializer, and exposes `isNativeCodeLoaded()`, `checkNativeCodeLoaded()`, native `loadLibrary()`, native `getLibraryName()`, and `getLoadingFailureReason()`.

## Control Flow
On class initialization, it checks `NativeCodeLoader.isNativeCodeLoaded()`. If Hadoop native code is available, it calls native `loadLibrary()` and records either `null` or the thrown error string. `checkNativeCodeLoaded` throws `RuntimeException` when loading failed.

## State and Persistence Behavior
Native availability is captured once per JVM in a static final string. There is no retry path or external persistence.

## Dependencies and Integration Points
It depends on Hadoop `NativeCodeLoader`, native JNI methods, and native coder tests that skip with JUnit assumptions when native code is unavailable.

## Risks and Test Signals
Risks include stale one-time failure state, native linkage errors, and relying on Hadoop native libraries before Ozone owns native EC bits. Test signals include native-present and native-absent test environments, assertion of failure reason text, and native coder construction/fallback behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/ErasureCodeNative.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeRSRawDecoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeRSRawDecoder.java

## Purpose
`NativeRSRawDecoder` adapts Ozone replication config to Hadoop's native Reed-Solomon decoder backed by ISA-L.

## Important APIs, Types, and Functions
It extends `AbstractNativeRawDecoder`, owns a Hadoop `NativeRSRawDecoder`, constructs it with `ErasureCoderOptions`, implements `performDecodeImpl(...)`, `release()`, and `preferDirectBuffer()`.

## Control Flow
Construction creates the Hadoop native decoder. Decode calls arrive through the abstract base, which supplies offsets and length to `HadoopNativeECAccessorUtil.performDecodeImpl`. Release delegates to the Hadoop native decoder.

## State and Persistence Behavior
Persistent process state is the wrapped native decoder and its native resources until `release()`.

## Dependencies and Integration Points
It integrates with `NativeRSRawErasureCoderFactory`, `CodecUtil` fallback order, Hadoop native EC accessor utilities, and native RS tests.

## Risks and Test Signals
Risks include native library absence, release-after-use errors, mismatched erased indexes, and config translation mistakes. Tests cover native RS data/parity erasure combinations, native skip when unavailable, and decode after release.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeRSRawDecoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeRSRawEncoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeRSRawEncoder.java

## Purpose
`NativeRSRawEncoder` is Ozone's native Reed-Solomon encoder wrapper over Hadoop ISA-L support.

## Important APIs, Types, and Functions
It extends `AbstractNativeRawEncoder`, owns Hadoop `NativeRSRawEncoder`, constructs with `ErasureCoderOptions`, implements `performEncodeImpl(...)`, `release()`, and `preferDirectBuffer()`.

## Control Flow
The base class validates and offsets inputs/outputs; this class delegates the actual encode operation to `HadoopNativeECAccessorUtil.performEncodeImpl`. Release forwards to the wrapped native object.

## State and Persistence Behavior
The wrapped native encoder may hold native tables/resources for the replication schema until released.

## Dependencies and Integration Points
It is created by `NativeRSRawErasureCoderFactory` and preferred by `CodecRegistry` before Java RS when available.

## Risks and Test Signals
Risks include native unavailability, direct/heap conversion overhead, resource lifecycle leaks, and schema mismatch. Tests include native RS parity correctness, direct/heap paths, release behavior, and Java fallback when construction fails.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeRSRawEncoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeRSRawErasureCoderFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeRSRawErasureCoderFactory.java

## Purpose
This factory exposes native Reed-Solomon raw coders to the registry.

## Important APIs, Types, and Functions
It implements `RawErasureCoderFactory`, defines `CODER_NAME = "rs_native"`, creates `NativeRSRawEncoder` and `NativeRSRawDecoder`, returns coder name, and returns codec name `rs`.

## Control Flow
Factory methods instantiate native wrappers; any native linkage failure is surfaced to `CodecUtil`, which can fall back to Java RS.

## State and Persistence Behavior
No mutable state is owned.

## Dependencies and Integration Points
It integrates with Java `ServiceLoader`, `CodecRegistry` native-first ordering, `ECReplicationConfig.EcCodec.RS`, and codec mapping tests.

## Risks and Test Signals
Risks include service-registration conflicts and native factory precedence breaking fallback. Tests assert registry order and native/Java mapping depending on native availability.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeRSRawErasureCoderFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeXORRawDecoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeXORRawDecoder.java

## Purpose
`NativeXORRawDecoder` adapts Ozone XOR decode calls to Hadoop's native XOR raw decoder.

## Important APIs, Types, and Functions
It extends `AbstractNativeRawDecoder`, owns Hadoop `NativeXORRawDecoder`, constructs with `ErasureCoderOptions`, implements `performDecodeImpl(...)`, and delegates `release()`.

## Control Flow
The base class validates decode state and calculates offsets, then this class calls `HadoopNativeECAccessorUtil.performDecodeImpl` on the wrapped native decoder.

## State and Persistence Behavior
The wrapped native decoder holds native resources until `release()`.

## Dependencies and Integration Points
It is created by `NativeXORRawErasureCoderFactory` and used by codec fallback for XOR.

## Risks and Test Signals
Risks include native library absence, XOR parity count assumptions, and release lifecycle errors. Tests include native XOR availability assumptions and decode-after-release behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeXORRawDecoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeXORRawEncoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeXORRawEncoder.java

## Purpose
`NativeXORRawEncoder` is Ozone's wrapper around Hadoop native XOR encoding.

## Important APIs, Types, and Functions
It extends `AbstractNativeRawEncoder`, owns Hadoop `NativeXORRawEncoder`, constructs with `ErasureCoderOptions`, implements `performEncodeImpl(...)`, and delegates `release()`.

## Control Flow
The abstract base gathers positions and locks the native path; this class forwards encode arguments to `HadoopNativeECAccessorUtil.performEncodeImpl`.

## State and Persistence Behavior
The wrapped native encoder is persistent for the Java object lifetime and must be released.

## Dependencies and Integration Points
It is created by `NativeXORRawErasureCoderFactory`, selected before Java XOR by `CodecRegistry`, and exercised by native XOR tests.

## Risks and Test Signals
Risks include native construction failure, resource leaks, and unsupported parity layouts. Test signals are native XOR encode/decode, Java fallback, direct buffer preference, and release behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeXORRawEncoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeXORRawErasureCoderFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeXORRawErasureCoderFactory.java

## Purpose
This factory exposes native XOR raw coders to the registry.

## Important APIs, Types, and Functions
It implements `RawErasureCoderFactory`, defines `CODER_NAME = "xor_native"`, creates `NativeXORRawEncoder` and `NativeXORRawDecoder`, and returns codec name `xor`.

## Control Flow
Factory creation is direct; exceptions are expected to be caught by higher-level fallback logic.

## State and Persistence Behavior
No factory state is retained.

## Dependencies and Integration Points
It integrates with `ServiceLoader`, `CodecRegistry`, `CodecUtil`, and mapping tests.

## Risks and Test Signals
Risks are service conflicts and ordering mistakes. Tests should assert native XOR is first in registry and Java XOR is selected after native failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/NativeXORRawErasureCoderFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RSRawDecoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RSRawDecoder.java

## Purpose
`RSRawDecoder` is the pure-Java Reed-Solomon decoder fallback compatible with ISA-L matrix behavior.

## Important APIs, Types, and Functions
It extends `RawErasureDecoder`, owns `encodeMatrix`, per-erasure `decodeMatrix`, `invertMatrix`, `gfTables`, `cachedErasedIndexes`, `validIndexes`, `numErasedDataUnits`, and `erasureFlags`. Important methods are both `doDecode` overloads, `prepareDecoding`, `processErasures`, and `generateDecodeMatrix`.

## Control Flow
Construction builds a Cauchy encode matrix and rejects data+parity counts at or above GF(256) field size. Each decode resets outputs, prepares decoding tables if erased/valid indexes changed, selects the first `k` valid inputs, and calls `RSUtil.encodeData` with decode tables. Decode matrix generation removes erased rows, inverts the surviving data matrix, copies rows for erased data units, and computes parity recovery rows from the encode matrix.

## State and Persistence Behavior
The encode matrix persists for the decoder lifetime. Decode matrices and GF tables are cached for the most recent erased/valid index pattern and reused on identical patterns. No disk persistence exists.

## Dependencies and Integration Points
It depends on `GF256`, `RSUtil`, `DumpUtil`, and the validation in `RawErasureDecoder`/state classes. It is selected by `RSRawErasureCoderFactory` and used when native RS is unavailable.

## Risks and Test Signals
Risks include mutable cached decode state in a synchronized decoder, invalid erased indexes, GF matrix inversion failures, and compatibility drift with ISA-L. Tests cover many 6+3 and 10+4 erasure patterns, too many erasures, input position behavior, direct and heap buffers, and native-vs-Java fallback mapping.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RSRawDecoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RSRawEncoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RSRawEncoder.java

## Purpose
`RSRawEncoder` is the pure-Java Reed-Solomon encoder fallback.

## Important APIs, Types, and Functions
It extends `RawErasureEncoder`, owns `encodeMatrix` and `gfTables`, constructs a Cauchy matrix using `RSUtil.genCauchyMatrix`, initializes GF tables for parity rows, and implements both `doEncode` overloads.

## Control Flow
Construction validates the number of units against GF(256), builds the encode matrix, optionally dumps diagnostics, and precomputes GF multiplication tables. Encode resets parity outputs to zero and calls `RSUtil.encodeData` for ByteBuffers or byte arrays.

## State and Persistence Behavior
Schema-specific matrix and GF tables persist for the encoder lifetime. No mutable per-call state is retained.

## Dependencies and Integration Points
It depends on `RSUtil`, `DumpUtil`, and `ECReplicationConfig`, is created by `RSRawErasureCoderFactory`, and is the Java fallback for RS codec operations.

## Risks and Test Signals
Risks include field-size limits, output reset omissions, and compatibility drift with native ISA-L. Tests include RS encode/decode round trips, Java/native mapping, direct and heap buffer paths, and erasure combinations from `TestRSRawCoderBase`.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RSRawEncoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RSRawErasureCoderFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RSRawErasureCoderFactory.java

## Purpose
This factory creates pure-Java Reed-Solomon raw coders.

## Important APIs, Types, and Functions
It implements `RawErasureCoderFactory`, defines `CODER_NAME = "rs_java"`, creates `RSRawEncoder` and `RSRawDecoder`, returns coder name, and returns codec name `rs`.

## Control Flow
Creation methods directly instantiate Java RS coders with the provided replication config.

## State and Persistence Behavior
No mutable factory state is held.

## Dependencies and Integration Points
It integrates with `CodecRegistry`, `CodecUtil` fallback, `ServiceLoader`, and tests that verify RS registry order.

## Risks and Test Signals
Risks are service registration conflicts and fallback not reaching Java RS after native failure. Tests assert registry coder names and successful RS Java coding.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RSRawErasureCoderFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RawErasureCoderFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RawErasureCoderFactory.java

## Purpose
`RawErasureCoderFactory` is the service-provider contract for raw erasure coder implementations.

## Important APIs, Types, and Functions
It declares `createEncoder(ECReplicationConfig)`, `createDecoder(ECReplicationConfig)`, `getCoderName()`, and `getCodecName()`.

## Control Flow
There is no implementation flow; `CodecRegistry` discovers implementations and `CodecUtil` invokes factories in priority order.

## State and Persistence Behavior
Factories decide their own state; the interface owns none.

## Dependencies and Integration Points
It depends on `ECReplicationConfig` and is implemented by RS, XOR, native, and dummy factories.

## Risks and Test Signals
Risks include duplicate coder names per codec, factories throwing during creation, and inconsistent codec names. Tests verify registry conflict handling, names, and factory-created types.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RawErasureCoderFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RawErasureDecoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RawErasureDecoder.java

## Purpose
`RawErasureDecoder` is the abstract public base for low-level decode operations over ByteBuffers, byte arrays, and `ECChunk` arrays.

## Important APIs, Types, and Functions
It stores `ECReplicationConfig` and exposes synchronized `decode(ByteBuffer[], int[], ByteBuffer[])`, synchronized `decode(byte[][], int[], byte[][])`, synchronized `decode(ECChunk[], int[], ECChunk[])`, abstract `doDecode` methods, data/parity count getters, `preferDirectBuffer()`, `allowChangeInputs()`, `allowVerboseDump()`, and `release()`.

## Control Flow
Public decode constructs a state object, returns immediately for zero length, records input positions for ByteBuffers, dispatches to direct or byte-array implementation, then advances non-null input positions by the decode length. The `ECChunk` overload unwraps chunks through `CoderUtil.toBuffers`.

## State and Persistence Behavior
The base stores immutable replication config. Decode methods are synchronized, protecting mutable concrete decoder state such as RS cached matrices.

## Dependencies and Integration Points
It integrates with state classes, `ECChunk`, `CoderUtil`, Java/native concrete decoders, and all raw coder tests.

## Risks and Test Signals
Risks include serialized decode throughput, position advancement surprises, invalid erased indexes not fully checked in the base, and release semantics being left to subclasses. Tests cover bad inputs/outputs, too many erasures, positions at end, idempotent releases, and decode after release for native wrappers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RawErasureDecoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RawErasureEncoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RawErasureEncoder.java

## Purpose
`RawErasureEncoder` is the abstract public base for low-level erasure encoding over ByteBuffers, byte arrays, and `ECChunk` arrays.

## Important APIs, Types, and Functions
It stores `ECReplicationConfig` and exposes `encode(ByteBuffer[], ByteBuffer[])`, `encode(byte[][], byte[][])`, `encode(ECChunk[], ECChunk[])`, abstract `doEncode` overloads, data/parity/all-unit getters, `preferDirectBuffer()`, `allowChangeInputs()`, `allowVerboseDump()`, and `release()`.

## Control Flow
ByteBuffer encode validates state, returns for zero length, records input positions, dispatches to direct or byte-array implementation, then advances input positions by encoded length. Byte-array encode validates and delegates. `ECChunk` encode unwraps buffers and delegates.

## State and Persistence Behavior
The base owns immutable replication config. Concrete encoders may hold schema-specific tables or native resources.

## Dependencies and Integration Points
It integrates with `EncodingState` subclasses, `ECChunk`, Java/native encoders, and the codec factory layer.

## Risks and Test Signals
Risks include non-synchronized encode despite comments about future thread safety, position advancement surprises, output buffers not being flipped by the framework, and release behavior varying by subclass. Tests cover round trips, direct/heap/sliced buffers, bad shape handling, idempotent release, and position checks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/RawErasureEncoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/XORRawDecoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/XORRawDecoder.java

## Purpose
`XORRawDecoder` is the pure-Java XOR decoder fallback.

## Important APIs, Types, and Functions
It extends `RawErasureDecoder` and implements ByteBuffer and byte-array `doDecode` methods.

## Control Flow
Each decode resets the single output buffer, reads the first erased index, then XORs all non-erased input units into the output using absolute buffer/array accesses.

## State and Persistence Behavior
It owns no mutable state beyond inherited config.

## Dependencies and Integration Points
It is created by `XORRawErasureCoderFactory` and used as fallback for XOR codec operations.

## Risks and Test Signals
Risks include assuming one output/parity style, null inputs beyond the erased index causing failures, and invalid erased indexes. Tests include data and parity erasure cases, too many erasures, and Java/native XOR mapping.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/XORRawDecoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/XORRawEncoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/XORRawEncoder.java

## Purpose
`XORRawEncoder` is the pure-Java XOR parity generator.

## Important APIs, Types, and Functions
It extends `RawErasureEncoder` and implements both ByteBuffer and byte-array encode paths.

## Control Flow
Encoding resets the first output, copies the first input into it, then XORs every remaining input into the same output. ByteBuffer operations use absolute get/put so caller positions are advanced only by the base class.

## State and Persistence Behavior
No mutable state is retained.

## Dependencies and Integration Points
It is created by `XORRawErasureCoderFactory` and tested through `TestXORRawCoderBase`.

## Risks and Test Signals
Risks include assuming a single parity output and all inputs being non-null. Tests should verify parity regeneration for different erased data indexes, parity erasure, direct and heap buffers, and too-many-erasure failure.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/XORRawEncoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/XORRawErasureCoderFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/XORRawErasureCoderFactory.java

## Purpose
This factory creates pure-Java XOR raw coders.

## Important APIs, Types, and Functions
It implements `RawErasureCoderFactory`, defines `CODER_NAME = "xor_java"`, and creates `XORRawEncoder`/`XORRawDecoder` for codec `xor`.

## Control Flow
Factory creation is direct and stateless.

## State and Persistence Behavior
No mutable state is retained.

## Dependencies and Integration Points
It is registered through service loading and used by codec fallback and mapping tests.

## Risks and Test Signals
Risks include wrong codec names and registry conflicts. Tests assert XOR factory ordering and successful Java XOR round trips.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/XORRawErasureCoderFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/package-info.java

## Purpose
This package descriptor documents the raw coder layer as the low-level math engine below higher-level erasure coders.

## Important APIs, Types, and Functions
It has no executable API and applies `@InterfaceAudience.Private` and `@InterfaceStability.Unstable`.

## Control Flow
There is no runtime flow.

## State and Persistence Behavior
No state is owned.

## Dependencies and Integration Points
It imports HDDS annotations and marks all raw coder APIs as internal/unstable.

## Risks and Test Signals
Risk is compatibility contract drift. Build/package annotation checks are enough.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/util/CodecUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/util/CodecUtil.java

## Purpose
`CodecUtil` creates raw encoders and decoders for an `ECReplicationConfig`, trying registered coder factories in priority order with fallback.

## Important APIs, Types, and Functions
It exposes `createRawEncoderWithFallback(ECReplicationConfig)` and `createRawDecoderWithFallback(ECReplicationConfig)`, plus private `createRawCoderFactory(String,String)`.

## Control Flow
For a config, it lowercases the codec enum name, fetches coder names from `CodecRegistry`, iterates in order, and tries to create a coder. It catches `LinkageError` and `Exception`, logs at debug, and tries the next coder. If all fail, it throws `IllegalArgumentException`.

## State and Persistence Behavior
The utility is stateless; registry state is external.

## Dependencies and Integration Points
It depends on `CodecRegistry`, raw coder factories, `ECReplicationConfig`, and SLF4J. It is the main integration point for native-first then Java fallback selection.

## Risks and Test Signals
Risks include `null` coder name arrays causing NPE for unknown codecs, swallowing important construction errors at debug level, and fallback order relying on registry correctness. Tests assert RS/XOR native-vs-Java selected types and unknown/invalid registry behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/util/CodecUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/util/DumpUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/util/DumpUtil.java

## Purpose
`DumpUtil` provides debug formatting for raw coder matrices and chunks.

## Important APIs, Types, and Functions
It exposes `bytesToHex(byte[], int)`, `dumpMatrix(byte[], int, int)`, `dumpChunks(String, ECChunk[])`, and `dumpChunk(ECChunk)`.

## Control Flow
Hex conversion truncates by limit when requested. Dump methods print formatted matrices or chunks to standard output and use `ECChunk.toBytesArray()` for chunk data.

## State and Persistence Behavior
It has no mutable state; output is transient console/debug output.

## Dependencies and Integration Points
It depends on `ECChunk` and is used by RS coders when verbose dump is enabled.

## Risks and Test Signals
Risks include noisy stdout in production-like tests and large dump output. Tests should check formatting only indirectly through diagnostic use, with verbose dump disabled by default.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/util/DumpUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/util/GF256.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/util/GF256.java

## Purpose
`GF256` implements optimized GF(2^8) primitives used by the ISA-L-compatible RS encoder/decoder.

## Important APIs, Types, and Functions
It defines base/log tables, a static multiplication table, and exposes `gfMulTab()`, `gfMul(byte,byte)`, `gfInv(byte)`, `gfInvertMatrix(byte[],byte[],int)`, and `gfVectMulInit(byte,byte[],int)`.

## Control Flow
Static initialization builds the full 256x256 multiplication table. Matrix inversion performs Gaussian elimination over GF(256), swapping rows when a pivot is zero, normalizing pivots, eliminating other rows, and writing the inverse. Vector table initialization precomputes low/high nibble multiplication tables for ISA-L style encoding.

## State and Persistence Behavior
The multiplication table is static process-local state initialized once. No mutable per-call persistent state exists.

## Dependencies and Integration Points
It is used by `RSUtil` and `RSRawDecoder` for table generation, matrix inversion, multiplication, and inversion.

## Risks and Test Signals
Risks include arithmetic table corruption, singular decode matrices, unsigned byte handling mistakes, and silent reliance on ISA-L constants. Tests should verify known GF multiplication/inversion values, RS round trips, and erasure patterns requiring decode matrix inversion.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/util/GF256.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/util/GaloisField.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/util/GaloisField.java

## Purpose
`GaloisField` is a general GF utility for field arithmetic, Vandermonde solving, polynomial operations, substitution, remainders, and Gaussian elimination.

## Important APIs, Types, and Functions
It caches instances by field size/primitive polynomial, defaults to GF(256) with primitive polynomial 285, and exposes `getInstance`, `getFieldSize`, `getPrimitivePolynomial`, `add`, `multiply`, `divide`, `power`, several `solveVandermondeSystem` overloads, polynomial `multiply`, `remainder`, `add`, `substitute` overloads, and `gaussianElimination`.

## Control Flow
Construction builds log/power tables and multiplication/division tables. Bulk methods operate over byte arrays or ByteBuffers with absolute offsets. Vandermonde solving and remainder methods mutate provided arrays/buffers in place.

## State and Persistence Behavior
Field instances and arithmetic tables are cached statically. Most operation state is caller-provided and often mutated.

## Dependencies and Integration Points
`RSUtil.GF` uses the default instance for primitive powers and field-size validation. The class is also a reusable utility for older RS-style algorithms.

## Risks and Test Signals
Risks include reliance on Java `assert` for argument validation, in-place mutation surprises, divide-by-zero misuse, and ByteBuffer position/limit assumptions. Test signals include known arithmetic identities, polynomial operations, bulk substitution/remainder correctness, and RS coder round trips.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/util/GaloisField.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/util/RSUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/util/RSUtil.java

## Purpose
`RSUtil` contains ISA-L-derived Reed-Solomon matrix/table generation and bulk encode routines.

## Important APIs, Types, and Functions
It exposes `GF`, `PRIMITIVE_ROOT`, `getPrimitivePower`, `initTables`, `genCauchyMatrix`, and `encodeData` overloads for byte arrays and ByteBuffers.

## Control Flow
`genCauchyMatrix` writes an identity data section and Cauchy parity rows. `initTables` builds 32-byte GF vector tables for each coding coefficient. `encodeData` loops over outputs and inputs, selects a GF multiplication table line, XORs table lookups into outputs in 8-byte chunks, then handles leftover bytes.

## State and Persistence Behavior
It is stateless except for using `GaloisField` and `GF256` static tables. Callers own matrix/table arrays.

## Dependencies and Integration Points
It is used by `RSRawEncoder` and `RSRawDecoder` for both encoding and decoding.

## Risks and Test Signals
Risks include incorrect matrix offsets, output buffers not reset before XOR accumulation, byte signedness errors, and performance regressions in the inner loops. Test signals include RS known erasure patterns, native compatibility, direct/heap buffers, odd data lengths, and different data/parity configurations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/util/RSUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/util/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/util/package-info.java

## Purpose
This descriptor marks raw coder utility classes as private unstable Ozone internals.

## Important APIs, Types, and Functions
No runtime API; package annotations are `@InterfaceAudience.Private` and `@InterfaceStability.Unstable`.

## Control Flow
No runtime flow.

## State and Persistence Behavior
No state is owned.

## Dependencies and Integration Points
It imports HDDS annotations and applies to `CodecUtil`, `GF256`, `GaloisField`, `RSUtil`, and dump utilities.

## Risks and Test Signals
Risk is package contract drift. Build/package annotation checks are sufficient.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/main/java/org/apache/ozone/erasurecode/rawcoder/util/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/BufferAllocator.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/BufferAllocator.java

## Purpose
`BufferAllocator` is a test helper abstraction for allocating heap/direct ByteBuffers, optionally as slices with non-zero offsets.

## Important APIs, Types, and Functions
It defines abstract `allocate(int)`, `isUsingDirect()`, and two implementations: `SimpleBufferAllocator` and `SlicedBufferAllocator`.

## Control Flow
Simple allocation returns either `ByteBuffer.allocateDirect` or `ByteBuffer.allocate`. Sliced allocation creates a larger buffer, advances position by an offset, slices it, and limits the slice to the requested length.

## State and Persistence Behavior
Each allocator records whether it uses direct buffers. Sliced allocator also carries a slice offset. No persistent storage exists.

## Dependencies and Integration Points
It is used by `TestCoderBase` to exercise direct/heap and sliced-buffer code paths.

## Risks and Test Signals
Risks include tests missing offset-sensitive bugs if only simple allocators are used. Test signals are raw coder tests with sliced buffers and position-at-end assertions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/BufferAllocator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/DumpUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/DumpUtil.java

## Purpose
This test-side `DumpUtil` duplicates debug formatting helpers for matrix/chunk dumps used by tests.

## Important APIs, Types, and Functions
It exposes `bytesToHex`, `dumpMatrix`, `dumpChunks`, and `dumpChunk`.

## Control Flow
It formats bytes as hex and prints chunks/matrices to stdout when tests enable dumping.

## State and Persistence Behavior
No state is owned.

## Dependencies and Integration Points
It depends on `ECChunk` and is used by `TestCoderBase` diagnostics.

## Risks and Test Signals
Risks are duplicated implementation drift from main `rawcoder.util.DumpUtil` and noisy test output. Test signal is primarily developer diagnostics during failing erasure-code tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/DumpUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/TestCodecRegistry.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/TestCodecRegistry.java

## Purpose
`TestCodecRegistry` verifies raw coder registration, lookup, ordering, conflict handling, and codec name coverage.

## Important APIs, Types, and Functions
Tests include `testGetCodecs`, `testGetCoders`, wrong lookup cases, `testUpdateCoders`, `testGetCoderNames`, and `testGetCoderByName`. It defines an inner incorrect RS factory to test duplicate coder-name rejection.

## Control Flow
Tests query the singleton registry, assert `rs` and `xor` codecs, verify native factories are ordered before Java factories, update the registry with a conflicting factory, and assert coder arrays remain unchanged.

## State and Persistence Behavior
The test mutates singleton registry state via `updateCoders`, so ordering and isolation matter across tests.

## Dependencies and Integration Points
It depends on AssertJ/JUnit, `CodecRegistry`, `ECReplicationConfig`, and factory classes.

## Risks and Test Signals
Risks include singleton state leakage and assumptions about service-loader ordering. Passing tests signal correct native-first ordering, duplicate rejection, and lookup by coder name.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/TestCodecRegistry.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/TestCoderBase.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/TestCoderBase.java

## Purpose
`TestCoderBase` is the shared high-level test harness for erasure coder data generation, chunk allocation, erasure simulation, verification, and diagnostics.

## Important APIs, Types, and Functions
Important fields configure data/parity counts, chunk size, erased data/parity indexes, direct vs heap, fixed data, allocator, and zero chunks. Key methods include `prepare`, `prepareBufferAllocator`, `compareAndVerify`, `getErasedIndexesForDecoding`, `prepareInputChunksForDecoding`, `backupAndEraseChunks`, `eraseDataFromChunks`, mark/restore helpers, clone helpers, output allocation, data/parity preparation, `toArrays`, `dumpSetting`, `dumpChunks`, and `corruptSomeChunk`.

## Control Flow
Tests call `prepare`, allocate data chunks, encode parity, clone expected erased chunks, null out erased positions, prepare decode inputs/outputs, run coder operations, and compare decoded chunks with backups. Data may be fixed deterministic or random.

## State and Persistence Behavior
State is per test instance and includes generated fixed data and allocator mode. There is no persistence outside test memory.

## Dependencies and Integration Points
It depends on `ECChunk`, `BufferAllocator`, `OzoneConfiguration`, random utilities, and JUnit assertions. `TestRawCoderBase` builds on it for raw coder-specific execution.

## Risks and Test Signals
Risks include tests hiding bugs through deterministic data, mark/reset assumptions on ByteBuffers, and direct/heap mode not being reset between tests. Strong signals are successful direct/heap/sliced tests, compare failures pinpointing decode corruption, and position verification.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/TestCoderBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/package-info.java

## Purpose
This test package descriptor names the erasure-code test package.

## Important APIs, Types, and Functions
No runtime API is declared.

## Control Flow
There is no runtime flow.

## State and Persistence Behavior
No state is owned.

## Dependencies and Integration Points
It belongs to the test source tree and groups test helpers and registry/coder tests.

## Risks and Test Signals
Risk is negligible; compile inclusion is the only practical signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/RawErasureCoderBenchmark.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/RawErasureCoderBenchmark.java

## Purpose
`RawErasureCoderBenchmark` is a command-line benchmark for raw encoder/decoder throughput across dummy, RS Java/native, and XOR Java/native coders.

## Important APIs, Types, and Functions
It defines `TARGET_BUFFER_SIZE_MB`, `MAX_CHUNK_SIZE`, coder factory list, `main`, `performBench`, `getRawEncoder`, `getRawDecoder`, `getBufferForInit`, `printThreadStatistics`, `genTestData`, `BenchData`, and `BenchmarkCallable`.

## Control Flow
The benchmark parses operation, coder index, thread count, data length, chunk size, and direct-buffer mode; initializes per-thread data; runs callables through an executor; times loops; and prints throughput/statistics.

## State and Persistence Behavior
State is in-memory benchmark buffers and per-thread callable counters. No files are written.

## Dependencies and Integration Points
It depends on raw coder factories, `ECReplicationConfig(6,3)`, Guava preconditions, random data, executor services, and Hadoop `StopWatch`.

## Risks and Test Signals
Risks include benchmark-only assumptions about RS 6+3, memory pressure from target buffer sizing, native availability differences, and use of benchmark code as a test. Signals include the benchmark test smoke-running dummy/RS paths and manual throughput comparisons.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/RawErasureCoderBenchmark.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestCodecRawCoderMapping.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestCodecRawCoderMapping.java

## Purpose
`TestCodecRawCoderMapping` verifies that `CodecUtil` creates the expected raw coder type for RS and XOR configurations.

## Important APIs, Types, and Functions
It has `testRSDefaultRawCoder` and `testXORRawCoder`, using `ECReplicationConfig`, `CodecUtil.createRawEncoderWithFallback`, and `createRawDecoderWithFallback`.

## Control Flow
Each test creates a config string, asks `CodecUtil` for encoder/decoder, and asserts native types when native code is loaded or Java fallback types otherwise.

## State and Persistence Behavior
No persistent state is owned.

## Dependencies and Integration Points
It depends on native availability via `ErasureCodeNative`, factory registry ordering, and JUnit assertions.

## Risks and Test Signals
Risks include environment-dependent assertions if native availability changes mid-JVM and registry order drift. Passing tests signal correct fallback behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestCodecRawCoderMapping.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestCoderUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestCoderUtil.java

## Purpose
`TestCoderUtil` validates concurrency behavior of the shared zero-buffer cache in `CoderUtil`.

## Important APIs, Types, and Functions
It resets the private static `emptyChunk` via reflection in `resetEmptyChunk`, tests `getEmptyChunkDoesNotShrinkWhenCacheGrowsConcurrently`, and uses helper `waitUntilBlocked`.

## Control Flow
The test creates two tasks: one requesting a slightly larger chunk and blocking on class initialization/locking, and another requesting a larger chunk. It verifies the final cache remains at the larger length and the smaller request receives a sufficiently large array.

## State and Persistence Behavior
It deliberately mutates static `CoderUtil.emptyChunk` between tests.

## Dependencies and Integration Points
It depends on reflection, executor services, futures, atomic references, AssertJ, and JUnit.

## Risks and Test Signals
Risks include brittle thread-block detection and reflective access breaking on field rename. Passing tests signal the double-check locking in `getEmptyChunk` avoids cache shrink races.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestCoderUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestDummyRawCoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestDummyRawCoder.java

## Purpose
`TestDummyRawCoder` verifies the dummy raw coder framework integration.

## Important APIs, Types, and Functions
It extends `TestRawCoderBase`, configures dummy factories in `setup`, runs two erasure pattern tests, overrides `testCoding(boolean)`, and creates empty chunks with `getEmptyChunks`.

## Control Flow
Setup uses 6 data and 3 parity units. Tests set erased data/parity indexes, run direct and heap variants, and expect dummy outputs to remain empty rather than real reconstructed data.

## State and Persistence Behavior
State is inherited test configuration and per-test chunks.

## Dependencies and Integration Points
It depends on dummy factory/encoder/decoder classes, `ECChunk`, `ByteBuffer`, and JUnit.

## Risks and Test Signals
Risks include dummy behavior being confused with correctness. Signals are no-op output behavior and framework validation around dummy coders.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestDummyRawCoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestNativeRSRawCoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestNativeRSRawCoder.java

## Purpose
`TestNativeRSRawCoder` runs RS raw coder correctness tests against native ISA-L wrappers when native code is available.

## Important APIs, Types, and Functions
It extends `TestRSRawCoderBase`, configures native RS factories in the constructor, skips tests in `setup` with `Assumptions.assumeTrue(ErasureCodeNative.isNativeCodeLoaded())`, and defines native-specific erasure pattern and after-release tests.

## Control Flow
When native code is present, inherited RS tests run for data/parity erasures, too many erasures, and 10+4 layout. `testAfterRelease63` verifies operations after release fail as expected.

## State and Persistence Behavior
State is inherited per-test raw coder setup. Native resources are created and released during tests.

## Dependencies and Integration Points
It depends on native library loading, native RS factories, and JUnit assumptions.

## Risks and Test Signals
Risks include tests being skipped in many environments and native lifecycle failures only visible on native-enabled hosts. Passing native tests signal Hadoop native accessor compatibility and Ozone wrapper correctness.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestNativeRSRawCoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestNativeXORRawCoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestNativeXORRawCoder.java

## Purpose
`TestNativeXORRawCoder` verifies native XOR coder wrapper behavior when native code is available.

## Important APIs, Types, and Functions
It extends `TestXORRawCoderBase`, configures native XOR factories, skips without native code, and defines `testAfterRelease63`.

## Control Flow
Inherited XOR tests exercise direct/heap paths and erasure patterns; the after-release test checks native resources reject later use.

## State and Persistence Behavior
State is inherited per-test coder setup plus native resources.

## Dependencies and Integration Points
It depends on `ErasureCodeNative`, native XOR factories, and JUnit assumptions.

## Risks and Test Signals
Risks include environment-dependent skips and release errors. Passing tests signal native XOR wrapper integration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestNativeXORRawCoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestRSRawCoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestRSRawCoder.java

## Purpose
`TestRSRawCoder` runs the shared RS correctness suite against pure-Java RS coders.

## Important APIs, Types, and Functions
It extends `TestRSRawCoderBase`, supplies `RSRawErasureCoderFactory` for encoder and decoder, and disables verbose dumps in setup.

## Control Flow
All meaningful test flow is inherited from `TestRSRawCoderBase` and `TestRawCoderBase`.

## State and Persistence Behavior
Per-test Java coder instances hold RS matrices/tables; no persistence exists.

## Dependencies and Integration Points
It depends on Java RS factory classes and inherited JUnit tests.

## Risks and Test Signals
Passing tests are the main signal that Java fallback remains correct across data/parity erasure patterns and buffer modes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestRSRawCoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestRSRawCoderBase.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestRSRawCoderBase.java

## Purpose
`TestRSRawCoderBase` defines the shared Reed-Solomon raw coder correctness scenarios.

## Important APIs, Types, and Functions
It extends `TestRawCoderBase` and defines tests for all data erased, selected data erasures, data plus parity erasures, all parity erased, parity subsets, too many erasures, 10+4 layout, and input buffer position.

## Control Flow
Each test sets erased data/parity indexes and calls `testCodingDoMixAndTwice`, negative bad-input tests, or position tests inherited from `TestRawCoderBase`.

## State and Persistence Behavior
State is inherited test configuration adjusted per method.

## Dependencies and Integration Points
It is subclassed by Java and native RS test classes.

## Risks and Test Signals
Risks include duplicated method names/labels and missing randomized erasure combinations beyond fixed scenarios. Passing tests signal RS core correctness for representative patterns and buffer handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestRSRawCoderBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestRawCoderBase.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestRawCoderBase.java

## Purpose
`TestRawCoderBase` bridges the generic chunk test harness to concrete raw encoder/decoder factories.

## Important APIs, Types, and Functions
It owns encoder/decoder factory classes and instances. Important methods include `testCodingDoMixAndTwice`, `testCodingDoMixed`, `testCoding`, bad input/output tests, `testCodingWithErasingTooMany`, `testIdempotentReleases`, `performTestCoding`, `prepareCoders`, `ensureOnlyLeastRequiredChunks`, `createEncoder`, `createDecoder`, `testInputPosition`, `verifyBufferPositionAtEnd`, and wrapper `encode`/`decode`.

## Control Flow
Tests create coders through reflection, encode parity, prepare erased inputs, decode, compare expected chunks, repeat with direct/heap and sliced/simple buffers, then release coders. Negative paths corrupt inputs/outputs or over-erase to assert exceptions.

## State and Persistence Behavior
Per-test state includes current encoder/decoder objects. Release is called and tested for idempotence.

## Dependencies and Integration Points
It depends on `TestCoderBase`, `RawErasureCoderFactory`, `ECReplicationConfig`, `ECChunk`, AssertJ/JUnit, and concrete factory subclasses.

## Risks and Test Signals
Risks include reflection hiding constructor changes, factory lifecycle state leaking between runs, and native release behavior varying. Passing tests signal round-trip correctness, validation failures, buffer position movement, and release semantics.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestRawCoderBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestRawErasureCoderBenchmark.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestRawErasureCoderBenchmark.java

## Purpose
`TestRawErasureCoderBenchmark` smoke-tests the benchmark entry point.

## Important APIs, Types, and Functions
It contains `testDummyCoder` and `testRSCoder`, each invoking `RawErasureCoderBenchmark.main` with small arguments.

## Control Flow
The tests run encode/decode benchmark paths for dummy and RS configurations with bounded data sizes so benchmark wiring is covered without long runs.

## State and Persistence Behavior
No persistent state is owned.

## Dependencies and Integration Points
It depends on the benchmark class and JUnit.

## Risks and Test Signals
Risks include timing/memory sensitivity if benchmark defaults change. Passing tests signal CLI argument parsing and basic benchmark execution.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestRawErasureCoderBenchmark.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestXORRawCoder.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestXORRawCoder.java

## Purpose
`TestXORRawCoder` runs the shared XOR suite against pure-Java XOR coders.

## Important APIs, Types, and Functions
It extends `TestXORRawCoderBase` and supplies `XORRawErasureCoderFactory` for both encoder and decoder.

## Control Flow
All tests are inherited from the XOR base class.

## State and Persistence Behavior
Per-test Java XOR coders are created and released by the base.

## Dependencies and Integration Points
It depends on Java XOR factory classes and inherited raw coder tests.

## Risks and Test Signals
Passing tests signal Java XOR correctness for representative erasures and validation failures.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestXORRawCoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestXORRawCoderBase.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestXORRawCoderBase.java

## Purpose
`TestXORRawCoderBase` defines shared XOR raw coder correctness and negative scenarios.

## Important APIs, Types, and Functions
It extends `TestRawCoderBase` and defines tests for erasing data unit 0, parity 0, data unit 5, too many erasures, and a bad-input data erasure.

## Control Flow
Each test sets the appropriate erased indexes and calls inherited round-trip or bad-input routines.

## State and Persistence Behavior
State is inherited and adjusted per test method.

## Dependencies and Integration Points
It is subclassed by Java and native XOR test classes.

## Risks and Test Signals
Risks include XOR-specific one-parity assumptions and limited erasure combinations. Passing tests signal XOR encode/decode and validation behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/TestXORRawCoderBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/package-info.java

## Purpose
This descriptor names the raw coder test package.

## Important APIs, Types, and Functions
No runtime API is declared.

## Control Flow
There is no runtime flow.

## State and Persistence Behavior
No state is owned.

## Dependencies and Integration Points
It groups raw coder benchmark and correctness tests.

## Risks and Test Signals
Risk is negligible; compile inclusion is the only signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/erasurecode/src/test/java/org/apache/ozone/erasurecode/rawcoder/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/dev-support/findbugsExcludeFile.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/dev-support/findbugsExcludeFile.xml

## Purpose
This SpotBugs/FindBugs exclude filter suppresses a specific warning in the HDDS framework module.

## Important APIs, Types, and Functions
It defines one `<Match>` for class `org.apache.hadoop.hdds.utils.ProtocolMessageMetrics` and bug pattern `RV_RETURN_VALUE_IGNORED_NO_SIDE_EFFECT`.

## Control Flow
There is no runtime flow; the Maven SpotBugs plugin reads the filter during static analysis.

## State and Persistence Behavior
The XML persists as build configuration only.

## Dependencies and Integration Points
It is referenced by `framework/pom.xml` through the SpotBugs plugin `excludeFilterFile`.

## Risks and Test Signals
Risks include suppressing a real issue if the class changes and stale exclusion paths after refactors. Test signals are SpotBugs runs and build validation that the filter path resolves.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/pom.xml -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/pom.xml

## Purpose
This Maven POM defines the `hdds-server-framework` jar module, its dependencies, annotation processing, static-analysis filters, and test-jar generation.

## Important APIs, Types, and Functions
Key metadata includes parent `org.apache.ozone:hdds:2.3.0-SNAPSHOT`, artifact `hdds-server-framework`, packaging `jar`, and property `classpath.skip=false`. Dependencies span logging, Jackson, Hadoop common/auth, Ozone HDDS modules, Ratis APIs, Jetty/Jersey, RocksDB, metrics, OpenTelemetry, BouncyCastle, YAML, and test dependencies. Plugins configure SpotBugs exclusions, compiler annotation processors `ConfigFileGenerator` and `ReplicateAnnotationProcessor`, Maven enforcer import restrictions, and test-jar creation.

## Control Flow
Build flow resolves dependencies, runs annotation processors with `-AartifactId`, applies SpotBugs exclude filter, enforces banned imports, compiles framework code, and attaches a test jar.

## State and Persistence Behavior
The POM is persistent build state. Generated config metadata and replicated annotations are build outputs, not checked here.

## Dependencies and Integration Points
It integrates the framework module into the parent HDDS reactor and supplies dependencies needed by config classes, HTTP servlets, Ratis configuration, security, metrics, and tests.

## Risks and Test Signals
Risks include dependency scope drift, annotation processor misconfiguration, SpotBugs filter path breakage, and runtime/provided logging conflicts. Test signals are `mvn -pl hadoop-hdds/framework test`, annotation-generated config files, SpotBugs, enforcer checks, and test-jar consumers.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/ExitManager.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/ExitManager.java

## Purpose
`ExitManager` wraps Ratis `ExitUtils.terminate` so services can be terminated on unrecoverable errors while tests can replace or intercept exit behavior.

## Important APIs, Types, and Functions
It exposes `exitSystem(int,String,Throwable,Logger)`, `exitSystem(int,String,Logger)`, `forceExit(int,Exception,Logger)`, and `forceExit(int,String,Logger)`.

## Control Flow
Each method delegates directly to the appropriate `ExitUtils.terminate` overload, deriving an exception message for `forceExit(int,Exception,Logger)`.

## State and Persistence Behavior
No state is owned. Effects are process termination or test-intercepted termination.

## Dependencies and Integration Points
It depends on `org.apache.ratis.util.ExitUtils` and SLF4J `Logger`, and integrates with HDDS service fatal-error paths.

## Risks and Test Signals
Risks include accidental real JVM termination in tests and losing exception detail through localized messages. Test signals are service fatal-error tests with mocked/replaced exit manager and Ratis ExitUtils interception.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/ExitManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/DatanodeRatisGrpcConfig.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/DatanodeRatisGrpcConfig.java

## Purpose
`DatanodeRatisGrpcConfig` declares the typed HDDS config bean for datanode Ratis gRPC settings.

## Important APIs, Types, and Functions
It is annotated `@ConfigGroup` with the HDDS datanode Ratis plus Ratis gRPC prefix. It defines config key `hdds.ratis.raft.grpc.flow.control.window`, default `5MB`, type `SIZE`, tags `OZONE`, `CLIENT`, and `PERFORMANCE`, and getter/setter `getFlowControlWindow`/`setFlowControlWindow`.

## Control Flow
There is no runtime algorithm beyond config binding. The annotation processor and Ozone configuration reflection populate the bean from configuration.

## State and Persistence Behavior
The bean stores `flowControlWindow` as an int in bytes. Persistent configuration lives in XML/properties; this object is runtime state.

## Dependencies and Integration Points
It depends on HDDS config annotations, `RatisHelper.HDDS_DATANODE_RATIS_PREFIX_KEY`, and Ratis `GrpcConfigKeys.PREFIX`. It feeds datanode Ratis gRPC setup.

## Risks and Test Signals
Risks include int overflow for large sizes, setting a window smaller than chunk size, and prefix/key duplication mismatches. Test signals include generated config docs, config binding tests, and datanode Ratis write throughput with large chunks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/DatanodeRatisGrpcConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/DatanodeRatisServerConfig.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/DatanodeRatisServerConfig.java

## Purpose
`DatanodeRatisServerConfig` declares typed configuration for datanode Ratis server behavior, timeouts, stream settings, log cleanup, pre-vote, and appender wait timing.

## Important APIs, Types, and Functions
It is annotated with `@ConfigGroup` for HDDS datanode Ratis plus Ratis server prefix. Config fields include request timeout, watch timeout, no-leader timeout, follower slowness timeout, pending request limit, datastream request threads, datastream client pool size, delete-Ratis-log-directory flag, pre-vote flag, and log appender minimum wait. Getters/setters expose each value, although the boolean setter for log directory cleanup is named `setLeaderNumPendingRequests(boolean)`.

## Control Flow
Runtime flow is config binding and later use by datanode/Ratis setup code. Duration setters convert to milliseconds.

## State and Persistence Behavior
The bean stores runtime config values; persistent values live in Ozone configuration files. Defaults are initialized in fields and annotations.

## Dependencies and Integration Points
It depends on HDDS config annotations/tags, `RatisHelper.HDDS_DATANODE_RATIS_PREFIX_KEY`, and Ratis `RaftServerConfigKeys.PREFIX`. It integrates with Ratis server construction and pipeline lifecycle behavior.

## Risks and Test Signals
Risks include setter name mismatch for `shouldDeleteRatisLogDirectory`, timeout relationships that can destabilize writes/watch behavior, and generated config metadata drift. Test signals include annotation processor output, config binding tests, Ratis pipeline creation/removal, pre-vote behavior, and datastream load tests.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/DatanodeRatisServerConfig.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/HddsConfServlet.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/HddsConfServlet.java

## Purpose
`HddsConfServlet` exposes running HDDS/Ozone configuration over HTTP in XML/JSON and supports tag-oriented configuration queries.

## Important APIs, Types, and Functions
It extends `HttpServlet`, owns constants `COMMAND` and static `OZONE_CONFIG`, and implements `doGet`, `getConfFromContext`, `processCommand`, `processConfigTagRequest`, `buildDescriptionMap`, `parseXmlDescriptions`, `getTextContent`, and `getOzoneConfig`.

## Control Flow
`doGet` first checks instrumentation access through `HttpServer2`, chooses response format defaulting to XML, reads `name` and `cmd`, and delegates. Without `cmd`, it writes full or named configuration as JSON or XML. With `cmd`, it handles `getOzoneTags` and `getPropertyByTag`; the latter validates `tags`, builds a description map by securely parsing configured XML resources, collects tagged properties, and writes JSON.

## State and Persistence Behavior
The servlet reads live configuration from servlet context for dump requests and uses a static `OZONE_CONFIG` for tag metadata/property lookup. It owns no persistent state; XML parsing is per request.

## Dependencies and Integration Points
It depends on servlet APIs, `OzoneConfiguration`, `HttpServer2`, `HttpServletUtils`, `JsonUtils`, Hadoop XML security utilities, DOM parsing, and configuration resource files.

## Risks and Test Signals
Risks include expensive XML parsing per tag request, static config differing from daemon live config, exposure of sensitive values if redaction is not handled by dump methods, and command validation/format errors. Tests should cover instrumentation access denial, XML/JSON output, named property lookup, invalid command/tag parameters, secure XML parsing, and tag-description enrichment.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/HddsConfServlet.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/ReconfigurableBase.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/ReconfigurableBase.java

## Purpose
`ReconfigurableBase` is an HDDS base class for Hadoop-style dynamic runtime reconfiguration.

## Important APIs, Types, and Functions
It extends `Configured` and implements `Reconfigurable`. Important fields include `reconfigThread`, `shouldRun`, `reconfigLock`, `startTime`, `endTime`, `status`, and completion callbacks. APIs include abstract `getNewConf`, `startReconfigurationTask`, `getReconfigurationTaskStatus`, `shutdownReconfigurationTask`, final `reconfigureProperty`, abstract `getReconfigurableProperties`, `isPropertyReconfigurable`, abstract `reconfigurePropertyImpl`, nested `ReconfigurationThread`, and `addReconfigurationCompleteCallback`.

## Control Flow
`startReconfigurationTask` rejects stopped or already-running tasks, starts a daemon thread, and records start time. The thread loads new config, computes changed properties, redacts log values, skips non-reconfigurable changes, applies reconfigurable ones through `reconfigurePropertyImpl`, updates old config, records optional error messages, marks end time/status, clears the thread, and invokes callbacks. Direct `reconfigureProperty` applies one property under the configuration lock.

## State and Persistence Behavior
Runtime state records task lifecycle and last status. Applied changes mutate the in-memory `Configuration`; persistence back to config files is not handled here.

## Dependencies and Integration Points
It depends on Hadoop `Configuration`, `Reconfigurable`, `ReconfigurationUtil`, `ReconfigurationTaskStatus`, `ConfigRedactor`, Guava `Maps`, and subclasses that define supported properties and reload sources.

## Risks and Test Signals
Risks include callback execution under `reconfigLock`, `shutdownReconfigurationTask` joining a thread after clearing the field, callbacks calling status while lock is held, and in-memory changes diverging from files. Tests should cover concurrent start rejection, status while running/finished, non-reconfigurable skips, exception capture, callback behavior, shutdown, and redaction.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/ReconfigurableBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/ReconfigurationChangeCallback.java -->
# sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/ReconfigurationChangeCallback.java

## Purpose
`ReconfigurationChangeCallback` is a functional interface for code that wants to react to configuration property changes.

## Important APIs, Types, and Functions
It declares one method: `onPropertiesChanged(Map<String, Boolean> changedKeys, Configuration newConf)`.

## Control Flow
There is no implementation flow in the interface. Callers provide lambdas or classes that receive changed-key metadata and the new configuration.

## State and Persistence Behavior
No state is owned by the interface.

## Dependencies and Integration Points
It depends on Hadoop `Configuration` and integrates with reconfiguration handlers/callback consumers elsewhere in HDDS.

## Risks and Test Signals
Risks include ambiguous Boolean semantics in `changedKeys` unless documented by callers and callback exceptions affecting reconfiguration code if not isolated. Test signals should cover callback invocation with expected changed-key maps and exception handling by the caller.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/framework/src/main/java/org/apache/hadoop/hdds/conf/ReconfigurationChangeCallback.java -->
