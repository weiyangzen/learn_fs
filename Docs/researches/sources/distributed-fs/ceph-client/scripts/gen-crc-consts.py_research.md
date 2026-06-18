# sources/distributed-fs/ceph-client/scripts/gen-crc-consts.py

## Purpose
`gen-crc-consts.py` emits C constants and tables for CRC variants, including slice-by-N tables, RISC-V carryless multiplication constants, and x86 PCLMUL folding constants.

## Important APIs, Types, and Functions
Polynomial helpers include `xor()`, `clmul()`, `div()`, `reduce()`, `bitreflect()`, and `fmt_poly()`. `CrcVariant` normalizes CRC width, polynomial, and bit order. Generators are `gen_slicebyN_tables()`, `gen_riscv_clmul_consts()`, and `gen_x86_pclmul_consts()`.

## Control Flow
The script expects two arguments: comma-separated constant types and comma-separated CRC variants like `crc32_lsb_0xedb88320`. It prints a generated-file header, parses variants, then dispatches each requested constant type to the matching generator.

## State and Persistence Behavior
It is a pure stdout generator with no file writes. All state is local polynomial arithmetic and generated text.

## Dependencies and Integration Points
It is intended for kernel build-time generation of CRC implementation data. Consumers compile the emitted C declarations into architecture-specific CRC code.

## Risks and Test Signals
The math is bit-order sensitive; wrong reflection or omitted high polynomial term produces silent incorrect CRCs. Argument validation uses assertions and exceptions rather than friendly diagnostics. Test generated constants against known CRC test vectors for each variant and against independent table/folding implementations.
