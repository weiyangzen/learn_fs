# subset-b-000754 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/kgdb.h -->
# sources/distributed-fs/ceph-client/arch/nios2/include/asm/kgdb.h

Purpose: defines the Nios II KGDB register numbering, register byte counts, breakpoint instruction, and
architecture breakpoint helper used by kgdb core and the Nios II trap path.

Important APIs/types/functions: functions: `arch_kgdb_breakpoint`; prototypes: `__volatile__`; enums: `regnames`; macros:
`_ASM_NIOS2_KGDB_H`, `CACHE_FLUSH_IS_SAFE`, `BUFMAX`, `GDB_SIZEOF_REG`, `DBG_MAX_REG_NUM`,
`NUMREGBYTES`, `BREAK_INSTR_SIZE`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: State is stored in saved pt_regs/switch_stack frames, user signal frames, debugger register packets,
thread flags, and ptrace-visible register sets.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB
subsystems plus Nios II control-register assembly. This source is part of the Nios II architecture
port under the vendored ceph-client kernel tree.

Risks: Risks include register-frame layout mismatches, incorrect syscall restart/error translation, broken
debugger or signal ABI, recursive exceptions, and returning to userspace with inconsistent status
bits.

Test signals: Test signals are syscall ABI tests, strace/ptrace, signal delivery and sigreturn tests, KGDB
breakpoint handling, interrupt/preemption stress, illegal/alignment exception tests, and user/kernel
register dump sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/kgdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/linkage.h -->
# sources/distributed-fs/ceph-client/arch/nios2/include/asm/linkage.h

Purpose: sets Nios II assembly/linkage alignment rules so ENTRY/SYM linkage macros emit functions on the
alignment expected by the architecture.

Important APIs/types/functions: macros: `_ASM_NIOS2_LINKAGE_H`, `__ALIGN`, `__ALIGN_STR`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB
subsystems plus Nios II control-register assembly. This source is part of the Nios II architecture
port under the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/linkage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/mmu.h -->
# sources/distributed-fs/ceph-client/arch/nios2/include/asm/mmu.h

Purpose: defines the Nios II mm_context_t storage used as the per-mm software ASID/PID context.

Important APIs/types/functions: typedefs: `mm_context_t`; macros: `_ASM_NIOS2_MMU_H`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: State includes page tables, PTE permission/cache bits, ASID or context identifiers, TLB entries,
vmalloc/ioremap mappings, swap PTE encodings, and boot-time memory reservations.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB
subsystems plus Nios II control-register assembly. This source is part of the Nios II architecture
port under the vendored ceph-client kernel tree.

Risks: Risks include stale TLB/cache state, wrong access permissions, corrupted page tables, bad ASID
reuse, kernel faults without fixups, DMA coherency loss, or ABI-visible memory corruption.

Test signals: Test signals are boot under an emulator or board, page-fault and fork/exec stress, mmap/mprotect,
swap where enabled, vmalloc/ioremap users, DMA drivers, module loading, and cache/TLB debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/mmu_context.h -->
# sources/distributed-fs/ceph-client/arch/nios2/include/asm/mmu_context.h

Purpose: declares and inlines the Nios II MMU context lifecycle hooks that allocate ASIDs, switch address
spaces, and integrate with generic mm context code.

Important APIs/types/functions: functions: `init_new_context`; prototypes: `Copyright`, `switch_mm`; types: `mm_struct`,
`task_struct`; macros: `_ASM_NIOS2_MMU_CONTEXT_H`, `init_new_context`, `activate_mm`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: State includes page tables, PTE permission/cache bits, ASID or context identifiers, TLB entries,
vmalloc/ioremap mappings, swap PTE encodings, and boot-time memory reservations.

Dependencies and integration points: Dependencies include `linux/mm_types.h`, `asm-generic/mm_hooks.h`, `asm-generic/mmu_context.h`.
Integration points include generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree,
syscall, and cache/TLB subsystems plus Nios II control-register assembly. This source is part of the
Nios II architecture port under the vendored ceph-client kernel tree.

Risks: Risks include stale TLB/cache state, wrong access permissions, corrupted page tables, bad ASID
reuse, kernel faults without fixups, DMA coherency loss, or ABI-visible memory corruption.

Test signals: Test signals are boot under an emulator or board, page-fault and fork/exec stress, mmap/mprotect,
swap where enabled, vmalloc/ioremap users, DMA drivers, module loading, and cache/TLB debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/mmu_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/page.h -->
# sources/distributed-fs/ceph-client/arch/nios2/include/asm/page.h

Purpose: defines Nios II page constants, kernel/user address layout, physical offset conversion,
PTE/PGD/pgprot scalar types, and page copy/clear hooks.

Important APIs/types/functions: prototypes: `Copyright`; types: `page`; typedefs: `pgtable_t`, `pte`, `pgd`, `pgprot`; macros:
`_ASM_NIOS2_PAGE_H`, `PAGE_OFFSET`, `PHYS_OFFSET`, `ARCH_PFN_OFFSET`, `clear_page(page)`,
`copy_page(to, from)`, `clear_user_page`, `pte_val(x)`, `pgd_val(x)`, `pgprot_val(x)`, `__pte(x)`,
`__pgd(x)`, and 8 more.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: State includes page tables, PTE permission/cache bits, ASID or context identifiers, TLB entries,
vmalloc/ioremap mappings, swap PTE encodings, and boot-time memory reservations.

Dependencies and integration points: Dependencies include `linux/pfn.h`, `linux/const.h`, `vdso/page.h`, `asm-generic/memory_model.h`,
`asm-generic/getorder.h`. Integration points include generic Linux MM, irq, signal, ptrace, module,
timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II control-register assembly.
This source is part of the Nios II architecture port under the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/page.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/pgalloc.h -->
# sources/distributed-fs/ceph-client/arch/nios2/include/asm/pgalloc.h

Purpose: connects Nios II page-directory allocation and PTE free hooks to the generic page-table allocator.

Important APIs/types/functions: functions: `Copyright`, `pmd_populate`; macros: `_ASM_NIOS2_PGALLOC_H`, `__pte_free_tlb(tlb, pte,
addr)`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: State includes page tables, PTE permission/cache bits, ASID or context identifiers, TLB entries,
vmalloc/ioremap mappings, swap PTE encodings, and boot-time memory reservations.

Dependencies and integration points: Dependencies include `linux/mm.h`, `asm-generic/pgalloc.h`. Integration points include generic Linux
MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus
Nios II control-register assembly. This source is part of the Nios II architecture port under the
vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/pgalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/pgtable-bits.h -->
# sources/distributed-fs/ceph-client/arch/nios2/include/asm/pgtable-bits.h

Purpose: names the Nios II hardware and software PTE bit assignments for global, execute, read, write, cache,
present, accessed, dirty, and swap-exclusive state.

Important APIs/types/functions: macros: `_ASM_NIOS2_PGTABLE_BITS_H`, `_PAGE_GLOBAL`, `_PAGE_EXEC`, `_PAGE_WRITE`, `_PAGE_READ`,
`_PAGE_CACHED`, `_PAGE_PRESENT`, `_PAGE_ACCESSED`, `_PAGE_DIRTY`, `_PAGE_SWP_EXCLUSIVE`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: State includes page tables, PTE permission/cache bits, ASID or context identifiers, TLB entries,
vmalloc/ioremap mappings, swap PTE encodings, and boot-time memory reservations.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB
subsystems plus Nios II control-register assembly. This source is part of the Nios II architecture
port under the vendored ceph-client kernel tree.

Risks: Risks include stale TLB/cache state, wrong access permissions, corrupted page tables, bad ASID
reuse, kernel faults without fixups, DMA coherency loss, or ABI-visible memory corruption.

Test signals: Test signals are boot under an emulator or board, page-fault and fork/exec stress, mmap/mprotect,
swap where enabled, vmalloc/ioremap users, DMA drivers, module loading, and cache/TLB debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/pgtable-bits.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/pgtable.h -->
# sources/distributed-fs/ceph-client/arch/nios2/include/asm/pgtable.h

Purpose: implements the Nios II two-level page-table contract, VMALLOC/modules address windows, PTE
protection helpers, swap encoding, and MMU-cache update hooks.

Important APIs/types/functions: functions: `set_pmd`, `pgprot_noncached`, `pte_none`, `pte_present`, `pte_mkclean`, `pte_mkold`,
`pte_mkwrite_novma`, `pte_mkdirty`, `pte_mkyoung`, `pte_modify`, `pmd_present`, `pmd_clear`, and 9
more; prototypes: `__pgprot`, `pte_val`, `flush_dcache_range`, `set_pte`, `pmd_val`, `paging_init`,
`set_ptes`; types: `mm_struct`; macros: `_ASM_NIOS2_PGTABLE_H`, `VMALLOC_START`, `VMALLOC_END`,
`MODULES_VADDR`, `MODULES_END`, `MKP(x, w, r)`, `PAGE_KERNEL`, `PAGE_SHARED`, `PAGE_COPY`,
`PTRS_PER_PGD`, `PTRS_PER_PTE`, `USER_PTRS_PER_PGD`, and 22 more.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: State includes page tables, PTE permission/cache bits, ASID or context identifiers, TLB entries,
vmalloc/ioremap mappings, swap PTE encodings, and boot-time memory reservations.

Dependencies and integration points: Dependencies include `linux/io.h`, `linux/bug.h`, `asm/page.h`, `asm/cacheflush.h`,
`asm/tlbflush.h`, `asm/pgtable-bits.h`, `asm-generic/pgtable-nopmd.h`. Integration points include
generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB
subsystems plus Nios II control-register assembly. This source is part of the Nios II architecture
port under the vendored ceph-client kernel tree.

Risks: Risks include stale TLB/cache state, wrong access permissions, corrupted page tables, bad ASID
reuse, kernel faults without fixups, DMA coherency loss, or ABI-visible memory corruption.

Test signals: Test signals are boot under an emulator or board, page-fault and fork/exec stress, mmap/mprotect,
swap where enabled, vmalloc/ioremap users, DMA drivers, module loading, and cache/TLB debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/processor.h -->
# sources/distributed-fs/ceph-client/arch/nios2/include/asm/processor.h

Purpose: defines Nios II thread_struct, task register access helpers, userspace stack limits, kuser mapping
constants, and process entry helpers.

Important APIs/types/functions: prototypes: `start_thread`; types: `thread_struct`, `pt_regs`, `task_struct`; macros:
`_ASM_NIOS2_PROCESSOR_H`, `NIOS2_FLAG_KTHREAD`, `NIOS2_OP_NOP`, `NIOS2_OP_BREAK`, `STACK_TOP`,
`STACK_TOP_MAX`, `KUSER_BASE`, `KUSER_SIZE`, `TASK_SIZE`, `TASK_UNMAPPED_BASE`, `INIT_THREAD`,
`task_pt_regs(p)`, and 3 more.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `asm/ptrace.h`, `asm/registers.h`, `asm/page.h`. Integration points include
generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB
subsystems plus Nios II control-register assembly. This source is part of the Nios II architecture
port under the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/nios2/include/asm/ptrace.h

Purpose: defines the kernel pt_regs and switch_stack layouts consumed by exception entry, ptrace, signal
delivery, kgdb, and context switching.

Important APIs/types/functions: prototypes: `show_regs`; types: `pt_regs`, `switch_stack`; macros: `_ASM_NIOS2_PTRACE_H`,
`user_mode(regs)`, `instruction_pointer(regs)`, `profile_pc(regs)`, `user_stack_pointer(regs)`,
`current_pt_regs()`, `force_successful_syscall_return()`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: State is stored in saved pt_regs/switch_stack frames, user signal frames, debugger register packets,
thread flags, and ptrace-visible register sets.

Dependencies and integration points: Dependencies include `uapi/asm/ptrace.h`. Integration points include generic Linux MM, irq, signal,
ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II control-
register assembly. This source is part of the Nios II architecture port under the vendored ceph-
client kernel tree.

Risks: Risks include register-frame layout mismatches, incorrect syscall restart/error translation, broken
debugger or signal ABI, recursive exceptions, and returning to userspace with inconsistent status
bits.

Test signals: Test signals are syscall ABI tests, strace/ptrace, signal delivery and sigreturn tests, KGDB
breakpoint handling, interrupt/preemption stress, illegal/alignment exception tests, and user/kernel
register dump sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/registers.h -->
# sources/distributed-fs/ceph-client/arch/nios2/include/asm/registers.h

Purpose: names Nios II control registers and status/TLB bit fields used by low-level assembly, TLB code, IRQ
code, and context switching.

Important APIs/types/functions: macros: `_ASM_NIOS2_REGISTERS_H`, `CTL_FSTATUS`, `CTL_ESTATUS`, `CTL_BSTATUS`, `CTL_IENABLE`,
`CTL_IPENDING`, `CTL_CPUID`, `CTL_RSV1`, `CTL_EXCEPTION`, `CTL_PTEADDR`, `CTL_TLBACC`,
`CTL_TLBMISC`, and 21 more.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `asm/cpuinfo.h`. Integration points include generic Linux MM, irq, signal,
ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II control-
register assembly. This source is part of the Nios II architecture port under the vendored ceph-
client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/registers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/setup.h -->
# sources/distributed-fs/ceph-client/arch/nios2/include/asm/setup.h

Purpose: declares Nios II setup hooks and imports generic setup definitions used during early architecture
initialization.

Important APIs/types/functions: prototypes: `Copyright`; macros: `_ASM_NIOS2_SETUP_H`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `asm-generic/setup.h`. Integration points include generic Linux MM, irq,
signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II
control-register assembly. This source is part of the Nios II architecture port under the vendored
ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/shmparam.h -->
# sources/distributed-fs/ceph-client/arch/nios2/include/asm/shmparam.h

Purpose: sets SHMLBA from the data-cache size so SysV shared-memory mappings avoid Nios II cache-alias
hazards.

Important APIs/types/functions: macros: `_ASM_NIOS2_SHMPARAM_H`, `SHMLBA`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB
subsystems plus Nios II control-register assembly. This source is part of the Nios II architecture
port under the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/shmparam.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/string.h -->
# sources/distributed-fs/ceph-client/arch/nios2/include/asm/string.h

Purpose: advertises and declares Nios II architecture implementations of memset, memcpy, and memmove.

Important APIs/types/functions: prototypes: `Copyright`; macros: `_ASM_NIOS2_STRING_H`, `__HAVE_ARCH_MEMSET`, `__HAVE_ARCH_MEMCPY`,
`__HAVE_ARCH_MEMMOVE`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB
subsystems plus Nios II control-register assembly. This source is part of the Nios II architecture
port under the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/swab.h -->
# sources/distributed-fs/ceph-client/arch/nios2/include/asm/swab.h

Purpose: uses the optional Nios II custom instruction for 16-bit and 32-bit byte swaps while falling back to
generic swab support otherwise.

Important APIs/types/functions: functions: `Copyright`, `__arch_swab32`; prototypes: `__nios2_swab`; macros: `_ASM_NIOS2_SWAB_H`,
`__nios2_swab(x)`, `__arch_swab16`, `__arch_swab32`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/types.h`, `asm-generic/swab.h`. Integration points include generic Linux
MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus
Nios II control-register assembly. This source is part of the Nios II architecture port under the
vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/swab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/switch_to.h -->
# sources/distributed-fs/ceph-client/arch/nios2/include/asm/switch_to.h

Purpose: wraps the assembly resume entry as the Nios II switch_to primitive and feeds the previous/current
task pointers expected by scheduler context switching.

Important APIs/types/functions: prototypes: `__volatile__`; macros: `_ASM_NIOS2_SWITCH_TO_H`, `switch_to(prev, next, last)`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB
subsystems plus Nios II control-register assembly. This source is part of the Nios II architecture
port under the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/switch_to.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/syscall.h -->
# sources/distributed-fs/ceph-client/arch/nios2/include/asm/syscall.h

Purpose: implements generic syscall tracing helpers for Nios II, including syscall number, arguments, return
value, rollback, and audit architecture values.

Important APIs/types/functions: functions: `Corporation`, `syscall_set_nr`, `syscall_rollback`, `syscall_get_error`,
`syscall_get_return_value`, `syscall_set_return_value`, `syscall_get_arguments`,
`syscall_set_arguments`, `syscall_get_arch`; types: `pt_regs`; macros: `__ASM_NIOS2_SYSCALL_H__`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `uapi/linux/audit.h`, `linux/err.h`, `linux/sched.h`. Integration points
include generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and
cache/TLB subsystems plus Nios II control-register assembly. This source is part of the Nios II
architecture port under the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are syscall ABI tests, strace/ptrace, signal delivery and sigreturn tests, KGDB
breakpoint handling, interrupt/preemption stress, illegal/alignment exception tests, and user/kernel
register dump sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/syscalls.h -->
# sources/distributed-fs/ceph-client/arch/nios2/include/asm/syscalls.h

Purpose: declares Nios II-specific syscall wrappers before including generic syscall prototypes.

Important APIs/types/functions: prototypes: `Corporation`; macros: `__ASM_NIOS2_SYSCALLS_H`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `asm-generic/syscalls.h`. Integration points include generic Linux MM, irq,
signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II
control-register assembly. This source is part of the Nios II architecture port under the vendored
ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are syscall ABI tests, strace/ptrace, signal delivery and sigreturn tests, KGDB
breakpoint handling, interrupt/preemption stress, illegal/alignment exception tests, and user/kernel
register dump sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/syscalls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/thread_info.h -->
# sources/distributed-fs/ceph-client/arch/nios2/include/asm/thread_info.h

Purpose: defines Nios II thread_info layout, stack size, current-thread lookup, and thread flags used by
return-to-user and syscall paths.

Important APIs/types/functions: prototypes: `asm`; types: `thread_info`, `task_struct`, `pt_regs`; macros:
`_ASM_NIOS2_THREAD_INFO_H`, `THREAD_SIZE_ORDER`, `THREAD_SIZE`, `INIT_THREAD_INFO(tsk)`,
`TIF_SYSCALL_TRACE`, `TIF_NOTIFY_RESUME`, `TIF_SIGPENDING`, `TIF_NEED_RESCHED`, `TIF_MEMDIE`,
`TIF_SECCOMP`, `TIF_SYSCALL_AUDIT`, `TIF_NOTIFY_SIGNAL`, and 12 more.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB
subsystems plus Nios II control-register assembly. This source is part of the Nios II architecture
port under the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/thread_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/timex.h -->
# sources/distributed-fs/ceph-client/arch/nios2/include/asm/timex.h

Purpose: defines the Nios II cycles_t interface and entropy timebase hook around get_cycles.

Important APIs/types/functions: prototypes: `get_cycles`; typedefs: `cycles_t`; macros: `_ASM_NIOS2_TIMEX_H`, `get_cycles`,
`random_get_entropy()`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB
subsystems plus Nios II control-register assembly. This source is part of the Nios II architecture
port under the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/timex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/tlb.h -->
# sources/distributed-fs/ceph-client/arch/nios2/include/asm/tlb.h

Purpose: declares the Nios II MMU PID setter and selects generic TLB gather handling.

Important APIs/types/functions: prototypes: `Copyright`; macros: `_ASM_NIOS2_TLB_H`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: State includes page tables, PTE permission/cache bits, ASID or context identifiers, TLB entries,
vmalloc/ioremap mappings, swap PTE encodings, and boot-time memory reservations.

Dependencies and integration points: Dependencies include `linux/pagemap.h`, `asm-generic/tlb.h`. Integration points include generic
Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems
plus Nios II control-register assembly. This source is part of the Nios II architecture port under
the vendored ceph-client kernel tree.

Risks: Risks include stale TLB/cache state, wrong access permissions, corrupted page tables, bad ASID
reuse, kernel faults without fixups, DMA coherency loss, or ABI-visible memory corruption.

Test signals: Test signals are boot under an emulator or board, page-fault and fork/exec stress, mmap/mprotect,
swap where enabled, vmalloc/ioremap users, DMA drivers, module loading, and cache/TLB debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/tlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/tlbflush.h -->
# sources/distributed-fs/ceph-client/arch/nios2/include/asm/tlbflush.h

Purpose: declares Nios II TLB flush entry points for all-mm, per-mm, per-range, and kernel address
invalidation.

Important APIs/types/functions: functions: `flush_tlb_page`, `flush_tlb_kernel_page`; prototypes: `Copyright`, `reload_tlb_page`;
types: `mm_struct`; macros: `_ASM_NIOS2_TLBFLUSH_H`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: State includes page tables, PTE permission/cache bits, ASID or context identifiers, TLB entries,
vmalloc/ioremap mappings, swap PTE encodings, and boot-time memory reservations.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB
subsystems plus Nios II control-register assembly. This source is part of the Nios II architecture
port under the vendored ceph-client kernel tree.

Risks: Risks include stale TLB/cache state, wrong access permissions, corrupted page tables, bad ASID
reuse, kernel faults without fixups, DMA coherency loss, or ABI-visible memory corruption.

Test signals: Test signals are boot under an emulator or board, page-fault and fork/exec stress, mmap/mprotect,
swap where enabled, vmalloc/ioremap users, DMA drivers, module loading, and cache/TLB debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/tlbflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/traps.h -->
# sources/distributed-fs/ceph-client/arch/nios2/include/asm/traps.h

Purpose: declares the Nios II trap exception helper and syscall trap ID used by assembly entry and C trap
code.

Important APIs/types/functions: prototypes: `Copyright`; macros: `_ASM_NIOS2_TRAPS_H`, `TRAP_ID_SYSCALL`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB
subsystems plus Nios II control-register assembly. This source is part of the Nios II architecture
port under the vendored ceph-client kernel tree.

Risks: Risks include register-frame layout mismatches, incorrect syscall restart/error translation, broken
debugger or signal ABI, recursive exceptions, and returning to userspace with inconsistent status
bits.

Test signals: Test signals are syscall ABI tests, strace/ptrace, signal delivery and sigreturn tests, KGDB
breakpoint handling, interrupt/preemption stress, illegal/alignment exception tests, and user/kernel
register dump sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/traps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/uaccess.h -->
# sources/distributed-fs/ceph-client/arch/nios2/include/asm/uaccess.h

Purpose: implements Nios II get_user, put_user, raw user-copy declarations, and exception-table annotated
inline user access sequences.

Important APIs/types/functions: functions: `Copyright`, `clear_user`; prototypes: `__volatile__`, `__clear_user`,
`raw_copy_from_user`, `__get_user_unknown`, `__get_user_asm`, `__typeof__`, `__put_user_asm`;
macros: `_ASM_NIOS2_UACCESS_H`, `__EX_TABLE_SECTION`, `INLINE_COPY_FROM_USER`,
`INLINE_COPY_TO_USER`, `__get_user_asm(val, insn, addr, err)`, `__get_user_8(val, ptr, err)`,
`__get_user_common(val, size, ptr, err)`, `__get_user(x, ptr)`, `get_user(x, ptr)`,
`__put_user_asm(val, insn, ptr, err)`, `__put_user_common(__pu_val, __pu_ptr)`, `__put_user(x,
ptr)`, and 1 more.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/string.h`, `asm/page.h`, `asm/extable.h`, `asm-generic/access_ok.h`.
Integration points include generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree,
syscall, and cache/TLB subsystems plus Nios II control-register assembly. This source is part of the
Nios II architecture port under the vendored ceph-client kernel tree.

Risks: Risks include stale TLB/cache state, wrong access permissions, corrupted page tables, bad ASID
reuse, kernel faults without fixups, DMA coherency loss, or ABI-visible memory corruption.

Test signals: Test signals are boot under an emulator or board, page-fault and fork/exec stress, mmap/mprotect,
swap where enabled, vmalloc/ioremap users, DMA drivers, module loading, and cache/TLB debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/uaccess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/nios2/include/asm/unistd.h

Purpose: connects Nios II to its UAPI syscall numbers and selects legacy stat64 and rlimit syscall wants.

Important APIs/types/functions: macros: `__ASM_UNISTD_H`, `__ARCH_WANT_STAT64`, `__ARCH_WANT_SET_GET_RLIMIT`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `uapi/asm/unistd.h`. Integration points include generic Linux MM, irq, signal,
ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II control-
register assembly. This source is part of the Nios II architecture port under the vendored ceph-
client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/vmalloc.h -->
# sources/distributed-fs/ceph-client/arch/nios2/include/asm/vmalloc.h

Purpose: provides the Nios II vmalloc architecture header, currently relying on generic vmalloc behavior.

Important APIs/types/functions: macros: `_ASM_NIOS2_VMALLOC_H`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB
subsystems plus Nios II control-register assembly. This source is part of the Nios II architecture
port under the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/asm/vmalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/uapi/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/nios2/include/uapi/asm/Kbuild

Purpose: defines the Nios II user ABI surface for `Kbuild`, exported to userspace through headers_install.

Important APIs/types/functions: Build declarations: `syscall-y=unistd_32.h`, `generic-y=ucontext.h`.

Control flow: The build system reads this file during Kbuild traversal; object lists and targets determine which
architecture sources are compiled or packaged for the selected configuration.

State and persistence: Persistent effects are build artifacts only: selected objects, generated images, DTBs, or exported
headers. Runtime state is created by the compiled code, not by the make fragment itself.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB
subsystems plus Nios II control-register assembly. This source is part of the Nios II architecture
port under the vendored ceph-client kernel tree.

Risks: Risks are missing objects, stale generated-header dependencies, wrong boot target names, or
configuration drift that silently excludes required architecture code.

Test signals: Test signals are architecture defconfig builds, `make ARCH=... headers_install`, boot image
generation, DTB generation, and allmodconfig coverage for selected options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/uapi/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/uapi/asm/byteorder.h -->
# sources/distributed-fs/ceph-client/arch/nios2/include/uapi/asm/byteorder.h

Purpose: defines the Nios II user ABI surface for `byteorder.h`, exported to userspace through
headers_install.

Important APIs/types/functions: macros: `_ASM_NIOS2_BYTEORDER_H`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file freezes user-visible ABI constants and structures; changes persist through compiled
userspace, ptrace tools, signal frame layouts, ELF loaders, and syscall numbering.

Dependencies and integration points: Dependencies include `linux/byteorder/little_endian.h`. Integration points include generic Linux MM,
irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II
control-register assembly. This source is part of the Nios II architecture port under the vendored
ceph-client kernel tree.

Risks: Risks are ABI breaks: changed constants, register order, signal context layout, byte order,
relocation numbers, or syscall numbering can break existing userspace and tooling.

Test signals: Test signals are headers_install, libc/toolchain builds, ptrace/core-dump inspection, signal ABI
tests, ELF relocation/module loader tests, and syscall table generation checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/uapi/asm/byteorder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/uapi/asm/elf.h -->
# sources/distributed-fs/ceph-client/arch/nios2/include/uapi/asm/elf.h

Purpose: defines the Nios II user ABI surface for `elf.h`, exported to userspace through headers_install.

Important APIs/types/functions: typedefs: `elf_greg_t`, `elf_fpregset_t`; macros: `_UAPI_ASM_NIOS2_ELF_H`, `R_NIOS2_NONE`,
`R_NIOS2_S16`, `R_NIOS2_U16`, `R_NIOS2_PCREL16`, `R_NIOS2_CALL26`, `R_NIOS2_IMM5`,
`R_NIOS2_CACHE_OPX`, `R_NIOS2_IMM6`, `R_NIOS2_IMM8`, `R_NIOS2_HI16`, `R_NIOS2_LO16`, and 16 more.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file freezes user-visible ABI constants and structures; changes persist through compiled
userspace, ptrace tools, signal frame layouts, ELF loaders, and syscall numbering.

Dependencies and integration points: Dependencies include `linux/ptrace.h`. Integration points include generic Linux MM, irq, signal,
ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II control-
register assembly. This source is part of the Nios II architecture port under the vendored ceph-
client kernel tree.

Risks: Risks are ABI breaks: changed constants, register order, signal context layout, byte order,
relocation numbers, or syscall numbering can break existing userspace and tooling.

Test signals: Test signals are headers_install, libc/toolchain builds, ptrace/core-dump inspection, signal ABI
tests, ELF relocation/module loader tests, and syscall table generation checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/uapi/asm/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/uapi/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/nios2/include/uapi/asm/ptrace.h

Purpose: defines the Nios II user ABI surface for `ptrace.h`, exported to userspace through headers_install.

Important APIs/types/functions: types: `user_pt_regs`; macros: `_UAPI_ASM_NIOS2_PTRACE_H`, `PTR_R0`, `PTR_R1`, `PTR_R2`, `PTR_R3`,
`PTR_R4`, `PTR_R5`, `PTR_R6`, `PTR_R7`, `PTR_R8`, `PTR_R9`, `PTR_R10`, and 39 more.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: State is stored in saved pt_regs/switch_stack frames, user signal frames, debugger register packets,
thread flags, and ptrace-visible register sets.

Dependencies and integration points: Dependencies include `linux/types.h`. Integration points include generic Linux MM, irq, signal,
ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II control-
register assembly. This source is part of the Nios II architecture port under the vendored ceph-
client kernel tree.

Risks: Risks include register-frame layout mismatches, incorrect syscall restart/error translation, broken
debugger or signal ABI, recursive exceptions, and returning to userspace with inconsistent status
bits.

Test signals: Test signals are syscall ABI tests, strace/ptrace, signal delivery and sigreturn tests, KGDB
breakpoint handling, interrupt/preemption stress, illegal/alignment exception tests, and user/kernel
register dump sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/uapi/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/uapi/asm/sigcontext.h -->
# sources/distributed-fs/ceph-client/arch/nios2/include/uapi/asm/sigcontext.h

Purpose: defines the Nios II user ABI surface for `sigcontext.h`, exported to userspace through
headers_install.

Important APIs/types/functions: types: `sigcontext`; macros: `_UAPI__ASM_SIGCONTEXT_H`, `MCONTEXT_VERSION`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file freezes user-visible ABI constants and structures; changes persist through compiled
userspace, ptrace tools, signal frame layouts, ELF loaders, and syscall numbering.

Dependencies and integration points: Dependencies include `linux/types.h`. Integration points include generic Linux MM, irq, signal,
ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II control-
register assembly. This source is part of the Nios II architecture port under the vendored ceph-
client kernel tree.

Risks: Risks are ABI breaks: changed constants, register order, signal context layout, byte order,
relocation numbers, or syscall numbering can break existing userspace and tooling.

Test signals: Test signals are headers_install, libc/toolchain builds, ptrace/core-dump inspection, signal ABI
tests, ELF relocation/module loader tests, and syscall table generation checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/uapi/asm/sigcontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/uapi/asm/signal.h -->
# sources/distributed-fs/ceph-client/arch/nios2/include/uapi/asm/signal.h

Purpose: defines the Nios II user ABI surface for `signal.h`, exported to userspace through headers_install.

Important APIs/types/functions: macros: `_ASM_NIOS2_SIGNAL_H`, `SA_RESTORER`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: State is stored in saved pt_regs/switch_stack frames, user signal frames, debugger register packets,
thread flags, and ptrace-visible register sets.

Dependencies and integration points: Dependencies include `asm-generic/signal.h`. Integration points include generic Linux MM, irq,
signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II
control-register assembly. This source is part of the Nios II architecture port under the vendored
ceph-client kernel tree.

Risks: Risks include register-frame layout mismatches, incorrect syscall restart/error translation, broken
debugger or signal ABI, recursive exceptions, and returning to userspace with inconsistent status
bits.

Test signals: Test signals are syscall ABI tests, strace/ptrace, signal delivery and sigreturn tests, KGDB
breakpoint handling, interrupt/preemption stress, illegal/alignment exception tests, and user/kernel
register dump sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/uapi/asm/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/uapi/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/nios2/include/uapi/asm/unistd.h

Purpose: defines the Nios II user ABI surface for `unistd.h`, exported to userspace through headers_install.

Important APIs/types/functions: The file is declarative and primarily contributes constants or include/export wiring.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file freezes user-visible ABI constants and structures; changes persist through compiled
userspace, ptrace tools, signal frame layouts, ELF loaders, and syscall numbering.

Dependencies and integration points: Dependencies include `asm/unistd_32.h`. Integration points include generic Linux MM, irq, signal,
ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II control-
register assembly. This source is part of the Nios II architecture port under the vendored ceph-
client kernel tree.

Risks: Risks are ABI breaks: changed constants, register order, signal context layout, byte order,
relocation numbers, or syscall numbering can break existing userspace and tooling.

Test signals: Test signals are headers_install, libc/toolchain builds, ptrace/core-dump inspection, signal ABI
tests, ELF relocation/module loader tests, and syscall table generation checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/include/uapi/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/Makefile -->
# sources/distributed-fs/ceph-client/arch/nios2/kernel/Makefile

Purpose: selects the Nios II kernel objects for build, including entry, traps, setup, process, signal,
syscall, IRQ, time, module, CPU info, and optional KGDB/alignment trap support.

Important APIs/types/functions: Build declarations: `obj-y=head.o`, `obj-y=cpuinfo.o`, `obj-y=entry.o`, `obj-y=insnemu.o`,
`obj-y=irq.o`, `obj-y=nios2_ksyms.o`, `obj-y=process.o`, `obj-y=prom.o`, `obj-y=ptrace.o`,
`obj-y=setup.o`, `obj-y=signal.o`, `obj-y=sys_nios2.o`, `obj-y=syscall_table.o`, `obj-y=time.o`,
`obj-y=traps.o`.

Control flow: The build system reads this file during Kbuild traversal; object lists and targets determine which
architecture sources are compiled or packaged for the selected configuration.

State and persistence: Persistent effects are build artifacts only: selected objects, generated images, DTBs, or exported
headers. Runtime state is created by the compiled code, not by the make fragment itself.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB
subsystems plus Nios II control-register assembly. This source is part of the Nios II architecture
port under the vendored ceph-client kernel tree.

Risks: Risks are missing objects, stale generated-header dependencies, wrong boot target names, or
configuration drift that silently excludes required architecture code.

Test signals: Test signals are architecture defconfig builds, `make ARCH=... headers_install`, boot image
generation, DTB generation, and allmodconfig coverage for selected options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/asm-offsets.c -->
# sources/distributed-fs/ceph-client/arch/nios2/kernel/asm-offsets.c

Purpose: emits structure offsets and constants consumed by Nios II assembly for pt_regs, switch_stack,
thread_info, task_struct, and thread_struct fields.

Important APIs/types/functions: functions: `Copyright`; prototypes: `OFFSET`; macros: `COMPILE_OFFSETS`.

Control flow: Generic kernel code calls the exported architecture hooks during boot, process management, fault
handling, cache/TLB maintenance, module loading, or platform probing; the file performs the
architecture-specific register and memory operations then returns to the generic subsystem.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/stddef.h`, `linux/sched.h`, `linux/kernel_stat.h`, `linux/ptrace.h`,
`linux/hardirq.h`, `linux/thread_info.h`, `linux/kbuild.h`. Integration points include generic Linux
MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus
Nios II control-register assembly. This source is part of the Nios II architecture port under the
vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/asm-offsets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/cpuinfo.c -->
# sources/distributed-fs/ceph-client/arch/nios2/kernel/cpuinfo.c

Purpose: parses CPU properties from devicetree, stores Nios II cache/TLB/MMU features in cpuinfo, and exposes
them through /proc/cpuinfo seq operations.

Important APIs/types/functions: functions: `fcpu`, `setup_cpuinfo`, `show_cpuinfo`, `cpuinfo_stop`; prototypes:
`of_property_read_u32`, `panic`, `seq_printf`, `cpuinfo_start`; types: `cpuinfo`, `device_node`;
macros: `err_cpu(x)`.

Control flow: Generic kernel code calls the exported architecture hooks during boot, process management, fault
handling, cache/TLB maintenance, module loading, or platform probing; the file performs the
architecture-specific register and memory operations then returns to the generic subsystem.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/kernel.h`, `linux/init.h`, `linux/delay.h`, `linux/seq_file.h`,
`linux/string.h`, `linux/of.h`, `asm/cpuinfo.h`. Integration points include generic Linux MM, irq,
signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II
control-register assembly. This source is part of the Nios II architecture port under the vendored
ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/cpuinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/entry.S -->
# sources/distributed-fs/ceph-client/arch/nios2/kernel/entry.S

Purpose: implements Nios II exception, interrupt, syscall, signal-return, context-switch, and kuser helper
assembly entry paths.

Important APIs/types/functions: entry points: `inthandler`, `handle_trap`, `handle_system_call`, `ret_from_interrupt`, `sys_clone`,
`__sys_clone3`, `sys_rt_sigreturn`, `resume`, `ret_from_fork`, `ret_from_kernel_thread`; prototypes:
`Copyright`.

Control flow: Exceptions enter through `inthandler`, save pt_regs, clear exception-mode state, dispatch through
exception/trap tables, run syscalls or C exception handlers, process return-to-user work, and
finally restore registers with `eret`.

State and persistence: State includes saved exception frames, thread_info flags, interrupt enable masks, current
task/thread pointers, kernel stacks, restart state, and architecture control registers.

Dependencies and integration points: Dependencies include `linux/sys.h`, `linux/linkage.h`, `asm/asm-offsets.h`, `asm/asm-macros.h`,
`asm/thread_info.h`, `asm/errno.h`, `asm/setup.h`, `asm/entry.h`, `asm/unistd.h`, `asm/processor.h`.
Integration points include generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree,
syscall, and cache/TLB subsystems plus Nios II control-register assembly. This source is part of the
Nios II architecture port under the vendored ceph-client kernel tree.

Risks: Risks include register-frame layout mismatches, incorrect syscall restart/error translation, broken
debugger or signal ABI, recursive exceptions, and returning to userspace with inconsistent status
bits.

Test signals: Test signals are syscall ABI tests, strace/ptrace, signal delivery and sigreturn tests, KGDB
breakpoint handling, interrupt/preemption stress, illegal/alignment exception tests, and user/kernel
register dump sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/entry.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/head.S -->
# sources/distributed-fs/ceph-client/arch/nios2/kernel/head.S

Purpose: contains the Nios II reset entry, cache initialization, kernel relocation, BSS clearing, fast TLB
miss hook, and transition into start_kernel.

Important APIs/types/functions: entry points: `_start`, `exception_handler_hook`, `fast_handler`, `fast_handler_end`.

Control flow: Boot starts at `_start`, disables interrupts, initializes instruction/data caches, relocates the
kernel image when needed, clears BSS, records current_thread, preserves boot arguments, and calls
`start_kernel`; the fast handler performs direct TLB refill from `pgd_current`.

State and persistence: State includes saved exception frames, thread_info flags, interrupt enable masks, current
task/thread pointers, kernel stacks, restart state, and architecture control registers.

Dependencies and integration points: Dependencies include `linux/init.h`, `linux/linkage.h`, `asm/thread_info.h`, `asm/processor.h`,
`asm/cache.h`, `asm/page.h`, `asm/asm-offsets.h`, `asm/asm-macros.h`. Integration points include
generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB
subsystems plus Nios II control-register assembly. This source is part of the Nios II architecture
port under the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/head.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/insnemu.S -->
# sources/distributed-fs/ceph-client/arch/nios2/kernel/insnemu.S

Purpose: emulates unsupported Nios II multiply and divide instruction forms by decoding the trapped
instruction and updating the saved register frame.

Important APIs/types/functions: entry points: `instruction_trap`.

Control flow: The illegal-instruction trap restores the interrupted register set, decodes the trapped instruction
word, emulates division or multiplication variants in software, stores the result into the saved
frame, and returns with the original state restored.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/linkage.h`, `asm/entry.h`. Integration points include generic Linux MM,
irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II
control-register assembly. This source is part of the Nios II architecture port under the vendored
ceph-client kernel tree.

Risks: Risks include register-frame layout mismatches, incorrect syscall restart/error translation, broken
debugger or signal ABI, recursive exceptions, and returning to userspace with inconsistent status
bits.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/insnemu.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/irq.c -->
# sources/distributed-fs/ceph-client/arch/nios2/kernel/irq.c

Purpose: initializes the Nios II IRQ domain and irq_chip, maintains the ienable mask, and dispatches hardware
interrupt vectors from assembly entry.

Important APIs/types/functions: functions: `do_IRQ`, `chip_unmask`, `chip_mask`, `irq_map`, `init_IRQ`; prototypes: `irq_enter`,
`BUG_ON`; types: `pt_regs`, `irq_domain`, `device_node`.

Control flow: Generic kernel code calls the exported architecture hooks during boot, process management, fault
handling, cache/TLB maintenance, module loading, or platform probing; the file performs the
architecture-specific register and memory operations then returns to the generic subsystem.

State and persistence: State includes saved exception frames, thread_info flags, interrupt enable masks, current
task/thread pointers, kernel stacks, restart state, and architecture control registers.

Dependencies and integration points: Dependencies include `linux/init.h`, `linux/interrupt.h`, `linux/irqdomain.h`, `linux/of.h`.
Integration points include generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree,
syscall, and cache/TLB subsystems plus Nios II control-register assembly. This source is part of the
Nios II architecture port under the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/kgdb.c -->
# sources/distributed-fs/ceph-client/arch/nios2/kernel/kgdb.c

Purpose: maps Nios II pt_regs into KGDB register packets, handles breakpoint exceptions, and wires
architecture KGDB operations into the generic debugger core.

Important APIs/types/functions: functions: `dbg_set_reg`, `sleeping_thread_to_gdb_regs`, `kgdb_arch_set_pc`,
`kgdb_arch_handle_exception`, `kgdb_breakpoint_c`, `kgdb_arch_init`, `kgdb_arch_exit`; prototypes:
`kgdb_handle_exception`; types: `dbg_reg_def_t`, `pt_regs`.

Control flow: Generic kernel code calls the exported architecture hooks during boot, process management, fault
handling, cache/TLB maintenance, module loading, or platform probing; the file performs the
architecture-specific register and memory operations then returns to the generic subsystem.

State and persistence: State is stored in saved pt_regs/switch_stack frames, user signal frames, debugger register packets,
thread flags, and ptrace-visible register sets.

Dependencies and integration points: Dependencies include `linux/ptrace.h`, `linux/kgdb.h`, `linux/kdebug.h`, `linux/io.h`. Integration
points include generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and
cache/TLB subsystems plus Nios II control-register assembly. This source is part of the Nios II
architecture port under the vendored ceph-client kernel tree.

Risks: Risks include register-frame layout mismatches, incorrect syscall restart/error translation, broken
debugger or signal ABI, recursive exceptions, and returning to userspace with inconsistent status
bits.

Test signals: Test signals are syscall ABI tests, strace/ptrace, signal delivery and sigreturn tests, KGDB
breakpoint handling, interrupt/preemption stress, illegal/alignment exception tests, and user/kernel
register dump sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/kgdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/misaligned.c -->
# sources/distributed-fs/ceph-client/arch/nios2/kernel/misaligned.c

Purpose: emulates or reports misaligned Nios II data accesses by decoding instruction fields, reading/writing
saved registers, and applying unaligned load/store behavior.

Important APIs/types/functions: functions: `get_reg_val`, `put_reg_val`, `handle_unaligned_c`, `instruction`,
`misaligned_calc_reg_offsets`, `misaligned_init`; prototypes: `put_reg_val`, `pr_err`,
`misaligned_calc_reg_offsets`; macros: `INST_LDHU`, `INST_STH`, `INST_LDH`, `INST_STW`, `INST_LDW`,
`UM_WARN`, `UM_FIXUP`, `UM_SIGNAL`, `KM_WARN`.

Control flow: Generic kernel code calls the exported architecture hooks during boot, process management, fault
handling, cache/TLB maintenance, module loading, or platform probing; the file performs the
architecture-specific register and memory operations then returns to the generic subsystem.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/errno.h`, `linux/string.h`, `linux/proc_fs.h`, `linux/init.h`,
`linux/sched.h`, `linux/uaccess.h`, `linux/seq_file.h`, `asm/traps.h`, `linux/unaligned.h`.
Integration points include generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree,
syscall, and cache/TLB subsystems plus Nios II control-register assembly. This source is part of the
Nios II architecture port under the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/misaligned.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/module.c -->
# sources/distributed-fs/ceph-client/arch/nios2/kernel/module.c

Purpose: applies Nios II ELF module relocations, validates relocation ranges, and flushes module text after
finalization.

Important APIs/types/functions: functions: `Copyright`, `module_finalize`; prototypes: `pr_debug`, `pr_err`; types: `module`.

Control flow: Generic kernel code calls the exported architecture hooks during boot, process management, fault
handling, cache/TLB maintenance, module loading, or platform probing; the file performs the
architecture-specific register and memory operations then returns to the generic subsystem.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/moduleloader.h`, `linux/elf.h`, `linux/mm.h`, `linux/slab.h`,
`linux/fs.h`, `linux/string.h`, `linux/kernel.h`, `asm/cacheflush.h`. Integration points include
generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB
subsystems plus Nios II control-register assembly. This source is part of the Nios II architecture
port under the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/nios2_ksyms.c -->
# sources/distributed-fs/ceph-client/arch/nios2/kernel/nios2_ksyms.c

Purpose: exports Nios II low-level library and cache functions required by loadable modules.

Important APIs/types/functions: prototypes: `Copyright`; macros: `DECLARE_EXPORT(name)`; exports: `memcpy`, `memset`, `memmove`,
`flush_icache_range`, `name`.

Control flow: Generic kernel code calls the exported architecture hooks during boot, process management, fault
handling, cache/TLB maintenance, module loading, or platform probing; the file performs the
architecture-specific register and memory operations then returns to the generic subsystem.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/export.h`, `linux/string.h`, `linux/pgtable.h`, `asm/cacheflush.h`.
Integration points include generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree,
syscall, and cache/TLB subsystems plus Nios II control-register assembly. This source is part of the
Nios II architecture port under the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/nios2_ksyms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/process.c -->
# sources/distributed-fs/ceph-client/arch/nios2/kernel/process.c

Purpose: implements idle, restart/halt/poweroff, register dumps, fork thread setup, kernel thread setup,
wait-channel lookup, start_thread, and clone wrapper glue.

Important APIs/types/functions: functions: `arch_cpu_idle`, `machine_restart`, `machine_halt`, `machine_power_off`, `show_regs`,
`flush_thread`, `copy_thread`, `dump`, `__get_wchan`, `mode`, `nios2_clone`; prototypes:
`Copyright`, `__volatile__`, `pr_notice`, `memset`, `pr_emerg`, `kernel_clone`; types: `pt_regs`,
`switch_stack`, `kernel_clone_args`; exports: `pm_power_off`.

Control flow: Generic kernel code calls the exported architecture hooks during boot, process management, fault
handling, cache/TLB maintenance, module loading, or platform probing; the file performs the
architecture-specific register and memory operations then returns to the generic subsystem.

State and persistence: State includes saved exception frames, thread_info flags, interrupt enable masks, current
task/thread pointers, kernel stacks, restart state, and architecture control registers.

Dependencies and integration points: Dependencies include `linux/export.h`, `linux/sched.h`, `linux/sched/debug.h`, `linux/sched/task.h`,
`linux/sched/task_stack.h`, `linux/mm_types.h`, `linux/tick.h`, `linux/uaccess.h`, `asm/unistd.h`,
`asm/traps.h`, `asm/cpuinfo.h`. Integration points include generic Linux MM, irq, signal, ptrace,
module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II control-register
assembly. This source is part of the Nios II architecture port under the vendored ceph-client kernel
tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/process.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/prom.c -->
# sources/distributed-fs/ceph-client/arch/nios2/kernel/prom.c

Purpose: performs early devicetree initialization for Nios II from the bootloader-provided blob.

Important APIs/types/functions: functions: `Copyright`; prototypes: `early_init_dt_scan`.

Control flow: Generic kernel code calls the exported architecture hooks during boot, process management, fault
handling, cache/TLB maintenance, module loading, or platform probing; the file performs the
architecture-specific register and memory operations then returns to the generic subsystem.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/init.h`, `linux/types.h`, `linux/memblock.h`, `linux/of.h`,
`linux/of_fdt.h`, `linux/io.h`, `asm/sections.h`. Integration points include generic Linux MM, irq,
signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II
control-register assembly. This source is part of the Nios II architecture port under the vendored
ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/prom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/ptrace.c -->
# sources/distributed-fs/ceph-client/arch/nios2/kernel/ptrace.c

Purpose: implements Nios II user regsets, ptrace architecture hooks, and syscall trace enter/exit behavior.

Important APIs/types/functions: functions: `Copyright`, `genregs_set`, `ptrace_disable`, `arch_ptrace`, `do_syscall_trace_enter`,
`do_syscall_trace_exit`; prototypes: `membuf_zero`, `user_regset_copyin_ignore`, `ptrace_request`,
`ptrace_report_syscall_exit`; types: `membuf`, `pt_regs`; enums: `nios2_regset`; macros:
`REG_IGNORE_RANGE(START, END)`, `REG_IN_ONE(PTR, LOC)`, `REG_IN_RANGE(PTR, START, END)`.

Control flow: Generic kernel code calls the exported architecture hooks during boot, process management, fault
handling, cache/TLB maintenance, module loading, or platform probing; the file performs the
architecture-specific register and memory operations then returns to the generic subsystem.

State and persistence: State is stored in saved pt_regs/switch_stack frames, user signal frames, debugger register packets,
thread flags, and ptrace-visible register sets.

Dependencies and integration points: Dependencies include `linux/elf.h`, `linux/errno.h`, `linux/kernel.h`, `linux/mm.h`,
`linux/ptrace.h`, `linux/regset.h`, `linux/sched.h`, `linux/sched/task_stack.h`, `linux/uaccess.h`,
`linux/user.h`. Integration points include generic Linux MM, irq, signal, ptrace, module,
timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II control-register assembly.
This source is part of the Nios II architecture port under the vendored ceph-client kernel tree.

Risks: Risks include register-frame layout mismatches, incorrect syscall restart/error translation, broken
debugger or signal ABI, recursive exceptions, and returning to userspace with inconsistent status
bits.

Test signals: Test signals are syscall ABI tests, strace/ptrace, signal delivery and sigreturn tests, KGDB
breakpoint handling, interrupt/preemption stress, illegal/alignment exception tests, and user/kernel
register dump sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/ptrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/setup.c -->
# sources/distributed-fs/ceph-client/arch/nios2/kernel/setup.c

Purpose: handles early boot argument capture, exception-vector copying, fast TLB miss handler installation,
memory bounds discovery, and setup_arch.

Important APIs/types/functions: functions: `copy_exception_handler`, `copy_fast_tlb_miss_handler`, `nios2_boot_init`, `find_limits`,
`adjust_lowmem_bounds`, `for_each_mem_range`, `setup_arch`; prototypes: `Copyright`, `__volatile__`,
`strscpy`, `early_init_devtree`, `memblock_set_current_limit`, `pr_debug`, `memblock_reserve`,
`early_init_fdt_reserve_self`; exports: `memory_start`, `memory_end`.

Control flow: Generic kernel code calls the exported architecture hooks during boot, process management, fault
handling, cache/TLB maintenance, module loading, or platform probing; the file performs the
architecture-specific register and memory operations then returns to the generic subsystem.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/export.h`, `linux/kernel.h`, `linux/mm.h`, `linux/sched.h`,
`linux/sched/task.h`, `linux/console.h`, `linux/memblock.h`, `linux/initrd.h`, `linux/of_fdt.h`,
`asm/mmu_context.h`, `asm/sections.h`, `asm/setup.h`, and 1 more. Integration points include generic
Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems
plus Nios II control-register assembly. This source is part of the Nios II architecture port under
the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/signal.c -->
# sources/distributed-fs/ceph-client/arch/nios2/kernel/signal.c

Purpose: constructs and restores Nios II rt signal frames, restarts interrupted syscalls, and handles return-
to-user signal/resume work.

Important APIs/types/functions: functions: `rt_restore_ucontext`, `do_rt_sigreturn`, `rt_setup_ucontext`, `setup_rt_frame`,
`handle_signal`, `do_signal`, `do_notify_resume`; prototypes: `signal_setup_done`, `handle_signal`,
`resume_user_mode_work`; types: `rt_sigframe`, `siginfo`, `ucontext`, `switch_stack`, `pt_regs`,
`ksignal`; macros: `_BLOCKABLE`.

Control flow: Signal delivery builds a rt frame on the user stack, saves register and sigmask state, points
execution at the handler/trampoline, and sigreturn validates/restores the ucontext before returning
through the syscall epilogue.

State and persistence: State is stored in saved pt_regs/switch_stack frames, user signal frames, debugger register packets,
thread flags, and ptrace-visible register sets.

Dependencies and integration points: Dependencies include `linux/signal.h`, `linux/errno.h`, `linux/ptrace.h`, `linux/uaccess.h`,
`linux/unistd.h`, `linux/personality.h`, `linux/resume_user_mode.h`, `asm/ucontext.h`,
`asm/cacheflush.h`. Integration points include generic Linux MM, irq, signal, ptrace, module,
timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II control-register assembly.
This source is part of the Nios II architecture port under the vendored ceph-client kernel tree.

Risks: Risks include register-frame layout mismatches, incorrect syscall restart/error translation, broken
debugger or signal ABI, recursive exceptions, and returning to userspace with inconsistent status
bits.

Test signals: Test signals are syscall ABI tests, strace/ptrace, signal delivery and sigreturn tests, KGDB
breakpoint handling, interrupt/preemption stress, illegal/alignment exception tests, and user/kernel
register dump sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/sys_nios2.c -->
# sources/distributed-fs/ceph-client/arch/nios2/kernel/sys_nios2.c

Purpose: implements Nios II cacheflush and getpagesize syscalls.

Important APIs/types/functions: functions: `Copyright`, `sys_getpagesize`; prototypes: `mmap_read_unlock`, `flush_cache_range`;
types: `vm_area_struct`, `mm_struct`.

Control flow: Generic kernel code calls the exported architecture hooks during boot, process management, fault
handling, cache/TLB maintenance, module loading, or platform probing; the file performs the
architecture-specific register and memory operations then returns to the generic subsystem.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/export.h`, `linux/file.h`, `linux/fs.h`, `linux/slab.h`,
`linux/syscalls.h`, `asm/cacheflush.h`, `asm/traps.h`. Integration points include generic Linux MM,
irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II
control-register assembly. This source is part of the Nios II architecture port under the vendored
ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/sys_nios2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/syscall_table.c -->
# sources/distributed-fs/ceph-client/arch/nios2/kernel/syscall_table.c

Purpose: defines the Nios II syscall dispatch table from generated syscall table macros.

Important APIs/types/functions: macros: `__SYSCALL(nr, call)`, `__SYSCALL_WITH_COMPAT(nr, native, compat)`, `sys_mmap2`,
`sys_clone3`.

Control flow: Generic kernel code calls the exported architecture hooks during boot, process management, fault
handling, cache/TLB maintenance, module loading, or platform probing; the file performs the
architecture-specific register and memory operations then returns to the generic subsystem.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/syscalls.h`, `linux/signal.h`, `linux/unistd.h`, `asm/syscalls.h`,
`asm/syscall_table_32.h`. Integration points include generic Linux MM, irq, signal, ptrace, module,
timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II control-register assembly.
This source is part of the Nios II architecture port under the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are syscall ABI tests, strace/ptrace, signal delivery and sigreturn tests, KGDB
breakpoint handling, interrupt/preemption stress, illegal/alignment exception tests, and user/kernel
register dump sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/syscall_table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/time.c -->
# sources/distributed-fs/ceph-client/arch/nios2/kernel/time.c

Purpose: drives Nios II timer clocksource and clockevent registration from devicetree timer nodes and exports
get_cycles.

Important APIs/types/functions: functions: `to_nios2_clkevent`, `to_nios2_clksource`, `timer_readw`, `timer_writew`,
`read_timersnapshot`, `nios2_timer_read`, `get_cycles`, `nios2_timer_start`, `nios2_timer_stop`,
`nios2_timer_config`, `nios2_timer_set_next_event`, `nios2_timer_shutdown`, and 9 more; prototypes:
`container_of`, `readw`, `timer_writew`, `local_irq_save`, `nios2_timer_read`, `nios2_timer_config`,
`nios2_timer_stop`, `nios2_timer_start`, `pr_crit`, `clockevents_config_and_register`,
`for_each_compatible_node`; types: `nios2_timer`, `nios2_clockevent_dev`, `clock_event_device`,
`nios2_clocksource`, `clocksource`, `device_node`; macros: `ALTR_TIMER_COMPATIBLE`,
`ALTERA_TIMER_STATUS_REG`, `ALTERA_TIMER_CONTROL_REG`, `ALTERA_TIMER_PERIODL_REG`,
`ALTERA_TIMER_PERIODH_REG`, `ALTERA_TIMER_SNAPL_REG`, `ALTERA_TIMER_SNAPH_REG`,
`ALTERA_TIMER_CONTROL_ITO_MSK`, `ALTERA_TIMER_CONTROL_CONT_MSK`, `ALTERA_TIMER_CONTROL_START_MSK`,
`ALTERA_TIMER_CONTROL_STOP_MSK`; exports: `get_cycles`.

Control flow: Generic kernel code calls the exported architecture hooks during boot, process management, fault
handling, cache/TLB maintenance, module loading, or platform probing; the file performs the
architecture-specific register and memory operations then returns to the generic subsystem.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/export.h`, `linux/interrupt.h`, `linux/clockchips.h`,
`linux/clocksource.h`, `linux/delay.h`, `linux/of.h`, `linux/of_address.h`, `linux/of_irq.h`,
`linux/io.h`, `linux/slab.h`. Integration points include generic Linux MM, irq, signal, ptrace,
module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II control-register
assembly. This source is part of the Nios II architecture port under the vendored ceph-client kernel
tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/traps.c -->
# sources/distributed-fs/ceph-client/arch/nios2/kernel/traps.c

Purpose: implements Nios II C trap handlers for breakpoints, unaligned access, illegal/supervisor/division
exceptions, unhandled exceptions, and stack/register display.

Important APIs/types/functions: functions: `_send_sig`, `die`, `_exception`, `show_stack`, `breakpoint_c`, `handle_unaligned_c`,
`handle_illegal_c`, `handle_supervisor_instr`, `handle_diverror_c`, `unhandled_exception`,
`handle_trap_1_c`, `handle_trap_2_c`, and 1 more; prototypes: `Copyright`, `make_task_dead`, `die`,
`printk`, `pr_alert`, `_exception`, `pr_emerg`.

Control flow: Generic kernel code calls the exported architecture hooks during boot, process management, fault
handling, cache/TLB maintenance, module loading, or platform probing; the file performs the
architecture-specific register and memory operations then returns to the generic subsystem.

State and persistence: State includes saved exception frames, thread_info flags, interrupt enable masks, current
task/thread pointers, kernel stacks, restart state, and architecture control registers.

Dependencies and integration points: Dependencies include `linux/sched.h`, `linux/sched/debug.h`, `linux/kernel.h`, `linux/signal.h`,
`linux/export.h`, `linux/mm.h`, `linux/ptrace.h`, `asm/traps.h`, `asm/sections.h`,
`linux/uaccess.h`. Integration points include generic Linux MM, irq, signal, ptrace, module,
timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II control-register assembly.
This source is part of the Nios II architecture port under the vendored ceph-client kernel tree.

Risks: Risks include register-frame layout mismatches, incorrect syscall restart/error translation, broken
debugger or signal ABI, recursive exceptions, and returning to userspace with inconsistent status
bits.

Test signals: Test signals are syscall ABI tests, strace/ptrace, signal delivery and sigreturn tests, KGDB
breakpoint handling, interrupt/preemption stress, illegal/alignment exception tests, and user/kernel
register dump sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/traps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/vmlinux.lds.S -->
# sources/distributed-fs/ceph-client/arch/nios2/kernel/vmlinux.lds.S

Purpose: defines the Nios II kernel link layout, sections, init areas, exception tables, BSS, and discard
rules.

Important APIs/types/functions: entry points: `_start`; prototypes: `EXCEPTION_TABLE`.

Control flow: Assembly labels are reached from reset, exception, or linker-defined entry points and transfer into
C helpers after saving the architecture register state.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `asm/page.h`, `asm-generic/vmlinux.lds.h`, `asm/cache.h`, `asm/thread_info.h`.
Integration points include generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree,
syscall, and cache/TLB subsystems plus Nios II control-register assembly. This source is part of the
Nios II architecture port under the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/kernel/vmlinux.lds.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/lib/Makefile -->
# sources/distributed-fs/ceph-client/arch/nios2/lib/Makefile

Purpose: builds the Nios II optimized delay and memory routine objects.

Important APIs/types/functions: Build declarations: `lib-y=delay.o`, `lib-y=memcpy.o`, `lib-y=memmove.o`, `lib-y=memset.o`.

Control flow: The build system reads this file during Kbuild traversal; object lists and targets determine which
architecture sources are compiled or packaged for the selected configuration.

State and persistence: Persistent effects are build artifacts only: selected objects, generated images, DTBs, or exported
headers. Runtime state is created by the compiled code, not by the make fragment itself.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB
subsystems plus Nios II control-register assembly. This source is part of the Nios II architecture
port under the vendored ceph-client kernel tree.

Risks: Risks are missing objects, stale generated-header dependencies, wrong boot target names, or
configuration drift that silently excludes required architecture code.

Test signals: Test signals are architecture defconfig builds, `make ARCH=... headers_install`, boot image
generation, DTB generation, and allmodconfig coverage for selected options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/lib/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/lib/delay.c -->
# sources/distributed-fs/ceph-client/arch/nios2/lib/delay.c

Purpose: implements Nios II busy-wait delay loops and exports delay, udelay, ndelay, and const_udelay
helpers.

Important APIs/types/functions: functions: `__delay`, `__const_udelay`, `__udelay`, `__ndelay`; prototypes: `__delay`; exports:
`__delay`, `__const_udelay`, `__udelay`, `__ndelay`.

Control flow: Generic kernel code calls the exported architecture hooks during boot, process management, fault
handling, cache/TLB maintenance, module loading, or platform probing; the file performs the
architecture-specific register and memory operations then returns to the generic subsystem.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/module.h`, `asm/delay.h`, `asm/param.h`, `asm/processor.h`,
`asm/timex.h`. Integration points include generic Linux MM, irq, signal, ptrace, module,
timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II control-register assembly.
This source is part of the Nios II architecture port under the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/lib/delay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/lib/memcpy.c -->
# sources/distributed-fs/ceph-client/arch/nios2/lib/memcpy.c

Purpose: implements optimized Nios II memcpy paths for aligned and byte copies, plus a memcpyb byte-copy
helper.

Important APIs/types/functions: functions: `_wordcopy_fwd_aligned`, `_wordcopy_fwd_dest_aligned`; prototypes:
`_wordcopy_fwd_aligned`, `BYTE_COPY_FWD`; macros: `op_t`, `OPSIZ`, `reg_char`, `MERGE(w0, sh_1, w1,
sh_2)`, `BYTE_COPY_FWD(dst_bp, src_bp, nbytes)`, `WORD_COPY_FWD(dst_bp, src_bp, nbytes_left,
nbytes)`, `OP_T_THRES`.

Control flow: Generic kernel code calls the exported architecture hooks during boot, process management, fault
handling, cache/TLB maintenance, module loading, or platform probing; the file performs the
architecture-specific register and memory operations then returns to the generic subsystem.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/types.h`. Integration points include generic Linux MM, irq, signal,
ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II control-
register assembly. This source is part of the Nios II architecture port under the vendored ceph-
client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/lib/memcpy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/lib/memmove.c -->
# sources/distributed-fs/ceph-client/arch/nios2/lib/memmove.c

Purpose: implements overlap-safe Nios II memory movement by copying forward or backward as needed.

Important APIs/types/functions: functions: `Copyright`.

Control flow: Generic kernel code calls the exported architecture hooks during boot, process management, fault
handling, cache/TLB maintenance, module loading, or platform probing; the file performs the
architecture-specific register and memory operations then returns to the generic subsystem.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/types.h`, `linux/string.h`. Integration points include generic Linux MM,
irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II
control-register assembly. This source is part of the Nios II architecture port under the vendored
ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/lib/memmove.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/lib/memset.c -->
# sources/distributed-fs/ceph-client/arch/nios2/lib/memset.c

Purpose: implements Nios II memset with byte writes over the requested range.

Important APIs/types/functions: functions: `Copyright`; prototypes: `__volatile__`.

Control flow: Generic kernel code calls the exported architecture hooks during boot, process management, fault
handling, cache/TLB maintenance, module loading, or platform probing; the file performs the
architecture-specific register and memory operations then returns to the generic subsystem.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/types.h`, `linux/string.h`. Integration points include generic Linux MM,
irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II
control-register assembly. This source is part of the Nios II architecture port under the vendored
ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/lib/memset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/mm/Makefile -->
# sources/distributed-fs/ceph-client/arch/nios2/mm/Makefile

Purpose: selects the Nios II MM objects for cache, init, fault, ioremap, extable, TLB, DMA mapping, page
tables, user access, and MMU contexts.

Important APIs/types/functions: Build declarations: `obj-y=cacheflush.o`, `obj-y=dma-mapping.o`, `obj-y=extable.o`, `obj-y=fault.o`,
`obj-y=init.o`, `obj-y=ioremap.o`, `obj-y=mmu_context.o`, `obj-y=pgtable.o`, `obj-y=tlb.o`,
`obj-y=uaccess.o`.

Control flow: The build system reads this file during Kbuild traversal; object lists and targets determine which
architecture sources are compiled or packaged for the selected configuration.

State and persistence: Persistent effects are build artifacts only: selected objects, generated images, DTBs, or exported
headers. Runtime state is created by the compiled code, not by the make fragment itself.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB
subsystems plus Nios II control-register assembly. This source is part of the Nios II architecture
port under the vendored ceph-client kernel tree.

Risks: Risks are missing objects, stale generated-header dependencies, wrong boot target names, or
configuration drift that silently excludes required architecture code.

Test signals: Test signals are architecture defconfig builds, `make ARCH=... headers_install`, boot image
generation, DTB generation, and allmodconfig coverage for selected options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/mm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/mm/cacheflush.c -->
# sources/distributed-fs/ceph-client/arch/nios2/mm/cacheflush.c

Purpose: implements Nios II cache maintenance, page/folio D-cache tracking, icache synchronization, and
update_mmu_cache_range TLB reload behavior.

Important APIs/types/functions: functions: `Copyright`, `__invalidate_dcache`, `__flush_icache`, `flush_aliases`, `flush_cache_all`,
`flush_cache_mm`, `flush_cache_dup_mm`, `flush_icache_range`, `flush_dcache_range`,
`invalidate_dcache_range`, `flush_cache_range`, `flush_icache_pages`, and 9 more; prototypes:
`__volatile__`, `__volatile`, `flush_dcache_mmap_lock_irqsave`, `__flush_icache`, `__flush_dcache`,
`clear_bit`, `__flush_dcache_folio`, `flush_aliases`, `set_bit`, `reload_tlb_page`; types:
`mm_struct`, `vm_area_struct`, `address_space`, `folio`, `page`; exports: `flush_dcache_range`,
`invalidate_dcache_range`, `flush_dcache_folio`, `flush_dcache_page`.

Control flow: Cache paths iterate line-sized ranges with Nios II flush/invalidate instructions, mark folios dirty
or clean, synchronize executable mappings, and reload the TLB entry after installing a userspace
PTE.

State and persistence: State is mostly hardware cache contents, folio dirty-cache flags, DMA-visible memory coherency, and
instruction-cache visibility after code or user-page updates.

Dependencies and integration points: Dependencies include `linux/export.h`, `linux/sched.h`, `linux/mm.h`, `linux/fs.h`,
`linux/pagemap.h`, `asm/cacheflush.h`, `asm/cpuinfo.h`. Integration points include generic Linux MM,
irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II
control-register assembly. This source is part of the Nios II architecture port under the vendored
ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are boot under an emulator or board, page-fault and fork/exec stress, mmap/mprotect,
swap where enabled, vmalloc/ioremap users, DMA drivers, module loading, and cache/TLB debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/mm/cacheflush.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/mm/dma-mapping.c -->
# sources/distributed-fs/ceph-client/arch/nios2/mm/dma-mapping.c

Purpose: implements Nios II DMA cache synchronization and coherent DMA preparation by flushing or
invalidating D-cache ranges and returning uncached aliases.

Important APIs/types/functions: functions: `Copyright`, `arch_sync_dma_for_cpu`, `arch_dma_prep_coherent`; prototypes:
`invalidate_dcache_range`, `flush_dcache_range`; enums: `dma_data_direction`.

Control flow: Generic kernel code calls the exported architecture hooks during boot, process management, fault
handling, cache/TLB maintenance, module loading, or platform probing; the file performs the
architecture-specific register and memory operations then returns to the generic subsystem.

State and persistence: State is mostly hardware cache contents, folio dirty-cache flags, DMA-visible memory coherency, and
instruction-cache visibility after code or user-page updates.

Dependencies and integration points: Dependencies include `linux/types.h`, `linux/mm.h`, `linux/string.h`, `linux/dma-mapping.h`,
`linux/io.h`, `linux/cache.h`, `asm/cacheflush.h`. Integration points include generic Linux MM, irq,
signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II
control-register assembly. This source is part of the Nios II architecture port under the vendored
ceph-client kernel tree.

Risks: Risks include stale TLB/cache state, wrong access permissions, corrupted page tables, bad ASID
reuse, kernel faults without fixups, DMA coherency loss, or ABI-visible memory corruption.

Test signals: Test signals are boot under an emulator or board, page-fault and fork/exec stress, mmap/mprotect,
swap where enabled, vmalloc/ioremap users, DMA drivers, module loading, and cache/TLB debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/mm/dma-mapping.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/mm/extable.c -->
# sources/distributed-fs/ceph-client/arch/nios2/mm/extable.c

Purpose: resolves Nios II exception-table fixups by replacing the saved exception address with the fixup
target.

Important APIs/types/functions: functions: `Copyright`.

Control flow: Generic kernel code calls the exported architecture hooks during boot, process management, fault
handling, cache/TLB maintenance, module loading, or platform probing; the file performs the
architecture-specific register and memory operations then returns to the generic subsystem.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/extable.h`, `linux/uaccess.h`. Integration points include generic Linux
MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus
Nios II control-register assembly. This source is part of the Nios II architecture port under the
vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/mm/extable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/mm/fault.c -->
# sources/distributed-fs/ceph-client/arch/nios2/mm/fault.c

Purpose: implements Nios II page-fault handling, including vm_area lookup, access checks, fault dispatch,
signal generation, OOM handling, and kernel fixups.

Important APIs/types/functions: functions: `Copyright`; prototypes: `mmap_read_unlock`, `pr_info`, `_exception`, `pr_alert`; types:
`vm_area_struct`, `task_struct`, `mm_struct`; macros: `EXC_SUPERV_INSN_ACCESS`,
`EXC_SUPERV_DATA_ACCESS`, `EXC_X_PROTECTION_FAULT`, `EXC_R_PROTECTION_FAULT`,
`EXC_W_PROTECTION_FAULT`.

Control flow: The fault handler decodes the faulting address/cause, locates the VMA under mmap_lock, validates
read/write/execute permissions, calls `handle_mm_fault`, and either resumes, signals userspace,
handles OOM, or applies an exception-table fixup.

State and persistence: State includes page tables, PTE permission/cache bits, ASID or context identifiers, TLB entries,
vmalloc/ioremap mappings, swap PTE encodings, and boot-time memory reservations.

Dependencies and integration points: Dependencies include `linux/signal.h`, `linux/sched.h`, `linux/sched/debug.h`, `linux/interrupt.h`,
`linux/kernel.h`, `linux/errno.h`, `linux/string.h`, `linux/types.h`, `linux/ptrace.h`,
`linux/mman.h`, `linux/mm.h`, `linux/extable.h`, and 4 more. Integration points include generic
Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems
plus Nios II control-register assembly. This source is part of the Nios II architecture port under
the vendored ceph-client kernel tree.

Risks: Risks include stale TLB/cache state, wrong access permissions, corrupted page tables, bad ASID
reuse, kernel faults without fixups, DMA coherency loss, or ABI-visible memory corruption.

Test signals: Test signals are boot under an emulator or board, page-fault and fork/exec stress, mmap/mprotect,
swap where enabled, vmalloc/ioremap users, DMA drivers, module loading, and cache/TLB debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/mm/fault.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/mm/init.c -->
# sources/distributed-fs/ceph-client/arch/nios2/mm/init.c

Purpose: initializes Nios II paging, global page-table state, kuser helper mapping, protection_map, and
executable memory allocation ranges.

Important APIs/types/functions: functions: `arch_zone_limits_init`, `paging_init`, `mmu_init`, `alloc_kuser_page`,
`arch_setup_additional_pages`; prototypes: `flush_dcache_range`, `flush_icache_range`,
`mmap_write_lock`; types: `mm_struct`, `vm_area_struct`, `execmem_info`.

Control flow: Generic kernel code calls the exported architecture hooks during boot, process management, fault
handling, cache/TLB maintenance, module loading, or platform probing; the file performs the
architecture-specific register and memory operations then returns to the generic subsystem.

State and persistence: State includes page tables, PTE permission/cache bits, ASID or context identifiers, TLB entries,
vmalloc/ioremap mappings, swap PTE encodings, and boot-time memory reservations.

Dependencies and integration points: Dependencies include `linux/signal.h`, `linux/sched.h`, `linux/kernel.h`, `linux/errno.h`,
`linux/string.h`, `linux/types.h`, `linux/ptrace.h`, `linux/mman.h`, `linux/mm.h`, `linux/init.h`,
`linux/pagemap.h`, `linux/memblock.h`, and 10 more. Integration points include generic Linux MM,
irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II
control-register assembly. This source is part of the Nios II architecture port under the vendored
ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/mm/init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/mm/ioremap.c -->
# sources/distributed-fs/ceph-client/arch/nios2/mm/ioremap.c

Purpose: maps physical MMIO ranges into Nios II vmalloc space, remaps PTEs as noncached, and tears mappings
down with iounmap.

Important APIs/types/functions: functions: `Copyright`, `remap_area_pmd`, `remap_area_pages`, `iounmap`; prototypes: `BUG`,
`pr_err`, `set_pte`, `return`, `vunmap`; types: `vm_struct`, `page`; macros:
`IS_MAPPABLE_UNCACHEABLE(addr)`; exports: `ioremap`, `iounmap`.

Control flow: Generic kernel code calls the exported architecture hooks during boot, process management, fault
handling, cache/TLB maintenance, module loading, or platform probing; the file performs the
architecture-specific register and memory operations then returns to the generic subsystem.

State and persistence: State includes page tables, PTE permission/cache bits, ASID or context identifiers, TLB entries,
vmalloc/ioremap mappings, swap PTE encodings, and boot-time memory reservations.

Dependencies and integration points: Dependencies include `linux/export.h`, `linux/sched.h`, `linux/mm.h`, `linux/slab.h`,
`linux/vmalloc.h`, `linux/io.h`, `asm/cacheflush.h`, `asm/tlbflush.h`. Integration points include
generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB
subsystems plus Nios II control-register assembly. This source is part of the Nios II architecture
port under the vendored ceph-client kernel tree.

Risks: Risks include stale TLB/cache state, wrong access permissions, corrupted page tables, bad ASID
reuse, kernel faults without fixups, DMA coherency loss, or ABI-visible memory corruption.

Test signals: Test signals are boot under an emulator or board, page-fault and fork/exec stress, mmap/mprotect,
swap where enabled, vmalloc/ioremap users, DMA drivers, module loading, and cache/TLB debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/mm/ioremap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/mm/mmu_context.c -->
# sources/distributed-fs/ceph-client/arch/nios2/mm/mmu_context.c

Purpose: allocates and recycles Nios II MMU contexts, switches page-directory roots, flushes stale ASIDs, and
programs hardware TLB PIDs.

Important APIs/types/functions: functions: `mmu_context_init`, `context`, `get_new_context`, `switch_mm`, `activate_mm`,
`get_pid_from_context`; prototypes: `flush_cache_all`, `local_irq_save`, `CTX_PID`; types:
`task_struct`; macros: `PID_SHIFT`, `PID_BITS`, `PID_MASK`, `VERSION_BITS`, `VERSION_SHIFT`,
`VERSION_MASK`, `CTX_VERSION(c)`, `CTX_PID(c)`, `FIRST_CTX`.

Control flow: Context switching allocates a new ASID when an mm lacks one, flushes all TLB entries on wrap,
records `pgd_current`, and writes the hardware PID before returning to the new address space.

State and persistence: State includes page tables, PTE permission/cache bits, ASID or context identifiers, TLB entries,
vmalloc/ioremap mappings, swap PTE encodings, and boot-time memory reservations.

Dependencies and integration points: Dependencies include `linux/mm.h`, `asm/cpuinfo.h`, `asm/mmu_context.h`, `asm/tlb.h`. Integration
points include generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and
cache/TLB subsystems plus Nios II control-register assembly. This source is part of the Nios II
architecture port under the vendored ceph-client kernel tree.

Risks: Risks include stale TLB/cache state, wrong access permissions, corrupted page tables, bad ASID
reuse, kernel faults without fixups, DMA coherency loss, or ABI-visible memory corruption.

Test signals: Test signals are boot under an emulator or board, page-fault and fork/exec stress, mmap/mprotect,
swap where enabled, vmalloc/ioremap users, DMA drivers, module loading, and cache/TLB debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/mm/mmu_context.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/mm/pgtable.c -->
# sources/distributed-fs/ceph-client/arch/nios2/mm/pgtable.c

Purpose: initializes Nios II PGDs to the invalid PTE table and allocates/copies kernel PGD entries for new
address spaces.

Important APIs/types/functions: functions: `Copyright`, `pagetable_init`; prototypes: `pgd_init`.

Control flow: Generic kernel code calls the exported architecture hooks during boot, process management, fault
handling, cache/TLB maintenance, module loading, or platform probing; the file performs the
architecture-specific register and memory operations then returns to the generic subsystem.

State and persistence: State includes page tables, PTE permission/cache bits, ASID or context identifiers, TLB entries,
vmalloc/ioremap mappings, swap PTE encodings, and boot-time memory reservations.

Dependencies and integration points: Dependencies include `linux/mm.h`, `linux/sched.h`, `asm/cpuinfo.h`, `asm/pgalloc.h`. Integration
points include generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and
cache/TLB subsystems plus Nios II control-register assembly. This source is part of the Nios II
architecture port under the vendored ceph-client kernel tree.

Risks: Risks include stale TLB/cache state, wrong access permissions, corrupted page tables, bad ASID
reuse, kernel faults without fixups, DMA coherency loss, or ABI-visible memory corruption.

Test signals: Test signals are boot under an emulator or board, page-fault and fork/exec stress, mmap/mprotect,
swap where enabled, vmalloc/ioremap users, DMA drivers, module loading, and cache/TLB debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/mm/pgtable.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/mm/tlb.c -->
# sources/distributed-fs/ceph-client/arch/nios2/mm/tlb.c

Purpose: implements Nios II TLB replacement, PID-tagged flush/reload operations, kernel flushes, diagnostic
dumping, and MMU PID programming.

Important APIs/types/functions: functions: `Copyright`, `pteaddr_invalid`, `replace_tlb_one_pid`, `flush_tlb_one_pid`,
`reload_tlb_one_pid`, `flush_tlb_range`, `reload_tlb_page`, `flush_tlb_one`,
`flush_tlb_kernel_range`, `dump_tlb_line`, `dump_tlb`, `flush_tlb_pid`, and 3 more; prototypes:
`WRCTL`, `replace_tlb_one_pid`, `flush_tlb_one_pid`, `reload_tlb_one_pid`, `pr_debug`,
`flush_tlb_one`, `flush_tlb_pid`, `memset`; macros: `TLB_INDEX_MASK`.

Control flow: TLB helpers compute PID-tagged probe addresses, invalidate or reload single pages/ranges by writing
Nios II control registers, flush all ways when contexts wrap, and preserve the current PID around
kernel/global operations.

State and persistence: State includes page tables, PTE permission/cache bits, ASID or context identifiers, TLB entries,
vmalloc/ioremap mappings, swap PTE encodings, and boot-time memory reservations.

Dependencies and integration points: Dependencies include `linux/init.h`, `linux/sched.h`, `linux/mm.h`, `linux/pagemap.h`, `asm/tlb.h`,
`asm/mmu_context.h`, `asm/cpuinfo.h`. Integration points include generic Linux MM, irq, signal,
ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus Nios II control-
register assembly. This source is part of the Nios II architecture port under the vendored ceph-
client kernel tree.

Risks: Risks include stale TLB/cache state, wrong access permissions, corrupted page tables, bad ASID
reuse, kernel faults without fixups, DMA coherency loss, or ABI-visible memory corruption.

Test signals: Test signals are boot under an emulator or board, page-fault and fork/exec stress, mmap/mprotect,
swap where enabled, vmalloc/ioremap users, DMA drivers, module loading, and cache/TLB debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/mm/tlb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/mm/uaccess.c -->
# sources/distributed-fs/ceph-client/arch/nios2/mm/uaccess.c

Purpose: implements Nios II raw_copy_from_user and raw_copy_to_user loops with exception-table fixups for
partial user copies.

Important APIs/types/functions: prototypes: `Copyright`; exports: `raw_copy_from_user`, `raw_copy_to_user`.

Control flow: User-copy loops copy bytes/words until completion or a fault; exception-table fixups redirect the
saved PC to return the uncopied byte count instead of oopsing the kernel.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/export.h`, `linux/uaccess.h`. Integration points include generic Linux
MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB subsystems plus
Nios II control-register assembly. This source is part of the Nios II architecture port under the
vendored ceph-client kernel tree.

Risks: Risks include stale TLB/cache state, wrong access permissions, corrupted page tables, bad ASID
reuse, kernel faults without fixups, DMA coherency loss, or ABI-visible memory corruption.

Test signals: Test signals are boot under an emulator or board, page-fault and fork/exec stress, mmap/mprotect,
swap where enabled, vmalloc/ioremap users, DMA drivers, module loading, and cache/TLB debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/mm/uaccess.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/platform/Makefile -->
# sources/distributed-fs/ceph-client/arch/nios2/platform/Makefile

Purpose: adds Nios II platform device initialization objects to the architecture build.

Important APIs/types/functions: Build declarations: `obj-y=platform.o`.

Control flow: The build system reads this file during Kbuild traversal; object lists and targets determine which
architecture sources are compiled or packaged for the selected configuration.

State and persistence: Persistent effects are build artifacts only: selected objects, generated images, DTBs, or exported
headers. Runtime state is created by the compiled code, not by the make fragment itself.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB
subsystems plus Nios II control-register assembly. This source is part of the Nios II architecture
port under the vendored ceph-client kernel tree.

Risks: Risks are missing objects, stale generated-header dependencies, wrong boot target names, or
configuration drift that silently excludes required architecture code.

Test signals: Test signals are architecture defconfig builds, `make ARCH=... headers_install`, boot image
generation, DTB generation, and allmodconfig coverage for selected options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/platform/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/platform/platform.c -->
# sources/distributed-fs/ceph-client/arch/nios2/platform/platform.c

Purpose: registers Nios II platform/SOC devices from devicetree, especially clocks required before normal
device probing.

Important APIs/types/functions: functions: `nios2_soc_device_init`; prototypes: `kfree`, `of_clk_init`; types: `soc_device`,
`soc_device_attribute`.

Control flow: Generic kernel code calls the exported architecture hooks during boot, process management, fault
handling, cache/TLB maintenance, module loading, or platform probing; the file performs the
architecture-specific register and memory operations then returns to the generic subsystem.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/init.h`, `linux/of_address.h`, `linux/of_fdt.h`, `linux/err.h`,
`linux/slab.h`, `linux/sys_soc.h`, `linux/io.h`, `linux/clk-provider.h`. Integration points include
generic Linux MM, irq, signal, ptrace, module, timekeeping, devicetree, syscall, and cache/TLB
subsystems plus Nios II control-register assembly. This source is part of the Nios II architecture
port under the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/nios2/platform/platform.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/Kbuild -->
# sources/distributed-fs/ceph-client/arch/openrisc/Kbuild

Purpose: adds OpenRISC lib, kernel, and mm subdirectories to the architecture build.

Important APIs/types/functions: Build declarations: `obj-y=lib/ kernel/ mm/`.

Control flow: The build system reads this file during Kbuild traversal; object lists and targets determine which
architecture sources are compiled or packaged for the selected configuration.

State and persistence: Persistent effects are build artifacts only: selected objects, generated images, DTBs, or exported
headers. Runtime state is created by the compiled code, not by the make fragment itself.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic asm-generic helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex,
ELF, and Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port under
the vendored ceph-client kernel tree.

Risks: Risks are missing objects, stale generated-header dependencies, wrong boot target names, or
configuration drift that silently excludes required architecture code.

Test signals: Test signals are architecture defconfig builds, `make ARCH=... headers_install`, boot image
generation, DTB generation, and allmodconfig coverage for selected options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/Kconfig -->
# sources/distributed-fs/ceph-client/arch/openrisc/Kconfig

Purpose: declares the OpenRISC architecture Kconfig feature set, CPU class options, optional instruction
availability, SMP/FPU switches, and debugging knobs.

Important APIs/types/functions: Kconfig symbols: `OPENRISC`, `CPU_BIG_ENDIAN`, `MMU`, `GENERIC_HWEIGHT`, `NO_IOPORT_MAP`,
`GENERIC_CSUM`, `STACKTRACE_SUPPORT`, `LOCKDEP_SUPPORT`, `FIX_EARLYCON_MEM`, `OR1K_1200`,
`DCACHE_WRITETHROUGH`, `BUILTIN_DTB_NAME`, `OPENRISC_HAVE_INST_FF1`, `OPENRISC_HAVE_INST_FL1`,
`OPENRISC_HAVE_INST_MUL`, `OPENRISC_HAVE_INST_DIV`, `OPENRISC_HAVE_INST_CMOV`,
`OPENRISC_HAVE_INST_ROR`, `OPENRISC_HAVE_INST_RORI`, `OPENRISC_HAVE_INST_SEXT`, `NR_CPUS`, `SMP`,
`FPU`, `OPENRISC_NO_SPR_SR_DSX`, and 4 more.

Control flow: Kconfig evaluates the architecture menu from top to bottom, enabling baseline OpenRISC capabilities
and exposing CPU feature, instruction, SMP, FPU, command-line, and debug choices to defconfig and
menuconfig users.

State and persistence: Persistent state is the chosen kernel configuration, which changes compiled instruction assumptions,
cache policy, SMP/FPU support, built-in DTB selection, and debug behavior.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic asm-generic helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex,
ELF, and Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port under
the vendored ceph-client kernel tree.

Risks: Risks are selecting instruction features unsupported by the target CPU, inconsistent SMP/FPU/cache
policy, or debug options that change exception behavior.

Test signals: Test signals are architecture defconfig builds, `make ARCH=... headers_install`, boot image
generation, DTB generation, and allmodconfig coverage for selected options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/Makefile -->
# sources/distributed-fs/ceph-client/arch/openrisc/Makefile

Purpose: sets OpenRISC compiler, linker, boot image, dtb, library, and install rules for the architecture
build.

Important APIs/types/functions: Build declarations: `libs-y=$(LIBGCC)`.

Control flow: The build system reads this file during Kbuild traversal; object lists and targets determine which
architecture sources are compiled or packaged for the selected configuration.

State and persistence: Persistent effects are build artifacts only: selected objects, generated images, DTBs, or exported
headers. Runtime state is created by the compiled code, not by the make fragment itself.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic asm-generic helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex,
ELF, and Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port under
the vendored ceph-client kernel tree.

Risks: Risks are missing objects, stale generated-header dependencies, wrong boot target names, or
configuration drift that silently excludes required architecture code.

Test signals: Test signals are architecture defconfig builds, `make ARCH=... headers_install`, boot image
generation, DTB generation, and allmodconfig coverage for selected options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/boot/Makefile -->
# sources/distributed-fs/ceph-client/arch/openrisc/boot/Makefile

Purpose: sets OpenRISC compiler, linker, boot image, dtb, library, and install rules for the architecture
build.

Important APIs/types/functions: Build declarations: none detected.

Control flow: The build system reads this file during Kbuild traversal; object lists and targets determine which
architecture sources are compiled or packaged for the selected configuration.

State and persistence: Persistent effects are build artifacts only: selected objects, generated images, DTBs, or exported
headers. Runtime state is created by the compiled code, not by the make fragment itself.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic asm-generic helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex,
ELF, and Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port under
the vendored ceph-client kernel tree.

Risks: Risks are missing objects, stale generated-header dependencies, wrong boot target names, or
configuration drift that silently excludes required architecture code.

Test signals: Test signals are architecture defconfig builds, `make ARCH=... headers_install`, boot image
generation, DTB generation, and allmodconfig coverage for selected options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/boot/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/boot/dts/Makefile -->
# sources/distributed-fs/ceph-client/arch/openrisc/boot/dts/Makefile

Purpose: sets OpenRISC compiler, linker, boot image, dtb, library, and install rules for the architecture
build.

Important APIs/types/functions: Build declarations: `dtb-y=$(addsuffix .dtb, $(CONFIG_BUILTIN_DTB_NAME))`.

Control flow: The build system reads this file during Kbuild traversal; object lists and targets determine which
architecture sources are compiled or packaged for the selected configuration.

State and persistence: Persistent effects are build artifacts only: selected objects, generated images, DTBs, or exported
headers. Runtime state is created by the compiled code, not by the make fragment itself.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic asm-generic helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex,
ELF, and Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port under
the vendored ceph-client kernel tree.

Risks: Risks are missing objects, stale generated-header dependencies, wrong boot target names, or
configuration drift that silently excludes required architecture code.

Test signals: Test signals are architecture defconfig builds, `make ARCH=... headers_install`, boot image
generation, DTB generation, and allmodconfig coverage for selected options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/boot/dts/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/Kbuild

Purpose: lists generic asm headers and local OpenRISC headers exported or generated for the architecture
include tree.

Important APIs/types/functions: Build declarations: `syscall-y=syscall_table_32.h`, `generic-y=extable.h`, `generic-y=kvm_para.h`,
`generic-y=parport.h`, `generic-y=spinlock_types.h`, `generic-y=spinlock.h`,
`generic-y=qrwlock_types.h`, `generic-y=qrwlock.h`, `generic-y=user.h`.

Control flow: The build system reads this file during Kbuild traversal; object lists and targets determine which
architecture sources are compiled or packaged for the selected configuration.

State and persistence: Persistent effects are build artifacts only: selected objects, generated images, DTBs, or exported
headers. Runtime state is created by the compiled code, not by the make fragment itself.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic asm-generic helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex,
ELF, and Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port under
the vendored ceph-client kernel tree.

Risks: Risks are missing objects, stale generated-header dependencies, wrong boot target names, or
configuration drift that silently excludes required architecture code.

Test signals: Test signals are architecture defconfig builds, `make ARCH=... headers_install`, boot image
generation, DTB generation, and allmodconfig coverage for selected options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/Kbuild -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/asm-offsets.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/asm-offsets.h

Purpose: includes the generated asm-offsets header needed by OpenRISC low-level assembly.

Important APIs/types/functions: The file is declarative and primarily contributes constants or include/export wiring.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `generated/asm-offsets.h`. Integration points include generic asm-generic
helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex, ELF, and
Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port under the
vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/asm-offsets.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/atomic.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/atomic.h

Purpose: implements OpenRISC atomic add/sub/and/or/xor operations and fetch-return variants with load-
linked/store-conditional style assembly.

Important APIs/types/functions: functions: `ATOMIC_OP_RETURN`; prototypes: `__volatile__`; macros: `__ASM_OPENRISC_ATOMIC_H`,
`ATOMIC_OP(op)`, `ATOMIC_OP_RETURN(op)`, `ATOMIC_FETCH_OP(op)`, `arch_atomic_add_return`,
`arch_atomic_sub_return`, `arch_atomic_fetch_add`, `arch_atomic_fetch_sub`, `arch_atomic_fetch_and`,
`arch_atomic_fetch_or`, `arch_atomic_fetch_xor`, `arch_atomic_add`, and 7 more.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/types.h`, `asm/cmpxchg.h`. Integration points include generic asm-
generic helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex, ELF, and
Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port under the
vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/barrier.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/barrier.h

Purpose: defines OpenRISC memory barriers and nop handling before falling back to generic barrier helpers.

Important APIs/types/functions: macros: `__ASM_BARRIER_H`, `mb()`, `nop()`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `asm-generic/barrier.h`. Integration points include generic asm-generic
helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex, ELF, and
Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port under the
vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/barrier.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/bitops.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/bitops.h

Purpose: assembles OpenRISC bit-operation support from local ffs/fls/atomic helpers and generic bitops
components.

Important APIs/types/functions: macros: `__ASM_OPENRISC_BITOPS_H`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/irqflags.h`, `linux/compiler.h`, `asm/barrier.h`, `asm/bitops/__ffs.h`,
`asm-generic/bitops/ffz.h`, `asm/bitops/fls.h`, `asm/bitops/__fls.h`, `asm-generic/bitops/fls64.h`,
`asm-generic/bitops/sched.h`, `asm/bitops/ffs.h`, `asm-generic/bitops/hweight.h`, `asm-
generic/bitops/lock.h`, and 4 more. Integration points include generic asm-generic helpers, OpenRISC
SPR/status register definitions, MM, irqflags, bitops, futex, ELF, and Kbuild/Kconfig
infrastructure. This source is part of the OpenRISC architecture port under the vendored ceph-client
kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/bitops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/bitops/__ffs.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/bitops/__ffs.h

Purpose: implements or selects the OpenRISC `__ffs` bit-operation helper used by generic bitmap, scheduler,
filesystem, and atomic bit APIs.

Important APIs/types/functions: functions: `Copyright`; prototypes: `__asm__`; macros: `__ASM_OPENRISC___FFS_H`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `asm-generic/bitops/__ffs.h`. Integration points include generic asm-generic
helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex, ELF, and
Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port under the
vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/bitops/__ffs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/bitops/__fls.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/bitops/__fls.h

Purpose: implements or selects the OpenRISC `__fls` bit-operation helper used by generic bitmap, scheduler,
filesystem, and atomic bit APIs.

Important APIs/types/functions: functions: `Copyright`; prototypes: `__asm__`; macros: `__ASM_OPENRISC___FLS_H`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `asm-generic/bitops/__fls.h`. Integration points include generic asm-generic
helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex, ELF, and
Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port under the
vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/bitops/__fls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/bitops/atomic.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/bitops/atomic.h

Purpose: implements or selects the OpenRISC `atomic` bit-operation helper used by generic bitmap, scheduler,
filesystem, and atomic bit APIs.

Important APIs/types/functions: functions: `Copyright`, `clear_bit`, `change_bit`, `test_and_set_bit`, `test_and_clear_bit`,
`test_and_change_bit`; prototypes: `__volatile__`; macros: `__ASM_OPENRISC_BITOPS_ATOMIC_H`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic asm-generic helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex,
ELF, and Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port under
the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/bitops/atomic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/bitops/ffs.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/bitops/ffs.h

Purpose: implements or selects the OpenRISC `ffs` bit-operation helper used by generic bitmap, scheduler,
filesystem, and atomic bit APIs.

Important APIs/types/functions: functions: `Copyright`; prototypes: `__asm__`; macros: `__ASM_OPENRISC_FFS_H`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `asm-generic/bitops/ffs.h`. Integration points include generic asm-generic
helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex, ELF, and
Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port under the
vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/bitops/ffs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/bitops/fls.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/bitops/fls.h

Purpose: implements or selects the OpenRISC `fls` bit-operation helper used by generic bitmap, scheduler,
filesystem, and atomic bit APIs.

Important APIs/types/functions: functions: `Copyright`; prototypes: `__asm__`; macros: `__ASM_OPENRISC_FLS_H`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `asm-generic/bitops/fls.h`. Integration points include generic asm-generic
helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex, ELF, and
Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port under the
vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/bitops/fls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/bug.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/bug.h

Purpose: selects generic BUG support and declares the architecture die path.

Important APIs/types/functions: prototypes: `die`; types: `pt_regs`; macros: `__ASM_OPENRISC_BUG_H`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `asm-generic/bug.h`. Integration points include generic asm-generic helpers,
OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex, ELF, and Kbuild/Kconfig
infrastructure. This source is part of the OpenRISC architecture port under the vendored ceph-client
kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/bug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/cache.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/cache.h

Purpose: defines OpenRISC L1 cache alignment constants and read-mostly aliasing for ro_after_init.

Important APIs/types/functions: macros: `__ASM_OPENRISC_CACHE_H`, `__ro_after_init`, `L1_CACHE_BYTES`, `L1_CACHE_SHIFT`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: State is mostly hardware cache contents, folio dirty-cache flags, DMA-visible memory coherency, and
instruction-cache visibility after code or user-page updates.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic asm-generic helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex,
ELF, and Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port under
the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are boot under an emulator or board, page-fault and fork/exec stress, mmap/mprotect,
swap where enabled, vmalloc/ioremap users, DMA drivers, module loading, and cache/TLB debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/cacheflush.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/cacheflush.h

Purpose: declares and wraps OpenRISC D-cache/I-cache page and range flush helpers, including SMP icache
invalidation and folio dirty-cache state.

Important APIs/types/functions: functions: `sync_icache_dcache`, `flush_dcache_folio`, `flush_dcache_page`; prototypes: `Copyright`,
`dcache_page_flush`, `sync_icache_dcache`; macros: `__ASM_CACHEFLUSH_H`, `dcache_page_flush(page)`,
`icache_page_inv(page)`, `local_dcache_block_flush(addr)`, `local_dcache_block_inv(addr)`,
`local_icache_block_inv(addr)`, `PG_dc_clean`, `flush_dcache_folio`,
`ARCH_IMPLEMENTS_FLUSH_DCACHE_PAGE`, `flush_icache_user_page(vma, page, addr, len)`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: State is mostly hardware cache contents, folio dirty-cache flags, DMA-visible memory coherency, and
instruction-cache visibility after code or user-page updates.

Dependencies and integration points: Dependencies include `linux/mm.h`, `asm-generic/cacheflush.h`. Integration points include generic
asm-generic helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex, ELF, and
Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port under the
vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are boot under an emulator or board, page-fault and fork/exec stress, mmap/mprotect,
swap where enabled, vmalloc/ioremap users, DMA drivers, module loading, and cache/TLB debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/cacheflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/cmpxchg.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/cmpxchg.h

Purpose: implements OpenRISC xchg and cmpxchg primitives, including byte/halfword masking around 32-bit
atomic operations.

Important APIs/types/functions: functions: `Copyright`, `xchg_u32`, `cmpxchg_small`, `xchg_small`, `__cmpxchg`, `__arch_xchg`;
prototypes: `__volatile__`, `cmpxchg`, `cmpxchg_small`, `__cmpxchg`,
`__xchg_called_with_bad_pointer`, `xchg_small`, `__arch_xchg`; macros: `__ASM_OPENRISC_CMPXCHG_H`,
`__HAVE_ARCH_CMPXCHG`, `arch_cmpxchg(ptr, o, n)`, `arch_xchg(ptr, with)`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/bits.h`, `linux/compiler.h`, `linux/types.h`. Integration points include
generic asm-generic helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex,
ELF, and Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port under
the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/cmpxchg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/cpuinfo.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/cpuinfo.h

Purpose: defines OpenRISC CPU/cache descriptor structures and exported cpuinfo setup/probing hooks.

Important APIs/types/functions: prototypes: `setup_cpuinfo`; types: `cache_desc`, `cpuinfo_or1k`; macros:
`__ASM_OPENRISC_CPUINFO_H`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `asm/spr.h`, `asm/spr_defs.h`. Integration points include generic asm-generic
helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex, ELF, and
Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port under the
vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/cpuinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/delay.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/delay.h

Purpose: uses generic delay loops with the OpenRISC loops_per_jiffy calibration value.

Important APIs/types/functions: macros: `__ASM_OPENRISC_DELAY_H`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `asm-generic/delay.h`. Integration points include generic asm-generic helpers,
OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex, ELF, and Kbuild/Kconfig
infrastructure. This source is part of the OpenRISC architecture port under the vendored ceph-client
kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/delay.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/elf.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/elf.h

Purpose: defines kernel-side OpenRISC ELF loader/core-dump behavior and register-copy hook.

Important APIs/types/functions: prototypes: `Copyright`; macros: `__ASM_OPENRISC_ELF_H`, `elf_check_arch(x)`, `ELF_ET_DYN_BASE`,
`CORE_DUMP_USE_REGSET`, `ELF_EXEC_PAGESIZE`, `ELF_CORE_COPY_REGS(dest, regs)`, `ELF_HWCAP`,
`ELF_PLATFORM`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/types.h`, `uapi/asm/elf.h`. Integration points include generic asm-
generic helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex, ELF, and
Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port under the
vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/elf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/fixmap.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/fixmap.h

Purpose: defines OpenRISC fixed mapping slots and the __set_fixmap hook used by early ioremap/fixmap users.

Important APIs/types/functions: prototypes: `__set_fixmap`; enums: `fixed_addresses`; macros: `__ASM_OPENRISC_FIXMAP_H`,
`FIXADDR_TOP`, `FIXADDR_SIZE`, `FIXADDR_START`, `FIXMAP_PAGE_IO`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/kernel.h`, `linux/bug.h`, `asm/page.h`, `asm-generic/fixmap.h`.
Integration points include generic asm-generic helpers, OpenRISC SPR/status register definitions,
MM, irqflags, bitops, futex, ELF, and Kbuild/Kconfig infrastructure. This source is part of the
OpenRISC architecture port under the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/fixmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/fpu.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/fpu.h

Purpose: provides save_fpu/restore_fpu hooks, compiling to no-ops unless OpenRISC FPU support is enabled.

Important APIs/types/functions: functions: `save_fpu`, `restore_fpu`; types: `task_struct`; macros: `__ASM_OPENRISC_FPU_H`,
`save_fpu(tsk)`, `restore_fpu(tsk)`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic asm-generic helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex,
ELF, and Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port under
the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/fpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/futex.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/futex.h

Purpose: implements OpenRISC futex atomic operations on user addresses with exception-table recovery.

Important APIs/types/functions: functions: `arch_futex_atomic_op_inuser`, `futex_atomic_cmpxchg_inatomic`; prototypes:
`__volatile__`, `__futex_atomic_op`; macros: `__ASM_OPENRISC_FUTEX_H`, `__futex_atomic_op(insn, ret,
oldval, uaddr, oparg)`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/futex.h`, `linux/uaccess.h`, `asm/errno.h`. Integration points include
generic asm-generic helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex,
ELF, and Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port under
the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/futex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/insn-def.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/insn-def.h

Purpose: defines OpenRISC instruction sizing and the canonical nop encoding used by text patching and jump
labels.

Important APIs/types/functions: macros: `__ASM_OPENRISC_INSN_DEF_H`, `OPENRISC_INSN_SIZE`, `OPENRISC_INSN_NOP`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic asm-generic helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex,
ELF, and Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port under
the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/insn-def.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/io.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/io.h

Purpose: defines OpenRISC MMIO and ioremap policy constants before including generic I/O helpers.

Important APIs/types/functions: macros: `__ASM_OPENRISC_IO_H`, `IO_SPACE_LIMIT`, `HAVE_ARCH_PIO_SIZE`, `PIO_RESERVED`, `PIO_OFFSET`,
`PIO_MASK`, `_PAGE_IOREMAP`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/types.h`, `asm/pgalloc.h`, `asm/pgtable.h`, `asm-generic/io.h`.
Integration points include generic asm-generic helpers, OpenRISC SPR/status register definitions,
MM, irqflags, bitops, futex, ELF, and Kbuild/Kconfig infrastructure. This source is part of the
OpenRISC architecture port under the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/irq.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/irq.h

Purpose: sets the OpenRISC interrupt count and generic IRQ integration constants.

Important APIs/types/functions: macros: `__ASM_OPENRISC_IRQ_H__`, `NR_IRQS`, `NO_IRQ`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `asm-generic/irq.h`. Integration points include generic asm-generic helpers,
OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex, ELF, and Kbuild/Kconfig
infrastructure. This source is part of the OpenRISC architecture port under the vendored ceph-client
kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/irqflags.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/irqflags.h

Purpose: maps OpenRISC interrupt-enable status bits to generic irqflag save/restore operations.

Important APIs/types/functions: macros: `___ASM_OPENRISC_IRQFLAGS_H`, `ARCH_IRQ_DISABLED`, `ARCH_IRQ_ENABLED`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `asm/spr_defs.h`, `asm-generic/irqflags.h`. Integration points include generic
asm-generic helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex, ELF, and
Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port under the
vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/irqflags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/jump_label.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/jump_label.h

Purpose: implements OpenRISC static-branch assembly and jump-table records for runtime branch patching.

Important APIs/types/functions: functions: `Copyright`, `arch_static_branch_jump`; prototypes: `goto`; macros:
`__ASM_OPENRISC_JUMP_LABEL_H`, `HAVE_JUMP_LABEL_BATCH`, `JUMP_LABEL_NOP_SIZE`,
`JUMP_TABLE_ENTRY(key, label)`, `ARCH_STATIC_BRANCH_ASM(key, label)`,
`ARCH_STATIC_BRANCH_JUMP_ASM(key, label)`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `linux/types.h`, `asm/insn-def.h`. Integration points include generic asm-
generic helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex, ELF, and
Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port under the
vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/jump_label.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/linkage.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/linkage.h

Purpose: sets OpenRISC assembly/linkage alignment directives.

Important APIs/types/functions: macros: `__ASM_OPENRISC_LINKAGE_H`, `__ALIGN`, `__ALIGN_STR`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic asm-generic helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex,
ELF, and Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port under
the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/linkage.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/mmu.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/mmu.h

Purpose: defines the OpenRISC mm_context_t type used by address-space switching.

Important APIs/types/functions: typedefs: `mm_context_t`; macros: `__ASM_OPENRISC_MMU_H`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: State includes page tables, PTE permission/cache bits, ASID or context identifiers, TLB entries,
vmalloc/ioremap mappings, swap PTE encodings, and boot-time memory reservations.

Dependencies and integration points: Dependencies are mostly implicit architecture and generic kernel headers. Integration points include
generic asm-generic helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex,
ELF, and Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port under
the vendored ceph-client kernel tree.

Risks: Risks include stale TLB/cache state, wrong access permissions, corrupted page tables, bad ASID
reuse, kernel faults without fixups, DMA coherency loss, or ABI-visible memory corruption.

Test signals: Test signals are boot under an emulator or board, page-fault and fork/exec stress, mmap/mprotect,
swap where enabled, vmalloc/ioremap users, DMA drivers, module loading, and cache/TLB debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/mmu_context.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/mmu_context.h

Purpose: declares OpenRISC MMU context creation, destruction, activation, switch_mm, and current_pgd
integration.

Important APIs/types/functions: prototypes: `Copyright`; types: `task_struct`; macros: `__ASM_OPENRISC_MMU_CONTEXT_H`,
`init_new_context`, `destroy_context`, `activate_mm(prev, next)`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: State includes page tables, PTE permission/cache bits, ASID or context identifiers, TLB entries,
vmalloc/ioremap mappings, swap PTE encodings, and boot-time memory reservations.

Dependencies and integration points: Dependencies include `asm-generic/mm_hooks.h`, `asm-generic/mmu_context.h`. Integration points
include generic asm-generic helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops,
futex, ELF, and Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port
under the vendored ceph-client kernel tree.

Risks: Risks include stale TLB/cache state, wrong access permissions, corrupted page tables, bad ASID
reuse, kernel faults without fixups, DMA coherency loss, or ABI-visible memory corruption.

Test signals: Test signals are boot under an emulator or board, page-fault and fork/exec stress, mmap/mprotect,
swap where enabled, vmalloc/ioremap users, DMA drivers, module loading, and cache/TLB debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/mmu_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/page.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/page.h

Purpose: defines OpenRISC page types, PAGE_OFFSET, virtual/physical conversion, and pfn/page helpers.

Important APIs/types/functions: functions: `virt_to_pfn`; typedefs: `pgtable_t`; macros: `__ASM_OPENRISC_PAGE_H`, `PAGE_OFFSET`,
`KERNELBASE`, `clear_page(page)`, `copy_page(to, from)`, `copy_user_page(to, from, vaddr, pg)`,
`pte_val(x)`, `pgd_val(x)`, `pgprot_val(x)`, `__pte(x)`, `__pgd(x)`, `__pgprot(x)`, and 4 more.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: State includes page tables, PTE permission/cache bits, ASID or context identifiers, TLB entries,
vmalloc/ioremap mappings, swap PTE encodings, and boot-time memory reservations.

Dependencies and integration points: Dependencies include `vdso/page.h`, `asm/setup.h`, `asm-generic/memory_model.h`, `asm-
generic/getorder.h`. Integration points include generic asm-generic helpers, OpenRISC SPR/status
register definitions, MM, irqflags, bitops, futex, ELF, and Kbuild/Kconfig infrastructure. This
source is part of the OpenRISC architecture port under the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/page.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/pgalloc.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/pgalloc.h

Purpose: implements OpenRISC page-directory and page-table allocation/population hooks.

Important APIs/types/functions: functions: `pmd_populate`, `current_pgd`; prototypes: `memcpy`; types: `page`; macros:
`__ASM_OPENRISC_PGALLOC_H`, `__HAVE_ARCH_PTE_ALLOC_ONE_KERNEL`, `pmd_populate_kernel(mm, pmd, pte)`,
`__pte_free_tlb(tlb, pte, addr)`.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: State includes page tables, PTE permission/cache bits, ASID or context identifiers, TLB entries,
vmalloc/ioremap mappings, swap PTE encodings, and boot-time memory reservations.

Dependencies and integration points: Dependencies include `asm/page.h`, `linux/threads.h`, `linux/mm.h`, `linux/memblock.h`, `asm-
generic/pgalloc.h`. Integration points include generic asm-generic helpers, OpenRISC SPR/status
register definitions, MM, irqflags, bitops, futex, ELF, and Kbuild/Kconfig infrastructure. This
source is part of the OpenRISC architecture port under the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/pgalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/pgtable.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/pgtable.h

Purpose: defines the OpenRISC page-table layout, PTE bit meanings, page protections, swap encoding, and MMU-
cache update hooks.

Important APIs/types/functions: functions: `pte_present`, `pte_write`, `pte_exec`, `pte_dirty`, `pte_young`, `pte_wrprotect`,
`pte_rdprotect`, `pte_exprotect`, `pte_mkclean`, `pte_mkold`, `pte_mkwrite_novma`, `pte_mkread`, and
13 more; prototypes: `Copyright`, `__va`, `update_cache`; types: `vm_area_struct`; typedefs:
`pte_addr_t`; macros: `__ASM_OPENRISC_PGTABLE_H`, `set_pte(pteptr, pteval)`, `set_pmd(pmdptr,
pmdval)`, `PGDIR_SHIFT`, `PGDIR_SIZE`, `PGDIR_MASK`, `PTRS_PER_PTE`, `PTRS_PER_PGD`,
`USER_PTRS_PER_PGD`, `VMALLOC_START`, `VMALLOC_END`, `VMALLOC_VMADDR(x)`, and 60 more.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: State includes page tables, PTE permission/cache bits, ASID or context identifiers, TLB entries,
vmalloc/ioremap mappings, swap PTE encodings, and boot-time memory reservations.

Dependencies and integration points: Dependencies include `asm-generic/pgtable-nopmd.h`, `asm/mmu.h`, `asm/fixmap.h`. Integration points
include generic asm-generic helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops,
futex, ELF, and Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port
under the vendored ceph-client kernel tree.

Risks: Risks include stale TLB/cache state, wrong access permissions, corrupted page tables, bad ASID
reuse, kernel faults without fixups, DMA coherency loss, or ABI-visible memory corruption.

Test signals: Test signals are boot under an emulator or board, page-fault and fork/exec stress, mmap/mprotect,
swap where enabled, vmalloc/ioremap users, DMA drivers, module loading, and cache/TLB debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/processor.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/processor.h

Purpose: defines OpenRISC thread_struct, kernel/user status values, task size, stack/register access, and
start_thread declarations.

Important APIs/types/functions: prototypes: `start_thread`; types: `task_struct`, `thread_struct`; macros:
`__ASM_OPENRISC_PROCESSOR_H`, `STACK_TOP`, `STACK_TOP_MAX`, `KERNEL_SR`, `USER_SR`, `TASK_SIZE`,
`TASK_UNMAPPED_BASE`, `user_regs(thread_info)`, `task_pt_regs(task)`, `INIT_SP`, `INIT_THREAD`,
`KSTK_EIP(tsk)`, and 2 more.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: The file has little durable storage of its own; effects flow through architecture globals, hardware
registers, task structures, or generic subsystem state owned by callers.

Dependencies and integration points: Dependencies include `asm/spr_defs.h`, `asm/page.h`, `asm/ptrace.h`. Integration points include
generic asm-generic helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops, futex,
ELF, and Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port under
the vendored ceph-client kernel tree.

Risks: Risks include architecture-specific assumptions about alignment, endianness, cache geometry, control
registers, compiler output, and boot/devicetree data.

Test signals: Test signals are cross-compilation, architecture boot smoke tests, relevant kernel selftests, and
subsystem-specific runtime paths that exercise the declared hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/openrisc/include/asm/ptrace.h

Purpose: defines OpenRISC kernel register frames, ptrace offsets, user/kernel mode predicates, and register-
query helpers.

Important APIs/types/functions: functions: `instruction_pointer`, `instruction_pointer_set`, `kernel_stack_pointer`,
`regs_return_value`, `regs_get_register`; prototypes: `regs_query_register_offset`; types:
`pt_regs`; macros: `__ASM_OPENRISC_PTRACE_H`, `STACK_FRAME_OVERHEAD`, `MAX_REG_OFFSET`,
`user_mode(regs)`, `user_stack_pointer(regs)`, `profile_pc(regs)`, `PT_SR`, `PT_SP`, `PT_GPR2`,
`PT_GPR3`, `PT_GPR4`, `PT_GPR5`, and 28 more.

Control flow: This header is consumed at compile time by generic Linux, low-level assembly, and architecture C
code; its macros/types are expanded into syscall, MM, signal, ptrace, or build-time contracts rather
than running standalone.

State and persistence: State is stored in saved pt_regs/switch_stack frames, user signal frames, debugger register packets,
thread flags, and ptrace-visible register sets.

Dependencies and integration points: Dependencies include `asm/spr_defs.h`, `uapi/asm/ptrace.h`, `linux/compiler.h`. Integration points
include generic asm-generic helpers, OpenRISC SPR/status register definitions, MM, irqflags, bitops,
futex, ELF, and Kbuild/Kconfig infrastructure. This source is part of the OpenRISC architecture port
under the vendored ceph-client kernel tree.

Risks: Risks include register-frame layout mismatches, incorrect syscall restart/error translation, broken
debugger or signal ABI, recursive exceptions, and returning to userspace with inconsistent status
bits.

Test signals: Test signals are syscall ABI tests, strace/ptrace, signal delivery and sigreturn tests, KGDB
breakpoint handling, interrupt/preemption stress, illegal/alignment exception tests, and user/kernel
register dump sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/openrisc/include/asm/ptrace.h -->
