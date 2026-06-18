# Research: subset-b-006091

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/poly1305-x86_64-cryptogams.pl -->
# sources/distributed-fs/ceph-client/lib/crypto/x86/poly1305-x86_64-cryptogams.pl

## Purpose
This Perl generator emits x86_64 Poly1305 assembly derived from OpenSSL CRYPTOGAMS for both standalone and Linux-kernel output modes. In this tree it is the source for the kernel x86 Poly1305 assembly used by `poly1305.h`, covering scalar integer code plus AVX, AVX2, AVX512F, and non-kernel VPMADD52/AVX512IFMA variants. It implements Poly1305 block accumulation, final tag emission, key-power precomputation, SIMD radix conversions, and optional non-kernel ChaCha20-Poly1305 XOR-and-pad helpers.

## Important APIs, Types, And Functions
- Generator controls: `$flavour`, `$output`, `$kernel`, `$win64`, and `$avx` select kernel versus perlasm output, Win64 SEH generation, and how many SIMD families to emit.
- `declare_function()` and `end_function()` abstract Linux `SYM_FUNC_START/END` versus ELF/MASM/NASM style function metadata.
- `poly1305_init_x86_64(ctx, key, out_fnptrs)` zeroes `h`, clamps and stores `r`, and in non-kernel mode selects function pointers from CPU capability flags.
- `poly1305_blocks_x86_64(ctx, inp, len, padbit)` is the scalar base-2^64 block loop. It processes 16-byte blocks, adds the block and pad bit into the accumulator, invokes `poly1305_iteration`, and stores `h[0..2]`.
- `poly1305_emit_x86_64(ctx, mac, nonce)` conditionally subtracts the Poly1305 modulus by comparing `h + 5`, adds the nonce, and writes the 16-byte tag.
- `__poly1305_block` and `poly1305_iteration()` implement the scalar 130-bit multiply/reduction core used both directly and for SIMD key-power setup.
- `__poly1305_init_avx()` computes `r^2`, `r^3`, and `r^4` and stores interleaved base-2^26 limbs and their `*5` multiples for parallel SIMD loops.
- `poly1305_blocks_avx`, `poly1305_blocks_avx2`, and `poly1305_blocks_avx512` process multiple blocks in base 2^26 with precomputed key powers, lazy reduction, horizontal lane folding, and scalar/SIMD conversion prologues.
- Non-kernel-only paths include `poly1305_init_base2_44`, `poly1305_blocks_vpmadd52`, `poly1305_blocks_vpmadd52_4x`, `poly1305_blocks_vpmadd52_8x`, and `poly1305_emit_base2_44`, which use radix 2^44 and AVX512IFMA/VPMADD52 instructions.
- Non-kernel helpers `xor128_encrypt_n_pad` and `xor128_decrypt_n_pad` update one-time-pad bytes while encrypting/decrypting and zero-pad the partial block area.

## Control Flow
The script first determines output flavor and assembler SIMD support, then builds a `$code` string containing rodata constants, function bodies, optional AVX families, optional Win64 SEH metadata, and final text translation. Kernel mode bypasses OpenSSL capability dispatch and emits Linux linkage macros. The scalar block routine shifts length to a block count and loops until all complete blocks are consumed. SIMD routines gate on input length and the `is_base2_26` state bit: short or unconverted inputs fall back to scalar, odd alignment tails are normalized through scalar blocks, and long aligned ranges jump into vector loops. AVX2/AVX512 share `poly1305_blocks_avxN()`, with AVX512 selected for sufficiently large lengths in non-kernel mode or a direct kernel entry. The IFMA path uses one-block setup until key powers exist, then chooses 2x/4x/8x loops based on block count. Final emission converts radix-specific accumulators back to the base-2^64 finalization shape before adding the nonce.

## State And Persistence Behavior
All persistent cryptographic state lives in the caller-provided opaque context. The first 24 bytes hold the accumulator in either base 2^64 or radix-specific form. Scalar state stores `h[3]`, `r[2]`, and no SIMD flag. AVX state overlays `h[5]`, `is_base2_26`, `r[2]`, a pad slot, and nine interleaved key-power records. The SIMD code mutates `is_base2_26` to mark base-2^26 state and writes precomputed powers into the context for later updates. The IFMA path uses a sentinel at offset 64 to indicate missing key powers and persists powers for reuse. No filesystem or global persistent state is written by generated assembly; the Perl generator itself only writes to the requested assembly output stream.

## Dependencies And Integration Points
The emitted kernel assembly depends on `<linux/linkage.h>`, Linux x86 calling conventions, AVX/SSE register availability chosen by C wrappers, and the context layout defined in `poly1305.h`. Non-kernel output depends on `x86_64-xlate.pl`, `OPENSSL_ia32cap_P`, assembler feature support, and optional Win64 unwind metadata. It integrates with `poly1305.h` declarations for `poly1305_init_x86_64`, `poly1305_blocks_x86_64`, `poly1305_emit_x86_64`, `poly1305_emit_avx`, and SIMD block functions. The key clamp constants match Poly1305 requirements, and vector constants such as `.Lmask26`, `.L129`, permutation tables, and 44-bit masks are shared by emitted vector paths.

## Risks
- Context layout coupling is tight: changing `struct poly1305_arch_internal` field order or size would break hard-coded offsets.
- Mixed scalar/SIMD updates require exact radix conversion. Bugs in `is_base2_26` handling or tail normalization can silently corrupt tags.
- AVX512 and IFMA paths are highly CPU-feature-sensitive and can affect frequency or require unavailable xfeatures if called without C-side gating.
- The generator contains non-kernel OpenSSL dispatch code that differs from kernel wrappers; regressions must be checked in the generated kernel assembly, not just the Perl source.
- Hand-coded reductions are constant-time with respect to message values, but correctness depends on limb bounds and lazy-reduction invariants.
- Win64 SEH and perlasm translation are separate surfaces that are not necessarily exercised by Linux kernel builds.

## Test Signals
- Known-answer Poly1305 and ChaCha20-Poly1305 test vectors should match across scalar, AVX, AVX2, AVX512, and any IFMA path.
- Cross-path tests should intentionally switch from SIMD to scalar update after partial processing to exercise radix conversion.
- Boundary lengths around 0, 1 block, 2 blocks, 18 blocks, 64/128/512 bytes, and non-multiple tails should be compared against the generic C implementation.
- Kernel crypto selftests and module load on CPUs with and without AVX/AVX2/AVX512 verify dispatch and FPU gating.
- Generated assembly should be inspected or rebuilt after generator changes to catch syntax, symbol, and relocation drift.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/poly1305-x86_64-cryptogams.pl -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/poly1305.h -->
# sources/distributed-fs/ceph-client/lib/crypto/x86/poly1305.h

## Purpose
This header is the x86_64 architecture glue for Poly1305 in the kernel crypto library. It declares the generated assembly entry points, defines the x86-specific context overlay, handles runtime CPU feature selection with static keys, mediates kernel FPU usage, and provides architecture hooks expected by the generic Poly1305 implementation.

## Important APIs, Types, And Functions
- `struct poly1305_arch_internal` overlays generic Poly1305 state with `h[5]`, `is_base2_26`, `hs[3]`, `r[2]`, `pad`, and `rn[9]` key-power records used by the assembly.
- `convert_to_base2_64(void *ctx)` converts an AVX base-2^26 accumulator back to scalar base-2^64 and fully reduces it.
- Assembly declarations include `poly1305_init_x86_64`, `poly1305_blocks_x86_64`, `poly1305_emit_x86_64`, `poly1305_emit_avx`, `poly1305_blocks_avx`, `poly1305_blocks_avx2`, and `poly1305_blocks_avx512`.
- Static keys `poly1305_use_avx`, `poly1305_use_avx2`, and `poly1305_use_avx512` cache boot-time feature decisions.
- `poly1305_block_init()` calls the scalar init assembly.
- `poly1305_blocks()` selects scalar or AVX-family block processing based on static keys, message length, existing SIMD setup, and `irq_fpu_usable()`.
- `poly1305_emit()` selects scalar or AVX final emission.
- `poly1305_mod_init_arch()` enables static keys when CPU and xstate support are present and avoids AVX512 on Skylake-X.

## Control Flow
Initialization always goes through `poly1305_init_x86_64`. Block processing first recovers the x86 context from the generic block state. It rejects SIMD when AVX is unavailable, the message is shorter than 18 blocks and SIMD key setup has not happened, or FPU use is not allowed in the current context. In that case it converts any base-2^26 accumulator to base-2^64 and invokes scalar assembly. Otherwise it processes at most one page per FPU critical section, calls the best enabled SIMD block function, then releases the FPU and advances the input pointer. Finalization uses scalar emit unless AVX support was enabled; AVX emit can handle both scalar and base-2^26 states.

## State And Persistence Behavior
The header mutates only the caller's Poly1305 context and static branch keys. The static keys become read-mostly after architecture initialization. Per-message state persists in the Poly1305 context across update calls, including `is_base2_26` and SIMD key powers. FPU state is borrowed only between `kernel_fpu_begin()` and `kernel_fpu_end()`, with 4 KiB chunking to bound preemption-disabled time. No dynamic allocation or external persistence occurs.

## Dependencies And Integration Points
This file depends on kernel CPU feature helpers, xstate checks, static branches, FPU APIs, `container_of`, `min`, `SZ_4K`, and generic Poly1305 types/constants such as `struct poly1305_block_state`, `struct poly1305_state`, `POLY1305_BLOCK_SIZE`, and `POLY1305_DIGEST_SIZE`. It is directly coupled to offsets and radix conventions emitted by `poly1305-x86_64-cryptogams.pl`.

## Risks
- The generic and x86-specific context layouts must remain compatible with assembly hard-coded offsets.
- FPU availability is context-dependent; incorrect use outside `irq_fpu_usable()` would corrupt kernel FPU state.
- Static key selection assumes boot CPU feature consistency and correct xstate availability.
- Threshold tuning at 288 bytes affects performance but not correctness; changing it should be benchmarked.
- Conversion from base 2^26 to base 2^64 is critical when callers update from different contexts or when FPU use becomes unavailable.

## Test Signals
- Generic Poly1305 selftests should pass with static keys disabled and enabled.
- Tests should cover short messages below 288 bytes, long messages crossing a 4 KiB page chunk, and update sequences that force AVX then scalar fallback.
- CPU-feature-matrix testing should verify AVX, AVX2, AVX512, no-AVX, and Skylake-X AVX512 suppression behavior.
- KMSAN/KASAN are useful around context overlay and FPU-bound assembly calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/poly1305.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/polyval-pclmul-avx.S -->
# sources/distributed-fs/ceph-client/lib/crypto/x86/polyval-pclmul-avx.S

## Purpose
This assembly file implements POLYVAL multiplication and block evaluation using AVX-encoded PCLMULQDQ carryless multiplication. It targets the GHASH-like finite field used by POLYVAL with modulus `x^128 + x^127 + x^126 + x^121 + 1`, processes up to eight blocks per stride, and reduces one 256-bit polynomial product per stride for throughput.

## Important APIs, Types, And Functions
- `polyval_mul_pclmul_avx(struct polyval_elem *a, const struct polyval_elem *b)` multiplies `a` by `b` in Montgomery form and stores the reduced result back to `a`.
- `polyval_blocks_pclmul_avx(struct polyval_elem *acc, const struct polyval_key *key, const u8 *data, size_t nblocks)` evaluates POLYVAL over complete 16-byte blocks.
- `schoolbook1`, `schoolbook1_iteration`, and `schoolbook1_noload` compute 128x128-bit polynomial products into `LO`, `MI`, and `HI`.
- `schoolbook2` folds middle terms into the 256-bit `[PH:PL]` representation.
- `montgomery_reduction` folds low 128 bits using the `.Lgstar` constant and returns a Montgomery-form 128-bit result.
- `full_stride` handles eight blocks using precomputed key powers `h^8 ... h^1`.
- `partial_stride` handles 1 to 7 remaining blocks by offsetting the key-power pointer to the matching powers.

## Control Flow
`polyval_mul_pclmul_avx` loads the reduction constant and operands, performs a single schoolbook multiplication, reduces, writes the accumulator, and returns. `polyval_blocks_pclmul_avx` loads the current accumulator into `SUM`, subtracts eight from the block count, and either enters full-stride processing or jumps to partial handling. The first full stride avoids reduction of prior `PL/PH`; subsequent strides call `full_stride 1` to reduce the previous product and XOR it into the first block of the next stride. After the stride loop, it reduces any pending product, adjusts the residual block count, optionally runs `partial_stride`, then writes `SUM` back.

## State And Persistence Behavior
The only persistent state is the 16-byte `acc` element updated in place. Key powers are read-only through `key`. Message data is read sequentially. Temporary polynomial products live in XMM registers and are not persisted. There is no stack state beyond the normal frame macro and no global mutation.

## Dependencies And Integration Points
The file includes `<linux/linkage.h>` and `<asm/frame.h>` and uses `SYM_FUNC_START/END`, `FRAME_BEGIN/END`, and `RET`. It requires AVX instruction encoding and PCLMULQDQ support, so its caller must dispatch only when CPU features and kernel SIMD/FPU rules allow it. It integrates with the kernel POLYVAL/GCM-SIV code that prepares key powers and passes complete block counts.

## Risks
- Callers must provide complete blocks; there is no partial-block padding here.
- The key-power layout must be exactly `h^8` through `h^1` in 16-byte slots.
- Carryless multiplication and reduction are field-specific; using GHASH constants or endian conventions would produce invalid tags.
- The code uses unaligned loads for data but assumes pointers are valid for the requested number of blocks.

## Test Signals
- POLYVAL known-answer vectors and AES-GCM-SIV vectors should match generic code.
- Block counts 1 through 9 are important because they cover all partial and full stride transitions.
- Tests should compare `polyval_mul_pclmul_avx` against generic field multiplication for random elements.
- CPU dispatch tests should ensure this path is never called without PCLMUL/AVX support and active FPU allowance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/polyval-pclmul-avx.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/sha1-avx2-asm.S -->
# sources/distributed-fs/ceph-client/lib/crypto/x86/sha1-avx2-asm.S

## Purpose
This Intel-derived assembly implements `sha1_transform_avx2`, an AVX2/BMI optimized SHA-1 compression function for x86_64. It hashes complete 64-byte blocks, uses AVX2 vectors to precompute message schedules for two blocks at a time, and uses scalar integer/BMI instructions for SHA-1 rounds.

## Important APIs, Types, And Functions
- Exported entry: `sha1_transform_avx2(struct sha1_block_state *state, const u8 *data, size_t nblocks)`.
- `SHA1_VECTOR_ASM` emits the function prologue/epilogue, saves callee-saved registers, aligns and reserves the stack, runs `vzeroupper`, loads arguments, and invokes the main body.
- `SHA1_PIPELINED_MAIN_BODY` loads `A..E`, sets schedule buffers, precomputes two blocks, processes one or two blocks per loop, updates state, and swaps buffers.
- `PRECALC_00_15`, `PRECALC_16_31`, and `PRECALC_32_79` build the SHA-1 message schedule using YMM registers and byte-swap masks.
- `RR`, `ROUND_F1`, `ROUND_F2`, and `ROUND_F3` emit two rounds at a time using `rorx`, `andn`, arithmetic, and the precalculated `WK` buffer.
- Constants `K_XMM_AR` and `BSWAP_SHUFB_CTL` provide round constants and big-endian input conversion masks.

## Control Flow
The function saves registers, aligns stack storage for the double-buffered schedule, and initializes `HASH_PTR`, `BUFFER_PTR`, `BUFFER_PTR2`, and `BLOCKS_CTR`. It precomputes schedule words for the first two blocks when available. The main loop processes the first block, decrements the block counter, conditionally processes a second block using previously scheduled results, updates the in-memory state after each block, resets register aliases, swaps the work and precalc buffers, and loops until no blocks remain. `vzeroupper` is executed on entry and exit to avoid AVX/SSE transition penalties.

## State And Persistence Behavior
The SHA-1 chaining state is updated in place in the five-word `sha1_block_state`. The stack holds schedule buffers and is discarded after the transform. Input is read only. The function assumes `nblocks` is nonzero and complete-block-only; buffering and final padding are handled by higher layers.

## Dependencies And Integration Points
This file includes `<linux/linkage.h>` and is declared/wrapped by `sha1.h`, which calls it only when AVX, AVX2, BMI1, BMI2, xfeatures, and FPU usability allow. It depends on System V x86_64 register conventions, AVX2 YMM state, BMI `rorx`/`andn`, and kernel FPU bracketing by the caller.

## Risks
- Caller dispatch must ensure AVX2 and BMI availability; the function contains no runtime guards.
- Stack alignment and buffer sizing are integral to the macro-generated addressing.
- It updates state after each block, so any interruption through incorrect FPU handling or calling convention mismatch would leave partial state.
- SHA-1 is cryptographically weak for collision resistance; this implementation should only serve legacy SHA-1 users that already accept that property.

## Test Signals
- SHA-1 known-answer and long-message vectors should match generic code for `nblocks >= 4`, where this wrapper is selected.
- Boundary testing around the wrapper threshold in `sha1.h` should compare AVX2 and AVX paths.
- Random block-count tests should include odd and even block counts to exercise single-block tail behavior.
- objtool/build tests should confirm stack frame, unwind, and symbol metadata are valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/sha1-avx2-asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/sha1-ni-asm.S -->
# sources/distributed-fs/ceph-client/lib/crypto/x86/sha1-ni-asm.S

## Purpose
This assembly implements `sha1_ni_transform`, a SHA-1 compression function using Intel SHA extensions. It processes complete 64-byte blocks by mapping SHA-1 rounds and message expansion onto `sha1rnds4`, `sha1nexte`, `sha1msg1`, and `sha1msg2`.

## Important APIs, Types, And Functions
- Exported entry: `sha1_ni_transform(struct sha1_block_state *state, const u8 *data, size_t nblocks)`.
- `do_4rounds(i, m0, m1, m2, m3, e0, e1)` loads message words for rounds 0..15, byte-swaps them, advances SHA extension message schedule state for later rounds, and performs four SHA-1 rounds.
- Registers `ABCD`, `E0`, and `E1` hold the SHA-1 working state; `ABCD_SAVED` and `E0_SAVED` preserve the previous chaining state for feed-forward.
- `PSHUFFLE_BYTE_FLIP_MASK` converts input words from big-endian byte order.

## Control Flow
The function loads the five-word state into SHA extension register layout, loads the byte-swap mask, and enters `.Lnext_block`. For each block it saves the current state, emits twenty `do_4rounds` expansions through `.irp` for 80 rounds, adds the saved state back via SHA extension and vector additions, advances the input pointer by 64 bytes, decrements the block count, and loops. On exit it stores `E` and the reversed `ABCD` words back to memory.

## State And Persistence Behavior
Only the caller-provided SHA-1 state is mutated. Message schedule words and working variables live in XMM registers. Input is read-only and must contain `nblocks` complete blocks. No stack or global persistent state is used.

## Dependencies And Integration Points
This file includes `<linux/linkage.h>` and is selected by `sha1.h` when `X86_FEATURE_SHA_NI` is present. The C wrapper handles `kernel_fpu_begin/end()` and falls back to generic SHA-1 when FPU use is not legal. It depends on Intel SHA-NI and SSSE3-style `pshufb` support implied by the selected feature set.

## Risks
- Assumes `nblocks` is nonzero and complete-block-only.
- Incorrect state word ordering on load/store would break compatibility with generic SHA-1.
- Must never be called without SHA-NI support or outside kernel FPU protection.
- SHA-1 collision weakness remains an algorithm-level concern.

## Test Signals
- SHA-1 known-answer vectors, multi-block vectors, and randomized comparisons against `sha1_blocks_generic`.
- CPU dispatch tests on SHA-NI-capable and non-SHA-NI systems.
- FPU-unusable context tests should confirm the wrapper falls back rather than calling this routine.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/sha1-ni-asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/sha1-ssse3-and-avx.S -->
# sources/distributed-fs/ceph-client/lib/crypto/x86/sha1-ssse3-and-avx.S

## Purpose
This file emits two SHA-1 compression functions, `sha1_transform_ssse3` and `sha1_transform_avx`, using a shared macro body. It accelerates SHA-1 complete-block processing by vectorizing message scheduling while doing SHA-1 round arithmetic in general-purpose registers.

## Important APIs, Types, And Functions
- Exported entries: `sha1_transform_ssse3(struct sha1_block_state *state, const u8 *data, size_t nblocks)` and `sha1_transform_avx(...)`.
- `SHA1_VECTOR_ASM(name)` emits each function body, including register saves, a 64-byte aligned schedule workspace, state setup, message scheduling constants, and cleanup.
- `SHA1_PIPELINED_MAIN_BODY` loads the five-word state, precomputes 16 schedule entries, runs 80 rounds, updates the state, and loops over blocks.
- Round macros `F1` through `F4`, `RR`, and `UPDATE_HASH` implement SHA-1 logical functions, two-round issue, and feed-forward.
- `W_PRECALC_SSSE3` and `W_PRECALC_AVX` provide two variants of vector message scheduling using `pshufb`/SSE or VEX-encoded AVX instructions.
- Constants `K_XMM_AR` and `BSWAP_SHUFB_CTL` hold SHA-1 round constants and byte-swap masks.

## Control Flow
Each generated function saves callee-saved registers, reserves and aligns a stack workspace, computes the end pointer from `nblocks`, loads constants, and enters the shared main body. The body maintains a circular 64-word `WK` schedule buffer, runs the 80 SHA-1 rounds in unrolled two-round chunks, advances `BUFFER_PTR` by 64 bytes near the end of each block, substitutes a safe dummy pointer at the end to avoid overrun during lookahead scheduling, writes the updated state, restores register aliases, and loops until the dummy pointer indicates completion. The AVX variant swaps only the vector instruction forms and `xmm_mov` implementation.

## State And Persistence Behavior
The five SHA-1 chaining words are updated in place. The stack schedule buffer is explicitly zeroed with `rep stosq` before return. Input is read-only. No global state is modified.

## Dependencies And Integration Points
The file depends on `<linux/linkage.h>`, SSSE3 `pshufb`, and optionally AVX VEX-encoded instructions. `sha1.h` declares wrappers that select SSSE3 or AVX based on CPU and xfeature availability and perform FPU bracketing. The function prototypes and state layout are shared with the generic SHA-1 core.

## Risks
- The lookahead scheduler uses a dummy source to avoid reading past the final block; pointer arithmetic errors would be memory-safety critical.
- Stack workspace cleanup and alignment must remain correct for kernel calling conventions.
- Caller dispatch must enforce the required instruction set and FPU safety.
- SHA-1 itself is legacy and collision-weak.

## Test Signals
- Known SHA-1 test vectors and randomized complete-block comparisons against generic code.
- Block counts 1 and 2 exercise the lookahead/dummy-source edge.
- Dispatch tests should verify SSSE3-only CPUs choose `sha1_transform_ssse3`, AVX-capable CPUs choose `sha1_transform_avx` unless AVX2/SHA-NI supersede it.
- Build and objtool checks should validate generated stack metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/sha1-ssse3-and-avx.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/sha1.h -->
# sources/distributed-fs/ceph-client/lib/crypto/x86/sha1.h

## Purpose
This header is the x86_64 SHA-1 architecture dispatch layer. It exposes a single `sha1_blocks()` hook to generic SHA-1 code while selecting among generic, SSSE3, AVX, AVX2, and SHA-NI compression functions using static calls and runtime CPU feature checks.

## Important APIs, Types, And Functions
- `DEFINE_STATIC_CALL(sha1_blocks_x86, sha1_blocks_generic)` creates the default dispatch target.
- `DEFINE_X86_SHA1_FN(c_fn, asm_fn)` declares an assembly transform and wraps it with `irq_fpu_usable()`, `kernel_fpu_begin()`, and fallback to generic code.
- Generated wrappers: `sha1_blocks_ssse3`, `sha1_blocks_avx`, and `sha1_blocks_ni`.
- `sha1_blocks_avx2()` dispatches to `sha1_transform_avx2` only when `nblocks >= SHA1_AVX2_BLOCK_OPTSIZE` and otherwise reuses the AVX transform to avoid AVX2 overhead on small inputs.
- `sha1_blocks()` invokes the selected static call target.
- `sha1_mod_init_arch()` updates the static call target based on SHA-NI, AVX/AVX2/BMI/xstate, or SSSE3 features.

## Control Flow
At boot/module initialization, `sha1_mod_init_arch()` chooses the strongest supported implementation: SHA-NI first, then AVX2 if AVX2 plus BMI1/BMI2 are available, then AVX, then SSSE3, otherwise generic. At runtime `sha1_blocks()` calls the current static-call target. Each SIMD wrapper checks FPU usability before entering assembly; if FPU use is unavailable it calls `sha1_blocks_generic`.

## State And Persistence Behavior
The selected static call target persists after init. The wrappers mutate only the caller's SHA-1 block state. FPU state is borrowed only within explicit begin/end calls. There is no allocation and no per-call persistent state outside the hash state.

## Dependencies And Integration Points
This file depends on `<asm/fpu/api.h>`, `<linux/static_call.h>`, CPU feature helpers, xstate checks, and generic SHA-1 types and functions. It integrates directly with assembly files `sha1-ni-asm.S`, `sha1-ssse3-and-avx.S`, and `sha1-avx2-asm.S`.

## Risks
- Runtime dispatch must align with instruction usage; AVX2 requires BMI1/BMI2 because the AVX2 routine uses BMI instructions.
- Static-call update order prefers SHA-NI over AVX2, which is correct for SHA extension hardware but should be benchmarked on new CPUs if changed.
- FPU-unusable contexts must reliably fall back to generic or kernel state can be corrupted.
- SHA-1 is legacy and should not be used for new collision-resistant designs.

## Test Signals
- Verify static call target selection under mocked or real CPU feature combinations.
- Known-answer SHA-1 tests should pass under all selected backends.
- Test `nblocks` below and above 4 on AVX2-capable systems to exercise the AVX fallback threshold.
- Run in contexts where `irq_fpu_usable()` is false to verify generic fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/sha1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/sha256-avx-asm.S -->
# sources/distributed-fs/ceph-client/lib/crypto/x86/sha256-avx-asm.S

## Purpose
This assembly implements `sha256_transform_avx`, a SHA-256 compression function using AVX1 vector instructions for message scheduling and scalar integer operations for the round function. It processes complete 64-byte blocks one block at a time.

## Important APIs, Types, And Functions
- Exported entry: `sha256_transform_avx(struct sha256_block_state *state, const u8 *data, size_t nblocks)`.
- `COPY_XMM_AND_BSWAP` loads unaligned message data and byte-swaps each 32-bit word using `vpshufb`.
- `FOUR_ROUNDS_AND_SCHED` emits four SHA-256 rounds while computing the next four message schedule words using XMM registers.
- `DO_ROUND` handles later rounds after the schedule is available.
- `rotate_Xs` and `ROTATE_ARGS` maintain circular message/state aliases.
- `K256`, `PSHUFFLE_BYTE_FLIP_MASK`, `_SHUF_00BA`, and `_SHUF_DC00` provide round constants and shuffle masks.

## Control Flow
The function saves callee-saved registers, aligns a small stack frame, converts `nblocks` to an end pointer, loads the eight state words, and loads shuffle masks. For each block it byte-swaps the first 16 schedule words into four XMM registers, stores the input pointer, runs three loops of scheduled four-round groups for rounds 0..47, runs two loops of `DO_ROUND` for rounds 48..63, feeds the result back into the state memory, advances by 64 bytes, and repeats until the end pointer is reached.

## State And Persistence Behavior
The eight-word SHA-256 state is updated in place. The stack holds a temporary `XFER` vector and input pointers. Input is read-only and must contain complete blocks. No global state is modified.

## Dependencies And Integration Points
The file includes `<linux/linkage.h>` and is declared by `sha256.h`, which selects it when AVX and required xfeatures are available and SHA-NI/AVX2/PHE do not supersede it. The C wrapper handles kernel FPU bracketing and generic fallback.

## Risks
- Callers must only invoke it with AVX-capable FPU context and complete block counts.
- The macro-heavy schedule interleaves scalar and vector state; register alias errors would produce digest mismatches that may only appear for multi-block inputs.
- It uses unaligned loads but assumes valid memory for all requested blocks.

## Test Signals
- SHA-256 known-answer tests and randomized comparisons against generic code.
- Multi-block lengths should exercise loop repetition and state feed-forward.
- Dispatch tests should verify AVX path is selected only when SHA-NI and AVX2 paths are unavailable or lower priority.
- Build tests should catch stack/register convention regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/sha256-avx-asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/sha256-avx2-asm.S -->
# sources/distributed-fs/ceph-client/lib/crypto/x86/sha256-avx2-asm.S

## Purpose
This assembly implements `sha256_transform_rorx`, an AVX2/BMI2 optimized SHA-256 compression function. It schedules two blocks at a time with YMM vectors, uses `rorx` for scalar rotates, and has a special single-last-block path for odd block counts.

## Important APIs, Types, And Functions
- Exported entry: `sha256_transform_rorx(struct sha256_block_state *state, const u8 *data, size_t nblocks)`.
- `FOUR_ROUNDS_AND_SCHED(disp)` performs four rounds and computes four schedule words across two blocks using AVX2 operations.
- `DO_4ROUNDS(disp)` consumes precomputed schedule entries for four rounds without further scheduling.
- `rotate_Xs` and `ROTATE_ARGS` rotate message and working-state aliases.
- Stack slots store two blocks worth of `K+W` schedule material, input end/current pointers, and context pointer.
- `K256` is duplicated per lane for two-block vector scheduling; masks provide byte swapping and schedule shuffles.

## Control Flow
The function saves registers, aligns the stack to 32 bytes, computes the last-block pointer, and special-cases single-block input. For two or more blocks it loads initial state and masks, then `.Lloop0` loads two message blocks into YMM registers, byte-swaps, transposes high and low halves, and enters scheduled rounds. It stores schedule data for both blocks, processes the first block, feeds state forward, then processes the second block from stored schedule data. If more pairs remain it loops. If exactly one final block remains, `.Ldo_last_block` loads only XMM data and reuses the common round path. It ends with `vzeroupper`.

## State And Persistence Behavior
The function updates the in-memory SHA-256 state after each block. It uses stack storage for the expanded schedule and context/input pointers. Input is read-only. No global state is modified.

## Dependencies And Integration Points
The file includes `<linux/linkage.h>` and is selected by `sha256.h` when AVX, AVX2, BMI2, and required xfeatures are available and SHA-NI/PHE do not supersede it. Kernel FPU protection is handled outside the assembly.

## Risks
- Requires BMI2 `rorx`; dispatch must match `sha256.h` feature checks.
- Odd block handling shares paths with pair processing and is sensitive to pointer comparisons around `_INP_END`.
- Schedule stack layout and 32-byte alignment are mandatory for YMM stores.
- Missing or misplaced `vzeroupper` would hurt callers mixing AVX and SSE.

## Test Signals
- SHA-256 known-answer tests with 1, 2, 3, and larger odd/even block counts.
- Random block streams compared to generic SHA-256.
- Dispatch verification on AVX2+BMI2 systems and AVX-only systems.
- Kernel build/objtool validation for stack and unwind safety.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/sha256-avx2-asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/sha256-ni-asm.S -->
# sources/distributed-fs/ceph-client/lib/crypto/x86/sha256-ni-asm.S

## Purpose
This file implements SHA-256 compression using Intel SHA extensions and also provides a two-message `finup` helper for parallel SHA-256 finalization. The first entry accelerates normal complete-block updates; the second computes two same-length message digests from a shared context by interleaving SHA-NI work.

## Important APIs, Types, And Functions
- `sha256_ni_transform(struct sha256_block_state *state, const u8 *data, size_t nblocks)` processes complete 64-byte blocks and updates state.
- `sha256_ni_finup2x(const struct __sha256_ctx *ctx, const u8 *data1, const u8 *data2, int len, u8 out1[32], u8 out2[32])` finalizes two equal-length SHA-256 messages in parallel.
- `do_4rounds` emits four rounds for one message using `sha256rnds2`, `sha256msg1`, and `sha256msg2`.
- `do_4rounds_2x` emits interleaved four-round groups for two independent messages.
- `PSHUFFLE_BYTE_FLIP_MASK` and `K256` provide endian conversion and SHA-256 constants.
- Hard-coded offsets `OFFSETOF_STATE`, `OFFSETOF_BYTECOUNT`, and `OFFSETOF_BUF` mirror `struct __sha256_ctx`.

## Control Flow
`sha256_ni_transform` converts `nblocks` to an end pointer, loads state into SHA-NI register order (`ABEF`/`CDGH`), loops over blocks with 64 rounds, feeds forward the saved state, advances input, and stores state back in canonical word order. `sha256_ni_finup2x` allocates aligned stack space, loads the initial context and byte count, handles any existing buffered bytes by combining `ctx->buf` with each input stream, then loops over pairs of blocks. Once data is exhausted, it constructs the SHA-256 padding block(s), including count-only spill when needed, processes final blocks, byte-swaps output words, and writes two 32-byte digests.

## State And Persistence Behavior
`sha256_ni_transform` mutates the caller's block state. `sha256_ni_finup2x` treats `ctx` as read-only and writes only `out1` and `out2`; it does not update `ctx`. Temporary final blocks and saved states are held on the stack. Both input streams are read-only.

## Dependencies And Integration Points
The file includes `<linux/linkage.h>` and is declared by `sha256.h`. `sha256.h` selects the transform through a static call when `X86_FEATURE_SHA_NI` is present and exposes `sha256_finup_2x_arch()` for the two-message helper when SHA-NI and FPU context are available. The two-message helper depends on exact `struct __sha256_ctx` layout asserted in the C header.

## Risks
- `sha256_ni_finup2x` has preconditions enforced by the wrapper: `len >= 64`, `len <= 65536`, same length for both messages, and FPU usability.
- The helper reads 64 bytes around tail handling by backing up pointers; the wrapper and callers must provide buffers satisfying those assumptions.
- Hard-coded context offsets must stay synchronized with C static assertions.
- SHA-NI state word ordering is non-obvious and prone to store/load mistakes.

## Test Signals
- SHA-256 known-answer and random multi-block tests for `sha256_ni_transform`.
- `finup2x` tests with buffered context lengths 0..63, message lengths around 64, 65, 119, 120, 65536, and count-only padding boundaries.
- Compare `finup2x` outputs to two independent generic SHA-256 computations.
- Dispatch tests should verify `have_sha_ni` gating and KMSAN unpoisoning behavior in `sha256.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/sha256-ni-asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/sha256-ssse3-asm.S -->
# sources/distributed-fs/ceph-client/lib/crypto/x86/sha256-ssse3-asm.S

## Purpose
This assembly implements `sha256_transform_ssse3`, a SHA-256 compression function for SSSE3-capable x86_64 CPUs. It uses XMM vector instructions for endian conversion and message schedule expansion while performing SHA-256 round arithmetic in general-purpose registers.

## Important APIs, Types, And Functions
- Exported entry: `sha256_transform_ssse3(struct sha256_block_state *state, const u8 *data, size_t nblocks)`.
- `COPY_XMM_AND_BSWAP` loads unaligned input and byte-swaps 32-bit words with `pshufb`.
- `FOUR_ROUNDS_AND_SCHED` computes four rounds and the next schedule words using XMM temporaries.
- `DO_ROUND` consumes stored `K+W` entries for one scalar round.
- `rotate_Xs`, `ROTATE_ARGS`, and `addm` maintain circular aliases and feed-forward.
- `K256`, `PSHUFFLE_BYTE_FLIP_MASK`, `_SHUF_00BA`, and `_SHUF_DC00` hold constants and shuffle controls.

## Control Flow
The function saves callee-saved registers, aligns the stack, computes the input end pointer, loads the current digest words, and loads shuffle masks. For each block it byte-swaps four XMM chunks, runs three schedule loops for the first 48 rounds, runs two loops for the last 16 rounds, adds the working state back into the digest memory, advances by 64 bytes, and repeats until the computed end pointer is reached.

## State And Persistence Behavior
Only the eight-word SHA-256 block state is persisted and updated. Stack storage holds a temporary vector transfer area and input pointer. Input is read-only. No global data is modified.

## Dependencies And Integration Points
The file includes `<linux/linkage.h>` and is selected by `sha256.h` as the baseline SIMD SHA-256 path when SSSE3 exists but stronger SHA-NI, PHE, AVX, or AVX2 paths are not selected. The C wrapper handles FPU begin/end and generic fallback.

## Risks
- It must only run on SSSE3-capable CPUs with usable kernel FPU state.
- Message schedule and scalar rounds are tightly interleaved; regressions may be data-dependent across rounds.
- The function assumes `nblocks` complete input blocks and does no padding.

## Test Signals
- SHA-256 known-answer vectors and random comparisons against the generic implementation.
- Single-block and multi-block tests exercise `.Lloop0`, `.Lloop1`, and `.Lloop2`.
- CPU dispatch tests should verify SSSE3 fallback behavior on non-AVX machines.
- Build/objtool checks should validate register save/restore and stack frame correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/sha256-ssse3-asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/sha256.h -->
# sources/distributed-fs/ceph-client/lib/crypto/x86/sha256.h

## Purpose
This header provides the x86_64 architecture dispatch layer for SHA-256. It selects among generic, SSSE3, AVX, AVX2/BMI2, SHA-NI, and Zhaoxin PHE implementations, wraps assembly with kernel FPU safety, and exposes a SHA-NI optimized two-message finalization hook.

## Important APIs, Types, And Functions
- `DEFINE_STATIC_CALL(sha256_blocks_x86, sha256_blocks_generic)` defines the runtime block transform target.
- `DEFINE_X86_SHA256_FN` declares an assembly transform and creates an FPU-safe wrapper.
- Wrappers include `sha256_blocks_ssse3`, `sha256_blocks_avx`, `sha256_blocks_avx2`, and `sha256_blocks_ni`.
- `sha256_blocks_phe()` invokes Zhaoxin `REP XSHA256` with a 32-byte, 16-byte-aligned state buffer.
- `sha256_blocks()` invokes the current static call target.
- `sha256_ni_finup2x()` is declared and wrapped by `sha256_finup_2x_arch()`.
- `sha256_finup_2x_is_optimized_arch()` reports whether SHA-NI two-message finalization is enabled.
- `sha256_mod_init_arch()` chooses SHA-NI first, then Zhaoxin PHE, then AVX2, AVX, SSSE3, or generic.

## Control Flow
During architecture initialization, the header updates the static call target based on CPU features and xstate. SHA-NI enables both the block transform and the `have_sha_ni` static key. If SHA-NI is absent, the Zhaoxin PHE path can be selected when configured and available; otherwise AVX2+BMI2, AVX, or SSSE3 are selected in descending order. Runtime block calls go through the static call. SIMD wrappers enter assembly only when `irq_fpu_usable()` succeeds. `sha256_finup_2x_arch()` checks SHA-NI, length bounds, and FPU usability before calling assembly and then unpoisons output for KMSAN.

## State And Persistence Behavior
The static call target and `have_sha_ni` static key persist after initialization. Block wrappers mutate only the SHA-256 block state. The PHE path copies state into an aligned stack buffer, runs the instruction, and copies it back. The two-message finup path treats the input context as read-only and writes output digests.

## Dependencies And Integration Points
This file depends on `<asm/fpu/api.h>`, `<linux/static_call.h>`, CPU feature helpers, xstate checks, `PTR_ALIGN`, `memcpy`, `kmsan_unpoison_memory`, SHA-256 context layout, and assembly files for SSSE3/AVX/AVX2/SHA-NI. Static assertions tie `struct __sha256_ctx` offsets to the assembly finup helper.

## Risks
- Dispatch feature checks must match instruction usage, especially AVX2 requiring BMI2 and SHA-NI finup requiring exact context offsets.
- PHE inline assembly has vendor-specific register and alignment requirements.
- FPU-unusable fallback is mandatory for correctness in interrupt or other restricted contexts.
- The two-message helper bounds `len` to 65536 to avoid long preemption-disabled regions; changing this has latency implications.

## Test Signals
- SHA-256 known-answer tests under each backend.
- Feature-dispatch tests for SHA-NI, Zhaoxin PHE, AVX2, AVX, SSSE3, and generic fallback.
- `sha256_finup_2x_arch()` comparisons against two independent generic hashes for many buffer and length alignments.
- KMSAN should see outputs unpoisoned after the optimized finup path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/sha256.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/sha512-avx-asm.S -->
# sources/distributed-fs/ceph-client/lib/crypto/x86/sha512-avx-asm.S

## Purpose
This assembly implements `sha512_transform_avx`, a SHA-512 compression function for x86_64 using AVX vector instructions to schedule two 64-bit message words at a time while scalar GPRs execute the 80 SHA-512 rounds. It processes complete 128-byte blocks.

## Important APIs, Types, And Functions
- Exported entry: `sha512_transform_avx(struct sha512_block_state *state, const u8 *data, size_t nblocks)`.
- `SHA512_Round(rnd)` performs one SHA-512 round using scalar 64-bit registers and `WK_2(rnd)` schedule constants.
- `SHA512_2Sched_2Round_avx(rnd)` computes two message schedule words with XMM/AVX operations while executing two scalar rounds.
- `RotateState` rotates aliases for `a..h`; `RORQ` uses `shld` for rotates.
- Stack frame arrays `W_t` and `WK_2` store 80 schedule words and two `W+K` values.
- `XMM_QWORD_BSWAP` byte-swaps two 64-bit words; `K512` holds the 80 SHA-512 constants.

## Control Flow
The function saves callee-saved GPRs, allocates an aligned stack frame, and enters `.Lupdateblock`. For each block it loads the eight 64-bit digest words into GPRs. The unrolled scheduler first loads and byte-swaps the initial 16 words in pairs, leading the round computation by one pair. For rounds 16 through 78 it calls `SHA512_2Sched_2Round_avx` to compute the next schedule words and two rounds. The final iteration executes the last two rounds without scheduling. It feeds the result back into the digest, advances by 128 bytes, decrements `nblocks`, and loops. The epilogue restores the stack and registers.

## State And Persistence Behavior
The eight-word SHA-512 state is updated in place. Message schedule state is stack-local and discarded. Input is read-only and must consist of complete SHA-512 blocks. No global mutable state exists.

## Dependencies And Integration Points
The file includes `<linux/linkage.h>` and relies on AVX-capable SIMD state managed by its C wrapper. It shares generic SHA-512 state layout and constants with the kernel crypto library. The caller is responsible for feature dispatch, FPU bracketing, and padding/buffering.

## Risks
- It assumes `nblocks >= 1` and complete blocks; zero or partial input is a caller bug.
- Stack frame alignment and large schedule storage are essential for correct addressing.
- Uses AVX/XMM registers without internal FPU guards, so wrapper dispatch must be correct.
- Register alias macros make round order sensitive to maintenance mistakes.

## Test Signals
- SHA-512 known-answer tests, including multi-block messages, compared against generic implementation.
- Boundary tests for exactly one block and several blocks.
- CPU dispatch tests should ensure AVX path is not called without xstate support and FPU usability.
- Build/objtool checks should catch stack and symbol regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/crypto/x86/sha512-avx-asm.S -->
