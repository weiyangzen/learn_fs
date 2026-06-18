# subset-b-007358 Research

Grouped source-tree-aligned research for the Hadoop raw erasure coder and TFile/BCFile files in this work item.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/ByteArrayDecodingState.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/ByteArrayDecodingState.java

Purpose: package-private decode-call state for byte-array raw erasure decoding. It records `RawErasureDecoder`, `inputs`, `inputOffsets`, `erasedIndexes`, `outputs`, `outputOffsets`, and `decodeLength`, allowing implementations to work with offset-aware `byte[][]` without revalidating call shape.

Important APIs/types/functions: constructors for public byte-array decode calls and converted heap `ByteBuffer` calls; `convertToByteBufferState()` for native/direct coders; `checkInputBuffers()` and `checkOutputBuffers()` for length/null/recoverability validation.

Control flow: the main constructor finds the first non-null input, sets `decodeLength` from its full array length, checks MDS-style parameters via `DecodingState`, accepts null inputs as erased/not-read positions, then requires at least `numDataUnits` valid inputs. Converted states preserve caller offsets and skip validation because the source `ByteBufferDecodingState` already validated logical ranges.

State and persistence: per-call only; no durable state. Offsets are significant because array-backed `ByteBuffer` decode passes can target slices.

Dependencies and integration: used by `RawErasureDecoder.decode(byte[][], ...)`, Java coders, and native adapters that convert arrays to direct buffers.

Risks: the direct public constructor assumes whole arrays and cannot express non-zero offsets; invalid null outputs throw immediately. Test signals should cover insufficient valid inputs, erased/output length mismatch, conversion offset correctness, and mixed null input scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/ByteArrayDecodingState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/ByteArrayEncodingState.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/ByteArrayEncodingState.java

Purpose: package-private encode-call state for byte-array raw erasure encoders. It normalizes `byte[][]` inputs/outputs into a shared `EncodingState` contract with `inputOffsets`, `outputOffsets`, and `encodeLength`.

Important APIs/types/functions: public-call constructor, converted-state constructor, `convertToByteBufferState()`, and `checkBuffers(byte[][])`.

Control flow: the public constructor finds the first valid input, uses its array length as the encode length, validates input/output counts against the encoder options, ensures every input and output is non-null and exactly that length, then initializes zero offsets. `convertToByteBufferState()` clones each input range into a direct buffer and allocates direct output buffers, enabling native encoders to serve array callers.

State and persistence: per-call only. It does not move caller positions because byte arrays have no cursor; offsets are either zero for direct public calls or inherited from a heap `ByteBuffer` conversion.

Dependencies and integration: consumed by `RawErasureEncoder`, Java RS/XOR implementations, legacy RS, dummy coder, and native base classes.

Risks: array callers cannot encode slices without coming through `ByteBuffer`; native conversion allocates and copies, which is intentionally logged as inefficient elsewhere. Tests should check length validation, non-null enforcement, direct conversion copy-back through native adapters, and zero-length early-return behavior in `RawErasureEncoder`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/ByteArrayEncodingState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/ByteBufferDecodingState.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/ByteBufferDecodingState.java

Purpose: per-call decoding state for `ByteBuffer` inputs, including erased indexes, output buffers, direct/heap mode, and the common `decodeLength`.

Important APIs/types/functions: main constructor, converted-state constructor, `convertToByteArrayState()`, `checkInputBuffers()`, and `checkOutputBuffers()`.

Control flow: the constructor selects the first non-null input to infer `decodeLength` and directness, validates array sizes and recoverability through `DecodingState`, then checks every non-null input has matching `remaining()` and buffer type. Outputs must be non-null, same `remaining()`, and same directness. Heap buffers can be converted to arrays by recording `arrayOffset() + position()` for each buffer.

State and persistence: per-call only. It captures cursor-relative ranges, and `RawErasureDecoder` later advances non-null input positions by `decodeLength`; output positions are managed by caller/coder behavior.

Dependencies and integration: central for `RawErasureDecoder.decode(ByteBuffer[], ...)`, ECChunk decoding, Java coders, and native JNI coders.

Risks: `convertToByteArrayState()` assumes heap buffers expose backing arrays; this is safe because callers with direct buffers bypass conversion, but read-only or non-array heap buffers would fail if accepted. Tests should cover direct/heap mixing rejection, enough valid inputs, output length mismatch, null outputs, and position/array-offset preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/ByteBufferDecodingState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/ByteBufferEncodingState.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/ByteBufferEncodingState.java

Purpose: per-call encoding state for `ByteBuffer` inputs/outputs. It records the logical slice length, homogeneous direct/heap mode, and buffer arrays for low-level encoders.

Important APIs/types/functions: main constructor, converted-state constructor, `convertToByteArrayState()`, and `checkBuffers(ByteBuffer[])`.

Control flow: the main constructor uses the first valid input to set `encodeLength` and `usingDirectBuffer`, validates input/output counts through `EncodingState`, then rejects null buffers, mismatched `remaining()`, or mixed directness. Heap buffers can be converted to byte arrays by capturing array offsets at current positions.

State and persistence: per-call only. It does not itself advance positions; `RawErasureEncoder` snapshots and advances non-null input positions after encoding.

Dependencies and integration: used by all encoder implementations through `RawErasureEncoder.encode(ByteBuffer[], ...)`; native encoders prefer direct mode, while Java encoders can serve both direct and heap.

Risks: the conversion path assumes array-backed heap buffers; direct buffers use native/ByteBuffer code. Output positions are not restored or flipped by this class, so integration tests should verify caller-visible cursor semantics in `RawErasureEncoder`, length validation, directness homogeneity, and heap-array offsets for sliced buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/ByteBufferEncodingState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/CoderUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/CoderUtil.java

Purpose: shared raw-coder helper methods for zeroing buffers, converting `ECChunk` wrappers, cloning arrays into direct buffers, and finding null/valid indexes.

Important APIs/types/functions: `getEmptyChunk()`, `resetBuffer()` overloads, `resetOutputBuffers()` overloads, `toBuffers(ECChunk[])`, `cloneAsDirectByteBuffer()`, `getNullIndexes()`, `findFirstValidInput()`, and `getValidIndexes()`.

Control flow: zeroing uses a shared cached zero-filled `byte[]`, growing it under a class lock when a larger request arrives. `toBuffers` unwraps chunk buffers and materializes all-zero chunks by zeroing their buffer range. Index helpers compact matching positions into freshly sized arrays.

State and persistence: only static in-memory `emptyChunk` cache persists. No file or durable state.

Dependencies and integration: used throughout raw coder state validation, Java coders, legacy RS, native conversion, and `DecodingValidator`.

Risks: `resetBuffer(ByteBuffer)` temporarily advances then restores position but requires enough remaining capacity; `getEmptyChunk` cache growth can retain a large array for process lifetime. Test signals should cover all-zero ECChunk conversion, null and valid index extraction, first-valid failure, position preservation after reset, and concurrent zero-cache growth.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/CoderUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/DecodingState.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/DecodingState.java

Purpose: base package-private state for decode operations, holding the decoder and common `decodeLength`, plus MDS-style parameter validation.

Important APIs/types/functions: fields `decoder` and `decodeLength`; generic `checkParameters(T[] inputs, int[] erasedIndexes, T[] outputs)`.

Control flow: validation requires the input array length to equal data plus parity units, output count to equal erased-index count, and erased count to be no more than parity units. Buffer-specific subclasses then enforce lengths, null rules, and valid-input count.

State and persistence: per-call in-memory only.

Dependencies and integration: subclassed by `ByteBufferDecodingState` and `ByteArrayDecodingState`; enforces assumptions used by RS, XOR, native, and dummy decoders.

Risks: this assumes an MDS recovery model; non-MDS codes must override or avoid this validation. The first invalid input-length branch throws plain `IllegalArgumentException` while later checks throw `HadoopIllegalArgumentException`, which matters for tests expecting exception types. Test signals should exercise too many erasures, erased/output mismatch, wrong all-unit length, and subclass-specific recovery failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/DecodingState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/DecodingValidator.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/DecodingValidator.java

Purpose: validates decode outputs by using the same decoder to reconstruct one originally valid input from the produced outputs and remaining inputs, then comparing buffers.

Important APIs/types/functions: constructor with `RawErasureDecoder`; `validate(ByteBuffer[], int[], ByteBuffer[])`; `validate(ECChunk[], ...)`; buffer allocation/reset helpers; `getNewValidIndexes()` and `getNewErasedIndex()` visible for tests.

Control flow: it marks output buffers, chooses the first valid input as a shape template, allocates/reuses a validation buffer matching directness and at least remaining capacity, builds new inputs by substituting decoded outputs into erased positions, selects one original input as the new erased target, decodes into the validation buffer, then compares the reconstructed bytes with the original input. Finally it advances original inputs to limits and resets outputs to their marks.

State and persistence: holds reusable validation `ByteBuffer` plus last validation indexes for testing. No durable persistence.

Dependencies and integration: uses `CoderUtil`, `ECChunk`, `RawErasureDecoder`, and `InvalidDecodingException`.

Risks: recursively invokes the decoder, so decoder state/caching bugs can affect validation; caller must pass input positions at readable starts. Tests should cover successful validation, forced corrupted output, direct and heap buffers, position restoration of outputs, input advancement, and new valid-index selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/DecodingValidator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/DummyRawDecoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/DummyRawDecoder.java

Purpose: test/performance-isolation decoder that performs no reconstruction math and leaves outputs as the zeroed buffers prepared by caller-side state handling.

Important APIs/types/functions: constructor with `ErasureCoderOptions`; overrides `doDecode(ByteBufferDecodingState)` and `doDecode(ByteArrayDecodingState)`.

Control flow: after `RawErasureDecoder` validates parameters and builds state, these overrides return immediately. The class comment says it returns zero bytes, but this implementation relies on the base/caller path or external setup for zeroed outputs; unlike RS/XOR implementations it does not explicitly call `CoderUtil.resetOutputBuffers`.

State and persistence: stateless; no caches or resources.

Dependencies and integration: created by `DummyRawErasureCoderFactory` for `DUMMY_CODEC_NAME`; useful when measuring HDFS erasure-code plumbing without codec cost.

Risks: if outputs are not already zeroed by upstream code, this decoder can expose stale output contents. Tests should assert intended zero-output semantics, decode validation bypass expectations, and that it still enforces normal raw decoder input/output validation through the base class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/DummyRawDecoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/DummyRawEncoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/DummyRawEncoder.java

Purpose: test/performance-isolation encoder that performs no parity math and is intended to produce zero parity.

Important APIs/types/functions: constructor with `ErasureCoderOptions`; overrides `doEncode(ByteArrayEncodingState)` and `doEncode(ByteBufferEncodingState)`.

Control flow: the base encoder validates and dispatches to the matching override; both overrides return immediately. As with the dummy decoder, the comment assumes output buffers have already been reset, but this class itself does not zero them.

State and persistence: stateless and resource-free.

Dependencies and integration: instantiated by `DummyRawErasureCoderFactory`; integrates with the same raw encoder public API as real coders, so it can isolate block-management overhead from codec work.

Risks: stale output content is possible if upstream callers do not zero outputs before calling the dummy encoder. Tests should verify whether the surrounding erasure-code framework zeroes outputs, and should also cover normal validation, zero-length fast path, and direct/heap paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/DummyRawEncoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/DummyRawErasureCoderFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/DummyRawErasureCoderFactory.java

Purpose: factory binding Hadoop's dummy erasure codec name to no-op raw encoder/decoder implementations.

Important APIs/types/functions: constant `CODER_NAME = "dummy_dummy"`; `createEncoder()`, `createDecoder()`, `getCoderName()`, and `getCodecName()`.

Control flow: creation simply instantiates `DummyRawEncoder` or `DummyRawDecoder` with the supplied `ErasureCoderOptions`; codec metadata returns `ErasureCodeConstants.DUMMY_CODEC_NAME`.

State and persistence: stateless factory.

Dependencies and integration: implements `RawErasureCoderFactory`, so it can be selected by the raw coder registry/configuration path used by Hadoop erasure coding.

Risks: users must not treat this as data-protecting; it is for tests or performance isolation. Tests should verify registry metadata, factory creation with varied coder options, and that dummy coders are not selected accidentally for real RS/XOR policies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/DummyRawErasureCoderFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/EncodingState.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/EncodingState.java

Purpose: base package-private state for encode operations, storing the encoder and logical `encodeLength`, with shared input/output count validation.

Important APIs/types/functions: fields `encoder`, `encodeLength`; generic `checkParameters(T[] inputs, T[] outputs)`.

Control flow: validation requires input count to equal `encoder.getNumDataUnits()` and output count to equal `encoder.getNumParityUnits()`. Buffer-specific subclasses handle null, length, directness, and offset details.

State and persistence: per-call in-memory only.

Dependencies and integration: superclass of `ByteBufferEncodingState` and `ByteArrayEncodingState`; used before all Java/native/dummy encoder dispatch.

Risks: limited to count checks; tests must include subclass validation to catch invalid buffers. Exception text is generic, so higher-level tests should rely on behavior rather than overly strict messages unless needed for compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/EncodingState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/InvalidDecodingException.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/InvalidDecodingException.java

Purpose: checked exception signaling that decoded outputs failed validation.

Important APIs/types/functions: public class extending `IOException`; `serialVersionUID`; constructor accepting a description string.

Control flow: no internal logic beyond passing the message to `IOException`. It is thrown by `DecodingValidator` when reconstruction comparison fails.

State and persistence: exception instance state only.

Dependencies and integration: lets validation failures flow through existing raw decoder `IOException` signatures.

Risks: because it is an `IOException`, callers may conflate validation failure with transport or native-code failures unless they catch the specific subtype. Tests should check the subtype for corrupted decode output and ensure ordinary decoder errors are not incorrectly mapped to this class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/InvalidDecodingException.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/NativeRSRawDecoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/NativeRSRawDecoder.java

Purpose: JNI-backed Reed-Solomon raw decoder using Intel ISA-L.

Important APIs/types/functions: static native-code load check, constructor calling native `initImpl`, `performDecodeImpl()`, `release()`, `preferDirectBuffer()`, native `decodeImpl()` and `destroyImpl()`.

Control flow: class loading verifies native erasure code availability. Construction initializes a native coder under the write lock inherited from `AbstractNativeRawDecoder`. Decode calls enter the base native class, which captures ByteBuffer offsets and delegates to `performDecodeImpl`; this class forwards to JNI. `release()` destroys native state under the write lock.

State and persistence: native coder pointer lives in the superclass private field and is owned for the Java object lifetime. No durable state.

Dependencies and integration: depends on `ErasureCodeNative`, `ErasureCoderOptions`, and `AbstractNativeRawDecoder`; produced by `NativeRSRawErasureCoderFactory`.

Risks: unavailable native libraries fail at class load/construction; using after `release()` raises `IOException` in the base class. Tests should cover native availability gating, direct-buffer preference, release idempotency expectations, decode correctness against Java RS, and array-call conversion through direct buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/NativeRSRawDecoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/NativeRSRawEncoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/NativeRSRawEncoder.java

Purpose: JNI-backed Reed-Solomon raw encoder using Intel ISA-L.

Important APIs/types/functions: static `ErasureCodeNative.checkNativeCodeLoaded()`, constructor/native `initImpl`, `performEncodeImpl()`, `release()`, `preferDirectBuffer()`, native `encodeImpl()` and `destroyImpl()`.

Control flow: constructor initializes native RS state under the encoder write lock. Public encode calls use `AbstractNativeRawEncoder`, which rejects closed native state, gathers input/output offsets, and calls this class's JNI delegate. `release()` destroys native resources under the write lock.

State and persistence: native coder state persists for the encoder object lifetime only.

Dependencies and integration: created by `NativeRSRawErasureCoderFactory`; integrates with the same `RawErasureEncoder` API and prefers direct buffers for performance.

Risks: native library/configuration dependence and JNI resource lifecycle dominate. Array inputs are converted and copied, so tests should cover direct-buffer fast path, heap-array fallback copy-back, release behavior, and parity equivalence with `RSRawEncoder` for representative schemas.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/NativeRSRawEncoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/NativeRSRawErasureCoderFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/NativeRSRawErasureCoderFactory.java

Purpose: factory for ISA-L native Reed-Solomon raw coders.

Important APIs/types/functions: `CODER_NAME = "rs_native"`; `createEncoder()`, `createDecoder()`, `getCoderName()`, `getCodecName()`.

Control flow: creation instantiates `NativeRSRawEncoder` or `NativeRSRawDecoder`, triggering native-code checks/initialization. Metadata binds the coder to `ErasureCodeConstants.RS_CODEC_NAME`.

State and persistence: stateless factory.

Dependencies and integration: implements `RawErasureCoderFactory`; selected by Hadoop raw coder configuration for RS policies when native support is preferred/available.

Risks: factory creation can fail if native code is not loaded, unlike Java factories. Tests should verify metadata names, successful creation under native-enabled builds, and fallback behavior in higher-level registry code when native creation is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/NativeRSRawErasureCoderFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/NativeXORRawDecoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/NativeXORRawDecoder.java

Purpose: JNI-backed XOR raw decoder using Intel ISA-L.

Important APIs/types/functions: native load check, constructor/native `initImpl`, `performDecodeImpl()`, `release()`, native `decodeImpl()` and `destroyImpl()`.

Control flow: construction initializes native XOR state under `decoderLock`. Decode requests flow through `AbstractNativeRawDecoder`, including offset capture and closed-state checking, then call JNI with inputs, erased indexes, outputs, and offsets. Release destroys native state under write lock.

State and persistence: native coder state is object-scoped; no durable state.

Dependencies and integration: depends on `ErasureCodeNative`, `ErasureCoderOptions`, and native base decoder; factory is `NativeXORRawErasureCoderFactory`.

Risks: this class does not override `preferDirectBuffer()`, but inherits `true` from `AbstractNativeRawDecoder`. Tests should cover one-erasure XOR decode semantics, native availability, release behavior, direct/heap conversion, and parity with `XORRawDecoder`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/NativeXORRawDecoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/NativeXORRawEncoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/NativeXORRawEncoder.java

Purpose: JNI-backed XOR raw encoder using Intel ISA-L.

Important APIs/types/functions: static native-code check, constructor/native `initImpl`, `performEncodeImpl()`, `release()`, native `encodeImpl()` and `destroyImpl()`.

Control flow: construction initializes native state under encoder write lock. Public encode calls in `AbstractNativeRawEncoder` validate native state, capture buffer offsets, and delegate to this class's JNI method. Release destroys the native coder under lock.

State and persistence: native pointer is object-scoped in the superclass.

Dependencies and integration: created by `NativeXORRawErasureCoderFactory`; participates in the same raw encoder API as Java XOR and inherits direct-buffer preference.

Risks: native dependency and heap-call conversion overhead. Tests should validate direct path, array fallback copy-back, release/closed behavior, and output parity equivalence with Java XOR for varied data lengths including non-8-byte multiples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/NativeXORRawEncoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/NativeXORRawErasureCoderFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/NativeXORRawErasureCoderFactory.java

Purpose: factory for ISA-L native XOR raw coders.

Important APIs/types/functions: `CODER_NAME = "xor_native"`; `createEncoder()`, `createDecoder()`, `getCoderName()`, `getCodecName()`.

Control flow: simple factory methods instantiate native XOR encoder/decoder and return codec metadata for `ErasureCodeConstants.XOR_CODEC_NAME`.

State and persistence: stateless.

Dependencies and integration: plugs into the `RawErasureCoderFactory` registry/configuration path for XOR policies.

Risks: native creation can fail at class load or construction if ISA-L/Hadoop native code is unavailable. Tests should cover name/codec metadata, native-enabled construction, and higher-level fallback to Java XOR when this factory cannot instantiate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/NativeXORRawErasureCoderFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RSLegacyRawDecoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RSLegacyRawDecoder.java

Purpose: older pure-Java Reed-Solomon decoder based on HDFS-RAID style Vandermonde/Galois-field operations.

Important APIs/types/functions: `errSignature`, `primitivePower`; overrides public `decode()` for ByteBuffer and byte arrays to reorder data/parity; `doDecodeImpl()` overloads; `doDecode()` overloads; `adjustOrder()`; temporary buffer helpers.

Control flow: public decode reorders caller layout from data-first/parity-after to the parity-first layout expected by the legacy math. The internal decode identifies null inputs as erased/not-read positions, maps requested erased indexes to caller outputs, allocates temporary buffers for unrequested nulls, computes syndromes with `RSUtil.GF.substitute`, then solves a Vandermonde system to recover missing units.

State and persistence: object-scoped `errSignature` and `primitivePower`; temporary buffers are per call in the current code. No durable state.

Dependencies and integration: extends `RawErasureDecoder`, uses `CoderUtil`, `RSUtil`, `GaloisField`, and `ErasureCoderOptions`; produced by legacy RS factory.

Risks: can compute unrequested not-read units unnecessarily; comments flag HADOOP-11871. `allowChangeInputs()` is relevant indirectly via legacy encoder, while decoder mutates outputs/temp buffers. Tests should cover data and parity erasures, order adjustment, nulls matching erased indexes, too many erasures, and parity with modern RS/native coders where compatible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RSLegacyRawDecoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RSLegacyRawEncoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RSLegacyRawEncoder.java

Purpose: older pure-Java Reed-Solomon encoder using a generating polynomial and Galois-field remainder calculation.

Important APIs/types/functions: object field `generatingPolynomial`; constructor polynomial generation; `doEncode(ByteBufferEncodingState)`; `doEncode(ByteArrayEncodingState)`.

Control flow: construction computes primitive powers for all units and multiplies `(root + x)` factors to build the generating polynomial. Encoding zeroes parity outputs, builds an array ordered as parity units followed by data units, optionally copies input data when `allowChangeInputs()` is false, then invokes `RSUtil.GF.remainder()` to compute parity in-place.

State and persistence: generating polynomial is schema-scoped and object-persistent. No durable state.

Dependencies and integration: extends `RawErasureEncoder`, uses `RSUtil`, `GaloisField`, `CoderUtil`, and `ErasureCoderOptions`; created by `RSLegacyRawErasureCoderFactory`.

Risks: `assert` enforces field-size constraints only when assertions are enabled; modern RS uses explicit exceptions. When `allowChangeInputs()` is true the input buffers can be modified by `remainder()`. Tests should cover both allow-change settings, direct and heap paths, parity compatibility with legacy decoder, and field-size boundary handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RSLegacyRawEncoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RSLegacyRawErasureCoderFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RSLegacyRawErasureCoderFactory.java

Purpose: factory for legacy Java Reed-Solomon raw coders.

Important APIs/types/functions: `CODER_NAME = "rs-legacy_java"`; `createEncoder()`, `createDecoder()`, `getCoderName()`, `getCodecName()`.

Control flow: factory methods create `RSLegacyRawEncoder` and `RSLegacyRawDecoder`; codec metadata returns `ErasureCodeConstants.RS_LEGACY_CODEC_NAME`.

State and persistence: stateless.

Dependencies and integration: implements `RawErasureCoderFactory`; used for configurations requiring compatibility with the legacy RS codec.

Risks: legacy algorithm behavior differs from modern ISA-L-compatible RS. Tests should ensure registry mapping stays distinct from `rs_java`, and that old-format policies choose this factory only when intended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RSLegacyRawErasureCoderFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RSRawDecoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RSRawDecoder.java

Purpose: modern pure-Java Reed-Solomon decoder compatible with ISA-L/native RS behavior.

Important APIs/types/functions: `encodeMatrix`; cached `decodeMatrix`, `invertMatrix`, `gfTables`, `cachedErasedIndexes`, `validIndexes`, `erasureFlags`; `doDecode()` overloads; `prepareDecoding()`; `processErasures()`; `generateDecodeMatrix()`.

Control flow: construction builds a Cauchy encode matrix and checks total units fit GF(256). Decode zeroes outputs, prepares/reuses decode tables keyed by erased indexes and valid indexes, selects the first `numDataUnits` valid inputs, then calls `RSUtil.encodeData()` with decode coefficients. Decode matrix generation inverts the selected valid rows and derives rows for erased data or parity units.

State and persistence: schema matrix and cached decode tables persist in the decoder instance; no durable state. Public decoder methods are synchronized in the base class, helping protect mutable cache fields.

Dependencies and integration: uses `GF256`, `RSUtil`, `DumpUtil`, `CoderUtil`, and raw decoding state classes; produced by `RSRawErasureCoderFactory`.

Risks: `GF256.gfInvertMatrix()` mutates its input temporary matrix and throws runtime errors for singular matrices. Cache correctness depends on valid-index comparison. Tests should cover multiple erasure patterns, parity erasures, cache reuse/invalidation, direct and heap buffers, verbose dump mode, and compatibility with native RS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RSRawDecoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RSRawEncoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RSRawEncoder.java

Purpose: modern pure-Java Reed-Solomon encoder compatible with ISA-L/native RS coder semantics.

Important APIs/types/functions: schema-scoped `encodeMatrix` and `gfTables`; constructor matrix/table generation; `doEncode()` overloads.

Control flow: construction validates total units are below GF(256) field size, builds a Cauchy matrix with identity data rows and parity rows, optionally dumps the matrix/tables, and initializes GF multiplication tables for parity rows. Encoding zeroes outputs then runs `RSUtil.encodeData()` over all data inputs into parity outputs.

State and persistence: encode matrix and precomputed GF tables persist for encoder lifetime; no durable state.

Dependencies and integration: extends `RawErasureEncoder`; uses `RSUtil`, `GF256` indirectly, `DumpUtil`, `CoderUtil`, and `ErasureCoderOptions`; produced by `RSRawErasureCoderFactory`.

Risks: output buffers must be reset before XOR-accumulating table products, which this class does explicitly. Tests should cover field-size boundary rejection, direct/heap parity equality, non-8-byte data lengths in `RSUtil.encodeData`, verbose dump mode, and native compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RSRawEncoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RSRawErasureCoderFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RSRawErasureCoderFactory.java

Purpose: factory for modern pure-Java Reed-Solomon raw coders.

Important APIs/types/functions: `CODER_NAME = "rs_java"`; `createEncoder()`, `createDecoder()`, `getCoderName()`, `getCodecName()`.

Control flow: factory methods instantiate `RSRawEncoder` and `RSRawDecoder` with supplied options. Metadata binds the factory to `ErasureCodeConstants.RS_CODEC_NAME`.

State and persistence: stateless.

Dependencies and integration: implements `RawErasureCoderFactory`; typically used as fallback when native RS is unavailable or when Java implementation is configured.

Risks: must remain distinct from `rs_native` and `rs-legacy_java` in registry/config. Tests should verify metadata and factory outputs, plus higher-level fallback ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RSRawErasureCoderFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RawErasureCoderFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RawErasureCoderFactory.java

Purpose: factory interface for creating paired raw erasure encoders/decoders and exposing coder/codec names for configuration.

Important APIs/types/functions: `createEncoder(ErasureCoderOptions)`, `createDecoder(ErasureCoderOptions)`, `getCoderName()`, `getCodecName()`.

Control flow: no implementation logic; concrete factories bind names such as `rs_java`, `rs_native`, `xor_java`, and dummy coders to raw coder classes.

State and persistence: interface only.

Dependencies and integration: consumed by Hadoop's erasure-code raw coder selection layer; implementors in this set cover Java, native, legacy, XOR, and dummy coders.

Risks: factory metadata drives configuration behavior, so name collisions or wrong codec names can route production policies to incompatible implementations. Tests should enumerate factories, assert unique coder names, and verify codec-name mapping to `ErasureCodeConstants`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RawErasureCoderFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RawErasureDecoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RawErasureDecoder.java

Purpose: abstract public-facing base for low-level raw erasure decoding over `ByteBuffer`, `byte[][]`, and `ECChunk`.

Important APIs/types/functions: synchronized `decode()` overloads; abstract `doDecode()` overloads; option accessors; `preferDirectBuffer()`, `allowChangeInputs()`, `allowVerboseDump()`, and `release()`.

Control flow: `ByteBuffer` decode constructs `ByteBufferDecodingState`, returns early for zero length, snapshots input positions, dispatches direct buffers to `doDecode(ByteBuffer...)` or converts heap buffers to byte arrays, then advances non-null input positions by consumed length. Byte-array decode builds `ByteArrayDecodingState` and dispatches. ECChunk decode unwraps via `CoderUtil.toBuffers`.

State and persistence: owns immutable `ErasureCoderOptions`; otherwise intended stateless, though subclasses may cache matrices/native handles. Decode methods are synchronized to protect mutable subclass decoder state.

Dependencies and integration: superclass for Java RS/XOR, legacy, native, dummy decoders; integrates with `ECChunk` and raw state classes.

Risks: output position semantics rely on implementations; heap ByteBuffer conversion requires array-backed buffers. Tests should cover input position advancement, zero-length return, erased/null semantics, direct-vs-heap dispatch, ECChunk all-zero handling, release behavior in subclasses, and synchronized cache safety.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RawErasureDecoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RawErasureEncoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RawErasureEncoder.java

Purpose: abstract public-facing base for low-level raw erasure encoding over `ByteBuffer`, `byte[][]`, and `ECChunk`.

Important APIs/types/functions: `encode()` overloads; abstract `doEncode()` overloads; data/parity/all-unit accessors; `preferDirectBuffer()`, `allowChangeInputs()`, `allowVerboseDump()`, and `release()`.

Control flow: `ByteBuffer` encode validates through `ByteBufferEncodingState`, returns for zero length, snapshots input positions, dispatches direct buffers to `doEncode(ByteBuffer...)` or converts heap buffers to byte arrays, then advances non-null input positions by encoded length. Byte-array encode constructs `ByteArrayEncodingState` and dispatches. ECChunk encode unwraps using `ECChunk.toBuffers`.

State and persistence: stores immutable `ErasureCoderOptions`; subclasses may hold schema matrices or native handles.

Dependencies and integration: superclass for Java, native, legacy, XOR, and dummy encoders; entry point used by higher-level Hadoop erasure coding.

Risks: encoder methods are not synchronized unlike decoder methods, so stateful encoders must handle thread-safety themselves. Tests should cover cursor advancement, direct/heap behavior, zero-length calls, output initialization by implementations, `allowChangeInputs()` effects, and ECChunk wrapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RawErasureEncoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/XORRawDecoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/XORRawDecoder.java

Purpose: pure-Java XOR decoder for single-erasure XOR parity schemes.

Important APIs/types/functions: constructor; `doDecode(ByteBufferDecodingState)`; `doDecode(ByteArrayDecodingState)`.

Control flow: each decode resets the single output, reads the first erased index, skips that input position, and XORs all remaining input bytes into output. ByteBuffer code uses absolute `get/put` over positions/limits; byte-array code uses offsets and `decodeLength`.

State and persistence: stateless.

Dependencies and integration: extends `RawErasureDecoder`, uses `CoderUtil`, and is created by `XORRawErasureCoderFactory`.

Risks: it assumes exactly one output/erased index, as XOR with one parity unit cannot recover multiple erasures; base validation prevents erasures greater than parity count. Null inputs other than the erased index would cause failures in the loop, so caller null set must be valid. Tests should cover data and parity erasure, direct/heap equality, null input behavior, and output zeroing before accumulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/XORRawDecoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/XORRawEncoder.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/XORRawEncoder.java

Purpose: pure-Java XOR encoder that computes one parity output by XORing all data inputs.

Important APIs/types/functions: constructor; `doEncode(ByteBufferEncodingState)`; `doEncode(ByteArrayEncodingState)`.

Control flow: encoding zeroes outputs, copies the first input into output, then XORs each subsequent input byte over the same output positions. It uses absolute buffer access so caller positions are left for the base class to advance.

State and persistence: stateless.

Dependencies and integration: extends `RawErasureEncoder`, uses `CoderUtil`, and is produced by `XORRawErasureCoderFactory`.

Risks: assumes a single parity output; if configured with multiple parity units, only output 0 is filled while validation would permit the output array length. Tests should assert intended parity-unit constraints at higher layers, direct/heap equality, non-zero output clearing, and odd data lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/XORRawEncoder.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/XORRawErasureCoderFactory.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/XORRawErasureCoderFactory.java

Purpose: factory for pure-Java XOR raw coders.

Important APIs/types/functions: `CODER_NAME = "xor_java"`; `createEncoder()`, `createDecoder()`, `getCoderName()`, `getCodecName()`.

Control flow: instantiates `XORRawEncoder`/`XORRawDecoder` and reports `ErasureCodeConstants.XOR_CODEC_NAME`.

State and persistence: stateless.

Dependencies and integration: implements `RawErasureCoderFactory`; Java fallback or configured implementation for XOR codec.

Risks: ensure XOR policies use one parity unit or higher-level validation prevents unsupported shapes. Tests should verify metadata, object creation, and registry/fallback behavior relative to `xor_native`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/XORRawErasureCoderFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/package-info.java

Purpose: package-level documentation and annotations for raw erasure coders.

Important APIs/types/functions: package annotations `@InterfaceAudience.Private` and `@InterfaceStability.Unstable`.

Control flow: documentation explains that raw erasure coders are low-level math components used by higher-level erasure coders, operating on groups of byte buffers/chunks rather than block-group layout.

State and persistence: none.

Dependencies and integration: imports Hadoop classification annotations and applies them to `org.apache.hadoop.io.erasurecode.rawcoder`.

Risks: signals non-public, unstable API; external use should not rely on compatibility. Tests are not direct, but release checks should ensure package annotations remain aligned with intended API stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/util/DumpUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/util/DumpUtil.java

Purpose: debug-only helpers for printing erasure-code matrices and chunk bytes.

Important APIs/types/functions: `bytesToHex(byte[], int)`, `dumpMatrix(byte[], int, int)`, `dumpChunks(String, ECChunk[])`, and `dumpChunk(ECChunk)`.

Control flow: `bytesToHex` formats bytes as uppercase hex with a `0x` prefix and spaces; non-positive or too-large limits mean full length. Matrix/chunk methods print directly to `System.out`.

State and persistence: stateless; output goes to process stdout only.

Dependencies and integration: used by RS encoder/decoder verbose-dump paths and accepts `ECChunk`.

Risks: direct stdout use is unsuitable for production logging and can leak data when verbose dump is enabled. `dumpMatrix` indexing appears oriented by caller-provided dimensions and should be tested with expected matrix layout. Test signals include hex formatting limits, null chunk output, and avoiding verbose dump in production defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/util/DumpUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/util/GF256.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/util/GF256.java

Purpose: optimized GF(256) arithmetic helper for modern RS coding, ported from ISA-L concepts.

Important APIs/types/functions: static base/log tables; static `theGfMulTab`; `gfMulTab()`, `gfMul(byte, byte)`, `gfInv(byte)`, `gfInvertMatrix(byte[], byte[], int)`, and `gfVectMulInit(byte, byte[], int)`.

Control flow: class initialization precomputes a full 256x256 multiplication table. Multiplication uses log/antilog tables; inversion returns zero for zero input. Matrix inversion performs Gauss-Jordan elimination over GF(256), mutating the input matrix and writing the inverse to `outMatrix`. Vector table initialization builds the 32-byte ISA-L-style nibble multiplication table for a coefficient.

State and persistence: static immutable lookup tables after initialization; no durable state.

Dependencies and integration: used by `RSUtil`, `RSRawDecoder`, and modern RS table generation.

Risks: `gfInvertMatrix` mutates its input and throws `RuntimeException` for singular matrices; callers must pass a disposable matrix. Tests should verify multiplication/inversion identities, matrix inversion on known matrices, singular matrix failure, and coefficient table compatibility with `RSUtil.encodeData`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/util/GF256.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/util/GaloisField.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/util/GaloisField.java

Purpose: general GF(2^p) arithmetic implementation, defaulting to GF(256) with primitive polynomial 285, used mainly by legacy RS code.

Important APIs/types/functions: singleton `getInstance()`/`getInstance(fieldSize, polynomial)`, arithmetic `add`, `multiply`, `divide`, `power`, polynomial `multiply`, `add`, `remainder`, `substitute`, bulk `solveVandermondeSystem` overloads, bulk `remainder`/`substitute`, and `gaussianElimination`.

Control flow: construction builds log, power, multiplication, and division tables. Singleton instances are cached under a synchronized map. Bulk methods apply table arithmetic over byte arrays or ByteBuffers at current offsets/positions, often mutating output/dividend buffers in place.

State and persistence: process-static singleton cache; per-instance lookup tables. No durable persistence.

Dependencies and integration: used by `RSUtil.GF`, legacy encoder/decoder, and RS primitive-power helpers.

Risks: many methods rely on Java `assert` for argument validation and mutate inputs. `gaussianElimination` pivot scan appears unusual (`matrix[i][j]`) and deserves regression coverage if used. Tests should cover arithmetic identities, Vandermonde solving, remainder/substitute byte and ByteBuffer paths, singleton cache behavior, and input mutation expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/util/GaloisField.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/util/RSUtil.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/util/RSUtil.java

Purpose: Reed-Solomon utility layer shared by Java RS coders, including matrix generation, GF table initialization, and table-driven data encoding.

Important APIs/types/functions: public `GF`, `PRIMITIVE_ROOT`; `getPrimitivePower()`, `initTables()`, `genCauchyMatrix()`, and `encodeData()` overloads for byte arrays and ByteBuffers.

Control flow: `genCauchyMatrix` writes identity data rows and Cauchy parity rows using `GF256.gfInv(i ^ j)`. `initTables` expands matrix coefficients into 32-byte multiplication tables. `encodeData` XOR-accumulates table-multiplied input bytes into outputs, processing eight bytes per loop then a tail.

State and persistence: static `GaloisField` singleton reference; all encode state is caller-provided.

Dependencies and integration: core for `RSRawEncoder`, `RSRawDecoder`, and legacy primitive-power helpers; uses `GF256`.

Risks: outputs must be zeroed by callers before `encodeData` because it XORs into existing bytes. Tests should cover Cauchy matrix layout, table initialization offsets, byte-array/ByteBuffer parity equivalence, data lengths not divisible by eight, and compatibility with native ISA-L results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/util/RSUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/util/package-info.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/util/package-info.java

Purpose: package-level documentation and annotations for raw erasure coder utility classes.

Important APIs/types/functions: package annotations `@InterfaceAudience.Private` and `@InterfaceStability.Unstable`.

Control flow: no runtime logic; comment identifies the package as general helpers for raw erasure coder implementations.

State and persistence: none.

Dependencies and integration: imports Hadoop classification annotations and applies them to `org.apache.hadoop.io.erasurecode.rawcoder.util`.

Risks: the utilities are explicitly private/unstable, so external consumers should not depend on compatibility. Test signals are indirect through coders and package annotation checks if API surface is audited.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/util/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/BCFile.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/BCFile.java

Purpose: block-compressed physical storage layer beneath TFile, supporting compressed data blocks, named meta blocks, indexes, magic/version footer, and bounded block readers.

Important APIs/types/functions: `BCFile.Writer`, `Writer.BlockAppender`, `WBlockState`, `Reader`, `Reader.BlockReader`, `RBlockState`, `MetaIndex`, `MetaIndexEntry`, `DataIndex`, `Magic`, and `BlockRegion`.

Control flow: writer starts at file offset zero, writes magic, creates data blocks until the first meta block, records each closed block region, then on close writes the data-index as a meta block, serializes meta index, writes meta-index offset, version, and trailing magic. Reader seeks to the footer, verifies version/magic, reads meta index, opens the `BCFile.index` meta block, and reconstructs the data index. Block readers wrap `BoundedRangeFileInputStream` with the configured decompressor.

State and persistence: persists block regions, compression names, meta names with `data:` prefix, version, and magic in the BCFile format. Writer maintains in-progress/closed flags and an error counter.

Dependencies and integration: depends on Hadoop FS streams, `Compression`, `Utils.Version`, TFile buffer settings, `SimpleBufferedOutputStream`, and `CompareUtils` for offset lookup.

Risks: only one block appender may be open; data blocks after meta blocks are illegal. `DataOutputStream.size()` wraps for raw blocks above 4GB, noted in comments. Tests should cover footer parsing, duplicate/missing meta blocks, block order rules, compression codecs, corrupt magic/version, block index lookup, and resource return on exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/BCFile.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/BoundedRangeFileInputStream.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/BoundedRangeFileInputStream.java

Purpose: exposes a fixed byte range of a shared `FSDataInputStream` as an independent `InputStream`.

Important APIs/types/functions: constructor with stream/offset/length; `available()`, `read()` overloads, `skip()`, `mark()`, `reset()`, `markSupported()`, and `close()`.

Control flow: reads synchronize on the underlying FS stream, seek to this wrapper's logical position, read at most the remaining range, then advance the wrapper position. EOF clamps `end` to current position. `skip` only advances local position. `mark/reset` store and restore local position.

State and persistence: local `pos`, `end`, and `mark`; no durable state. Close nulls the underlying stream reference and invalidates range state.

Dependencies and integration: used by `BCFile.Reader.RBlockState` to constrain decompression to a block's compressed region.

Risks: after close, calling methods that dereference `in` can throw `NullPointerException`; close does not close the shared underlying stream. `available()` depends on underlying stream availability and clamps to range. Tests should cover independent wrappers over one FS stream, range EOF, mark/reset, invalid offsets, skip beyond end, and close behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/BoundedRangeFileInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/ByteArray.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/ByteArray.java

Purpose: lightweight adapter exposing a byte-array region as `RawComparable`.

Important APIs/types/functions: constructors from `BytesWritable`, whole `byte[]`, and `byte[]` slice; `buffer()`, `offset()`, and `size()`.

Control flow: slice constructor validates offset/length using bitwise bounds check, then stores references. Accessors return raw backing buffer and range metadata without copying.

State and persistence: immutable wrapper fields, but the underlying byte array remains mutable by external owners.

Dependencies and integration: used with `CompareUtils.BytesComparator` and Hadoop `RawComparator` workflows in TFile code.

Risks: no defensive copy, so comparisons can change if the backing array is mutated. Tests should cover bounds validation, `BytesWritable` length handling, whole/sliced wrappers, and comparator integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/ByteArray.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/Chunk.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/Chunk.java

Purpose: chunk-encoding utilities for representing sub-streams as length-prefixed chunk chains.

Important APIs/types/functions: `ChunkDecoder`, `ChunkEncoder`, and `SingleChunkEncoder`.

Control flow: encoded chains use VInt lengths where non-terminal chunks are negative and the terminal chunk is non-negative. `ChunkDecoder` reads chunk lengths lazily, tracks remaining bytes, and drains to the last chunk on close. `ChunkEncoder` buffers data and writes negative chunks until close writes the final positive-length chunk. `SingleChunkEncoder` writes the advertised size first, then enforces exactly that many bytes before close succeeds.

State and persistence: stream-local counters and buffers; chunk format is persisted to the underlying stream.

Dependencies and integration: uses `Utils.readVInt/writeVInt`; supports TFile sub-stream/data-block encoding patterns.

Risks: corrupted streams where data ends before declared chunk size raise `IOException`. `ChunkEncoder.close()` nulls internal buffer/out, making repeated use invalid. Tests should cover empty stream final chunk, multi-chunk data, reset reuse of decoder, advertised size under/over-write, close draining, skip semantics, and corrupt length/data cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/Chunk.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/CompareUtils.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/CompareUtils.java

Purpose: small comparator helpers for raw byte ranges and scalar offsets used by TFile/BCFile lookup code.

Important APIs/types/functions: `BytesComparator`, `Scalar`, `ScalarLong`, `ScalarComparator`, and `MemcmpRawComparator`.

Control flow: `BytesComparator` delegates byte-range comparison to a supplied Hadoop `RawComparator`. `ScalarComparator` orders by `magnitude()` using long subtraction sign. `MemcmpRawComparator` delegates to `WritableComparator.compareBytes` and deliberately rejects object comparison.

State and persistence: comparator instances only; no durable state.

Dependencies and integration: `BCFile.Reader.getBlockIndexNear()` uses scalar comparison with `Utils.lowerBound`; TFile key comparisons can use `BytesComparator`/`RawComparable`.

Risks: `ScalarComparator` computes `o1 - o2`, which can overflow for extreme longs. Tests should cover lower-bound ordering, raw byte lexicographic comparison, unsupported object comparison, and extreme scalar values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/CompareUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/Compression.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/Compression.java

Purpose: compression abstraction for TFile/BCFile, supporting LZO, GZ, and NONE plus codec pooling and block-flush behavior.

Important APIs/types/functions: enum `Algorithm`; `FinishOnFlushCompressionStream`; algorithm methods `isSupported()`, `getCodec()`, `createCompressionStream()`, `createDecompressionStream()`, `getCompressor()`, `returnCompressor()`, `getDecompressor()`, `returnDecompressor()`, `getName()`; top-level `getCompressionAlgorithmByName()` and `getSupportedAlgorithms()`.

Control flow: LZO lazily loads a configurable codec class and buffers both compressor streams and decompressor streams. GZ uses `DefaultCodec` and adjusts file-buffer settings. NONE returns buffered or raw streams. Pooled compressors/decompressors are reset when acquired and returned to `CodecPool` after use. `FinishOnFlushCompressionStream.flush()` finishes, flushes, and resets compression state to support block boundaries.

State and persistence: enum instances cache codec/loading state and share a static `Configuration`. BCFile persists algorithm names in indexes.

Dependencies and integration: used by `BCFile` block writer/reader; depends on Hadoop compression codecs, `CodecPool`, `ReflectionUtils`, and TFile constants.

Risks: static configuration and LZO lazy state can affect tests; LZO availability is environment-dependent. Tests should cover algorithm name resolution, supported algorithm listing, NONE passthrough, GZ round trip, LZO missing-class failures, compressor return on exceptions, and finish-on-flush block separation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/Compression.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/MetaBlockAlreadyExists.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/MetaBlockAlreadyExists.java

Purpose: checked exception indicating an attempt to create a duplicate named BCFile/TFile meta block.

Important APIs/types/functions: class extends `IOException`; package-private constructor accepting a message.

Control flow: `BCFile.Writer.prepareMetaBlock()` throws it when `MetaIndex` already has the requested name.

State and persistence: exception instance only.

Dependencies and integration: public stable API class in `org.apache.hadoop.io.file.tfile`, but construction is package-private, so TFile/BCFile code controls emission.

Risks: callers can catch the public type but cannot construct it directly. Tests should verify duplicate meta block creation throws this subtype and leaves writer state consistent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/MetaBlockAlreadyExists.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/MetaBlockDoesNotExist.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/MetaBlockDoesNotExist.java

Purpose: checked exception indicating a named meta block is absent.

Important APIs/types/functions: class extends `IOException`; package-private constructor accepting a message.

Control flow: `BCFile.Reader.getMetaBlock()` throws it when `MetaIndex.getMetaByName()` returns null.

State and persistence: exception instance only.

Dependencies and integration: public stable API type for TFile/BCFile readers.

Risks: callers must distinguish absent optional metadata from file corruption or I/O failures. Tests should verify missing meta block lookup throws this subtype and that existing meta blocks open normally.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/MetaBlockDoesNotExist.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/RawComparable.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/RawComparable.java

Purpose: public evolving interface for objects that expose a byte-array range to a Hadoop `RawComparator`.

Important APIs/types/functions: `buffer()`, `offset()`, and `size()`.

Control flow: no implementation logic; adapters such as `ByteArray` provide backing data and range metadata, while external comparators define semantics.

State and persistence: interface only.

Dependencies and integration: used by `CompareUtils.BytesComparator` and TFile key/range comparison helpers.

Risks: implementors expose mutable backing buffers, and semantic compatibility depends on using the correct `RawComparator`. Tests should cover implementations with slices and ensure comparator consumers honor offset/size rather than whole arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/RawComparable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/SimpleBufferedOutputStream.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/SimpleBufferedOutputStream.java

Purpose: lightweight buffered output stream that borrows a caller-provided buffer and exposes current buffered byte count.

Important APIs/types/functions: constructor with downstream `OutputStream` and `byte[]`; `write(int)`, `write(byte[], int, int)`, `flush()`, and `size()`.

Control flow: single-byte writes flush when the buffer is full. Bulk writes larger than the buffer bypass buffering after flushing; smaller writes flush first if they do not fit, then copy into the borrowed buffer. `flush()` drains buffered bytes and flushes downstream. `size()` reports buffered bytes not yet written.

State and persistence: in-memory borrowed buffer and count; downstream receives persisted bytes only on flush/bypass.

Dependencies and integration: used by `BCFile.Writer.WBlockState` so compressed-size accounting can include `fsBufferedOutput.size()` before downstream flush.

Risks: no internal bounds checks beyond normal arraycopy behavior for bulk arguments; borrowed buffer must outlive the stream. Tests should cover buffered count, flush behavior, large-write bypass, boundary writes exactly filling the buffer, and downstream exception propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/file/tfile/SimpleBufferedOutputStream.java -->
