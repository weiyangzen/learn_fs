<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/csum.c -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/csum.c

## Purpose
`csum.c` implements RISC-V Internet checksum helpers, including optimized IPv6 pseudo-header checksum on 64-bit and the generic `do_csum()` buffer checksum.

## Important APIs, Types, And Functions
`csum_ipv6_magic()` is exported on non-RV32. `do_csum_common()` accumulates word-sized data and carry. `do_csum_with_alignment()` handles misaligned buffers using controlled over-reads and KASAN checks. `do_csum_no_alignment()` is used for aligned or fast-misaligned systems. `do_csum()` chooses the path.

## Control Flow
The code performs word-sized additions, folds carry, masks over-read bytes at head/tail, and folds to 16 bits. When Zbb and toolchain support are present, inline assembly uses bit-manipulation instructions for rotation, byte reversal, and faster folding.

## State And Persistence
No state is retained. It reads packet memory and returns checksum values.

## Dependencies And Integration Points
It depends on KASAN read checking, RISC-V feature static keys, endian configuration, network checksum types, and optional Zbb toolchain support.

## Risks
The alignment path intentionally over-reads within aligned words; KASAN checks and same-page/cache-line assumptions are important. Endian and offset folding must preserve Internet checksum semantics. Inline asm variants must match C fallback results.

## Test Signals
Network checksum selftests, IPv6 traffic tests, KASAN builds, misaligned buffer tests, RV32/RV64 builds, and Zbb vs non-Zbb comparison tests are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/csum.c -->
