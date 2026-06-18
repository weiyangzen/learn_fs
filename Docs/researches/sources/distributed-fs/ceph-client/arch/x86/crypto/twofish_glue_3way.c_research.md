<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/twofish_glue_3way.c -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/twofish_glue_3way.c

Purpose: This file registers 3-way parallel Twofish ECB and CBC skcipher drivers and exports the 3-way block routines for AVX fallback chains. It includes CPU blacklist logic to avoid slower implementations on in-order or rotate-slow processors.

Important APIs/types/functions: It exports `__twofish_enc_blk_3way`, `twofish_dec_blk_3way`, and `twofish_dec_blk_cbc_3way`. `twofish_dec_blk_cbc_3way()` preserves previous ciphertext for in-place CBC decrypt and XORs blocks after 3-way decryption. `tf_skciphers[]` registers `ecb-twofish-3way` and `cbc-twofish-3way` with priority 300. `is_blacklisted_cpu()` checks Intel Atom Bonnell/Saltwell and Pentium 4 families. The `force` module parameter bypasses the blacklist.

Control flow: Init refuses registration if the CPU is blacklisted and `force` is unset. ECB handlers process 3-block chunks with 3-way routines and one-block tails with base assembly. CBC encrypt is scalar. CBC decrypt uses the CBC 3-way helper then scalar tails. Exit unregisters the skcipher table.

State and persistence: Persistent state includes the static `force` module parameter and registered algorithms. Per-transform state is `struct twofish_ctx`; request state is held by `skcipher_walk`.

Dependencies and integration points: It depends on x86 CPU identification, generic Twofish, the base single-block assembly symbols, the 3-way assembly file, and shared ECB/CBC helpers. It is both a standalone skcipher provider and a dependency for `twofish_avx_glue.c`.

Risks and test signals: CPU blacklist accuracy affects performance and algorithm availability. In-place CBC decrypt relies on a two-block buffer before overwriting. Tests should cover blacklist and `force` behavior, 3-block and tail vectors, module export resolution, and comparison against the base Twofish cipher.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/twofish_glue_3way.c -->
