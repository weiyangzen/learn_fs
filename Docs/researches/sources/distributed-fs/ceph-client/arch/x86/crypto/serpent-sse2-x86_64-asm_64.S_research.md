<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-sse2-x86_64-asm_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-sse2-x86_64-asm_64.S

Purpose: This x86-64 assembly file implements the SSE2 Serpent 8-way block routines used when AVX is not required or not selected. It is structurally similar to the AVX implementation but uses SSE2-compatible XMM instructions and the x86-64 calling convention.

Important APIs/types/functions: Public symbols are `__serpent_enc_blk_8way` and `serpent_dec_blk_8way`. The encryption entry accepts a `bool xor` parameter for normal output or XOR output. The file defines two-lane S-box macros (`S0_1`/`S0_2`, etc.), inverse macros, `K2`, `LK2`, `KL2`, `SP`, `transpose_4x4`, `read_blocks`, `write_blocks`, and `xor_blocks`.

Control flow: Eight input blocks are arranged as two four-block groups in XMM registers. Encryption runs key mixing and 32 Serpent rounds, then either writes the generated ciphertext or XORs it into the destination depending on the flag. Decryption applies the inverse round schedule and writes plaintext. The C glue's CBC helper handles chaining after decryption.

State and persistence: It has no persistent state and reads only the caller-provided Serpent key schedule. It mutates destination buffers and uses XMM registers under the caller's FPU ownership.

Dependencies and integration points: It includes `linux/linkage.h`; `serpent-sse2.h` declares its ABI for non-32-bit builds. `serpent_sse2_glue.c` registers the Crypto API algorithms and checks `X86_FEATURE_XMM2`.

Risks and test signals: Register ordering differs between encrypted and decrypted outputs, so the write macros must match the C wrapper expectation. Build and runtime tests should include x86-64 SSE2-only module loading, 8-block Serpent known-answer vectors, CBC in-place decrypt, XOR path coverage from any XTS/LRW-style users, and comparison with generic Serpent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-sse2-x86_64-asm_64.S -->
