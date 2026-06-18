# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/io/erasurecode/rawcoder/util/RSUtil.java

Purpose: Reed-Solomon utility layer shared by Java RS coders, including matrix generation, GF table initialization, and table-driven data encoding.

Important APIs/types/functions: public `GF`, `PRIMITIVE_ROOT`; `getPrimitivePower()`, `initTables()`, `genCauchyMatrix()`, and `encodeData()` overloads for byte arrays and ByteBuffers.

Control flow: `genCauchyMatrix` writes identity data rows and Cauchy parity rows using `GF256.gfInv(i ^ j)`. `initTables` expands matrix coefficients into 32-byte multiplication tables. `encodeData` XOR-accumulates table-multiplied input bytes into outputs, processing eight bytes per loop then a tail.

State and persistence: static `GaloisField` singleton reference; all encode state is caller-provided.

Dependencies and integration: core for `RSRawEncoder`, `RSRawDecoder`, and legacy primitive-power helpers; uses `GF256`.

Risks: outputs must be zeroed by callers before `encodeData` because it XORs into existing bytes. Tests should cover Cauchy matrix layout, table initialization offsets, byte-array/ByteBuffer parity equivalence, data lengths not divisible by eight, and compatibility with native ISA-L results.
