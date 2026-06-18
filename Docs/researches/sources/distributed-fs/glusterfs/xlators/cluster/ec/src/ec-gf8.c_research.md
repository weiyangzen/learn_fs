# sources/distributed-fs/glusterfs/xlators/cluster/ec/src/ec-gf8.c

## Purpose

`ec-gf8.c` is the precomputed GF(2^8) multiplication-program table used by GlusterFS erasure coding. It contains no request handling logic and no callable arithmetic routines of its own; instead it defines one static `ec_gf_mul_t` descriptor for each byte coefficient `0x00` through `0xff`, then exports `ec_gf8_mul[]` as a 256-entry lookup table.

Each descriptor represents multiplication by a constant in the 8-bit Galois field as a compact sequence of register operations. The EC code generator consumes those sequences when building optimized encode/decode routines. This avoids deriving a multiplication circuit at runtime for every coefficient and gives the generator known bounds for temporary registers and operation count.

## Important APIs, Types, and Data

- `#include "ec-gf8.h"` brings in the exported table declaration and, through `ec-galois.h` and `ec-types.h`, the `ec_gf_mul_t` and `ec_gf_op_t` definitions.
- `static ec_gf_op_t ec_gf8_mul_XX_ops[]` defines the opcode program for multiplication by coefficient `0xXX`.
- `static ec_gf_mul_t ec_gf8_mul_XX` wraps each opcode program with a register count and output-register map.
- `ec_gf_mul_t *ec_gf8_mul[]` is the only exported object from this file. It is ordered by coefficient value and contains pointers from `&ec_gf8_mul_00` through `&ec_gf8_mul_FF`.

The shared type contract is defined outside this file in `ec-types.h`: `ec_gf_op_t` contains an opcode and three integer arguments, while `ec_gf_mul_t` contains `regs`, `map[EC_GF_MAX_REGS]`, and `ops`. The opcodes used here are `EC_GF_OP_COPY`, `EC_GF_OP_XOR2`, `EC_GF_OP_XOR3`, and `EC_GF_OP_END`; this file does not use `LOAD`, `STORE`, or `XORM` inside the precomputed multiplier programs.

Structural signals from the source:

- 256 `ec_gf8_mul_XX` descriptors.
- 256 `ec_gf8_mul_XX_ops[]` opcode arrays.
- 256 `EC_GF_OP_END` sentinel entries, one per opcode array.
- Opcode mix in this generated table is dominated by XOR: 1716 `XOR2`, 84 `XOR3`, and 68 `COPY` operation entries.
- `ec_gf8_mul_00` has zero live output registers and an empty program; `ec_gf8_mul_01` maps the eight input bit registers unchanged and also has an empty program.
- Most nontrivial descriptors use 8 to 10 registers, with occasional temporary registers above bit positions 0-7.

## Control Flow

The file itself has only static initialization, not executable control flow. Its effective control flow happens in consumers:

1. `ec_gf_prepare()` in `ec-galois.c` accepts only `bits == 8`, selects `ec_gf8_mul` as the multiplication table, creates the GF log/power tables, and records `gf->table = ec_gf8_mul`.
2. During preparation, `ec_gf_prepare()` walks each descriptor's `ops` array until `EC_GF_OP_END` to calculate `min_ops`, `max_ops`, and `avg_ops`; these bounds are later used to size code-builder buffers.
3. `ec_code_gf_mul()` in `ec-code.c` looks up `builder->code->gf->table[value]`, duplicates every opcode into the builder until the sentinel, then remaps the builder's register map through `mul->map`.
4. `ec_code_compile()` emits target operations by dispatching opcodes through the selected code generator's `copy`, `xor2`, and `xor3` callbacks.
5. Higher-level matrix setup in `ec-method.c` asks for GF(8) through `ec_gf_prepare(EC_GF_BITS, EC_GF_MOD)`, then encode/decode paths use generated matrix code from `ec-code.c`.

Because `ec_gf8_mul[]` is a constant table, correctness depends on the array order and every descriptor's opcode/map pair matching the same coefficient.

## State and Persistence Behavior

All state in this file is process-static, initialized by the C loader, and read-only in normal operation. The arrays are not declared `const`, so the compiler cannot enforce immutability, but the EC code path treats them as immutable shared data. The file performs no allocation, locking, I/O, persistence, logging, or cleanup.

Persistent behavior is indirect: these descriptors determine the parity and reconstruction math used for stored erasure-coded file data. A bad table entry can cause durable parity corruption or failed reconstruction even though this file does not write data itself.

## Dependencies and Integration Points

Direct dependency:

- `ec-gf8.h`, which declares `ec_gf8_mul[]` and includes `ec-galois.h`.

Type and consumer dependencies:

- `ec-types.h` defines `ec_gf_opcode_t`, `ec_gf_op_t`, and `ec_gf_mul_t`.
- `ec-galois.c` imports the table into `ec_gf_t` for GF(8) contexts and derives operation-count statistics.
- `ec-code.c` turns descriptors into generated encode/decode code through `ec_code_gf_mul()` and `ec_code_compile()`.
- `ec-method.c` initializes the matrix subsystem with `ec_gf_prepare()` and uses generated matrix encoders/decoders.
- `ec-inode-write.c` and `ec-inode-read.c` reach this table indirectly through `ec_method_encode()` and `ec_method_decode()` for write parity generation and read reconstruction.

The table assumes the GF(8) modulus behavior used by `ec_gf_prepare()`, which defaults to `0x11d` when no modulus is specified. Any regeneration or replacement must match the same field definition and coefficient ordering expected by `ec-method.c` matrix construction.

## Risks and Edge Cases

- The source is generated-looking data with no local validation. A single wrong opcode, map entry, register count, or table-order slot can silently corrupt erasure-coded parity or decode output.
- The exported table has no explicit compile-time size. Consumers index it by GF value; missing, duplicated, or reordered entries would become runtime memory or correctness failures.
- Descriptor arrays are mutable C globals despite being intended as constants. Accidental writes from nearby code would affect all GF contexts in the process.
- Register counts must cover every map and opcode argument used by the descriptor. If `regs` is too small relative to temporary registers, `ec_code_gf_mul()` can copy too little mapping state after replaying the opcode list.
- The operation programs must be sentinel-terminated. `ec_gf_prepare()` and `ec_code_gf_mul()` both rely on `EC_GF_OP_END` to stop scanning.
- Field-parameter drift is high risk. The table is only valid for the GF(2^8) arithmetic model it was generated for; changing `EC_GF_MOD`, the default modulus, or the generator's bit ordering without regenerating this table would break parity math.
- Because the file has no comments explaining generation provenance, maintainers must infer correctness from consumers and external tests rather than from an embedded generator reference.

## Test Signals

Strong test signals should check both table structure and arithmetic behavior:

- Compile/link tests must ensure `ec_gf8_mul[]` is defined exactly once and visible through `ec-gf8.h`.
- A structural test can assert 256 descriptors, non-null table slots for all coefficients, descriptor arrays ending in `EC_GF_OP_END`, and register counts covering all used registers.
- Arithmetic tests should replay each descriptor and compare multiplication by every coefficient against `ec_gf_mul()`/log-table multiplication for representative byte values, ideally exhaustive 256 x 256 validation.
- Integration tests should exercise `ec_method_encode()` and `ec_method_decode()` for multiple EC layouts, missing-fragment masks, and non-default matrix coefficients.
- Regression tests should include read/write/reconstruct cases through GlusterFS EC translator paths, because this table affects durable data correctness rather than just a local helper result.

I did not find a colocated unit test for this exact table during this worker pass. Existing GlusterFS EC integration tests, if present elsewhere in the tree, are the likely practical signal; a focused arithmetic replay test would reduce risk for any future regeneration.
