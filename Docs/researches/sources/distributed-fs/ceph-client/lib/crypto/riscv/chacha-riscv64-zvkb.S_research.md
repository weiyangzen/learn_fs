# sources/distributed-fs/ceph-client/lib/crypto/riscv/chacha-riscv64-zvkb.S

## Purpose
Implements RISC-V vector ChaCha encryption/decryption using the Zvkb vector crypto bit-manipulation extension.

## Important APIs, Types, and Functions
Exports `chacha_zvkb(struct chacha_state *state, const u8 *in, u8 *out, size_t nblocks, int nrounds)`. Macro `chacha_round` implements one quarter-round pattern over four vectorized columns/diagonals.

## Control Flow
The function saves callee-saved scalar registers, loads the 16-word ChaCha state into scalar registers, then loops while blocks remain. Each iteration sets `vl` to the number of blocks the vector unit can handle, broadcasts constants/key/nonce into vector registers, creates per-lane counters with `vid.v`, loads input with strided segment loads, runs double-rounds until `nrounds` is consumed, adds the original state, xors with input, stores output with strided segment stores, advances pointers and block count, and repeats. It writes the updated counter back to `state->x[12]`.

## State and Persistence
The input/output buffers are transformed in place or out of place according to caller pointers. The ChaCha counter in the state is persisted after all full blocks. Saved registers are restored before return.

## Dependencies and Integration Points
Requires RV64I, V with VLEN at least 128, and Zvkb. Called by `riscv/chacha.h`, which handles vector begin/end and tail buffering.

## Risks
The function requires `nblocks` to be nonzero and whole-block based. Counter overflow behavior follows a 32-bit `state->x[12]` convention. Strided segment loads/stores rely on correct vector length and block layout.

## Test Signals
ChaCha20 known-answer tests for multiple block counts and non-default round counts. Header-level tests should verify tail handling and final counter values.
