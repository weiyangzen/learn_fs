# sources/distributed-fs/ceph-client/lib/crypto/x86/sha512-avx2-asm.S

## Purpose
Provides the x86-64 AVX2/BMI2 SHA-512 compression transform used by the kernel crypto SHA-512 implementation. Despite the `avx2` filename, the exported symbol is `sha512_transform_rorx`, selected by x86 SHA-512 glue when AVX2, BMI2, and usable YMM state are available.

## APIs, Types, and Functions
The only externally visible API is `SYM_FUNC_START(sha512_transform_rorx)`, with the C ABI `void sha512_transform_rorx(struct sha512_block_state *state, const u8 *data, size_t nblocks)`. It includes `<linux/linkage.h>`, uses the kernel symbol/return macros, and expects a SHA-512 block state of eight 64-bit chaining words. Internal assembly macros include `addm`, `COPY_YMM_AND_BSWAP`, `rotate_Ys`, `RotateState`, `MY_VPALIGNR`, `FOUR_ROUNDS_AND_SCHED`, and `DO_4ROUNDS`. Read-only data sections provide the standard 80-entry `K512` table, a byte-swap shuffle mask, and a YMM lane mask.

## Control Flow
The function saves callee-saved GPRs, aligns a stack frame, converts `nblocks` to an end pointer, and loads the eight chaining variables. For each 128-byte input block, it byte-swaps four YMM chunks into big-endian 64-bit words, then runs the SHA-512 schedule and rounds in groups of four. The first loop expands scheduled words while hashing; the second loop finishes the remaining rounds using already prepared schedule vectors. At block completion it adds the working variables back into the caller's state, advances by one block, and loops until the input pointer reaches the computed end. It finishes with `vzeroupper` before returning.

## State and Persistence
Persistent state is only the caller-owned SHA-512 block state updated in place. The message schedule, round-transfer buffer, saved context pointer, input pointer, and end pointer live on the stack. The constants are immutable rodata. There is no allocation, locking, or global mutable state.

## Dependencies and Integration Points
This file is used through `sha512.h`, which wraps the assembly call in `kernel_fpu_begin()`/`kernel_fpu_end()` and exposes it through a static call selected at module initialization. It depends on AVX2 vector instructions, BMI2 `rorx`, x86-64 calling conventions, YMM state support, and the SHA-512 generic fallback for contexts where FPU use is unsafe.

## Risks and Test Signals
Risks are concentrated in assembly correctness: stack alignment, preserving callee-saved registers, using `vzeroupper`, correct byte order, exact `K512` constants, and correct handling of `nblocks >= 1`. The wrapper must never call it when `irq_fpu_usable()` is false. Test signals include crypto manager SHA-512 vectors, comparison against `sha512_blocks_generic`, KASAN/objtool/unwind checks for the hand-written frame, boot tests on AVX2/BMI2 and non-AVX2 machines, and stress tests from interrupt-heavy or softirq contexts that force fallback paths.
