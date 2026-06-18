<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/twofish-x86_64-asm_64.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/twofish-x86_64-asm_64.S

Purpose: This x86-64 assembly file implements the base single-block Twofish encryption and decryption routines for the `twofish-asm` cipher driver.

Important APIs/types/functions: Public typed symbols are `twofish_enc_blk` and `twofish_dec_blk`. Macros define context offsets for S-box tables, whitening keys, and round keys, plus `input_whitening`, `output_whitening`, `encrypt_round`, `encrypt_last_round`, `decrypt_round`, and `decrypt_last_round`.

Control flow: Encryption loads the four 32-bit block words, XORs input whitening keys, executes Twofish's round structure with precomputed table lookups and key additions, applies output whitening, and stores output. Decryption reverses the process with decryption round macros and reversed whitening use.

State and persistence: The routines are stateless beyond the caller-owned `struct twofish_ctx`. They use general-purpose registers and preserve callee-saved state needed by the ABI.

Dependencies and integration points: It includes `linux/linkage.h`, CFI type metadata, and `asm/asm-offsets.h`. `twofish_glue.c` registers and exports these routines; 3-way and AVX modules use them as scalar fallbacks.

Risks and test signals: Context layout offsets must match `crypto/twofish.h`. Endianness and table lookup byte selection are correctness-sensitive. Tests should include all official Twofish key sizes, fallback paths from AVX/3-way glue, unaligned buffers, and CFI/objtool validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/twofish-x86_64-asm_64.S -->
