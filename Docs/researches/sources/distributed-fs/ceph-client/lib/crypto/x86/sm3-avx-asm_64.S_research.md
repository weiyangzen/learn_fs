# sources/distributed-fs/ceph-client/lib/crypto/x86/sm3-avx-asm_64.S

## Purpose
Implements the x86-64 AVX/BMI2 accelerated SM3 compression transform for the kernel crypto SM3 implementation.

## APIs, Types, and Functions
The exported symbol is `sm3_transform_avx`, with C ABI `void sm3_transform_avx(struct sm3_block_state *state, const u8 *data, size_t nblocks)`. The file defines state offsets for eight 32-bit chaining words, all 64 rotated SM3 round constants, register aliases for GPR and XMM state, and a stack layout for expanded words and saved registers. Macros implement rotates, additions, `FF1`/`GG1`, `FF2`/`GG2`, round execution, input byte-swapping, and three-word-at-a-time schedule expansion.

## Control Flow
The transform zeroes upper vector state, saves the frame and callee-saved registers, loads the eight 32-bit chaining variables, and enters a per-block loop. It reads a 64-byte input block, byte-swaps words to host order, computes `W` and `W1 ^ W2` schedule data in XMM registers and stack slots, and unrolls all 64 SM3 rounds. Rounds 0-15 use the XOR-style boolean functions and rounds 16-63 use the majority/choose-style functions. At block end the working variables are XORed into the original state words, `nblocks` is decremented, and the loop repeats. It clears vector registers and restores saved GPRs before returning.

## State and Persistence
The caller-owned `struct sm3_block_state` is updated in place. All schedule and temporary state is local to registers and the stack. The byte-swap mask is read-only data. There is no global mutable state or allocation.

## Dependencies and Integration Points
The assembly depends on AVX, BMI2-style `rorx` helpers, x86-64 ABI conventions, `<asm/frame.h>`, and `<linux/linkage.h>`. `sm3.h` wraps this symbol in FPU protection and selects it with a static call when AVX, BMI2, and YMM xfeatures are available.

## Risks and Test Signals
Risks include round-constant or schedule mistakes, endianness errors, incomplete vector-state cleanup, callee-saved register corruption, and invoking the transform without usable kernel FPU state. Test signals include SM3 known-answer tests, generic-vs-AVX comparisons for multi-block messages, boot tests on AVX/BMI2 and fallback systems, objtool/unwind validation, and stress tests around preemption or interrupt contexts that should trigger generic fallback.
