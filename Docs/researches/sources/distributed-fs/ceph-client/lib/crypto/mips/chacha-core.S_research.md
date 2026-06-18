# sources/distributed-fs/ceph-client/lib/crypto/mips/chacha-core.S

## Purpose
Provides MIPS assembly implementations of ChaCha stream encryption and HChaCha block derivation.

## Important APIs, Types, and Functions
- Defines global `chacha_crypt_arch(struct chacha_state *state, u8 *dst, const u8 *src, unsigned int bytes, int nrounds)`.
- Defines global `hchacha_block_arch(const struct chacha_state *state, u32 out[HCHACHA_OUT_WORDS], int nrounds)`.
- Uses register macros for ChaCha words `X0`-`X15`, temporary registers, input registers, and `AXR()` quarter-round groups.
- Provides aligned and unaligned store paths plus jump-table entries for final partial words.

## Control Flow and State
`chacha_crypt_arch()` returns immediately for zero bytes, saves callee-saved registers, loads counter word 12 into `NONCE_0`, and loops over 64-byte blocks. Each loop loads the state, executes `nrounds` in two-round steps, adds original state words, endian-converts on big-endian builds, XORs with input, writes output, and increments the counter. Tail handling uses aligned/unaligned jump tables for complete words and byte-by-byte logic for the final one to three bytes. The final counter is written back to the state. `hchacha_block_arch()` runs the same round structure and writes the HChaCha output words.

## Dependencies and Integration Points
Declared by `mips/chacha.h` and selected as an architecture implementation by the generic ChaCha library. It depends on MIPS assembler semantics, `wsbh`/`rotr` availability for endian conversion, and ABI-preserved register rules.

## Risks and Test Signals
Risks include counter writeback errors, final-byte jump-table mistakes, big-endian conversion differences, and ABI register clobbering. Tests should compare aligned and unaligned buffers, in-place encryption, all tail lengths 0-63, multiple `nrounds` values used by the library, HChaCha known vectors, counter wrap behavior expected by callers, and generic-vs-MIPS output.
