# sources/distributed-fs/ceph-client/arch/powerpc/kernel/vdso/vgetrandom-chacha.S

## Purpose
Implements a stack-conscious PowerPC ChaCha20 block generator for the vDSO getrandom path.

## Important APIs, Types, And Functions
Exports `__arch_chacha20_blocks_nostack(dst_bytes, key, counter, nblocks)`. It defines register aliases for the key, counter, and 16-word state, plus `quarterround4` and `QUARTERROUND4` macros that perform four ChaCha quarter rounds in parallel.

## Control Flow
The function saves callee-saved registers, loads the 256-bit key and 64-bit counter, then for each 64-byte block initializes constants/key/counter/zero nonce, runs 10 double-round iterations, adds the original state, writes little-endian output (using byte-reversed stores on big-endian), increments the 64-bit counter, and loops. At the end it writes back the updated counter, clears key registers `r6-r12`, restores saved registers, and returns.

## State And Persistence
Mutates caller-provided output and counter memory. It has no static state. On 64-bit it saves registers below `r1` without moving the stack pointer, while 32-bit uses a small stack frame.

## Dependencies And Integration Points
Used by the generic vDSO getrandom implementation included by `vgetrandom.c`. Depends on PowerPC integer rotate/add/xor instructions, endian handling, and ABI register preservation.

## Risks And Edge Cases
The routine assumes a positive block count and valid pointers supplied by higher-level code. Register save/restore and 64-bit below-stack usage are ABI-sensitive. Key material clearing covers volatile key registers but does not erase output or caller state. Big-endian byte order must match ChaCha's little-endian block format.

## Test Signals
Known-answer ChaCha20 tests for 32-bit/64-bit and big/little endian, getrandom vDSO tests, KASAN/objtool-style checks where available, and stress tests around counter carry and multi-block output are valuable.
