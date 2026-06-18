# subset-b-000814 research

Grouped research for RISC-V architecture MMU, syscall, SBI, vector, vendor extension, UAPI, ACPI, alternatives, and low-level kernel support files. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/pgalloc.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/pgalloc.h

Purpose: Provides RISC-V page-table page allocation and population helpers for the Linux MMU, including PMD/PUD/P4D/PGD population, kernel mapping synchronization, and TLB-free hooks.

Important APIs/types/functions: `pmd_populate_kernel()`, `pmd_populate()`, `pud_populate()`, `p4d_populate()`, `pgd_populate()`, `p4d_populate_safe()`, `pgd_populate_safe()`, `pgd_alloc()`, `pud_free()`, `__pud_free_tlb()`, `__p4d_free_tlb()`, `__pmd_free_tlb()`, `__pte_free_tlb()`, and `sync_kernel_mappings()`.

Control flow: Population helpers convert child table virtual addresses or pages into PFNs and install entries with table protections. `pgd_alloc()` allocates a PGD, copies/synchronizes kernel mappings, and returns it to generic MM. TLB free helpers hand page-table pages to `tlb_remove_ptdesc()` only when the relevant levels are not folded.

State and persistence: State is page-table memory owned by each `mm_struct`; no persistent data is stored in the header. The important persistence behavior is keeping each process PGD synchronized with global kernel mappings.

Dependencies and integration points: Depends on Linux generic pgalloc, `asm/tlb.h`, `asm/sbi.h`, RISC-V pgtable types, folded level configuration, and mmu_gather teardown.

Risks: Wrong PFN/protection encoding, missing kernel mapping sync, or freeing a folded level would corrupt address spaces. Safe population helpers rely on callers only installing non-present or identical entries.

Test signals: Boot, fork/exec stress, vmalloc/module mapping, page-table debug, KASAN/KFENCE, THP on RV64, and TLB gather teardown tests are relevant.

Source read size: 140 lines, 3250 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/pgalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/pgtable-32.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/pgtable-32.h

Purpose: Defines the RV32 page-table geometry and PTE bit masks used by the common RISC-V pgtable layer.

Important APIs/types/functions: Key definitions are `PGDIR_SHIFT`, `PGDIR_SIZE`, `PGDIR_MASK`, `MAX_POSSIBLE_PHYSMEM_BITS`, `_PAGE_PFN_MASK`, `_PAGE_CHG_MASK`, and zero-valued cacheability attributes.

Control flow: There is no runtime control flow; including `asm-generic/pgtable-nopmd.h` folds PMD and higher levels for Sv32.

State and persistence: No state is stored; constants shape every RV32 page-table walk and swap/PFN encoding.

Dependencies and integration points: Used by `pgtable.h` for non-64-bit builds and by generic MM macros that consume folded page-table levels.

Risks: Changing shifts or PFN masks breaks Sv32 virtual layout, physical address reach, and swap/PTE preservation semantics.

Test signals: RV32 defconfig build, boot, mmap boundary tests, highmem/physical-memory sizing, and page-table selftests.

Source read size: 39 lines, 1092 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/pgtable-32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/pgtable-64.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/pgtable-64.h

Purpose: Defines RV64 Sv39/Sv48/Sv57 page-table geometry, upper-level entry types, hugepage support, NAPOT contiguous mappings, and vendor/cache memory-type bits.

Important APIs/types/functions: Important items include `pgtable_l4_enabled`, `pgtable_l5_enabled`, `PGDIR/P4D/PUD/PMD_*` geometry, `p4d_t`, `pud_t`, `pmd_t`, `pud_*`, `p4d_*`, `pgd_*`, `pfn_pmd()`, `pfn_pud()`, `riscv_page_mtmask()`, `riscv_page_nocache()`, and NAPOT helpers.

Control flow: Most helpers test presence/leaf/bad state, set entries with `WRITE_ONCE`, convert entries to lower page-table pointers or pages, and select Svpbmt versus T-Head PMA memory-type bits at runtime.

State and persistence: Persistent state is limited to global booleans selecting 4-level or 5-level page tables; entries encode PFN, leaf, user, and memory-type state.

Dependencies and integration points: Depends on cpufeature/errata alternatives, Svpbmt/Svnapot config, T-Head PMA alternatives, and the common `pgtable.h` PTE helpers.

Risks: Level folding, PFN masking, NAPOT order decoding, and memory-type selection are boot- and data-corruption sensitive.

Test signals: RV64 boots across Sv39/Sv48/Sv57, hugepage and NAPOT mappings, ioremap cacheability, T-Head errata machines, and page-table debug.

Source read size: 406 lines, 9738 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/pgtable-64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/pgtable-bits.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/pgtable-bits.h

Purpose: Centralizes RISC-V PTE bit definitions shared by 32-bit and 64-bit pgtable code.

Important APIs/types/functions: Defines hardware bits such as `_PAGE_PRESENT`, `_PAGE_READ`, `_PAGE_WRITE`, `_PAGE_EXEC`, `_PAGE_USER`, `_PAGE_GLOBAL`, `_PAGE_ACCESSED`, `_PAGE_DIRTY`, plus Linux software bits like `_PAGE_PROT_NONE`, `_PAGE_SPECIAL`, `_PAGE_TABLE`, `_PAGE_LEAF`, soft-dirty, uffd-wp, and swap-exclusive encodings.

Control flow: No runtime flow; macros compose hardware and software permissions used by page table creation and mutation.

State and persistence: PTE bit layout is persistent ABI-like kernel state because live page tables, swap PTEs, and migration entries store these values.

Dependencies and integration points: Consumed by `pgtable.h`, `pgtable-32.h`, `pgtable-64.h`, fault handlers, swap code, THP, and userfaultfd/soft-dirty support.

Risks: Bit collisions with hardware extensions or vendor PMA/Svpbmt bits can make valid entries fault, grant unintended access, or lose swap metadata.

Test signals: Build matrix for soft-dirty, uffd-wp, THP, swap, Svrsw60t59b, Svpbmt, and page-table selftests.

Source read size: 78 lines, 2334 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/pgtable-bits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/pgtable.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/pgtable.h

Purpose: Implements the main RISC-V Linux page-table contract: virtual address layout, page protections, PTE/PMD/PUD/PGD conversion helpers, TLB cache update hooks, THP helpers, swap encoding, and task-size definitions.

Important APIs/types/functions: Key APIs include `pte_pfn()`, `pfn_pte()`, `pte_present()`, `pte_accessible()`, `pte_modify()`, `set_ptes()`, `ptep_get_and_clear()`, `ptep_set_wrprotect()`, `pgprot_noncached()`, `pgprot_writecombine()`, THP `pmd*`/`pud*` helpers, swap macros, `update_mmu_cache_range()`, `set_pgd_safe()`, and `set_p4d_safe()`.

Control flow: The header computes MMU layout from Sv32/Sv39/Sv48/Sv57, builds protection constants, mutates PTEs with `WRITE_ONCE`/atomic exchange, flushes icache for executable mappings, and issues local SFENCE.VMA for new valid mappings unless Svvptc makes invalid-entry caching safe.

State and persistence: Persistent state includes global page directories, early page-table allocation callbacks, `satp_mode`, early DTB pointers, and every live page-table entry. It also encodes swap type/offset/exclusive/soft-dirty/uffd-wp state in non-present PTEs.

Dependencies and integration points: Integrates with generic Linux MM, TLB flush, page-table check, cpufeature, compat task sizing, THP, NUMA balancing, Svnapot, Svadu/Svade A/D semantics, and T-Head PMA alternatives.

Risks: This is high-risk memory-management code. Incorrect address-space sizing, missing SFENCE, bad A/D assumptions, incorrect shadow-stack write-protect handling, or swap-bit collisions can cause memory corruption or security bugs.

Test signals: RISC-V MM boot tests, mmap limit tests, fork/exec, swap, THP collapse/split, NUMA balancing, userfaultfd, soft-dirty, icache coherency, KASAN, page_table_check, and vendor-extension systems are strong signals.

Source read size: 1288 lines, 32232 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/probes.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/probes.h

Purpose: Defines RISC-V architecture interfaces for `probes.h`.

Important APIs/types/functions: The file is a small architecture header whose exported macros/types are consumed by nearby RISC-V kernel code.

Control flow: Control flow is compile-time or inline only, with runtime behavior provided by implementation files.

State and persistence: No substantial private state is stored in this header.

Dependencies and integration points: Integrates with the surrounding RISC-V architecture subsystem and generic Linux kernel APIs.

Risks: The main risk is ABI or include-contract drift with its implementation users.

Test signals: Architecture build coverage and subsystem-specific runtime tests.

Source read size: 24 lines, 563 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/probes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/processor.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/processor.h

Purpose: Defines RISC-V task CPU state, process memory-layout constants, prefetch hooks, vector context flags, and thread startup interfaces.

Important APIs/types/functions: Key items are `struct thread_struct`, `INIT_THREAD`, `task_pt_regs()`, `KSTK_EIP`, `KSTK_ESP`, `TASK_UNMAPPED_BASE`, `STACK_TOP`, `user_max_virt_addr()`, prefetch helpers, `start_thread()`, `__get_wchan()`, and `wait_for_interrupt()`.

Control flow: Most logic is macro/inline: stack and mmap bounds derive from VA bits and compat state, `task_pt_regs()` locates saved registers at the top of the kernel stack, and optional prefetch emits Zicbop alternatives.

State and persistence: Per-task persistent state stores callee-saved GPRs, FPU/vector state, envcfg, SUM, bad cause, alignment control, and SMP icache-migration flags.

Dependencies and integration points: Used by scheduler, exec, ptrace, traps, vector/FPU context code, mmap, and arch thread lifecycle.

Risks: Struct layout feeds assembly offsets; wrong vector flags or stack calculations corrupt context switches or signal/ptrace state.

Test signals: Context-switch stress, exec/signal/ptrace tests, vector/FPU save-restore, mmap layout tests, SMP migration icache tests, and asm-offset rebuilds.

Source read size: 221 lines, 7460 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/ptrace.h

Purpose: Defines the kernel trap register frame and helper accessors used by RISC-V ptrace, syscall, tracing, profiling, and exception code.

Important APIs/types/functions: Important items are `struct pt_regs`, `user_mode()`, `instruction_pointer()`, `user_stack_pointer()`, `frame_pointer()`, `regs_return_value()`, `regs_set_return_value()`, `regs_get_register()`, `regs_get_kernel_argument()`, and `regs_irqs_disabled()`.

Control flow: Helpers read and write saved register fields directly. Register-offset validation prevents out-of-range inspection, and argument helpers expose a0-a7 for tracing.

State and persistence: `pt_regs` persists the architectural trap frame: EPC, integer registers, status, bad address, cause, and original syscall a0.

Dependencies and integration points: Consumed by entry.S, traps, syscall tracing, ftrace, kprobes/uprobes, perf, signal handling, and KVM offset generation.

Risks: Layout or status interpretation changes must match assembly and UAPI register ABI or debugging, signals, and syscall restart break.

Test signals: Ptrace regset tests, signal frame tests, syscall tracing/seccomp, ftrace/perf/kprobe tests, and asm-offset validation.

Source read size: 185 lines, 4416 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/runtime-const.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/runtime-const.h

Purpose: Provides RISC-V assembly helpers for runtime constants that can be patched into instruction streams after boot-time values are known.

Important APIs/types/functions: Defines macros around runtime-constant relocation records and assembler sequences for loading patched constants.

Control flow: Code emits placeholder instruction sequences and metadata that later patching code can rewrite with actual constant encodings.

State and persistence: State lives in generated runtime-constant sections and patched text rather than ordinary variables.

Dependencies and integration points: Integrates with alternative/text patching, linker sections, and assembly users that need efficient access to runtime-selected values.

Risks: Immediate encoding, relocation range, and patch ordering mistakes can create invalid instructions early in boot.

Test signals: Objdump inspection, boot on MMU modes with differing constants, alternatives selftests, and module/text patching builds.

Source read size: 272 lines, 8119 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/runtime-const.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/sbi.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/sbi.h

Purpose: Declares the Supervisor Binary Interface IDs, data structures, feature flags, and kernel call wrappers used to communicate with RISC-V firmware.

Important APIs/types/functions: Covers SBI extension/function enums for BASE, TIME, IPI, RFENCE, HSM, SRST, SUSP, PMU, DBCN, STA, NACL, FWFT, MPXY, DBTR, legacy v0.1 calls, `struct sbiret`, `sbi_ecall()`, extension probe/version helpers, hart suspend/start/status, rfence helpers, PMU snapshot/event structs, reset, debug console, firmware feature calls, and static-key state.

Control flow: Callers probe extensions, then issue `sbi_ecall()` with extension/function IDs and arguments. Header fallbacks compile to disabled/no-op behavior when SBI is not configured.

State and persistence: Persistent state includes probed SBI version/implementation IDs, extension availability, static keys, PMU shared-memory layout, and firmware-managed hart/timer/reset/debug state.

Dependencies and integration points: Integrates with early boot, timers, IPI, TLB shootdown, CPU hotplug/suspend, perf, console, reset, KVM, and alternatives that read vendor IDs via SBI.

Risks: SBI ABI constants are firmware contracts; wrong IDs or argument ordering can hang CPUs, lose TLB shootdowns, miscount PMU events, or reset the system unexpectedly.

Test signals: OpenSBI/QEMU boots, extension probe tests, SMP IPI/rfence, CPU hotplug/HSM, suspend/resume, PMU perf tests, DBCN console, and reset paths.

Source read size: 707 lines, 21334 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/sbi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/scs.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/scs.h

Purpose: Provides shadow-call-stack assembly macros for RISC-V task switch and entry code.

Important APIs/types/functions: Defines `scs_load_current`, `scs_save_current`, and no-op variants depending on `CONFIG_SHADOW_CALL_STACK`.

Control flow: When enabled, assembly loads/stores the per-task shadow call stack pointer from `thread_info`; otherwise macros assemble away.

State and persistence: Persists each task shadow-call-stack pointer in `thread_info.scs_sp`.

Dependencies and integration points: Depends on generated asm offsets and integrates with entry, switch_to, and compiler SCS instrumentation.

Risks: Wrong offset or missing save/restore corrupts return-address protection and can crash on context switch.

Test signals: SCS-enabled boot, context-switch stress, ftrace/interrupt nesting, and objdump checks for SCS macro expansion.

Source read size: 53 lines, 1090 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/scs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/seccomp.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/seccomp.h

Purpose: Connects RISC-V syscall numbering to the generic seccomp implementation.

Important APIs/types/functions: Includes `asm/unistd.h` and `asm-generic/seccomp.h`; it defines no custom filtering helpers.

Control flow: No runtime flow in this header; generic seccomp uses the architecture syscall ABI.

State and persistence: No state is stored here.

Dependencies and integration points: Used by seccomp, syscall tracing, and audit paths.

Risks: Risk is primarily include/ABI drift if syscall numbers or compat handling diverge from generic expectations.

Test signals: Seccomp filter selftests, syscall user-dispatch, audit, and compat syscall filtering on RV64.

Source read size: 20 lines, 504 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/seccomp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/sections.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/sections.h

Purpose: Declares RISC-V linker section symbols and text-address classification helpers.

Important APIs/types/functions: Exports `_start`, `_start_kernel`, init/exit/alternative section bounds, `is_va_kernel_text()`, and `is_va_kernel_lm_alias_text()`.

Control flow: Inline helpers compare virtual addresses against linker-symbol ranges for kernel text and linear-map aliases.

State and persistence: State is linker-defined section boundaries rather than mutable data.

Dependencies and integration points: Used by alternatives, ftrace/kprobes, text patching, memory permissions, and address sanitization helpers.

Risks: Incorrect bounds can permit patching/nonpatching wrong memory or misclassify kernel text aliases.

Test signals: Boot/link tests, kallsyms/ftrace/kprobe tests, module/text permission transitions, and vmlinux linker script changes.

Source read size: 34 lines, 883 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/sections.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/semihost.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/semihost.h

Purpose: Declares RISC-V semihosting support used for early debug/firmware-style host calls.

Important APIs/types/functions: Provides semihosting trap encoding constants and `semihosting_enabled()`/call declarations depending on config.

Control flow: Runtime code probes or checks enablement before issuing semihosting break sequences; disabled configs compile out.

State and persistence: No durable kernel state beyond semihosting enablement policy.

Dependencies and integration points: Integrates with early console/debug paths and trap handling.

Risks: Executing semihosting traps on unsupported systems can raise illegal-instruction or breakpoint exceptions.

Test signals: QEMU semihosting boot, disabled-config build, earlycon/debug output, and trap handling tests.

Source read size: 26 lines, 596 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/semihost.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/set_memory.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/set_memory.h

Purpose: Declares RISC-V runtime page-permission and direct-map attribute APIs.

Important APIs/types/functions: Includes `set_memory_ro/rw/x/nx/rw_nx()`, `set_kernel_memory()`, direct-map validity helpers, `kernel_page_present()`, `SECTION_ALIGN`, and PE/COFF alignment constants.

Control flow: Enabled MMU builds route permission changes to implementation code; non-MMU builds return success no-ops. `set_kernel_memory()` computes page ranges from start/end pointers.

State and persistence: Persistent effects are PTE permission changes for kernel text/modules/BPF/direct-map pages.

Dependencies and integration points: Used by module loader, alternatives/text patching, strict kernel RWX, hibernation, BPF JIT, and memory hotplug/debug code.

Risks: Incorrect permission transitions expose writable executable memory or make live code/data inaccessible.

Test signals: STRICT_KERNEL_RWX, module load/unload, BPF JIT, ftrace/kprobe patching, hibernation, and debug page-present checks.

Source read size: 63 lines, 2049 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/set_memory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/signal32.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/signal32.h

Purpose: Declares 32-bit compatibility signal-frame setup and restore hooks for RV64 compat tasks.

Important APIs/types/functions: Declares `compat_setup_rt_frame()` and `compat_sys_rt_sigreturn()` under compat support.

Control flow: Signal delivery code calls setup to build a 32-bit frame; sigreturn validates/restores it into kernel register state.

State and persistence: State is user-visible compat signal frame content and restored `pt_regs`/FPU/vector context.

Dependencies and integration points: Integrates with compat syscalls, signal.c, uapi sigcontext/ucontext, and ptrace register layout.

Risks: ABI mistakes break 32-bit processes or allow malformed signal frames to restore unsafe state.

Test signals: RV64 compat signal selftests, sigreturn fuzzing, ptrace/signal interaction, and altstack tests.

Source read size: 18 lines, 358 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/signal32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/simd.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/simd.h

Purpose: Provides the generic kernel SIMD gating API for RISC-V, mapped to vector-context availability.

Important APIs/types/functions: Defines `may_use_simd()`, `kernel_vector_begin()`, `kernel_vector_end()` integration, and interrupt/preemption checks.

Control flow: Callers test whether SIMD/vector use is safe, then bracket vector operations with begin/end.

State and persistence: State is per-task/vector context ownership and preemption/interrupt state.

Dependencies and integration points: Used by crypto/string routines that may use vector instructions and by vector context code.

Risks: Using vector state in unsafe contexts can corrupt user or kernel vector registers.

Test signals: Kernel-mode vector crypto/string tests, preemption/RT configs, interrupt nesting, and vector save/restore stress.

Source read size: 64 lines, 1772 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/simd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/smp.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/smp.h

Purpose: Declares RISC-V SMP CPU bring-up, IPI, hart ID, and remote operation interfaces.

Important APIs/types/functions: Key items include `cpuid_to_hartid_map()`, `riscv_hartid_to_cpuid()`, `arch_send_call_function_ipi_mask()`, `arch_send_call_function_single_ipi()`, `handle_IPI()`, `smp_callin()`, `riscv_ipi_set_virq_range()`, and SMP/non-SMP fallbacks.

Control flow: SMP code maps logical CPUs to hart IDs, sends IPIs through selected backends, and handles call-function/reschedule events; UP builds collapse to local-only helpers.

State and persistence: Persistent state includes hart ID mappings, possible CPU masks, and IPI virq allocation.

Dependencies and integration points: Integrates with SBI IPI, irqchip backends, CPU hotplug, scheduler, TLB shootdown, and ACPI/DT CPU discovery.

Risks: Bad hart mapping or IPI routing can hang secondary CPUs or miss reschedules/TLB flushes.

Test signals: SMP boot, CPU hotplug, scheduler IPI stress, TLB shootdown tests, ACPI and DT platforms, and UP build coverage.

Source read size: 117 lines, 2553 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/smp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/soc.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/soc.h

Purpose: Declares RISC-V SoC identification hooks used to attach vendor/platform-specific behavior.

Important APIs/types/functions: Defines `struct riscv_soc_id` matching data and `riscv_soc_init()`-style declarations.

Control flow: Platform code matches discovered SoC IDs against tables during boot and runs selected init hooks.

State and persistence: State is discovered SoC identity and any platform init side effects outside this header.

Dependencies and integration points: Integrates with DT/ACPI platform discovery, errata, cache, and vendor extension code.

Risks: Incorrect matching can apply errata or platform quirks to the wrong hardware.

Test signals: Boot on supported SoCs, DT/ACPI matching tests, and vendor errata enablement checks.

Source read size: 24 lines, 627 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/soc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/sparsemem.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/sparsemem.h

Purpose: Defines sparsemem geometry for RISC-V memory sections.

Important APIs/types/functions: Sets `MAX_PHYSMEM_BITS`/`SECTION_SIZE_BITS`-related constants through generic sparsemem expectations.

Control flow: No runtime flow; constants drive memory model sizing at build time.

State and persistence: Shapes persistent PFN-to-section and vmemmap layout.

Dependencies and integration points: Used by memory hotplug, vmemmap, page allocator, and sparsemem core.

Risks: Bad sizing loses addressable memory or bloats metadata.

Test signals: Sparsemem/vmemmap builds, high-memory boot, memory hotplug, and pfn_to_page/page_to_pfn tests.

Source read size: 15 lines, 331 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/sparsemem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/spinlock.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/spinlock.h

Purpose: Selects RISC-V queued spinlock and queued rwlock implementations.

Important APIs/types/functions: Includes qspinlock/qrwlock headers or generic lock definitions based on configuration.

Control flow: No custom flow here; locking operations are provided by included generic implementations.

State and persistence: Persistent state is lock word content owned by callers.

Dependencies and integration points: Used pervasively by kernel synchronization and depends on atomic instruction support.

Risks: Misconfigured lock implementation affects all SMP mutual exclusion.

Test signals: Locktorture, qspinlock/rwlock tests, SMP stress, PREEMPT_RT config builds, and atomic instruction emulation tests.

Source read size: 50 lines, 1302 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/spinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/stackprotector.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/stackprotector.h

Purpose: Defines architecture hook for stack canary initialization.

Important APIs/types/functions: Provides `boot_init_stack_canary()` as a no-op or architecture-specific bridge to generic stack protector setup.

Control flow: Called during early boot/task setup when stack protector is enabled.

State and persistence: State is per-task/global stack canary stored outside this header.

Dependencies and integration points: Integrates with compiler stack-protector instrumentation and `task_struct.stack_canary` offset generation.

Risks: Missing canary initialization weakens stack-smash detection or causes false positives.

Test signals: STACKPROTECTOR builds, boot, fork/exec, and stack protector fault injection.

Source read size: 22 lines, 589 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/stackprotector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/stacktrace.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/stacktrace.h

Purpose: Declares RISC-V stack walking data structures and helpers.

Important APIs/types/functions: Defines `struct stackframe`, `walk_stackframe()`, and unwind helper declarations.

Control flow: Callers seed frame pointer/return address and iterate frames through the architecture unwinder.

State and persistence: State is transient unwind cursor state plus stack contents produced by call frames.

Dependencies and integration points: Used by dump_stack, perf callchains, ftrace, livepatch-style checks, and debugging.

Risks: Bad frame validation can read invalid stacks or produce misleading traces.

Test signals: Stacktrace selftests, perf callchain, ftrace, exception-stack traces, and frame-pointer/non-frame-pointer builds.

Source read size: 29 lines, 774 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/stacktrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/string.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/string.h

Purpose: Declares RISC-V optimized string/memory routines and selects fortify behavior.

Important APIs/types/functions: Declares `memset`, `__memset`, `memcpy`, `__memcpy`, `memmove`, `__memmove`, `strcmp`, `strlen`, `strncmp`, `strnlen`, `strchr`, `strrchr`, and maps builtins depending on compiler/config.

Control flow: There is no inline algorithm here; calls dispatch to assembly/C implementations selected elsewhere.

State and persistence: No persistent state.

Dependencies and integration points: Used by the whole kernel, boot code, KASAN/fortify, and architecture string assembly.

Risks: Prototype or macro mismatch can bypass fortify or call unsafe overlapping copy implementations.

Test signals: LKDTM/fortify tests, KUnit string tests, boot with optimized routines, KASAN, and compiler matrix builds.

Source read size: 53 lines, 1690 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/suspend.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/suspend.h

Purpose: Declares CPU suspend, hibernation, and SBI HSM suspend interfaces for RISC-V.

Important APIs/types/functions: Defines `struct suspend_context`, `cpu_suspend()`, `__cpu_suspend_enter()`, resume entry points, CSR save/restore, hibernation image restore functions, and SBI suspend helpers.

Control flow: Suspend saves GPR/CSR context, calls a platform finisher, and resumes through low-level restore paths; hibernation uses separate image restore entry points.

State and persistence: Persistent suspend state includes saved callee registers, status/ie/tvec/scratch/envcfg CSRs, hibernation page backup entries, and `in_suspend`.

Dependencies and integration points: Integrates with SBI HSM/SUSP, PM core, hibernate assembly, CPU hotplug, and CSR definitions.

Risks: Incomplete CSR/register save or invalid non-retentive suspend handling corrupts resumed kernels.

Test signals: s2idle/system suspend, hibernation, CPU hotplug around suspend, SBI HSM platforms, and resume path fault injection.

Source read size: 65 lines, 1929 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/suspend.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/swab.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/swab.h

Purpose: Provides RISC-V byte-swap helpers, using Zbb `rev8` alternatives when available.

Important APIs/types/functions: Defines `__arch_swab32()` and `__arch_swab64()` or falls back to generic swab based on XLEN and extension support.

Control flow: Inline assembly emits generic shifts or alternative-patched `rev8` sequences for efficient byteswapping.

State and persistence: No persistent state.

Dependencies and integration points: Used by endian conversion, networking, filesystems, crypto, and depends on alternatives/Zbb detection.

Risks: Wrong instruction selection or 32-bit truncation breaks endian-sensitive data structures.

Test signals: Endian conversion KUnit, networking/filesystem checksums, Zbb and non-Zbb boot, RV32/RV64 builds, and objdump inspection.

Source read size: 87 lines, 2626 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/swab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/switch_to.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/switch_to.h

Purpose: Defines RISC-V task context switching hooks for GPR, FPU, vector, envcfg, shadow call stack, and user CFI state.

Important APIs/types/functions: Key APIs are `__switch_to()`, `switch_to()`, `__switch_to_aux()`, `fstate_save()/restore()`, `riscv_v_vstate_save/restore()` integration, and per-task CSR helpers.

Control flow: The scheduler saves current extended state, switches callee-saved GPRs in assembly, restores next task extended/CSR state, and updates shadow-call-stack/user-CFI state when enabled.

State and persistence: Persistent state is `thread_struct` register/FPU/vector/envcfg/SUM/user-CFI/SCS content.

Dependencies and integration points: Integrates with scheduler, entry assembly, FPU/vector code, asm offsets, SCS, and user CFI.

Risks: Context switch bugs corrupt registers across tasks or leak FPU/vector/CFI state.

Test signals: Scheduler stress, FPU/vector context tests, user CFI tests, SCS builds, preemption, and SMP migration.

Source read size: 128 lines, 3400 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/switch_to.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/sync_core.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/sync_core.h

Purpose: Provides instruction-stream/core synchronization helpers after text modification.

Important APIs/types/functions: Defines `sync_core()` and related architecture hooks using `fence.i`/instruction synchronization.

Control flow: Callers invoke synchronization after code patching so subsequent execution observes modified instructions.

State and persistence: No durable state; effect is hardware ordering of instruction fetch.

Dependencies and integration points: Used by alternatives, ftrace, kprobes, jump labels, BPF JIT, and module patching.

Risks: Missing synchronization can execute stale instructions after patching.

Test signals: Dynamic ftrace, kprobe, jump-label, BPF JIT, module load, and multi-core patching tests.

Source read size: 29 lines, 689 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/sync_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/syscall.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/syscall.h

Purpose: Defines RISC-V syscall inspection and mutation helpers for tracing, seccomp, audit, and syscall restart.

Important APIs/types/functions: Includes `syscall_get_nr()`, `syscall_rollback()`, `syscall_get_error()`, `syscall_get_return_value()`, `syscall_set_return_value()`, `syscall_get_arguments()`, `syscall_set_arguments()`, and syscall work hooks.

Control flow: Helpers interpret `pt_regs.a7` as syscall number, `a0-a5` as arguments, and `orig_a0` for restart/rollback behavior.

State and persistence: State is the live `pt_regs` syscall frame.

Dependencies and integration points: Used by entry syscall path, ptrace, seccomp, audit, tracepoints, and restart logic.

Risks: Wrong argument ordering or error detection breaks tracing and seccomp decisions.

Test signals: strace/ptrace tests, seccomp selftests, syscall restart tests, audit, and compat syscall tests.

Source read size: 124 lines, 2924 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/syscall_table.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/syscall_table.h

Purpose: Declares the RISC-V syscall table symbol consumed by entry/syscall dispatch code.

Important APIs/types/functions: Exports `sys_call_table[]` as an array of syscall handler pointers.

Control flow: No runtime flow in the header; assembly/C syscall entry indexes this table by syscall number.

State and persistence: Table contents are generated/linked elsewhere and persist for kernel lifetime.

Dependencies and integration points: Integrates with syscall table generation, unistd numbers, compat table support, and entry.S.

Risks: Table type or number mismatch dispatches the wrong syscall.

Test signals: Syscall ABI selftests, generated table build checks, seccomp/audit, and compat syscall matrix.

Source read size: 7 lines, 137 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/syscall_table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/syscall_wrapper.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/syscall_wrapper.h

Purpose: Provides RISC-V syscall wrapper macros that adapt generic syscall declarations to pt_regs-based entry calling conventions.

Important APIs/types/functions: Defines `SC_RISCV_REGS_TO_ARGS`, `__SYSCALL_DEFINEx`, `__ARCH_WANT_SYS_*` wrapper behavior, and compat wrapper variants.

Control flow: Macros generate wrapper functions that extract arguments from `pt_regs` registers and call the typed syscall implementation.

State and persistence: No persistent state; wrappers operate on each syscall frame.

Dependencies and integration points: Used by syscall definition expansion, trace metadata, compat syscalls, and generated syscall tables.

Risks: Argument extraction errors produce ABI-visible syscall corruption, especially for 64-bit arguments and compat calls.

Test signals: Syscall selftests, compat syscall tests, tracing metadata builds, and generated wrapper compile checks.

Source read size: 108 lines, 4052 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/syscall_wrapper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/text-patching.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/text-patching.h

Purpose: Declares low-level RISC-V text patching APIs.

Important APIs/types/functions: Includes `patch_text_nosync()`, `patch_text_set_nosync()`, `patch_text()`, and related patch helpers.

Control flow: Callers write replacement instructions and then synchronize instruction execution when using the syncing API.

State and persistence: Persistent effect is modified kernel/module/vDSO text.

Dependencies and integration points: Used by alternatives, jump labels, ftrace, kprobes, BPF, and errata patching.

Risks: Incorrect patch size/alignment or missing sync can corrupt executable text.

Test signals: Alternatives boot, ftrace/jump-label/kprobe tests, module patching, and W^X permission tests.

Source read size: 16 lines, 449 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/text-patching.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/thread_info.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/thread_info.h

Purpose: Defines RISC-V low-level thread metadata, flags, and stack layout used by entry assembly and scheduler code.

Important APIs/types/functions: Key items are `struct thread_info`, `INIT_THREAD_INFO`, `THREAD_SIZE`, `THREAD_SHIFT`, `TIF_*` flags, syscall-work masks, and current-thread helpers.

Control flow: Entry/scheduler code reads flags to decide reschedule, signal, syscall tracing, vector restore, uaccess, and CFI work.

State and persistence: Per-task persistent state includes CPU number, preempt count, kernel/user stack pointers, syscall flags, optional SCS pointer, and user CFI state.

Dependencies and integration points: Integrates with entry.S, scheduler, signal, ptrace/seccomp, vector, SCS, and asm-offset generation.

Risks: Flag or layout drift breaks assembly entry decisions and can miss reschedules/signals or corrupt stacks.

Test signals: Boot, preemption/signal/syscall tracing, SCS/user CFI/vector configs, and asm-offset validation.

Source read size: 127 lines, 3524 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/thread_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/timex.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/timex.h

Purpose: Defines RISC-V cycle counter access and clocksource-related time helpers.

Important APIs/types/functions: Provides `get_cycles()`, `get_cycles64()`, `random_get_entropy()`, `get_cycles_snapshot()`, and time CSR reading helpers including RV32 high/low sequencing.

Control flow: RV64 reads `cycle` directly; RV32 loops reading high/low/high until stable to avoid rollover races.

State and persistence: No kernel state in the header; values reflect hardware counters.

Dependencies and integration points: Used by scheduler clock, random entropy, delay/timers, vDSO, and perf.

Risks: Incorrect RV32 rollover handling or unavailable counters can return non-monotonic time.

Test signals: Timekeeping selftests, RV32/RV64 builds, counter access under virtualization, vDSO clock tests, and perf counter tests.

Source read size: 91 lines, 1829 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/timex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/tlb.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/tlb.h

Purpose: Adapts generic Linux TLB gather/mmu_gather behavior to RISC-V.

Important APIs/types/functions: Defines `tlb_flush()` integration and includes generic TLB helpers with RISC-V flush hooks.

Control flow: During unmap/free, generic MM gathers ranges and calls RISC-V flush functions before freeing page tables.

State and persistence: State is transient `mmu_gather` range/batch state.

Dependencies and integration points: Used by memory unmap, page-table freeing, THP split/collapse, and `tlbflush.h` implementations.

Risks: Incorrect batching can free page tables before remote CPUs stop using stale translations.

Test signals: munmap/mprotect stress, THP split, swap reclaim, SMP TLB shootdown, and mmu_gather debug.

Source read size: 27 lines, 582 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/tlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/tlbbatch.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/tlbbatch.h

Purpose: Defines RISC-V architecture-specific TLB unmap batch state.

Important APIs/types/functions: Defines `struct arch_tlbflush_unmap_batch` with CPU mask/range fields used by deferred flush support.

Control flow: MM code records CPUs/ranges in the batch and flushes them together through `arch_tlbbatch_flush()`.

State and persistence: Transient batch cpumask/range state attached to unmap operations.

Dependencies and integration points: Works with `tlbflush.h`, MM unmap batching, ASID/mm context, and SMP IPI flush code.

Risks: Lost CPU bits or stale ranges cause use-after-free through stale TLB entries.

Test signals: TLB batching stress, reclaim, munmap on SMP, KCSAN/lockdep, and ASID rollover tests.

Source read size: 15 lines, 273 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/tlbbatch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/tlbflush.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/tlbflush.h

Purpose: Declares and inlines local and remote RISC-V TLB flush operations.

Important APIs/types/functions: Key APIs are `local_flush_tlb_all()`, `local_flush_tlb_all_asid()`, `local_flush_tlb_page()`, `local_flush_tlb_page_asid()`, `flush_tlb_all()`, `flush_tlb_mm_range()`, `flush_tlb_page()`, `flush_tlb_kernel_range()`, hugepage range flushes, and tlbbatch hooks.

Control flow: Local helpers emit `sfence.vma` variants, optionally through errata wrappers; SMP implementations perform remote shootdowns and range/all selection.

State and persistence: No durable state here except `tlb_flush_all_threshold`; hardware TLBs are the target state.

Dependencies and integration points: Used by page-table updates, vmalloc, ioremap, ASID management, SBI/irq IPI backends, and errata code.

Risks: Under-flushing causes stale translations and memory corruption; over-flushing hurts performance.

Test signals: SMP shootdown tests, ASID rollover, mprotect/munmap, vmalloc/ioremap, THP, and errata-platform boot.

Source read size: 73 lines, 2245 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/tlbflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/topology.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/topology.h

Purpose: Connects RISC-V CPU topology to generic Linux topology and optional NUMA scheduling data.

Important APIs/types/functions: Defines topology macros and includes generic topology defaults, with NUMA/cpumask integration when enabled.

Control flow: No direct runtime flow; generic scheduler/topology code consumes the macros and per-CPU data.

State and persistence: Persistent topology state is maintained by generic CPU/NUMA code.

Dependencies and integration points: Used by scheduler domains, sysfs topology, ACPI/DT CPU discovery, and NUMA setup.

Risks: Incorrect topology reporting harms scheduling placement and hotplug behavior.

Test signals: Topology sysfs, lscpu validation, NUMA scheduling, CPU hotplug, ACPI and DT boots.

Source read size: 26 lines, 822 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/topology.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/trace.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/trace.h

Purpose: Defines RISC-V trace helpers/events for architecture-specific tracing.

Important APIs/types/functions: Contains tracepoint declarations/macros for arch events and includes tracepoint plumbing.

Control flow: Trace callsites emit events when enabled; disabled tracepoints compile to static branches/no-ops.

State and persistence: State is tracepoint enablement and ring-buffer data outside this header.

Dependencies and integration points: Integrates with ftrace/perf/tracefs and architecture callsites.

Risks: Trace ABI field changes can break tooling; tracing in sensitive paths must preserve registers and timing.

Test signals: tracefs event enablement, perf record, ftrace, and build checks with tracing disabled/enabled.

Source read size: 54 lines, 1054 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/uaccess.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/uaccess.h

Purpose: Defines RISC-V architecture interfaces for `uaccess.h`.

Important APIs/types/functions: The file is a small architecture header whose exported macros/types are consumed by nearby RISC-V kernel code.

Control flow: Control flow is compile-time or inline only, with runtime behavior provided by implementation files.

State and persistence: No substantial private state is stored in this header.

Dependencies and integration points: Integrates with the surrounding RISC-V architecture subsystem and generic Linux kernel APIs.

Risks: The main risk is ABI or include-contract drift with its implementation users.

Test signals: Architecture build coverage and subsystem-specific runtime tests.

Source read size: 493 lines, 14710 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/uaccess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/unistd.h

Purpose: Defines kernel-side RISC-V syscall numbering policy and generic syscall feature selections.

Important APIs/types/functions: Sets `__ARCH_WANT_*` feature macros, includes UAPI `asm/unistd.h`, and exposes `NR_syscalls` for kernel code.

Control flow: No runtime flow; generated syscall tables and wrappers use these constants.

State and persistence: No mutable state; syscall numbers are ABI state.

Dependencies and integration points: Used by syscall table generation, seccomp, audit, and compat logic.

Risks: Changing feature macros or counts changes syscall ABI/dispatch.

Test signals: Syscall table generation, libc smoke tests, seccomp, strace, and compat builds.

Source read size: 29 lines, 719 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/uprobes.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/uprobes.h

Purpose: Defines RISC-V uprobes breakpoint instruction properties and arch hooks.

Important APIs/types/functions: Declares `uprobe_opcode_t`, breakpoint opcode constants, `arch_uprobe` fields, and uprobe analysis/emulation entry points.

Control flow: Uprobe code copies/analyzes an instruction, plants a breakpoint, single-steps or emulates, then resumes user execution.

State and persistence: Persistent uprobe state includes original instruction bytes, slot metadata, and per-task probe context held by generic uprobes.

Dependencies and integration points: Integrates with instruction decoding, ptrace, traps, perf uprobes, and user memory access.

Risks: Compressed instruction length and PC-relative emulation mistakes can corrupt user execution.

Test signals: Perf uprobes, uprobes selftests, compressed/non-compressed instruction probes, signal interaction, and multi-threaded probes.

Source read size: 51 lines, 1065 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/uprobes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/usercfi.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/usercfi.h

Purpose: Declares user-mode control-flow-integrity state, especially shadow-stack support, for RISC-V.

Important APIs/types/functions: Defines `struct user_cfi_state`, shadow-stack flags/helpers, syscall/prctl hooks, signal helpers, and no-op fallbacks when disabled.

Control flow: Enabled builds save/restore user shadow-stack pointers across context switch, signal delivery, exec, and prctl/syscall operations.

State and persistence: Per-thread persistent state includes user shadow-stack pointer and CFI enablement flags in `thread_info`/task state.

Dependencies and integration points: Integrates with Zicfiss/FWFT support, signal frames, switch_to, ptrace/prctl, and memory permissions for shadow stacks.

Risks: Bad state transitions can weaken CFI or make user tasks unrecoverably fault on return.

Test signals: User CFI/shadow-stack selftests, signal/altstack, exec/fork/clone, ptrace, and SBI FWFT feature tests.

Source read size: 97 lines, 3102 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/usercfi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso.h

Purpose: Declares RISC-V vDSO image symbols, data page layout hooks, and mapping helpers.

Important APIs/types/functions: Exports vDSO start/end symbols, `vdso_data`, `riscv_vdso_*` declarations, and vDSO install/setup helpers.

Control flow: Architecture setup maps vDSO pages into user processes and updates shared data used by user-space fast paths.

State and persistence: Persistent state includes vDSO text image, shared vvar/vdso data, and per-mm mappings.

Dependencies and integration points: Integrates with timekeeping, signal return trampolines, ELF auxv, alternatives, and compat vDSO.

Risks: Mapping or data layout mismatches break user-space time/syscall helper ABI.

Test signals: vDSO selftests, clock_gettime/getcpu/getrandom tests, ASLR/mmap inspection, compat vDSO, and alternatives applied to vDSO.

Source read size: 52 lines, 1378 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso/arch_data.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso/arch_data.h

Purpose: Defines RISC-V architecture-specific data embedded in vDSO data pages.

Important APIs/types/functions: Provides arch data structures/fields consumed by vDSO code.

Control flow: Kernel updates data, vDSO reads it locklessly with generic vDSO sequencing.

State and persistence: Persistent shared vvar data visible to user space.

Dependencies and integration points: Used by vDSO gettimeofday/getrandom/processor helpers and generic vDSO data definitions.

Risks: Layout changes are user ABI sensitive for the vDSO image.

Test signals: vDSO ABI/selftests and clock/getrandom correctness tests.

Source read size: 23 lines, 638 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso/arch_data.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso/clocksource.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso/clocksource.h

Purpose: Selects the RISC-V vDSO clocksource interface.

Important APIs/types/functions: Includes generic vDSO clocksource definitions with RISC-V cycle counter support.

Control flow: vDSO reads the time CSR/cycle source through generic helper paths.

State and persistence: No standalone state; uses vvar clock data.

Dependencies and integration points: Timekeeping, timex counter access, and generic vDSO clock mode code.

Risks: Wrong clock mode exposes non-monotonic vDSO time.

Test signals: vDSO clock_gettime selftests and counter virtualization tests.

Source read size: 8 lines, 169 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso/clocksource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso/getrandom.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso/getrandom.h

Purpose: Provides RISC-V vDSO getrandom architecture hooks.

Important APIs/types/functions: Defines arch-specific getrandom state sizes, opaque data hooks, and syscall fallback integration.

Control flow: vDSO getrandom uses shared random state when available and falls back to the syscall on slow/error paths.

State and persistence: Shared vDSO random state and per-call buffer/counter state.

Dependencies and integration points: Generic vDSO getrandom, random subsystem, syscall ABI, and vvar mapping.

Risks: ABI/layout mistakes can return weak random data or break fallback.

Test signals: vDSO getrandom selftests, fork/thread races, and fallback syscall tests.

Source read size: 30 lines, 752 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso/getrandom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso/gettimeofday.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso/gettimeofday.h

Purpose: Implements RISC-V vDSO time read helpers around the hardware time CSR.

Important APIs/types/functions: Defines `__arch_get_hw_counter()`, `gettimeofday` helper macros, and clock-mode validation for vDSO.

Control flow: User-space vDSO code reads the cycle/time CSR and combines it with vvar timekeeper data under the generic sequence protocol.

State and persistence: No mutable private state; reads shared vvar data and hardware counters.

Dependencies and integration points: Depends on `timex.h`, generic vDSO timekeeping, and kernel-updated vvar pages.

Risks: Counter access traps or non-monotonic frequency data break user-space clocks.

Test signals: vDSO clock_gettime/gettimeofday tests, time namespace tests, virtualization, and RV32 counter rollover coverage.

Source read size: 84 lines, 2144 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso/gettimeofday.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso/processor.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso/processor.h

Purpose: Defines RISC-V task CPU state, process memory-layout constants, prefetch hooks, vector context flags, and thread startup interfaces.

Important APIs/types/functions: Key items are `struct thread_struct`, `INIT_THREAD`, `task_pt_regs()`, `KSTK_EIP`, `KSTK_ESP`, `TASK_UNMAPPED_BASE`, `STACK_TOP`, `user_max_virt_addr()`, prefetch helpers, `start_thread()`, `__get_wchan()`, and `wait_for_interrupt()`.

Control flow: Most logic is macro/inline: stack and mmap bounds derive from VA bits and compat state, `task_pt_regs()` locates saved registers at the top of the kernel stack, and optional prefetch emits Zicbop alternatives.

State and persistence: Per-task persistent state stores callee-saved GPRs, FPU/vector state, envcfg, SUM, bad cause, alignment control, and SMP icache-migration flags.

Dependencies and integration points: Used by scheduler, exec, ptrace, traps, vector/FPU context code, mmap, and arch thread lifecycle.

Risks: Struct layout feeds assembly offsets; wrong vector flags or stack calculations corrupt context switches or signal/ptrace state.

Test signals: Context-switch stress, exec/signal/ptrace tests, vector/FPU save-restore, mmap layout tests, SMP migration icache tests, and asm-offset rebuilds.

Source read size: 29 lines, 592 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso/vsyscall.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso/vsyscall.h

Purpose: Declares kernel-to-vDSO vsyscall update hooks for RISC-V.

Important APIs/types/functions: Provides arch hooks used by generic vDSO data update code.

Control flow: Kernel timekeeping invokes hooks to update shared vvar/vsyscall data.

State and persistence: Shared vDSO data pages.

Dependencies and integration points: Generic vDSO, timekeeping, and vvar mapping.

Risks: Wrong update hooks produce stale or inconsistent vDSO results.

Test signals: vDSO clock tests and timekeeping update stress.

Source read size: 14 lines, 333 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vdso/vsyscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vector.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/vector.h

Purpose: Implements RISC-V vector extension state management interfaces for user and kernel mode, including standard V and T-Head vector variants.

Important APIs/types/functions: Key APIs are `has_vector()`, `has_xtheadvector()`, `riscv_v_enable()/disable()`, `riscv_v_vstate_save()/restore()/discard()`, `__switch_to_vector()`, kernel vector begin/end declarations, first-use handling, vector context allocation/free, and preemptible vector flags.

Control flow: Code tests extension availability, toggles VS bits, saves/restores vector CSRs and 32 vector registers, handles T-Head CSR differences, lazily restores user vector state, and saves preemptible kernel vector context on switch/trap boundaries.

State and persistence: Persistent state includes per-task `vstate`, `kernel_vstate`, vector flags, allocated vector data buffers, and global `riscv_v_vsize`.

Dependencies and integration points: Integrates with scheduler, traps, signal/ptrace regsets, cpufeature, vendor extensions, CSR helpers, and kernel SIMD users.

Risks: Vector context is large and security-sensitive; missed dirty/save transitions leak data or corrupt user/kernel vector registers, especially with preemptible vector and T-Head differences.

Test signals: Vector user ABI tests, signal/ptrace vector regsets, context-switch stress, kernel-mode vector tests, preempt/RT configs, T-Head vector hardware, and first-use fault tests.

Source read size: 444 lines, 12314 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions.h

Purpose: Defines the framework for RISC-V vendor-specific ISA extension discovery and lookup.

Important APIs/types/functions: Includes `struct riscv_isa_vendor_ext_data_list`, vendor bitmap helpers, vendor extension availability checks, and extern lists for Andes, MIPS, SiFive, and T-Head.

Control flow: Boot/vendor code populates per-vendor extension bitmaps; feature checks query by vendor ID and extension number.

State and persistence: Persistent state is per-vendor/per-CPU extension bitmaps and vendor extension data lists.

Dependencies and integration points: Used by cpufeature, hwprobe, vector/errata code, and vendor extension implementation files.

Risks: Vendor ID or bit assignment errors expose unsupported instructions or hide required errata.

Test signals: Vendor extension parsing, hwprobe vendor keys, boot on vendor CPUs, and fallback builds without vendor configs.

Source read size: 104 lines, 3247 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions/andes.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions/andes.h

Purpose: Declares `andes` vendor-specific RISC-V extension IDs and extension list metadata.

Important APIs/types/functions: Provides enum/define values for vendor extension bit numbers and extern data-list declarations.

Control flow: No runtime flow; boot cpufeature code consumes the list when parsing ISA/vendor strings or probing hardware.

State and persistence: Persistent state is vendor extension bitmap entries allocated according to these IDs.

Dependencies and integration points: Used by `vendor_extensions.h`, cpufeature parsing, hwprobe vendor reporting, and any vendor errata/feature users.

Risks: Renumbering extension IDs breaks bitmap interpretation and userspace hwprobe mapping.

Test signals: Vendor ISA parsing, hwprobe vendor tests, and builds with each vendor extension config enabled/disabled.

Source read size: 19 lines, 473 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions/andes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions/mips.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions/mips.h

Purpose: Declares `mips` vendor-specific RISC-V extension IDs and extension list metadata.

Important APIs/types/functions: Provides enum/define values for vendor extension bit numbers and extern data-list declarations.

Control flow: No runtime flow; boot cpufeature code consumes the list when parsing ISA/vendor strings or probing hardware.

State and persistence: Persistent state is vendor extension bitmap entries allocated according to these IDs.

Dependencies and integration points: Used by `vendor_extensions.h`, cpufeature parsing, hwprobe vendor reporting, and any vendor errata/feature users.

Risks: Renumbering extension IDs breaks bitmap interpretation and userspace hwprobe mapping.

Test signals: Vendor ISA parsing, hwprobe vendor tests, and builds with each vendor extension config enabled/disabled.

Source read size: 37 lines, 1133 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions/mips.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions/mips_hwprobe.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions/mips_hwprobe.h

Purpose: Declares hwprobe glue for RISC-V vendor extension reporting in `mips_hwprobe.h`.

Important APIs/types/functions: Defines vendor hwprobe key/bit mapping declarations and helper prototypes used by `sys_hwprobe.c`.

Control flow: The hwprobe syscall asks vendor-specific code to translate kernel extension bitmaps into UAPI bit masks.

State and persistence: State is read from vendor extension bitmaps and exposed as syscall output.

Dependencies and integration points: Integrates with `uapi/asm/hwprobe.h`, `vendor_extensions.h`, and vendor extension lists.

Risks: Incorrect mapping exposes unstable or wrong userspace capability bits.

Test signals: hwprobe selftests for vendor keys, unsupported vendor fallback, and vendor hardware/QEMU coverage.

Source read size: 22 lines, 580 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions/mips_hwprobe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions/sifive.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions/sifive.h

Purpose: Declares `sifive` vendor-specific RISC-V extension IDs and extension list metadata.

Important APIs/types/functions: Provides enum/define values for vendor extension bit numbers and extern data-list declarations.

Control flow: No runtime flow; boot cpufeature code consumes the list when parsing ISA/vendor strings or probing hardware.

State and persistence: Persistent state is vendor extension bitmap entries allocated according to these IDs.

Dependencies and integration points: Used by `vendor_extensions.h`, cpufeature parsing, hwprobe vendor reporting, and any vendor errata/feature users.

Risks: Renumbering extension IDs breaks bitmap interpretation and userspace hwprobe mapping.

Test signals: Vendor ISA parsing, hwprobe vendor tests, and builds with each vendor extension config enabled/disabled.

Source read size: 16 lines, 466 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions/sifive.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions/sifive_hwprobe.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions/sifive_hwprobe.h

Purpose: Declares hwprobe glue for RISC-V vendor extension reporting in `sifive_hwprobe.h`.

Important APIs/types/functions: Defines vendor hwprobe key/bit mapping declarations and helper prototypes used by `sys_hwprobe.c`.

Control flow: The hwprobe syscall asks vendor-specific code to translate kernel extension bitmaps into UAPI bit masks.

State and persistence: State is read from vendor extension bitmaps and exposed as syscall output.

Dependencies and integration points: Integrates with `uapi/asm/hwprobe.h`, `vendor_extensions.h`, and vendor extension lists.

Risks: Incorrect mapping exposes unstable or wrong userspace capability bits.

Test signals: hwprobe selftests for vendor keys, unsupported vendor fallback, and vendor hardware/QEMU coverage.

Source read size: 19 lines, 502 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions/sifive_hwprobe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions/thead.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions/thead.h

Purpose: Declares `thead` vendor-specific RISC-V extension IDs and extension list metadata.

Important APIs/types/functions: Provides enum/define values for vendor extension bit numbers and extern data-list declarations.

Control flow: No runtime flow; boot cpufeature code consumes the list when parsing ISA/vendor strings or probing hardware.

State and persistence: Persistent state is vendor extension bitmap entries allocated according to these IDs.

Dependencies and integration points: Used by `vendor_extensions.h`, cpufeature parsing, hwprobe vendor reporting, and any vendor errata/feature users.

Risks: Renumbering extension IDs breaks bitmap interpretation and userspace hwprobe mapping.

Test signals: Vendor ISA parsing, hwprobe vendor tests, and builds with each vendor extension config enabled/disabled.

Source read size: 47 lines, 1554 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions/thead.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions/thead_hwprobe.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions/thead_hwprobe.h

Purpose: Declares hwprobe glue for RISC-V vendor extension reporting in `thead_hwprobe.h`.

Important APIs/types/functions: Defines vendor hwprobe key/bit mapping declarations and helper prototypes used by `sys_hwprobe.c`.

Control flow: The hwprobe syscall asks vendor-specific code to translate kernel extension bitmaps into UAPI bit masks.

State and persistence: State is read from vendor extension bitmaps and exposed as syscall output.

Dependencies and integration points: Integrates with `uapi/asm/hwprobe.h`, `vendor_extensions.h`, and vendor extension lists.

Risks: Incorrect mapping exposes unstable or wrong userspace capability bits.

Test signals: hwprobe selftests for vendor keys, unsupported vendor fallback, and vendor hardware/QEMU coverage.

Source read size: 19 lines, 496 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions/thead_hwprobe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions/vendor_hwprobe.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions/vendor_hwprobe.h

Purpose: Declares hwprobe glue for RISC-V vendor extension reporting in `vendor_hwprobe.h`.

Important APIs/types/functions: Defines vendor hwprobe key/bit mapping declarations and helper prototypes used by `sys_hwprobe.c`.

Control flow: The hwprobe syscall asks vendor-specific code to translate kernel extension bitmaps into UAPI bit masks.

State and persistence: State is read from vendor extension bitmaps and exposed as syscall output.

Dependencies and integration points: Integrates with `uapi/asm/hwprobe.h`, `vendor_extensions.h`, and vendor extension lists.

Risks: Incorrect mapping exposes unstable or wrong userspace capability bits.

Test signals: hwprobe selftests for vendor keys, unsupported vendor fallback, and vendor hardware/QEMU coverage.

Source read size: 37 lines, 1114 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendor_extensions/vendor_hwprobe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendorid_list.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendorid_list.h

Purpose: Centralizes numeric RISC-V vendor IDs used by errata and vendor extension code.

Important APIs/types/functions: Defines `ANDES_VENDOR_ID`, `MICROCHIP_VENDOR_ID`, `MIPS_VENDOR_ID`, `SIFIVE_VENDOR_ID`, and `THEAD_VENDOR_ID`.

Control flow: No runtime flow; code compares hardware/SBI vendor IDs against these constants.

State and persistence: No mutable state; constants are hardware identity contracts.

Dependencies and integration points: Used by alternatives, errata, vendor extensions, vector T-Head support, and hwprobe.

Risks: Wrong IDs apply vendor logic to the wrong CPU family.

Test signals: Boot on vendor systems, errata selection tests, and cpufeature/hwprobe validation.

Source read size: 14 lines, 298 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vendorid_list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vermagic.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/vermagic.h

Purpose: Adds RISC-V architecture-specific module version-magic text.

Important APIs/types/functions: Defines `MODULE_ARCH_VERMAGIC` from ISA string/build configuration.

Control flow: Module loader compares vermagic strings when loading modules.

State and persistence: State is compiled into module metadata.

Dependencies and integration points: Used by module build/load infrastructure and RISC-V ISA config.

Risks: Too-broad vermagic can load incompatible modules; too-narrow strings reject valid modules.

Test signals: Module build/load across ISA configs and modinfo/vermagic checks.

Source read size: 9 lines, 213 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vermagic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vmalloc.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/vmalloc.h

Purpose: Declares RISC-V vmalloc huge mapping capabilities and ioremap maximum order.

Important APIs/types/functions: Defines `IOREMAP_MAX_ORDER`, `arch_vmap_pud_supported()`, and `arch_vmap_pmd_supported()`.

Control flow: vmap/ioremap code asks whether PUD/PMD huge mappings are supported for a protection; helpers reflect current page-table level enablement.

State and persistence: Reads global `pgtable_l4_enabled`/`pgtable_l5_enabled`; no private state.

Dependencies and integration points: Used by vmalloc, ioremap, module/BPF mappings, and page-table geometry.

Risks: Returning support for folded/unavailable levels can create invalid vmalloc mappings.

Test signals: vmalloc/ioremap huge mapping tests, Sv39/Sv48/Sv57 boots, and debug page-table checks.

Source read size: 25 lines, 574 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/vmalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/word-at-a-time.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/word-at-a-time.h

Purpose: Implements word-at-a-time byte scanning primitives for RISC-V string operations.

Important APIs/types/functions: Defines `WORD_AT_A_TIME_CONSTANTS`, `has_zero()`, `prep_zero_mask()`, `create_zero_mask()`, `find_zero()`, and related zero-byte helpers.

Control flow: String routines load machine words and use arithmetic/bit operations to detect zero bytes efficiently.

State and persistence: No persistent state.

Dependencies and integration points: Used by generic string helpers such as strlen/strnlen and user string routines.

Risks: Endian or word-size mistakes produce overreads or wrong string lengths.

Test signals: KUnit string tests, endian/word-size builds, KASAN/UBSAN, and user string boundary tests.

Source read size: 76 lines, 1766 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/word-at-a-time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/Kbuild

Purpose: Lists RISC-V UAPI headers exported or generated for userspace.

Important APIs/types/functions: Uses Kbuild `generic-y`/`generated-y` style declarations.

Control flow: Header installation tooling reads this file during `headers_install`.

State and persistence: No runtime state.

Dependencies and integration points: Integrates with kernel UAPI header export and libc/toolchain builds.

Risks: Missing entries hide required ABI headers from userspace.

Test signals: `make headers_install`, libc build smoke tests, and UAPI header checks.

Source read size: 3 lines, 85 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/auxvec.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/auxvec.h

Purpose: Defines RISC-V ELF auxiliary vector constants for userspace capability discovery.

Important APIs/types/functions: Defines `AT_SYSINFO_EHDR`, cache geometry auxvec keys, and RISC-V-specific entries such as hardware capability exposure.

Control flow: ELF loader populates auxvec entries at exec; userspace reads them through libc/getauxval.

State and persistence: Auxvec values are per-process exec-time ABI state.

Dependencies and integration points: Used by ELF loader, vDSO setup, libc, dynamic linkers, and hwcap code.

Risks: Changing numbers breaks userspace ABI.

Test signals: getauxval tests, vDSO mapping checks, dynamic linker smoke tests, and cache/hwcap reporting.

Source read size: 40 lines, 1232 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/auxvec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/bitsperlong.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/bitsperlong.h

Purpose: Defines UAPI word-size selection for RISC-V user headers.

Important APIs/types/functions: Sets `__BITS_PER_LONG` based on ABI and includes generic bitsperlong.

Control flow: No runtime flow; compile-time ABI selection.

State and persistence: No state; affects userspace struct layout.

Dependencies and integration points: Used by all UAPI headers with long-sized fields.

Risks: Wrong value breaks 32-bit/64-bit userspace ABI.

Test signals: headers_install, RV32/RV64 libc builds, and ABI struct-size checks.

Source read size: 14 lines, 377 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/bitsperlong.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/bpf_perf_event.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/bpf_perf_event.h

Purpose: Provides RISC-V BPF perf event UAPI register mapping.

Important APIs/types/functions: Includes generic BPF perf event definitions or architecture register access definitions.

Control flow: BPF/perf tooling uses the definitions to read sampled register state.

State and persistence: No persistent state in the header.

Dependencies and integration points: Used by eBPF helpers, perf events, and tracing tools.

Risks: Register-index mismatch breaks BPF programs that inspect perf contexts.

Test signals: BPF selftests, perf trace tests, and headers_install.

Source read size: 9 lines, 261 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/bpf_perf_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/byteorder.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/byteorder.h

Purpose: Selects little-endian byte order definitions for RISC-V UAPI.

Important APIs/types/functions: Includes Linux little-endian byteorder helpers.

Control flow: Compile-time only.

State and persistence: No state.

Dependencies and integration points: Used by exported structs/protocols that need endian annotations.

Risks: Wrong byteorder breaks all userspace ABI interpretation.

Test signals: headers_install and endian conversion build tests.

Source read size: 12 lines, 327 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/byteorder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/elf.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/elf.h

Purpose: Defines RISC-V ELF UAPI constants, relocation flags, register-set notes, and HWCAP exposure.

Important APIs/types/functions: Defines `ELF_NGREG`, `ELF_NFPREG`, RISC-V relocation/flag constants, `R_RISCV_*` values, and arch ELF metadata consumed by tools.

Control flow: No kernel runtime flow in the header; ELF loader, core dump, ptrace, and toolchains consume constants.

State and persistence: ELF files/core notes persist these ABI values.

Dependencies and integration points: Used by binutils, glibc, loaders, ptrace/core dump, and module/toolchain flows.

Risks: ABI number changes break binaries, debuggers, and core files.

Test signals: Toolchain relocation tests, core dump regset tests, headers_install, and dynamic loader smoke tests.

Source read size: 101 lines, 2916 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/hwcap.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/hwcap.h

Purpose: Defines legacy RISC-V ELF HWCAP bits exposed to userspace.

Important APIs/types/functions: Defines `COMPAT_HWCAP_ISA_*` bits for base ISA letters such as I/M/A/F/D/C/V.

Control flow: Kernel populates auxvec HWCAP based on probed ISA; userspace reads it.

State and persistence: Per-process auxvec hardware capability state.

Dependencies and integration points: Used by ELF loader, libc dispatch, and CPU feature parsing.

Risks: Wrong bits cause userspace to execute unsupported instructions or miss optimizations.

Test signals: getauxval/hwcap tests, libc ifunc dispatch, QEMU extension matrix.

Source read size: 26 lines, 973 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/hwcap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/hwprobe.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/hwprobe.h

Purpose: Defines the `riscv_hwprobe` userspace ABI for detailed RISC-V hardware capability and performance queries.

Important APIs/types/functions: Defines `struct riscv_hwprobe`, keys for vendor/arch IDs, base behavior, ISA extension bitmaps, misaligned access performance, block sizes, virtual address range, time CSR frequency, vendor extension keys, and `RISCV_HWPROBE_WHICH_CPUS`.

Control flow: Userspace passes key/value entries to the hwprobe syscall; kernel fills values for the selected CPU set.

State and persistence: Returned values reflect probed CPU capability state and may vary by CPU selection.

Dependencies and integration points: Integrated with `sys_hwprobe.c`, cpufeature, vendor extensions, libc/runtime dispatch, and documentation.

Risks: This is a stable UAPI; bit reuse or incorrect per-CPU aggregation can make userspace dispatch unsafe.

Test signals: hwprobe selftests, heterogeneous CPU masks, vendor extension keys, extension matrix, and headers ABI checks.

Source read size: 125 lines, 4979 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/hwprobe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/kvm.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/kvm.h

Purpose: Defines the RISC-V KVM userspace ABI for vCPU registers, ISA/SBI extension IDs, timers, AIA CSRs, firmware features, and one-reg encodings.

Important APIs/types/functions: Important types include `kvm_riscv_config`, `kvm_riscv_core`, `kvm_riscv_csr`, `kvm_riscv_aia_csr`, `kvm_riscv_timer`, extension enums `KVM_RISCV_ISA_EXT_ID` and `KVM_RISCV_SBI_EXT_ID`, SBI STA/FWFT structs, and `KVM_REG_RISCV_*` macros.

Control flow: Userspace VMMs use KVM ioctls and one-reg IDs to configure ISA exposure, inspect/save/restore vCPU state, timers, CSRs, and SBI feature policy.

State and persistence: ABI state persists in VM/vCPU register files, timer values, enabled extension bitmaps, and migration streams.

Dependencies and integration points: Consumed by QEMU/kvmtool, KVM RISC-V kernel code, selftests, and migration tooling.

Risks: Enum ordering and register IDs are ABI. Reordering or wrong struct sizing breaks userspace VMMs and migration compatibility.

Test signals: KVM selftests, QEMU boot/migration, one-reg round trips, timer/AIA tests, and headers_install ABI checks.

Source read size: 401 lines, 12559 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/kvm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/perf_regs.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/perf_regs.h

Purpose: Defines perf register numbers for RISC-V sampled register dumps.

Important APIs/types/functions: Enumerates `PERF_REG_RISCV_*` GPR indices and `PERF_REG_RISCV_MAX`.

Control flow: Perf encodes sampled registers using these indices; userspace decodes samples accordingly.

State and persistence: Perf sample ABI state.

Dependencies and integration points: Used by perf, eBPF stack/register sampling, and unwind tooling.

Risks: Index changes break perf.data compatibility and tooling.

Test signals: perf record/report register sampling, BPF perf_event tests, and headers ABI checks.

Source read size: 42 lines, 920 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/perf_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/ptrace.h

Purpose: Defines user-visible RISC-V ptrace register structures and regset constants.

Important APIs/types/functions: Defines `struct user_regs_struct`, floating-point state structs, vector state headers/data structs, NT regset constants, and alignment/size metadata.

Control flow: Ptrace, core dump, and signal tooling copy these structs between kernel and userspace.

State and persistence: User ABI state includes GPR/FPR/vector register files and regset note formats.

Dependencies and integration points: Used by debuggers, core dumps, signal context, KVM core register ABI, and libc/sysroot headers.

Risks: Layout changes break debuggers, core files, checkpoint/restore, and signal tooling.

Test signals: ptrace regset selftests, gdb/core dump tests, vector regset tests, and RV32/RV64 ABI checks.

Source read size: 169 lines, 4120 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/setup.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/setup.h

Purpose: Defines RISC-V boot command-line size for UAPI consumers.

Important APIs/types/functions: Defines `COMMAND_LINE_SIZE` as 2048.

Control flow: Compile-time only.

State and persistence: Boot command line storage size.

Dependencies and integration points: Used by boot/setup tooling and exported headers.

Risks: Changing size can affect bootloader/user tooling assumptions.

Test signals: headers_install and boot command-line length tests.

Source read size: 8 lines, 203 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/sigcontext.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/sigcontext.h

Purpose: Defines the RISC-V signal context ABI for saved user register state.

Important APIs/types/functions: Defines `struct sigcontext` containing user GPRs and floating/vector extension state references.

Control flow: Signal delivery writes this structure to the user signal frame; sigreturn validates and restores it.

State and persistence: Per-signal-frame persistent ABI state until sigreturn.

Dependencies and integration points: Used by signal.c, compat signal code, libc, debuggers, and checkpoint/restore.

Risks: Layout or extension-state mistakes can corrupt restored user context or break old binaries.

Test signals: Signal selftests, altstack, FPU/vector signal tests, sigreturn fuzzing, and libc ABI checks.

Source read size: 41 lines, 948 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/sigcontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/ucontext.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/ucontext.h

Purpose: Defines RISC-V `ucontext_t` ABI wrapper for signal/user context.

Important APIs/types/functions: Defines `struct ucontext` fields including flags, link, stack, signal mask, and machine context.

Control flow: Signal setup populates ucontext; userspace signal handlers and `setcontext`-style code consume it.

State and persistence: Signal-frame ABI state.

Dependencies and integration points: Used by libc, signal delivery, sigreturn, and checkpoint/restore tooling.

Risks: Struct layout changes break user signal handlers and unwinding.

Test signals: Signal/ucontext libc tests, altstack, and headers ABI checks.

Source read size: 38 lines, 1348 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/ucontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/unistd.h

Purpose: Defines RISC-V UAPI syscall number inclusions and architecture-specific syscall availability.

Important APIs/types/functions: Sets `__ARCH_WANT_NEW_STAT`, `__ARCH_WANT_SET_GET_RLIMIT`, includes generic unistd, and defines RISC-V arch syscall numbers such as `riscv_hwprobe` where applicable.

Control flow: Userspace and kernel generated tables compile against these numbers.

State and persistence: Stable syscall ABI numbering.

Dependencies and integration points: Used by libc, seccomp, syscall tables, strace, and VDSO/syscall wrappers.

Risks: Changing numbers or feature wants breaks userspace ABI.

Test signals: headers_install, libc syscall tests, strace/seccomp, and syscall table generation.

Source read size: 23 lines, 852 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/Makefile -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/Makefile

Purpose: Builds the RISC-V architecture kernel objects and applies special compiler flags for low-level entry, patching, vDSO, suspend, and feature code.

Important APIs/types/functions: Defines `obj-y`, `obj-$(CONFIG_*)`, `extra-y`, CFLAGS overrides, syscall table generation, vdso targets, and per-object instrumentation restrictions.

Control flow: Kbuild selects objects based on config, builds generated syscall tables/asm offsets, and compiles sensitive files with instrumentation disabled when required.

State and persistence: No runtime state, but build outputs determine linked kernel behavior.

Dependencies and integration points: Integrates with Kbuild, syscall generation, vDSO/compat vDSO, ftrace, alternatives, KASAN/KCSAN, ACPI, KVM, suspend, and vendor extension objects.

Risks: Wrong object selection or missing no-instrument flags can break early boot, patching with MMU off, or tracing recursion.

Test signals: Config matrix builds for SMP/MMU/ACPI/KVM/VDSO/ftrace/suspend/vendor extensions and boot smoke tests.

Source read size: 130 lines, 3830 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/acpi.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/acpi.c

Purpose: Implements RISC-V low-level ACPI boot support, table initialization, FADT validation, RINTC MADT caching, ACPI table mapping, ACPI ioremap policy, PCI config access, and CPU UID lookup.

Important APIs/types/functions: Key functions are `parse_acpi()`, `acpi_boot_table_init()`, `acpi_init_rintc_map()`, `acpi_cpu_get_madt_rintc()`, `__acpi_map_table()`, `__acpi_unmap_table()`, `acpi_os_ioremap()`, `raw_pci_read()`, `raw_pci_write()`, and `acpi_get_cpu_uid()`.

Control flow: Early `acpi=` parameters decide whether to disable, prefer, or force ACPI. Boot initialization enables ACPI, parses tables, checks FADT revision/HW-reduced mode, parses SPCR/BGRT, caches enabled MADT RINTC entries by CPU, and maps AML/ACPI physical regions with EFI/memblock-aware protections.

State and persistence: Persistent state includes `acpi_disabled`, `acpi_noirq`, `acpi_pci_disabled`, command-line booleans, and `cpu_madt_rintc[NR_CPUS]`.

Dependencies and integration points: Integrates with EFI, memblock, early remap, ACPI core, MADT/RINTC, SPCR early console, BGRT, PCI, and RISC-V hart-to-CPU mapping.

Risks: Bad ACPI enable policy or ioremap protections can boot the wrong firmware path, expose kernel memory to AML mappings, or lose CPU UID/RINTC data.

Test signals: ACPI and DT boot matrix, `acpi=off/on/force`, invalid FADT tests, SPCR early console, ACPI PCI config access, MADT RINTC CPU mapping, and EFI memory map edge cases.

Source read size: 355 lines, 9593 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/acpi_numa.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/acpi_numa.c

Purpose: Implements ACPI SRAT-based NUMA CPU-to-node discovery for RISC-V.

Important APIs/types/functions: Key functions are `acpi_map_cpus_to_nodes()`, `acpi_numa_rintc_affinity_init()`, `acpi_parse_rintc_pxm()`, and internal UID-to-CPU lookup.

Control flow: SRAT RINTC affinity entries map ACPI processor UIDs to logical CPUs using cached MADT RINTC data, translate proximity domains to nodes, record early CPU-node mapping, and mark parsed NUMA nodes.

State and persistence: Persistent boot-time state is `acpi_early_node_map[NR_CPUS]` and generic NUMA parsed-node masks.

Dependencies and integration points: Depends on ACPI SRAT/MADT, `acpi_get_cpu_uid()`, `cpuid_to_hartid_map()`, generic NUMA mapping, memblock, and topology.

Risks: UID mismatches or invalid proximity domains put CPUs on wrong NUMA nodes, hurting locality or causing boot warnings/bad SRAT handling.

Test signals: ACPI NUMA boots, malformed SRAT length tests, disabled SRAT, multiple proximity domains, CPU hotplug/topology sysfs, and memory locality benchmarks.

Source read size: 134 lines, 3322 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/acpi_numa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/alternative.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/alternative.c

Purpose: Implements RISC-V runtime alternative instruction patching for CPU features, vendor errata, modules, and the vDSO.

Important APIs/types/functions: Key functions are `riscv_fill_cpu_mfr_info()`, `riscv_alternative_fix_offsets()`, `apply_boot_alternatives()`, `apply_early_boot_alternatives()`, `apply_module_alternatives()`, and internal JAL/AUIPC+JALR fixup helpers.

Control flow: The code reads vendor/arch/implementation IDs from CSRs or SBI, runs generic cpufeature patching, dispatches vendor errata patch functions, adjusts PC-relative call/jump immediates when alternative blocks move, and applies alternatives at early boot, normal boot, module load, and vDSO setup.

State and persistence: Persistent effects are patched kernel/module/vDSO instruction bytes; manufacturer info is transient.

Dependencies and integration points: Depends on alternative section symbols, cpufeature patching, vendor errata, SBI/CSR IDs, instruction decoder/encoder, text patching, module loader, and vDSO ELF sections.

Risks: Incorrect immediate fixups or vendor selection can patch invalid code very early in boot. Early path has MMU-off and no-instrumentation constraints.

Test signals: Boot with feature/errata alternatives, module alternative tests, vDSO alternative checks, objdump validation of call fixups, vendor CPU matrix, and ftrace/KASAN instrumentation builds.

Source read size: 241 lines, 6244 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/alternative.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/asm-offsets.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/asm-offsets.c

Purpose: Generates assembler-visible offsets and constants for RISC-V task, trap, suspend, KVM, FPU, stacktrace, ftrace, and SBI structures.

Important APIs/types/functions: Emits `OFFSET()` and `DEFINE()` values for `task_struct`, `thread_info`, `pt_regs`, suspend/hibernate structs, `kvm_vcpu_arch`, `kvm_cpu_context`, `kvm_cpu_trap`, FPU state, stack frames, ftrace regs, and SBI FWFT constants.

Control flow: Kbuild compiles this C file in offset-generation mode; emitted constants are included by low-level assembly.

State and persistence: No runtime state, but generated constants encode structure layout contracts consumed by assembly.

Dependencies and integration points: Depends on scheduler, ptrace, KVM host structs, suspend, stacktrace, ftrace, SBI, and config options like SCS, USER_CFI, KVM, and dynamic ftrace.

Risks: Missing or stale offsets cause silent register corruption in entry, context switch, KVM, hibernation, or tracing assembly.

Test signals: Full config matrix builds, objdump/asm-offset checks after struct changes, KVM boot, suspend/hibernate, ftrace, and SCS/user-CFI builds.

Source read size: 542 lines, 22929 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/asm-offsets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/bugs.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kernel/bugs.c

Purpose: Provides the RISC-V architecture bug-check initialization hook.

Important APIs/types/functions: Implements `check_bugs()`.

Control flow: Called during boot after CPU feature setup; currently delegates to `riscv_check_elf_hwcap()` when MMU support is enabled.

State and persistence: Persistent effects are any CPU/hwcap validation warnings or adjustments performed by delegated helpers.

Dependencies and integration points: Integrates with generic init bug checking and RISC-V ELF hwcap/cpufeature code.

Risks: Too little validation can expose incorrect HWCAPs; too much validation can reject working systems.

Test signals: Boot logs across extension sets, HWCAP/getauxval tests, MMU and NOMMU builds.

Source read size: 60 lines, 1401 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kernel/bugs.c -->
