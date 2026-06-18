# subset-b-006569 research

Grouped research for Linux tools architecture headers and the x86 Dell UART backlight emulator. Each source file section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/arm64/include/asm/cputype.h -->
# sources/distributed-fs/ceph-client/tools/arch/arm64/include/asm/cputype.h

## Purpose
Mirrored arm64 CPU identification header for tools code that needs the kernel's MIDR/MPIDR layout, CPU implementor IDs, part numbers, and erratum range helpers without including the live architecture tree.

## Important APIs, Types, and Functions
Defines MPIDR affinity extraction macros, MIDR field masks, `MIDR_CPU_MODEL()`, `MIDR_CPU_VAR_REV()`, implementor/part constants for Arm, Cavium, Broadcom, Qualcomm, NVIDIA, Fujitsu, HiSilicon, Apple, Ampere, and Microsoft cores, and C helpers around `struct midr_range` and `struct target_impl_cpu`. Inline helpers include `midr_is_cpu_model_range()`, `is_midr_in_range()`, `is_midr_in_range_list()`, `read_cpuid_id()`, `read_cpuid_mpidr()`, `read_cpuid_implementor()`, `read_cpuid_part_number()`, and `read_cpuid_cachetype()`.

## Control Flow, State, and Persistence
There is no mutable storage. Consumers mask a raw MIDR/MPIDR value, compare it against compile-time model/range constants, or read CPU system registers through `read_sysreg_s()`. Range-list traversal is sentinel-based and stops on a zero `.model` entry.

## Dependencies and Integration Points
Depends on arm64 `sysreg.h`, integer type macros, and system-register access helpers. It is used by tools and generated/perf-style code that need the same CPU model and erratum predicates as the kernel.

## Risks and Test Signals
Risk centers on drift from upstream arm64 CPU IDs or erratum masks; a wrong part number silently changes model matching. Test signals are successful tools builds, compile-time use of every range helper, and comparison against known MIDR values for supported cores including newer Cortex/Neoverse and vendor cores.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/arm64/include/asm/cputype.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/arm64/include/asm/esr.h -->
# sources/distributed-fs/ceph-client/tools/arch/arm64/include/asm/esr.h

## Purpose
Defines arm64 Exception Syndrome Register encodings for tools and kernel-adjacent code that decodes traps, aborts, system-register accesses, MOPS, SME, CFI breakpoints, and ERET traps.

## Important APIs, Types, and Functions
Exports exception-class constants, EC/IL/ISS/ISS2 extraction macros, abort status bits and fault-code helpers, system-instruction ISS encoders such as `ESR_ELx_SYS64_ISS_SYS_VAL()`, CP15 conversion macros, MOPS register extractors, and inline classifiers `esr_is_data_abort()`, `esr_is_cfi_brk()`, `esr_fsc_is_translation_fault()`, `esr_fsc_is_permission_fault()`, `esr_fsc_is_access_flag_fault()`, `esr_iss_is_eretax()`, and `esr_iss_is_eretab()`. It declares `esr_get_class_string()`.

## Control Flow, State, and Persistence
All behavior is pure macro/inline decoding. Callers pass an ESR value, mask EC or ISS fields, and branch on the decoded fault or trap category. No persistent state is kept.

## Dependencies and Integration Points
Depends on `asm/sysreg.h`, `asm/types.h`, bit masks, and CFI break immediate constants supplied elsewhere. Integrates with trap reporting, KVM/system-register emulation, fault classification, and debug output.

## Risks and Test Signals
Risk is architectural drift: ISS2 and newer exception classes such as MOPS, SME, GCS, overlay, and dirty-bit faults must match the Arm ARM. Test signals include unit-style decode checks for representative ESR values, KVM sysreg trap emulation, fault handler classification, and build coverage in both assembler-excluded and C paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/arm64/include/asm/esr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/arm64/include/asm/gpr-num.h -->
# sources/distributed-fs/ceph-client/tools/arch/arm64/include/asm/gpr-num.h

## Purpose
Supplies assembler-visible numeric aliases for arm64 general-purpose registers so macro-generated `mrs_s`/`msr_s` instructions can encode register operands by name.

## Important APIs, Types, and Functions
Defines `.L__gpr_num_x0` through `.L__gpr_num_x30`, matching `w0` aliases, plus `xzr`/`wzr` as 31. In C mode it provides `__DEFINE_ASM_GPR_NUMS`, a string fragment that emits the same `.equ` definitions inside inline assembly.

## Control Flow, State, and Persistence
There is no runtime flow. Consumers include this before defining assembler macros that need to map textual register names to instruction bits.

## Dependencies and Integration Points
Integrated by arm64 `sysreg.h` for unsupported-by-GAS system register access. It depends only on the assembler/C preprocessor split.

## Risks and Test Signals
Risk is limited but precise: a wrong register number corrupts generated system instructions. Test signals are assembly of `mrs_s`/`msr_s` macros for regular and zero registers and tools builds with older binutils paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/arm64/include/asm/gpr-num.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/arm64/include/asm/sysreg.h -->
# sources/distributed-fs/ceph-client/tools/arch/arm64/include/asm/sysreg.h

## Purpose
Central arm64 system-register and system-instruction encoding header for tools. It mirrors kernel definitions for register encodings, PSTATE writes, cache/TLBI/AT operations, SCTLR/MAIR/PAR fields, PMU/SPE/GIC/MTE/PIE/POE/GCS bits, and inline system-register access helpers.

## Important APIs, Types, and Functions
Key APIs are `sys_reg()`, `sys_insn()`, field extractors `sys_reg_Op0()` through `sys_reg_Op2()`, `__emit_inst()`, PSTATE setters, generated `asm/sysreg-defs.h` inclusion, hundreds of `SYS_*`/`OP_*` encodings, register bit masks, `read_sysreg()`, `write_sysreg()`, `read_sysreg_s()`, `write_sysreg_s()`, `sysreg_clear_set()`, `sysreg_clear_set_s()`, `read_sysreg_par()`, and `SYS_FIELD_*` helpers.

## Control Flow, State, and Persistence
The file is macro-driven. Named registers use assembler mnemonics when available; unsupported registers are emitted via generated `mrs_s`/`msr_s` macros using encoded op fields. `read_sysreg_par()` wraps PAR reads with an erratum workaround alternative. There is no persistent state beyond CPU register side effects requested by callers.

## Dependencies and Integration Points
Depends on Linux bit/bitfield/build-bug/stringify/type headers, KASAN tag constants, `asm/gpr-num.h`, `asm/alternative.h`, and the generated `asm/sysreg-defs.h` from the arm64 tools Makefile. It is a foundation for CPU feature decode, traps, KVM, perf, and low-level tools code.

## Risks and Test Signals
Risks include stale generated sysreg definitions, assembler compatibility paths, endian instruction emission, wrong RES1/RES0 initialization masks, and dangerous side effects from write helpers. Test signals are arm64 tools builds with generated headers, compile tests for both named and encoded sysreg access, and targeted checks for TLBI/cache/system-register encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/arm64/include/asm/sysreg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/arm64/include/uapi/asm/bitsperlong.h -->
# sources/distributed-fs/ceph-client/tools/arch/arm64/include/uapi/asm/bitsperlong.h

## Purpose
Provides the arm64 UAPI word-size contract for tools headers.

## Important APIs, Types, and Functions
Defines `__BITS_PER_LONG` as 64 and includes `asm-generic/bitsperlong.h` for derived generic definitions.

## Control Flow, State, and Persistence
No control flow or state exists; preprocessing selects a fixed 64-bit ABI.

## Dependencies and Integration Points
Used by perf/tools UAPI consumers and any copied kernel header that needs userspace word size. Depends on the generic bits-per-long header.

## Risks and Test Signals
Risk is accidental mismatch with arm64 userspace ABI. Test signals are preprocessing on arm64 and build checks that size-dependent UAPI structs use 64-bit long semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/arm64/include/uapi/asm/bitsperlong.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/arm64/include/uapi/asm/kvm.h -->
# sources/distributed-fs/ceph-client/tools/arch/arm64/include/uapi/asm/kvm.h

## Purpose
Defines the arm64 userspace KVM ABI copied into tools: vCPU register layout, vCPU feature bits, VGIC control attributes, SVE register IDs, firmware pseudo-registers, PMU/timer/pvtime controls, PSCI constants, SMCCC filtering, and feature-ID writable-mask query structures.

## Important APIs, Types, and Functions
Important types include `struct kvm_regs`, `kvm_vcpu_init`, `kvm_guest_debug_arch`, `kvm_debug_exit_arch`, `kvm_sync_regs`, `kvm_pmu_event_filter`, `kvm_vcpu_events`, `kvm_arm_copy_mte_tags`, `kvm_arm_counter_offset`, `kvm_smccc_filter`, and `reg_mask_range`. Register-id helpers include `KVM_REG_ARM_CORE_REG()`, `ARM64_SYS_REG()`, SVE `KVM_REG_ARM64_SVE_*` macros, and firmware bitmap register macros.

## Control Flow, State, and Persistence
This header is declarative ABI. Userspace fills structs and numeric IDs for ioctls; KVM persists guest state in kernel, while tools only encode/decode the contract. Some values, notably swapped virtual timer CVAL/CNT IDs, are intentionally frozen ABI rather than architectural encodings.

## Dependencies and Integration Points
Depends on `linux/psci.h`, `linux/types.h`, arm64 ptrace state, and SVE context constants. Integrates with QEMU/kvmtool/perf tests and kernel KVM ioctls for vCPU init, one-reg access, interrupt injection, device attributes, migration, and hypercall exit routing.

## Risks and Test Signals
Risks are ABI breakage from changing padding, reserved fields, frozen register IDs, SVE slice sizing, or feature bitmap numbering. Test signals include userspace KVM build coverage, `KVM_GET/SET_ONE_REG` round trips for timers/SVE/FW regs, vCPU feature negotiation, VGIC device-attribute ioctls, and migration struct compatibility tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/arm64/include/uapi/asm/kvm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/arm64/include/uapi/asm/mman.h -->
# sources/distributed-fs/ceph-client/tools/arch/arm64/include/uapi/asm/mman.h

## Purpose
Perf/tools compatibility wrapper for arm64 memory-management constants.

## Important APIs, Types, and Functions
Includes `uapi/asm-generic/mman.h` and defines missing `MAP_32BIT` as 0 because arm64 does not implement that x86-specific mapping flag.

## Control Flow, State, and Persistence
No runtime behavior. It normalizes preprocessing so generic tools code can reference `MAP_32BIT` unconditionally.

## Dependencies and Integration Points
Integrated by tools/perf and other copied UAPI users that expect a common mmap constant set.

## Risks and Test Signals
Risk is treating zero as a real supported flag rather than a harmless no-op placeholder. Test signals are cross-architecture tools builds and mmap flag formatting tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/arm64/include/uapi/asm/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/arm64/include/uapi/asm/perf_regs.h -->
# sources/distributed-fs/ceph-client/tools/arch/arm64/include/uapi/asm/perf_regs.h

## Purpose
Defines arm64 perf sample register indexes for user and tools code.

## Important APIs, Types, and Functions
Exports `enum perf_event_arm_regs` for X0-X30/LR/SP/PC and pseudo register `PERF_REG_ARM64_VG` for SVE vector granule. `PERF_REG_EXTENDED_MASK` marks the extended pseudo register.

## Control Flow, State, and Persistence
No state or control flow; perf records and consumers use enum indexes to request and decode register samples.

## Dependencies and Integration Points
Integrated with perf event `sample_regs_user`/`sample_regs_intr` masks and arm64 register dump code.

## Risks and Test Signals
Risk is enum numbering drift, especially the sparse `VG = 46` extended slot. Test signals are perf register mask tests, SVE VG sample decode, and user/kernel header consistency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/arm64/include/uapi/asm/perf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/arm64/include/uapi/asm/unistd.h -->
# sources/distributed-fs/ceph-client/tools/arch/arm64/include/uapi/asm/unistd.h

## Purpose
Selects arm64 syscall table options for generic unistd generation in tools.

## Important APIs, Types, and Functions
Defines `__ARCH_WANT_RENAMEAT`, `__ARCH_WANT_NEW_STAT`, `__ARCH_WANT_SET_GET_RLIMIT`, `__ARCH_WANT_TIME32_SYSCALLS`, and `__ARCH_WANT_MEMFD_SECRET`, then includes `asm-generic/unistd.h`.

## Control Flow, State, and Persistence
The include-time flow is generic syscall macro expansion. No persistent state exists.

## Dependencies and Integration Points
Used by syscall table generation and tools that need arm64 syscall numbers matching kernel UAPI.

## Risks and Test Signals
Risk is stale architecture wants changing generated syscall numbers or availability macros. Test signals are syscall-number diff checks and perf trace/syscall-table generation on arm64.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/arm64/include/uapi/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/arm64/tools/Makefile -->
# sources/distributed-fs/ceph-client/tools/arch/arm64/tools/Makefile

## Purpose
Build fragment that generates arm64 tools system-register definitions.

## Important APIs, Types, and Functions
Defines `top_srcdir`, includes `tools/scripts/Makefile.include`, sets `AWK`, `MKDIR`, `RM`, locates `arch/arm64/tools/sysreg` and `gen-sysreg.awk`, and builds `$(OUTPUT)arch/arm64/include/generated/asm/sysreg-defs.h`.

## Control Flow, State, and Persistence
The default target depends on the generated header. The rule creates the output directory and pipes the sysreg table through AWK. `clean` removes the generated arm64 include directory.

## Dependencies and Integration Points
Integrated by tools builds before including `asm/sysreg.h`. It depends on kernel source layout, `OUTPUT`, AWK, and the arm64 sysreg generator/table.

## Risks and Test Signals
Risks include incorrect `top_srcdir` inference when invoked from unusual directories, stale generated files, and AWK/generator errors propagating into register encodings. Test signals are `make -C tools/arch/arm64/tools`, clean/regenerate idempotence, and consumers finding `asm/sysreg-defs.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/arm64/tools/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/csky/include/uapi/asm/perf_regs.h -->
# sources/distributed-fs/ceph-client/tools/arch/csky/include/uapi/asm/perf_regs.h

## Purpose
Defines C-SKY perf register indexes matching `struct pt_regs` layout.

## Important APIs, Types, and Functions
Exports `enum perf_event_csky_regs` covering TLS, LR, PC, SR, SP, original A0, argument registers, `regs0`-`regs9`, and ABI v2 extra registers plus HI/LO/DCSR when `__CSKYABIV2__` is defined.

## Control Flow, State, and Persistence
No runtime state. Conditional preprocessing changes the maximum enum value for ABI v1 versus ABI v2 builds.

## Dependencies and Integration Points
Integrated with perf register sampling and C-SKY tools that decode register masks.

## Risks and Test Signals
Risk is ABI-conditional enum mismatch between producer and consumer. Test signals are perf build coverage for both ABI modes and register dump/sample mask decode tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/csky/include/uapi/asm/perf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/hexagon/include/uapi/asm/mman.h -->
# sources/distributed-fs/ceph-client/tools/arch/hexagon/include/uapi/asm/mman.h

## Purpose
Hexagon tools mmap compatibility shim.

## Important APIs, Types, and Functions
Includes generic mman definitions and defines absent `MAP_32BIT` as 0.

## Control Flow, State, and Persistence
No control flow or state; it is a preprocessor normalization header.

## Dependencies and Integration Points
Used by perf/tools code that refers to common mmap flag names across architectures.

## Risks and Test Signals
Risk is confusing placeholder zero with supported Hexagon behavior. Test signals are Hexagon tools builds and flag-printing tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/hexagon/include/uapi/asm/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/hexagon/include/uapi/asm/unistd.h -->
# sources/distributed-fs/ceph-client/tools/arch/hexagon/include/uapi/asm/unistd.h

## Purpose
Hexagon syscall UAPI selector for tools, including aliases and architecture-specific generic syscall wants.

## Important APIs, Types, and Functions
Defines `sys_mmap2` as `sys_mmap_pgoff`, requests renameat, stat64, set/getrlimit, execve, clone, vfork, fork, and time32 syscall support, then includes `asm-generic/unistd.h`.

## Control Flow, State, and Persistence
The file participates only in preprocessing; generic unistd expands syscall numbers or prototypes depending on `__SYSCALL` usage.

## Dependencies and Integration Points
Integrated by syscall table generation and tracing tools for Hexagon.

## Risks and Test Signals
Risk is wrong `__ARCH_WANT_*` selection changing syscall availability or table layout. Test signals include generated syscall tables, trace syscall decoding, and build coverage with `__SYSCALL` declaration/table modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/hexagon/include/uapi/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/loongarch/include/asm/inst.h -->
# sources/distributed-fs/ceph-client/tools/arch/loongarch/include/asm/inst.h

## Purpose
LoongArch instruction-format helper header used by tools that inspect or synthesize LoongArch instructions.

## Important APIs, Types, and Functions
Defines opcode enums for branches, break, ERTN, load/store, pointer load/store, and AM swap; bitfield structs for instruction formats; `union loongarch_instruction`; `enum loongarch_gpr`; `LOONGARCH_INSN_NOP`; `LOONGARCH_INSN_SIZE`; and `emit_jirl()` via `DEF_EMIT_REG2I16_FORMAT()`.

## Control Flow, State, and Persistence
Consumers read or write the union's format-specific bitfields. The only emitted helper sets opcode, immediate, source register, and destination register fields for a JIRL instruction. No persistent state exists.

## Dependencies and Integration Points
Depends on `linux/bitops.h` and LoongArch encoding conventions. Integrates with objtool, ORC/unwinder, patching, or test code that needs instruction decoding.

## Risks and Test Signals
Risks include C bitfield layout assumptions, endian/compiler sensitivity, immediate range truncation, and opcode drift. Test signals are instruction encode/decode golden values, `emit_jirl()` byte-word checks, and LoongArch tools builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/loongarch/include/asm/inst.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/loongarch/include/asm/orc_types.h -->
# sources/distributed-fs/ceph-client/tools/arch/loongarch/include/asm/orc_types.h

## Purpose
Defines LoongArch ORC unwind record types shared by objtool-style generation and unwinder consumers.

## Important APIs, Types, and Functions
Exports base register constants `ORC_REG_*`, unwind type constants `ORC_TYPE_*`, and `struct orc_entry` with SP/FP/RA offsets, base-register selectors, type, and signal flag.

## Control Flow, State, and Persistence
No runtime control exists here; generated ORC tables persist arrays of `struct orc_entry` that an unwinder uses to reconstruct caller state.

## Dependencies and Integration Points
Depends on `linux/types.h`. Integrated by LoongArch ORC metadata producers and consumers.

## Risks and Test Signals
Risk is packed bitfield/offset ABI drift between table generator and unwinder. Test signals include ORC table generation, unwinding through calls, interrupts, partial register frames, and end-of-stack entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/loongarch/include/asm/orc_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/loongarch/include/uapi/asm/perf_regs.h -->
# sources/distributed-fs/ceph-client/tools/arch/loongarch/include/uapi/asm/perf_regs.h

## Purpose
Defines LoongArch perf register indexes.

## Important APIs, Types, and Functions
Exports `enum perf_event_loongarch_regs` for PC and general registers R1-R31, ending at `PERF_REG_LOONGARCH_MAX`.

## Control Flow, State, and Persistence
No state; perf sampling uses enum indexes in register masks and sample payloads.

## Dependencies and Integration Points
Integrated with perf register dumping and LoongArch perf events.

## Risks and Test Signals
Risk is register numbering mismatch with user pt_regs conventions. Test signals are perf sample decode and register-mask build tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/loongarch/include/uapi/asm/perf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/loongarch/include/uapi/asm/unistd.h -->
# sources/distributed-fs/ceph-client/tools/arch/loongarch/include/uapi/asm/unistd.h

## Purpose
LoongArch syscall UAPI selector for tools.

## Important APIs, Types, and Functions
Requests `__ARCH_WANT_SYS_CLONE` and includes `asm-generic/unistd.h`.

## Control Flow, State, and Persistence
No runtime flow; generic syscall generation handles expansion.

## Dependencies and Integration Points
Integrated by syscall-number and trace tooling for LoongArch.

## Risks and Test Signals
Risk is missing architecture wants as LoongArch syscall ABI evolves. Test signals are syscall table generation and clone syscall trace coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/loongarch/include/uapi/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/microblaze/include/uapi/asm/mman.h -->
# sources/distributed-fs/ceph-client/tools/arch/microblaze/include/uapi/asm/mman.h

## Purpose
MicroBlaze tools mmap compatibility wrapper.

## Important APIs, Types, and Functions
Includes generic mman definitions and supplies `MAP_32BIT` as 0.

## Control Flow, State, and Persistence
No state or control flow.

## Dependencies and Integration Points
Used by perf/tools cross-architecture code.

## Risks and Test Signals
Risk is placeholder constants hiding architecture-specific gaps. Test signals are MicroBlaze tools builds and mmap flag decode checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/microblaze/include/uapi/asm/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/mips/include/asm/barrier.h -->
# sources/distributed-fs/ceph-client/tools/arch/mips/include/asm/barrier.h

## Purpose
Minimal MIPS barrier implementation for tools, copied from older perf support rather than the full kernel arch header.

## Important APIs, Types, and Functions
Defines `mb()` as inline assembly that switches to MIPS II, emits `sync`, and restores MIPS0 mode; `wmb()` and `rmb()` alias to `mb()`.

## Control Flow, State, and Persistence
There is no stored state. Barrier macros create compiler and hardware ordering points when expanded.

## Dependencies and Integration Points
Used by tools code needing Linux-style memory barrier macros on MIPS. It does not depend on Kconfig-rich kernel barrier variants.

## Risks and Test Signals
Risks are incomplete modeling of modern MIPS barrier variants and assembler mode assumptions. Test signals are MIPS tools compilation and concurrency-sensitive tests that exercise lock-free helpers using these barriers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/mips/include/asm/barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/mips/include/asm/errno.h -->
# sources/distributed-fs/ceph-client/tools/arch/mips/include/asm/errno.h

## Purpose
Internal MIPS errno wrapper for tools.

## Important APIs, Types, and Functions
Includes `uapi/asm/errno.h` and defines `EMAXERRNO` as 1133, the largest MIPS errno value in this copied set.

## Control Flow, State, and Persistence
No flow or state; it makes the UAPI errno table and max-error constant visible.

## Dependencies and Integration Points
Integrated with tools code that needs kernel-style error-range tests on MIPS.

## Risks and Test Signals
Risk is `EMAXERRNO` drift if the UAPI table changes. Test signals are preprocessing and error-pointer range checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/mips/include/asm/errno.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/mips/include/uapi/asm/bitsperlong.h -->
# sources/distributed-fs/ceph-client/tools/arch/mips/include/uapi/asm/bitsperlong.h

## Purpose
MIPS UAPI word-size selector.

## Important APIs, Types, and Functions
Defines `__BITS_PER_LONG` from `_MIPS_SZLONG` and includes the generic bits-per-long header.

## Control Flow, State, and Persistence
No runtime state; ABI word size comes from compiler-provided MIPS ABI macros.

## Dependencies and Integration Points
Used by copied UAPI and perf/tools code for MIPS o32/n32/n64 builds.

## Risks and Test Signals
Risk is missing `_MIPS_SZLONG` in non-MIPS cross builds or mismatched ABI mode. Test signals are builds under o32, n32, and n64 toolchains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/mips/include/uapi/asm/bitsperlong.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/mips/include/uapi/asm/errno.h -->
# sources/distributed-fs/ceph-client/tools/arch/mips/include/uapi/asm/errno.h

## Purpose
MIPS ABI-specific errno numbering table for tools.

## Important APIs, Types, and Functions
Includes generic base errnos and defines MIPS-specific values for IPC, STREAMS, networking, restart, filesystem, key, robust mutex, RF-kill, hardware poison, and quota errors. Aliases include `EFSBADCRC` to `EBADMSG`, `EFSCORRUPTED` to `EUCLEAN`, and `EWOULDBLOCK` to `EAGAIN`.

## Control Flow, State, and Persistence
No control flow; constants are compiled into callers that translate or compare errno values.

## Dependencies and Integration Points
Integrated with MIPS UAPI consumers and tools that must display or interpret target errno numbers rather than host numbers.

## Risks and Test Signals
Risk is ABI-sensitive numbering drift, especially because MIPS differs from generic Linux errno ordering. Test signals are errno-name lookup tests and target syscall trace decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/mips/include/uapi/asm/errno.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/mips/include/uapi/asm/kvm.h -->
# sources/distributed-fs/ceph-client/tools/arch/mips/include/uapi/asm/kvm.h

## Purpose
Defines the MIPS userspace KVM ABI for tools.

## Important APIs, Types, and Functions
Important types are `struct kvm_regs`, empty `kvm_fpu`, `kvm_debug_exit_arch`, `kvm_guest_debug_arch`, `kvm_sync_regs`, `kvm_sregs`, and `kvm_mips_interrupt`. Register ID macros cover GP registers, CP0 namespace, KVM-specific Count controls, and FPU/MSA register subsets.

## Control Flow, State, and Persistence
The header encodes ioctl payload layouts and one-reg IDs only. KVM persists guest registers/timer state; userspace uses `COUNT_CTL`, `COUNT_RESUME`, and `COUNT_HZ` to freeze/resume CP0_Count consistently.

## Dependencies and Integration Points
Depends on `linux/types.h` and generic KVM register-size bits. Integrates with MIPS KVM userspace, migration, debug exits, and interrupt injection.

## Risks and Test Signals
Risks include register ID layout mistakes, 32-bit CPU sign-extension semantics, and timer-freeze behavior being misused during migration. Test signals are `KVM_GET/SET_ONE_REG` round trips, Count freeze/resume migration tests, and interrupt injection validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/mips/include/uapi/asm/kvm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/mips/include/uapi/asm/mman.h -->
# sources/distributed-fs/ceph-client/tools/arch/mips/include/uapi/asm/mman.h

## Purpose
MIPS tools mmap/madvise constant shim.

## Important APIs, Types, and Functions
Defines MIPS-specific `MADV_*`, `MAP_*`, and `PROT_*` values plus missing perf compatibility placeholders `MADV_SOFT_OFFLINE`, `MAP_32BIT`, and `MAP_UNINITIALIZED`.

## Control Flow, State, and Persistence
No runtime flow; constants are consumed by tools when decoding mmap flags or compiling common code.

## Dependencies and Integration Points
Integrated with perf and syscall tracing for MIPS target semantics.

## Risks and Test Signals
Risk is value drift from MIPS UAPI or accidentally treating compatibility zeros as supported target flags. Test signals are mmap flag formatting tests and cross-checks against kernel UAPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/mips/include/uapi/asm/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/mips/include/uapi/asm/perf_regs.h -->
# sources/distributed-fs/ceph-client/tools/arch/mips/include/uapi/asm/perf_regs.h

## Purpose
Defines MIPS perf register indexes.

## Important APIs, Types, and Functions
Exports `enum perf_event_mips_regs` for PC and R1-R31, with `PERF_REG_MIPS_MAX` set after R31.

## Control Flow, State, and Persistence
No state; perf masks and samples use these ordinal values.

## Dependencies and Integration Points
Integrated with MIPS perf register sampling.

## Risks and Test Signals
Risk is numbering mismatch with perf's target register dump order. Test signals are sample decode and register mask tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/mips/include/uapi/asm/perf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/parisc/include/uapi/asm/bitsperlong.h -->
# sources/distributed-fs/ceph-client/tools/arch/parisc/include/uapi/asm/bitsperlong.h

## Purpose
PARISC UAPI word-size selector.

## Important APIs, Types, and Functions
Defines `__BITS_PER_LONG` and `SHIFT_PER_LONG` based on whether `__LP64__` is set, then includes generic bits-per-long support.

## Control Flow, State, and Persistence
No runtime state; compiler ABI controls 32-bit versus 64-bit selection.

## Dependencies and Integration Points
Used by PARISC tools and copied UAPI headers.

## Risks and Test Signals
Risk is building with a compiler that does not expose the expected ABI macro. Test signals are 32-bit and 64-bit PARISC preprocessing/build checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/parisc/include/uapi/asm/bitsperlong.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/parisc/include/uapi/asm/errno.h -->
# sources/distributed-fs/ceph-client/tools/arch/parisc/include/uapi/asm/errno.h

## Purpose
PARISC ABI-specific errno numbering for tools.

## Important APIs, Types, and Functions
Includes generic errno base and defines PARISC-specific values for IPC, STREAMS, networking, restart, filesystem, key, robust mutex, and hardware poison cases. It keeps compatibility aliases such as `EWOULDBLOCK`, `EDEADLOCK`, `EFSBADCRC`, and `EFSCORRUPTED`.

## Control Flow, State, and Persistence
No flow or state; constants are consumed at compile time.

## Dependencies and Integration Points
Integrated with target errno display and syscall tracing for PARISC.

## Risks and Test Signals
Risk is target-host errno confusion because PARISC numbering differs from generic Linux. Test signals are errno mapping tests and syscall trace output checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/parisc/include/uapi/asm/errno.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/parisc/include/uapi/asm/mman.h -->
# sources/distributed-fs/ceph-client/tools/arch/parisc/include/uapi/asm/mman.h

## Purpose
PARISC mmap/madvise constants for tools.

## Important APIs, Types, and Functions
Defines target-specific `MADV_*`, `MAP_*`, and `PROT_*` values, including `MAP_VARIABLE`, `MAP_HUGETLB`, grow-up/down protections, and compatibility `MAP_32BIT` as 0.

## Control Flow, State, and Persistence
No state; constants drive decoding and compilation.

## Dependencies and Integration Points
Integrated with perf and syscall trace tooling for PARISC.

## Risks and Test Signals
Risk is flag-number drift or missing generic flags because this file does not include the full generic mman header. Test signals are mmap flag decode tests against PARISC UAPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/parisc/include/uapi/asm/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/powerpc/include/asm/barrier.h -->
# sources/distributed-fs/ceph-client/tools/arch/powerpc/include/asm/barrier.h

## Purpose
PowerPC tools memory-barrier header.

## Important APIs, Types, and Functions
Defines `mb()`, `rmb()`, `wmb()` using `sync`, `smp_lwsync()` using `lwsync`, plus release/acquire helpers implemented with compiler barriers and `WRITE_ONCE`/`READ_ONCE`.

## Control Flow, State, and Persistence
No persistent state. Expanded macros emit ordering instructions or compiler barriers at call sites.

## Dependencies and Integration Points
Used by perf/tools code that needs Linux-style barriers on PowerPC.

## Risks and Test Signals
Risks include using light-weight barriers where full ordering is required and divergence from kernel Kconfig-specific barrier behavior. Test signals are PowerPC tools builds and lock-free primitive tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/powerpc/include/asm/barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/powerpc/include/uapi/asm/bitsperlong.h -->
# sources/distributed-fs/ceph-client/tools/arch/powerpc/include/uapi/asm/bitsperlong.h

## Purpose
PowerPC UAPI word-size selector for tools.

## Important APIs, Types, and Functions
Includes generic bits-per-long definitions; architecture selection is left to the generic/compiler environment.

## Control Flow, State, and Persistence
No runtime flow.

## Dependencies and Integration Points
Integrated by copied PowerPC UAPI headers and tools.

## Risks and Test Signals
Risk is relying on generic behavior across 32/64-bit ABI modes. Test signals are ppc32 and ppc64 preprocessing/build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/powerpc/include/uapi/asm/bitsperlong.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/powerpc/include/uapi/asm/errno.h -->
# sources/distributed-fs/ceph-client/tools/arch/powerpc/include/uapi/asm/errno.h

## Purpose
PowerPC errno compatibility wrapper.

## Important APIs, Types, and Functions
Includes generic errno definitions and aliases `EDEADLOCK` to `EDEADLK`.

## Control Flow, State, and Persistence
No state or flow.

## Dependencies and Integration Points
Used by PowerPC tools that expect the architecture's UAPI errno alias.

## Risks and Test Signals
Risk is minimal; test signals are errno preprocessing and source compatibility checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/powerpc/include/uapi/asm/errno.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/powerpc/include/uapi/asm/kvm.h -->
# sources/distributed-fs/ceph-client/tools/arch/powerpc/include/uapi/asm/kvm.h

## Purpose
Large PowerPC userspace KVM ABI header for tools, covering register state, special registers, BookE/BookS MMU state, TCE/RMA/RTAS, hash page-table streaming, radix MMU configuration, CPU characteristics, XICS/XIVE interrupt controllers, and one-reg IDs.

## Important APIs, Types, and Functions
Key types include `struct kvm_regs`, feature-gated `struct kvm_sregs`, `kvm_fpu`, debug structs, TCE creation structs, `kvm_rtas_token_args`, Book3E TLB structs, `kvm_get_htab_fd/header`, `kvm_ppc_mmuv3_cfg`, `kvm_ppc_rmmu_info`, `kvm_ppc_cpu_char`, `kvm_ppc_xive_eq`, `kvm_ppc_pvinfo`, `kvm_ppc_smmu_info`, and `kvm_ppc_resize_hpt`. Macros enumerate many one-reg IDs for SPRs, FPR/VR/VSR, TM checkpointed state, ICP/VP state, and XICS/XIVE attributes.

## Control Flow, State, and Persistence
This is ABI layout, not implementation. Userspace fills ioctls and register IDs; kernel KVM owns guest CPU/MMU/interrupt state. Feature bits in `kvm_sregs` gate which embedded registers are valid or updated, and special update bits avoid clobbering asynchronous state.

## Dependencies and Integration Points
Depends on `linux/types.h` and generic KVM register-size namespaces. Integrated with PowerPC KVM userspace, migration/checkpointing, interrupt controller device APIs, and perf/test tools.

## Risks and Test Signals
Risks are high because padding, feature bits, and one-reg IDs are ABI. Particular risks include partial 64-bit debug register exposure, special-update semantics, HPT stream format compatibility, and XIVE/XICS attribute packing. Test signals are KVM selftests, migration round trips across BookE/BookS and ppc32/ppc64, one-reg enumeration tests, and interrupt controller save/restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/powerpc/include/uapi/asm/kvm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/powerpc/include/uapi/asm/mman.h -->
# sources/distributed-fs/ceph-client/tools/arch/powerpc/include/uapi/asm/mman.h

## Purpose
PowerPC tools mman constant shim.

## Important APIs, Types, and Functions
Defines target-specific `MAP_DENYWRITE`, `MAP_EXECUTABLE`, `MAP_GROWSDOWN`, `MAP_LOCKED`, `MAP_NORESERVE`, includes generic common mman constants, and supplies missing `MAP_32BIT` as 0.

## Control Flow, State, and Persistence
No runtime state; constants are compile-time ABI values.

## Dependencies and Integration Points
Integrated with perf and syscall tracing for PowerPC.

## Risks and Test Signals
Risk is flag-value drift or treating `MAP_32BIT` as supported. Test signals are flag decode checks against PowerPC UAPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/powerpc/include/uapi/asm/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/powerpc/include/uapi/asm/perf_regs.h -->
# sources/distributed-fs/ceph-client/tools/arch/powerpc/include/uapi/asm/perf_regs.h

## Purpose
Defines PowerPC perf sampled-register indexes.

## Important APIs, Types, and Functions
Exports `enum perf_event_powerpc_regs` for GPRs, NIP/MSR/ORIG_R3/CTR/LINK/XER/CCR/SOFTE/TRAP/DAR/DSISR/SIER/MMCRA/MMCR0/MMCR2/MMCR3/SIER2/SIER3 plus PVR, and PMU mask helpers `PERF_REG_PMU_MASK*`.

## Control Flow, State, and Persistence
No state; perf uses the enum and masks to request/decode register samples, including PMU-dependent subsets.

## Dependencies and Integration Points
Integrated with PowerPC perf event sampling and register dump code.

## Risks and Test Signals
Risks include changing enum order or PMU mask coverage, which breaks perf ABI. Test signals are perf sample register tests on PMU versions 3.00 and 3.1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/powerpc/include/uapi/asm/perf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/riscv/include/asm/barrier.h -->
# sources/distributed-fs/ceph-client/tools/arch/riscv/include/asm/barrier.h

## Purpose
RISC-V tools barrier header.

## Important APIs, Types, and Functions
Defines full and SMP memory barriers using `RISCV_FENCE()` with appropriate predecessor/successor sets, plus release/acquire helpers using `barrier()` and `WRITE_ONCE`/`READ_ONCE`.

## Control Flow, State, and Persistence
No stored state; macros emit `fence` instructions or compiler barriers.

## Dependencies and Integration Points
Depends on `asm/fence.h` and `linux/compiler.h`. Integrated with tools code that needs Linux barrier primitives on RISC-V.

## Risks and Test Signals
Risk is insufficient ordering if the fence masks do not match caller assumptions, especially I/O versus memory. Test signals are RISC-V tools builds and lock-free/barrier litmus-style tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/riscv/include/asm/barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/riscv/include/asm/csr.h -->
# sources/distributed-fs/ceph-client/tools/arch/riscv/include/asm/csr.h

## Purpose
Comprehensive RISC-V CSR and status-bit header for tools.

## Important APIs, Types, and Functions
Defines status bits, SATP/HGATP fields, exception and interrupt causes, PMP flags, hypervisor/AIA/envcfg/stateen masks, CSR numeric addresses for user/supervisor/virtual supervisor/hypervisor/machine/vector registers, mode-dependent aliases, interrupt enable bits, and inline CSR helpers `csr_swap()`, `csr_read()`, `csr_write()`, `csr_read_set()`, `csr_set()`, `csr_read_clear()`, and `csr_clear()`.

## Control Flow, State, and Persistence
Macros choose M-mode versus S-mode aliases at compile time. Inline helpers emit `csrr*` assembly and return old values where appropriate. No persistent storage is kept except the targeted hardware CSR side effects.

## Dependencies and Integration Points
Depends on `linux/bits.h`, `_AC/_ULL` style constants, and compiler support for RISC-V CSR inline assembly. Integrated with low-level RISC-V tools, perf, KVM, and vDSO-adjacent code.

## Risks and Test Signals
Risks include spec drift for AIA/hypervisor/vector CSRs, XLEN-dependent masks, wrong mode aliases, and dangerous writes through generic helpers. Test signals are riscv32/riscv64 builds, CSR encoding compile tests, and runtime smoke tests for read/set/clear on safe CSRs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/riscv/include/asm/csr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/riscv/include/asm/fence.h -->
# sources/distributed-fs/ceph-client/tools/arch/riscv/include/asm/fence.h

## Purpose
Small RISC-V fence macro helper.

## Important APIs, Types, and Functions
Defines `RISCV_FENCE_ASM(p, s)` and `RISCV_FENCE(p, s)` to stringify predecessor/successor sets into `fence` instructions for assembly or C inline assembly.

## Control Flow, State, and Persistence
No state. Callers choose fence masks and the macro emits the instruction with a memory clobber in C mode.

## Dependencies and Integration Points
Used by `asm/barrier.h` and any tools code needing explicit RISC-V fences.

## Risks and Test Signals
Risk is misuse with incomplete predecessor/successor sets. Test signals are assembly output checks for `iorw,iorw`, `r,r`, `w,w`, and build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/riscv/include/asm/fence.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/riscv/include/asm/vdso/processor.h -->
# sources/distributed-fs/ceph-client/tools/arch/riscv/include/asm/vdso/processor.h

## Purpose
RISC-V vDSO processor helper for tools.

## Important APIs, Types, and Functions
Defines `cpu_relax()`; on RISC-V builds it emits `pause` when `__riscv_zihintpause` is available, otherwise the raw pause encoding, and on non-RISC-V fallback it uses a compiler barrier.

## Control Flow, State, and Persistence
No persistent state. It is used inside spin/poll loops to provide a CPU hint without changing program-visible data.

## Dependencies and Integration Points
Depends on `asm-generic/barrier.h`. Integrated with vDSO and tools code compiled for or about RISC-V.

## Risks and Test Signals
Risk is assembler/toolchain support for `pause` and correct fallback encoding. Test signals are builds with and without `zihintpause` and inspection of generated code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/riscv/include/asm/vdso/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/riscv/include/uapi/asm/bitsperlong.h -->
# sources/distributed-fs/ceph-client/tools/arch/riscv/include/uapi/asm/bitsperlong.h

## Purpose
RISC-V UAPI word-size selector.

## Important APIs, Types, and Functions
Defines `__BITS_PER_LONG` from `__riscv_xlen` when available, otherwise falls back to 64, then includes generic bits-per-long.

## Control Flow, State, and Persistence
No runtime state.

## Dependencies and Integration Points
Used by RISC-V tools UAPI consumers for riscv32/riscv64 layout selection.

## Risks and Test Signals
Risk is host-side preprocessing without `__riscv_xlen` defaulting to 64 unexpectedly. Test signals are riscv32/riscv64 cross builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/riscv/include/uapi/asm/bitsperlong.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/riscv/include/uapi/asm/perf_regs.h -->
# sources/distributed-fs/ceph-client/tools/arch/riscv/include/uapi/asm/perf_regs.h

## Purpose
Defines RISC-V perf register indexes.

## Important APIs, Types, and Functions
Exports `enum perf_event_riscv_regs` for PC, RA, SP, GP, TP, temporaries, saved registers, and argument registers following RISC-V ABI names.

## Control Flow, State, and Persistence
No state; perf uses ordinal indexes in sample masks and payloads.

## Dependencies and Integration Points
Integrated with RISC-V perf register sampling.

## Risks and Test Signals
Risk is ABI name/order mismatch. Test signals are perf sample register decoding and mask validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/riscv/include/uapi/asm/perf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/riscv/include/uapi/asm/unistd.h -->
# sources/distributed-fs/ceph-client/tools/arch/riscv/include/uapi/asm/unistd.h

## Purpose
RISC-V syscall UAPI selector and architecture-specific syscall declaration.

## Important APIs, Types, and Functions
Requests `__ARCH_WANT_NEW_STAT` and `__ARCH_WANT_SET_GET_RLIMIT`, includes generic unistd, defines `__NR_riscv_flush_icache`, and registers it with `__SYSCALL()`.

## Control Flow, State, and Persistence
Include-time flow expands generic syscall definitions, then appends the RISC-V flush-icache syscall used because userspace cannot portably synchronize remote instruction caches itself.

## Dependencies and Integration Points
Integrated with syscall tracing and generated syscall tables for RISC-V.

## Risks and Test Signals
Risk is wrong arch-specific syscall offset or missing syscall registration. Test signals are syscall table generation and trace/decode of `riscv_flush_icache`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/riscv/include/uapi/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/s390/include/asm/barrier.h -->
# sources/distributed-fs/ceph-client/tools/arch/s390/include/asm/barrier.h

## Purpose
s390 tools memory-barrier header.

## Important APIs, Types, and Functions
Defines `__ASM_BARRIER` as `bcr 14,0` with z196 features or `bcr 15,0` otherwise, maps `mb()/rmb()/wmb()` to that instruction, and provides release/acquire helpers.

## Control Flow, State, and Persistence
No persistent state. Barrier macros impose ordering at expansion sites.

## Dependencies and Integration Points
Used by tools code requiring Linux barrier primitives on s390.

## Risks and Test Signals
Risks include Kconfig feature mismatch and assuming compiler-only release/acquire is sufficient for all contexts. Test signals are s390 tools builds and concurrency primitive tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/s390/include/asm/barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/s390/include/uapi/asm/bitsperlong.h -->
# sources/distributed-fs/ceph-client/tools/arch/s390/include/uapi/asm/bitsperlong.h

## Purpose
s390 UAPI word-size contract.

## Important APIs, Types, and Functions
Defines `__BITS_PER_LONG` as 64 and includes generic bits-per-long.

## Control Flow, State, and Persistence
No state or flow.

## Dependencies and Integration Points
Integrated by s390 UAPI/tools headers.

## Risks and Test Signals
Risk is minimal unless 31-bit compatibility headers are expected in this tools path. Test signals are s390 tools preprocessing/builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/s390/include/uapi/asm/bitsperlong.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/s390/include/uapi/asm/kvm.h -->
# sources/distributed-fs/ceph-client/tools/arch/s390/include/uapi/asm/kvm.h

## Purpose
s390 userspace KVM ABI header for tools, covering storage keys, CMMA, memory operations, interrupts, protected virtualization, zPCI, FLIC, VM attributes, CPU model/crypto/migration, register structs, guest debug, sync regs, and one-reg IDs.

## Important APIs, Types, and Functions
Important types include `kvm_s390_skeys`, `kvm_s390_cmma_log`, `kvm_s390_mem_op`, `kvm_s390_psw`, interrupt info unions, PV command/info structs, `kvm_s390_zpci_op`, adapter/AIS request structs, CPU model feature/subfunction structs, `kvm_regs`, `kvm_sregs`, `kvm_fpu`, debug structs, and the large `kvm_sync_regs` block. Enums define PV command groups and info IDs.

## Control Flow, State, and Persistence
This is ioctl ABI. Userspace passes structured payloads and flags; KVM persists guest CPU, memory, interrupt, PV, and device state. `KVM_SYNC_*` bits select which fields in `kvm_sync_regs` are valid.

## Dependencies and Integration Points
Depends on `linux/types.h` and generic KVM constants. Integrates with s390 KVM userspace, migration, protected virtualization setup/dump, interrupt injection, memory operation helpers, and device-control attributes.

## Risks and Test Signals
Risks are ABI layout/padding drift, bit ordering for feature/subfunction blocks, large FLIC buffer sizing, PV command reserved fields, and sync-reg alignment. Test signals are KVM selftests, migration/PV tests, mem-op extension tests, interrupt state save/restore, and CPU model attribute round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/s390/include/uapi/asm/kvm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/s390/include/uapi/asm/mman.h -->
# sources/distributed-fs/ceph-client/tools/arch/s390/include/uapi/asm/mman.h

## Purpose
s390 tools mmap compatibility wrapper.

## Important APIs, Types, and Functions
Includes generic mman definitions and defines missing `MAP_32BIT` as 0.

## Control Flow, State, and Persistence
No state; preprocessor-only normalization.

## Dependencies and Integration Points
Integrated with perf/tools common mmap flag code.

## Risks and Test Signals
Risk is treating zero as an actual s390 flag. Test signals are s390 tools build and flag decode tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/s390/include/uapi/asm/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/s390/include/uapi/asm/perf_regs.h -->
# sources/distributed-fs/ceph-client/tools/arch/s390/include/uapi/asm/perf_regs.h

## Purpose
Defines s390 perf register indexes.

## Important APIs, Types, and Functions
Exports `enum perf_event_s390_regs` for GPRs R0-R15, FP0-FP15, PSW mask, and PC.

## Control Flow, State, and Persistence
No runtime state; perf uses these indexes in sample masks.

## Dependencies and Integration Points
Integrated with s390 perf register sampling.

## Risks and Test Signals
Risk is sample layout mismatch with kernel perf ABI. Test signals are perf register sampling and mask tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/s390/include/uapi/asm/perf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/s390/include/uapi/asm/sie.h -->
# sources/distributed-fs/ceph-client/tools/arch/s390/include/uapi/asm/sie.h

## Purpose
s390 SIE intercept decoding data for tools and trace/user interfaces.

## Important APIs, Types, and Functions
Defines macro tables for diagnose codes, SIGP orders, program interruption codes, interceptable instruction codes, and SIE intercept codes. Helper macros `exit_code_ipa0()`, `exit_code()`, `INSN_DECODE_IPA0()`, `INSN_DECODE()`, and `icpt_insn_decoder()` create table entries and decode intercepted instruction keys.

## Control Flow, State, and Persistence
There is no storage. Consumers expand the tables into lookup arrays and use `icpt_insn_decoder(insn)` as a conditional-expression decoder suitable for trace declarations where general C control flow is undesirable.

## Dependencies and Integration Points
Integrated with s390 KVM/SIE tracing and userspace tools that need stable intercept names. It intentionally avoids switch/if constructs for parser friendliness.

## Risks and Test Signals
Risks include incomplete instruction coverage, decoder bit-shift mistakes for different opcode formats, and userspace parsers depending on macro shape. Test signals are decode golden tests for each IPA0 group, tracepoint build checks, and lookup coverage for diagnose/SIGP/program codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/s390/include/uapi/asm/sie.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/sh/include/asm/barrier.h -->
# sources/distributed-fs/ceph-client/tools/arch/sh/include/asm/barrier.h

## Purpose
SuperH tools barrier wrapper.

## Important APIs, Types, and Functions
For `__SH4A__`, defines `mb()/rmb()/wmb()` with `synco`; otherwise falls through to `asm-generic/barrier.h`. Comments document legacy control-register barrier needs.

## Control Flow, State, and Persistence
No persistent state. Compile-time CPU family selection controls whether SH-specific barriers exist.

## Dependencies and Integration Points
Integrated with tools code that needs barrier macros on SH.

## Risks and Test Signals
Risk is under-modeling non-SH4A control-register barrier requirements in tools. Test signals are SH cross builds for SH4A and non-SH4A configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/sh/include/asm/barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/sh/include/uapi/asm/mman.h -->
# sources/distributed-fs/ceph-client/tools/arch/sh/include/uapi/asm/mman.h

## Purpose
SH tools mmap compatibility wrapper.

## Important APIs, Types, and Functions
Includes generic mman definitions and defines missing `MAP_32BIT` as 0.

## Control Flow, State, and Persistence
No runtime behavior.

## Dependencies and Integration Points
Integrated with perf/tools mmap flag handling.

## Risks and Test Signals
Risk is placeholder misuse. Test signals are SH tools builds and flag decode checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/sh/include/uapi/asm/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/sparc/include/asm/barrier.h -->
# sources/distributed-fs/ceph-client/tools/arch/sparc/include/asm/barrier.h

## Purpose
SPARC tools barrier dispatcher.

## Important APIs, Types, and Functions
Includes `barrier_64.h` when compiling for 64-bit SPARC and `barrier_32.h` otherwise.

## Control Flow, State, and Persistence
No state; compile-time architecture macros select the implementation.

## Dependencies and Integration Points
Integrated by tools code including `<asm/barrier.h>` on SPARC.

## Risks and Test Signals
Risk is incorrect macro detection in cross builds. Test signals are sparc32 and sparc64 preprocessing/build checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/sparc/include/asm/barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/sparc/include/asm/barrier_32.h -->
# sources/distributed-fs/ceph-client/tools/arch/sparc/include/asm/barrier_32.h

## Purpose
sparc32 tools barrier fallback.

## Important APIs, Types, and Functions
Includes `asm-generic/barrier.h` and defines only an include guard.

## Control Flow, State, and Persistence
No architecture-specific state or instructions are added.

## Dependencies and Integration Points
Used through `asm/barrier.h` for 32-bit SPARC tools builds.

## Risks and Test Signals
Risk is relying on generic compiler barriers where hardware ordering would be needed. Test signals are sparc32 tools builds and any lock-free primitive tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/sparc/include/asm/barrier_32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/sparc/include/asm/barrier_64.h -->
# sources/distributed-fs/ceph-client/tools/arch/sparc/include/asm/barrier_64.h

## Purpose
sparc64 tools barrier implementation with Spitfire erratum workaround.

## Important APIs, Types, and Functions
Defines `membar_safe(type)` by placing `membar` in a predicted-taken branch delay slot, maps `mb()` to `membar_safe("#StoreLoad")`, treats `rmb()` and `wmb()` as compiler barriers under TSO assumptions, and provides release/acquire helpers.

## Control Flow, State, and Persistence
No persistent state. The emitted instruction sequence avoids a known hang scenario after mispredicted branches.

## Dependencies and Integration Points
Integrated through `asm/barrier.h` for sparc64 tools code.

## Risks and Test Signals
Risks include assembler syntax compatibility and relying on TSO/compiler-only read/write barriers. Test signals are sparc64 assembly build checks and inspection of emitted `ba,pt` plus `membar` sequence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/sparc/include/asm/barrier_64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/sparc/include/uapi/asm/bitsperlong.h -->
# sources/distributed-fs/ceph-client/tools/arch/sparc/include/uapi/asm/bitsperlong.h

## Purpose
SPARC UAPI word-size selector for tools.

## Important APIs, Types, and Functions
Defines `__BITS_PER_LONG` as 64 for `__sparc__ && __arch64__`, otherwise 32, then includes generic bits-per-long. The include guard name is historically Alpha-like but only guards this file.

## Control Flow, State, and Persistence
No runtime state.

## Dependencies and Integration Points
Integrated by SPARC UAPI/tools headers.

## Risks and Test Signals
Risk is macro-detection drift or confusing include guard naming during maintenance. Test signals are sparc32/sparc64 preprocessing checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/sparc/include/uapi/asm/bitsperlong.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/sparc/include/uapi/asm/errno.h -->
# sources/distributed-fs/ceph-client/tools/arch/sparc/include/uapi/asm/errno.h

## Purpose
SPARC errno numbering table for tools, matching SunOS-influenced SPARC ABI values.

## Important APIs, Types, and Functions
Includes generic errno base and defines networking, filesystem, STREAMS, key, robust mutex, RF-kill, and hardware poison errnos with SPARC-specific numbers and aliases.

## Control Flow, State, and Persistence
No flow or state; constants are compiled into target-aware tools.

## Dependencies and Integration Points
Integrated with syscall tracing and errno-name mapping for SPARC targets.

## Risks and Test Signals
Risk is host/target errno mismatch because SPARC values differ from generic Linux. Test signals are errno mapping tests and syscall trace decode checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/sparc/include/uapi/asm/errno.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/sparc/include/uapi/asm/mman.h -->
# sources/distributed-fs/ceph-client/tools/arch/sparc/include/uapi/asm/mman.h

## Purpose
SPARC tools mman constant shim.

## Important APIs, Types, and Functions
Defines SPARC-specific `MAP_DENYWRITE`, `MAP_EXECUTABLE`, `MAP_GROWSDOWN`, `MAP_LOCKED`, and `MAP_NORESERVE`, includes generic common mman constants, and supplies `MAP_32BIT` as 0.

## Control Flow, State, and Persistence
No state; constants support compilation and flag decoding.

## Dependencies and Integration Points
Integrated by perf/tools and syscall trace paths for SPARC.

## Risks and Test Signals
Risk is flag-value drift or placeholder misuse. Test signals are mmap flag decode checks against SPARC UAPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/sparc/include/uapi/asm/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/x86/dell-uart-backlight-emulator/Makefile -->
# sources/distributed-fs/ceph-client/tools/arch/x86/dell-uart-backlight-emulator/Makefile

## Purpose
Build/install Makefile for the Dell UART backlight emulator test utility.

## Important APIs, Types, and Functions
Declares the `dell-uart-backlight-emulator` target from its C source, `BINDIR ?= /usr/bin`, appends `-O2 -Wall` to `CFLAGS`, provides a generic `%: %.c` compile rule, `clean`, and `install` targets.

## Control Flow, State, and Persistence
Build flow compiles the single C file with `$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)`. Install creates `$(DESTDIR)$(BINDIR)` and installs mode 755. No persistent state outside generated binary/install path.

## Dependencies and Integration Points
Integrated as a standalone x86 architecture tool for testing the kernel Dell UART backlight driver.

## Risks and Test Signals
Risks include stale comment text mentioning Intel SDSi, no dependency generation, and host-only build assumptions. Test signals are `make`, `make clean`, and staged `make DESTDIR=... install`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/x86/dell-uart-backlight-emulator/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/x86/dell-uart-backlight-emulator/dell-uart-backlight-emulator.c -->
# sources/distributed-fs/ceph-client/tools/arch/x86/dell-uart-backlight-emulator/dell-uart-backlight-emulator.c

## Purpose
User-space serial emulator for Dell AIO UART backlight boards, used to test the Linux `dell-uart-backlight` driver without hardware.

## Important APIs, Types, and Functions
Functions are `dell_uart_checksum()`, `signalhdlr()`, and `main()`. Global state is `serial_fd` and current `brightness`. The emulator uses termios, signal handling, byte-wise serial reads, checksum validation, and replies for get version, set brightness, get brightness, and set power commands.

## Control Flow, State, and Persistence
`main()` opens the requested serial port, saves/restores termios, configures 9600 baud raw mode without flow control, installs SIGINT/SIGTERM handlers so blocking `read()` exits, then synchronizes on command first bytes `0x6a` or `0x8a`. It validates checksum, updates brightness for command `0x0b`, returns version `PHI23-V321`, returns brightness for `0x0c`, accepts power `0x0e`, and writes response length/ack/data/checksum.

## Dependencies and Integration Points
Depends on POSIX file, termios, signal, and unistd APIs. Integrated with pseudo-terminal or serial-port based driver tests.

## Risks and Test Signals
Risks include fixed 4-byte command buffer, no partial-write retry, `strcpy()` relying on a small constant version string, and simplistic resynchronization. Test signals are pty-based protocol tests for valid commands, checksum failures, invalid brightness/power parameters, signal shutdown, and termios restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/x86/dell-uart-backlight-emulator/dell-uart-backlight-emulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/x86/include/asm/amd/ibs.h -->
# sources/distributed-fs/ceph-client/tools/arch/x86/include/asm/amd/ibs.h

## Purpose
AMD Instruction Based Sampling register-layout header for x86 tools.

## Important APIs, Types, and Functions
Defines IBS data source constants, unions `ibs_fetch_ctl`, `ibs_op_ctl`, `ibs_op_data`, `ibs_op_data2`, `ibs_op_data3`, `ic_ibs_extd_ctl`, and `struct perf_ibs_data` with raw caps/data and MSR register storage.

## Control Flow, State, and Persistence
No active control flow. Consumers read MSR snapshots into the unions and inspect bitfields for fetch/op sample validity, latency, cache/TLB misses, branch metadata, data source, and memory operation details.

## Dependencies and Integration Points
Depends on `../msr-index.h` for IBS MSR count constants. Integrated with perf AMD IBS decoding and sample export paths.

## Risks and Test Signals
Risks include C bitfield layout/endian assumptions, family/model-specific field changes, and reserved-bit interpretation. Test signals are perf IBS decode tests with known MSR values and build checks against current MSR index definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/x86/include/asm/amd/ibs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/x86/include/asm/asm.h -->
# sources/distributed-fs/ceph-client/tools/arch/x86/include/asm/asm.h

## Purpose
x86 assembly macro compatibility header for tools and copied kernel code.

## Important APIs, Types, and Functions
Defines stringification helpers for assembler versus C, instruction-size selectors, register-name selectors, pointer/alignment directives, common instruction/register aliases, argument register macros for i386 and x86_64, exception-table macros under `__KERNEL__`, kprobe blacklist support, and `ASM_CALL_CONSTRAINT` for inline asm calls.

## Control Flow, State, and Persistence
No runtime state. Preprocessor selection emits either raw assembler syntax or C string fragments, and 32/64-bit branches select register/instruction sizes.

## Dependencies and Integration Points
Depends on `linux/stringify.h` in C mode and kernel exception handler symbols when `__KERNEL__` paths are used. Integrated by x86 tools asm helpers, atomics, and copied low-level code.

## Risks and Test Signals
Risks include wrong 32/64-bit selection, malformed inline assembly strings, exception-table use outside kernel context, and missing call constraints causing objtool warnings. Test signals are i386/x86_64 builds and inline asm compile tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/x86/include/asm/asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/x86/include/asm/atomic.h -->
# sources/distributed-fs/ceph-client/tools/arch/x86/include/asm/atomic.h

## Purpose
x86 tools atomic primitive header.

## Important APIs, Types, and Functions
Defines `LOCK_PREFIX`, `ATOMIC_INIT`, `atomic_read()`, `atomic_set()`, `atomic_inc()`, `atomic_dec_and_test()`, `atomic_cmpxchg()`, `test_and_set_bit()`, and `test_and_clear_bit()` using x86 locked instructions and rmwcc helpers.

## Control Flow, State, and Persistence
Atomic operations act on caller-owned `atomic_t` or bit memory. `atomic_read()`/`atomic_set()` use READ/WRITE semantics, increments and bit ops emit locked instructions, and cmpxchg delegates to `cmpxchg.h`.

## Dependencies and Integration Points
Depends on `linux/compiler.h`, `linux/types.h`, `rmwcc.h`, `asm/asm.h`, and `asm/cmpxchg.h`. Integrated with tools libraries needing kernel-style atomic operations on x86.

## Risks and Test Signals
Risks include only implementing the subset used by tools, inline asm constraint mistakes, and architecture-size interactions for bit operations. Test signals are x86 tools builds and atomic/bit operation unit tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/x86/include/asm/atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/x86/include/asm/barrier.h -->
# sources/distributed-fs/ceph-client/tools/arch/x86/include/asm/barrier.h

## Purpose
x86 tools memory-barrier header.

## Important APIs, Types, and Functions
Defines full/read/write barriers for i386 via locked add on stack and for x86_64 via `mfence`, `lfence`, `sfence`; defines SMP barriers on x86_64; and provides release/acquire helpers.

## Control Flow, State, and Persistence
No persistent state. Macros emit ordering instructions or compiler barriers at call sites.

## Dependencies and Integration Points
Integrated by tools code that uses Linux barrier primitives on x86.

## Risks and Test Signals
Risks include stack-address assumptions for locked add barriers, compiler differences, and missing definitions for some non-x86_64 SMP helpers. Test signals are i386/x86_64 builds and barrier/atomic primitive tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/x86/include/asm/barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/x86/include/asm/cmpxchg.h -->
# sources/distributed-fs/ceph-client/tools/arch/x86/include/asm/cmpxchg.h

## Purpose
x86 tools compare-and-exchange helper.

## Important APIs, Types, and Functions
Defines size constants, an error symbol `__cmpxchg_wrong_size()`, `__raw_cmpxchg()` for 1/2/4/8-byte operands using locked `cmpxchg`, `__cmpxchg()`, and public `cmpxchg()`.

## Control Flow, State, and Persistence
The macro evaluates typed old/new values, switches on operand size, emits the correct instruction, and returns the previous memory value. On 32-bit builds the 8-byte case is made impossible with a `-1` size constant.

## Dependencies and Integration Points
Depends on `linux/compiler.h` and `LOCK_PREFIX` supplied by including code. Integrated by x86 tools atomics and lock-free helpers.

## Risks and Test Signals
Risks include unsupported operand sizes surfacing as link/compile errors, 64-bit use on 32-bit builds, and inline asm constraints. Test signals are compile tests for byte/word/long/quad cmpxchg and wrong-size negative tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/arch/x86/include/asm/cmpxchg.h -->
