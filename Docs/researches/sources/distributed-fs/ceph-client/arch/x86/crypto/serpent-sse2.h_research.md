<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-sse2.h -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-sse2.h

Purpose: This header abstracts the 32-bit and 64-bit SSE2 Serpent assembly ABIs behind common inline wrappers for glue code.

Important APIs/types/functions: On `CONFIG_X86_32`, `SERPENT_PARALLEL_BLOCKS` is 4 and declarations target `__serpent_enc_blk_4way` plus `serpent_dec_blk_4way`. Otherwise the parallel count is 8 and declarations target `__serpent_enc_blk_8way` plus `serpent_dec_blk_8way`. Inline wrappers `serpent_enc_blk_xway`, `serpent_enc_blk_xway_xor`, and `serpent_dec_blk_xway` normalize the caller interface and set the encryption XOR flag.

Control flow: The header has no standalone runtime flow. Glue code calls the common inline names, which dispatch to the architecture-width-specific assembly entry points.

State and persistence: It owns no state. It passes caller-owned `struct serpent_ctx`, source, and destination pointers to assembly.

Dependencies and integration points: It includes `linux/crypto.h` and `crypto/serpent.h`. It connects `serpent_sse2_glue.c` to either `serpent-sse2-i586-asm_32.S` or `serpent-sse2-x86_64-asm_64.S`.

Risks and test signals: The parallel block constant must match the selected assembly routine and the glue walk thresholds. Tests should compile both 32-bit and 64-bit configurations and run Serpent vector tests across ECB and CBC modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-sse2.h -->
