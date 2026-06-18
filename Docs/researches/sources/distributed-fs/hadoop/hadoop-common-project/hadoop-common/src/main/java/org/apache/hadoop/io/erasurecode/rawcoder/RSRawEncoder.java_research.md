# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/RSRawEncoder.java

Purpose: modern pure-Java Reed-Solomon encoder compatible with ISA-L/native RS coder semantics.

Important APIs/types/functions: schema-scoped `encodeMatrix` and `gfTables`; constructor matrix/table generation; `doEncode()` overloads.

Control flow: construction validates total units are below GF(256) field size, builds a Cauchy matrix with identity data rows and parity rows, optionally dumps the matrix/tables, and initializes GF multiplication tables for parity rows. Encoding zeroes outputs then runs `RSUtil.encodeData()` over all data inputs into parity outputs.

State and persistence: encode matrix and precomputed GF tables persist for encoder lifetime; no durable state.

Dependencies and integration: extends `RawErasureEncoder`; uses `RSUtil`, `GF256` indirectly, `DumpUtil`, `CoderUtil`, and `ErasureCoderOptions`; produced by `RSRawErasureCoderFactory`.

Risks: output buffers must be reset before XOR-accumulating table products, which this class does explicitly. Tests should cover field-size boundary rejection, direct/heap parity equality, non-8-byte data lengths in `RSUtil.encodeData`, verbose dump mode, and native compatibility.
