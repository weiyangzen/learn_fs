# Group Research: subset-b-000813

Grouped research for RISC-V Linux architecture headers in the Ceph client source tree. Each section preserves the source path and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/alternative.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/alternative.h

## Purpose
Declares the RISC-V runtime alternatives patching interface used to rewrite boot, module, early-boot, vendor-errata, and CPU-feature instruction sequences.

## Important APIs, Types, And Functions
types `alt_entry`; functions/prototypes `apply_module_alternatives`, `riscv_alternative_fix_offsets`, `andes_errata_patch_func`, `mips_errata_patch_func`, `sifive_errata_patch_func`, `thead_errata_patch_func`, `riscv_cpufeature_patch_func`, `apply_boot_alternatives`, `apply_early_boot_alternatives`; macros/constants `__ASM_ALTERNATIVE_H`, `PATCH_ID_CPUFEATURE_ID(p) lower_16_bits(p)`, `PATCH_ID_CPUFEATURE_VALUE(p) upper_16_bits(p)`, `RISCV_ALTERNATIVES_BOOT`, `RISCV_ALTERNATIVES_MODULE`, `RISCV_ALTERNATIVES_EARLY_BOOT`, `__ALT_PTR(a, f) ((void *)&(a)->f + (a)->f)`, `ALT_OLD_PTR(a) __ALT_PTR(a, old_offset)`, `ALT_ALT_PTR(a) __ALT_PTR(a, alt_offset)`.

## Control Flow
The header is primarily declarative. Runtime behavior occurs in the including architecture implementation files and generic Linux subsystems that consume the constants, types, macros, and prototypes defined here. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
The header itself owns no filesystem or durable state. It defines ABI-like constants or inline behavior consumed by longer-lived kernel objects.

## Dependencies And Integration Points
Direct includes are `asm/alternative-macros.h`, `linux/init.h`, `linux/kernel.h`, `linux/types.h`, `linux/stddef.h`, `asm/hwcap.h`. Integrates with generic Linux architecture headers and RISC-V implementation files through include-time contracts.

## Risks And Edge Cases
The main risk is that generic code treats these definitions as architecture ABI. Renaming, renumbering, or changing inline semantics without matching implementation changes can create build-only or boot-time failures.

## Test Signals
Test signals include architecture build coverage, include dependency checks, and subsystem tests for the generic code that consumes this header.

Source read size: 73 lines, 2536 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/alternative.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/arch_hweight.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/arch_hweight.h

## Purpose
Provides optimized population-count helpers that can patch in Zbb `cpop/cpopw` instructions while retaining generic fallbacks.

## Important APIs, Types, And Functions
functions/prototypes `__arch_hweight32`, `__arch_hweight16`, `__arch_hweight8`, `__arch_hweight64`; macros/constants `_ASM_RISCV_HWEIGHT_H`, `CPOPW`.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
Direct includes are `asm/alternative-macros.h`, `asm/hwcap.h`. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 70 lines, 1587 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/arch_hweight.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/archrandom.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/archrandom.h

## Purpose
Implements the RISC-V architectural random seed path using the Zkr `SEED` CSR and exposes it to the kernel random subsystem.

## Important APIs, Types, And Functions
macros/constants `ASM_RISCV_ARCHRANDOM_H`, `SEED_RETRY_LOOPS`.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
Direct includes are `asm/csr.h`, `asm/processor.h`. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 72 lines, 1534 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/archrandom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/asm-extable.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/asm-extable.h

## Purpose
Defines assembler exception-table entry encodings and helper macros for fixups, BPF, user access, and unaligned zero-padding loads.

## Important APIs, Types, And Functions
macros/constants `__ASM_ASM_EXTABLE_H`, `EX_TYPE_NONE`, `EX_TYPE_FIXUP`, `EX_TYPE_BPF`, `EX_TYPE_UACCESS_ERR_ZERO`, `EX_TYPE_LOAD_UNALIGNED_ZEROPAD`, `__ASM_EXTABLE_RAW(insn, fixup, type, data)`, `_ASM_EXTABLE(insn, fixup)`, `EX_DATA_REG_ERR_SHIFT`, `EX_DATA_REG_ERR`, `EX_DATA_REG_ZERO_SHIFT`, `EX_DATA_REG_ZERO`, `EX_DATA_REG_DATA_SHIFT`, `EX_DATA_REG_DATA`, plus 6 more.

## Control Flow
The control flow is mostly preprocessor and assembler expansion: low-level entry, trap, module, and patching code include these macros and emit exact instructions or section records at build time. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State is usually encoded in generated sections, register save areas, alternative tables, exception tables, or trap metadata rather than stored in this header. The definitions must remain stable because assembly and C code share them.

## Dependencies And Integration Points
Direct includes are `linux/bits.h`, `linux/stringify.h`, `asm/gpr-num.h`. Integrates with RISC-V assembler support, generated offsets, linker sections, alternatives, exception tables, low-level entry code, module relocation, and compiler feature tests.

## Risks And Edge Cases
Risks are instruction-encoding, section-layout, relocation, register-width, and generated-offset mistakes. A small macro change can break boot, trap entry, module loading, or runtime text patching.

## Test Signals
Test signals include defconfig/allmodconfig builds, objdump validation of emitted instructions and sections, boot smoke tests, module load/unload, alternatives/errata patch logs, exception fixup tests, and trap-entry stress.

Source read size: 86 lines, 2323 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/asm-extable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/asm-offsets.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/asm-offsets.h

## Purpose
Forwards generated C-structure offsets to RISC-V assembly sources.

## Important APIs, Types, And Functions
include-time glue with no public C type or function declarations.

## Control Flow
The control flow is mostly preprocessor and assembler expansion: low-level entry, trap, module, and patching code include these macros and emit exact instructions or section records at build time.

## State And Persistence
State is usually encoded in generated sections, register save areas, alternative tables, exception tables, or trap metadata rather than stored in this header. The definitions must remain stable because assembly and C code share them.

## Dependencies And Integration Points
Direct includes are `generated/asm-offsets.h`. Integrates with RISC-V assembler support, generated offsets, linker sections, alternatives, exception tables, low-level entry code, module relocation, and compiler feature tests.

## Risks And Edge Cases
Risks are instruction-encoding, section-layout, relocation, register-width, and generated-offset mistakes. A small macro change can break boot, trap entry, module loading, or runtime text patching.

## Test Signals
Test signals include defconfig/allmodconfig builds, objdump validation of emitted instructions and sections, boot smoke tests, module load/unload, alternatives/errata patch logs, exception fixup tests, and trap-entry stress.

Source read size: 1 lines, 35 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/asm-offsets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/asm-prototypes.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/asm-prototypes.h

## Purpose
Publishes RISC-V assembly routine prototypes to C and module symbol/version generation.

## Important APIs, Types, And Functions
types `pt_regs`; functions/prototypes `__lshrti3`, `__ashrti3`, `__ashlti3`, `enter_vector_usercopy`, `xor_regs_2_`, `xor_regs_3_`, `xor_regs_4_`, `xor_regs_5_`, `riscv_v_context_nesting_start`, `riscv_v_context_nesting_end`, `ret_from_fork_kernel`, `ret_from_fork_user`, plus 3 more; macros/constants `_ASM_RISCV_PROTOTYPES_H`, `DECLARE_DO_ERROR_INFO(name) asmlinkage void name(struct pt_regs *regs)`.

## Control Flow
The control flow is mostly preprocessor and assembler expansion: low-level entry, trap, module, and patching code include these macros and emit exact instructions or section records at build time. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State is usually encoded in generated sections, register save areas, alternative tables, exception tables, or trap metadata rather than stored in this header. The definitions must remain stable because assembly and C code share them.

## Dependencies And Integration Points
Direct includes are `linux/ftrace.h`, `asm-generic/asm-prototypes.h`. Integrates with RISC-V assembler support, generated offsets, linker sections, alternatives, exception tables, low-level entry code, module relocation, and compiler feature tests.

## Risks And Edge Cases
Risks are instruction-encoding, section-layout, relocation, register-width, and generated-offset mistakes. A small macro change can break boot, trap entry, module loading, or runtime text patching.

## Test Signals
Test signals include defconfig/allmodconfig builds, objdump validation of emitted instructions and sections, boot smoke tests, module load/unload, alternatives/errata patch logs, exception fixup tests, and trap-entry stress.

Source read size: 63 lines, 2407 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/asm-prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/asm.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/asm.h

## Purpose
Centralizes RISC-V assembly portability macros for register-width loads/stores, pointer sizes, sections, symbol annotations, and instruction emission.

## Important APIs, Types, And Functions
macros/constants `_ASM_RISCV_ASM_H`, `__ASM_STR(x)`, `ASM_INSN_I(__x)`, `__REG_SEL(a, b) __ASM_STR(a)`, `__REG_SEL(a, b) __ASM_STR(b)`, `REG_L`, `REG_S`, `REG_SC`, `REG_AMOSWAP_AQ`, `REG_ASM`, `SZREG`, `LGREG`, `SRLI`, `RISCV_PTR`, plus 9 more.

## Control Flow
The control flow is mostly preprocessor and assembler expansion: low-level entry, trap, module, and patching code include these macros and emit exact instructions or section records at build time. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State is usually encoded in generated sections, register save areas, alternative tables, exception tables, or trap metadata rather than stored in this header. The definitions must remain stable because assembly and C code share them.

## Dependencies And Integration Points
Direct includes are `asm/asm-offsets.h`. Integrates with RISC-V assembler support, generated offsets, linker sections, alternatives, exception tables, low-level entry code, module relocation, and compiler feature tests.

## Risks And Edge Cases
Risks are instruction-encoding, section-layout, relocation, register-width, and generated-offset mistakes. A small macro change can break boot, trap entry, module loading, or runtime text patching.

## Test Signals
Test signals include defconfig/allmodconfig builds, objdump validation of emitted instructions and sections, boot smoke tests, module load/unload, alternatives/errata patch logs, exception fixup tests, and trap-entry stress.

Source read size: 199 lines, 4159 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/assembler.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/assembler.h

## Purpose
Provides higher-level assembly macros for control-flow integrity properties, stack/register helpers, alternatives, and low-level entry code.

## Important APIs, Types, And Functions
macros/constants `__ASM_ASSEMBLER_H`, `NT_GNU_PROPERTY_TYPE_0`, `GNU_PROPERTY_RISCV_FEATURE_1_AND`, `GNU_PROPERTY_RISCV_FEATURE_1_ZICFILP`, `GNU_PROPERTY_RISCV_FEATURE_1_ZICFISS`, `GNU_PROPERTY_RISCV_FEATURE_1_DEFAULT`.

## Control Flow
The control flow is mostly preprocessor and assembler expansion: low-level entry, trap, module, and patching code include these macros and emit exact instructions or section records at build time.

## State And Persistence
State is usually encoded in generated sections, register save areas, alternative tables, exception tables, or trap metadata rather than stored in this header. The definitions must remain stable because assembly and C code share them.

## Dependencies And Integration Points
Direct includes are `asm/asm.h`, `asm/asm-offsets.h`, `asm/csr.h`. Integrates with RISC-V assembler support, generated offsets, linker sections, alternatives, exception tables, low-level entry code, module relocation, and compiler feature tests.

## Risks And Edge Cases
Risks are instruction-encoding, section-layout, relocation, register-width, and generated-offset mistakes. A small macro change can break boot, trap entry, module loading, or runtime text patching.

## Test Signals
Test signals include defconfig/allmodconfig builds, objdump validation of emitted instructions and sections, boot smoke tests, module load/unload, alternatives/errata patch logs, exception fixup tests, and trap-entry stress.

Source read size: 126 lines, 3456 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/assembler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/atomic.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/atomic.h

## Purpose
Implements RISC-V atomic integer APIs on AMO and LR/SC primitives with acquire, release, relaxed, and full ordering variants.

## Important APIs, Types, And Functions
functions/prototypes `arch_atomic_read`, `arch_atomic_set`, `arch_atomic64_read`, `arch_atomic64_set`, `arch_atomic_fetch_add_unless`, `arch_atomic64_fetch_add_unless`, `arch_atomic_inc_unless_negative`, `arch_atomic_dec_unless_positive`, `arch_atomic_dec_if_positive`, `arch_atomic64_inc_unless_negative`, `arch_atomic64_dec_unless_positive`, `arch_atomic64_dec_if_positive`; macros/constants `_ASM_RISCV_ATOMIC_H`, `__atomic_acquire_fence()`, `__atomic_release_fence()`, `ATOMIC64_INIT(i) { (i)`, `ATOMIC_OP(op, asm_op, I, asm_type, c_type, prefix)`, `ATOMIC_OPS(op, asm_op, I)`, `ATOMIC_FETCH_OP(op, asm_op, I, asm_type, c_type, prefix)`, `ATOMIC_OP_RETURN(op, asm_op, c_op, I, asm_type, c_type, prefix)`, `ATOMIC_OPS(op, asm_op, c_op, I)`, `arch_atomic_add_return_relaxed`, `arch_atomic_sub_return_relaxed`, `arch_atomic_add_return`, `arch_atomic_sub_return`, `arch_atomic_fetch_add_relaxed`, plus 35 more.

## Control Flow
The header is primarily declarative. Runtime behavior occurs in the including architecture implementation files and generic Linux subsystems that consume the constants, types, macros, and prototypes defined here. Special attention: arithmetic operations are generated by macros across 32-bit and 64-bit atomic types; fetch/return variants insert the exact ordering suffixes expected by the generic atomic API.

## State And Persistence
The header itself owns no filesystem or durable state. It defines ABI-like constants or inline behavior consumed by longer-lived kernel objects.

## Dependencies And Integration Points
Direct includes are `asm-generic/atomic64.h`, `asm/cmpxchg.h`. Integrates with generic Linux architecture headers and RISC-V implementation files through include-time contracts.

## Risks And Edge Cases
The main risk is that generic code treats these definitions as architecture ABI. Renaming, renumbering, or changing inline semantics without matching implementation changes can create build-only or boot-time failures.

## Test Signals
Test signals include architecture build coverage, include dependency checks, and subsystem tests for the generic code that consumes this header.

Source read size: 353 lines, 10470 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/barrier.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/barrier.h

## Purpose
Defines RISC-V memory barrier, SMP barrier, acquire/release, and conditional-load primitives.

## Important APIs, Types, And Functions
macros/constants `_ASM_RISCV_BARRIER_H`, `__mb() RISCV_FENCE(iorw, iorw)`, `__rmb() RISCV_FENCE(ir, ir)`, `__wmb() RISCV_FENCE(ow, ow)`, `__smp_mb() RISCV_FENCE(rw, rw)`, `__smp_rmb() RISCV_FENCE(r, r)`, `__smp_wmb() RISCV_FENCE(w, w)`, `smp_mb__after_spinlock() RISCV_FENCE(iorw, iorw)`, `__smp_store_release(p, v)`, `__smp_load_acquire(p)`, `smp_cond_load_relaxed(ptr, cond_expr)`.

## Control Flow
The header is primarily declarative. Runtime behavior occurs in the including architecture implementation files and generic Linux subsystems that consume the constants, types, macros, and prototypes defined here. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
The header itself owns no filesystem or durable state. It defines ABI-like constants or inline behavior consumed by longer-lived kernel objects.

## Dependencies And Integration Points
Direct includes are `asm/cmpxchg.h`, `asm/fence.h`, `asm-generic/barrier.h`. Integrates with generic Linux architecture headers and RISC-V implementation files through include-time contracts.

## Risks And Edge Cases
The main risk is that generic code treats these definitions as architecture ABI. Renaming, renumbering, or changing inline semantics without matching implementation changes can create build-only or boot-time failures.

## Test Signals
Test signals include architecture build coverage, include dependency checks, and subsystem tests for the generic code that consumes this header.

Source read size: 87 lines, 2727 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/bitops.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/bitops.h

## Purpose
Implements architecture bit operations using Zbb bit-scan alternatives and AMO-based atomic bit manipulation.

## Important APIs, Types, And Functions
functions/prototypes `variable_fls`, `arch_test_and_set_bit`, `arch_test_and_clear_bit`, `arch_test_and_change_bit`, `arch_set_bit`, `arch_clear_bit`, `arch_change_bit`, `arch_test_and_set_bit_lock`, `arch_clear_bit_unlock`, `arch___clear_bit_unlock`, `arch_xor_unlock_is_negative_byte`; macros/constants `_ASM_RISCV_BITOPS_H`, `__HAVE_ARCH___FFS`, `__HAVE_ARCH___FLS`, `__HAVE_ARCH_FFS`, `__HAVE_ARCH_FLS`, `CTZW`, `CLZW`, `__ffs(word)`, `__fls(word)`, `ffs(x) (__builtin_constant_p(x) ? __builtin_ffs(x) : variable_ffs(x))`, `fls(x)`, `__AMO(op)`, `__test_and_op_bit_ord(op, mod, nr, addr, ord)`, `__op_bit_ord(op, mod, nr, addr, ord)`, plus 4 more.

## Control Flow
The header is primarily declarative. Runtime behavior occurs in the including architecture implementation files and generic Linux subsystems that consume the constants, types, macros, and prototypes defined here. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
The header itself owns no filesystem or durable state. It defines ABI-like constants or inline behavior consumed by longer-lived kernel objects.

## Dependencies And Integration Points
Direct includes are `linux/compiler.h`, `asm/barrier.h`, `asm/bitsperlong.h`, `asm-generic/bitops/__ffs.h`, `asm-generic/bitops/__fls.h`, `asm-generic/bitops/ffs.h`, `asm-generic/bitops/fls.h`, `asm/alternative-macros.h`, `asm/hwcap.h`, `asm-generic/bitops/ffz.h`, plus 9 more. Integrates with generic Linux architecture headers and RISC-V implementation files through include-time contracts.

## Risks And Edge Cases
The main risk is that generic code treats these definitions as architecture ABI. Renaming, renumbering, or changing inline semantics without matching implementation changes can create build-only or boot-time failures.

## Test Signals
Test signals include architecture build coverage, include dependency checks, and subsystem tests for the generic code that consumes this header.

Source read size: 362 lines, 9926 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/bitops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/bug.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/bug.h

## Purpose
Defines RISC-V BUG/WARN trap instruction encoding, bug-table entries, and trap-reporting interfaces.

## Important APIs, Types, And Functions
types `bug_entry`, `pt_regs`, `task_struct`; functions/prototypes `__show_regs`, `die`, `do_trap`; macros/constants `_ASM_RISCV_BUG_H`, `__INSN_LENGTH_MASK`, `__INSN_LENGTH_32`, `__COMPRESSED_INSN_MASK`, `__BUG_INSN_32`, `__BUG_INSN_16`, `GET_INSN_LENGTH(insn)`, `__BUG_ENTRY_ADDR`, `__BUG_ENTRY_FILE(file)`, `__BUG_ENTRY(file, line, flags)`, `ARCH_WARN_ASM(file, line, flags, size)`, `__BUG_FLAGS(cond_str, flags)`, `BUG()`, `__WARN_FLAGS(cond_str, flags) __BUG_FLAGS(cond_str, BUGFLAG_WARNING|(flags))`, plus 2 more.

## Control Flow
Runtime flow is driven by dynamic patching and trap/debug callbacks: ftrace, jump-labels, kprobes, KGDB, BUG, and exception tables rewrite or interpret instruction streams at runtime. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State is held in patched text, per-probe/ftrace records, exception table entries, debug register snapshots, static keys, or trap frames depending on the subsystem.

## Dependencies And Integration Points
Direct includes are `linux/compiler.h`, `linux/const.h`, `linux/types.h`, `asm/asm.h`, `asm-generic/bug.h`. Integrates with ftrace, jump labels, kprobes, KGDB, BUG/WARN, exception-table fixups, perf, and architecture trap handling.

## Risks And Edge Cases
Risks include patching the wrong instruction width, corrupting breakpoint/probe/ftrace state, exception-table data packing mistakes, and debug/trap handlers losing register state.

## Test Signals
Test signals include ftrace and function-graph selftests, static-key/jump-label tests, kprobes/KGDB tests, BUG/WARN/oops decoding, perf callchain checks, and exception-table fault-injection tests.

Source read size: 99 lines, 2472 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/bug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/bugs.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/bugs.h

## Purpose
Declares runtime CPU-bug mitigation hooks, currently including T-Head GhostWrite state and controls.

## Important APIs, Types, And Functions
types `mitigation_state`; functions/prototypes `ghostwrite_set_vulnerable`, `ghostwrite_enable_mitigation`, `ghostwrite_get_state`; macros/constants `__ASM_BUGS_H`.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
It has no direct includes. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 22 lines, 463 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/bugs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/cache.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/cache.h

## Purpose
Defines RISC-V cacheline sizing and DMA/slab alignment contracts.

## Important APIs, Types, And Functions
functions/prototypes `dma_get_cache_alignment`, `dma_cache_alignment`; macros/constants `_ASM_RISCV_CACHE_H`, `L1_CACHE_SHIFT`, `L1_CACHE_BYTES`, `ARCH_DMA_MINALIGN`, `ARCH_KMALLOC_MINALIGN`, `ARCH_SLAB_MINALIGN`, `dma_get_cache_alignment`.

## Control Flow
The header is primarily declarative. Runtime behavior occurs in the including architecture implementation files and generic Linux subsystems that consume the constants, types, macros, and prototypes defined here. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
The header itself owns no filesystem or durable state. It defines ABI-like constants or inline behavior consumed by longer-lived kernel objects.

## Dependencies And Integration Points
It has no direct includes. Integrates with generic Linux architecture headers and RISC-V implementation files through include-time contracts.

## Risks And Edge Cases
The main risk is that generic code treats these definitions as architecture ABI. Renaming, renumbering, or changing inline semantics without matching implementation changes can create build-only or boot-time failures.

## Test Signals
Test signals include architecture build coverage, include dependency checks, and subsystem tests for the generic code that consumes this header.

Source read size: 40 lines, 899 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/cacheflush.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/cacheflush.h

## Purpose
Declares cache and instruction-cache flush helpers, DMA-cache alignment setup, CBO support discovery, and the userspace icache-flush syscall flags.

## Important APIs, Types, And Functions
types `folio`, `page`, `mm_struct`; functions/prototypes `local_flush_icache_all`, `local_flush_icache_range`, `flush_dcache_folio`, `flush_dcache_page`, `flush_cache_vmap`, `flush_icache_all`, `flush_icache_mm`, `flush_icache_range`, `riscv_init_cbo_blocksizes`, `riscv_noncoherent_supported`, `riscv_set_dma_cache_alignment`, `sizeof`, plus 3 more; macros/constants `_ASM_RISCV_CACHEFLUSH_H`, `PG_dcache_clean`, `flush_dcache_folio`, `ARCH_IMPLEMENTS_FLUSH_DCACHE_PAGE`, `flush_icache_user_page(vma, pg, addr, len)`, `flush_cache_vmap`, `flush_cache_vmap_early(start, end) local_flush_tlb_kernel_range(start, end)`, `flush_icache_all() local_flush_icache_all()`, `flush_icache_mm(mm, local) flush_icache_all()`, `flush_icache_range`, `SYS_RISCV_FLUSH_ICACHE_LOCAL`, `SYS_RISCV_FLUSH_ICACHE_ALL`.

## Control Flow
Runtime flow is reached through generic MM, page-table, fault, TLB, and mapping callbacks. The header supplies inline conversions and declarations that the implementation files call during context switch, map/unmap, and flush paths. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State is carried in `mm_struct`, page tables, ASIDs, fixed mappings, folios, cache/TLB state, or architecture context fields; this header defines how those state holders are interpreted.

## Dependencies And Integration Points
Direct includes are `linux/mm.h`, `asm-generic/cacheflush.h`. Integrates with Linux MM, page-table helpers, TLB shootdown, cache maintenance, hugetlb, KASAN/KFENCE, EFI mapping, kexec, and architecture fault handling.

## Risks And Edge Cases
Risks include stale cache/TLB state, wrong virtual/physical conversions, ASID/version reuse bugs, fixed-map overlap, hugepage PTE corruption, and ABI changes in ELF or image headers.

## Test Signals
Test signals include MM selftests, mmap/mprotect/fork/exec stress, hugetlb tests, KASAN/KFENCE boot, kexec/crashkernel boot, EFI boot, cacheflush tests, and TLB shootdown stress.

Source read size: 107 lines, 2780 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/cacheflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/cacheinfo.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/cacheinfo.h

## Purpose
Connects RISC-V cache discovery to the generic Linux cacheinfo subsystem.

## Important APIs, Types, And Functions
types `riscv_cacheinfo_ops`, `attribute_group`, `cacheinfo`, `cache_type`; functions/prototypes `riscv_set_cacheinfo_ops`; macros/constants `_ASM_RISCV_CACHEINFO_H`.

## Control Flow
The header is primarily declarative. Runtime behavior occurs in the including architecture implementation files and generic Linux subsystems that consume the constants, types, macros, and prototypes defined here.

## State And Persistence
The header itself owns no filesystem or durable state. It defines ABI-like constants or inline behavior consumed by longer-lived kernel objects.

## Dependencies And Integration Points
Direct includes are `linux/cacheinfo.h`. Integrates with generic Linux architecture headers and RISC-V implementation files through include-time contracts.

## Risks And Edge Cases
The main risk is that generic code treats these definitions as architecture ABI. Renaming, renumbering, or changing inline semantics without matching implementation changes can create build-only or boot-time failures.

## Test Signals
Test signals include architecture build coverage, include dependency checks, and subsystem tests for the generic code that consumes this header.

Source read size: 20 lines, 511 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/cacheinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/cfi.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/cfi.h

## Purpose
Declares RISC-V control-flow-integrity failure handling and BPF call annotation behavior.

## Important APIs, Types, And Functions
types `pt_regs`, `bug_trap_type`; functions/prototypes `handle_cfi_failure`; macros/constants `_ASM_RISCV_CFI_H`, `__bpfcall`.

## Control Flow
Runtime flow is driven by dynamic patching and trap/debug callbacks: ftrace, jump-labels, kprobes, KGDB, BUG, and exception tables rewrite or interpret instruction streams at runtime. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State is held in patched text, per-probe/ftrace records, exception table entries, debug register snapshots, static keys, or trap frames depending on the subsystem.

## Dependencies And Integration Points
Direct includes are `linux/bug.h`. Integrates with ftrace, jump labels, kprobes, KGDB, BUG/WARN, exception-table fixups, perf, and architecture trap handling.

## Risks And Edge Cases
Risks include patching the wrong instruction width, corrupting breakpoint/probe/ftrace state, exception-table data packing mistakes, and debug/trap handlers losing register state.

## Test Signals
Test signals include ftrace and function-graph selftests, static-key/jump-label tests, kprobes/KGDB tests, BUG/WARN/oops decoding, perf callchain checks, and exception-table fault-injection tests.

Source read size: 24 lines, 485 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/cfi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/checksum.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/checksum.h

## Purpose
Selects RISC-V checksum implementations for IP and IPv6 checksum paths.

## Important APIs, Types, And Functions
types `in6_addr`; functions/prototypes `do_csum`; macros/constants `__ASM_RISCV_CHECKSUM_H`, `ip_fast_csum`, `do_csum`, `_HAVE_ARCH_IPV6_CSUM`.

## Control Flow
Runtime flow is driven by dynamic patching and trap/debug callbacks: ftrace, jump-labels, kprobes, KGDB, BUG, and exception tables rewrite or interpret instruction streams at runtime. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State is held in patched text, per-probe/ftrace records, exception table entries, debug register snapshots, static keys, or trap frames depending on the subsystem.

## Dependencies And Integration Points
Direct includes are `linux/in6.h`, `linux/uaccess.h`, `asm-generic/checksum.h`. Integrates with ftrace, jump labels, kprobes, KGDB, BUG/WARN, exception-table fixups, perf, and architecture trap handling.

## Risks And Edge Cases
Risks include patching the wrong instruction width, corrupting breakpoint/probe/ftrace state, exception-table data packing mistakes, and debug/trap handlers losing register state.

## Test Signals
Test signals include ftrace and function-graph selftests, static-key/jump-label tests, kprobes/KGDB tests, BUG/WARN/oops decoding, perf callchain checks, and exception-table fault-injection tests.

Source read size: 87 lines, 2466 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/checksum.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/clint.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/clint.h

## Purpose
Declares CLINT MMIO symbols used by early timer and interrupt code.

## Important APIs, Types, And Functions
functions/prototypes `clint_time_val`; macros/constants `_ASM_RISCV_CLINT_H`.

## Control Flow
Runtime flow is a wrapper sequence around MMIO or port-I/O reads and writes: optional fences bracket raw loads/stores, endian conversion is applied for CPU-visible values, and generic driver code calls the resulting accessors. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
No durable state is stored by the header. Accessors mutate device-visible MMIO state and rely on fences to preserve ordering against CPUs, DMA, and devices.

## Dependencies And Integration Points
Direct includes are `linux/types.h`, `asm/mmio.h`. Integrates with driver MMIO APIs, PCI I/O space, generic `asm-generic/io.h`, DMA/noncoherent cache hooks, and RISC-V fence semantics.

## Risks And Edge Cases
Risks are missing fences, wrong endian conversion, noncoherent DMA cache omissions, and incorrect port/MMIO address translation, which can produce device data corruption or ordering bugs.

## Test Signals
Test signals include driver probe and DMA tests on coherent and noncoherent systems, PCI enumeration, MMIO ordering litmus tests, CBO cache-maintenance tests, and sparse/endian build checks.

Source read size: 26 lines, 797 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/clint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/clocksource.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/clocksource.h

## Purpose
Includes the RISC-V vDSO clocksource contract for kernel clocksource integration.

## Important APIs, Types, And Functions
macros/constants `_ASM_CLOCKSOURCE_H`.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
Direct includes are `asm/vdso/clocksource.h`. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 7 lines, 136 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/clocksource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/cmpxchg.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/cmpxchg.h

## Purpose
Implements exchange, compare-exchange, masked subword atomics, 128-bit CAS support, and wait-on-change helpers.

## Important APIs, Types, And Functions
types `__u128_halves`; functions/prototypes `__cmpwait`; macros/constants `_ASM_RISCV_CMPXCHG_H`, `__arch_xchg_masked`, `__arch_xchg(sfx, prepend, append, r, p, n)`, `_arch_xchg`, `arch_xchg_relaxed(ptr, x)`, `arch_xchg_acquire(ptr, x)`, `arch_xchg_release(ptr, x)`, `arch_xchg(ptr, x)`, `xchg32(ptr, x)`, `xchg64(ptr, x)`, `__arch_cmpxchg_masked`, `__arch_cmpxchg`, `_arch_cmpxchg`, `SC_SFX(x)`, plus 20 more.

## Control Flow
The header is primarily declarative. Runtime behavior occurs in the including architecture implementation files and generic Linux subsystems that consume the constants, types, macros, and prototypes defined here. Special attention: subword exchange/compare-exchange is implemented with masked LR/SC loops, while Zacas/alternative paths are available for wider compare-exchange where supported.

## State And Persistence
The header itself owns no filesystem or durable state. It defines ABI-like constants or inline behavior consumed by longer-lived kernel objects.

## Dependencies And Integration Points
Direct includes are `linux/bug.h`, `asm/alternative-macros.h`, `asm/fence.h`, `asm/hwcap.h`, `asm/insn-def.h`, `asm/cpufeature-macros.h`, `asm/processor.h`, `asm/errata_list.h`. Integrates with generic Linux architecture headers and RISC-V implementation files through include-time contracts.

## Risks And Edge Cases
The main risk is that generic code treats these definitions as architecture ABI. Renaming, renumbering, or changing inline semantics without matching implementation changes can create build-only or boot-time failures.

## Test Signals
Test signals include architecture build coverage, include dependency checks, and subsystem tests for the generic code that consumes this header.

Source read size: 447 lines, 12563 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/cmpxchg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/compat.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/compat.h

## Purpose
Defines 32-bit compat task detection and register conversion helpers for 64-bit kernels running RV32 userspace.

## Important APIs, Types, And Functions
types `thread_info`, `compat_user_regs_struct`, `pt_regs`; functions/prototypes `is_compat_task`, `is_compat_thread`, `set_compat_task`, `regs_to_cregs`, `cregs_to_regs`; macros/constants `__ASM_COMPAT_H`, `COMPAT_UTS_MACHINE`.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
Direct includes are `linux/types.h`, `linux/sched.h`, `asm-generic/compat.h`. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 147 lines, 4152 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/cpu.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/cpu.h

## Purpose
Provides the minimal RISC-V CPU header hook used by generic architecture code.

## Important APIs, Types, And Functions
macros/constants `_ASM_CPU_H`.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
It has no direct includes. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 8 lines, 172 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/cpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/cpu_ops.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/cpu_ops.h

## Purpose
Defines the CPU bring-up operations table used by SMP boot and hotplug paths.

## Important APIs, Types, And Functions
types `cpu_operations`, `task_struct`; functions/prototypes `cpu_ops_spinwait`, `cpu_ops`; macros/constants `__ASM_CPU_OPS_H`.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
Direct includes are `linux/init.h`, `linux/sched.h`, `linux/threads.h`. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 35 lines, 971 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/cpu_ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/cpu_ops_sbi.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/cpu_ops_sbi.h

## Purpose
Declares the SBI-backed CPU operations and hart boot-data handoff structure.

## Important APIs, Types, And Functions
types `cpu_operations`, `sbi_hart_boot_data`; functions/prototypes `cpu_ops_sbi`; macros/constants `__ASM_CPU_OPS_SBI_H`.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
Direct includes are `linux/init.h`, `linux/sched.h`, `linux/threads.h`. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 27 lines, 610 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/cpu_ops_sbi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/cpufeature-macros.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/cpufeature-macros.h

## Purpose
Provides static-key/alternative aware helpers for fast RISC-V ISA extension tests.

## Important APIs, Types, And Functions
functions/prototypes `__riscv_isa_extension_available`, `__riscv_has_extension_likely`, `__riscv_has_extension_unlikely`, `riscv_has_extension_unlikely`, `riscv_has_extension_likely`; macros/constants `_ASM_CPUFEATURE_MACROS_H`, `STANDARD_EXT`, `riscv_isa_extension_available(isa_bitmap, ext)`.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
Direct includes are `asm/hwcap.h`, `asm/alternative-macros.h`. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 66 lines, 1706 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/cpufeature-macros.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/cpufeature.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/cpufeature.h

## Purpose
Declares CPU and ISA feature discovery state, extension descriptors, unaligned-access probing, and ELF hwcap export helpers.

## Important APIs, Types, And Functions
types `riscv_cpuinfo`, `riscv_isainfo`, `seq_operations`, `work_struct`, `riscv_isa_ext_data`; functions/prototypes `unaligned_access_init`, `cpu_online_unaligned_access_init`, `unaligned_emulation_finish`, `unaligned_ctl_available`, `misaligned_traps_can_delegate`, `check_vector_unaligned_access_emulated`, `has_fast_unaligned_accesses`, `riscv_get_elf_hwcap`, `riscv_isa_extension_base`, `riscv_cpu_has_extension_likely`, `riscv_cpu_has_extension_unlikely`, `cpu_supports_shadow_stack`, plus 5 more; macros/constants `_ASM_CPUFEATURE_H`, `_RISCV_ISA_EXT_DATA(_name, _id, _subset_exts, _subset_exts_size, _validate)`, `__RISCV_ISA_EXT_DATA(_name, _id) _RISCV_ISA_EXT_DATA(_name, _id, NULL, 0, NULL)`, `__RISCV_ISA_EXT_DATA_VALIDATE(_name, _id, _validate)`, `__RISCV_ISA_EXT_BUNDLE(_name, _bundled_exts)`, `__RISCV_ISA_EXT_BUNDLE_VALIDATE(_name, _bundled_exts, _validate)`, `__RISCV_ISA_EXT_SUPERSET(_name, _id, _sub_exts)`, `__RISCV_ISA_EXT_SUPERSET_VALIDATE(_name, _id, _sub_exts, _validate)`.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
Direct includes are `linux/bitmap.h`, `linux/jump_label.h`, `linux/workqueue.h`, `linux/kconfig.h`, `linux/percpu-defs.h`, `linux/threads.h`, `asm/hwcap.h`, `asm/cpufeature-macros.h`. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 167 lines, 4991 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/cpufeature.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/cpuidle.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/cpuidle.h

## Purpose
Defines the RISC-V idle primitive used by cpuidle and generic idle loops.

## Important APIs, Types, And Functions
functions/prototypes `cpu_do_idle`; macros/constants `_ASM_RISCV_CPUIDLE_H`.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
Direct includes are `asm/barrier.h`, `asm/processor.h`. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 24 lines, 450 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/cpuidle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/crash_reserve.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/crash_reserve.h

## Purpose
Defines architecture limits and alignment for crashkernel reservation.

## Important APIs, Types, And Functions
functions/prototypes `memblock_end_of_DRAM`; macros/constants `_RISCV_CRASH_RESERVE_H`, `CRASH_ALIGN`, `CRASH_ADDR_LOW_MAX`, `CRASH_ADDR_HIGH_MAX`.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
It has no direct includes. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 11 lines, 291 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/crash_reserve.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/csr.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/csr.h

## Purpose
Defines RISC-V CSR numbers, status bits, exception causes, extension state masks, PMP/HSTATUS/HGATP fields, and CSR access macros.

## Important APIs, Types, And Functions
macros/constants `_ASM_RISCV_CSR_H`, `SR_SIE`, `SR_MIE`, `SR_SPIE`, `SR_MPIE`, `SR_SPP`, `SR_MPP`, `SR_SUM`, `SR_SPELP`, `SR_MPELP`, `SR_ELP`, `SR_FS`, `SR_FS_OFF`, `SR_FS_INITIAL`, plus 380 more.

## Control Flow
The header is primarily declarative. Runtime behavior occurs in the including architecture implementation files and generic Linux subsystems that consume the constants, types, macros, and prototypes defined here. Special attention: this file is the numeric source of truth for status bits, SATP/HGATP layout, exception and interrupt causes, PMP fields, state-enable bits, seed CSR fields, and inline CSR read/write/set/clear/swap helpers.

## State And Persistence
The header itself owns no filesystem or durable state. It defines ABI-like constants or inline behavior consumed by longer-lived kernel objects.

## Dependencies And Integration Points
Direct includes are `asm/asm.h`, `linux/bits.h`. Integrates with generic Linux architecture headers and RISC-V implementation files through include-time contracts.

## Risks And Edge Cases
The main risk is that generic code treats these definitions as architecture ABI. Renaming, renumbering, or changing inline semantics without matching implementation changes can create build-only or boot-time failures.

## Test Signals
Test signals include architecture build coverage, include dependency checks, and subsystem tests for the generic code that consumes this header.

Source read size: 611 lines, 17738 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/csr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/current.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/current.h

## Purpose
Implements `current` retrieval from the RISC-V thread pointer register.

## Important APIs, Types, And Functions
types `task_struct`, `thread_info`; functions/prototypes `get_current`; macros/constants `_ASM_RISCV_CURRENT_H`, `current`.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
Direct includes are `linux/bug.h`, `linux/compiler.h`. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 40 lines, 1003 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/current.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/delay.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/delay.h

## Purpose
Declares RISC-V delay-loop calibration and udelay/ndelay entry points.

## Important APIs, Types, And Functions
functions/prototypes `udelay`, `ndelay`, `__delay`, `riscv_timebase`; macros/constants `_ASM_RISCV_DELAY_H`, `udelay`, `ndelay`.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
It has no direct includes. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 20 lines, 471 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/delay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/dma-noncoherent.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/dma-noncoherent.h

## Purpose
Declares non-coherent DMA cache-operation registration hooks for RISC-V platforms.

## Important APIs, Types, And Functions
types `riscv_nonstd_cache_ops`; functions/prototypes `riscv_noncoherent_register_cache_ops`, `noncoherent_cache_ops`; macros/constants `__ASM_DMA_NONCOHERENT_H`.

## Control Flow
Runtime flow is a wrapper sequence around MMIO or port-I/O reads and writes: optional fences bracket raw loads/stores, endian conversion is applied for CPU-visible values, and generic driver code calls the resulting accessors.

## State And Persistence
No durable state is stored by the header. Accessors mutate device-visible MMIO state and rely on fences to preserve ordering against CPUs, DMA, and devices.

## Dependencies And Integration Points
Direct includes are `linux/dma-direct.h`. Integrates with driver MMIO APIs, PCI I/O space, generic `asm-generic/io.h`, DMA/noncoherent cache hooks, and RISC-V fence semantics.

## Risks And Edge Cases
Risks are missing fences, wrong endian conversion, noncoherent DMA cache omissions, and incorrect port/MMIO address translation, which can produce device data corruption or ordering bugs.

## Test Signals
Test signals include driver probe and DMA tests on coherent and noncoherent systems, PCI enumeration, MMIO ordering litmus tests, CBO cache-maintenance tests, and sparse/endian build checks.

Source read size: 28 lines, 835 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/dma-noncoherent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/dmi.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/dmi.h

## Purpose
Maps generic DMI early/remap/allocation hooks to RISC-V memremap and allocation primitives.

## Important APIs, Types, And Functions
macros/constants `__ASM_DMI_H`, `dmi_early_remap(x, l) memremap(x, l, MEMREMAP_WB)`, `dmi_early_unmap(x, l) memunmap(x)`, `dmi_remap(x, l) memremap(x, l, MEMREMAP_WB)`, `dmi_unmap(x) memunmap(x)`, `dmi_alloc(l) kzalloc(l, GFP_KERNEL)`.

## Control Flow
Runtime flow is a wrapper sequence around MMIO or port-I/O reads and writes: optional fences bracket raw loads/stores, endian conversion is applied for CPU-visible values, and generic driver code calls the resulting accessors.

## State And Persistence
No durable state is stored by the header. Accessors mutate device-visible MMIO state and rely on fences to preserve ordering against CPUs, DMA, and devices.

## Dependencies And Integration Points
Direct includes are `linux/io.h`, `linux/slab.h`. Integrates with driver MMIO APIs, PCI I/O space, generic `asm-generic/io.h`, DMA/noncoherent cache hooks, and RISC-V fence semantics.

## Risks And Edge Cases
Risks are missing fences, wrong endian conversion, noncoherent DMA cache omissions, and incorrect port/MMIO address translation, which can produce device data corruption or ordering bugs.

## Test Signals
Test signals include driver probe and DMA tests on coherent and noncoherent systems, PCI enumeration, MMIO ordering litmus tests, CBO cache-maintenance tests, and sparse/endian build checks.

Source read size: 24 lines, 640 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/dmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/efi.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/efi.h

## Purpose
Declares RISC-V EFI mapping, virtual-call setup, kernel-image placement, initrd limit, and icache-sync helpers.

## Important APIs, Types, And Functions
types `mm_struct`; functions/prototypes `efi_init`, `efi_create_mapping`, `efi_set_mapping_permissions`, `efi_get_max_initrd_addr`, `efi_get_kimg_min_align`, `arch_efi_call_virt_setup`, `arch_efi_call_virt_teardown`, `stext_offset`, `efi_icache_sync`; macros/constants `_ASM_EFI_H`, `efi_init()`, `ARCH_EFI_IRQ_FLAGS_MASK`, `EFI_KIMG_PREFERRED_ADDRESS`.

## Control Flow
Runtime flow is reached through generic MM, page-table, fault, TLB, and mapping callbacks. The header supplies inline conversions and declarations that the implementation files call during context switch, map/unmap, and flush paths. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State is carried in `mm_struct`, page tables, ASIDs, fixed mappings, folios, cache/TLB state, or architecture context fields; this header defines how those state holders are interpreted.

## Dependencies And Integration Points
Direct includes are `asm/csr.h`, `asm/io.h`, `asm/mmu_context.h`, `asm/ptrace.h`, `asm/tlbflush.h`, `asm/pgalloc.h`. Integrates with Linux MM, page-table helpers, TLB shootdown, cache maintenance, hugetlb, KASAN/KFENCE, EFI mapping, kexec, and architecture fault handling.

## Risks And Edge Cases
Risks include stale cache/TLB state, wrong virtual/physical conversions, ASID/version reuse bugs, fixed-map overlap, hugepage PTE corruption, and ABI changes in ELF or image headers.

## Test Signals
Test signals include MM selftests, mmap/mprotect/fork/exec stress, hugetlb tests, KASAN/KFENCE boot, kexec/crashkernel boot, EFI boot, cacheflush tests, and TLB shootdown stress.

Source read size: 50 lines, 1209 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/efi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/elf.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/elf.h

## Purpose
Defines the RISC-V ELF ABI hooks, hwcap/auxv export, core-reg copying, compat ELF checks, and personality setup.

## Important APIs, Types, And Functions
types `linux_binprm`, `user_regs_struct`; functions/prototypes `compat_elf_check_arch`, `arch_setup_additional_pages`, `compat_arch_setup_additional_pages`, `elf_hwcap`; macros/constants `_ASM_RISCV_ELF_H`, `ELF_ARCH`, `ELF_CLASS`, `ELF_DATA`, `elf_check_arch(x) (((x)->e_machine == EM_RISCV)`, `compat_elf_check_arch`, `CORE_DUMP_USE_REGSET`, `ELF_FDPIC_CORE_EFLAGS`, `ELF_EXEC_PAGESIZE`, `ELF_ET_DYN_BASE`, `STACK_RND_MASK`, `ELF_HWCAP`, `ELF_FDPIC_PLAT_INIT(_r, _exec_map_addr, _interp_map_addr, dynamic_addr)`, `ELF_PLATFORM`, plus 7 more.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
Direct includes are `uapi/linux/elf.h`, `linux/compat.h`, `uapi/asm/elf.h`, `asm/auxvec.h`, `asm/byteorder.h`, `asm/cacheinfo.h`, `asm/cpufeature.h`. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 156 lines, 4748 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/entry-common.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/entry-common.h

## Purpose
Declares C entry points reached from low-level exception, page-fault, breakpoint, misaligned-access, vector, and CFI paths.

## Important APIs, Types, And Functions
types `pt_regs`; functions/prototypes `arch_exit_to_user_mode_prepare`, `handle_page_fault`, `handle_break`, `handle_misaligned_load`, `handle_misaligned_store`, `handle_user_cfi_violation`; macros/constants `_ASM_RISCV_ENTRY_COMMON_H`, `arch_exit_to_user_mode_prepare`.

## Control Flow
The header is primarily declarative. Runtime behavior occurs in the including architecture implementation files and generic Linux subsystems that consume the constants, types, macros, and prototypes defined here. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
The header itself owns no filesystem or durable state. It defines ABI-like constants or inline behavior consumed by longer-lived kernel objects.

## Dependencies And Integration Points
Direct includes are `asm/stacktrace.h`, `asm/thread_info.h`, `asm/vector.h`. Integrates with generic Linux architecture headers and RISC-V implementation files through include-time contracts.

## Risks And Edge Cases
The main risk is that generic code treats these definitions as architecture ABI. Renaming, renumbering, or changing inline semantics without matching implementation changes can create build-only or boot-time failures.

## Test Signals
Test signals include architecture build coverage, include dependency checks, and subsystem tests for the generic code that consumes this header.

Source read size: 45 lines, 1119 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/entry-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/errata_list.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/errata_list.h

## Purpose
Defines alternative-instruction macros for RISC-V architectural and vendor errata, including fence, page-fault, CMO, and PMA/PBMT substitutions.

## Important APIs, Types, And Functions
macros/constants `ASM_ERRATA_LIST_H`, `ALT_INSN_FAULT(x)`, `ALT_PAGE_FAULT(x)`, `ALT_SFENCE_VMA_ASID(asid)`, `ALT_SFENCE_VMA_ADDR(addr)`, `ALT_SFENCE_VMA_ADDR_ASID(addr, asid)`, `ALT_RISCV_PAUSE()`, `ALT_SVPBMT_SHIFT`, `ALT_THEAD_MAE_SHIFT`, `ALT_SVPBMT(_val, prot)`, `ALT_THEAD_PMA(_val)`, `ALT_CMO_OP(_op, _start, _size, _cachesize)`, `THEAD_C9XX_RV_IRQ_PMU`, `THEAD_C9XX_CSR_SCOUNTEROF`.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
Direct includes are `asm/csr.h`, `asm/insn-def.h`, `asm/hwcap.h`, `asm/vendorid_list.h`, `asm/errata_list_vendors.h`, `asm/vendor_extensions/mips.h`. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 122 lines, 3806 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/errata_list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/errata_list_vendors.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/errata_list_vendors.h

## Purpose
Assigns vendor errata IDs used by the alternatives and errata patching infrastructure.

## Important APIs, Types, And Functions
macros/constants `ASM_ERRATA_LIST_VENDORS_H`, `ERRATA_ANDES_NO_IOCP`, `ERRATA_ANDES_NUMBER`, `ERRATA_SIFIVE_CIP_453`, `ERRATA_SIFIVE_CIP_1200`, `ERRATA_SIFIVE_NUMBER`, `ERRATA_THEAD_MAE`, `ERRATA_THEAD_PMU`, `ERRATA_THEAD_GHOSTWRITE`, `ERRATA_THEAD_NUMBER`, `ERRATA_MIPS_P8700_PAUSE_OPCODE`, `ERRATA_MIPS_NUMBER`.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
It has no direct includes. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 29 lines, 638 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/errata_list_vendors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/exec.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/exec.h

## Purpose
Declares RISC-V stack-alignment behavior for exec.

## Important APIs, Types, And Functions
functions/prototypes `arch_align_stack`; macros/constants `__ASM_EXEC_H`.

## Control Flow
The header is primarily declarative. Runtime behavior occurs in the including architecture implementation files and generic Linux subsystems that consume the constants, types, macros, and prototypes defined here.

## State And Persistence
The header itself owns no filesystem or durable state. It defines ABI-like constants or inline behavior consumed by longer-lived kernel objects.

## Dependencies And Integration Points
It has no direct includes. Integrates with generic Linux architecture headers and RISC-V implementation files through include-time contracts.

## Risks And Edge Cases
The main risk is that generic code treats these definitions as architecture ABI. Renaming, renumbering, or changing inline semantics without matching implementation changes can create build-only or boot-time failures.

## Test Signals
Test signals include architecture build coverage, include dependency checks, and subsystem tests for the generic code that consumes this header.

Source read size: 8 lines, 172 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/exec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/extable.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/extable.h

## Purpose
Declares RISC-V relative exception-table format and fixup handlers.

## Important APIs, Types, And Functions
types `exception_table_entry`, `pt_regs`; functions/prototypes `fixup_exception`, `ex_handler_bpf`; macros/constants `_ASM_RISCV_EXTABLE_H`, `ARCH_HAS_RELATIVE_EXTABLE`, `swap_ex_entry_fixup(a, b, tmp, delta)`.

## Control Flow
Runtime flow is driven by dynamic patching and trap/debug callbacks: ftrace, jump-labels, kprobes, KGDB, BUG, and exception tables rewrite or interpret instruction streams at runtime. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State is held in patched text, per-probe/ftrace records, exception table entries, debug register snapshots, static keys, or trap frames depending on the subsystem.

## Dependencies And Integration Points
It has no direct includes. Integrates with ftrace, jump labels, kprobes, KGDB, BUG/WARN, exception-table fixups, perf, and architecture trap handling.

## Risks And Edge Cases
Risks include patching the wrong instruction width, corrupting breakpoint/probe/ftrace state, exception-table data packing mistakes, and debug/trap handlers losing register state.

## Test Signals
Test signals include ftrace and function-graph selftests, static-key/jump-label tests, kprobes/KGDB tests, BUG/WARN/oops decoding, perf callchain checks, and exception-table fault-injection tests.

Source read size: 52 lines, 1495 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/extable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/fence.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/fence.h

## Purpose
Defines assembler and C forms of RISC-V fence/acquire/release/full barrier instructions.

## Important APIs, Types, And Functions
macros/constants `_ASM_RISCV_FENCE_H`, `RISCV_FENCE_ASM(p, s)`, `RISCV_FENCE(p, s)`, `RISCV_ACQUIRE_BARRIER`, `RISCV_RELEASE_BARRIER`, `RISCV_FULL_BARRIER`.

## Control Flow
The header is primarily declarative. Runtime behavior occurs in the including architecture implementation files and generic Linux subsystems that consume the constants, types, macros, and prototypes defined here. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
The header itself owns no filesystem or durable state. It defines ABI-like constants or inline behavior consumed by longer-lived kernel objects.

## Dependencies And Integration Points
It has no direct includes. Integrates with generic Linux architecture headers and RISC-V implementation files through include-time contracts.

## Risks And Edge Cases
The main risk is that generic code treats these definitions as architecture ABI. Renaming, renumbering, or changing inline semantics without matching implementation changes can create build-only or boot-time failures.

## Test Signals
Test signals include architecture build coverage, include dependency checks, and subsystem tests for the generic code that consumes this header.

Source read size: 19 lines, 564 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/fence.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/fixmap.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/fixmap.h

## Purpose
Defines RISC-V fixed virtual-address slots for early ioremap, fixmap bitmap slots, and late fixmap updates.

## Important APIs, Types, And Functions
types `fixed_addresses`; functions/prototypes `__set_fixmap`; macros/constants `_ASM_RISCV_FIXMAP_H`, `NR_FIX_BTMAPS`, `FIX_BTMAPS_SLOTS`, `TOTAL_FIX_BTMAPS`, `__early_set_fixmap`, `__late_set_fixmap`, `__late_clear_fixmap(idx) __set_fixmap((idx), 0, FIXMAP_PAGE_CLEAR)`.

## Control Flow
Runtime flow is reached through generic MM, page-table, fault, TLB, and mapping callbacks. The header supplies inline conversions and declarations that the implementation files call during context switch, map/unmap, and flush paths. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State is carried in `mm_struct`, page tables, ASIDs, fixed mappings, folios, cache/TLB state, or architecture context fields; this header defines how those state holders are interpreted.

## Dependencies And Integration Points
Direct includes are `linux/kernel.h`, `linux/sizes.h`, `linux/pgtable.h`, `asm/page.h`, `asm-generic/fixmap.h`. Integrates with Linux MM, page-table helpers, TLB shootdown, cache maintenance, hugetlb, KASAN/KFENCE, EFI mapping, kexec, and architecture fault handling.

## Risks And Edge Cases
Risks include stale cache/TLB state, wrong virtual/physical conversions, ASID/version reuse bugs, fixed-map overlap, hugepage PTE corruption, and ABI changes in ELF or image headers.

## Test Signals
Test signals include MM selftests, mmap/mprotect/fork/exec stress, hugetlb tests, KASAN/KFENCE boot, kexec/crashkernel boot, EFI boot, cacheflush tests, and TLB shootdown stress.

Source read size: 67 lines, 1789 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/fixmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/fpu.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/fpu.h

## Purpose
Declares kernel floating-point begin/end hooks and maps availability to RISC-V F/D support.

## Important APIs, Types, And Functions
functions/prototypes `kernel_fpu_begin`, `kernel_fpu_end`; macros/constants `_ASM_RISCV_FPU_H`, `kernel_fpu_available() has_fpu()`.

## Control Flow
The header is primarily declarative. Runtime behavior occurs in the including architecture implementation files and generic Linux subsystems that consume the constants, types, macros, and prototypes defined here.

## State And Persistence
The header itself owns no filesystem or durable state. It defines ABI-like constants or inline behavior consumed by longer-lived kernel objects.

## Dependencies And Integration Points
Direct includes are `asm/switch_to.h`. Integrates with generic Linux architecture headers and RISC-V implementation files through include-time contracts.

## Risks And Edge Cases
The main risk is that generic code treats these definitions as architecture ABI. Renaming, renumbering, or changing inline semantics without matching implementation changes can create build-only or boot-time failures.

## Test Signals
Test signals include architecture build coverage, include dependency checks, and subsystem tests for the generic code that consumes this header.

Source read size: 16 lines, 291 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/fpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/ftrace.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/ftrace.h

## Purpose
Defines RISC-V dynamic ftrace instruction encoding, call patching metadata, ftrace register accessors, and syscall tracing filters.

## Important APIs, Types, And Functions
types `pt_regs`, `dyn_arch_ftrace`, `dyn_ftrace`, `module`, `ftrace_ops`, `ftrace_regs`, `__arch_ftrace_regs`; functions/prototypes `return_address`, `_mcount`, `ftrace_call_adjust`, `arch_ftrace_get_symaddr`, `arch_trace_is_compat_syscall`, `arch_syscall_match_sym_name`, `ftrace_init_nop`, `ftrace_regs_get_instruction_pointer`, `ftrace_regs_set_instruction_pointer`, `ftrace_regs_get_stack_pointer`, `ftrace_regs_get_frame_pointer`, `ftrace_regs_get_argument`, plus 8 more; macros/constants `_ASM_RISCV_FTRACE_H`, `HAVE_FUNCTION_GRAPH_FP_TEST`, `ARCH_SUPPORTS_FTRACE_OPS`, `ftrace_return_address(n) return_address(n)`, `ftrace_get_symaddr(fentry_ip) arch_ftrace_get_symaddr(fentry_ip)`, `ARCH_TRACE_IGNORE_COMPAT_SYSCALLS`, `ARCH_HAS_SYSCALL_MATCH_SYM_NAME`, `MCOUNT_ADDR`, `JALR_SIGN_MASK`, `JALR_OFFSET_MASK`, `AUIPC_OFFSET_MASK`, `AUIPC_PAD`, `JALR_SHIFT`, `JALR_T0`, plus 14 more.

## Control Flow
Runtime flow is driven by dynamic patching and trap/debug callbacks: ftrace, jump-labels, kprobes, KGDB, BUG, and exception tables rewrite or interpret instruction streams at runtime. Special attention: call-site rewriting depends on exact AUIPC/JALR encodings, call range checks, NOP sizing, and register accessors for full and partial ftrace frames.

## State And Persistence
State is held in patched text, per-probe/ftrace records, exception table entries, debug register snapshots, static keys, or trap frames depending on the subsystem.

## Dependencies And Integration Points
It has no direct includes. Integrates with ftrace, jump labels, kprobes, KGDB, BUG/WARN, exception-table fixups, perf, and architecture trap handling.

## Risks And Edge Cases
Risks include patching the wrong instruction width, corrupting breakpoint/probe/ftrace state, exception-table data packing mistakes, and debug/trap handlers losing register state.

## Test Signals
Test signals include ftrace and function-graph selftests, static-key/jump-label tests, kprobes/KGDB tests, BUG/WARN/oops decoding, perf callchain checks, and exception-table fault-injection tests.

Source read size: 242 lines, 6523 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/ftrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/futex.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/futex.h

## Purpose
Implements futex atomic operations in user memory using RISC-V inline assembly and exception-table fixups.

## Important APIs, Types, And Functions
functions/prototypes `arch_futex_atomic_op_inuser`, `futex_atomic_cmpxchg_inatomic`; macros/constants `_ASM_RISCV_FUTEX_H`, `__enable_user_access() do { } while (0)`, `__disable_user_access() do { } while (0)`, `__futex_atomic_op(insn, ret, oldval, uaddr, oparg)`.

## Control Flow
Runtime flow is driven by dynamic patching and trap/debug callbacks: ftrace, jump-labels, kprobes, KGDB, BUG, and exception tables rewrite or interpret instruction streams at runtime. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State is held in patched text, per-probe/ftrace records, exception table entries, debug register snapshots, static keys, or trap frames depending on the subsystem.

## Dependencies And Integration Points
Direct includes are `linux/futex.h`, `linux/uaccess.h`, `linux/errno.h`, `asm/asm.h`, `asm/asm-extable.h`. Integrates with ftrace, jump labels, kprobes, KGDB, BUG/WARN, exception-table fixups, perf, and architecture trap handling.

## Risks And Edge Cases
Risks include patching the wrong instruction width, corrupting breakpoint/probe/ftrace state, exception-table data packing mistakes, and debug/trap handlers losing register state.

## Test Signals
Test signals include ftrace and function-graph selftests, static-key/jump-label tests, kprobes/KGDB tests, BUG/WARN/oops decoding, perf callchain checks, and exception-table fault-injection tests.

Source read size: 104 lines, 2483 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/futex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/gdb_xml.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/gdb_xml.h

## Purpose
Contains KGDB/GDB XML register descriptions for RISC-V base and extension register sets.

## Important APIs, Types, And Functions
macros/constants `__ASM_GDB_XML_H_`.

## Control Flow
The header is primarily declarative. Runtime behavior occurs in the including architecture implementation files and generic Linux subsystems that consume the constants, types, macros, and prototypes defined here. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
The header itself owns no filesystem or durable state. It defines ABI-like constants or inline behavior consumed by longer-lived kernel objects.

## Dependencies And Integration Points
It has no direct includes. Integrates with generic Linux architecture headers and RISC-V implementation files through include-time contracts.

## Risks And Edge Cases
The main risk is that generic code treats these definitions as architecture ABI. Renaming, renumbering, or changing inline semantics without matching implementation changes can create build-only or boot-time failures.

## Test Signals
Test signals include architecture build coverage, include dependency checks, and subsystem tests for the generic code that consumes this header.

Source read size: 116 lines, 5601 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/gdb_xml.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/gpr-num.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/gpr-num.h

## Purpose
Maps RISC-V register names to numeric assembler constants for generated instruction encodings.

## Important APIs, Types, And Functions
macros/constants `__ASM_GPR_NUM_H`, `__DEFINE_ASM_GPR_NUMS`.

## Control Flow
The control flow is mostly preprocessor and assembler expansion: low-level entry, trap, module, and patching code include these macros and emit exact instructions or section records at build time.

## State And Persistence
State is usually encoded in generated sections, register save areas, alternative tables, exception tables, or trap metadata rather than stored in this header. The definitions must remain stable because assembly and C code share them.

## Dependencies And Integration Points
It has no direct includes. Integrates with RISC-V assembler support, generated offsets, linker sections, alternatives, exception tables, low-level entry code, module relocation, and compiler feature tests.

## Risks And Edge Cases
Risks are instruction-encoding, section-layout, relocation, register-width, and generated-offset mistakes. A small macro change can break boot, trap entry, module loading, or runtime text patching.

## Test Signals
Test signals include defconfig/allmodconfig builds, objdump validation of emitted instructions and sections, boot smoke tests, module load/unload, alternatives/errata patch logs, exception fixup tests, and trap-entry stress.

Source read size: 85 lines, 2429 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/gpr-num.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/hugetlb.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/hugetlb.h

## Purpose
Declares RISC-V hugepage PTE operations and migration support hooks.

## Important APIs, Types, And Functions
types `folio`, `hstate`, `mm_struct`, `vm_area_struct`; functions/prototypes `arch_clear_hugetlb_flags`, `arch_hugetlb_migration_supported`, `huge_pte_clear`, `set_huge_pte_at`, `huge_ptep_get_and_clear`, `huge_ptep_clear_flush`, `huge_ptep_set_wrprotect`, `huge_ptep_set_access_flags`, `huge_ptep_get`, `arch_make_huge_pte`; macros/constants `_ASM_RISCV_HUGETLB_H`, `arch_clear_hugetlb_flags`, `arch_hugetlb_migration_supported`, `__HAVE_ARCH_HUGE_PTE_CLEAR`, `__HAVE_ARCH_HUGE_SET_HUGE_PTE_AT`, `__HAVE_ARCH_HUGE_PTEP_GET_AND_CLEAR`, `__HAVE_ARCH_HUGE_PTEP_CLEAR_FLUSH`, `__HAVE_ARCH_HUGE_PTEP_SET_WRPROTECT`, `__HAVE_ARCH_HUGE_PTEP_SET_ACCESS_FLAGS`, `__HAVE_ARCH_HUGE_PTEP_GET`, `arch_make_huge_pte`.

## Control Flow
Runtime flow is reached through generic MM, page-table, fault, TLB, and mapping callbacks. The header supplies inline conversions and declarations that the implementation files call during context switch, map/unmap, and flush paths. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State is carried in `mm_struct`, page tables, ASIDs, fixed mappings, folios, cache/TLB state, or architecture context fields; this header defines how those state holders are interpreted.

## Dependencies And Integration Points
Direct includes are `asm/cacheflush.h`, `asm/page.h`, `asm-generic/hugetlb.h`. Integrates with Linux MM, page-table helpers, TLB shootdown, cache maintenance, hugetlb, KASAN/KFENCE, EFI mapping, kexec, and architecture fault handling.

## Risks And Edge Cases
Risks include stale cache/TLB state, wrong virtual/physical conversions, ASID/version reuse bugs, fixed-map overlap, hugepage PTE corruption, and ABI changes in ELF or image headers.

## Test Signals
Test signals include MM selftests, mmap/mprotect/fork/exec stress, hugetlb tests, KASAN/KFENCE boot, kexec/crashkernel boot, EFI boot, cacheflush tests, and TLB shootdown stress.

Source read size: 57 lines, 1805 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/hugetlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/hwcap.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/hwcap.h

## Purpose
Enumerates RISC-V ISA extension IDs and bitmap sizing used by cpufeature, alternatives, KVM, and userspace hwcap reporting.

## Important APIs, Types, And Functions
macros/constants `_ASM_RISCV_HWCAP_H`, `RISCV_ISA_EXT_a`, `RISCV_ISA_EXT_c`, `RISCV_ISA_EXT_d`, `RISCV_ISA_EXT_f`, `RISCV_ISA_EXT_h`, `RISCV_ISA_EXT_i`, `RISCV_ISA_EXT_m`, `RISCV_ISA_EXT_q`, `RISCV_ISA_EXT_v`, `RISCV_ISA_EXT_BASE`, `RISCV_ISA_EXT_SSCOFPMF`, `RISCV_ISA_EXT_SSTC`, `RISCV_ISA_EXT_SVINVAL`, plus 82 more.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure. Special attention: extension IDs are shared by cpufeature, alternatives, KVM ISA exposure, ELF hwcaps, and hwprobe reporting; gaps and numbering are compatibility-sensitive.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
Direct includes are `uapi/asm/hwcap.h`. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 129 lines, 4081 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/hwcap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/hwprobe.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/hwprobe.h

## Purpose
Declares kernel-side helpers for the RISC-V `hwprobe` syscall key validation, sorting, and asynchronous probing.

## Important APIs, Types, And Functions
types `riscv_hwprobe`; functions/prototypes `riscv_hwprobe_key_is_valid`, `hwprobe_key_is_bitmask`, `riscv_hwprobe_pair_cmp`, `riscv_hwprobe_register_async_probe`, `riscv_hwprobe_complete_async_probe`; macros/constants `_ASM_HWPROBE_H`, `RISCV_HWPROBE_MAX_KEY`.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
Direct includes are `uapi/asm/hwprobe.h`. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 53 lines, 1288 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/hwprobe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/image.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/image.h

## Purpose
Defines the RISC-V boot image header, magic values, flags, version, and load metadata.

## Important APIs, Types, And Functions
types `riscv_image_header`; macros/constants `_ASM_RISCV_IMAGE_H`, `RISCV_IMAGE_MAGIC`, `RISCV_IMAGE_MAGIC2`, `RISCV_IMAGE_FLAG_BE_SHIFT`, `RISCV_IMAGE_FLAG_BE_MASK`, `RISCV_IMAGE_FLAG_LE`, `RISCV_IMAGE_FLAG_BE`, `__HEAD_FLAG_BE`, `__HEAD_FLAG(field)`, `__HEAD_FLAGS`, `RISCV_HEADER_VERSION_MAJOR`, `RISCV_HEADER_VERSION_MINOR`, `RISCV_HEADER_VERSION`, `riscv_image_flag_field(flags, field)`.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
It has no direct includes. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 67 lines, 1775 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/image.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/insn-def.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/insn-def.h

## Purpose
Defines instruction-construction macros for emitting R/I/S-form RISC-V opcodes from C or assembly.

## Important APIs, Types, And Functions
macros/constants `__ASM_INSN_DEF_H`, `INSN_R_FUNC7_SHIFT`, `INSN_R_RS2_SHIFT`, `INSN_R_RS1_SHIFT`, `INSN_R_FUNC3_SHIFT`, `INSN_R_RD_SHIFT`, `INSN_R_OPCODE_SHIFT`, `INSN_I_SIMM12_SHIFT`, `INSN_I_RS1_SHIFT`, `INSN_I_FUNC3_SHIFT`, `INSN_I_RD_SHIFT`, `INSN_I_OPCODE_SHIFT`, `INSN_S_SIMM7_SHIFT`, `INSN_S_RS2_SHIFT`, plus 77 more.

## Control Flow
The control flow is mostly preprocessor and assembler expansion: low-level entry, trap, module, and patching code include these macros and emit exact instructions or section records at build time. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State is usually encoded in generated sections, register save areas, alternative tables, exception tables, or trap metadata rather than stored in this header. The definitions must remain stable because assembly and C code share them.

## Dependencies And Integration Points
Direct includes are `asm/asm.h`, `asm/gpr-num.h`, `linux/stringify.h`. Integrates with RISC-V assembler support, generated offsets, linker sections, alternatives, exception tables, low-level entry code, module relocation, and compiler feature tests.

## Risks And Edge Cases
Risks are instruction-encoding, section-layout, relocation, register-width, and generated-offset mistakes. A small macro change can break boot, trap entry, module loading, or runtime text patching.

## Test Signals
Test signals include defconfig/allmodconfig builds, objdump validation of emitted instructions and sections, boot smoke tests, module load/unload, alternatives/errata patch logs, exception fixup tests, and trap-entry stress.

Source read size: 351 lines, 10515 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/insn-def.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/insn.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/insn.h

## Purpose
Defines instruction bitfield masks, opcodes, immediate extraction/insertion helpers, and instruction-class predicates.

## Important APIs, Types, And Functions
functions/prototypes `riscv_insn_is_system`, `riscv_insn_is_branch`, `riscv_insn_is_c_jr`, `riscv_insn_is_c_jalr`, `riscv_insn_extract_jtype_imm`, `riscv_insn_insert_jtype_imm`, `riscv_insn_extract_utype_itype_imm`, `riscv_insn_insert_utype_itype_imm`; macros/constants `_ASM_RISCV_INSN_H`, `RV_INSN_FUNCT3_MASK`, `RV_INSN_FUNCT3_OPOFF`, `RV_INSN_OPCODE_MASK`, `RV_INSN_OPCODE_OPOFF`, `RV_INSN_FUNCT12_OPOFF`, `RV_ENCODE_FUNCT3(f_) (RVG_FUNCT3_##f_ << RV_INSN_FUNCT3_OPOFF)`, `RV_ENCODE_FUNCT12(f_) (RVG_FUNCT12_##f_ << RV_INSN_FUNCT12_OPOFF)`, `RV_I_IMM_SIGN_OPOFF`, `RV_I_IMM_11_0_OPOFF`, `RV_I_IMM_SIGN_OFF`, `RV_I_IMM_11_0_OFF`, `RV_I_IMM_11_0_MASK`, `RV_J_IMM_SIGN_OPOFF`, plus 314 more.

## Control Flow
The header is primarily declarative. Runtime behavior occurs in the including architecture implementation files and generic Linux subsystems that consume the constants, types, macros, and prototypes defined here. Special attention: the immediate extraction and insertion helpers are consumed by instruction patching, probes, and ftrace-style call rewriting, so bitfield definitions are executable correctness data.

## State And Persistence
The header itself owns no filesystem or durable state. It defines ABI-like constants or inline behavior consumed by longer-lived kernel objects.

## Dependencies And Integration Points
Direct includes are `linux/bits.h`. Integrates with generic Linux architecture headers and RISC-V implementation files through include-time contracts.

## Risks And Edge Cases
The main risk is that generic code treats these definitions as architecture ABI. Renaming, renumbering, or changing inline semantics without matching implementation changes can create build-only or boot-time failures.

## Test Signals
Test signals include architecture build coverage, include dependency checks, and subsystem tests for the generic code that consumes this header.

Source read size: 603 lines, 20987 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/insn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/io.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/io.h

## Purpose
Defines RISC-V I/O-space limits, ioremap wrappers, and ordered string I/O accessors.

## Important APIs, Types, And Functions
macros/constants `_ASM_RISCV_IO_H`, `IO_SPACE_LIMIT`, `PCI_IOBASE`, `ioremap_wc(addr, size)`, `__io_pbr() RISCV_FENCE(io, i)`, `__io_par(v) RISCV_FENCE(i, ior)`, `__io_pbw() RISCV_FENCE(iow, o)`, `__io_paw() RISCV_FENCE(o, io)`, `__io_reads_ins(port, ctype, len, bfence, afence)`, `__io_writes_outs(port, ctype, len, bfence, afence)`, `readsb(addr, buffer, count) __readsb(addr, buffer, count)`, `readsw(addr, buffer, count) __readsw(addr, buffer, count)`, `readsl(addr, buffer, count) __readsl(addr, buffer, count)`, `insb(addr, buffer, count) __insb(PCI_IOBASE + (addr), buffer, count)`, plus 13 more.

## Control Flow
Runtime flow is a wrapper sequence around MMIO or port-I/O reads and writes: optional fences bracket raw loads/stores, endian conversion is applied for CPU-visible values, and generic driver code calls the resulting accessors. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
No durable state is stored by the header. Accessors mutate device-visible MMIO state and rely on fences to preserve ordering against CPUs, DMA, and devices.

## Dependencies And Integration Points
Direct includes are `linux/types.h`, `linux/pgtable.h`, `asm/mmiowb.h`, `asm/early_ioremap.h`, `asm/mmio.h`, `asm-generic/io.h`. Integrates with driver MMIO APIs, PCI I/O space, generic `asm-generic/io.h`, DMA/noncoherent cache hooks, and RISC-V fence semantics.

## Risks And Edge Cases
Risks are missing fences, wrong endian conversion, noncoherent DMA cache omissions, and incorrect port/MMIO address translation, which can produce device data corruption or ordering bugs.

## Test Signals
Test signals include driver probe and DMA tests on coherent and noncoherent systems, PCI enumeration, MMIO ordering litmus tests, CBO cache-maintenance tests, and sparse/endian build checks.

Source read size: 147 lines, 5424 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/irq.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/irq.h

## Purpose
Declares RISC-V interrupt-controller discovery, ACPI GSI mapping, hart-index lookup, and backtrace IPI hooks.

## Important APIs, Types, And Functions
types `fwnode_handle`, `riscv_irqchip_type`, `resource`; functions/prototypes `arch_trigger_cpumask_backtrace`, `riscv_set_intc_hwnode_fn`, `riscv_get_intc_hwnode`, `riscv_get_hart_index`, `riscv_acpi_get_gsi_info`, `riscv_acpi_get_gsi_domain_id`, `acpi_rintc_index_to_hartid`, `acpi_rintc_ext_parent_to_hartid`, `acpi_rintc_get_plic_nr_contexts`, `acpi_rintc_get_plic_context`, `riscv_acpi_update_gsi_range`; macros/constants `_ASM_RISCV_IRQ_H`, `INVALID_CONTEXT`, `arch_trigger_cpumask_backtrace`.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
Direct includes are `linux/interrupt.h`, `linux/linkage.h`, `asm-generic/irq.h`. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 87 lines, 2428 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/irq_stack.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/irq_stack.h

## Purpose
Declares IRQ-stack switching and vmapped IRQ-stack allocation helpers.

## Important APIs, Types, And Functions
types `pt_regs`; functions/prototypes `call_on_irq_stack`, `arch_alloc_vmap_stack`; macros/constants `_ASM_RISCV_IRQ_STACK_H`.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
Direct includes are `linux/bug.h`, `linux/gfp.h`, `linux/kconfig.h`, `linux/vmalloc.h`, `linux/pgtable.h`, `asm/thread_info.h`. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 33 lines, 843 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/irq_stack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/irq_work.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/irq_work.h

## Purpose
Declares whether RISC-V has an interrupt for generic irq_work.

## Important APIs, Types, And Functions
functions/prototypes `arch_irq_work_has_interrupt`; macros/constants `_ASM_RISCV_IRQ_WORK_H`.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
It has no direct includes. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 10 lines, 225 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/irq_work.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/irqflags.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/irqflags.h

## Purpose
Implements local interrupt save/restore/enable/disable helpers using status CSR bits.

## Important APIs, Types, And Functions
functions/prototypes `arch_local_save_flags`, `arch_local_irq_enable`, `arch_local_irq_disable`, `arch_local_irq_save`, `arch_irqs_disabled_flags`, `arch_irqs_disabled`, `arch_local_irq_restore`; macros/constants `_ASM_RISCV_IRQFLAGS_H`.

## Control Flow
Runtime flow begins during boot and CPU hotplug, where platform/SBI code chooses CPU operations, probes ISA features, and records per-hart capabilities for alternatives and userspace exposure.

## State And Persistence
State persists in CPU feature bitmaps, static keys, ASID/VMID counters, topology or boot-operation tables, and exported hwcap/hwprobe results.

## Dependencies And Integration Points
Direct includes are `asm/csr.h`. Integrates with device-tree/ACPI CPU discovery, SBI, cpufeature probing, alternatives, ELF hwcaps, hwprobe, idle, crash reservation, and scheduler/hotplug paths.

## Risks And Edge Cases
Risks include feature bits that do not match real hardware, alternatives patched before capabilities are stable, compat/ELF ABI mismatches, and boot/hotplug operations racing CPU state transitions.

## Test Signals
Test signals include boot logs for ISA extension discovery, hwprobe syscall tests, ELF hwcap/auxv checks, CPU hotplug, cpuidle smoke tests, compat userspace on 64-bit kernels, and errata-specific hardware/QEMU coverage.

Source read size: 54 lines, 1148 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/irqflags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/jump_label.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/jump_label.h

## Purpose
Defines RISC-V static-key/jump-label NOP and branch encodings.

## Important APIs, Types, And Functions
types `static_key`; functions/prototypes `arch_static_branch`, `arch_static_branch_jump`; macros/constants `__ASM_JUMP_LABEL_H`, `HAVE_JUMP_LABEL_BATCH`, `JUMP_LABEL_NOP_SIZE`, `JUMP_TABLE_ENTRY(key, label)`, `ARCH_STATIC_BRANCH_ASM(key, label)`, `ARCH_STATIC_BRANCH_JUMP_ASM(key, label)`.

## Control Flow
Runtime flow is driven by dynamic patching and trap/debug callbacks: ftrace, jump-labels, kprobes, KGDB, BUG, and exception tables rewrite or interpret instruction streams at runtime.

## State And Persistence
State is held in patched text, per-probe/ftrace records, exception table entries, debug register snapshots, static keys, or trap frames depending on the subsystem.

## Dependencies And Integration Points
Direct includes are `linux/types.h`, `asm/asm.h`. Integrates with ftrace, jump labels, kprobes, KGDB, BUG/WARN, exception-table fixups, perf, and architecture trap handling.

## Risks And Edge Cases
Risks include patching the wrong instruction width, corrupting breakpoint/probe/ftrace state, exception-table data packing mistakes, and debug/trap handlers losing register state.

## Test Signals
Test signals include ftrace and function-graph selftests, static-key/jump-label tests, kprobes/KGDB tests, BUG/WARN/oops decoding, perf callchain checks, and exception-table fault-injection tests.

Source read size: 70 lines, 1645 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/jump_label.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kasan.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kasan.h

## Purpose
Defines RISC-V KASAN shadow address layout and initialization hooks.

## Important APIs, Types, And Functions
functions/prototypes `kasan_init`, `kasan_early_init`, `kasan_swapper_init`; macros/constants `__ASM_KASAN_H`, `KASAN_SHADOW_SCALE_SHIFT`, `KASAN_SHADOW_SIZE`, `KASAN_SHADOW_START`, `KASAN_SHADOW_END`, `KASAN_SHADOW_OFFSET`.

## Control Flow
Runtime flow is reached through generic MM, page-table, fault, TLB, and mapping callbacks. The header supplies inline conversions and declarations that the implementation files call during context switch, map/unmap, and flush paths. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State is carried in `mm_struct`, page tables, ASIDs, fixed mappings, folios, cache/TLB state, or architecture context fields; this header defines how those state holders are interpreted.

## Dependencies And Integration Points
It has no direct includes. Integrates with Linux MM, page-table helpers, TLB shootdown, cache maintenance, hugetlb, KASAN/KFENCE, EFI mapping, kexec, and architecture fault handling.

## Risks And Edge Cases
Risks include stale cache/TLB state, wrong virtual/physical conversions, ASID/version reuse bugs, fixed-map overlap, hugepage PTE corruption, and ABI changes in ELF or image headers.

## Test Signals
Test signals include MM selftests, mmap/mprotect/fork/exec stress, hugetlb tests, KASAN/KFENCE boot, kexec/crashkernel boot, EFI boot, cacheflush tests, and TLB shootdown stress.

Source read size: 45 lines, 1590 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kasan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kdebug.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kdebug.h

## Purpose
Defines die-notifier event values for RISC-V debug/oops paths.

## Important APIs, Types, And Functions
types `die_val`; macros/constants `_ASM_ARC_KDEBUG_H`.

## Control Flow
Runtime flow is driven by dynamic patching and trap/debug callbacks: ftrace, jump-labels, kprobes, KGDB, BUG, and exception tables rewrite or interpret instruction streams at runtime.

## State And Persistence
State is held in patched text, per-probe/ftrace records, exception table entries, debug register snapshots, static keys, or trap frames depending on the subsystem.

## Dependencies And Integration Points
It has no direct includes. Integrates with ftrace, jump labels, kprobes, KGDB, BUG/WARN, exception-table fixups, perf, and architecture trap handling.

## Risks And Edge Cases
Risks include patching the wrong instruction width, corrupting breakpoint/probe/ftrace state, exception-table data packing mistakes, and debug/trap handlers losing register state.

## Test Signals
Test signals include ftrace and function-graph selftests, static-key/jump-label tests, kprobes/KGDB tests, BUG/WARN/oops decoding, perf callchain checks, and exception-table fault-injection tests.

Source read size: 12 lines, 158 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kdebug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kexec.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kexec.h

## Purpose
Declares RISC-V kexec/crash-dump image limits, relocation hooks, and crash register capture.

## Important APIs, Types, And Functions
types `pt_regs`, `kimage_arch`, `kexec_file_ops`, `purgatory_info`, `kimage`; functions/prototypes `riscv_crash_save_regs`, `crash_setup_regs`, `arch_kexec_apply_relocations_add`, `arch_kimage_file_post_load_cleanup`, `load_extra_segments`, `riscv_kexec_relocate_size`, `riscv_kexec_norelocate`, `elf_kexec_ops`, `image_kexec_ops`; macros/constants `_RISCV_KEXEC_H`, `KEXEC_SOURCE_MEMORY_LIMIT`, `KEXEC_DESTINATION_MEMORY_LIMIT`, `KEXEC_CONTROL_MEMORY_LIMIT`, `KEXEC_CONTROL_PAGE_SIZE`, `KEXEC_ARCH`, `ARCH_HAS_KIMAGE_ARCH`, `arch_kexec_apply_relocations_add`, `arch_kimage_file_post_load_cleanup`.

## Control Flow
Runtime flow is reached through generic MM, page-table, fault, TLB, and mapping callbacks. The header supplies inline conversions and declarations that the implementation files call during context switch, map/unmap, and flush paths. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State is carried in `mm_struct`, page tables, ASIDs, fixed mappings, folios, cache/TLB state, or architecture context fields; this header defines how those state holders are interpreted.

## Dependencies And Integration Points
Direct includes are `asm/page.h`. Integrates with Linux MM, page-table helpers, TLB shootdown, cache maintenance, hugetlb, KASAN/KFENCE, EFI mapping, kexec, and architecture fault handling.

## Risks And Edge Cases
Risks include stale cache/TLB state, wrong virtual/physical conversions, ASID/version reuse bugs, fixed-map overlap, hugepage PTE corruption, and ABI changes in ELF or image headers.

## Test Signals
Test signals include MM selftests, mmap/mprotect/fork/exec stress, hugetlb tests, KASAN/KFENCE boot, kexec/crashkernel boot, EFI boot, cacheflush tests, and TLB shootdown stress.

Source read size: 78 lines, 2130 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kexec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kfence.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kfence.h

## Purpose
Declares KFENCE pool initialization and per-page protection hooks.

## Important APIs, Types, And Functions
functions/prototypes `arch_kfence_init_pool`, `kfence_protect_page`; macros/constants `_ASM_RISCV_KFENCE_H`.

## Control Flow
Runtime flow is reached through generic MM, page-table, fault, TLB, and mapping callbacks. The header supplies inline conversions and declarations that the implementation files call during context switch, map/unmap, and flush paths.

## State And Persistence
State is carried in `mm_struct`, page tables, ASIDs, fixed mappings, folios, cache/TLB state, or architecture context fields; this header defines how those state holders are interpreted.

## Dependencies And Integration Points
Direct includes are `linux/kfence.h`, `linux/pfn.h`, `asm-generic/pgalloc.h`, `asm/pgtable.h`. Integrates with Linux MM, page-table helpers, TLB shootdown, cache maintenance, hugetlb, KASAN/KFENCE, EFI mapping, kexec, and architecture fault handling.

## Risks And Edge Cases
Risks include stale cache/TLB state, wrong virtual/physical conversions, ASID/version reuse bugs, fixed-map overlap, hugepage PTE corruption, and ABI changes in ELF or image headers.

## Test Signals
Test signals include MM selftests, mmap/mprotect/fork/exec stress, hugetlb tests, KASAN/KFENCE boot, kexec/crashkernel boot, EFI boot, cacheflush tests, and TLB shootdown stress.

Source read size: 32 lines, 674 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kfence.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kgdb.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kgdb.h

## Purpose
Defines KGDB register numbering, packet sizes, breakpoint instruction size, and breakpoint helper.

## Important APIs, Types, And Functions
functions/prototypes `arch_kgdb_breakpoint`, `kgdb_compiled_break`; macros/constants `__ASM_KGDB_H_`, `GDB_SIZEOF_REG`, `DBG_MAX_REG_NUM`, `NUMREGBYTES`, `CACHE_FLUSH_IS_SAFE`, `BUFMAX`, `BREAK_INSTR_SIZE`, `DBG_REG_ZERO`, `DBG_REG_RA`, `DBG_REG_SP`, `DBG_REG_GP`, `DBG_REG_TP`, `DBG_REG_T0`, `DBG_REG_T1`, plus 66 more.

## Control Flow
Runtime flow is driven by dynamic patching and trap/debug callbacks: ftrace, jump-labels, kprobes, KGDB, BUG, and exception tables rewrite or interpret instruction streams at runtime. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State is held in patched text, per-probe/ftrace records, exception table entries, debug register snapshots, static keys, or trap frames depending on the subsystem.

## Dependencies And Integration Points
Direct includes are `linux/build_bug.h`. Integrates with ftrace, jump labels, kprobes, KGDB, BUG/WARN, exception-table fixups, perf, and architecture trap handling.

## Risks And Edge Cases
Risks include patching the wrong instruction width, corrupting breakpoint/probe/ftrace state, exception-table data packing mistakes, and debug/trap handlers losing register state.

## Test Signals
Test signals include ftrace and function-graph selftests, static-key/jump-label tests, kprobes/KGDB tests, BUG/WARN/oops decoding, perf callchain checks, and exception-table fault-injection tests.

Source read size: 111 lines, 2701 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kgdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kprobes.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kprobes.h

## Purpose
Declares RISC-V kprobe instruction-slot, breakpoint, single-step, and fault handling hooks.

## Important APIs, Types, And Functions
types `prev_kprobe`, `kprobe`, `kprobe_ctlblk`, `pt_regs`; functions/prototypes `arch_remove_kprobe`, `kprobe_fault_handler`, `kprobe_breakpoint_handler`, `kprobe_single_step_handler`; macros/constants `_ASM_RISCV_KPROBES_H`, `__ARCH_WANT_KPROBES_INSN_SLOT`, `MAX_INSN_SIZE`, `flush_insn_slot(p) do { } while (0)`, `kretprobe_blacklist_size`.

## Control Flow
Runtime flow is driven by dynamic patching and trap/debug callbacks: ftrace, jump-labels, kprobes, KGDB, BUG, and exception tables rewrite or interpret instruction streams at runtime. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State is held in patched text, per-probe/ftrace records, exception table entries, debug register snapshots, static keys, or trap frames depending on the subsystem.

## Dependencies And Integration Points
Direct includes are `asm-generic/kprobes.h`, `linux/types.h`, `linux/ptrace.h`, `linux/percpu.h`, `asm/probes.h`. Integrates with ftrace, jump labels, kprobes, KGDB, BUG/WARN, exception-table fixups, perf, and architecture trap handling.

## Risks And Edge Cases
Risks include patching the wrong instruction width, corrupting breakpoint/probe/ftrace state, exception-table data packing mistakes, and debug/trap handlers losing register state.

## Test Signals
Test signals include ftrace and function-graph selftests, static-key/jump-label tests, kprobes/KGDB tests, BUG/WARN/oops decoding, perf callchain checks, and exception-table fault-injection tests.

Source read size: 54 lines, 1216 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kprobes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_aia.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_aia.h

## Purpose
Declares KVM Advanced Interrupt Architecture VM/vCPU state and IMSIC/APLIC helper interfaces.

## Important APIs, Types, And Functions
types `kvm_aia`, `kvm_vcpu_aia_csr`, `kvm_vcpu_aia`, `kvm_device_ops`, `kvm_vcpu`, `kvm`, `kvm_msi`; functions/prototypes `kvm_riscv_vcpu_aia_imsic_has_interrupt`, `kvm_riscv_vcpu_aia_imsic_load`, `kvm_riscv_vcpu_aia_imsic_put`, `kvm_riscv_vcpu_aia_imsic_release`, `kvm_riscv_vcpu_aia_imsic_update`, `kvm_riscv_vcpu_aia_imsic_rmw`, `kvm_riscv_aia_imsic_rw_attr`, `kvm_riscv_aia_imsic_has_attr`, `kvm_riscv_vcpu_aia_imsic_reset`, `kvm_riscv_vcpu_aia_imsic_inject`, `kvm_riscv_vcpu_aia_imsic_init`, `kvm_riscv_vcpu_aia_imsic_cleanup`, plus 34 more; macros/constants `__KVM_RISCV_AIA_H`, `KVM_RISCV_AIA_UNDEF_ADDR`, `kvm_riscv_aia_initialized(k) ((k)->arch.aia.initialized)`, `irqchip_in_kernel(k) ((k)->arch.aia.in_kernel)`, `kvm_riscv_aia_available()`, `KVM_RISCV_AIA_IMSIC_TOPEI`, `KVM_RISCV_VCPU_AIA_CSR_FUNCS`.

## Control Flow
Runtime flow is driven by KVM VM/vCPU creation, guest entry/exit, SBI or MMIO/CSR emulation, interrupt injection, and TLB/fence processing. This header supplies state layouts and function contracts consumed by the C implementation files rather than executing logic itself. Special attention: AIA state bridges in-kernel irqchip mode, IMSIC guest files, APLIC attributes, MSI injection, and static-key detection of hardware support.

## State And Persistence
Persistent state is per-VM and per-vCPU architecture state: guest registers, CSRs, timers, interrupt bitmaps, VMIDs, guest-stage page tables, AIA/IMSIC state, PMU counters, SBI state, and optional NACL shared memory. Lifetimes are tied to KVM objects and CPU entry/exit serialization.

## Dependencies And Integration Points
Direct includes are `linux/jump_label.h`, `linux/kvm_types.h`, `asm/csr.h`. Integrates with generic KVM, SBI, RISC-V virtualization CSRs, guest-stage MMU code, AIA/IMSIC/APLIC interrupt controllers, hrtimers, perf, one-reg ioctls, QEMU/KVM userspace ABI, and low-level guest entry assembly.

## Risks And Edge Cases
Risks concentrate around guest-visible ABI drift, incorrect CSR or interrupt state migration, missing memory ordering around atomic bitmaps and fences, stale VMID/TLB state, incorrect shared-memory endian conversion, and mismatches with QEMU/KVM one-reg expectations.

## Test Signals
Test signals include RISC-V KVM selftests, QEMU/KVM guest boot and migration, SBI extension tests, timer and PMU tests, AIA/IMSIC interrupt injection, dirty logging, MMIO/CSR emulation, nested-acceleration availability, and TLB/fence stress.

Source read size: 173 lines, 5579 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_aia.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_gstage.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_gstage.h

## Purpose
Declares KVM guest-stage page-table state, mapping, unmapping, write-protect, and G-stage mode detection.

## Important APIs, Types, And Functions
types `kvm_gstage`, `kvm`, `kvm_gstage_mapping`, `kvm_mmu_memory_cache`, `kvm_riscv_gstage_op`; functions/prototypes `kvm_riscv_gstage_gpa_bits`, `kvm_riscv_gstage_get_leaf`, `kvm_riscv_gstage_set_pte`, `kvm_riscv_gstage_map_page`, `kvm_riscv_gstage_split_huge`, `kvm_riscv_gstage_op_pte`, `kvm_riscv_gstage_unmap_range`, `kvm_riscv_gstage_wp_range`, `kvm_riscv_gstage_mode_detect`, `kvm_riscv_gstage_mode`, `kvm_riscv_gstage_init`, `kvm_riscv_gstage_max_pgd_levels`; macros/constants `__RISCV_KVM_GSTAGE_H_`, `KVM_GSTAGE_FLAGS_LOCAL`, `kvm_riscv_gstage_index_bits`, `kvm_riscv_gstage_pgd_xbits`, `kvm_riscv_gstage_pgd_size`.

## Control Flow
Runtime flow is driven by KVM VM/vCPU creation, guest entry/exit, SBI or MMIO/CSR emulation, interrupt injection, and TLB/fence processing. This header supplies state layouts and function contracts consumed by the C implementation files rather than executing logic itself. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
Persistent state is per-VM and per-vCPU architecture state: guest registers, CSRs, timers, interrupt bitmaps, VMIDs, guest-stage page tables, AIA/IMSIC state, PMU counters, SBI state, and optional NACL shared memory. Lifetimes are tied to KVM objects and CPU entry/exit serialization.

## Dependencies And Integration Points
Direct includes are `linux/kvm_types.h`. Integrates with generic KVM, SBI, RISC-V virtualization CSRs, guest-stage MMU code, AIA/IMSIC/APLIC interrupt controllers, hrtimers, perf, one-reg ioctls, QEMU/KVM userspace ABI, and low-level guest entry assembly.

## Risks And Edge Cases
Risks concentrate around guest-visible ABI drift, incorrect CSR or interrupt state migration, missing memory ordering around atomic bitmaps and fences, stale VMID/TLB state, incorrect shared-memory endian conversion, and mismatches with QEMU/KVM one-reg expectations.

## Test Signals
Test signals include RISC-V KVM selftests, QEMU/KVM guest boot and migration, SBI extension tests, timer and PMU tests, AIA/IMSIC interrupt injection, dirty logging, MMIO/CSR emulation, nested-acceleration availability, and TLB/fence stress.

Source read size: 109 lines, 2854 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_gstage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_host.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_host.h

## Purpose
Defines the core RISC-V KVM VM and vCPU architecture state, request numbers, trap context, CSR state, interrupt bitmaps, and vCPU lifecycle APIs.

## Important APIs, Types, And Functions
types `kvm_vm_stat`, `kvm_vm_stat_generic`, `kvm_vcpu_stat`, `kvm_vcpu_stat_generic`, `kvm_arch_memory_slot`, `kvm_arch`, `kvm_vmid`, `kvm_guest_timer`, `kvm_aia`, `kvm_cpu_trap`, plus 22 more; functions/prototypes `kvm_arch_pmi_in_guest`, `kvm_arch_vcpu_blocking`, `kvm_arch_vcpu_unblocking`, `kvm_riscv_setup_default_irq_routing`, `__kvm_riscv_unpriv_trap`, `kvm_riscv_vcpu_unpriv_read`, `kvm_riscv_vcpu_trap_redirect`, `kvm_riscv_vcpu_exit`, `__kvm_riscv_switch_to`, `kvm_riscv_vcpu_setup_isa`, `kvm_riscv_vcpu_num_regs`, `kvm_riscv_vcpu_copy_reg_indices`, plus 13 more; macros/constants `__RISCV_KVM_HOST_H__`, `KVM_MAX_VCPUS`, `KVM_HALT_POLL_NS_DEFAULT`, `KVM_VCPU_MAX_FEATURES`, `KVM_IRQCHIP_NUM_PINS`, `KVM_REQ_SLEEP`, `KVM_REQ_VCPU_RESET`, `KVM_REQ_UPDATE_HGATP`, `KVM_REQ_FENCE_I`, `KVM_REQ_HFENCE_VVMA_ALL`, `KVM_REQ_HFENCE`, `KVM_REQ_STEAL_UPDATE`, `__KVM_HAVE_ARCH_FLUSH_REMOTE_TLBS_RANGE`, `KVM_DIRTY_LOG_MANUAL_CAPS`, plus 1 more.

## Control Flow
Runtime flow is driven by KVM VM/vCPU creation, guest entry/exit, SBI or MMIO/CSR emulation, interrupt injection, and TLB/fence processing. This header supplies state layouts and function contracts consumed by the C implementation files rather than executing logic itself. Special attention: `struct kvm_vcpu_arch` is the aggregation point for guest context, host context, CSR state, reset state, pending interrupt bitmaps, MMIO/CSR decode data, SBI, timer, PMU, AIA, FP/vector, and memory-cache state.

## State And Persistence
Persistent state is per-VM and per-vCPU architecture state: guest registers, CSRs, timers, interrupt bitmaps, VMIDs, guest-stage page tables, AIA/IMSIC state, PMU counters, SBI state, and optional NACL shared memory. Lifetimes are tied to KVM objects and CPU entry/exit serialization.

## Dependencies And Integration Points
Direct includes are `linux/types.h`, `linux/kvm.h`, `linux/kvm_types.h`, `linux/spinlock.h`, `asm/hwcap.h`, `asm/kvm_aia.h`, `asm/ptrace.h`, `asm/kvm_tlb.h`, `asm/kvm_vmid.h`, `asm/kvm_vcpu_config.h`, plus 6 more. Integrates with generic KVM, SBI, RISC-V virtualization CSRs, guest-stage MMU code, AIA/IMSIC/APLIC interrupt controllers, hrtimers, perf, one-reg ioctls, QEMU/KVM userspace ABI, and low-level guest entry assembly.

## Risks And Edge Cases
Risks concentrate around guest-visible ABI drift, incorrect CSR or interrupt state migration, missing memory ordering around atomic bitmaps and fences, stale VMID/TLB state, incorrect shared-memory endian conversion, and mismatches with QEMU/KVM one-reg expectations.

## Test Signals
Test signals include RISC-V KVM selftests, QEMU/KVM guest boot and migration, SBI extension tests, timer and PMU tests, AIA/IMSIC interrupt injection, dirty logging, MMIO/CSR emulation, nested-acceleration availability, and TLB/fence stress.

Source read size: 323 lines, 8399 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_host.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_isa.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_isa.h

## Purpose
Declares KVM ISA extension conversion and host-supported enable/disable policy helpers.

## Important APIs, Types, And Functions
functions/prototypes `kvm_riscv_base2isa_ext`, `__kvm_riscv_isa_check_host`, `kvm_riscv_isa_enable_allowed`, `kvm_riscv_isa_disable_allowed`; macros/constants `__KVM_RISCV_ISA_H`, `kvm_riscv_isa_check_host(ext)`.

## Control Flow
Runtime flow is driven by KVM VM/vCPU creation, guest entry/exit, SBI or MMIO/CSR emulation, interrupt injection, and TLB/fence processing. This header supplies state layouts and function contracts consumed by the C implementation files rather than executing logic itself.

## State And Persistence
Persistent state is per-VM and per-vCPU architecture state: guest registers, CSRs, timers, interrupt bitmaps, VMIDs, guest-stage page tables, AIA/IMSIC state, PMU counters, SBI state, and optional NACL shared memory. Lifetimes are tied to KVM objects and CPU entry/exit serialization.

## Dependencies And Integration Points
Direct includes are `linux/types.h`. Integrates with generic KVM, SBI, RISC-V virtualization CSRs, guest-stage MMU code, AIA/IMSIC/APLIC interrupt controllers, hrtimers, perf, one-reg ioctls, QEMU/KVM userspace ABI, and low-level guest entry assembly.

## Risks And Edge Cases
Risks concentrate around guest-visible ABI drift, incorrect CSR or interrupt state migration, missing memory ordering around atomic bitmaps and fences, stale VMID/TLB state, incorrect shared-memory endian conversion, and mismatches with QEMU/KVM one-reg expectations.

## Test Signals
Test signals include RISC-V KVM selftests, QEMU/KVM guest boot and migration, SBI extension tests, timer and PMU tests, AIA/IMSIC interrupt injection, dirty logging, MMIO/CSR emulation, nested-acceleration availability, and TLB/fence stress.

Source read size: 20 lines, 537 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_isa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_mmu.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_mmu.h

## Purpose
Declares RISC-V KVM MMU map/ioremap/page-table allocation and HGATP update hooks.

## Important APIs, Types, And Functions
types `kvm`, `kvm_vcpu`, `kvm_memory_slot`, `kvm_gstage_mapping`; functions/prototypes `kvm_riscv_mmu_ioremap`, `kvm_riscv_mmu_iounmap`, `kvm_riscv_mmu_map`, `kvm_riscv_mmu_alloc_pgd`, `kvm_riscv_mmu_free_pgd`, `kvm_riscv_mmu_update_hgatp`; macros/constants `__RISCV_KVM_MMU_H_`.

## Control Flow
Runtime flow is driven by KVM VM/vCPU creation, guest entry/exit, SBI or MMIO/CSR emulation, interrupt injection, and TLB/fence processing. This header supplies state layouts and function contracts consumed by the C implementation files rather than executing logic itself.

## State And Persistence
Persistent state is per-VM and per-vCPU architecture state: guest registers, CSRs, timers, interrupt bitmaps, VMIDs, guest-stage page tables, AIA/IMSIC state, PMU counters, SBI state, and optional NACL shared memory. Lifetimes are tied to KVM objects and CPU entry/exit serialization.

## Dependencies And Integration Points
Direct includes are `asm/kvm_gstage.h`. Integrates with generic KVM, SBI, RISC-V virtualization CSRs, guest-stage MMU code, AIA/IMSIC/APLIC interrupt controllers, hrtimers, perf, one-reg ioctls, QEMU/KVM userspace ABI, and low-level guest entry assembly.

## Risks And Edge Cases
Risks concentrate around guest-visible ABI drift, incorrect CSR or interrupt state migration, missing memory ordering around atomic bitmaps and fences, stale VMID/TLB state, incorrect shared-memory endian conversion, and mismatches with QEMU/KVM one-reg expectations.

## Test Signals
Test signals include RISC-V KVM selftests, QEMU/KVM guest boot and migration, SBI extension tests, timer and PMU tests, AIA/IMSIC interrupt injection, dirty logging, MMIO/CSR emulation, nested-acceleration availability, and TLB/fence stress.

Source read size: 21 lines, 721 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_nacl.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_nacl.h

## Purpose
Declares KVM nested acceleration shared-memory state, static-key capabilities, SBI NACL switching, and HFENCE synchronization helpers.

## Important APIs, Types, And Functions
types `kvm_vcpu_arch`, `kvm_riscv_nacl`; functions/prototypes `__kvm_riscv_nacl_hfence`, `__kvm_riscv_nacl_switch_to`, `kvm_riscv_nacl_enable`, `kvm_riscv_nacl_disable`, `kvm_riscv_nacl_exit`, `kvm_riscv_nacl_init`; macros/constants `__KVM_NACL_H`, `kvm_riscv_nacl_available()`, `kvm_riscv_nacl_sync_csr_available()`, `kvm_riscv_nacl_sync_hfence_available()`, `kvm_riscv_nacl_sync_sret_available()`, `kvm_riscv_nacl_autoswap_csr_available()`, `lelong_to_cpu(__x) le32_to_cpu(__x)`, `cpu_to_lelong(__x) cpu_to_le32(__x)`, `lelong_to_cpu(__x) le64_to_cpu(__x)`, `cpu_to_lelong(__x) cpu_to_le64(__x)`, `nacl_shmem()`, `nacl_scratch_read_long(__shmem, __offset)`, `nacl_scratch_write_long(__shmem, __offset, __val)`, `nacl_scratch_write_longs(__shmem, __offset, __array, __count)`, plus 20 more.

## Control Flow
Runtime flow is driven by KVM VM/vCPU creation, guest entry/exit, SBI or MMIO/CSR emulation, interrupt injection, and TLB/fence processing. This header supplies state layouts and function contracts consumed by the C implementation files rather than executing logic itself. Special attention: NACL helpers build little-endian shared-memory records and SBI calls for synchronized CSR, HFENCE, SRET, autoswap, and guest/host switch acceleration.

## State And Persistence
Persistent state is per-VM and per-vCPU architecture state: guest registers, CSRs, timers, interrupt bitmaps, VMIDs, guest-stage page tables, AIA/IMSIC state, PMU counters, SBI state, and optional NACL shared memory. Lifetimes are tied to KVM objects and CPU entry/exit serialization.

## Dependencies And Integration Points
Direct includes are `linux/jump_label.h`, `linux/percpu.h`, `asm/byteorder.h`, `asm/csr.h`, `asm/sbi.h`. Integrates with generic KVM, SBI, RISC-V virtualization CSRs, guest-stage MMU code, AIA/IMSIC/APLIC interrupt controllers, hrtimers, perf, one-reg ioctls, QEMU/KVM userspace ABI, and low-level guest entry assembly.

## Risks And Edge Cases
Risks concentrate around guest-visible ABI drift, incorrect CSR or interrupt state migration, missing memory ordering around atomic bitmaps and fences, stale VMID/TLB state, incorrect shared-memory endian conversion, and mismatches with QEMU/KVM one-reg expectations.

## Test Signals
Test signals include RISC-V KVM selftests, QEMU/KVM guest boot and migration, SBI extension tests, timer and PMU tests, AIA/IMSIC interrupt injection, dirty logging, MMIO/CSR emulation, nested-acceleration availability, and TLB/fence stress.

Source read size: 245 lines, 7700 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_nacl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_tlb.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_tlb.h

## Purpose
Declares KVM hypervisor fence/TLB request types and local/remote guest-stage and virtual-address flush helpers.

## Important APIs, Types, And Functions
types `kvm_riscv_hfence_type`, `kvm_riscv_hfence`, `kvm_vcpu`, `kvm`; functions/prototypes `kvm_riscv_local_hfence_gvma_vmid_gpa`, `kvm_riscv_local_hfence_gvma_vmid_all`, `kvm_riscv_local_hfence_gvma_gpa`, `kvm_riscv_local_hfence_gvma_all`, `kvm_riscv_local_hfence_vvma_asid_gva`, `kvm_riscv_local_hfence_vvma_asid_all`, `kvm_riscv_local_hfence_vvma_gva`, `kvm_riscv_local_hfence_vvma_all`, `kvm_riscv_local_tlb_sanitize`, `kvm_riscv_tlb_flush_process`, `kvm_riscv_fence_i_process`, `kvm_riscv_hfence_vvma_all_process`, plus 8 more; macros/constants `__RISCV_KVM_TLB_H_`, `KVM_RISCV_VCPU_MAX_HFENCE`, `KVM_RISCV_GSTAGE_TLB_MIN_ORDER`.

## Control Flow
Runtime flow is driven by KVM VM/vCPU creation, guest entry/exit, SBI or MMIO/CSR emulation, interrupt injection, and TLB/fence processing. This header supplies state layouts and function contracts consumed by the C implementation files rather than executing logic itself.

## State And Persistence
Persistent state is per-VM and per-vCPU architecture state: guest registers, CSRs, timers, interrupt bitmaps, VMIDs, guest-stage page tables, AIA/IMSIC state, PMU counters, SBI state, and optional NACL shared memory. Lifetimes are tied to KVM objects and CPU entry/exit serialization.

## Dependencies And Integration Points
Direct includes are `linux/kvm_types.h`. Integrates with generic KVM, SBI, RISC-V virtualization CSRs, guest-stage MMU code, AIA/IMSIC/APLIC interrupt controllers, hrtimers, perf, one-reg ioctls, QEMU/KVM userspace ABI, and low-level guest entry assembly.

## Risks And Edge Cases
Risks concentrate around guest-visible ABI drift, incorrect CSR or interrupt state migration, missing memory ordering around atomic bitmaps and fences, stale VMID/TLB state, incorrect shared-memory endian conversion, and mismatches with QEMU/KVM one-reg expectations.

## Test Signals
Test signals include RISC-V KVM selftests, QEMU/KVM guest boot and migration, SBI extension tests, timer and PMU tests, AIA/IMSIC interrupt injection, dirty logging, MMIO/CSR emulation, nested-acceleration availability, and TLB/fence stress.

Source read size: 85 lines, 2865 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_tlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_types.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_types.h

## Purpose
Provides the RISC-V KVM memory-cache object-count constant for generic KVM code.

## Important APIs, Types, And Functions
macros/constants `_ASM_RISCV_KVM_TYPES_H`, `KVM_ARCH_NR_OBJS_PER_MEMORY_CACHE`.

## Control Flow
Runtime flow is driven by KVM VM/vCPU creation, guest entry/exit, SBI or MMIO/CSR emulation, interrupt injection, and TLB/fence processing. This header supplies state layouts and function contracts consumed by the C implementation files rather than executing logic itself.

## State And Persistence
Persistent state is per-VM and per-vCPU architecture state: guest registers, CSRs, timers, interrupt bitmaps, VMIDs, guest-stage page tables, AIA/IMSIC state, PMU counters, SBI state, and optional NACL shared memory. Lifetimes are tied to KVM objects and CPU entry/exit serialization.

## Dependencies And Integration Points
It has no direct includes. Integrates with generic KVM, SBI, RISC-V virtualization CSRs, guest-stage MMU code, AIA/IMSIC/APLIC interrupt controllers, hrtimers, perf, one-reg ioctls, QEMU/KVM userspace ABI, and low-level guest entry assembly.

## Risks And Edge Cases
Risks concentrate around guest-visible ABI drift, incorrect CSR or interrupt state migration, missing memory ordering around atomic bitmaps and fences, stale VMID/TLB state, incorrect shared-memory endian conversion, and mismatches with QEMU/KVM one-reg expectations.

## Test Signals
Test signals include RISC-V KVM selftests, QEMU/KVM guest boot and migration, SBI extension tests, timer and PMU tests, AIA/IMSIC interrupt injection, dirty logging, MMIO/CSR emulation, nested-acceleration availability, and TLB/fence stress.

Source read size: 7 lines, 184 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_config.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_config.h

## Purpose
Declares RISC-V KVM vCPU configuration loading and debug/run-once policy hooks.

## Important APIs, Types, And Functions
types `kvm_vcpu`, `kvm_vcpu_config`; functions/prototypes `kvm_riscv_vcpu_config_init`, `kvm_riscv_vcpu_config_guest_debug`, `kvm_riscv_vcpu_config_ran_once`, `kvm_riscv_vcpu_config_load`; macros/constants `__KVM_VCPU_RISCV_CONFIG_H`.

## Control Flow
Runtime flow is driven by KVM VM/vCPU creation, guest entry/exit, SBI or MMIO/CSR emulation, interrupt injection, and TLB/fence processing. This header supplies state layouts and function contracts consumed by the C implementation files rather than executing logic itself. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
Persistent state is per-VM and per-vCPU architecture state: guest registers, CSRs, timers, interrupt bitmaps, VMIDs, guest-stage page tables, AIA/IMSIC state, PMU counters, SBI state, and optional NACL shared memory. Lifetimes are tied to KVM objects and CPU entry/exit serialization.

## Dependencies And Integration Points
Direct includes are `linux/types.h`. Integrates with generic KVM, SBI, RISC-V virtualization CSRs, guest-stage MMU code, AIA/IMSIC/APLIC interrupt controllers, hrtimers, perf, one-reg ioctls, QEMU/KVM userspace ABI, and low-level guest entry assembly.

## Risks And Edge Cases
Risks concentrate around guest-visible ABI drift, incorrect CSR or interrupt state migration, missing memory ordering around atomic bitmaps and fences, stale VMID/TLB state, incorrect shared-memory endian conversion, and mismatches with QEMU/KVM one-reg expectations.

## Test Signals
Test signals include RISC-V KVM selftests, QEMU/KVM guest boot and migration, SBI extension tests, timer and PMU tests, AIA/IMSIC interrupt injection, dirty logging, MMIO/CSR emulation, nested-acceleration availability, and TLB/fence stress.

Source read size: 25 lines, 565 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_config.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_fp.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_fp.h

## Purpose
Declares guest and host floating-point context save/restore and FP register get/set helpers.

## Important APIs, Types, And Functions
types `kvm_cpu_context`, `kvm_vcpu`, `kvm_one_reg`; functions/prototypes `__kvm_riscv_fp_f_save`, `__kvm_riscv_fp_f_restore`, `__kvm_riscv_fp_d_save`, `__kvm_riscv_fp_d_restore`, `kvm_riscv_vcpu_fp_reset`, `kvm_riscv_vcpu_guest_fp_save`, `kvm_riscv_vcpu_guest_fp_restore`, `kvm_riscv_vcpu_host_fp_save`, `kvm_riscv_vcpu_host_fp_restore`, `kvm_riscv_vcpu_get_reg_fp`, `kvm_riscv_vcpu_set_reg_fp`; macros/constants `__KVM_VCPU_RISCV_FP_H`.

## Control Flow
Runtime flow is driven by KVM VM/vCPU creation, guest entry/exit, SBI or MMIO/CSR emulation, interrupt injection, and TLB/fence processing. This header supplies state layouts and function contracts consumed by the C implementation files rather than executing logic itself. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
Persistent state is per-VM and per-vCPU architecture state: guest registers, CSRs, timers, interrupt bitmaps, VMIDs, guest-stage page tables, AIA/IMSIC state, PMU counters, SBI state, and optional NACL shared memory. Lifetimes are tied to KVM objects and CPU entry/exit serialization.

## Dependencies And Integration Points
Direct includes are `linux/types.h`. Integrates with generic KVM, SBI, RISC-V virtualization CSRs, guest-stage MMU code, AIA/IMSIC/APLIC interrupt controllers, hrtimers, perf, one-reg ioctls, QEMU/KVM userspace ABI, and low-level guest entry assembly.

## Risks And Edge Cases
Risks concentrate around guest-visible ABI drift, incorrect CSR or interrupt state migration, missing memory ordering around atomic bitmaps and fences, stale VMID/TLB state, incorrect shared-memory endian conversion, and mismatches with QEMU/KVM one-reg expectations.

## Test Signals
Test signals include RISC-V KVM selftests, QEMU/KVM guest boot and migration, SBI extension tests, timer and PMU tests, AIA/IMSIC interrupt injection, dirty logging, MMIO/CSR emulation, nested-acceleration availability, and TLB/fence stress.

Source read size: 59 lines, 1728 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_fp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_insn.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_insn.h

## Purpose
Declares KVM emulation paths for WFI, virtual instructions, CSR exits, and MMIO load/store completion.

## Important APIs, Types, And Functions
types `kvm_vcpu`, `kvm_run`, `kvm_cpu_trap`, `kvm_mmio_decode`, `kvm_csr_decode`, `kvm_insn_return`; functions/prototypes `kvm_riscv_vcpu_wfi`, `kvm_riscv_vcpu_csr_return`, `kvm_riscv_vcpu_virtual_insn`, `kvm_riscv_vcpu_mmio_load`, `kvm_riscv_vcpu_mmio_store`, `kvm_riscv_vcpu_mmio_return`; macros/constants `__KVM_VCPU_RISCV_INSN_H`.

## Control Flow
Runtime flow is driven by KVM VM/vCPU creation, guest entry/exit, SBI or MMIO/CSR emulation, interrupt injection, and TLB/fence processing. This header supplies state layouts and function contracts consumed by the C implementation files rather than executing logic itself.

## State And Persistence
Persistent state is per-VM and per-vCPU architecture state: guest registers, CSRs, timers, interrupt bitmaps, VMIDs, guest-stage page tables, AIA/IMSIC state, PMU counters, SBI state, and optional NACL shared memory. Lifetimes are tied to KVM objects and CPU entry/exit serialization.

## Dependencies And Integration Points
It has no direct includes. Integrates with generic KVM, SBI, RISC-V virtualization CSRs, guest-stage MMU code, AIA/IMSIC/APLIC interrupt controllers, hrtimers, perf, one-reg ioctls, QEMU/KVM userspace ABI, and low-level guest entry assembly.

## Risks And Edge Cases
Risks concentrate around guest-visible ABI drift, incorrect CSR or interrupt state migration, missing memory ordering around atomic bitmaps and fences, stale VMID/TLB state, incorrect shared-memory endian conversion, and mismatches with QEMU/KVM one-reg expectations.

## Test Signals
Test signals include RISC-V KVM selftests, QEMU/KVM guest boot and migration, SBI extension tests, timer and PMU tests, AIA/IMSIC interrupt injection, dirty logging, MMIO/CSR emulation, nested-acceleration availability, and TLB/fence stress.

Source read size: 48 lines, 1234 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_insn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_pmu.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_pmu.h

## Purpose
Declares KVM virtual PMU counters, firmware events, SBI PMU handlers, and snapshot shared-memory support.

## Important APIs, Types, And Functions
types `kvm_fw_event`, `kvm_pmc`, `perf_event`, `sbi_pmu_ctr_info`, `kvm_vcpu`, `kvm_pmu`, `riscv_pmu_snapshot_data`, `kvm_vcpu_sbi_return`; functions/prototypes `kvm_riscv_vcpu_pmu_incr_fw`, `kvm_riscv_vcpu_pmu_read_hpm`, `kvm_riscv_vcpu_pmu_num_ctrs`, `kvm_riscv_vcpu_pmu_ctr_info`, `kvm_riscv_vcpu_pmu_ctr_start`, `kvm_riscv_vcpu_pmu_ctr_stop`, `kvm_riscv_vcpu_pmu_ctr_cfg_match`, `kvm_riscv_vcpu_pmu_fw_ctr_read`, `kvm_riscv_vcpu_pmu_fw_ctr_read_hi`, `kvm_riscv_vcpu_pmu_init`, `kvm_riscv_vcpu_pmu_snapshot_set_shmem`, `kvm_riscv_vcpu_pmu_event_info`, plus 3 more; macros/constants `__KVM_VCPU_RISCV_PMU_H`, `RISCV_KVM_MAX_FW_CTRS`, `RISCV_KVM_MAX_HW_CTRS`, `RISCV_KVM_MAX_COUNTERS`, `vcpu_to_pmu(vcpu) (&(vcpu)->arch.pmu_context)`, `pmu_to_vcpu(pmu) (container_of((pmu), struct kvm_vcpu, arch.pmu_context))`, `KVM_RISCV_VCPU_HPMCOUNTER_CSR_FUNCS`.

## Control Flow
Runtime flow is driven by KVM VM/vCPU creation, guest entry/exit, SBI or MMIO/CSR emulation, interrupt injection, and TLB/fence processing. This header supplies state layouts and function contracts consumed by the C implementation files rather than executing logic itself. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
Persistent state is per-VM and per-vCPU architecture state: guest registers, CSRs, timers, interrupt bitmaps, VMIDs, guest-stage page tables, AIA/IMSIC state, PMU counters, SBI state, and optional NACL shared memory. Lifetimes are tied to KVM objects and CPU entry/exit serialization.

## Dependencies And Integration Points
Direct includes are `linux/perf/riscv_pmu.h`, `asm/kvm_vcpu_insn.h`, `asm/sbi.h`. Integrates with generic KVM, SBI, RISC-V virtualization CSRs, guest-stage MMU code, AIA/IMSIC/APLIC interrupt controllers, hrtimers, perf, one-reg ioctls, QEMU/KVM userspace ABI, and low-level guest entry assembly.

## Risks And Edge Cases
Risks concentrate around guest-visible ABI drift, incorrect CSR or interrupt state migration, missing memory ordering around atomic bitmaps and fences, stale VMID/TLB state, incorrect shared-memory endian conversion, and mismatches with QEMU/KVM one-reg expectations.

## Test Signals
Test signals include RISC-V KVM selftests, QEMU/KVM guest boot and migration, SBI extension tests, timer and PMU tests, AIA/IMSIC interrupt injection, dirty logging, MMIO/CSR emulation, nested-acceleration availability, and TLB/fence stress.

Source read size: 135 lines, 4837 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_pmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_sbi.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_sbi.h

## Purpose
Declares KVM SBI extension dispatch, reset handling, SBI register exposure, and extension context state.

## Important APIs, Types, And Functions
types `kvm_riscv_sbi_ext_status`, `kvm_vcpu_sbi_context`, `kvm_vcpu_sbi_return`, `kvm_cpu_trap`, `kvm_vcpu_sbi_extension`, `kvm_vcpu`, `kvm_run`, `kvm_one_reg`; functions/prototypes `kvm_riscv_vcpu_sbi_forward_handler`, `kvm_riscv_vcpu_sbi_system_reset`, `kvm_riscv_vcpu_sbi_request_reset`, `kvm_riscv_vcpu_sbi_load_reset_state`, `kvm_riscv_vcpu_sbi_return`, `kvm_riscv_vcpu_reg_indices_sbi_ext`, `kvm_riscv_vcpu_set_reg_sbi_ext`, `kvm_riscv_vcpu_get_reg_sbi_ext`, `kvm_riscv_vcpu_reg_indices_sbi`, `kvm_riscv_vcpu_set_reg_sbi`, `kvm_riscv_vcpu_get_reg_sbi`, `kvm_riscv_vcpu_sbi_ecall`, plus 18 more; macros/constants `__RISCV_KVM_VCPU_SBI_H__`, `KVM_SBI_IMPID`, `KVM_SBI_VERSION_MAJOR`, `KVM_SBI_VERSION_MINOR`.

## Control Flow
Runtime flow is driven by KVM VM/vCPU creation, guest entry/exit, SBI or MMIO/CSR emulation, interrupt injection, and TLB/fence processing. This header supplies state layouts and function contracts consumed by the C implementation files rather than executing logic itself. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
Persistent state is per-VM and per-vCPU architecture state: guest registers, CSRs, timers, interrupt bitmaps, VMIDs, guest-stage page tables, AIA/IMSIC state, PMU counters, SBI state, and optional NACL shared memory. Lifetimes are tied to KVM objects and CPU entry/exit serialization.

## Dependencies And Integration Points
It has no direct includes. Integrates with generic KVM, SBI, RISC-V virtualization CSRs, guest-stage MMU code, AIA/IMSIC/APLIC interrupt controllers, hrtimers, perf, one-reg ioctls, QEMU/KVM userspace ABI, and low-level guest entry assembly.

## Risks And Edge Cases
Risks concentrate around guest-visible ABI drift, incorrect CSR or interrupt state migration, missing memory ordering around atomic bitmaps and fences, stale VMID/TLB state, incorrect shared-memory endian conversion, and mismatches with QEMU/KVM one-reg expectations.

## Test Signals
Test signals include RISC-V KVM selftests, QEMU/KVM guest boot and migration, SBI extension tests, timer and PMU tests, AIA/IMSIC interrupt injection, dirty logging, MMIO/CSR emulation, nested-acceleration availability, and TLB/fence stress.

Source read size: 117 lines, 4416 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_sbi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_sbi_fwft.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_sbi_fwft.h

## Purpose
Defines KVM SBI FWFT feature configuration state.

## Important APIs, Types, And Functions
types `kvm_sbi_fwft_feature`, `kvm_sbi_fwft_config`, `kvm_sbi_fwft`; macros/constants `__KVM_VCPU_RISCV_FWFT_H`, `vcpu_to_fwft(vcpu) (&(vcpu)->arch.fwft_context)`.

## Control Flow
Runtime flow is driven by KVM VM/vCPU creation, guest entry/exit, SBI or MMIO/CSR emulation, interrupt injection, and TLB/fence processing. This header supplies state layouts and function contracts consumed by the C implementation files rather than executing logic itself. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
Persistent state is per-VM and per-vCPU architecture state: guest registers, CSRs, timers, interrupt bitmaps, VMIDs, guest-stage page tables, AIA/IMSIC state, PMU counters, SBI state, and optional NACL shared memory. Lifetimes are tied to KVM objects and CPU entry/exit serialization.

## Dependencies And Integration Points
Direct includes are `asm/sbi.h`. Integrates with generic KVM, SBI, RISC-V virtualization CSRs, guest-stage MMU code, AIA/IMSIC/APLIC interrupt controllers, hrtimers, perf, one-reg ioctls, QEMU/KVM userspace ABI, and low-level guest entry assembly.

## Risks And Edge Cases
Risks concentrate around guest-visible ABI drift, incorrect CSR or interrupt state migration, missing memory ordering around atomic bitmaps and fences, stale VMID/TLB state, incorrect shared-memory endian conversion, and mismatches with QEMU/KVM one-reg expectations.

## Test Signals
Test signals include RISC-V KVM selftests, QEMU/KVM guest boot and migration, SBI extension tests, timer and PMU tests, AIA/IMSIC interrupt injection, dirty logging, MMIO/CSR emulation, nested-acceleration availability, and TLB/fence stress.

Source read size: 34 lines, 663 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_sbi_fwft.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_timer.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_timer.h

## Purpose
Declares guest timer and per-vCPU timer state, register accessors, synchronization, and pending-event helpers.

## Important APIs, Types, And Functions
types `kvm_guest_timer`, `kvm_vcpu_timer`, `hrtimer`, `kvm_vcpu`, `kvm_one_reg`, `kvm`; functions/prototypes `kvm_riscv_vcpu_timer_next_event`, `kvm_riscv_vcpu_get_reg_timer`, `kvm_riscv_vcpu_set_reg_timer`, `kvm_riscv_vcpu_timer_init`, `kvm_riscv_vcpu_timer_deinit`, `kvm_riscv_vcpu_timer_reset`, `kvm_riscv_vcpu_timer_restore`, `kvm_riscv_guest_timer_init`, `kvm_riscv_vcpu_timer_sync`, `kvm_riscv_vcpu_timer_save`, `kvm_riscv_vcpu_timer_pending`; macros/constants `__KVM_VCPU_RISCV_TIMER_H`.

## Control Flow
Runtime flow is driven by KVM VM/vCPU creation, guest entry/exit, SBI or MMIO/CSR emulation, interrupt injection, and TLB/fence processing. This header supplies state layouts and function contracts consumed by the C implementation files rather than executing logic itself.

## State And Persistence
Persistent state is per-VM and per-vCPU architecture state: guest registers, CSRs, timers, interrupt bitmaps, VMIDs, guest-stage page tables, AIA/IMSIC state, PMU counters, SBI state, and optional NACL shared memory. Lifetimes are tied to KVM objects and CPU entry/exit serialization.

## Dependencies And Integration Points
Direct includes are `linux/hrtimer.h`. Integrates with generic KVM, SBI, RISC-V virtualization CSRs, guest-stage MMU code, AIA/IMSIC/APLIC interrupt controllers, hrtimers, perf, one-reg ioctls, QEMU/KVM userspace ABI, and low-level guest entry assembly.

## Risks And Edge Cases
Risks concentrate around guest-visible ABI drift, incorrect CSR or interrupt state migration, missing memory ordering around atomic bitmaps and fences, stale VMID/TLB state, incorrect shared-memory endian conversion, and mismatches with QEMU/KVM one-reg expectations.

## Test Signals
Test signals include RISC-V KVM selftests, QEMU/KVM guest boot and migration, SBI extension tests, timer and PMU tests, AIA/IMSIC interrupt injection, dirty logging, MMIO/CSR emulation, nested-acceleration availability, and TLB/fence stress.

Source read size: 52 lines, 1595 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_vector.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_vector.h

## Purpose
Declares guest and host vector context allocation, save/restore, and vector register get/set helpers.

## Important APIs, Types, And Functions
types `kvm_cpu_context`, `kvm_vcpu`, `kvm_one_reg`; functions/prototypes `__kvm_riscv_vector_save`, `__kvm_riscv_vector_restore`, `kvm_riscv_vcpu_vector_reset`, `kvm_riscv_vcpu_guest_vector_save`, `kvm_riscv_vcpu_guest_vector_restore`, `kvm_riscv_vcpu_host_vector_save`, `kvm_riscv_vcpu_host_vector_restore`, `kvm_riscv_vcpu_alloc_vector_context`, `kvm_riscv_vcpu_free_vector_context`, `kvm_riscv_vcpu_get_reg_vector`, `kvm_riscv_vcpu_set_reg_vector`; macros/constants `__KVM_VCPU_RISCV_VECTOR_H`.

## Control Flow
Runtime flow is driven by KVM VM/vCPU creation, guest entry/exit, SBI or MMIO/CSR emulation, interrupt injection, and TLB/fence processing. This header supplies state layouts and function contracts consumed by the C implementation files rather than executing logic itself. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
Persistent state is per-VM and per-vCPU architecture state: guest registers, CSRs, timers, interrupt bitmaps, VMIDs, guest-stage page tables, AIA/IMSIC state, PMU counters, SBI state, and optional NACL shared memory. Lifetimes are tied to KVM objects and CPU entry/exit serialization.

## Dependencies And Integration Points
Direct includes are `linux/types.h`, `asm/vector.h`, `asm/kvm_host.h`. Integrates with generic KVM, SBI, RISC-V virtualization CSRs, guest-stage MMU code, AIA/IMSIC/APLIC interrupt controllers, hrtimers, perf, one-reg ioctls, QEMU/KVM userspace ABI, and low-level guest entry assembly.

## Risks And Edge Cases
Risks concentrate around guest-visible ABI drift, incorrect CSR or interrupt state migration, missing memory ordering around atomic bitmaps and fences, stale VMID/TLB state, incorrect shared-memory endian conversion, and mismatches with QEMU/KVM one-reg expectations.

## Test Signals
Test signals include RISC-V KVM selftests, QEMU/KVM guest boot and migration, SBI extension tests, timer and PMU tests, AIA/IMSIC interrupt injection, dirty logging, MMIO/CSR emulation, nested-acceleration availability, and TLB/fence stress.

Source read size: 78 lines, 2098 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vcpu_vector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vmid.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vmid.h

## Purpose
Declares guest-stage VMID bit discovery, version tracking, initialization, and update helpers.

## Important APIs, Types, And Functions
types `kvm_vmid`, `kvm`, `kvm_vcpu`; functions/prototypes `kvm_riscv_gstage_vmid_bits`, `kvm_riscv_gstage_vmid_init`, `kvm_riscv_gstage_vmid_ver_changed`, `kvm_riscv_gstage_vmid_update`; macros/constants `__RISCV_KVM_VMID_H_`.

## Control Flow
Runtime flow is driven by KVM VM/vCPU creation, guest entry/exit, SBI or MMIO/CSR emulation, interrupt injection, and TLB/fence processing. This header supplies state layouts and function contracts consumed by the C implementation files rather than executing logic itself.

## State And Persistence
Persistent state is per-VM and per-vCPU architecture state: guest registers, CSRs, timers, interrupt bitmaps, VMIDs, guest-stage page tables, AIA/IMSIC state, PMU counters, SBI state, and optional NACL shared memory. Lifetimes are tied to KVM objects and CPU entry/exit serialization.

## Dependencies And Integration Points
Direct includes are `linux/kvm_types.h`. Integrates with generic KVM, SBI, RISC-V virtualization CSRs, guest-stage MMU code, AIA/IMSIC/APLIC interrupt controllers, hrtimers, perf, one-reg ioctls, QEMU/KVM userspace ABI, and low-level guest entry assembly.

## Risks And Edge Cases
Risks concentrate around guest-visible ABI drift, incorrect CSR or interrupt state migration, missing memory ordering around atomic bitmaps and fences, stale VMID/TLB state, incorrect shared-memory endian conversion, and mismatches with QEMU/KVM one-reg expectations.

## Test Signals
Test signals include RISC-V KVM selftests, QEMU/KVM guest boot and migration, SBI extension tests, timer and PMU tests, AIA/IMSIC interrupt injection, dirty logging, MMIO/CSR emulation, nested-acceleration availability, and TLB/fence stress.

Source read size: 26 lines, 654 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/kvm_vmid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/linkage.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/linkage.h

## Purpose
Defines RISC-V function alignment used by assembler linkage macros.

## Important APIs, Types, And Functions
macros/constants `_ASM_RISCV_LINKAGE_H`, `__ALIGN`, `__ALIGN_STR`.

## Control Flow
The control flow is mostly preprocessor and assembler expansion: low-level entry, trap, module, and patching code include these macros and emit exact instructions or section records at build time.

## State And Persistence
State is usually encoded in generated sections, register save areas, alternative tables, exception tables, or trap metadata rather than stored in this header. The definitions must remain stable because assembly and C code share them.

## Dependencies And Integration Points
It has no direct includes. Integrates with RISC-V assembler support, generated offsets, linker sections, alternatives, exception tables, low-level entry code, module relocation, and compiler feature tests.

## Risks And Edge Cases
Risks are instruction-encoding, section-layout, relocation, register-width, and generated-offset mistakes. A small macro change can break boot, trap entry, module loading, or runtime text patching.

## Test Signals
Test signals include defconfig/allmodconfig builds, objdump validation of emitted instructions and sections, boot smoke tests, module load/unload, alternatives/errata patch logs, exception fixup tests, and trap-entry stress.

Source read size: 12 lines, 267 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/linkage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/membarrier.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/membarrier.h

## Purpose
Implements RISC-V membarrier hooks for switching memory contexts.

## Important APIs, Types, And Functions
types `mm_struct`, `task_struct`; functions/prototypes `membarrier_arch_switch_mm`; macros/constants `_ASM_RISCV_MEMBARRIER_H`.

## Control Flow
The header is primarily declarative. Runtime behavior occurs in the including architecture implementation files and generic Linux subsystems that consume the constants, types, macros, and prototypes defined here. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
The header itself owns no filesystem or durable state. It defines ABI-like constants or inline behavior consumed by longer-lived kernel objects.

## Dependencies And Integration Points
It has no direct includes. Integrates with generic Linux architecture headers and RISC-V implementation files through include-time contracts.

## Risks And Edge Cases
The main risk is that generic code treats these definitions as architecture ABI. Renaming, renumbering, or changing inline semantics without matching implementation changes can create build-only or boot-time failures.

## Test Signals
Test signals include architecture build coverage, include dependency checks, and subsystem tests for the generic code that consumes this header.

Source read size: 50 lines, 1767 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/membarrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/mman.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/mman.h

## Purpose
Maps RISC-V mmap protection bits to generic VM flags, including tagged-address/memory-type policy hooks.

## Important APIs, Types, And Functions
functions/prototypes `arch_calc_vm_prot_bits`; macros/constants `__ASM_MMAN_H__`, `arch_calc_vm_prot_bits(prot, pkey) arch_calc_vm_prot_bits(prot, pkey)`.

## Control Flow
Runtime flow is reached through generic MM, page-table, fault, TLB, and mapping callbacks. The header supplies inline conversions and declarations that the implementation files call during context switch, map/unmap, and flush paths.

## State And Persistence
State is carried in `mm_struct`, page tables, ASIDs, fixed mappings, folios, cache/TLB state, or architecture context fields; this header defines how those state holders are interpreted.

## Dependencies And Integration Points
Direct includes are `linux/compiler.h`, `linux/types.h`, `linux/mm.h`, `uapi/asm/mman.h`. Integrates with Linux MM, page-table helpers, TLB shootdown, cache maintenance, hugetlb, KASAN/KFENCE, EFI mapping, kexec, and architecture fault handling.

## Risks And Edge Cases
Risks include stale cache/TLB state, wrong virtual/physical conversions, ASID/version reuse bugs, fixed-map overlap, hugepage PTE corruption, and ABI changes in ELF or image headers.

## Test Signals
Test signals include MM selftests, mmap/mprotect/fork/exec stress, hugetlb tests, KASAN/KFENCE boot, kexec/crashkernel boot, EFI boot, cacheflush tests, and TLB shootdown stress.

Source read size: 26 lines, 623 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/mmio.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/mmio.h

## Purpose
Defines raw and endian-converting MMIO accessors plus relaxed/ordered read/write wrappers.

## Important APIs, Types, And Functions
functions/prototypes `__raw_writeb`, `__raw_writew`, `__raw_writel`, `__raw_writeq`, `__raw_readb`, `__raw_readw`, `__raw_readl`, `__raw_readq`; macros/constants `_ASM_RISCV_MMIO_H`, `__raw_writeb`, `__raw_writew`, `__raw_writel`, `__raw_writeq`, `__raw_readb`, `__raw_readw`, `__raw_readl`, `__raw_readq`, `readb_cpu(c) ({ u8 __r = __raw_readb(c); __r; })`, `readw_cpu(c) ({ u16 __r = le16_to_cpu((__force __le16)__raw_readw(c)); __r; })`, `readl_cpu(c) ({ u32 __r = le32_to_cpu((__force __le32)__raw_readl(c)); __r; })`, `writeb_cpu(v, c) ((void)__raw_writeb((v), (c)))`, `writew_cpu(v, c) ((void)__raw_writew((__force u16)cpu_to_le16(v), (c)))`, plus 27 more.

## Control Flow
Runtime flow is a wrapper sequence around MMIO or port-I/O reads and writes: optional fences bracket raw loads/stores, endian conversion is applied for CPU-visible values, and generic driver code calls the resulting accessors. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
No durable state is stored by the header. Accessors mutate device-visible MMIO state and rely on fences to preserve ordering against CPUs, DMA, and devices.

## Dependencies And Integration Points
Direct includes are `linux/types.h`, `asm/fence.h`, `asm/mmiowb.h`. Integrates with driver MMIO APIs, PCI I/O space, generic `asm-generic/io.h`, DMA/noncoherent cache hooks, and RISC-V fence semantics.

## Risks And Edge Cases
Risks are missing fences, wrong endian conversion, noncoherent DMA cache omissions, and incorrect port/MMIO address translation, which can produce device data corruption or ordering bugs.

## Test Signals
Test signals include driver probe and DMA tests on coherent and noncoherent systems, PCI enumeration, MMIO ordering litmus tests, CBO cache-maintenance tests, and sparse/endian build checks.

Source read size: 152 lines, 5292 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/mmio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/mmiowb.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/mmiowb.h

## Purpose
Defines RISC-V MMIO write barrier behavior.

## Important APIs, Types, And Functions
macros/constants `_ASM_RISCV_MMIOWB_H`, `mmiowb() RISCV_FENCE(o, w)`.

## Control Flow
Runtime flow is a wrapper sequence around MMIO or port-I/O reads and writes: optional fences bracket raw loads/stores, endian conversion is applied for CPU-visible values, and generic driver code calls the resulting accessors.

## State And Persistence
No durable state is stored by the header. Accessors mutate device-visible MMIO state and rely on fences to preserve ordering against CPUs, DMA, and devices.

## Dependencies And Integration Points
Direct includes are `linux/smp.h`, `asm-generic/mmiowb.h`. Integrates with driver MMIO APIs, PCI I/O space, generic `asm-generic/io.h`, DMA/noncoherent cache hooks, and RISC-V fence semantics.

## Risks And Edge Cases
Risks are missing fences, wrong endian conversion, noncoherent DMA cache omissions, and incorrect port/MMIO address translation, which can produce device data corruption or ordering bugs.

## Test Signals
Test signals include driver probe and DMA tests on coherent and noncoherent systems, PCI enumeration, MMIO ordering litmus tests, CBO cache-maintenance tests, and sparse/endian build checks.

Source read size: 15 lines, 365 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/mmiowb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/mmu.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/mmu.h

## Purpose
Defines RISC-V MM context fields and ASID/version extraction helpers.

## Important APIs, Types, And Functions
macros/constants `_ASM_RISCV_MMU_H`, `MM_CONTEXT_LOCK_PMLEN`, `cntx2asid(cntx) ((cntx) & SATP_ASID_MASK)`, `cntx2version(cntx) ((cntx) & ~SATP_ASID_MASK)`.

## Control Flow
Runtime flow is reached through generic MM, page-table, fault, TLB, and mapping callbacks. The header supplies inline conversions and declarations that the implementation files call during context switch, map/unmap, and flush paths. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State is carried in `mm_struct`, page tables, ASIDs, fixed mappings, folios, cache/TLB state, or architecture context fields; this header defines how those state holders are interpreted.

## Dependencies And Integration Points
It has no direct includes. Integrates with Linux MM, page-table helpers, TLB shootdown, cache maintenance, hugetlb, KASAN/KFENCE, EFI mapping, kexec, and architecture fault handling.

## Risks And Edge Cases
Risks include stale cache/TLB state, wrong virtual/physical conversions, ASID/version reuse bugs, fixed-map overlap, hugepage PTE corruption, and ABI changes in ELF or image headers.

## Test Signals
Test signals include MM selftests, mmap/mprotect/fork/exec stress, hugetlb tests, KASAN/KFENCE boot, kexec/crashkernel boot, EFI boot, cacheflush tests, and TLB shootdown stress.

Source read size: 45 lines, 1075 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/mmu_context.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/mmu_context.h

## Purpose
Declares RISC-V address-space switching and context initialization hooks.

## Important APIs, Types, And Functions
types `mm_struct`, `task_struct`; functions/prototypes `switch_mm`, `activate_mm`, `init_new_context`, `mm_untag_mask`, `deactivate_mm`; macros/constants `_ASM_RISCV_MMU_CONTEXT_H`, `activate_mm`, `init_new_context`, `mm_untag_mask`, `deactivate_mm`.

## Control Flow
Runtime flow is reached through generic MM, page-table, fault, TLB, and mapping callbacks. The header supplies inline conversions and declarations that the implementation files call during context switch, map/unmap, and flush paths. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State is carried in `mm_struct`, page tables, ASIDs, fixed mappings, folios, cache/TLB state, or architecture context fields; this header defines how those state holders are interpreted.

## Dependencies And Integration Points
Direct includes are `linux/mm_types.h`, `asm-generic/mm_hooks.h`, `linux/mm.h`, `linux/sched.h`, `asm-generic/mmu_context.h`. Integrates with Linux MM, page-table helpers, TLB shootdown, cache maintenance, hugetlb, KASAN/KFENCE, EFI mapping, kexec, and architecture fault handling.

## Risks And Edge Cases
Risks include stale cache/TLB state, wrong virtual/physical conversions, ASID/version reuse bugs, fixed-map overlap, hugepage PTE corruption, and ABI changes in ELF or image headers.

## Test Signals
Test signals include MM selftests, mmap/mprotect/fork/exec stress, hugetlb tests, KASAN/KFENCE boot, kexec/crashkernel boot, EFI boot, cacheflush tests, and TLB shootdown stress.

Source read size: 60 lines, 1379 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/mmu_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/module.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/module.h

## Purpose
Defines RISC-V module GOT/PLT entry formats and relocation-emission helpers.

## Important APIs, Types, And Functions
types `module`, `mod_section`, `mod_arch_specific`, `got_entry`, `plt_entry`; functions/prototypes `module_emit_got_entry`, `module_emit_plt_entry`, `emit_got_entry`, `get_got_entry`, `emit_plt_entry`, `get_got_plt_idx`, `get_plt_entry`; macros/constants `_ASM_RISCV_MODULE_H`, `OPC_AUIPC`, `OPC_LD`, `OPC_JALR`, `REG_T0`, `REG_T1`.

## Control Flow
The header is primarily declarative. Runtime behavior occurs in the including architecture implementation files and generic Linux subsystems that consume the constants, types, macros, and prototypes defined here. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
The header itself owns no filesystem or durable state. It defines ABI-like constants or inline behavior consumed by longer-lived kernel objects.

## Dependencies And Integration Points
Direct includes are `asm-generic/module.h`, `linux/elf.h`. Integrates with generic Linux architecture headers and RISC-V implementation files through include-time contracts.

## Risks And Edge Cases
The main risk is that generic code treats these definitions as architecture ABI. Renaming, renumbering, or changing inline semantics without matching implementation changes can create build-only or boot-time failures.

## Test Signals
Test signals include architecture build coverage, include dependency checks, and subsystem tests for the generic code that consumes this header.

Source read size: 130 lines, 3375 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/module.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/module.lds.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/module.lds.h

## Purpose
Adds architecture-specific module linker script sections for RISC-V.

## Important APIs, Types, And Functions
include-time glue with no public C type or function declarations.

## Control Flow
The control flow is mostly preprocessor and assembler expansion: low-level entry, trap, module, and patching code include these macros and emit exact instructions or section records at build time. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State is usually encoded in generated sections, register save areas, alternative tables, exception tables, or trap metadata rather than stored in this header. The definitions must remain stable because assembly and C code share them.

## Dependencies And Integration Points
It has no direct includes. Integrates with RISC-V assembler support, generated offsets, linker sections, alternatives, exception tables, low-level entry code, module relocation, and compiler feature tests.

## Risks And Edge Cases
Risks are instruction-encoding, section-layout, relocation, register-width, and generated-offset mistakes. A small macro change can break boot, trap entry, module loading, or runtime text patching.

## Test Signals
Test signals include defconfig/allmodconfig builds, objdump validation of emitted instructions and sections, boot smoke tests, module load/unload, alternatives/errata patch logs, exception fixup tests, and trap-entry stress.

Source read size: 9 lines, 207 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/module.lds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/numa.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/numa.h

## Purpose
Selects RISC-V NUMA topology support through generic topology headers.

## Important APIs, Types, And Functions
macros/constants `__ASM_NUMA_H`.

## Control Flow
The header is primarily declarative. Runtime behavior occurs in the including architecture implementation files and generic Linux subsystems that consume the constants, types, macros, and prototypes defined here.

## State And Persistence
The header itself owns no filesystem or durable state. It defines ABI-like constants or inline behavior consumed by longer-lived kernel objects.

## Dependencies And Integration Points
Direct includes are `asm/topology.h`, `asm-generic/numa.h`. Integrates with generic Linux architecture headers and RISC-V implementation files through include-time contracts.

## Risks And Edge Cases
The main risk is that generic code treats these definitions as architecture ABI. Renaming, renumbering, or changing inline semantics without matching implementation changes can create build-only or boot-time failures.

## Test Signals
Test signals include architecture build coverage, include dependency checks, and subsystem tests for the generic code that consumes this header.

Source read size: 8 lines, 165 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/numa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/page.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/page.h

## Purpose
Defines RISC-V page geometry, kernel virtual layout, PTE/PGD wrappers, and physical/virtual translation helpers.

## Important APIs, Types, And Functions
types `definitions`, `page`, `kernel_mapping`; functions/prototypes `clear_page`, `linear_mapping_pa_to_va`, `linear_mapping_va_to_pa`, `__virt_to_phys`, `__phys_addr_symbol`, `kaslr_offset`, `pfn_to_kaddr`, `kernel_map`, `phys_ram_base`, `vmemmap_start_pfn`; macros/constants `_ASM_RISCV_PAGE_H`, `HPAGE_SHIFT`, `HPAGE_SIZE`, `HPAGE_MASK`, `HUGETLB_PAGE_ORDER`, `PAGE_OFFSET_L5`, `PAGE_OFFSET_L4`, `PAGE_OFFSET_L3`, `PAGE_OFFSET`, `clear_page(pgaddr) memset((pgaddr), 0, PAGE_SIZE)`, `copy_page(to, from) memcpy((to), (from), PAGE_SIZE)`, `copy_user_page(vto, vfrom, vaddr, topg) copy_page(vto, vfrom)`, `pte_val(x) ((x).pte)`, `pgd_val(x) ((x).pgd)`, plus 29 more.

## Control Flow
Runtime flow is reached through generic MM, page-table, fault, TLB, and mapping callbacks. The header supplies inline conversions and declarations that the implementation files call during context switch, map/unmap, and flush paths. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State is carried in `mm_struct`, page tables, ASIDs, fixed mappings, folios, cache/TLB state, or architecture context fields; this header defines how those state holders are interpreted.

## Dependencies And Integration Points
Direct includes are `linux/pfn.h`, `linux/const.h`, `vdso/page.h`, `asm-generic/memory_model.h`, `asm-generic/getorder.h`. Integrates with Linux MM, page-table helpers, TLB shootdown, cache maintenance, hugetlb, KASAN/KFENCE, EFI mapping, kexec, and architecture fault handling.

## Risks And Edge Cases
Risks include stale cache/TLB state, wrong virtual/physical conversions, ASID/version reuse bugs, fixed-map overlap, hugepage PTE corruption, and ABI changes in ELF or image headers.

## Test Signals
Test signals include MM selftests, mmap/mprotect/fork/exec stress, hugetlb tests, KASAN/KFENCE boot, kexec/crashkernel boot, EFI boot, cacheflush tests, and TLB shootdown stress.

Source read size: 186 lines, 5221 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/page.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/paravirt.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/paravirt.h

## Purpose
Provides the current RISC-V paravirtualization placeholder hooks.

## Important APIs, Types, And Functions
macros/constants `_ASM_RISCV_PARAVIRT_H`, `pv_time_init() do {} while (0)`.

## Control Flow
The header is primarily declarative. Runtime behavior occurs in the including architecture implementation files and generic Linux subsystems that consume the constants, types, macros, and prototypes defined here. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
The header itself owns no filesystem or durable state. It defines ABI-like constants or inline behavior consumed by longer-lived kernel objects.

## Dependencies And Integration Points
It has no direct includes. Integrates with generic Linux architecture headers and RISC-V implementation files through include-time contracts.

## Risks And Edge Cases
The main risk is that generic code treats these definitions as architecture ABI. Renaming, renumbering, or changing inline semantics without matching implementation changes can create build-only or boot-time failures.

## Test Signals
Test signals include architecture build coverage, include dependency checks, and subsystem tests for the generic code that consumes this header.

Source read size: 14 lines, 267 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/paravirt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/pci.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/pci.h

## Purpose
Defines RISC-V PCI I/O and memory minimums, bus-to-node lookup, and generic PCI integration.

## Important APIs, Types, And Functions
types `pci_bus`; functions/prototypes `pcibus_to_node`; macros/constants `_ASM_RISCV_PCI_H`, `PCIBIOS_MIN_IO`, `PCIBIOS_MIN_MEM`, `cpumask_of_pcibus(bus) (pcibus_to_node(bus)`.

## Control Flow
Runtime flow is a wrapper sequence around MMIO or port-I/O reads and writes: optional fences bracket raw loads/stores, endian conversion is applied for CPU-visible values, and generic driver code calls the resulting accessors. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
No durable state is stored by the header. Accessors mutate device-visible MMIO state and rely on fences to preserve ordering against CPUs, DMA, and devices.

## Dependencies And Integration Points
Direct includes are `linux/types.h`, `linux/slab.h`, `linux/dma-mapping.h`, `asm/io.h`, `asm-generic/pci.h`. Integrates with driver MMIO APIs, PCI I/O space, generic `asm-generic/io.h`, DMA/noncoherent cache hooks, and RISC-V fence semantics.

## Risks And Edge Cases
Risks are missing fences, wrong endian conversion, noncoherent DMA cache omissions, and incorrect port/MMIO address translation, which can produce device data corruption or ordering bugs.

## Test Signals
Test signals include driver probe and DMA tests on coherent and noncoherent systems, PCI enumeration, MMIO ordering litmus tests, CBO cache-maintenance tests, and sparse/endian build checks.

Source read size: 33 lines, 728 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/perf_event.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/perf_event.h

## Purpose
Declares RISC-V perf caller-register capture and BPF user-register mapping helpers.

## Important APIs, Types, And Functions
types `user_regs_struct`; macros/constants `_ASM_RISCV_PERF_EVENT_H`, `perf_arch_bpf_user_pt_regs(regs) (struct user_regs_struct *)`, `perf_arch_fetch_caller_regs(regs, __ip)`.

## Control Flow
Runtime flow is driven by dynamic patching and trap/debug callbacks: ftrace, jump-labels, kprobes, KGDB, BUG, and exception tables rewrite or interpret instruction streams at runtime. Configuration-sensitive branches in this header mean build coverage must include the enabled and disabled forms of the relevant `CONFIG_*` options.

## State And Persistence
State is held in patched text, per-probe/ftrace records, exception table entries, debug register snapshots, static keys, or trap frames depending on the subsystem.

## Dependencies And Integration Points
Direct includes are `linux/perf_event.h`. Integrates with ftrace, jump labels, kprobes, KGDB, BUG/WARN, exception-table fixups, perf, and architecture trap handling.

## Risks And Edge Cases
Risks include patching the wrong instruction width, corrupting breakpoint/probe/ftrace state, exception-table data packing mistakes, and debug/trap handlers losing register state.

## Test Signals
Test signals include ftrace and function-graph selftests, static-key/jump-label tests, kprobes/KGDB tests, BUG/WARN/oops decoding, perf callchain checks, and exception-table fault-injection tests.

Source read size: 23 lines, 575 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/perf_event.h -->
