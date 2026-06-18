# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/DecodingState.java

Purpose: base package-private state for decode operations, holding the decoder and common `decodeLength`, plus MDS-style parameter validation.

Important APIs/types/functions: fields `decoder` and `decodeLength`; generic `checkParameters(T[] inputs, int[] erasedIndexes, T[] outputs)`.

Control flow: validation requires the input array length to equal data plus parity units, output count to equal erased-index count, and erased count to be no more than parity units. Buffer-specific subclasses then enforce lengths, null rules, and valid-input count.

State and persistence: per-call in-memory only.

Dependencies and integration: subclassed by `ByteBufferDecodingState` and `ByteArrayDecodingState`; enforces assumptions used by RS, XOR, native, and dummy decoders.

Risks: this assumes an MDS recovery model; non-MDS codes must override or avoid this validation. The first invalid input-length branch throws plain `IllegalArgumentException` while later checks throw `HadoopIllegalArgumentException`, which matters for tests expecting exception types. Test signals should exercise too many erasures, erased/output mismatch, wrong all-unit length, and subclass-specific recovery failures.
