# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RSLegacyRawEncoder.java

Purpose: older pure-Java Reed-Solomon encoder using a generating polynomial and Galois-field remainder calculation.

Important APIs/types/functions: object field `generatingPolynomial`; constructor polynomial generation; `doEncode(ByteBufferEncodingState)`; `doEncode(ByteArrayEncodingState)`.

Control flow: construction computes primitive powers for all units and multiplies `(root + x)` factors to build the generating polynomial. Encoding zeroes parity outputs, builds an array ordered as parity units followed by data units, optionally copies input data when `allowChangeInputs()` is false, then invokes `RSUtil.GF.remainder()` to compute parity in-place.

State and persistence: generating polynomial is schema-scoped and object-persistent. No durable state.

Dependencies and integration: extends `RawErasureEncoder`, uses `RSUtil`, `GaloisField`, `CoderUtil`, and `ErasureCoderOptions`; created by `RSLegacyRawErasureCoderFactory`.

Risks: `assert` enforces field-size constraints only when assertions are enabled; modern RS uses explicit exceptions. When `allowChangeInputs()` is true the input buffers can be modified by `remainder()`. Tests should cover both allow-change settings, direct and heap paths, parity compatibility with legacy decoder, and field-size boundary handling.
