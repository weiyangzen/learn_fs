<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-sse2-i586-asm_32.S -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-sse2-i586-asm_32.S

Purpose: This i386 assembly file implements 4-way SSE2 Serpent encryption and decryption for 32-bit x86. It provides the low-level routines behind the shared SSE2 Serpent glue on CONFIG_X86_32 builds.

Important APIs/types/functions: Public symbols are `__serpent_enc_blk_4way` and `serpent_dec_blk_4way`. The encryption symbol accepts an extra `bool xor` argument that selects either normal write or XOR-with-existing-output behavior through the `xor_blocks` macro. Macro groups define key loading (`get_key`, `K`, `LK`, `KL`), Serpent S-boxes and inverse S-boxes (`S0` through `S7`, `SI0` through `SI7`), block transposition, and read/write/xor helpers.

Control flow: The encrypt routine reads four blocks from the source, transposes them into bit-sliced SSE registers, applies the Serpent round sequence with linear transforms, and writes or XORs output depending on the caller's flag. The decrypt routine reads four encrypted blocks, applies inverse rounds, and writes plaintext. The i386 calling convention uses stack argument offsets for context, destination, source, and the XOR flag.

State and persistence: The code is stateless apart from the caller's Serpent context. It uses XMM registers and stack-passed arguments. Output is written to the request destination; no global state changes.

Dependencies and integration points: It includes `linux/linkage.h` and is declared by `serpent-sse2.h`. `serpent_sse2_glue.c` calls it through inline wrappers and gates module registration on `X86_FEATURE_XMM2`.

Risks and test signals: The 32-bit ABI and stack offsets are fragile. SSE2 register use must match kernel FPU ownership in the glue helpers. Tests should include 32-bit build coverage, 4-block and tail Serpent vectors, CBC decrypt through the glue helper, in-place requests, and verification that the XOR-enabled encrypt path is only used by callers that expect it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/serpent-sse2-i586-asm_32.S -->
