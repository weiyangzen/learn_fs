# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RSRawDecoder.java

Purpose: modern pure-Java Reed-Solomon decoder compatible with ISA-L/native RS behavior.

Important APIs/types/functions: `encodeMatrix`; cached `decodeMatrix`, `invertMatrix`, `gfTables`, `cachedErasedIndexes`, `validIndexes`, `erasureFlags`; `doDecode()` overloads; `prepareDecoding()`; `processErasures()`; `generateDecodeMatrix()`.

Control flow: construction builds a Cauchy encode matrix and checks total units fit GF(256). Decode zeroes outputs, prepares/reuses decode tables keyed by erased indexes and valid indexes, selects the first `numDataUnits` valid inputs, then calls `RSUtil.encodeData()` with decode coefficients. Decode matrix generation inverts the selected valid rows and derives rows for erased data or parity units.

State and persistence: schema matrix and cached decode tables persist in the decoder instance; no durable state. Public decoder methods are synchronized in the base class, helping protect mutable cache fields.

Dependencies and integration: uses `GF256`, `RSUtil`, `DumpUtil`, `CoderUtil`, and raw decoding state classes; produced by `RSRawErasureCoderFactory`.

Risks: `GF256.gfInvertMatrix()` mutates its input temporary matrix and throws runtime errors for singular matrices. Cache correctness depends on valid-index comparison. Tests should cover multiple erasure patterns, parity erasures, cache reuse/invalidation, direct and heap buffers, verbose dump mode, and compatibility with native RS.
