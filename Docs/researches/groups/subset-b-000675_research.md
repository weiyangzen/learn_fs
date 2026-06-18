# subset-b-000675 research

Grouped research for the requested arm64 architecture headers. Each file has a source-path title and reconciliation markers for splitting into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/atomic_lse.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/atomic_lse.h

Purpose: provides the Large System Extensions implementation bodies for arm64 atomic integer, 64-bit atomic, cmpxchg, and cmpxchg128 operations. It is included by the atomics dispatch layer rather than used directly by generic code.

Important APIs/types/functions: macro families generate `__lse_atomic_*`, `__lse_atomic_fetch_*`, `__lse_atomic*_add_return*`, `__lse_atomic64_dec_if_positive`, `__lse__cmpxchg_case_*`, and `__lse__cmpxchg128*`. The assembly maps arithmetic and bitwise operations to LSE opcodes such as `stadd`, `ldadd`, `stclr`, `ldclr`, `cas`, and `casp`, with relaxed/acquire/release/full variants.

Control flow: most operations are single inline assembly instructions. Subtraction and `and` are built by negating or complementing the add/clear forms. `dec_if_positive` loops with `casal` until the decrement succeeds or the value is negative.

State and persistence: no durable state. It mutates caller-supplied `atomic_t`, `atomic64_t`, or memory operands with architecture-defined ordering semantics.

Dependencies and integration: depends on `__LSE_PREAMBLE`, atomic type definitions, inline-asm constraints, and the LL/SC/LSE selection framework. It integrates with generic Linux atomic APIs through arm64 atomic headers.

Risks: ordering suffixes and memory clobbers are correctness-critical. Any wrong constraint, missing clobber, or return-value adjustment breaks lock-free algorithms. `casp` register pairing and 128-bit alignment are especially sensitive. Test signals are arm64 atomic selftests, LKMM/litmus tests, KCSAN stress, qemu and hardware boot with and without LSE, and compiler build coverage for GCC/Clang.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/atomic_lse.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/barrier.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/barrier.h

Purpose: defines arm64 CPU, SMP, DMA, IO, speculation, and acquire/release barrier primitives. These are foundational memory-ordering contracts for the entire kernel.

Important APIs/types/functions: exports `sev`, `wfe`, `wfi`, `isb`, `dmb`, `dsb`, `psb_csync`, `tsb_csync`, `csdb`, `dgh`, `spec_bar`, `pmr_sync`, `__mb/__rmb/__wmb`, DMA barriers, SMP barriers, `array_index_mask_nospec`, `arch_counter_enforce_ordering`, `__smp_store_release`, `__smp_load_acquire`, and conditional load helpers.

Control flow: most macros emit one instruction. `spec_bar` and `pmr_sync` use alternative patching based on CPU capabilities. Store-release/load-acquire switch on operand size to emit `stlr*`/`ldar*`. Conditional loads spin, read, test the caller expression, then sleep with `__cmpwait_relaxed`.

State and persistence: no persistent state, but it controls visibility and ordering of all shared state. `tsb_csync` consults finalized CPU capabilities for erratum handling.

Dependencies and integration: depends on KASAN access checks, alternatives, cpufeature finalization, `asm-generic/barrier.h`, and cmpwait from cmpxchg. Used by atomics, locking, MMIO, scheduler, RCU, and timekeeping.

Risks: weakening one barrier can create rare data corruption or security bugs. Tests are LKMM litmus runs, lock/RCU stress, KCSAN, speculative-execution hardening tests, tracing barrier tests, and hardware validation on erratum-affected systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/bitops.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/bitops.h

Purpose: arm64 bit operation facade. It enforces inclusion through `<linux/bitops.h>` and composes generic bit scanning, atomic, locking, endian, scheduler, and ext2 helpers.

Important APIs/types/functions: no local functions. It includes generic implementations for `ffs`, `fls`, `ffz`, hweight, atomic bitops, lock bitops, non-atomic bitops, little-endian bitops, and ext2 atomic set-bit helpers.

Control flow: compile-time include aggregation only.

State and persistence: no state; state changes happen in the generic atomic bitops that this header exposes.

Dependencies and integration: depends on `linux/compiler.h` and the generic bitops headers. It is the architecture hook for every kernel user of bitmaps, flags, and bit locks on arm64.

Risks: include-order violations or replacing a generic header can alter atomicity or endian behavior globally. Test signals include full arm64 builds, lib/bitmap tests, filesystem tests using ext2 bitops, lockdep, and atomic bitops stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/bitops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/bitrev.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/bitrev.h

Purpose: provides architecture-accelerated bit reversal helpers using the A64 `rbit` instruction.

Important APIs/types/functions: exports `__arch_bitrev32`, `__arch_bitrev16`, and `__arch_bitrev8`. The 16-bit and 8-bit helpers reuse the 32-bit result and shift the reversed value down.

Control flow: single inline assembly instruction for 32-bit input; smaller widths are pure expressions.

State and persistence: stateless, attribute-const helpers.

Dependencies and integration: selected by generic bitrev code when arm64 architecture helpers are available. Used by protocol, CRC, and bit-order conversion code.

Risks: width truncation errors would silently corrupt bit order. Test signals are lib/bitrev tests, compiler build coverage, and comparison against generic bit reversal on randomized inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/bitrev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/boot.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/boot.h

Purpose: documents and exports boot-time placement constraints for arm64 kernel images and device trees.

Important APIs/types/functions: defines `MIN_FDT_ALIGN` as 8, `MAX_FDT_SIZE` as 2 MiB, and `MIN_KIMG_ALIGN` as 2 MiB.

Control flow: constants only.

State and persistence: no runtime state; the constants constrain bootloader and EFI stub placement decisions.

Dependencies and integration: depends on `<linux/sizes.h>`. Used by boot code, EFI, decompression/stub code, and documentation-aligned validation.

Risks: changing these constants can make valid bootloaders fail or allow invalid placements. Test signals include EFI stub boots, non-EFI bootloader boots, DTB placement tests, and image alignment checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/boot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/brk-imm.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/brk-imm.h

Purpose: reserves immediate values for AArch64 `BRK` instructions used by probes, debuggers, BUG/WARN, KASAN, UBSAN, and CFI.

Important APIs/types/functions: defines `KPROBES_BRK_IMM`, `UPROBES_BRK_IMM`, `KPROBES_BRK_SS_IMM`, `KRETPROBES_BRK_IMM`, `FAULT_BRK_IMM`, KGDB immediates, `BUG_BRK_IMM`, KASAN/UBSAN bases and masks, and CFI target/type/base/mask fields.

Control flow: constants only; exception handlers later decode the immediate from ESR.

State and persistence: no state. The values are ABI-like internal contracts between instruction generation and trap decoding.

Dependencies and integration: CFI masks use `GENMASK`; consumers include `bug.h`, `insn-def.h`, KASAN, UBSAN, kprobes, uprobes, KGDB, and ESR helpers.

Risks: collisions cause one subsystem's trap to be decoded as another's. Tests are kprobe/uprobe selftests, KGDB breakpoints, BUG/WARN tests, KASAN/UBSAN trap tests, and CFI fault decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/brk-imm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/bug.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/bug.h

Purpose: supplies arm64 implementations of `BUG()` and warning trap emission.

Important APIs/types/functions: defines `__BUG_FLAGS(flags)`, `BUG()`, `__WARN_FLAGS(cond_str, flags)`, and `HAVE_ARCH_BUG`. It delegates trap encoding details to `asm/asm-bug.h` and generic warning handling to `asm-generic/bug.h`.

Control flow: `BUG()` emits an architecture BUG instruction with flags, then marks control as unreachable. Warnings emit a flagged BUG trap that generic code can treat as recoverable.

State and persistence: no mutable state; BUG tables and trap sites persist in the kernel image.

Dependencies and integration: integrates compiler unreachable analysis, exception decoding, report generation, and generic BUG infrastructure.

Risks: bad flags or instruction encoding can make BUG/WARN sites unrecoverable or unreportable. Test signals are `CONFIG_BUG`, WARN/BUG selftests, objdump inspection of BUG tables, and panic/oops decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/bug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/cache.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/cache.h

Purpose: defines cache geometry, alignment, and cache-type helpers for arm64.

Important APIs/types/functions: exports L1 cache line constants, CLIDR extraction macros, DMA/kmalloc/slab alignment rules, `icache_is_aliasing`, `cache_type_cwg`, `cache_line_size_of_cpu`, `cache_line_size`, `dma_get_cache_alignment`, `arch_sync_dma_flush`, `arch_compact_of_hwid`, and `read_cpuid_effective_cachetype`.

Control flow: helpers read CPU ID registers, derive cache line sizes or aliasing flags, and compact MPIDR affinity into a topology key. KASAN/MTE configuration changes slab minimum alignment.

State and persistence: `__icache_flags` records global I-cache properties; other values are computed from CPU registers. No persistence beyond kernel data.

Dependencies and integration: depends on sysreg/cputype/MTE/KASAN headers. Used by DMA, slab, cache maintenance, CPU topology, and userspace cache-type reporting.

Risks: alignment mistakes can corrupt DMA buffers or KASAN tags; cache-type reporting affects self-modifying code and userspace. Test signals include DMA API tests, cacheflush tests, slab/KASAN boot tests, and heterogeneous CPU bring-up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/cacheflush.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/cacheflush.h

Purpose: declares arm64 cache maintenance operations and defines instruction-cache flushing behavior.

Important APIs/types/functions: declares `caches_clean_inval_pou`, `icache_inval_pou`, D-cache clean/invalidate variants to PoC/PoP/PoU, `caches_clean_inval_user_pou`, `sync_icache_aliases`, `flush_icache_range`, `copy_to_user_page`, `flush_dcache_page`, `flush_dcache_folio`, and `icache_inval_all_pou`. Defines `PG_dcache_clean`.

Control flow: `flush_icache_range` cleans and invalidates to PoU, performs KGDB breakpoint cache sync when enabled, and syncs aliases. Page helpers delegate to implementation files.

State and persistence: uses page/folio `PG_dcache_clean` state to remember D-cache cleanliness. Cache hardware state is modified but not persisted.

Dependencies and integration: depends on MM, KGDB, cache assembly routines, module text patching, BPF/JIT, user page copying, and executable mapping paths.

Risks: missing clean/invalidate creates stale instructions, data corruption, or debugger breakpoints not taking effect. Test signals are module load/unload, BPF JIT tests, ftrace/kprobe patching, KGDB, self-modifying code, and DMA coherency tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/cacheflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/cfi.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/cfi.h

Purpose: minimal arm64 Control Flow Integrity hook header.

Important APIs/types/functions: defines `__bpfcall` as empty, allowing common CFI/BPF code to refer to an architecture calling convention marker.

Control flow: none.

State and persistence: no state.

Dependencies and integration: consumed by BPF and CFI build paths when annotating indirect-call interfaces.

Risks: the empty definition is deliberate; changing it can affect ABI annotations or compiler CFI assumptions. Test signals are CFI-enabled arm64 builds and BPF verifier/JIT selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/cfi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/checksum.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/checksum.h

Purpose: implements fast arm64 IP checksum helpers and declares the generic checksum backend.

Important APIs/types/functions: exports `_HAVE_ARCH_IPV6_CSUM`, `csum_fold`, `ip_fast_csum`, `do_csum`, and includes generic checksum support. The IPv6 csum declaration is present through the generic interface.

Control flow: `csum_fold` folds a 32-bit partial checksum with carry handling. `ip_fast_csum` loops over IPv4 header words using inline assembly adds/adcs and returns a folded complement. `do_csum` is implemented elsewhere.

State and persistence: stateless computations over caller buffers.

Dependencies and integration: depends on network checksum types and generic checksum code. Used by IPv4/IPv6/TCP/UDP packet paths.

Risks: carry or endian mistakes cause packet drops or silent corruption. Test signals are networking checksum selftests, packet generators, IPv4 options coverage, IPv6 traffic, and cross-checking with software checksum fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/checksum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/clocksource.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/clocksource.h

Purpose: routes arm64 clocksource definitions to the vDSO-facing clocksource header.

Important APIs/types/functions: includes `<asm/vdso/clocksource.h>` and defines no local API.

Control flow: compile-time include only.

State and persistence: no state in this header.

Dependencies and integration: used by timekeeping and vDSO build paths to share clocksource definitions.

Risks: include path breakage affects vDSO time reads and kernel timekeeping builds. Test signals are vDSO selftests, clocksource boot logs, and timekeeping regression tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/clocksource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/cmpxchg.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/cmpxchg.h

Purpose: implements arm64 exchange, compare-exchange, 128-bit compare-exchange, and compare-wait primitives.

Important APIs/types/functions: exports `arch_xchg_relaxed/acquire/release/full`, `arch_cmpxchg*`, `arch_cmpxchg64*`, `arch_cmpxchg128`, `arch_cmpxchg128_local`, `system_has_cmpxchg128`, and `__cmpwait_relaxed`. Internal macro generators emit size-specific LL/SC and LSE paths.

Control flow: xchg uses alternative-patched LL/SC loops or LSE `swp` instructions. cmpxchg dispatches through `__lse_ll_sc_body`. cmpwait performs `sevl`, `wfe`, exclusive load, compares, and optionally waits again.

State and persistence: mutates caller memory atomically; no independent state.

Dependencies and integration: depends on barriers, LSE dispatch, build-bug checks, and generic atomic/locking users. Used by locks, atomics, refcounts, futexes, and wait loops.

Risks: size dispatch, acquire/release mapping, and LL/SC retry behavior are critical. Incorrect 128-bit support can corrupt paired-word atomics. Test signals are atomic selftests, qspinlock/refcount stress, LKMM litmus tests, and LSE/non-LSE hardware coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/cmpxchg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/compat.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/compat.h

Purpose: defines AArch32 compatibility ABI types and helpers for an arm64 kernel.

Important APIs/types/functions: defines 16-bit compat uid/gid/mode/pid types, `struct compat_stat`, `struct compat_statfs`, `COMPAT_UTS_MACHINE`, `compat_user_stack_pointer`, `COMPAT_MINSIGSTKSZ`, `is_compat_task`, `is_compat_thread`, and `compat_arm_syscall`.

Control flow: helpers test `TIF_32BIT` on current task or a supplied thread. Compat syscall handling is implemented elsewhere.

State and persistence: reads thread flags and task register state; structure layouts define persistent userspace ABI for compat stat/statfs.

Dependencies and integration: depends on generic compat definitions, task stack helpers, ptrace regs, and syscall/ELF handling.

Risks: layout or flag changes break 32-bit userspace ABI. Test signals are compat LTP, 32-bit libc/syscall tests, stat/statfs ABI checks, and mixed 32/64-bit process tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/compiler.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/compiler.h

Purpose: arm64 compiler integration for assembly preambles, pointer-auth stripping, and return-address handling.

Important APIs/types/functions: defines `ARM64_ASM_PREAMBLE`, `xpaclri(ptr)`, `ptrauth_strip_kernel_insn_pac`, `ptrauth_strip_user_insn_pac`, and overrides `__builtin_return_address` under pointer-auth configurations.

Control flow: `xpaclri` emits a hint-form pointer-auth strip instruction with fixed register usage; the return-address macro strips PAC from nonzero return addresses.

State and persistence: stateless pointer transformations.

Dependencies and integration: depends on assembler architecture features and pointer-auth config. Used by unwinding, tracing, ftrace, kprobes, and code inspecting instruction pointers.

Risks: incorrect PAC stripping breaks stack traces, profiling, and security instrumentation. Test signals are pointer-auth boot tests, unwinder tests, ftrace/perf/kprobe traces, and compiler compatibility builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/compiler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/cpu.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/cpu.h

Purpose: declares per-CPU CPU identification and feature snapshot structures for arm64.

Important APIs/types/functions: defines `struct cpuinfo_32bit` and `struct cpuinfo_arm64`, declares per-CPU `cpu_data`, and prototypes `cpuinfo_store_cpu`, `cpuinfo_store_boot_cpu`, `init_cpu_features`, and `update_cpu_features`.

Control flow: implemented code stores boot and per-CPU ID registers, then updates feature state when CPUs come online.

State and persistence: `cpu_data` persists each CPU's MIDR/MPIDR, cache type, ID registers, ZCR/SMCR, and AArch32 info while the kernel runs.

Dependencies and integration: depends on CPU hotplug, sysfs CPU objects, cpufeature, topology, and scheduler bring-up.

Risks: stale or inconsistent ID snapshots cause wrong capability decisions on heterogeneous systems. Test signals are CPU hotplug, heterogeneous big.LITTLE boot, sysfs CPU info, and cpufeature sanity warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/cpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/cpu_ops.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/cpu_ops.h

Purpose: abstracts platform-specific CPU boot, suspend, and shutdown operations.

Important APIs/types/functions: defines `struct cpu_operations` with `name`, `cpu_init`, `cpu_prepare`, `cpu_boot`, `cpu_postboot`, `cpu_can_disable`, `cpu_disable`, `cpu_die`, `cpu_kill`, and `cpu_suspend`. Declares `init_cpu_ops`, `get_cpu_ops`, and inline `init_bootcpu_ops`.

Control flow: boot code selects operations per CPU, initializes the boot CPU, then uses the table for secondary CPU lifecycle and suspend paths.

State and persistence: the selected `cpu_operations` pointer per CPU is maintained by implementation code; this header only declares the contract.

Dependencies and integration: used by PSCI/spin-table CPU bring-up, hotplug, suspend, and SMP initialization.

Risks: wrong return semantics or missing hooks strand CPUs during hotplug or resume. Test signals are SMP boot, CPU hotplug loops, suspend/resume, PSCI and non-PSCI platform tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/cpu_ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/cpucaps.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/cpucaps.h

Purpose: exposes the generated arm64 CPU capability numbers and compile-time possibility checks.

Important APIs/types/functions: includes `asm/cpucap-defs.h` and defines `cpucap_is_possible`, which returns true when a capability is within `ARM64_NCAPS` and is not known impossible under the current configuration.

Control flow: compile-time and inline capability validation only.

State and persistence: no state; it indexes into capability bitmaps declared elsewhere.

Dependencies and integration: used by cpufeature, alternatives, static branches, and code that guards capability-specific paths.

Risks: mismatched generated capability numbers break alternative patching and feature checks. Test signals are generated header consistency checks, allconfig builds, alternative patching tests, and cpufeature boot logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/cpucaps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/cpufeature.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/cpufeature.h

Purpose: central arm64 CPU feature and erratum capability interface. It describes feature-register sanitization, capability detection scopes, late-CPU conflict rules, HWCAP exposure, and many high-level feature predicates.

Important APIs/types/functions: defines `enum ftr_type`, `struct arm64_ftr_bits`, `struct arm64_ftr_override`, `struct arm64_ftr_reg`, and `struct arm64_cpu_capabilities`. Exports capability scope/type flags, `system_cpucaps`, `boot_cpucaps`, `cpus_have_cap`, final-cap helpers, `read_sanitised_ftr_reg`, ID field extractors, feature setup/check routines, HWCAP getters, system support predicates for FPSIMD/SVE/SME/PAN/PAuth/MTE/BTI/GCS/LPA2/MPAM/PMU, override helpers, and feature-specific CPU probes.

Control flow: boot stores raw ID registers, computes safe system values, finalizes boot and system capabilities, patches alternatives, then validates late CPUs against finalized capability state. Helpers choose local CPU registers or sanitized system registers depending on scope.

State and persistence: global bitmaps hold detected boot/system capabilities; `arm64_ftr_reg` records sanitized and user-visible register values; override structures persist command-line or early override decisions.

Dependencies and integration: integrates alternatives, hwcap/ELF, KVM, scheduler CPU hotplug, errata, sysreg access, and userspace ABI exposure.

Risks: incorrect safe-value rules or late-CPU flags can enable features unsupported by some CPUs, hide ABI features, or miss errata workarounds. Test signals are heterogeneous CPU boot, CPU hotplug rejection paths, `/proc/cpuinfo` and auxv HWCAP checks, KVM ID register tests, alternative patch verification, and erratum-specific regression tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/cpufeature.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/cpuidle.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/cpuidle.h

Purpose: declares arm64 CPU idle entry points and PSCI idle-state helpers.

Important APIs/types/functions: provides `cpu_do_idle`, `cpu_do_idle_irqprio`, `cpu_suspend`, `arm_cpuidle_init`, and PSCI CPU suspend parameter helpers when PSCI CPU idle is enabled.

Control flow: idle code enters WFI-like low-power states, with special handling when IRQ priority masking is active. PSCI helpers encode firmware suspend state parameters.

State and persistence: no durable state in this header; CPU idle drivers and firmware manage idle state.

Dependencies and integration: integrates cpuidle, PSCI firmware, CPU suspend, IRQ priority masking, and scheduler idle.

Risks: wrong entry path can leave interrupts masked or choose invalid firmware states. Test signals are cpuidle residency, suspend/resume, interrupt wakeups, and PSCI idle-state validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/cpuidle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/cputype.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/cputype.h

Purpose: defines MIDR/MPIDR encodings, implementer/part identifiers, and helpers for matching arm64 CPU models and revisions.

Important APIs/types/functions: exports MIDR field masks/shifts, implementer and part constants, `MIDR_CPU_MODEL`, `MIDR_CPU_VAR_REV`, `struct midr_range`, `MIDR_RANGE`, `MIDR_ALL_VERSIONS`, `is_midr_in_range`, `midr_is_cpu_model_range`, MPIDR affinity helpers, and current CPU read helpers.

Control flow: inline helpers compare extracted MIDR fields with ranges, including optional REVIDR masks for fixed revisions.

State and persistence: reads CPU registers; no independent state.

Dependencies and integration: used by errata matching, cpufeature, topology, KVM, PMU, and vendor-specific workarounds.

Risks: wrong model IDs or range comparisons apply errata to wrong CPUs or miss required workarounds. Test signals are boot logs on affected CPUs, errata selftests, KVM CPU-model exposure, and review against Arm/vendor TRMs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/cputype.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/crash_reserve.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/crash_reserve.h

Purpose: declares architecture crash-kernel reservation initialization.

Important APIs/types/functions: exposes `crash_reserve_memblock(void)` when crash dump support is configured, otherwise an empty inline stub.

Control flow: early boot calls reserve memory for crash kernels when enabled.

State and persistence: reservation state lives in memblock and later kexec crash structures; this header only declares the hook.

Dependencies and integration: integrates arm64 early memory setup with kdump/kexec.

Risks: incorrect reservation can overlap normal memory or fail to preserve crash kernel memory. Test signals are `crashkernel=` boot tests, kdump capture, memblock debug output, and kexec-tools validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/crash_reserve.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/current.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/current.h

Purpose: provides efficient access to the current task pointer on arm64.

Important APIs/types/functions: defines `get_current()` by reading `sp_el0`, then maps `current` to `get_current()`.

Control flow: single system-register read.

State and persistence: relies on context-switch and exception-entry code maintaining `sp_el0` as the current task pointer while in kernel mode.

Dependencies and integration: depends on sysreg helpers and task/thread setup. Used everywhere through `current`.

Risks: any mismatch between `sp_el0` maintenance and this helper corrupts current-task access globally. Test signals are context-switch stress, syscall/interrupt entry tests, CPU hotplug, and lockdep/scheduler sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/current.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/daifflags.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/daifflags.h

Purpose: controls DAIF exception mask flags for debug, SError, IRQ, and FIQ handling.

Important APIs/types/functions: exports DAIF flag constants and helpers such as `local_daif_mask`, `local_daif_restore`, `local_daif_inherit`, `local_daif_save`, `local_daif_flags`, and `system_has_prio_mask_debugging`-aware assertions.

Control flow: helpers read/write DAIF with barriers, preserve expected mask ordering, and coordinate with pseudo-NMI/priority masking paths.

State and persistence: changes processor PSTATE DAIF bits; no memory persistence.

Dependencies and integration: used by exception entry/exit, IRQ flags, idle, debug monitors, SError handling, and tracing.

Risks: restoring wrong DAIF bits can re-enable exceptions too early or mask NMIs indefinitely. Test signals are IRQ/NMI stress, lockdep IRQ state checks, debug exception tests, and SError injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/daifflags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/dcc.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/dcc.h

Purpose: declares debug communications channel console helpers.

Important APIs/types/functions: provides DCC status bit definitions and inline helpers for reading/writing debug channel registers when enabled by low-level debug code.

Control flow: helpers poll status and access debug data registers through sysreg instructions.

State and persistence: interacts with external debug channel hardware; no kernel-persistent state here.

Dependencies and integration: used by early debug/printk or debug monitor code on systems where DCC is available.

Risks: polling or register misuse can hang early boot or lose debug output. Test signals are earlycon/debug-console boots on supported hardware and build coverage with debug configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/dcc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/debug-monitors.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/debug-monitors.h

Purpose: declares arm64 debug monitor state, breakpoint/single-step controls, and debug exception hooks.

Important APIs/types/functions: provides MDSCR/KDE/MDE/SS constants, `DBG_ACTIVE_EL0/EL1`, hooks for enabling/disabling debug monitors, single-step state helpers, breakpoint handlers, and user/kernel debug control interfaces.

Control flow: implementation code toggles MDSCR bits and routes debug exceptions through registered hooks.

State and persistence: per-CPU debug register state and per-thread single-step flags live outside the header; this file defines the contract.

Dependencies and integration: used by ptrace, hardware breakpoints, kprobes, kgdb, perf, and exception handlers.

Risks: incorrect debug mask handling can expose kernel debugging to user mode or break single-step. Test signals are ptrace single-step tests, hw breakpoint tests, kprobe/kgdb tests, and perf watchpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/debug-monitors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/device.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/device.h

Purpose: provides arm64 architecture-private device state slots.

Important APIs/types/functions: defines `struct dev_archdata` and `struct pdev_archdata` as currently empty/placeholder architecture data containers.

Control flow: none.

State and persistence: device core embeds these structures in device/platform-device objects, reserving architecture extension space.

Dependencies and integration: included by generic device structures and platform bus code.

Risks: adding fields affects device lifetime and initialization expectations. Test signals are allmodconfig builds and device probe/remove tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/dmi.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/dmi.h

Purpose: arm64 DMI/SMBIOS integration helpers.

Important APIs/types/functions: declares `dmi_setup`, `dmi_remap`, `dmi_unmap`, and DMI availability behavior depending on configuration.

Control flow: early boot can initialize DMI tables and remap SMBIOS memory for parsing.

State and persistence: DMI core stores parsed table data; remaps are transient virtual mappings.

Dependencies and integration: integrates EFI/ACPI firmware table discovery with Linux DMI matching.

Risks: bad remap ranges can fault during early boot or hide platform quirks. Test signals are DMI table detection on server systems, ACPI/EFI boots, and DMI quirk matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/dmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/efi.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/efi.h

Purpose: arm64 EFI boot and runtime-services integration.

Important APIs/types/functions: declares `efi_init`, `efi_runtime_fixup_exception`, `efi_create_mapping`, `efi_set_mapping_permissions`, `arch_efi_call_virt`, `efi_rt_stack_top`, `__efi_rt_asm_wrapper`, runtime setup/teardown, `current_in_efi`, EFI DAIF save/restore macros, `efi_get_max_initrd_addr`, `efi_get_kimg_min_align`, `efi_set_pgd`, `efi_virtmap_load/unload`, capsule cache flushing, corrupted-x18 handling, and `efi_icache_sync`.

Control flow: boot code initializes EFI memory maps and runtime mappings. Runtime calls switch stacks/page tables, call firmware through an assembly wrapper, and restore kernel state afterward.

State and persistence: runtime page tables, `efi_rt_stack_top`, firmware virtual mappings, and EFI runtime-services enablement persist after boot.

Dependencies and integration: depends on boot constraints, cpufeature, FPSIMD/NEON, IO, memory management, TLB, ptrace, and TTBR0 PAN handling.

Risks: EFI calls run untrusted firmware in fragile CPU state; wrong DAIF, page-table, x18, cache, or FP handling can corrupt kernel execution. Test signals are EFI boot, runtime variable access, capsule update, kexec, KASLR/no-KASLR alignment, and fault injection during runtime calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/efi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/el2_setup.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/el2_setup.h

Purpose: assembly-only macro library for initializing EL2 state before the kernel or KVM relies on it.

Important APIs/types/functions: exports macros `init_el2_hcr`, `init_el2_state`, `finalise_el2_state`, and many internal setup macros for SCTLR, HCRX, timers, debug/SPE/TRBE/BRBE, LOR, stage-2, GICv3/v5, HSTR, virtual CPU ID registers, CPTR, fine-grained traps, MPAM, GCS, SVE, and SME.

Control flow: early assembly probes ID registers, handles VHE-only behavior, disables traps, zeros stage-2 translation, enables timer/GIC access, configures debug ownership, and later finalizes feature-specific EL2 access based on overrides or sanitized values.

State and persistence: writes EL2 system registers such as HCR_EL2, SCTLR_EL2, HCRX_EL2, CNTHCTL_EL2, MDCR_EL2, VTTBR_EL2, ICC/ICH registers, CPTR_EL2, FGT registers, ZCR_EL2, SMCR_EL2, and MPAM/GCS state. These persist as CPU-local control state.

Dependencies and integration: used by early head/KVM assembly. Depends on KVM register definitions, sysreg encodings, cpufeature overrides, GIC definitions, and VHE/nVHE build modes.

Risks: EL2 setup bugs prevent boot, break KVM, expose traps to guests/host, or misconfigure security-sensitive features. Test signals are VHE and nVHE boots, pKVM/KVM selftests, nested virtualization probes, SVE/SME/GCS/MPAM boots, GICv3/v5 interrupt tests, and CPU hotplug through EL2 initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/el2_setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/elf.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/elf.h

Purpose: defines arm64 ELF ABI, relocation constants, core register sets, aux vector entries, personality setup, compat ELF handling, and GNU property parsing.

Important APIs/types/functions: exports AArch64 relocation IDs, `ELF_CLASS/DATA/ARCH/PLATFORM`, `elf_check_arch`, `ELF_ET_DYN_BASE`, `ELF_NGREG`, `ELF_CORE_COPY_REGS`, `elf_gregset_t`, `elf_fpregset_t`, `ELF_PLAT_INIT`, `SET_PERSONALITY`, `ARCH_DLINFO`, stack randomization masks, compat ELF constants, `struct arch_elf_state`, `ARM64_ELF_BTI`, `arch_parse_elf_property`, and `arch_elf_adjust_prot`.

Control flow: exec setup validates ELF machine type, resets personality, emits vDSO/minsigstksz aux entries, parses BTI properties, and adjusts mmap protections when required.

State and persistence: affects process personality, thread flags, mm context/vDSO exposure, executable mapping protections, and core dump format.

Dependencies and integration: integrates binfmt_elf, signal ABI, ptrace/user register layout, HWCAP, compat mode, BTI, and vDSO.

Risks: ABI changes break loaders, core dumps, ASLR, BTI enforcement, or 32-bit compat exec. Test signals are ELF loader tests, auxv inspection, core dump/gdb tests, BTI property tests, ASLR checks, and compat userspace bootstraps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/entry-common.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/entry-common.h

Purpose: arm64 hooks for generic kernel entry/exit code.

Important APIs/types/functions: defines `ARCH_EXIT_TO_USER_MODE_WORK`, `arch_exit_to_user_mode_work`, and `arch_irqentry_exit_need_resched`.

Control flow: on return to user mode, pending MTE async faults are converted to `SIGSEGV`, and foreign FP state triggers FPSIMD restore. IRQ exit avoids preemption when pseudo-NMI DAIF state or unfinished CPU feature finalization makes it unsafe.

State and persistence: clears thread flags, sends signals, and restores current task FP state.

Dependencies and integration: depends on thread flags, cpufeature finalization, DAIF, FPSIMD, MTE, stacktrace, and generic entry code.

Risks: missed exit work leaks FP state or loses MTE faults; unsafe preemption can restore stale PSTATE. Test signals are MTE async fault tests, FPSIMD context-switch tests, IRQ/preempt stress, and CPU feature bring-up races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/entry-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/esr.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/esr.h

Purpose: defines ESR_ELx exception class and syndrome field encodings plus helpers for decoding faults and traps.

Important APIs/types/functions: exports EC constants for traps, aborts, SError, BRK, SVE/SME/GCS/MOPS/PAuth/BTI, ISS/ISS2 masks, abort FSC helpers, system-instruction decoding macros, BRK comment masks, `esr_sys64_to_sysreg`, `esr_cp15_to_sysreg`, GCS/MOPS/SME fields, and inline helpers such as `esr_is_data_abort`, `esr_is_cfi_brk`, `esr_fsc_is_translation_fault`, and `esr_get_class_string`.

Control flow: handlers extract exception class and ISS fields, classify faults, convert trapped sysreg encodings, and decode sanitizer/control-flow breakpoints.

State and persistence: stateless decoding of exception syndrome values captured by hardware.

Dependencies and integration: used by exception handlers, KVM trap emulation, page fault handling, debug, CFI/UBSAN/KASAN, MTE, GCS, and user sysreg emulation.

Risks: wrong masks misclassify faults, send wrong signals, or emulate incorrect sysregs. Test signals are fault injection, KVM sysreg trap tests, sanitizer trap tests, MTE/GCS tests, and page-fault regression coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/esr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/exception.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/exception.h

Purpose: declares arm64 exception vector C handlers and syndrome handling entry points.

Important APIs/types/functions: defines `__exception_irq_entry`, `disr_to_esr`, vector handlers for EL1t/EL1h/EL0 64-bit/EL0 32-bit sync/IRQ/FIQ/error, IRQ stack call helpers, memory abort, undefined, BTI, GCS, breakpoint/watchpoint, single-step, BRK, FP/SVE/SME, sysreg, svc, FPAC, MOPS, SError, and bad-stack panic handlers.

Control flow: assembly vectors enter these C handlers with `pt_regs`; handlers decode ESR and dispatch to subsystem-specific fault handling.

State and persistence: operates on pt_regs, signal state, task state, debug state, and fault accounting maintained elsewhere.

Dependencies and integration: depends on ESR definitions, ptrace regs, interrupt annotations, hardware breakpoints, syscall entry, and signal/fault subsystems.

Risks: prototype mismatch with assembly vectors or wrong handler routing causes crashes or incorrect user signals. Test signals are syscall tests, page-fault tests, debug exception tests, SError injection, compat exception tests, and bad-stack handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/exception.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/exec.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/exec.h

Purpose: provides architecture hooks for exec transitions.

Important APIs/types/functions: defines `arch_align_stack` behavior by delegating to generic/randomized stack alignment where applicable.

Control flow: used during `execve()` setup to choose the new user stack alignment.

State and persistence: affects new process stack pointer only.

Dependencies and integration: integrates binfmt loaders, ASLR, and process setup.

Risks: stack misalignment breaks ABI expectations for userspace startup. Test signals are execve tests, ABI alignment checks, and userspace dynamic loader smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/exec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/extable.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/extable.h

Purpose: defines arm64 exception-table entry layout and fixup helpers.

Important APIs/types/functions: includes generic extable support, defines architecture exception table structures/macros, and declares fixup handlers used by uaccess and fault recovery paths.

Control flow: when a fault occurs at a protected instruction, exception handling searches extables and redirects execution to a fixup target or specialized handler.

State and persistence: exception table entries are persistent kernel image metadata; runtime state is the adjusted pt_regs.

Dependencies and integration: used by uaccess, futex, copy routines, alternatives, module loading, and fault handling.

Risks: bad relative offsets or handler IDs can turn recoverable user faults into kernel oopses. Test signals are usercopy fault tests, futex fault tests, module extable validation, and objtool/build checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/extable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/fixmap.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/fixmap.h

Purpose: defines arm64 fixed virtual address slots used during early boot and runtime special mappings.

Important APIs/types/functions: defines fixmap address bounds, slot enums for early console, FDT, PCI IO, fixmap page tables, and permanent/temporary mappings; exposes fixmap helpers through generic fixmap infrastructure.

Control flow: early boot maps physical resources into predetermined virtual slots, then later code uses fixed slots for special-purpose mappings.

State and persistence: page table entries for fixmap slots persist while mappings are active; early temporary mappings are overwritten.

Dependencies and integration: depends on memory layout, page-table levels, EFI/early ioremap, PCI IO, FDT setup, and generic fixmap.

Risks: slot overlap or wrong address calculation corrupts early mappings and can break boot before normal VM is available. Test signals are earlycon, DTB parsing, EFI boot, KASAN/VMAP configurations, and page-table debug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/fixmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/fpsimd.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/fpsimd.h

Purpose: declares FPSIMD, SVE, SME, FA64, FPMR, and vector-length state management for arm64 tasks and CPUs.

Important APIs/types/functions: exports CPACR enable/restore helpers, FPSIMD save/load/switch/flush/update routines, `struct cpu_fp_state`, per-CPU `fpsimd_last_state`, thread SM/ZA helpers, SVE/SME state save/load/flush/VL routines, CPU enable callbacks, vector-length maps via `struct vl_info`, user enable/disable helpers, vector length setters/getters, SVE/SME state-size helpers, SME streaming mode helpers, DVMSync active tracking, and EFI FPSIMD begin/end hooks.

Control flow: context-switch and exception paths lazily preserve/restore FP/vector state, allocate SVE/SME buffers, update vector lengths, and gate user access through CPACR bits.

State and persistence: per-task FPSIMD/SVE/SME/FPMR/SVCR state, per-CPU last-state cache, global vector-length maps, and CPU control registers persist across scheduling events.

Dependencies and integration: integrates scheduler, signal ABI, ptrace, cpufeature, sysreg, EFI runtime services, KVM virtualization, and errata workarounds.

Risks: stale vector state leaks data between tasks or corrupts user registers; VL size mistakes overflow signal frames. Test signals are FPSIMD/SVE/SME selftests, signal frame tests, ptrace vector tests, context-switch stress, CPU hotplug, suspend/resume, and EFI runtime calls using FP state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/fpsimd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/fpsimdmacros.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/fpsimdmacros.h

Purpose: assembly macro support for saving, restoring, and manipulating FPSIMD/SVE register state.

Important APIs/types/functions: provides macros for vector register loads/stores, FPSIMD register save/restore sequences, and related assembler helpers used by low-level context-switch code.

Control flow: macro expansion emits repeated SIMD register transfer instructions in deterministic register order.

State and persistence: moves architectural FP/SIMD register state to and from task memory buffers.

Dependencies and integration: included by arm64 assembly implementation files for FPSIMD, signal, and context switching.

Risks: register order or offset mistakes corrupt user FP/vector state. Test signals are FPSIMD/SVE signal tests, ptrace register round-trips, and context-switch stress with randomized vector contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/fpsimdmacros.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/fpu.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/fpu.h

Purpose: small generic FPU interface adapter for arm64.

Important APIs/types/functions: exposes `kernel_fpu_available`, `kernel_fpu_begin`, and `kernel_fpu_end` semantics by tying them to FPSIMD/NEON support.

Control flow: callers bracket kernel-mode FP/NEON usage with begin/end helpers implemented elsewhere or as wrappers.

State and persistence: interacts with current task FP ownership and CPU FP enable state.

Dependencies and integration: used by crypto, RAID, networking, and other kernel code that may use vector instructions.

Risks: unbalanced begin/end or wrong availability checks corrupt user FP state. Test signals are crypto SIMD selftests, preemption stress around kernel NEON users, and FPSIMD context-switch tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/fpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/ftrace.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/ftrace.h

Purpose: arm64 ftrace, function graph tracing, direct-call, syscall-trace, and ftrace-regs ABI definitions.

Important APIs/types/functions: defines ftrace instruction sizes, PLT counts, stack tracer shift, `struct dyn_arch_ftrace`, `struct __arch_ftrace_regs`, ftrace regs accessors, partial pt_regs conversion, perf regs fill macro, `ftrace_call_adjust`, `arch_ftrace_get_symaddr`, `ftrace_init_nop`, `ftrace_graph_func`, direct caller setter, syscall compat ignore hooks, syscall symbol matching, and `prepare_ftrace_return`.

Control flow: dynamic ftrace patches callsites to branch to trampolines; trampolines capture selected registers, optionally redirect returns, and feed graph/perf/syscall tracing.

State and persistence: ftrace callsites and graph call targets are patched in kernel text; `ftrace_regs` captures transient call state.

Dependencies and integration: depends on instruction encoding, dynamic ftrace, function graph tracer, perf, syscall tracing, compat detection, and module text patching.

Risks: wrong register layout or instruction adjustment corrupts traced functions or stack unwinding. Test signals are ftrace selftests, function graph tracer, direct-call tests, perf callchains, module tracing, and compat syscall trace filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/ftrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/futex.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/futex.h

Purpose: implements arm64 atomic futex operations on user memory.

Important APIs/types/functions: defines `FUTEX_MAX_LOOPS`, LL/SC futex atomic op generators, optional LSUI operation generators, `__llsc_futex_cmpxchg`, `__lsui_cmpxchg32/64`, `arch_futex_atomic_op_inuser`, and `futex_atomic_cmpxchg_inatomic`.

Control flow: validates user access, masks user pointers, enables privileged user access or TTBR0 access, performs atomic LL/SC or LSUI operations with exception-table recovery, applies memory barriers, and returns old values or errors.

State and persistence: mutates a user futex word atomically; no kernel-persistent state.

Dependencies and integration: depends on uaccess, exception tables, LSUI/LLSC dispatch, futex core, and memory ordering.

Risks: user-access windows, retry limits, and barriers are security and correctness critical. Test signals are futex selftests, robust futex tests, fault-injection on user addresses, stress-ng futex workloads, LSUI hardware coverage, and memory-order litmus tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/futex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/gcs.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/gcs.h

Purpose: declares Guarded Control Stack support for arm64 user shadow stacks.

Important APIs/types/functions: provides `gcsb_dsync`, `gcsstr`, `gcsss1`, `gcsss2`, `PR_SHADOW_STACK_SUPPORTED_STATUS_MASK`, `task_gcs_el0_enabled`, `gcs_set_el0_mode`, `gcs_free`, `gcs_preserve_current_state`, `gcs_alloc_thread_stack`, `gcs_check_locked`, `put_user_gcs`, `push_user_gcs`, `get_user_gcs`, and `pop_user_gcs`, with stubs when disabled.

Control flow: helpers write/read GCS memory with special instructions, validate user access, temporarily enable TTBR0 access, update `GCSPR_EL0`, and enforce locked prctl bits.

State and persistence: per-task `gcs_el0_mode`, lock bits, allocated shadow stacks, and `GCSPR_EL0` persist across user execution.

Dependencies and integration: integrates prctl shadow-stack controls, clone/signal handling, uaccess, sysregs, and exception decoding for GCS faults.

Risks: pointer updates and permission checks protect return-address integrity; mistakes can corrupt shadow stacks or bypass locking. Test signals are GCS selftests, clone/exec/signal tests, fault injection, prctl locking tests, and context-switch preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/gcs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/gpr-num.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/gpr-num.h

Purpose: names AArch64 general-purpose register numbers for assembly and decoding code.

Important APIs/types/functions: defines constants for x0-x30 plus frame pointer, link register, stack pointer/zero register aliases as used by low-level code.

Control flow: constants only.

State and persistence: no state.

Dependencies and integration: used by instruction generation, ptrace/register access, assembly macros, and BPF/tracing helpers.

Risks: wrong numbering breaks generated instructions and register decoding. Test signals are instruction encoder tests, ptrace register tests, and BPF/ftrace register mapping tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/gpr-num.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/hardirq.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/hardirq.h

Purpose: defines arm64 hard IRQ accounting structures and stack helpers.

Important APIs/types/functions: declares per-CPU IRQ stack state, `ack_bad_irq`, hardirq stat fields, and irq-stack access helpers depending on configuration.

Control flow: IRQ entry may switch to a per-CPU IRQ stack and update hardirq accounting; bad IRQs are reported through the architecture hook.

State and persistence: per-CPU IRQ stack pointers and IRQ statistics persist during runtime.

Dependencies and integration: used by generic IRQ entry, interrupt handling, stack unwinding, and `/proc/interrupts` accounting.

Risks: stack switching bugs cause hard-to-debug crashes under interrupt load. Test signals are interrupt storm tests, lockdep IRQ state checks, stack unwinder tests, and bad-IRQ injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/hardirq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/hugetlb.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/hugetlb.h

Purpose: provides arm64 hugepage page-table helpers.

Important APIs/types/functions: declares and defines huge PTE operations for hugepage lookup, clear, set, migration/special handling, contiguous PTE support, and architecture hooks used by hugetlbfs.

Control flow: memory-management code manipulates huge PTEs through these helpers, handling contiguous mappings and break-before-make requirements implemented in MM code.

State and persistence: modifies page tables and hugepage mapping metadata.

Dependencies and integration: depends on pgtable definitions, hugetlbfs, THP-adjacent page-table code, TLB invalidation, and mmu-gather paths.

Risks: hugepage PTE mistakes corrupt address spaces or violate arm64 TLB rules. Test signals are hugetlbfs tests, libhugetlbfs, mmap/mprotect/munmap stress, migration tests, and page-table debug.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/hugetlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/hw_breakpoint.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/hw_breakpoint.h

Purpose: declares arm64 hardware breakpoint/watchpoint data structures, register encodings, and perf/ptrace integration hooks.

Important APIs/types/functions: defines `struct arch_hw_breakpoint_ctrl`, `struct arch_hw_breakpoint`, privilege/type/length constants, kernel step states, max BRP/WRP counts, debug register accessor macros, `encode_ctrl_reg`, `decode_ctrl_reg`, breakpoint parse/install/uninstall/read/slot APIs, thread-switch copy hooks, `get_num_brps`, `get_num_wrps`, and CPU suspend debug restore hook.

Control flow: perf/ptrace config is parsed into architecture breakpoint state, installed into debug registers, handled on exceptions, and restored across context switches and suspend.

State and persistence: breakpoint/watchpoint registers are CPU-local hardware state; per-task breakpoint state lives in perf/ptrace structures.

Dependencies and integration: depends on cputype/cpufeature/sysreg/virt and integrates perf, ptrace, debug monitors, exception handling, and CPU PM.

Risks: privilege or length encoding mistakes can miss watchpoints or trap in the wrong context. Test signals are perf hw_breakpoint tests, ptrace watchpoint tests, KVM/hyp mode checks, CPU hotplug, and suspend/resume with active breakpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/hw_breakpoint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/hwcap.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/hwcap.h

Purpose: defines arm64 HWCAP bit positions and compatibility HWCAP exposure.

Important APIs/types/functions: declares compat HWCAP/HWCAP2 bits, kernel HWCAP mapping macros for HWCAP/HWCAP2/HWCAP3, includes generated `kernel-hwcap.h`, defines `ELF_HWCAP*`, compat HWCAP globals, and enumerates internal hardware capability indices.

Control flow: cpufeature code sets HWCAP bits; ELF/auxv code reads them through macros.

State and persistence: global compat HWCAP variables and kernel capability bitmaps persist; user processes see values in auxv.

Dependencies and integration: integrates cpufeature, ELF loader, `/proc/cpuinfo`, compat AArch32 ABI, and userspace feature discovery.

Risks: changing bit positions breaks userspace ABI. Test signals are auxv HWCAP tests, glibc/hwcap probing, compat program startup, and feature-specific selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/hwcap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/hyp_image.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/hyp_image.h

Purpose: defines symbol and section naming helpers for KVM nVHE/hyp images.

Important APIs/types/functions: exports `kvm_nvhe_sym`, `HYP_SECTION_NAME`, `HYP_SECTION_SYMBOL_NAME`, `BEGIN_HYP_SECTION`, `END_HYP_SECTION`, `HYP_SECTION`, `KVM_NVHE_ALIAS`, and `KVM_NVHE_ALIAS_HYP`.

Control flow: assembler/linker macros place code/data into hyp sections and create aliases between kernel and hyp symbol namespaces.

State and persistence: affects link-time section layout and symbol aliases in the kernel/hyp images.

Dependencies and integration: used by KVM nVHE build, linker scripts, and hyp relocation/symbol access code.

Risks: wrong aliases or section boundaries break hyp text/data relocation and pKVM isolation. Test signals are KVM selftests, nVHE/pKVM boot, kallsyms/linker map inspection, and module-free allconfig builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/hyp_image.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/hypervisor.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/hypervisor.h

Purpose: collects arm64 hypervisor service initialization hooks.

Important APIs/types/functions: includes Xen hypervisor support and declares `kvm_init_hyp_services`, `kvm_arm_hyp_service_available`, `kvm_arm_target_impl_cpu_init`, optional `pkvm_init_hyp_services`, and `kvm_arch_init_hyp_services`.

Control flow: KVM initialization registers available hyp services, optionally initializes pKVM services, and performs target CPU initialization.

State and persistence: service availability state is maintained by implementation code; this header defines callers' interface.

Dependencies and integration: integrates KVM, pKVM, Xen detection, and CPU initialization.

Risks: missing service initialization can disable KVM capabilities or expose unavailable hypercalls. Test signals are KVM selftests, pKVM boots, Xen guest boots, and service availability probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/hypervisor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/image.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/image.h

Purpose: defines the arm64 kernel Image header layout and flag encodings.

Important APIs/types/functions: defines `ARM64_IMAGE_MAGIC`, image flag shifts/masks/values for endianness, page size, and physical base, `arm64_image_flag_field`, and `struct arm64_image_header`.

Control flow: bootloaders and EFI stub read the fixed header fields to place and launch the kernel image.

State and persistence: header data is embedded in the kernel Image and consumed before normal kernel execution.

Dependencies and integration: used by boot protocol, EFI stub, decompression/image tooling, and external bootloaders.

Risks: layout changes break bootloader ABI. Test signals are image header inspection, EFI and non-EFI boot tests, big/little endian builds, and page-size variant boots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/image.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/insn-def.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/insn-def.h

Purpose: defines small fixed AArch64 instruction encodings shared by assembly and C.

Important APIs/types/functions: includes BRK immediates and defines `AARCH64_BREAK_MON` plus `AARCH64_BREAK_FAULT`.

Control flow: constants only.

State and persistence: generated instruction words persist in patched or assembled text.

Dependencies and integration: used by instruction generation, fault injection, and trap code.

Risks: wrong opcodes produce undefined instructions or wrong trap classes. Test signals are objdump inspection, trap/fault tests, and instruction encoder tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/insn-def.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/insn.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/insn.h

Purpose: arm64 instruction decoding and generation API for dynamic patching, probes, alternatives, ftrace, BPF, and emulation.

Important APIs/types/functions: defines enums for hints, immediate/register types, registers, special/system registers, variants, conditions, branch/load/store/data/atomic/barrier types, and generated `aarch64_insn_is_*` predicates. Declares immediate/register decode/encode, branch/load/store/data/atomic/barrier/sysreg instruction generators, branch/ADRP offset getters/setters, AArch32 instruction helpers, and pstate condition-check table.

Control flow: inline predicates mask and compare instruction words. Generator functions synthesize valid opcodes from typed operands; patching code uses offset helpers to retarget branches or literals.

State and persistence: stateless computations, but outputs are written into executable text by callers.

Dependencies and integration: depends on instruction definitions and build-bug assertions. Integrated with alternatives, ftrace, kprobes, uprobes, BPF JIT, module patching, live text modification, and KVM/sysreg emulation.

Risks: bad encoders can patch invalid or unsafe instructions into kernel text. Range/offset and register encoding bugs are high impact. Test signals are arm64 insn unit tests, ftrace/kprobe/BPF selftests, module patching, alternatives validation, and disassembler cross-checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/insn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/io.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/io.h

Purpose: implements arm64 raw MMIO accessors, IO barriers, PCI IO space mapping, write-combining copy helpers, and ioremap variants.

Important APIs/types/functions: exports `__raw_read/write{b,w,l,q}`, IO barrier macros, `arch_has_dev_port`, `IO_SPACE_LIMIT`, `PCI_IOBASE`, optimized `__iowrite32_copy` and `__iowrite64_copy`, `ioremap_prot`, `ioremap`, `ioremap_wc`, `ioremap_np`, `ioremap_encrypted`, big-endian IO read/write macros, `ioremap_cache`, physical range validators, `arch_memremap_can_ram_remap`, and `arm64_is_protected_mmio`.

Control flow: raw accessors emit loads/stores, with alternative acquire loads for device-load errata. IO read barriers enforce DMA ordering and a control dependency. Constant-sized copy helpers emit contiguous stores and `dgh`; dynamic copies call full implementations. Mapping helpers select page attributes.

State and persistence: MMIO writes affect devices; ioremap creates persistent virtual mappings until unmapped; protected-MMIO checks query realm state.

Dependencies and integration: depends on barriers, memory layout, early_ioremap, alternatives, cpufeature, RSI/realm support, PCI, and generic IO.

Risks: ordering or attribute mistakes can corrupt devices, break PCI write combining, or map protected memory incorrectly. Test signals are driver MMIO tests, PCI write-combining throughput, ioremap debug, endian IO tests, and realm/protected-MMIO tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/irq.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/irq.h

Purpose: declares arm64 IRQ controller entry hooks and backtrace support.

Important APIs/types/functions: exports `arch_trigger_cpumask_backtrace`, `set_handle_irq`, `set_handle_fiq`, and `nr_legacy_irqs`.

Control flow: platform IRQ code registers top-level IRQ/FIQ handlers; exception entry calls the registered handler with pt_regs. Backtrace code can request cross-CPU stack dumps.

State and persistence: registered IRQ/FIQ handler pointers persist after interrupt controller initialization.

Dependencies and integration: depends on generic IRQ, cpumasks, interrupt controllers, SMP backtrace, and exception entry.

Risks: missing or duplicate handler registration prevents interrupt delivery. Test signals are interrupt controller boot, IPI/backtrace tests, FIQ paths, and warning paths for legacy IRQ count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/irq_work.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/irq_work.h

Purpose: tells generic irq_work whether arm64 can raise interrupt-backed irq_work.

Important APIs/types/functions: defines `arch_irq_work_has_interrupt()` returning true.

Control flow: generic irq_work uses this predicate to decide if queued work can be kicked by an interrupt.

State and persistence: no state in this header.

Dependencies and integration: used by irq_work, scheduler, perf, and RCU callbacks needing interrupt context execution.

Risks: incorrect return value changes latency or deadlock assumptions. Test signals are irq_work selftests, perf event delivery, RCU stall tests, and scheduler nohz coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/irq_work.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/irqflags.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/irqflags.h

Purpose: implements generic local IRQ flag operations for arm64, supporting both DAIF masking and GIC priority masking.

Important APIs/types/functions: exports `arch_local_irq_enable`, `arch_local_irq_disable`, `arch_local_save_flags`, `arch_irqs_disabled_flags`, `arch_irqs_disabled`, `arch_local_irq_save`, and `arch_local_irq_restore`, with DAIF and PMR internal variants.

Control flow: each public helper checks `system_uses_irq_prio_masking()`. DAIF paths write `daifset/daifclr` or restore DAIF; PMR paths read/write `ICC_PMR_EL1`, validate debug-priority states, and call `pmr_sync` where required.

State and persistence: modifies CPU-local DAIF/PSTATE or interrupt-controller PMR state.

Dependencies and integration: depends on barrier, ptrace PSR bits, sysreg, cpufeature, GIC priority constants, and pseudo-NMI support.

Risks: wrong save/restore semantics can enable interrupts in critical sections or block them permanently. Test signals are lockdep IRQ tracing, pseudo-NMI tests, interrupt storm stress, preempt/RT tests, and GIC priority masking debug checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/irqflags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/jump_label.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/jump_label.h

Purpose: arm64 static key/jump label implementation for patchable branches.

Important APIs/types/functions: defines `HAVE_JUMP_LABEL_BATCH`, `JUMP_LABEL_NOP_SIZE`, `JUMP_TABLE_ENTRY`, `ARCH_STATIC_BRANCH_ASM`, `arch_static_branch`, and `arch_static_branch_jump`.

Control flow: inline assembly emits a NOP or branch placeholder plus a jump table entry. Static key updates patch the instruction to branch or fall through.

State and persistence: jump table entries and patched text persist while keys change.

Dependencies and integration: depends on instruction size/encoding and static key core. Used by cpufeature alternatives, tracepoints, sched features, networking, and many static branches.

Risks: bad instruction size or table entries corrupt text patching. Test signals are jump_label selftests, tracepoint toggling, static key stress, module load/unload, and objdump validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/jump_label.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kasan.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kasan.h

Purpose: arm64 KASAN initialization and memory-tag helper interface.

Important APIs/types/functions: maps `arch_kasan_set_tag`, `arch_kasan_reset_tag`, and `arch_kasan_get_tag` to tag helpers, and declares `kasan_early_init` plus `kasan_init` when KASAN is enabled.

Control flow: early boot initializes KASAN shadow/tagging before normal memory use; tag helpers manipulate pointer tags inline.

State and persistence: KASAN shadow memory and tag state persist at runtime; this header only declares accessors and init hooks.

Dependencies and integration: depends on memory layout, MTE-KASAN helpers, page-table types, and generic KASAN.

Risks: early init or tag manipulation bugs cause false reports, missed memory bugs, or boot failures. Test signals are KASAN boot, KASAN selftests, MTE tag tests, slab/page allocator tests, and fault-report decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/kasan.h -->
