<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/twofish.h -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/twofish.h

Purpose: This header declares x86 Twofish assembly entry points shared by base, 3-way, and AVX glue files.

Important APIs/types/functions: It declares `twofish_enc_blk` and `twofish_dec_blk` for single-block assembly, `__twofish_enc_blk_3way` and `twofish_dec_blk_3way` for 3-way parallel assembly, and `twofish_dec_blk_cbc_3way` as a C helper exported by the 3-way glue. It includes `crypto/twofish.h` and `crypto/b128ops.h`.

Control flow: There is no runtime control flow. Consumers include the header to call the appropriate block function and to compose fallback chains.

State and persistence: The header owns no state and exposes caller-owned context/buffer APIs.

Dependencies and integration points: It ties `twofish_glue.c`, `twofish_glue_3way.c`, `twofish_avx_glue.c`, and their assembly files together. The declarations must match both i386 and x86-64 assembly symbol ABIs where applicable.

Risks and test signals: Prototype mismatches can corrupt registers or stack state. Build tests with all x86 Twofish variants enabled and Crypto API vector tests through each driver are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/twofish.h -->
