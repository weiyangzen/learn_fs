<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/memcpy.S -->
# sources/distributed-fs/ceph-client/arch/riscv/lib/memcpy.S

## Purpose
`memcpy.S` implements RISC-V `memcpy` and early-boot aliases for non-overlapping memory copies.

## Important APIs, Types, And Functions
`__memcpy` is the main symbol, with weak `memcpy` and `__pi_memcpy` aliases. It uses byte copying for small or poorly aligned cases and unrolled word copying for co-aligned large buffers.

## Control Flow
The function preserves the destination return value, rejects word copy for sizes under 128 or mismatched low alignment, byte-copies to alignment, runs a 16*SZREG unrolled load/store loop, and finishes with word or byte tail copying.

## State And Persistence
It writes `n` bytes to destination and keeps no state.

## Dependencies And Integration Points
It uses RISC-V ABI register conventions and `SZREG` macros. It is used throughout the kernel, including position-independent early code through aliases.

## Risks
`memcpy` does not handle overlap; callers needing overlap must use `memmove`. Alignment and tail handling must preserve return value in `a0`. Early boot aliases require this code to remain relocation-safe.

## Test Signals
lib/string tests, boot smoke tests, KASAN-excluded build variants, and randomized alignment/size memcpy tests are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/lib/memcpy.S -->
