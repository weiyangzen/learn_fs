<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/glue_helper-asm-avx.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/glue_helper-asm-avx.S

Purpose: This small include file defines common XMM load/store helper macros for 8-way AVX block-cipher assembly wrappers. It keeps ECB and CBC I/O packing consistent across CAST6, Serpent, and Twofish AVX implementations.

Important APIs/types/functions: `load_8way(src, x0..x7)` loads eight 16-byte blocks from consecutive memory into XMM registers. `store_8way(dst, x0..x7)` stores eight XMM registers back to consecutive output blocks. `store_cbc_8way(src, dst, x0..x7)` XORs decrypted blocks with the previous CBC chain using ciphertext from `src`, then stores the resulting plaintext.

Control flow: Consumer assembly calls `load_8way`, runs its cipher core, and then calls either `store_8way` for ECB or `store_cbc_8way` for CBC decrypt. The CBC helper XORs block zero with the caller's current IV already carried in the first loaded chain register convention and subsequent blocks with previous ciphertext from memory.

State and persistence: The macros have no persistent state. They operate on caller-selected vector registers and memory pointers. Their effects are the loads from `src` and stores to `dst`.

Dependencies and integration points: The include is pulled into x86-64 AVX assembly files after register conventions are defined. It depends on 16-byte block ciphers and on callers arranging decrypted block registers in the order expected by the store macro.

Risks and test signals: A register-order mismatch in a consumer silently corrupts ECB output or CBC chaining. In-place CBC requires source memory still contain ciphertext when the store helper reads previous blocks. Tests should include exact 8-block ECB/CBC vectors, in-place CBC decrypt, and inspection of all users after register convention changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/glue_helper-asm-avx.S -->
