# subset-b-006104 Research

Grouped research report for RAID XOR and RAID6 sources. Each file has a source-path title and an exact begin/end marker for deterministic split into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/alpha/xor.c -->
# sources/distributed-fs/ceph-client/lib/raid/xor/alpha/xor.c

Purpose: provides Alpha EV5/EV6 hand-scheduled RAID XOR implementations for the generic XOR dispatch framework. It exports two templates, `xor_block_alpha` and `xor_block_alpha_prefetch`, wrapping assembly entry points for 2 through 5 operands.

Important APIs and flow: external assembly symbols `xor_alpha_{2,3,4,5}` and `xor_alpha_prefetch_{2,3,4,5}` process 64-byte chunks with Alpha `ldq`, `xor`, and `stq` instructions. `DO_XOR_BLOCKS()` builds `xor_gen_alpha()` and `xor_gen_alpha_prefetch()` so the core can feed arbitrary source counts in groups of up to four source buffers.

State and persistence: no durable state; only in-place mutation of the destination parity buffer. Template speed is later filled by XOR calibration unless Alpha architecture code forces a template.

Dependencies and integration: depends on `xor_impl.h` for template shape and wrapper generation, and on `alpha/xor_arch.h` for registration policy. It integrates with `xor-core.c` through `struct xor_block_template`.

Risks and test signals: risks are assembly ABI register assumptions, 64-byte alignment, and read-past/write-past mistakes in unrolled loops. Signals include `CONFIG_XOR_KUNIT_TEST`, boot-time XOR speed logs, Alpha EV6 selection of prefetch code, and RAID5 parity checks under large aligned buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/alpha/xor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/alpha/xor_arch.h -->
# sources/distributed-fs/ceph-client/lib/raid/xor/alpha/xor_arch.h

Purpose: supplies Alpha-specific XOR implementation registration for the common XOR core.

Important APIs and flow: declares `xor_block_alpha` and `xor_block_alpha_prefetch`. `arch_xor_init()` tests `implver()`: EV6 forces `xor_block_alpha_prefetch` because cold-cache behavior is expected to be better, while other Alpha variants register generic `8regs`, `32regs`, and both Alpha templates for calibration.

State and persistence: no runtime persistence beyond `xor-core.c`'s forced-template or registered-template list.

Dependencies and integration: depends on `<asm/special_insns.h>` for `implver()` and `IMPLVER_EV6`, and is included by `xor-core.c` when `CONFIG_XOR_BLOCKS_ARCH` is enabled.

Risks and test signals: forced selection bypasses calibration, so a CPU identification mistake could lock in a slower or broken path. Signals are boot logs showing forced or measured template choice and KUnit XOR correctness on Alpha builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/alpha/xor_arch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/arm/xor-neon-glue.c -->
# sources/distributed-fs/ceph-client/lib/raid/xor/arm/xor-neon-glue.c

Purpose: exposes the ARM NEON XOR implementation to the generic XOR template registry while containing NEON use inside the kernel NEON critical section.

Important APIs and flow: `xor_gen_neon()` calls `kernel_neon_begin()`, then `xor_gen_neon_inner()`, then `kernel_neon_end()`. `xor_block_neon` advertises the wrapper as template name `neon`.

State and persistence: no persistent state; the only state concern is CPU SIMD context ownership while parity buffers are mutated in place.

Dependencies and integration: depends on `xor_arch.h` for `xor_gen_neon_inner()` and NEON helpers, and is registered by `arm/xor_arch.h` when `CONFIG_KERNEL_MODE_NEON` and `cpu_has_neon()` are true.

Risks and test signals: risk centers on entering NEON while preemption or kernel-mode SIMD constraints are not satisfied. Signals include ARM KUnit XOR tests, build coverage with `CONFIG_KERNEL_MODE_NEON`, and parity workloads on NEON-capable ARMv7.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/arm/xor-neon-glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/arm/xor-neon.c -->
# sources/distributed-fs/ceph-client/lib/raid/xor/arm/xor-neon.c

Purpose: builds the ARM NEON inner XOR implementation by compiling the generic `xor-8regs.c` loop with vectorization enabled.

Important APIs and flow: requires `__ARM_NEON__` and, for GCC, enables `tree-vectorize`. It defines `NO_TEMPLATE`, includes `../xor-8regs.c` to reuse `xor_8regs_{2,3,4,5}`, then emits `xor_gen_neon_inner()` through `__DO_XOR_BLOCKS()`.

State and persistence: no persistent state; it mutates `dest` in place according to `srcs`.

Dependencies and integration: depends on NEON compiler flags from the build system, `xor_impl.h` wrapper macros, and the glue file that performs `kernel_neon_begin/end`.

Risks and test signals: correctness depends on compiler vectorization preserving the scalar XOR semantics and respecting alignment/length assumptions. Signals include compiler build failures when flags are missing, KUnit randomized XOR tests, and inspection of generated NEON code in architecture builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/arm/xor-neon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/arm/xor.c -->
# sources/distributed-fs/ceph-client/lib/raid/xor/arm/xor.c

Purpose: implements an ARM 32-bit scalar assembly XOR template named `arm4regs`.

Important APIs and flow: macros `GET_BLOCK_2/4`, `XOR_BLOCK_2/4`, and `PUT_BLOCK_2/4` use `ldmia` and `stmia` with fixed registers. `xor_arm4regs_{2,3}` process four words per iteration; `{4,5}` reduce register pressure by processing two words per iteration. `DO_XOR_BLOCKS()` creates `xor_gen_arm4regs()`.

State and persistence: no persistence; destination memory is updated in place.

Dependencies and integration: registered from `arm/xor_arch.h` alongside generic and optional NEON templates. The code relies on ARM register allocation constraints and inline assembly clobber behavior.

Risks and test signals: risk comes from inline assembly register constraints, `lr`/`ip` use, alignment, and source count dispatch. Signals include ARM KUnit XOR tests, RAID5 parity tests, and boot calibration logs comparing `arm4regs` against generic and NEON routines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/arm/xor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/arm/xor_arch.h -->
# sources/distributed-fs/ceph-client/lib/raid/xor/arm/xor_arch.h

Purpose: defines ARM XOR template registration policy.

Important APIs and flow: declares `xor_block_arm4regs`, `xor_block_neon`, and `xor_gen_neon_inner()`. `arch_xor_init()` always registers ARM scalar `arm4regs` and generic `8regs`/`32regs`; with kernel-mode NEON and `cpu_has_neon()`, it also registers `xor_block_neon`.

State and persistence: registration feeds the core's init-only template list; no other persistence.

Dependencies and integration: depends on `<asm/neon.h>` and is included by `xor-core.c` for ARM builds with architecture XOR blocks.

Risks and test signals: CPU feature detection and SIMD gating determine whether NEON participates in calibration. Signals are boot XOR measurement output, KUnit, and NEON build/config combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/arm/xor_arch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/arm64/xor-neon-glue.c -->
# sources/distributed-fs/ceph-client/lib/raid/xor/arm64/xor-neon-glue.c

Purpose: creates arm64 SIMD-safe `xor_block_template` wrappers for NEON and SHA3 `eor3` XOR implementations.

Important APIs and flow: `XOR_TEMPLATE(neon)` and `XOR_TEMPLATE(eor3)` generate `xor_gen_neon()` and `xor_gen_eor3()`. Each wrapper executes the corresponding `_inner` function inside `scoped_ksimd()` and publishes `xor_block_neon` or `xor_block_eor3`.

State and persistence: no durable state; it protects live kernel SIMD state while mutating parity buffers.

Dependencies and integration: depends on `<asm/simd.h>`, `xor-neon.h`, and `arm64/xor_arch.h`, which registers one of these templates when NEON is present.

Risks and test signals: risks include SIMD use outside a valid kernel SIMD section and mismatched inner function declarations. Signals include arm64 build coverage, KUnit XOR tests, and boot logs selecting `neon` or `eor3`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/arm64/xor-neon-glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/arm64/xor-neon.c -->
# sources/distributed-fs/ceph-client/lib/raid/xor/arm64/xor-neon.c

Purpose: provides arm64 NEON and SHA3 EOR3 accelerated XOR inner loops.

Important APIs and flow: `__xor_neon_{2,3,4,5}` load four `uint64x2_t` vectors per iteration, XOR each requested source into destination, and store back. `eor3()` emits the SHA3 `eor3` instruction. `__xor_eor3_{3,4,5}` use three-input XOR where profitable, while the 2-source case reuses NEON. `__DO_XOR_BLOCKS()` emits `xor_gen_neon_inner()` and `xor_gen_eor3_inner()`.

State and persistence: no persistent state; destination pages are modified in place. The caller must already own SIMD state.

Dependencies and integration: depends on `<asm/neon-intrinsics.h>`, ARM64 SHA3 feature support, `xor-neon.h`, and glue wrappers.

Risks and test signals: risks include alignment assumptions, SHA3 feature gating, and inline assembly constraints for `eor3`. Signals include KUnit randomized XOR testing, feature-gated boot selection, and parity verification on NEON-only and SHA3-capable arm64 CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/arm64/xor-neon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/arm64/xor-neon.h -->
# sources/distributed-fs/ceph-client/lib/raid/xor/arm64/xor-neon.h

Purpose: declares the two arm64 SIMD inner XOR generator functions shared between implementation and glue units.

Important APIs and flow: exposes `xor_gen_neon_inner()` and `xor_gen_eor3_inner()` with the standard XOR generator signature: destination, source pointer array, source count, and byte length.

State and persistence: no state; this is an interface header.

Dependencies and integration: included by `arm64/xor-neon.c` and `arm64/xor-neon-glue.c` to keep SIMD instruction bodies separate from SIMD state wrappers.

Risks and test signals: prototype mismatch would be caught by compiler diagnostics. Runtime signals are the same as the arm64 NEON/EOR3 implementation and glue paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/arm64/xor-neon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/arm64/xor_arch.h -->
# sources/distributed-fs/ceph-client/lib/raid/xor/arm64/xor_arch.h

Purpose: defines arm64 XOR algorithm registration.

Important APIs and flow: `arch_xor_init()` registers generic `8regs` and `32regs`; if `cpu_has_neon()` is true, it registers `xor_block_eor3` when the named SHA3 feature is present, otherwise `xor_block_neon`.

State and persistence: only init-time registration state in the XOR core.

Dependencies and integration: depends on `<asm/simd.h>` and arm64 CPU feature helpers. It is included by `xor-core.c` under `CONFIG_XOR_BLOCKS_ARCH`.

Risks and test signals: choosing EOR3 skips registering plain NEON, so SHA3 detection must be reliable. Signals include boot template logs and KUnit XOR validation on arm64 hardware variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/arm64/xor_arch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/loongarch/xor_arch.h -->
# sources/distributed-fs/ceph-client/lib/raid/xor/loongarch/xor_arch.h

Purpose: registers LoongArch XOR implementations, including generic fallbacks and LSX/LASX SIMD candidates.

Important APIs and flow: `arch_xor_init()` always registers `8regs`, `8regs_prefetch`, `32regs`, and `32regs_prefetch`. It conditionally registers `xor_block_lsx` and `xor_block_lasx` when build options and runtime CPU feature flags are available.

State and persistence: no persistent state beyond the core's init-time template list and measured speeds.

Dependencies and integration: depends on `<asm/cpu-features.h>` and templates from `xor_simd_glue.c`.

Risks and test signals: vector templates intentionally participate in calibration instead of being forced because future LoongArch cores may vary. Signals include boot speed comparison, LSX/LASX feature detection, and KUnit parity checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/loongarch/xor_arch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/loongarch/xor_simd.c -->
# sources/distributed-fs/ceph-client/lib/raid/xor/loongarch/xor_simd.c

Purpose: instantiates LoongArch LSX and LASX SIMD XOR assembly loops.

Important APIs and flow: defines a 64-byte `LINE_WIDTH` and macro families for LSX (`vld`, `vst`, `vxor.v`) and LASX (`xvld`, `xvst`, `xvxor.v`). It includes `xor_template.c` twice with `XOR_FUNC_NAME()` mapped to `__xor_lsx_N` or `__xor_lasx_N` so each flavor gets 2 through 5 source helper functions.

State and persistence: no persistent state; vector code mutates destination memory in place.

Dependencies and integration: linked to `xor_simd_glue.c` through declarations in `xor_simd.h`. SIMD instructions must only be called inside the glue's FPU critical section.

Risks and test signals: risks include macro-template drift, vector instruction availability, and assuming 64-byte multiples. Signals include LSX/LASX build coverage, boot calibration, and KUnit randomized XOR correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/loongarch/xor_simd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/loongarch/xor_simd.h -->
# sources/distributed-fs/ceph-client/lib/raid/xor/loongarch/xor_simd.h

Purpose: declares the raw LoongArch SIMD XOR functions implemented by `xor_simd.c`.

Important APIs and flow: under `CONFIG_CPU_HAS_LSX` it declares `__xor_lsx_{2,3,4,5}`; under `CONFIG_CPU_HAS_LASX` it declares `__xor_lasx_{2,3,4,5}`. Each function accepts byte count, destination pointer, and up to four source pointers.

State and persistence: no state; interface-only header.

Dependencies and integration: used by `xor_simd_glue.c` to wrap raw SIMD routines with `DO_XOR_BLOCKS()` and FPU state handling.

Risks and test signals: wrong prototypes would corrupt calling convention. Compiler diagnostics plus KUnit XOR runs on LSX/LASX systems are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/loongarch/xor_simd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/loongarch/xor_simd_glue.c -->
# sources/distributed-fs/ceph-client/lib/raid/xor/loongarch/xor_simd_glue.c

Purpose: publishes LoongArch LSX and LASX raw SIMD routines as safe XOR templates.

Important APIs and flow: `MAKE_XOR_GLUES(flavor)` emits an inner grouped-source generator, a public `xor_gen_flavor()` wrapper around `kernel_fpu_begin()` and `kernel_fpu_end()`, and a `struct xor_block_template`. Enabled flavors are controlled by `CONFIG_CPU_HAS_LSX` and `CONFIG_CPU_HAS_LASX`.

State and persistence: no durable state; it protects CPU FPU/vector state while mutating parity buffers.

Dependencies and integration: depends on `<asm/fpu.h>`, `xor_simd.h`, and the LoongArch registration header.

Risks and test signals: missing FPU bracketing would corrupt task state. Signals include preemption-sensitive stress tests, KUnit XOR coverage, and boot logs measuring `lsx` or `lasx`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/loongarch/xor_simd_glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/loongarch/xor_template.c -->
# sources/distributed-fs/ceph-client/lib/raid/xor/loongarch/xor_template.c

Purpose: provides the macro template used to generate LoongArch SIMD XOR helpers for multiple vector widths.

Important APIs and flow: expected macros define line width, load/store/XOR operations, and function naming. Generated `XOR_FUNC_NAME(2..5)` loops over `bytes / LINE_WIDTH`, loads the destination line, XORs each source line, stores the destination, and advances all pointers by one line.

State and persistence: no persistence; all behavior is in-place memory transformation.

Dependencies and integration: included from `xor_simd.c` after LSX or LASX macro setup.

Risks and test signals: this file is not standalone, so macro contract changes can silently break both SIMD flavors. Signals are LSX/LASX build failures, disassembly inspection, and KUnit parity checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/loongarch/xor_template.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/powerpc/xor_arch.h -->
# sources/distributed-fs/ceph-client/lib/raid/xor/powerpc/xor_arch.h

Purpose: registers PowerPC XOR templates, including generic fallbacks and optional AltiVec.

Important APIs and flow: `arch_xor_init()` registers all four generic scalar templates. With `CONFIG_ALTIVEC` and `CPU_FTR_ALTIVEC`, it also registers `xor_block_altivec` for calibration.

State and persistence: no persistent state beyond the XOR core's template list and selected static call target.

Dependencies and integration: depends on `<asm/cpu_has_feature.h>` and the VMX glue template.

Risks and test signals: risk is CPU feature detection or SIMD-state management in the selected AltiVec path. Signals include boot measurement logs, KUnit, and RAID5 parity workloads on PowerPC AltiVec systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/powerpc/xor_arch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/powerpc/xor_vmx.c -->
# sources/distributed-fs/ceph-client/lib/raid/xor/powerpc/xor_vmx.c

Purpose: implements the raw PowerPC AltiVec XOR inner loop.

Important APIs and flow: uses `vector signed char` as the native vector type. `__xor_altivec_{2,3,4,5}` load four vector registers from each buffer, combine sources with `vec_xor()`, store the destination, and advance by four vectors. `__DO_XOR_BLOCKS()` emits `xor_gen_altivec_inner()`.

State and persistence: no persistence; destination memory changes in place. The caller must have enabled kernel AltiVec.

Dependencies and integration: includes `<altivec.h>` outside sparse checking and exports the inner function declared by `xor_vmx.h`; `xor_vmx_glue.c` wraps it.

Risks and test signals: risks include AltiVec ABI/compiler issues and vector-state use outside the critical section. Signals are PowerPC build/sparse coverage, KUnit XOR tests, and boot calibration output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/powerpc/xor_vmx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/powerpc/xor_vmx.h -->
# sources/distributed-fs/ceph-client/lib/raid/xor/powerpc/xor_vmx.h

Purpose: provides the small interface between PowerPC AltiVec implementation and glue files.

Important APIs and flow: declares `xor_gen_altivec_inner()` with the common XOR generator signature.

State and persistence: no state.

Dependencies and integration: included by `xor_vmx.c` and `xor_vmx_glue.c` to enforce separation between vector instruction implementation and vector-state enabling.

Risks and test signals: prototype mismatch is the main local risk; compile coverage catches it, while KUnit validates runtime behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/powerpc/xor_vmx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/powerpc/xor_vmx_glue.c -->
# sources/distributed-fs/ceph-client/lib/raid/xor/powerpc/xor_vmx_glue.c

Purpose: wraps PowerPC AltiVec XOR in safe kernel vector-state handling and publishes the `altivec` template.

Important APIs and flow: `xor_gen_altivec()` disables preemption, enables kernel AltiVec, calls `xor_gen_altivec_inner()`, disables AltiVec, then re-enables preemption. `xor_block_altivec` exposes the function to the XOR core.

State and persistence: no durable state; it temporarily changes CPU vector-state ownership.

Dependencies and integration: depends on `<asm/switch_to.h>` and the PowerPC registration header.

Risks and test signals: preemption and vector state bracketing are critical. Signals include KUnit under preemptible kernels, RAID workloads, and absence of vector-state corruption warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/powerpc/xor_vmx_glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/riscv/xor-glue.c -->
# sources/distributed-fs/ceph-client/lib/raid/xor/riscv/xor-glue.c

Purpose: exposes RISC-V vector assembly XOR helpers as a safe XOR template.

Important APIs and flow: `DO_XOR_BLOCKS(vector_inner, xor_regs_2_, xor_regs_3_, xor_regs_4_, xor_regs_5_)` builds an inner generator. `xor_gen_vector()` wraps it with `kernel_vector_begin()` and `kernel_vector_end()`. `xor_block_rvv` registers template name `rvv`.

State and persistence: no persistent state; only vector context bracketing and destination mutation.

Dependencies and integration: depends on RISC-V vector switch helpers, assembly prototypes, `xor.S`, and `riscv/xor_arch.h`.

Risks and test signals: vector state handling and runtime feature gating are critical. Signals include RISC-V vector build coverage, KUnit XOR tests, and boot calibration choosing `rvv`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/riscv/xor-glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/riscv/xor.S -->
# sources/distributed-fs/ceph-client/lib/raid/xor/riscv/xor.S

Purpose: implements raw RISC-V vector XOR loops for 2 through 5 operand cases.

Important APIs and flow: exports `xor_regs_2_`, `xor_regs_3_`, `xor_regs_4_`, and `xor_regs_5_`. Each loop uses `vsetvli` with byte elements, vector-loads destination and sources, performs chained `vxor.vv`, vector-stores the destination, advances pointers by the selected vector length, and repeats until all bytes are consumed.

State and persistence: no persistence; destination buffer is updated in place. Vector context ownership is handled by the C glue.

Dependencies and integration: called by `riscv/xor-glue.c` and declared through architecture assembly prototypes.

Risks and test signals: risks include incorrect ABI register usage, varying vector length handling, and missing vector feature gating. Signals include assembly build coverage, KUnit randomized XOR tests, and hardware parity stress on RVV systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/riscv/xor.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/riscv/xor_arch.h -->
# sources/distributed-fs/ceph-client/lib/raid/xor/riscv/xor_arch.h

Purpose: registers RISC-V XOR templates.

Important APIs and flow: `arch_xor_init()` registers generic `8regs` and `32regs`. With `CONFIG_RISCV_ISA_V` and `has_vector()`, it also registers `xor_block_rvv`.

State and persistence: only init-time template registration and later selected template speed.

Dependencies and integration: depends on `<asm/vector.h>` and `xor-glue.c`.

Risks and test signals: feature probing determines whether RVV participates in calibration. Signals include boot logs, KUnit, and RISC-V vector enable/disable config tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/riscv/xor_arch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/s390/xor.c -->
# sources/distributed-fs/ceph-client/lib/raid/xor/s390/xor.c

Purpose: implements the s390 optimized XOR template using the `xc` instruction.

Important APIs and flow: `xor_xc_{2,3,4,5}` use inline assembly to process 256-byte blocks with `xc`, then handle a remaining byte count through `exrl`. `DO_XOR_BLOCKS(xc, ...)` emits `xor_gen_xc()`, and `xor_block_xc` exposes the template.

State and persistence: no persistence; destination bytes are XORed in place.

Dependencies and integration: `s390/xor_arch.h` forces this template, bypassing generic calibration.

Risks and test signals: risks include inline assembly length handling and forced selection on all s390 builds. Signals include KUnit XOR tests, RAID parity verification, and boot logs showing the forced `xc` template.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/s390/xor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/s390/xor_arch.h -->
# sources/distributed-fs/ceph-client/lib/raid/xor/s390/xor_arch.h

Purpose: defines s390 XOR selection policy.

Important APIs and flow: declares `xor_block_xc`; `arch_xor_init()` calls `xor_force(&xor_block_xc)`, making the core use the s390 `xc` implementation without measuring alternatives.

State and persistence: sets the XOR core forced-template pointer during initialization.

Dependencies and integration: included by `xor-core.c` when architecture XOR blocks are configured.

Risks and test signals: forced selection assumes `xc` is universally preferable and correct. Signals include boot template message, KUnit, and s390 RAID parity tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/s390/xor_arch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/sparc/xor-sparc32.c -->
# sources/distributed-fs/ceph-client/lib/raid/xor/sparc/xor-sparc32.c

Purpose: provides SPARC 32-bit optimized XOR using doubleword load/store instructions.

Important APIs and flow: `sparc_{2,3,4,5}` loop over eight `long` words, load destination/source blocks with `ldd`, apply register XOR chains, store with `std`, and advance pointers. `DO_XOR_BLOCKS(sparc32, ...)` emits `xor_gen_sparc32()`, exported through `xor_block_SPARC`.

State and persistence: no persistent state; destination buffers are mutated.

Dependencies and integration: registered by `sparc/xor_arch.h` on non-sparc64 builds alongside generic templates.

Risks and test signals: inline assembly clobber lists and alignment are the main risks. Signals include sparc32 build tests, boot calibration, and KUnit XOR correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/sparc/xor-sparc32.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/sparc/xor-sparc64-glue.c -->
# sources/distributed-fs/ceph-client/lib/raid/xor/sparc/xor-sparc64-glue.c

Purpose: publishes SPARC64 VIS and Niagara assembly XOR functions as core XOR templates.

Important APIs and flow: declares `xor_vis_{2,3,4,5}` and `xor_niagara_{2,3,4,5}` implemented in assembly. `DO_XOR_BLOCKS()` creates `xor_gen_vis()` and `xor_gen_niagara()`, exposed as `xor_block_VIS` and `xor_block_niagara`.

State and persistence: no persistence; selection is handled by `sparc/xor_arch.h`.

Dependencies and integration: depends on `xor-sparc64.S` for implementation and on SPARC architecture detection to force the proper template.

Risks and test signals: mismatch between glue prototypes and assembly ABI would be severe. Signals include sparc64 build/link coverage, boot forced-template logs, and RAID/KUnit parity checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/sparc/xor-sparc64-glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/sparc/xor-sparc64.S -->
# sources/distributed-fs/ceph-client/lib/raid/xor/sparc/xor-sparc64.S

Purpose: implements SPARC64 high-speed XOR routines using VIS floating/vector registers and Niagara block operations.

Important APIs and flow: exports `xor_vis_{2,3,4,5}` and Niagara variants. VIS functions enter VIS state if needed, switch ASI to block primary, use `ldda` and `stda` plus `fxor` over 64-byte or 128-byte blocks, issue memory barriers, restore ASI/FPRS, and return.

State and persistence: no durable state; it temporarily changes FPRS and ASI and must restore them before return. Destination memory is updated.

Dependencies and integration: included through `xor-sparc64-glue.c`; selection is forced by `sparc/xor_arch.h` based on `tlb_type` and `sun4v_chip_type`.

Risks and test signals: risks include strict alignment/length requirements, VIS state handling, ASI restoration, and Niagara CPU classification. Signals include sparc64 boot logs, KUnit XOR tests, and RAID parity stress on VIS and Niagara machines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/sparc/xor-sparc64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/sparc/xor_arch.h -->
# sources/distributed-fs/ceph-client/lib/raid/xor/sparc/xor_arch.h

Purpose: defines SPARC XOR registration and forced selection policy.

Important APIs and flow: on sparc64, `arch_xor_init()` forces `xor_block_niagara` for hypervisor Niagara chip types and otherwise forces `xor_block_VIS`. On 32-bit SPARC it registers generic `8regs`, `32regs`, and `xor_block_SPARC`.

State and persistence: forced-template state is stored in the XOR core during init.

Dependencies and integration: sparc64 path depends on `<asm/spitfire.h>` global CPU type data; 32-bit path depends on `xor-sparc32.c`.

Risks and test signals: forced selection relies on CPU-type detection and assembly requirements. Signals include boot logs, KUnit, and parity workloads on sun4v Niagara and non-Niagara SPARC64 systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/sparc/xor_arch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/tests/Makefile -->
# sources/distributed-fs/ceph-client/lib/raid/xor/tests/Makefile

Purpose: builds the XOR KUnit test module.

Important APIs and flow: adds `xor_kunit.o` to the build when `CONFIG_XOR_KUNIT_TEST` is enabled.

State and persistence: no runtime state here; it controls build inclusion.

Dependencies and integration: integrated into Kbuild under the XOR library test directory.

Risks and test signals: local risk is only config wiring. The test signal is the `xor` KUnit suite appearing and running when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/tests/xor_kunit.c -->
# sources/distributed-fs/ceph-client/lib/raid/xor/tests/xor_kunit.c

Purpose: unit-tests the exported `xor_gen()` API against a bytewise reference implementation.

Important APIs and flow: fixed seed `XOR_KUNIT_SEED` makes randomized tests repeatable. Suite init allocates guard-page-backed `vmalloc()` buffers, fills destination/reference/source data, then `xor_test()` runs 1000 iterations with random source counts up to 64, 512-byte-multiple lengths up to 16 KiB, random 64-byte alignments, and end-of-buffer placements. It compares `xor_ref()` and `xor_gen()` with `KUNIT_EXPECT_MEMEQ_MSG()`.

State and persistence: module-global buffers and PRNG state live for the suite and are released in `xor_suite_exit()`. No persistent state.

Dependencies and integration: depends on KUnit, `prandom`, `vmalloc`, `linux/raid/xor.h`, and the selected XOR implementation behind `xor_gen()`.

Risks and test signals: this is the primary regression signal for generic and architecture XOR routines, especially buffer overreads and multi-source dispatch. It does not exhaustively test every CPU feature path unless run on those architectures/configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/tests/xor_kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/um/xor_arch.h -->
# sources/distributed-fs/ceph-client/lib/raid/xor/um/xor_arch.h

Purpose: reuses x86 XOR registration for User Mode Linux builds.

Important APIs and flow: includes `<../x86/xor_arch.h>`, so UML inherits the x86 architecture XOR selection definitions.

State and persistence: no state.

Dependencies and integration: depends on the x86 XOR header being suitable for the UML include context.

Risks and test signals: risk is include-path or feature-helper incompatibility between UML and native x86. Signals include UML builds with XOR blocks enabled and KUnit XOR execution in UML.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/um/xor_arch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/x86/xor-avx.c -->
# sources/distributed-fs/ceph-client/lib/raid/xor/x86/xor-avx.c

Purpose: implements AVX-accelerated x86 XOR parity generation.

Important APIs and flow: `xor_avx_{2,3,4,5}` process 512-byte units using sixteen 32-byte YMM blocks. Each block loads the highest-numbered source, XORs lower sources and destination with `vxorps`, stores back with `vmovdqa`, and advances pointers. `DO_XOR_BLOCKS(avx_inner, ...)` builds grouped-source dispatch, and `xor_gen_avx()` wraps it in `kernel_fpu_begin/end`. `xor_block_avx` is the published template.

State and persistence: no persistence; in-place destination mutation plus temporary FPU state ownership.

Dependencies and integration: x86 selection forces this template when AVX and OSXSAVE are present.

Risks and test signals: risks are AVX state handling, alignment, and forcing without calibration. Signals include boot selection logs, KUnit XOR tests on AVX systems, and RAID parity stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/x86/xor-avx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/x86/xor-mmx.c -->
# sources/distributed-fs/ceph-client/lib/raid/xor/x86/xor-mmx.c

Purpose: implements legacy x86 MMX XOR templates for Pentium II and Pentium-style scheduling.

Important APIs and flow: `xor_pII_mmx_{2,3,4,5}` process 128-byte chunks with macro-expanded `movq` and `pxor`. `xor_p5_mmx_{2,3,4,5}` process 64-byte chunks with a different instruction schedule. Both sets use `DO_XOR_BLOCKS()` and wrappers `xor_gen_pII_mmx()` and `xor_gen_p5_mmx()` inside `kernel_fpu_begin/end`.

State and persistence: no durable state; MMX/FPU state is temporarily owned and destination memory is mutated.

Dependencies and integration: registered by `x86/xor_arch.h` only when MMX exists and SSE/AVX choices are unavailable.

Risks and test signals: risks include old inline assembly constraints, operand-register limits, and FPU state cleanup. Signals include x86 32-bit build coverage, KUnit XOR tests on legacy configs, and boot calibration output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/x86/xor-mmx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/x86/xor-sse.c -->
# sources/distributed-fs/ceph-client/lib/raid/xor/x86/xor-sse.c

Purpose: implements SSE and prefetch64-SSE XOR templates for x86.

Important APIs and flow: `xor_sse_{2,3,4,5}` and `xor_sse_{2,3,4,5}_pf64` process 256-byte chunks using `movaps`, `xorps`, and `prefetchnta`, with macro-expanded schedules for each source count. `DO_XOR_BLOCKS()` creates `xor_gen_sse_inner()` and `xor_gen_sse_pf64_inner()`, wrapped with `kernel_fpu_begin/end` and exported as `xor_block_sse` and `xor_block_sse_pf64`.

State and persistence: no persistence; in-place destination mutation and temporary FPU/SSE state ownership.

Dependencies and integration: registered by x86 selection on x86-64 or XMM-capable 32-bit CPUs when AVX is not forced.

Risks and test signals: risks include alignment assumptions for `movaps`, prefetch behavior, and register constraints across 32/64-bit modes. Signals include KUnit XOR tests, boot calibration comparing SSE variants, and RAID parity workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/x86/xor-sse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/x86/xor_arch.h -->
# sources/distributed-fs/ceph-client/lib/raid/xor/x86/xor_arch.h

Purpose: defines x86 XOR implementation selection.

Important APIs and flow: `arch_xor_init()` forces `xor_block_avx` if AVX and OSXSAVE are available. Otherwise it registers SSE variants on x86-64 or XMM-capable x86, MMX variants on MMX-only CPUs, and generic scalar fallbacks when no SIMD path is available.

State and persistence: uses XOR core forced-template state for AVX, or registration list for measured selection of other candidates.

Dependencies and integration: depends on x86 CPU feature helpers and templates from AVX, SSE, MMX, and generic files.

Risks and test signals: AVX is forced without benchmarking, and SIMD availability must match kernel FPU save support. Signals include boot logs, KUnit, and CPU feature matrix boot tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/x86/xor_arch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/xor-32regs-prefetch.c -->
# sources/distributed-fs/ceph-client/lib/raid/xor/xor-32regs-prefetch.c

Purpose: generic scalar XOR implementation that uses register temporaries and software prefetch.

Important APIs and flow: `xor_32regs_p_{2,3,4,5}` prefetch destination and source lines, load eight `long` values into locals, XOR requested sources, write back, and use a `once_more` tail pattern because the loop prefetches one line ahead. `DO_XOR_BLOCKS()` emits `xor_gen_32regs_p()`, exposed as `xor_block_32regs_p`.

State and persistence: no persistence; mutates destination in place.

Dependencies and integration: depends on `<linux/prefetch.h>` and `xor_impl.h`; registered by generic and several architecture init paths.

Risks and test signals: risks include off-by-one loop handling and prefetching near guard pages. The KUnit test's end-of-buffer placement is a key overread signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/xor-32regs-prefetch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/xor-32regs.c -->
# sources/distributed-fs/ceph-client/lib/raid/xor/xor-32regs.c

Purpose: generic scalar XOR template optimized around explicit register temporaries.

Important APIs and flow: `xor_32regs_{2,3,4,5}` process eight `long` values per iteration. They load destination words into locals, XOR source words according to operand count, store back, and advance pointers. `DO_XOR_BLOCKS()` builds `xor_gen_32regs()`.

State and persistence: no persistent state; destination is mutated.

Dependencies and integration: core generic template exported as `xor_block_32regs` for fallback and calibration.

Risks and test signals: assumes byte counts are suitable for eight-`long` loop granularity, which is satisfied by the public `xor_gen()` contract. Signals include KUnit randomized length/source tests and boot calibration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/xor-32regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/xor-8regs-prefetch.c -->
# sources/distributed-fs/ceph-client/lib/raid/xor/xor-8regs-prefetch.c

Purpose: generic scalar XOR template using direct memory XORs plus prefetch.

Important APIs and flow: `xor_8regs_p_{2,3,4,5}` process eight `long` words per line, prefetch destination/source pointers one line ahead, and use a `once_more` label to process the final line after the prefetch loop. `DO_XOR_BLOCKS()` exposes `xor_gen_8regs_p()`.

State and persistence: no persistence; in-place destination mutation.

Dependencies and integration: depends on `linux/prefetch.h` and is registered as `xor_block_8regs_p`.

Risks and test signals: risks are tail-loop correctness and prefetch safety at page ends. KUnit guard-page tests and boot speed calibration are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/xor-8regs-prefetch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/xor-8regs.c -->
# sources/distributed-fs/ceph-client/lib/raid/xor/xor-8regs.c

Purpose: simplest generic scalar XOR template.

Important APIs and flow: `xor_8regs_{2,3,4,5}` process eight `long` words per iteration and directly apply `p1[i] ^= p2[i] ...`. `DO_XOR_BLOCKS()` emits `xor_gen_8regs()` unless `NO_TEMPLATE` is defined; ARM NEON reuses the helper bodies with `NO_TEMPLATE`.

State and persistence: no persistence; destination is updated in place.

Dependencies and integration: exported as `xor_block_8regs` for generic fallback and architecture calibration.

Risks and test signals: low complexity, but public contract still requires aligned buffers and 512-byte-multiple lengths. Signals include KUnit, boot calibration, and use as fallback when architecture SIMD is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/xor-8regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/xor-core.c -->
# sources/distributed-fs/ceph-client/lib/raid/xor/xor-core.c

Purpose: central dispatcher and selector for RAID5-style XOR parity functions.

Important APIs and flow: exported `xor_gen()` validates task context, nonzero 512-byte-multiple length, then invokes the selected function through `static_call(xor_gen_impl)`. `xor_register()` adds templates to an init-time list; `xor_force()` sets a forced template. `calibrate_xor_blocks()` allocates benchmark pages, times each registered template over `BENCH_SIZE` and `REPS`, records `speed`, and updates the static call to the fastest. `xor_init()` invokes `arch_xor_init()`, handles forced selection, and chooses either early default or module-time calibration.

State and persistence: global static call target is runtime process state. `template_list` is init data, `forced_template` may persist after init, and template speed fields are filled by calibration.

Dependencies and integration: depends on module/init APIs, jiffies/ktime/preemption, static calls, and architecture `xor_arch.h` when configured. Consumers call `linux/raid/xor.h`.

Risks and test signals: wrong dispatch affects RAID5 parity globally. Risks include empty template list, calibration timing instability, and context restrictions. Signals include boot logs, KUnit `xor` suite, and module/built-in init ordering tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/xor-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/xor_impl.h -->
# sources/distributed-fs/ceph-client/lib/raid/xor/xor_impl.h

Purpose: defines the common template ABI and wrapper macros for XOR implementations.

Important APIs and flow: `struct xor_block_template` carries linked-list pointer, name, measured speed, and `xor_gen` function pointer. `__DO_XOR_BLOCKS()` creates a public generator that consumes any `src_cnt` by chunking sources into groups of up to four and dispatching to 2 through 5-buffer handlers, where the destination is counted as the first operand. `DO_XOR_BLOCKS()` makes the generator static. It declares generic templates and registration functions.

State and persistence: the struct carries mutable `speed` and `next` fields during init/calibration.

Dependencies and integration: included by every XOR implementation and `xor-core.c`.

Risks and test signals: macro dispatch must preserve source ordering and handle source counts greater than four. KUnit randomized source counts up to 64 directly exercise this behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid/xor/xor_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/Makefile -->
# sources/distributed-fs/ceph-client/lib/raid6/Makefile

Purpose: builds the RAID6 P/Q library and generates architecture-specific unrolled sources and lookup tables.

Important APIs and flow: `raid6_pq-y` includes algorithm selection, recovery, generated tables, and integer unrolls. Conditional object lists add x86, AltiVec, NEON, s390, LoongArch, and RISC-V implementations. `mktables` is a host program that emits `tables.c`; `unroll.awk` turns `.uc` templates into `intN`, `altivecN`, `vpermxorN`, `neonN`, and `s390vxN` sources. It also manages required compiler flags for AltiVec and NEON/FPU objects.

State and persistence: build-system state only; generated C files are build artifacts.

Dependencies and integration: Kbuild, host tools, architecture configs, and compiler feature flags.

Risks and test signals: risks include wrong FPU flags causing SIMD instructions outside wrappers or failed generated-source dependencies. Signals are all-architecture build coverage and RAID6 test programs/KUnit equivalents where present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/algos.c -->
# sources/distributed-fs/ceph-client/lib/raid6/algos.c

Purpose: owns RAID6 syndrome and recovery algorithm selection.

Important APIs and flow: exports global `raid6_call`, `raid6_2data_recov`, and `raid6_datap_recov`. `raid6_algos[]` lists generation implementations by architecture and fallback integer routines. `raid6_recov_algos[]` lists recovery implementations. `raid6_choose_gen()` selects the first valid highest-priority algorithm unless `CONFIG_RAID6_PQ_BENCHMARK` measures throughput, then stores `raid6_call`. `raid6_choose_recov()` picks the highest-priority valid recovery implementation and installs global function pointers. `raid6_select_algo()` allocates pages, seeds test data from `raid6_gfmul`, runs both selectors, frees pages, and is called at `subsys_initcall`.

State and persistence: runtime global dispatch state lives in `raid6_call` and recovery function pointers. No filesystem persistence.

Dependencies and integration: depends on `linux/raid/pq.h`, generated GF tables, jiffies/preemption for benchmarking, and architecture validity callbacks.

Risks and test signals: global selection affects all RAID6 users. Risks include priority mistakes, invalid CPU feature checks, and disabled benchmarking selecting a suboptimal first candidate. Signals include boot logs for selected gen/recovery algorithms, RAID6 recovery tests, and architecture feature matrix boots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/algos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/avx2.c -->
# sources/distributed-fs/ceph-client/lib/raid6/avx2.c

Purpose: implements x86 AVX2 RAID6 syndrome generation and read-modify-write syndrome update.

Important APIs and flow: `raid6_have_avx2()` checks AVX2 and AVX. `raid6_avx21_*`, `raid6_avx22_*`, and x86-64 `raid6_avx24_*` process 32, 64, or 128 bytes per outer iteration. Generation computes P as XOR of data and Q as GF(2^8) multiply-by-2 recurrence using `0x1d` reduction. `xor_syndrome` updates P/Q over a data subrange with left-side Q advancement. Published `raid6_avx2x1/x2/x4` structures have priority 2.

State and persistence: no durable state; it mutates P and Q buffers and temporarily owns FPU/AVX state.

Dependencies and integration: depends on `x86.h`, boot CPU feature checks, `kernel_fpu_begin/end`, and `raid6_algos[]`.

Risks and test signals: risks include alignment, byte-count multiples, AVX state handling, and GF recurrence errors. Signals are RAID6 boot selection logs, parity-generation tests, recovery tests using AVX2-generated syndromes, and x86-64 versus 32-bit coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/avx2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/avx512.c -->
# sources/distributed-fs/ceph-client/lib/raid6/avx512.c

Purpose: implements x86 AVX512 RAID6 syndrome generation and xor-syndrome update.

Important APIs and flow: `raid6_have_avx512()` requires AVX2, AVX, AVX512F, BW, VL, and DQ. `raid6_avx512{1,2,4}_gen_syndrome()` and matching xor functions operate on 64, 128, or 256 bytes per iteration using ZMM registers, mask compares, byte shifts, `0x1d` reduction, and non-temporal stores for generated P/Q. Published structures have priority 2.

State and persistence: no persistence; mutates P/Q buffers and temporarily owns wide vector state.

Dependencies and integration: depends on x86 FPU APIs, feature detection, and `raid6_algos[]`.

Risks and test signals: AVX512 state, downclock/performance tradeoffs, alignment, and feature gating are key risks. Signals include boot algorithm logs, RAID6 parity tests on AVX512 hardware, and fallback behavior when any required AVX512 subfeature is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/avx512.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/loongarch.h -->
# sources/distributed-fs/ceph-client/lib/raid6/loongarch.h

Purpose: provides shared LoongArch RAID6 SIMD definitions for kernel and userspace test builds.

Important APIs and flow: in-kernel builds include CPU feature and FPU helpers. Userspace builds define HWCAP values if needed, no-op `kernel_fpu_begin/end`, and map `cpu_has_lsx/lasx` to `getauxval(AT_HWCAP)`.

State and persistence: no persistent state.

Dependencies and integration: included by LoongArch syndrome and recovery SIMD files.

Risks and test signals: userspace compatibility macros must match kernel feature semantics. Signals include kernel builds and standalone RAID6 test builds on glibc/musl LoongArch systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/loongarch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/loongarch_simd.c -->
# sources/distributed-fs/ceph-client/lib/raid6/loongarch_simd.c

Purpose: implements LoongArch LSX and LASX RAID6 syndrome generation and xor-syndrome update.

Important APIs and flow: LSX uses 16-byte vectors four at a time; LASX uses 32-byte vectors two at a time. `raid6_lsx_gen_syndrome()` and `raid6_lasx_gen_syndrome()` compute P and Q with vector XOR, byte shift, sign-mask, and `0x1d` reduction. `*_xor_syndrome()` updates a P/Q range and advances Q through left-side data positions. Published `raid6_lsx` and `raid6_lasx` have priority 0 so scalar algorithms remain competitive unless benchmarking chooses SIMD.

State and persistence: no persistence; mutates P/Q and temporarily owns LoongArch FPU/vector state.

Dependencies and integration: depends on `loongarch.h`, CPU feature flags, and `raid6_algos[]`.

Risks and test signals: risks include vector feature gating, priority policy, and GF recurrence correctness. Signals include boot selection logs, LoongArch RAID6 parity tests, and LSX/LASX userspace test builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/loongarch_simd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/mktables.c -->
# sources/distributed-fs/ceph-client/lib/raid6/mktables.c

Purpose: host build tool that generates RAID6 Galois-field lookup tables.

Important APIs and flow: `gfmul()` implements GF(2^8) multiply with polynomial `0x1d`; `gfpow()` exponentiates using repeated squaring. `main()` prints C definitions for `raid6_gfmul`, nibble-vector `raid6_vgfmul`, `raid6_gfexp`, `raid6_gflog`, `raid6_gfinv`, and `raid6_gfexi`, plus kernel export directives.

State and persistence: output is generated source `tables.c` during the build; no runtime state in this tool.

Dependencies and integration: invoked by the RAID6 Makefile as a host program, and generated tables are used by scalar and SIMD recovery.

Risks and test signals: a table-generation error corrupts all RAID6 recovery math. Signals include deterministic generated output, RAID6 test vectors, and recovery tests for all failure positions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/mktables.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/mmx.c -->
# sources/distributed-fs/ceph-client/lib/raid6/mmx.c

Purpose: provides 32-bit x86 MMX RAID6 syndrome generation.

Important APIs and flow: compiled only under `CONFIG_X86_32`. `raid6_have_mmx()` checks MMX. `raid6_mmx1_gen_syndrome()` processes 8 bytes per iteration; `raid6_mmx2_gen_syndrome()` processes 16 bytes. Both compute P and Q in MMX registers using `0x1d` reduction and publish `raid6_mmxx1`/`raid6_mmxx2`. `xor_syndrome` is not implemented for these structures.

State and persistence: no persistence; mutates P/Q and uses `kernel_fpu_begin/end`.

Dependencies and integration: depends on x86 FPU APIs, generated constants shared with SSE1, and `raid6_algos[]`.

Risks and test signals: legacy inline assembly and missing xor-syndrome support are the main caveats. Signals include i386 build tests, boot algorithm logs, and RAID6 parity validation on MMX-capable 32-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/mmx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/neon.c -->
# sources/distributed-fs/ceph-client/lib/raid6/neon.c

Purpose: wraps generated ARM NEON RAID6 syndrome functions in safe kernel SIMD sections.

Important APIs and flow: `RAID6_NEON_WRAPPER(n)` creates generation and xor-syndrome wrappers for `n` equal to 1, 2, 4, and 8. Each wrapper calls generated `raid6_neonN_*_real()` inside `scoped_ksimd()` and publishes `raid6_neonxN` with `raid6_have_neon()`.

State and persistence: no persistence; wrappers protect SIMD state while real implementations mutate P/Q.

Dependencies and integration: generated `neonN.c` files from `neon.uc`, ARM SIMD helpers, and `raid6_algos[]`.

Risks and test signals: separation prevents NEON instructions outside the critical section. Signals include ARM/arm64 NEON builds, boot algorithm selection, and RAID6 parity tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/neon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/neon.h -->
# sources/distributed-fs/ceph-client/lib/raid6/neon.h

Purpose: declares ARM NEON RAID6 generated syndrome and recovery helper functions.

Important APIs and flow: declares `raid6_neon{1,2,4,8}_gen_syndrome_real()` and `raid6_neon{1,2,4,8}_xor_syndrome_real()` plus low-level recovery helpers `__raid6_2data_recov_neon()` and `__raid6_datap_recov_neon()`.

State and persistence: no state; interface only.

Dependencies and integration: shared by NEON wrappers and NEON inner recovery implementation.

Risks and test signals: prototype mismatch would break compilation or corrupt calls. Signals include NEON build coverage and RAID6 parity/recovery tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/neon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/recov.c -->
# sources/distributed-fs/ceph-client/lib/raid6/recov.c

Purpose: implements scalar fallback RAID6 recovery for two failed data blocks or one data block plus P.

Important APIs and flow: `raid6_2data_recov_intx1()` temporarily replaces failed data pointers with zero pages and P/Q pointers with failed buffers, regenerates syndromes to get deltas, restores `ptrs`, picks `pbmul` and `qmul`, then reconstructs both data blocks byte by byte. `raid6_datap_recov_intx1()` follows the same pattern for data+P failure and updates P. `raid6_recov_intx1` exposes priority 0 fallback. Userspace-only `raid6_dual_recov()` dispatches failure cases for tests.

State and persistence: mutates caller-provided data/parity buffers and temporarily mutates the `ptrs` array, restoring it before returning.

Dependencies and integration: depends on selected `raid6_call.gen_syndrome`, GF tables, and zero-page helper.

Risks and test signals: temporary pointer rewriting must be restored exactly, and failure indexes drive GF table selection. Signals include RAID6 recovery tests over all disk positions and fallback selection logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/recov.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/recov_avx2.c -->
# sources/distributed-fs/ceph-client/lib/raid6/recov_avx2.c

Purpose: implements AVX2-accelerated RAID6 recovery.

Important APIs and flow: after the same syndrome-delta setup as scalar recovery, `raid6_2data_recov_avx2()` uses `raid6_vgfmul` nibble tables with `vpshufb` to compute Q multipliers and P multipliers over 32-byte or 64-byte chunks, reconstructing both failed data blocks. `raid6_datap_recov_avx2()` reconstructs one data block and updates P. `raid6_recov_avx2` has priority 2 and valid callback `raid6_has_avx2()`.

State and persistence: temporarily mutates `ptrs`, restores it, mutates failed buffers/P, and owns AVX state inside `kernel_fpu_begin/end`.

Dependencies and integration: depends on selected `raid6_call.gen_syndrome`, vector GF tables, x86 FPU APIs, and recovery selector.

Risks and test signals: risks include vector table indexing, 32/64-bit chunk differences, and AVX feature gating. Signals include RAID6 recovery tests on AVX2 hardware and boot recovery algorithm logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/recov_avx2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/recov_avx512.c -->
# sources/distributed-fs/ceph-client/lib/raid6/recov_avx512.c

Purpose: implements AVX512-accelerated RAID6 recovery with widest x86 vector path.

Important APIs and flow: `raid6_has_avx512()` checks AVX2, AVX, and AVX512F/BW/VL/DQ. Recovery setup mirrors scalar code, then ZMM code uses `vpshufb` against nibble GF tables to compute reconstructed blocks in 64-byte or 128-byte chunks. `raid6_recov_avx512` has priority 3, above AVX2.

State and persistence: temporary `ptrs` mutation is restored; failed data/P buffers are updated; vector state is bracketed with `kernel_fpu_begin/end`.

Dependencies and integration: depends on `raid6_call.gen_syndrome`, vector GF tables, x86 feature checks, and the recovery selector.

Risks and test signals: wide-vector state, alignment, feature gating, and table math are key risks. Signals include recovery tests on AVX512 systems, boot logs selecting `avx512x2/x1`, and fallback when features are missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/recov_avx512.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/recov_loongarch_simd.c -->
# sources/distributed-fs/ceph-client/lib/raid6/recov_loongarch_simd.c

Purpose: implements LSX and LASX RAID6 recovery for LoongArch.

Important APIs and flow: LSX and LASX recovery first compute syndrome deltas through `raid6_call.gen_syndrome`, restore `ptrs`, then use `raid6_vgfmul` nibble tables and vector shuffle instructions to compute two-data or data+P reconstruction. LSX publishes priority 1; LASX publishes priority 2 because recovery selection is priority-only rather than benchmarked.

State and persistence: temporarily mutates and restores `ptrs`; mutates failed data and P buffers; wraps vector work in `kernel_fpu_begin/end`.

Dependencies and integration: depends on `loongarch.h`, GF vector tables, selected syndrome generator, and `raid6_recov_algos[]`.

Risks and test signals: priorities assume future LASX is not slower than LSX, unlike syndrome generation. Signals include LoongArch recovery tests, CPU feature gating, and boot logs selecting `lsx` or `lasx`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/recov_loongarch_simd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/recov_neon.c -->
# sources/distributed-fs/ceph-client/lib/raid6/recov_neon.c

Purpose: wraps ARM NEON RAID6 recovery helpers in SIMD-safe sections and publishes the recovery algorithm.

Important APIs and flow: `raid6_2data_recov_neon()` and `raid6_datap_recov_neon()` perform the standard zero-page syndrome-delta setup, restore `ptrs`, choose vector GF tables, then call `__raid6_2data_recov_neon()` or `__raid6_datap_recov_neon()` inside `scoped_ksimd()`. `raid6_recov_neon` has priority 10.

State and persistence: temporarily mutates `ptrs`, restores it, and updates failed data/P buffers. SIMD state is scoped.

Dependencies and integration: depends on `neon.h`, `raid6_call.gen_syndrome`, GF vector tables, and ARM SIMD support.

Risks and test signals: high priority makes NEON preferred when available, so correctness and SIMD gating are critical. Signals include recovery tests on NEON-capable ARM systems and boot recovery algorithm logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/recov_neon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/recov_neon_inner.c -->
# sources/distributed-fs/ceph-client/lib/raid6/recov_neon_inner.c

Purpose: contains the actual ARM NEON RAID6 recovery vector math.

Important APIs and flow: for AArch32, supplies `vqtbl1q_u8()` using two 64-bit table lookups. `__raid6_2data_recov_neon()` loads pbmul/qmul low and high nibble tables, computes `px = p ^ dp`, `qx = qmul[q ^ dq]`, `db = pbmul[px] ^ qx`, stores reconstructed B in `dq` and A in `dp`. `__raid6_datap_recov_neon()` computes `dq = qmul[q ^ dq]` and updates P. Both process 16 bytes per loop.

State and persistence: no durable state; mutates recovery buffers passed by the wrapper. SIMD ownership is handled by the caller.

Dependencies and integration: depends on `<arm_neon.h>` and declarations in `neon.h`.

Risks and test signals: table lookup portability between AArch32 and AArch64 and exact GF nibble math are risks. Signals include NEON recovery tests and build coverage for both ARM modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/recov_neon_inner.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/recov_rvv.c -->
# sources/distributed-fs/ceph-client/lib/raid6/recov_rvv.c

Purpose: implements RISC-V vector RAID6 recovery.

Important APIs and flow: internal helpers set vector length to 16 bytes and use RVV loads, XORs, shifts, masks, and `vrgather.vv` table lookups against qmul/pbmul nibbles. Public `raid6_2data_recov_rvv()` and `raid6_datap_recov_rvv()` do standard syndrome-delta setup, restore `ptrs`, then call helpers inside `kernel_vector_begin/end`. `raid6_recov_rvv` has priority 1 and valid callback `rvv_has_vector`.

State and persistence: temporary `ptrs` mutation is restored; failed buffers and P are updated; vector state is scoped.

Dependencies and integration: depends on `rvv.h`, selected syndrome generator, GF vector tables, and recovery selection.

Risks and test signals: risks include fixed 16-byte vector length assumptions, inline assembly constraints, and vector feature gating. Signals include RISC-V vector recovery tests and boot recovery algorithm logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/recov_rvv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/recov_s390xc.c -->
# sources/distributed-fs/ceph-client/lib/raid6/recov_s390xc.c

Purpose: implements s390 RAID6 recovery using the `xc` instruction for block XOR acceleration.

Important APIs and flow: `xor_block()` applies `xc` over 256 bytes. `raid6_2data_recov_s390xc()` performs standard syndrome-delta setup, XORs deltas with P/Q in 256-byte blocks, applies scalar GF table multipliers per byte, and XORs reconstructed data back. `raid6_datap_recov_s390xc()` handles data+P similarly. Published `raid6_recov_s390xc` has priority 1 and no validity callback.

State and persistence: temporarily rewrites `ptrs`, restores it, and mutates failed/P buffers.

Dependencies and integration: depends on `raid6_call.gen_syndrome`, GF scalar tables, and the recovery selector.

Risks and test signals: risks include assuming byte counts are multiples of 256 and correctness of inline `xc` memory constraints. Signals include s390 recovery tests, boot logs selecting `s390xc`, and RAID6 rebuild validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/lib/raid6/recov_s390xc.c -->
