<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/twofish-x86_64-asm_64-3way.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/twofish-x86_64-asm_64-3way.S

Purpose: This x86-64 assembly file implements 3-way parallel Twofish encryption and decryption using general-purpose 64-bit registers. It improves throughput on out-of-order CPUs without requiring SIMD.

Important APIs/types/functions: Public symbols are `__twofish_enc_blk_3way` and `twofish_dec_blk_3way`. The encryption function accepts an XOR flag used by wrapper code. Macros include `do16bit_ror`, `swap_ab_with_cd`, `g1g2_3`, `encrypt_round3`, `decrypt_round3`, `encrypt_cycle3`, `decrypt_cycle3`, `inpack3`, `outunpack3`, `inpack_enc3`, `outunpack_enc3`, `inpack_dec3`, and `outunpack_dec3`.

Control flow: The encryption entry packs three input blocks into register pairs, applies whitening and eight round cycles, and writes or XORs output depending on the flag. Decryption packs ciphertext, runs inverse cycles, and writes plaintext. Stack slots hold parts of the third block while registers are reused for table lookups and round arithmetic.

State and persistence: The file has no global state. It reads the caller's Twofish context and mutates only destination buffers. It saves/restores callee-saved registers as required by the x86-64 ABI.

Dependencies and integration points: It includes linkage and CFI type headers. `twofish_glue_3way.c` exports the symbols, registers skcipher modes, and decides whether to disable the module on CPUs where this implementation is slower.

Risks and test signals: The performance benefit is CPU-dependent, and the glue blacklists Atom/Pentium 4 unless forced. Correctness risks include packed register ordering, XOR-output mode, and table offsets. Tests should include 3-block ECB vectors, CBC decrypt through the C helper, forced and blacklisted module load paths, and comparison against single-block Twofish.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/twofish-x86_64-asm_64-3way.S -->
