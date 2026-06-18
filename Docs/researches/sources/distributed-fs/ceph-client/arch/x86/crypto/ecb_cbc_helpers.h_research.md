<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/ecb_cbc_helpers.h -->
# sources/distributed-fs/ceph-client/arch/x86/crypto/ecb_cbc_helpers.h

Purpose: This header provides macro templates for x86 block-cipher skcipher ECB and CBC request walking. It is designed for glue files that need direct calls to vector assembly and scalar fallbacks without indirect-call overhead.

Important APIs/types/functions: `ECB_WALK_START` and `CBC_WALK_START` declare local walk state, calculate whether the FPU/vector path should be active, and begin `kernel_fpu_begin()` when a segment has enough blocks. `ECB_BLOCK` calls a block function repeatedly for a fixed block count. `CBC_ENC_BLOCK` implements serial CBC encryption with `crypto_xor_cpy`. `CBC_DEC_BLOCK` handles parallel CBC decryption, preserving the last ciphertext block for IV update and in-place safety. `ECB_WALK_END` and `CBC_WALK_END` close the FPU section and call `skcipher_walk_done`.

Control flow: A glue handler expands `*_WALK_START`, one or more `*_BLOCK` invocations from largest to smallest block grouping, and `*_WALK_END`. The generated loop advances through each contiguous skcipher segment. When the code transitions from vector chunk size to smaller scalar chunks, the macro ends the kernel FPU section so scalar C helpers run outside vector state ownership.

State and persistence: All state is local macro-expanded stack state: `ctx`, `skcipher_walk`, `nbytes`, `src`, `dst`, `do_fpu`, and a small IV preservation buffer. The only persistent mutation is the caller-visible CBC IV in `walk.iv`, carried across segments.

Dependencies and integration points: It includes `crypto/internal/skcipher.h` and `asm/fpu/api.h`. Consumers must provide block functions with the signature `(ctx, dst, src)` and must pass accurate block sizes and vector block counts. It integrates many x86 CAST, Serpent, and Twofish glue files with the Crypto API walk model.

Risks and test signals: Because these are macros, variable names and control-flow structure are part of the contract; misuse can compile but corrupt data. `fpu_blocks == -1` disables FPU ownership for scalar-only paths. In-place CBC decrypt relies on the local buffer before overwrite. Tests should stress segmented scatterlists, zero-length and tail requests, transitions from vector to scalar fallback, IV continuity across walk segments, and lockdep/preemption-sensitive FPU usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/crypto/ecb_cbc_helpers.h -->
