# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/ByteArrayDecodingState.java

Purpose: package-private decode-call state for byte-array raw erasure decoding. It records `RawErasureDecoder`, `inputs`, `inputOffsets`, `erasedIndexes`, `outputs`, `outputOffsets`, and `decodeLength`, allowing implementations to work with offset-aware `byte[][]` without revalidating call shape.

Important APIs/types/functions: constructors for public byte-array decode calls and converted heap `ByteBuffer` calls; `convertToByteBufferState()` for native/direct coders; `checkInputBuffers()` and `checkOutputBuffers()` for length/null/recoverability validation.

Control flow: the main constructor finds the first non-null input, sets `decodeLength` from its full array length, checks MDS-style parameters via `DecodingState`, accepts null inputs as erased/not-read positions, then requires at least `numDataUnits` valid inputs. Converted states preserve caller offsets and skip validation because the source `ByteBufferDecodingState` already validated logical ranges.

State and persistence: per-call only; no durable state. Offsets are significant because array-backed `ByteBuffer` decode passes can target slices.

Dependencies and integration: used by `RawErasureDecoder.decode(byte[][], ...)`, Java coders, and native adapters that convert arrays to direct buffers.

Risks: the direct public constructor assumes whole arrays and cannot express non-zero offsets; invalid null outputs throw immediately. Test signals should cover insufficient valid inputs, erased/output length mismatch, conversion offset correctness, and mixed null input scenarios.
