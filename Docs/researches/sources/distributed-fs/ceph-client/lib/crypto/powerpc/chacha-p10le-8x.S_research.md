# sources/distributed-fs/ceph-client/lib/crypto/powerpc/chacha-p10le-8x.S

## Purpose
Implements a Power10 little-endian VSX/vector accelerated ChaCha20 transform that processes 4 or 8 blocks in parallel for the PowerPC ChaCha arch hook.

## Important APIs, Types, and Functions
Exports `SYM_FUNC_START(chacha_p10le_8x)`. Internal macros include `SAVE_REGS`, `RESTORE_REGS`, `QT_loop_8x`, `QT_loop_4x`, `TP_4x`, `Add_state`, and `Write_256`. Local data symbol `PERMX` supplies permutation constants used by rotate/permutation operations.

## Control Flow
The function returns immediately for nonpositive length. Otherwise it saves a large GPR/vector/VSX register frame, loads the ChaCha constants, key, counter, nonce, and permutation constants, and sets the double-round count from `nrounds / 2`. For input of at least 512 bytes, `Loop_8x` performs two 4-block lanes per iteration. Smaller remaining chunks use `Loop_4x`. Each loop broadcasts state words to vectors, adds per-block counters, runs repeated quarter-round macros, transposes the vector layout, adds the original state, xors with input, writes 256-byte chunks, advances offsets, and updates counter vectors.

## State and Persistence
The assembly writes ciphertext/plaintext to `dst` and does not itself store the updated counter back to the C `chacha_state`; the header wrapper increments `state->x[12]` by processed full blocks after the assembly call. Callee-saved registers and vector state are restored from the stack.

## Dependencies and Integration Points
Included through `chacha.h` on Power10 little-endian systems. It depends on Power10/VSX instructions including `vpermxor`, vector rotates, and unaligned vector load/store patterns. The C wrapper manages `enable_kernel_vsx()` and limits calls to full 256-byte multiples.

## Risks
The split between assembly processing and C-side counter update is a key integration risk. Lengths passed to this function must be block-aligned and chunked as the wrapper expects. The save frame is large and ABI-sensitive. This file is little-endian specific.

## Test Signals
ChaCha20 known-answer tests should cover lengths just over one block, 256-byte multiples, 512-byte multiples, and residual bytes handled by the generic fallback. Tests should assert final `state->x[12]` after mixed accelerated/generic chunks.
