# sources/distributed-fs/ceph-client/lib/crypto/arm/chacha-scalar-core.S

## Purpose
This ARM scalar assembly file implements ChaCha encryption/XOR and HChaCha without NEON, optimized around ARM register constraints.

## Important APIs, Types, and Functions
It defines `ENTRY(chacha_doarm)` and `ENTRY(hchacha_block_arm)`. Core macros include `_halfround`, `_doubleround`, `_chacha_permute`, and `_chacha`.

## Control Flow
`chacha_doarm()` loads the 16-word state and chooses 12 or 20 rounds. `_chacha` permutes the state, adds the original state, XORs a full aligned 64-byte block quickly when possible, otherwise generates a keystream block on the stack and XORs the required bytes. It increments the block counter and loops. `hchacha_block_arm()` runs the permutation and stores x0-x3 and x12-x15.

## State and Persistence
The function consumes caller-provided state and output/input pointers. It does not mutate the original state directly; the C wrapper updates `state->x[12]`. Temporary state is in registers and stack.

## Dependencies and Integration Points
It depends on ARM assembler helpers and is always part of ARM `libchacha` arch support. `arm/chacha.h` uses it as fallback and for small messages.

## Risks and Test Signals
Risks include stack layout complexity, alignment slow-path correctness, counter overflow conventions, 12-round selection, and big-endian byte swaps. ChaCha20, ChaCha12, HChaCha, XChaCha, partial-block, and unaligned-buffer tests are key.
