# sources/distributed-fs/ceph-client/arch/x86/crypto/aria-avx.h

Purpose: Shared header for x86 ARIA vector backends. It centralizes block-count constants, exported assembler prototypes, and the runtime dispatch table used by AVX, AVX2, and AVX512 glue files.

Important APIs/types/functions: defines `ARIA_AESNI_PARALLEL_BLOCKS`/`_SIZE` for 16-way AVX, `ARIA_AESNI_AVX2_PARALLEL_BLOCKS`/`_SIZE` for 32-way AVX2, and `ARIA_GFNI_AVX512_PARALLEL_BLOCKS`/`_SIZE` for 64-way AVX512. Declares all 16-way and 32-way AES-NI/GFNI assembler entry points. Defines `struct aria_avx_ops` with function pointers for 16/32/64-way encrypt, decrypt, and CTR operations.

Control flow: this file has no executable control flow. It shapes the dispatch flow in glue files: module init validates CPU features, fills `aria_avx_ops` with the best available implementation, and request handlers call through those pointers for bulk processing.

State and persistence: no runtime state is stored here. `struct aria_avx_ops` instances are static globals in glue modules, not in the header. The constants determine request-context keystream buffer sizes and skcipher walk thresholds.

Dependencies and integration points: includes `linux/types.h` and assumes `ARIA_BLOCK_SIZE` is visible before size constants are used by C files that also include `crypto/aria.h`. The prototypes bind C glue to architecture-specific symbols in `aria-aesni-avx-asm_64.S`, `aria-aesni-avx2-asm_64.S`, and `aria-gfni-avx512-asm_64.S`.

Risks: any mismatch between constants and assembly batch widths causes buffer overrun or missed fast paths. Prototype drift would be especially dangerous for CTR because the argument order includes both a scratch keystream pointer and mutable IV pointer.

Test signals: compile coverage across AVX, AVX2, and AVX512 configs catches declaration mismatches. Runtime crypto tests should verify that each driver consumes exactly its advertised block batch and that request context sizes are adequate for CTR scratch buffers.
