# sources/distributed-fs/ceph-client/arch/x86/crypto/blowfish-x86_64-asm_64.S

Purpose: Implements x86_64 assembly Blowfish single-block encryption/decryption and 4-block parallel encryption/decryption used by the Blowfish glue module.

Important APIs/functions: exported symbols are `blowfish_enc_blk`, `blowfish_dec_blk`, `blowfish_enc_blk_4way`, and `__blowfish_dec_blk_4way`. Macros define the context layout (`p`, `s0`-`s3`), Blowfish F-function table lookups, endian block packing, and 4-way round-key preloading.

Control flow: single-block functions load an 8-byte block, transform endian/layout, run 16 Feistel rounds through `round_enc` or `round_dec`, apply final P-array whitening, and write the block. The 4-way encryption path loads four blocks, preloads round keys, applies the F-function across four independent registers per round, then writes four blocks. The 4-way decrypt routine accepts a `cbc` flag; after decryption it optionally XORs with previous ciphertext blocks before output.

State and persistence: all persistent state is in `struct bf_ctx`, specifically P-array and S-box tables prepared by generic Blowfish key setup. This assembly mutates only caller-provided output and register temporaries. The CBC 4-way path reads the source ciphertext as chaining input.

Dependencies and integration points: called by `blowfish_glue.c` through the crypto cipher and skcipher APIs. Depends on exact `struct bf_ctx` table layout from `crypto/blowfish.h` and Linux `SYM_FUNC` linkage macros.

Risks: register preservation is manual, including `%r12` and `%rbx`; mistakes can corrupt callers. CBC decryption relies on source blocks still being available for XOR. Endian conversion and 64-bit rotates are performance-sensitive and are why the glue blacklists Pentium 4 by default.

Test signals: use Blowfish known-answer tests for cipher, ECB, and CBC; test 1-, 4-, and non-multiple-of-4 block counts; in-place CBC decrypt; and module behavior with the `force` parameter on blacklisted CPUs.
