# subset-b-000641 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/mcpm.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/mcpm.h

## Purpose
Defines ARM multi-cluster power management (MCPM) limits, entry vectors, CPU/cluster power lifecycle APIs, platform callback registration, and the assembly-visible synchronization structure used to coordinate big.LITTLE style cluster shutdown and bring-up.

## Important APIs, Types, And Functions
Key declarations include extern void mcpm_entry_point(void);; void mcpm_set_entry_vector(unsigned cpu, unsigned cluster, void *ptr);; void mcpm_set_early_poke(unsigned cpu, unsigned cluster,; unsigned long poke_phys_addr, unsigned long poke_val);; int mcpm_cpu_power_up(unsigned int cpu, unsigned int cluster);; void mcpm_cpu_power_down(void);. Important macros/constants include MCPM_H, MAX_CPUS_PER_CLUSTER, MAX_NR_CLUSTERS, MAX_NR_CLUSTERS, __CACHE_WRITEBACK_GRANULE, CPU_DOWN, CPU_COMING_UP, CPU_UP, CPU_GOING_DOWN, CLUSTER_DOWN. It depends directly on #include <linux/types.h>, #include <asm/cacheflush.h>, #include <asm/asm-offsets.h>.

## Control Flow
Power control is driven by callers setting entry vectors and early pokes, requesting CPU power-up/down/suspend, and platform callbacks updating CPU, cluster, and inbound states under the MCPM lock. Assembly code consumes the sync structure offsets for cache-safe handoff.

## State And Persistence
State is held in the MCPM synchronization structure with per-CPU, per-cluster, and inbound flags aligned to cache writeback granules; platform code owns the real power-controller state.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/types.h>, #include <asm/cacheflush.h>, #include <asm/asm-offsets.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/mcpm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/mcs_spinlock.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/mcs_spinlock.h

## Purpose
Supplies ARM SMP hooks for generic MCS queued spinlocks using WFE/SEV-friendly acquire and release primitives.

## Important APIs, Types, And Functions
Important macros/constants include __ASM_MCS_LOCK_H, arch_mcs_spin_lock_contended(lock), arch_mcs_spin_unlock_contended(lock). It depends directly on #include <asm/spinlock.h>.

## Control Flow
Waiters publish prior stores, sleep in WFE until the node lock byte becomes true with acquire ordering, and unlockers store-release then call dsb_sev to wake sleepers.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/spinlock.h>.

## Risks And Edge Cases
Ordering and wakeup details are concurrency-critical; missing barriers or broken WFE/SEV alternatives can deadlock SMP systems or expose protected data before lock acquisition is complete.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/mcs_spinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/memblock.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/memblock.h

## Purpose
Declares ARM early-memory setup entry points that initialize memblock from the selected machine description and reserve aligned boot-time memory before the normal allocator exists.

## Important APIs, Types, And Functions
Key declarations include struct machine_desc;; void arm_memblock_init(const struct machine_desc *);; phys_addr_t arm_memblock_steal(phys_addr_t size, phys_addr_t align);. Important macros/constants include _ASM_ARM_MEMBLOCK_H.

## Control Flow
Boot code calls arm_memblock_init, then arm_memblock_steal can carve physically aligned ranges for low-level data structures.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/memblock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/memory.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/memory.h

## Purpose
Central ARM memory-layout contract for PAGE_OFFSET, task/module/vmalloc/FDT/vector placement, physical-to-virtual translation, PFN conversion, idmap aliases, and debug-virtual hooks.

## Important APIs, Types, And Functions
Key declarations include extern unsigned long setup_vectors_base(void);; extern unsigned long vectors_base;; extern u64 kernel_sec_start;; extern u64 kernel_sec_end;; extern unsigned long __pv_phys_pfn_offset;; extern u64 __pv_offset;. Important macros/constants include __ASM_ARM_MEMORY_H, PAGE_OFFSET, KERNEL_OFFSET, TASK_SIZE, TASK_SIZE, TASK_UNMAPPED_BASE, TASK_SIZE_26, MODULES_VADDR, MODULES_VADDR, MODULES_END. It depends directly on #include <linux/compiler.h>, #include <linux/const.h>, #include <linux/types.h>, #include <linux/sizes.h>, #include <mach/memory.h>, #include <asm/kasan_def.h>.

## Control Flow
Compile-time CONFIG_MMU, CONFIG_ARM_PATCH_PHYS_VIRT, LPAE, XIP, KASAN, HIGHMEM, and NoMMU branches select constants and inline assembly stubs; runtime phys/virt patching can rewrite pv-table entries before helpers such as __pa, __va, virt_to_phys, and phys_to_virt are used.

## State And Persistence
State is architectural memory-management state: page tables, ASIDs or pending switches, vmalloc sequence counters, physical/virtual offsets, and linker-defined address ranges. The header itself stores no data except declared externs and compile-time constants.

## Dependencies And Integration Points
Integrated with the generic Linux MM, scheduler, exception, and cache/TLB subsystems. Dependencies include #include <linux/compiler.h>, #include <linux/const.h>, #include <linux/types.h>, #include <linux/sizes.h>, #include <mach/memory.h>, #include <asm/kasan_def.h>, CP15 processor helpers, and configuration choices such as CONFIG_MMU, CONFIG_ARM_LPAE, CONFIG_SMP, and CPU feature selections.

## Risks And Edge Cases
Bit definitions and barriers are ABI-critical. Incorrect masks, missing cache/TLB maintenance, wrong ASID handling, or bad user-access bounds can cause silent memory corruption, stale translations, privilege bypass, or hard-to-debug boot failures.

## Test Signals
Signals include ARM allnoconfig/defconfig builds across MMU/NoMMU and LPAE variants, boot tests, vmalloc/module loading, mmap/mprotect/hugetlb where applicable, and MM selftests that exercise faults and TLB shootdowns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/memory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/mman.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/mman.h

## Purpose
Adds ARM-specific mmap policy support on top of UAPI mman definitions, currently exposing whether write-execute denial is supported by the CPU architecture.

## Important APIs, Types, And Functions
Key declarations include static inline bool arch_memory_deny_write_exec_supported(void). Important macros/constants include __ASM_MMAN_H__, arch_memory_deny_write_exec_supported. It depends directly on #include <asm/system_info.h>, #include <uapi/asm/mman.h>.

## Control Flow
The inline helper gates memory-deny-write-exec support on cpu_architecture() >= ARMv6.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/system_info.h>, #include <uapi/asm/mman.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/mman.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/mmu.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/mmu.h

## Purpose
Defines mm_context_t for ARM MMU and NoMMU kernels, including ASID state, vmalloc sequence tracking, signal/vDSO page addresses, and FDPIC load-map fields.

## Important APIs, Types, And Functions
Key declarations include typedef struct {; unsigned long sigpage;; unsigned long vdso;; unsigned long exec_fdpic_loadmap;; unsigned long interp_fdpic_loadmap;; typedef struct {. Important macros/constants include __ARM_MMU_H, ASID_BITS, ASID_MASK, ASID(mm), ASID(mm).

## Control Flow
The MMU branch tracks ASIDs or deferred switches plus vmalloc synchronization; the NoMMU branch keeps end_brk and optional FDPIC metadata.

## State And Persistence
State is architectural memory-management state: page tables, ASIDs or pending switches, vmalloc sequence counters, physical/virtual offsets, and linker-defined address ranges. The header itself stores no data except declared externs and compile-time constants.

## Dependencies And Integration Points
Integrated with the generic Linux MM, scheduler, exception, and cache/TLB subsystems. Dependencies include the surrounding ARM architecture build and generic kernel headers, CP15 processor helpers, and configuration choices such as CONFIG_MMU, CONFIG_ARM_LPAE, CONFIG_SMP, and CPU feature selections.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/mmu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/mmu_context.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/mmu_context.h

## Purpose
Implements the ARM context-switch interface between scheduler/MM code and CPU page-table switching, including ASID allocation paths, vmalloc sequence checks, lazy TLB handling, and non-ASID deferred switches.

## Important APIs, Types, And Functions
Key declarations include void __check_vmalloc_seq(struct mm_struct *mm);; static inline void check_vmalloc_seq(struct mm_struct *mm); void check_and_switch_context(struct mm_struct *mm, struct task_struct *tsk);; static inline int; void a15_erratum_get_cpumask(int this_cpu, struct mm_struct *mm,; static inline void a15_erratum_get_cpumask(int this_cpu, struct mm_struct *mm,. Important macros/constants include __ASM_ARM_MMU_CONTEXT_H, init_new_context, finish_arch_post_lock_switch, activate_mm(prev,next), enter_lazy_tlb. It depends directly on #include <linux/compiler.h>, #include <linux/sched.h>, #include <linux/mm_types.h>, #include <linux/preempt.h>, #include <asm/cacheflush.h>, #include <asm/cachetype.h>.

## Control Flow
switch_mm records active CPUs, checks vmalloc sequence, optionally flushes cache on VIVT/VIPT aliasing CPUs, and calls check_and_switch_context or cpu_switch_mm; finish_arch_post_lock_switch completes deferred non-ASID switches after IRQ-disabled sections.

## State And Persistence
State is architectural memory-management state: page tables, ASIDs or pending switches, vmalloc sequence counters, physical/virtual offsets, and linker-defined address ranges. The header itself stores no data except declared externs and compile-time constants.

## Dependencies And Integration Points
Integrated with the generic Linux MM, scheduler, exception, and cache/TLB subsystems. Dependencies include #include <linux/compiler.h>, #include <linux/sched.h>, #include <linux/mm_types.h>, #include <linux/preempt.h>, #include <asm/cacheflush.h>, #include <asm/cachetype.h>, #include <asm/proc-fns.h>, #include <asm/smp_plat.h>, CP15 processor helpers, and configuration choices such as CONFIG_MMU, CONFIG_ARM_LPAE, CONFIG_SMP, and CPU feature selections.

## Risks And Edge Cases
Bit definitions and barriers are ABI-critical. Incorrect masks, missing cache/TLB maintenance, wrong ASID handling, or bad user-access bounds can cause silent memory corruption, stale translations, privilege bypass, or hard-to-debug boot failures.

## Test Signals
Signals include ARM allnoconfig/defconfig builds across MMU/NoMMU and LPAE variants, boot tests, vmalloc/module loading, mmap/mprotect/hugetlb where applicable, and MM selftests that exercise faults and TLB shootdowns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/mmu_context.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/module.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/module.h

## Purpose
Defines ARM module-loader architecture state, including unwind table bookkeeping and PLT sections used when module relocations need stubs near kernel text.

## Important APIs, Types, And Functions
Key declarations include struct plt_entries {; struct mod_plt_sec {; struct elf32_shdr *plt;; struct plt_entries *plt_ent;; struct mod_arch_specific {; struct list_head unwind_list;. Important macros/constants include _ASM_ARM_MODULE_H, ELF_SECTION_UNWIND, PLT_ENT_STRIDE, PLT_ENT_COUNT, PLT_ENT_SIZE, HAVE_ARCH_KALLSYMS_SYMBOL_VALUE. It depends directly on #include <asm-generic/module.h>, #include <asm/unwind.h>.

## Control Flow
The module loader fills mod_arch_specific during load; kallsyms_symbol_value returns PLT-adjusted symbol values when CONFIG_ARM_MODULE_PLTS is enabled.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm-generic/module.h>, #include <asm/unwind.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/module.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/module.lds.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/module.lds.h

## Purpose
Provides the ARM module linker-script include point; in this tree it is intentionally empty and relies on generic module layout.

## Important APIs, Types, And Functions
This file intentionally has little local API surface; its exported behavior is the include or linker-script contract itself.

## Control Flow
There is no runtime flow; build scripts may include it to allow architecture-specific sections without requiring conditional include logic.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/module.lds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/mpu.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/mpu.h

## Purpose
Defines PMSA/MPU register bit layouts, memory attributes, region descriptors, and setup hooks for ARM NoMMU/MPU systems.

## Important APIs, Types, And Functions
Key declarations include struct mpu_rgn {; struct mpu_rgn_info {; unsigned int used;; struct mpu_rgn rgns[MPU_MAX_REGIONS];; extern struct mpu_rgn_info mpu_rgn_info;; extern void __init pmsav7_adjust_lowmem_bounds(void);. Important macros/constants include __ARM_MPU_H, MPUIR_nU, MPUIR_DREGION, MPUIR_IREGION, MPUIR_DREGION_SZMASK, MPUIR_IREGION_SZMASK, MMFR0_PMSA, MMFR0_PMSAv7, MMFR0_PMSAv8, PMSAv7_RSR_SZ.

## Control Flow
Early architecture setup detects PMSAv7 or PMSAv8, adjusts lowmem bounds, fills mpu_rgn_info, and programs region base/limit/access attributes.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/mpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/mtd-xip.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/mtd-xip.h

## Purpose
Provides ARM execute-in-place flash support hooks for MTD XIP users.

## Important APIs, Types, And Functions
Important macros/constants include __ARM_MTD_XIP_H__, xip_iprefetch(). It depends directly on #include <mach/mtd-xip.h>.

## Control Flow
The xip_iprefetch macro emits a short NOP train so flash-backed instruction fetch can be prefetched around polling paths.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <mach/mtd-xip.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/mtd-xip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/neon.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/neon.h

## Purpose
Defines kernel NEON availability and critical-section entry/exit helpers for code that temporarily uses NEON/VFP registers in kernel mode.

## Important APIs, Types, And Functions
Key declarations include void kernel_neon_begin(void);; void kernel_neon_end(void);. Important macros/constants include cpu_has_neon(), kernel_neon_begin(). It depends directly on #include <asm/hwcap.h>.

## Control Flow
Callers test cpu_has_neon, enter kernel_neon_begin, perform bounded SIMD work with preemption/FPU ownership handled elsewhere, and leave through kernel_neon_end.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/hwcap.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/neon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/nwflash.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/nwflash.h

## Purpose
Defines NetWinder flash command constants for enabling and disabling writes to legacy flash hardware.

## Important APIs, Types, And Functions
Important macros/constants include _FLASH_H, CMD_WRITE_DISABLE, CMD_WRITE_ENABLE, CMD_WRITE_BASE64K_ENABLE.

## Control Flow
Callers issue the command values to platform flash registers; this header has no executable flow.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/nwflash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/opcodes-sec.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/opcodes-sec.h

## Purpose
Defines the secure monitor call opcode macro for emitting SMC instructions in either ARM or Thumb-2 code.

## Important APIs, Types, And Functions
Important macros/constants include __ASM_ARM_OPCODES_SEC_H, __SMC(imm4). It depends directly on #include <asm/opcodes.h>.

## Control Flow
__SMC composes the correct ARM/Thumb opcode through opcodes.h instruction-emission helpers.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/opcodes.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/opcodes-sec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/opcodes-virt.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/opcodes-virt.h

## Purpose
Defines virtualization instruction opcode macros for HVC, ERET, and MSR ELR_hyp in ARM or Thumb-2 mode.

## Important APIs, Types, And Functions
Important macros/constants include __ASM_ARM_OPCODES_VIRT_H, __HVC(imm16), __ERET, __MSR_ELR_HYP(regnum). It depends directly on #include <asm/opcodes.h>.

## Control Flow
Hypervisor stubs use these macros so the assembler receives the right encoding independent of kernel instruction set mode.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/opcodes.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/opcodes-virt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/opcodes.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/opcodes.h

## Purpose
Centralizes ARM/Thumb opcode byte-order conversion, instruction emission, Thumb-32 composition, and condition-code testing declarations for probes, patching, and exception code.

## Important APIs, Types, And Functions
Key declarations include extern asmlinkage unsigned int arm_check_condition(u32 opcode, u32 psr);; extern __u32 __opcode_to_mem_thumb32(__u32);. Important macros/constants include __ASM_ARM_OPCODES_H, ARM_OPCODE_CONDTEST_FAIL, ARM_OPCODE_CONDTEST_PASS, ARM_OPCODE_CONDTEST_UNCOND, ___asm_opcode_swab32(x), ___asm_opcode_swab16(x), ___asm_opcode_swahb32(x), ___asm_opcode_swahw32(x). It depends directly on #include <linux/linkage.h>, #include <linux/types.h>, #include <linux/swab.h>, #include <linux/stringify.h>.

## Control Flow
Compile-time assembly macros and C helpers translate between opcode values and memory order, select ARM versus Thumb encodings, and emit .long/.short directives for inline instruction constants.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/linkage.h>, #include <linux/types.h>, #include <linux/swab.h>, #include <linux/stringify.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/opcodes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/outercache.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/outercache.h

## Purpose
Defines the outer-cache operation dispatch table and inline wrappers used by ARM platforms with external L2 caches.

## Important APIs, Types, And Functions
Key declarations include struct l2x0_regs;; struct outer_cache_fns {; void (*inv_range)(unsigned long, unsigned long);; void (*clean_range)(unsigned long, unsigned long);; void (*flush_range)(unsigned long, unsigned long);; void (*flush_all)(void);. Important macros/constants include __ASM_OUTERCACHE_H. It depends directly on #include <linux/types.h>.

## Control Flow
If CONFIG_OUTER_CACHE is enabled, wrappers call registered outer_cache callbacks for range invalidate/clean/flush, all-cache flush, disable, resume, secure writes, and L2x0 configuration; otherwise they compile to no-ops.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/types.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/outercache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/page-nommu.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/page-nommu.h

## Purpose
Defines NoMMU page primitives and minimal page-table scalar types for ARM configurations without an MMU.

## Important APIs, Types, And Functions
Key declarations include typedef unsigned long pte_t;; typedef unsigned long pmd_t;; typedef unsigned long pgd_t[2];; typedef unsigned long pgprot_t;. Important macros/constants include _ASMARM_PAGE_NOMMU_H, clear_page(page), copy_page(to,from), copy_user_page(to,, pte_val(x), pmd_val(x), pgd_val(x), pgprot_val(x).

## Control Flow
clear_page/copy_page map to memset/memcpy and pte/pmd/pgd/pgprot accessors are direct integer wrappers.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/page-nommu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/page.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/page.h

## Purpose
Defines ARM page size assumptions, cache-color user-page operations, page-table type selection, clear/copy highpage helpers, and inclusion ordering for memory.h.

## Important APIs, Types, And Functions
Key declarations include struct page;; struct vm_area_struct;; struct cpu_user_fns {; void (*cpu_clear_user_highpage)(struct page *page, unsigned long vaddr);; void (*cpu_copy_user_highpage)(struct page *to, struct page *from,; unsigned long vaddr, struct vm_area_struct *vma);. Important macros/constants include _ASMARM_PAGE_H, __cpu_clear_user_highpage, __cpu_copy_user_highpage, __cpu_clear_user_highpage, __cpu_copy_user_highpage, clear_user_highpage(page,vaddr), __HAVE_ARCH_COPY_USER_HIGHPAGE, copy_user_highpage(to,from,vaddr,vma), clear_page(page), ARCH_PAGE_TABLE_SYNC_MASK. It depends directly on #include <vdso/page.h>, #include <asm/page-nommu.h>, #include <asm/glue.h>, #include <asm/pgtable-3level-types.h>, #include <asm/pgtable-2level-types.h>, #include <asm/memory.h>.

## Control Flow
Build-time CPU cache model selection chooses user highpage functions; callers go through clear_user_highpage, copy_user_highpage, page_to_phys, and pgtable type helpers.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <vdso/page.h>, #include <asm/page-nommu.h>, #include <asm/glue.h>, #include <asm/pgtable-3level-types.h>, #include <asm/pgtable-2level-types.h>, #include <asm/memory.h>, #include <asm-generic/getorder.h>, #include <asm-generic/memory_model.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/page.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/pci.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/pci.h

## Purpose
Declares ARM PCI host-bridge integration constants and helpers for resource mapping and optional I/O remapping.

## Important APIs, Types, And Functions
Key declarations include extern unsigned long pcibios_min_io;; extern unsigned long pcibios_min_mem;; static inline int pci_proc_domain(struct pci_bus *bus); extern void pcibios_report_status(unsigned int status_mask, int warn);. Important macros/constants include ASMARM_PCI_H, PCIBIOS_MIN_IO, PCIBIOS_MIN_MEM, pcibios_assign_all_busses(), HAVE_PCI_MMAP, ARCH_GENERIC_PCI_MMAP_RESOURCE. It depends directly on #include <asm/mach/pci.h> /* for pci_sys_data */.

## Control Flow
PCI core code uses the arch hooks during bus scan, resource setup, and mmap of PCI memory to userspace.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/mach/pci.h> /* for pci_sys_data */.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/percpu.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/percpu.h

## Purpose
Provides ARM per-CPU offset access definitions and falls through to the generic per-CPU implementation.

## Important APIs, Types, And Functions
Key declarations include static inline void set_my_cpu_offset(unsigned long off); extern unsigned int smp_on_up;; unsigned long off;. Important macros/constants include _ASM_ARM_PERCPU_H_, __my_cpu_offset, set_my_cpu_offset(x). It depends directly on #include <asm/insn.h>, #include <asm-generic/percpu.h>.

## Control Flow
Generated code resolves per-CPU variables through the architecture offset mechanism selected by the generic headers.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/insn.h>, #include <asm-generic/percpu.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/percpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/perf_event.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/perf_event.h

## Purpose
Defines ARM perf-event architecture hooks and PMU interrupt plumbing.

## Important APIs, Types, And Functions
Important macros/constants include __ARM_PERF_EVENT_H__, perf_arch_fetch_caller_regs(regs,.

## Control Flow
Perf core calls the declared PMU setup/IRQ helpers to bind counters to CPU-local hardware and event mappings.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/perf_event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/pgalloc.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/pgalloc.h

## Purpose
Implements ARM page-table allocation, construction, and freeing helpers used by the MM subsystem.

## Important APIs, Types, And Functions
Key declarations include static inline void pud_populate(struct mm_struct *mm, pud_t *pud, pmd_t *pmd); extern pgd_t *pgd_alloc(struct mm_struct *mm);; extern void pgd_free(struct mm_struct *mm, pgd_t *pgd);; static inline void clean_pte_table(pte_t *pte); static inline pte_t *; static inline pgtable_t. Important macros/constants include _ASMARM_PGALLOC_H, _PAGE_USER_TABLE, _PAGE_KERNEL_TABLE, PGD_SIZE, PGD_SIZE, pmd_alloc_one(mm,addr), pmd_free(mm,, pud_populate(mm,pmd,pte), pud_populate(mm,pmd,pte), PGTABLE_HIGHMEM. It depends directly on #include <linux/pagemap.h>, #include <asm/domain.h>, #include <asm/pgtable-hwdef.h>, #include <asm/processor.h>, #include <asm/cacheflush.h>, #include <asm/tlbflush.h>.

## Control Flow
PGD/PTE allocation paths allocate pages, initialize kernel mappings, clean/flush page-table entries for hardware table walks, and free tables through quicklist or page allocator paths.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/pagemap.h>, #include <asm/domain.h>, #include <asm/pgtable-hwdef.h>, #include <asm/processor.h>, #include <asm/cacheflush.h>, #include <asm/tlbflush.h>, #include <asm-generic/pgalloc.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/pgalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/pgtable-2level-hwdef.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/pgtable-2level-hwdef.h

## Purpose
Defines short-descriptor ARM page-table hardware bit encodings for PMD section entries, PTE small pages, domains, access permissions, TEX/C/B memory types, and execute-never flags.

## Important APIs, Types, And Functions
Important macros/constants include _ASM_PGTABLE_2LEVEL_HWDEF_H, PMD_TYPE_MASK, PMD_TYPE_FAULT, PMD_TYPE_TABLE, PMD_TYPE_SECT, PMD_PXNTABLE, PMD_BIT4, PMD_DOMAIN(x), PMD_DOMAIN_MASK, PMD_PROTECTION.

## Control Flow
Low-level MM code combines these constants with Linux PTE bits when cpu_set_pte_ext writes the hardware half of a two-level page table.

## State And Persistence
State is architectural memory-management state: page tables, ASIDs or pending switches, vmalloc sequence counters, physical/virtual offsets, and linker-defined address ranges. The header itself stores no data except declared externs and compile-time constants.

## Dependencies And Integration Points
Integrated with the generic Linux MM, scheduler, exception, and cache/TLB subsystems. Dependencies include the surrounding ARM architecture build and generic kernel headers, CP15 processor helpers, and configuration choices such as CONFIG_MMU, CONFIG_ARM_LPAE, CONFIG_SMP, and CPU feature selections.

## Risks And Edge Cases
Bit definitions and barriers are ABI-critical. Incorrect masks, missing cache/TLB maintenance, wrong ASID handling, or bad user-access bounds can cause silent memory corruption, stale translations, privilege bypass, or hard-to-debug boot failures.

## Test Signals
Signals include ARM allnoconfig/defconfig builds across MMU/NoMMU and LPAE variants, boot tests, vmalloc/module loading, mmap/mprotect/hugetlb where applicable, and MM selftests that exercise faults and TLB shootdowns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/pgtable-2level-hwdef.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/pgtable-2level-types.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/pgtable-2level-types.h

## Purpose
Defines pteval_t, pmdval_t, pgdval_t and wrapper structures/macros for ARM short-descriptor page tables.

## Important APIs, Types, And Functions
Key declarations include typedef u32 pteval_t;; typedef u32 pmdval_t;; typedef struct { pteval_t pte; } pte_t;; typedef struct { pmdval_t pmd; } pmd_t;; typedef struct { pmdval_t pgd[2]; } pgd_t;; typedef struct { pteval_t pgprot; } pgprot_t;. Important macros/constants include _ASM_PGTABLE_2LEVEL_TYPES_H, pte_val(x), pmd_val(x), pgd_val(x), pgprot_val(x), __pte(x), __pmd(x), __pgprot(x), pte_val(x), pmd_val(x). It depends directly on #include <asm/types.h>.

## Control Flow
Generic MM code manipulates opaque pte_t/pmd_t/pgd_t values while architecture code extracts integer values through pte_val, pmd_val, pgd_val, and __pte/__pmd/__pgd.

## State And Persistence
State is architectural memory-management state: page tables, ASIDs or pending switches, vmalloc sequence counters, physical/virtual offsets, and linker-defined address ranges. The header itself stores no data except declared externs and compile-time constants.

## Dependencies And Integration Points
Integrated with the generic Linux MM, scheduler, exception, and cache/TLB subsystems. Dependencies include #include <asm/types.h>, CP15 processor helpers, and configuration choices such as CONFIG_MMU, CONFIG_ARM_LPAE, CONFIG_SMP, and CPU feature selections.

## Risks And Edge Cases
Bit definitions and barriers are ABI-critical. Incorrect masks, missing cache/TLB maintenance, wrong ASID handling, or bad user-access bounds can cause silent memory corruption, stale translations, privilege bypass, or hard-to-debug boot failures.

## Test Signals
Signals include ARM allnoconfig/defconfig builds across MMU/NoMMU and LPAE variants, boot tests, vmalloc/module loading, mmap/mprotect/hugetlb where applicable, and MM selftests that exercise faults and TLB shootdowns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/pgtable-2level-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/pgtable-2level.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/pgtable-2level.h

## Purpose
Maps Linux three-level MM expectations onto ARM classic two-level short-descriptor hardware tables, including folded PMDs, Linux shadow PTEs, hardware PTE offsets, software accessed/dirty bits, and memory type encodings.

## Important APIs, Types, And Functions
Key declarations include static inline int pud_none(pud_t pud); static inline int pud_bad(pud_t pud); static inline int pud_present(pud_t pud); static inline void pud_clear(pud_t *pudp); static inline void set_pud(pud_t *pudp, pud_t pud); static inline pmd_t *pmd_offset(pud_t *pud, unsigned long addr). Important macros/constants include _ASM_PGTABLE_2LEVEL_H, __PAGETABLE_PMD_FOLDED, PTRS_PER_PTE, PTRS_PER_PMD, PTRS_PER_PGD, PTE_HWTABLE_PTRS, PTE_HWTABLE_OFF, PTE_HWTABLE_SIZE, MAX_POSSIBLE_PHYSMEM_BITS, PMD_SHIFT.

## Control Flow
The MM layer updates Linux PTE bits; set_pte_ext converts them into adjacent hardware PTE entries. Accessed and dirty are emulated by faulting until handle_pte_fault updates the Linux bits and TLB maintenance observes the changed hardware permissions.

## State And Persistence
State is architectural memory-management state: page tables, ASIDs or pending switches, vmalloc sequence counters, physical/virtual offsets, and linker-defined address ranges. The header itself stores no data except declared externs and compile-time constants.

## Dependencies And Integration Points
Integrated with the generic Linux MM, scheduler, exception, and cache/TLB subsystems. Dependencies include the surrounding ARM architecture build and generic kernel headers, CP15 processor helpers, and configuration choices such as CONFIG_MMU, CONFIG_ARM_LPAE, CONFIG_SMP, and CPU feature selections.

## Risks And Edge Cases
Bit definitions and barriers are ABI-critical. Incorrect masks, missing cache/TLB maintenance, wrong ASID handling, or bad user-access bounds can cause silent memory corruption, stale translations, privilege bypass, or hard-to-debug boot failures.

## Test Signals
Signals include ARM allnoconfig/defconfig builds across MMU/NoMMU and LPAE variants, boot tests, vmalloc/module loading, mmap/mprotect/hugetlb where applicable, and MM selftests that exercise faults and TLB shootdowns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/pgtable-2level.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/pgtable-3level-hwdef.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/pgtable-3level-hwdef.h

## Purpose
Defines ARM LPAE long-descriptor page-table hardware encodings, including descriptor types, access flags, shareability, AP permissions, execute-never bits, MAIR indexes, and TTBR/TCR field values.

## Important APIs, Types, And Functions
Important macros/constants include _ASM_PGTABLE_3LEVEL_HWDEF_H, PUD_TABLE_BIT, PMD_TYPE_MASK, PMD_TYPE_FAULT, PMD_TYPE_TABLE, PMD_TYPE_SECT, PMD_TABLE_BIT, PMD_BIT4, PMD_DOMAIN(x), PMD_APTABLE_SHIFT.

## Control Flow
LPAE page-table setup and set_pte_ext use these constants to populate 64-bit PUD/PMD/PTE descriptors and translation-control registers.

## State And Persistence
State is architectural memory-management state: page tables, ASIDs or pending switches, vmalloc sequence counters, physical/virtual offsets, and linker-defined address ranges. The header itself stores no data except declared externs and compile-time constants.

## Dependencies And Integration Points
Integrated with the generic Linux MM, scheduler, exception, and cache/TLB subsystems. Dependencies include the surrounding ARM architecture build and generic kernel headers, CP15 processor helpers, and configuration choices such as CONFIG_MMU, CONFIG_ARM_LPAE, CONFIG_SMP, and CPU feature selections.

## Risks And Edge Cases
Bit definitions and barriers are ABI-critical. Incorrect masks, missing cache/TLB maintenance, wrong ASID handling, or bad user-access bounds can cause silent memory corruption, stale translations, privilege bypass, or hard-to-debug boot failures.

## Test Signals
Signals include ARM allnoconfig/defconfig builds across MMU/NoMMU and LPAE variants, boot tests, vmalloc/module loading, mmap/mprotect/hugetlb where applicable, and MM selftests that exercise faults and TLB shootdowns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/pgtable-3level-hwdef.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/pgtable-3level-types.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/pgtable-3level-types.h

## Purpose
Defines 64-bit LPAE page-table value types and wrapper structs for PTE, PMD, PUD, PGD, and pgprot values.

## Important APIs, Types, And Functions
Key declarations include typedef u64 pteval_t;; typedef u64 pmdval_t;; typedef u64 pgdval_t;; typedef struct { pteval_t pte; } pte_t;; typedef struct { pmdval_t pmd; } pmd_t;; typedef struct { pgdval_t pgd; } pgd_t;. Important macros/constants include _ASM_PGTABLE_3LEVEL_TYPES_H, pte_val(x), pmd_val(x), pgd_val(x), pgprot_val(x), __pte(x), __pmd(x), __pgd(x), pte_val(x), pmd_val(x). It depends directly on #include <asm/types.h>.

## Control Flow
Generic MM code remains type-safe through wrappers while LPAE-specific code reads and writes 64-bit descriptor values.

## State And Persistence
State is architectural memory-management state: page tables, ASIDs or pending switches, vmalloc sequence counters, physical/virtual offsets, and linker-defined address ranges. The header itself stores no data except declared externs and compile-time constants.

## Dependencies And Integration Points
Integrated with the generic Linux MM, scheduler, exception, and cache/TLB subsystems. Dependencies include #include <asm/types.h>, CP15 processor helpers, and configuration choices such as CONFIG_MMU, CONFIG_ARM_LPAE, CONFIG_SMP, and CPU feature selections.

## Risks And Edge Cases
Bit definitions and barriers are ABI-critical. Incorrect masks, missing cache/TLB maintenance, wrong ASID handling, or bad user-access bounds can cause silent memory corruption, stale translations, privilege bypass, or hard-to-debug boot failures.

## Test Signals
Signals include ARM allnoconfig/defconfig builds across MMU/NoMMU and LPAE variants, boot tests, vmalloc/module loading, mmap/mprotect/hugetlb where applicable, and MM selftests that exercise faults and TLB shootdowns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/pgtable-3level-types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/pgtable-3level.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/pgtable-3level.h

## Purpose
Implements ARM LPAE three-level page-table layout, 64-bit Linux PTE bits, huge PMD handling, PTE comparison rules, and PMD permission/dirty/accessed helpers.

## Important APIs, Types, And Functions
Key declarations include static inline pmd_t *pud_pgtable(pud_t pud); static inline pte_t pte_mkspecial(pte_t pte); static inline pmd_t pmd_##fn(pmd_t pmd) { pmd_val(pmd) op; return pmd; }; static inline pmd_t pmd_mkinvalid(pmd_t pmd); static inline pmd_t pmd_modify(pmd_t pmd, pgprot_t newprot); static inline void set_pmd_at(struct mm_struct *mm, unsigned long addr,. Important macros/constants include _ASM_PGTABLE_3LEVEL_H, PTRS_PER_PTE, PTRS_PER_PMD, PTRS_PER_PGD, PTE_HWTABLE_PTRS, PTE_HWTABLE_OFF, PTE_HWTABLE_SIZE, MAX_POSSIBLE_PHYSMEM_BITS, PGDIR_SHIFT, PMD_SHIFT.

## Control Flow
PUD and PMD entries are cleaned/flushed for table-walk visibility; set_pmd_at adjusts validity and write permission based on PROT_NONE, dirty, and writable state, then writes non-global section descriptors for user mappings.

## State And Persistence
State is architectural memory-management state: page tables, ASIDs or pending switches, vmalloc sequence counters, physical/virtual offsets, and linker-defined address ranges. The header itself stores no data except declared externs and compile-time constants.

## Dependencies And Integration Points
Integrated with the generic Linux MM, scheduler, exception, and cache/TLB subsystems. Dependencies include the surrounding ARM architecture build and generic kernel headers, CP15 processor helpers, and configuration choices such as CONFIG_MMU, CONFIG_ARM_LPAE, CONFIG_SMP, and CPU feature selections.

## Risks And Edge Cases
Bit definitions and barriers are ABI-critical. Incorrect masks, missing cache/TLB maintenance, wrong ASID handling, or bad user-access bounds can cause silent memory corruption, stale translations, privilege bypass, or hard-to-debug boot failures.

## Test Signals
Signals include ARM allnoconfig/defconfig builds across MMU/NoMMU and LPAE variants, boot tests, vmalloc/module loading, mmap/mprotect/hugetlb where applicable, and MM selftests that exercise faults and TLB shootdowns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/pgtable-3level.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/pgtable-hwdef.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/pgtable-hwdef.h

## Purpose
Selects the correct ARM page-table hardware-definition header for either LPAE three-level or classic two-level MMU builds.

## Important APIs, Types, And Functions
Important macros/constants include _ASMARM_PGTABLE_HWDEF_H. It depends directly on #include <asm/pgtable-3level-hwdef.h>, #include <asm/pgtable-2level-hwdef.h>.

## Control Flow
The include path is compile-time only and gives pgtable.h a uniform set of descriptor constants.

## State And Persistence
State is architectural memory-management state: page tables, ASIDs or pending switches, vmalloc sequence counters, physical/virtual offsets, and linker-defined address ranges. The header itself stores no data except declared externs and compile-time constants.

## Dependencies And Integration Points
Integrated with the generic Linux MM, scheduler, exception, and cache/TLB subsystems. Dependencies include #include <asm/pgtable-3level-hwdef.h>, #include <asm/pgtable-2level-hwdef.h>, CP15 processor helpers, and configuration choices such as CONFIG_MMU, CONFIG_ARM_LPAE, CONFIG_SMP, and CPU feature selections.

## Risks And Edge Cases
Bit definitions and barriers are ABI-critical. Incorrect masks, missing cache/TLB maintenance, wrong ASID handling, or bad user-access bounds can cause silent memory corruption, stale translations, privilege bypass, or hard-to-debug boot failures.

## Test Signals
Signals include ARM allnoconfig/defconfig builds across MMU/NoMMU and LPAE variants, boot tests, vmalloc/module loading, mmap/mprotect/hugetlb where applicable, and MM selftests that exercise faults and TLB shootdowns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/pgtable-hwdef.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/pgtable-nommu.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/pgtable-nommu.h

## Purpose
Provides NoMMU pgtable constants and stubs so generic memory-management code can compile without hardware translation tables.

## Important APIs, Types, And Functions
Key declarations include typedef pte_t *pte_addr_t;; extern unsigned int kobjsize(const void *objp);. Important macros/constants include _ASMARM_PGTABLE_NOMMU_H, pgd_present(pgd), pgd_none(pgd), pgd_bad(pgd), pgd_clear(pgdp), PGDIR_SHIFT, PGDIR_SIZE, PGDIR_MASK, PAGE_NONE, PAGE_SHARED. It depends directly on #include <linux/slab.h>, #include <asm/processor.h>, #include <asm/page.h>.

## Control Flow
Most page protection and pte helpers collapse to direct values or no-ops because NoMMU mappings are not changed through page tables.

## State And Persistence
State is architectural memory-management state: page tables, ASIDs or pending switches, vmalloc sequence counters, physical/virtual offsets, and linker-defined address ranges. The header itself stores no data except declared externs and compile-time constants.

## Dependencies And Integration Points
Integrated with the generic Linux MM, scheduler, exception, and cache/TLB subsystems. Dependencies include #include <linux/slab.h>, #include <asm/processor.h>, #include <asm/page.h>, CP15 processor helpers, and configuration choices such as CONFIG_MMU, CONFIG_ARM_LPAE, CONFIG_SMP, and CPU feature selections.

## Risks And Edge Cases
Bit definitions and barriers are ABI-critical. Incorrect masks, missing cache/TLB maintenance, wrong ASID handling, or bad user-access bounds can cause silent memory corruption, stale translations, privilege bypass, or hard-to-debug boot failures.

## Test Signals
Signals include ARM allnoconfig/defconfig builds across MMU/NoMMU and LPAE variants, boot tests, vmalloc/module loading, mmap/mprotect/hugetlb where applicable, and MM selftests that exercise faults and TLB shootdowns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/pgtable-nommu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/pgtable.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/pgtable.h

## Purpose
Top-level ARM page-table interface connecting generic MM code to NoMMU, short-descriptor, or LPAE implementations, including VMALLOC bounds, pgprot definitions, PTE predicates, permission modifiers, and set_ptes.

## Important APIs, Types, And Functions
Key declarations include extern void __pte_error(const char *file, int line, pte_t);; extern void __pmd_error(const char *file, int line, pmd_t);; extern void __pgd_error(const char *file, int line, pgd_t);; extern pgprot_t pgprot_user;; extern pgprot_t pgprot_kernel;; struct file;. Important macros/constants include _ASMARM_PGTABLE_H, VMALLOC_OFFSET, VMALLOC_START, VMALLOC_END, LIBRARY_TEXT_START, pte_ERROR(pte), pmd_ERROR(pmd), pgd_ERROR(pgd), FIRST_USER_ADDRESS, USER_PGTABLES_CEILING. It depends directly on #include <linux/const.h>, #include <asm/proc-fns.h>, #include <asm-generic/pgtable-nopud.h>, #include <asm/pgtable-nommu.h>, #include <asm/page.h>, #include <asm/pgtable-hwdef.h>.

## Control Flow
The header includes the selected low-level page-table layout, defines pgprot transformations for normal/device/DMA mappings, and supplies PTE/PMD helpers that generic fault, mmap, and TLB code call.

## State And Persistence
State is architectural memory-management state: page tables, ASIDs or pending switches, vmalloc sequence counters, physical/virtual offsets, and linker-defined address ranges. The header itself stores no data except declared externs and compile-time constants.

## Dependencies And Integration Points
Integrated with the generic Linux MM, scheduler, exception, and cache/TLB subsystems. Dependencies include #include <linux/const.h>, #include <asm/proc-fns.h>, #include <asm-generic/pgtable-nopud.h>, #include <asm/pgtable-nommu.h>, #include <asm/page.h>, #include <asm/pgtable-hwdef.h>, #include <asm/tlbflush.h>, #include <asm/pgtable-3level.h>, CP15 processor helpers, and configuration choices such as CONFIG_MMU, CONFIG_ARM_LPAE, CONFIG_SMP, and CPU feature selections.

## Risks And Edge Cases
Bit definitions and barriers are ABI-critical. Incorrect masks, missing cache/TLB maintenance, wrong ASID handling, or bad user-access bounds can cause silent memory corruption, stale translations, privilege bypass, or hard-to-debug boot failures.

## Test Signals
Signals include ARM allnoconfig/defconfig builds across MMU/NoMMU and LPAE variants, boot tests, vmalloc/module loading, mmap/mprotect/hugetlb where applicable, and MM selftests that exercise faults and TLB shootdowns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/pgtable.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/probes.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/probes.h

## Purpose
Defines ARM kprobe/uprobes instruction-analysis interfaces and architecture-specific probe instruction storage.

## Important APIs, Types, And Functions
Key declarations include typedef u32 probes_opcode_t;; struct arch_probes_insn;; typedef void (probes_insn_handler_t)(probes_opcode_t,; struct arch_probes_insn *,; struct pt_regs *);; typedef unsigned long (probes_check_cc)(unsigned long);. Important macros/constants include _ASM_PROBES_H, MAX_STACK_SIZE.

## Control Flow
Probe setup decodes instruction slots through arch_probes_insn and installs pre/post handlers for breakpoint and single-step emulation.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/probes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/proc-fns.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/proc-fns.h

## Purpose
Defines the processor operations vector that abstracts CPU-specific data aborts, cache maintenance, page-table switching, PTE writes, idle, reset, and suspend/resume implementations.

## Important APIs, Types, And Functions
Key declarations include struct mm_struct;; struct processor {; void (*_data_abort)(unsigned long pc);; unsigned long (*_prefetch_abort)(unsigned long lr);; void (*_proc_init)(void);; void (*check_bugs)(void);. Important macros/constants include __ASM_PROCFNS_H, PROC_VTABLE(f), PROC_TABLE(f), PROC_VTABLE(f), PROC_TABLE(f), cpu_proc_init, cpu_check_bugs, cpu_proc_fin, cpu_reset, cpu_do_idle. It depends directly on #include <asm/glue-proc.h>, #include <asm/page.h>, #include <linux/smp.h>.

## Control Flow
Boot CPU detection initializes either fixed symbols or a runtime processor vtable; higher-level code calls cpu_switch_mm, cpu_set_pte_ext, cpu_reset, cpu_do_idle, and cp15 TTBCR/TTBR helpers through these bindings.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/glue-proc.h>, #include <asm/page.h>, #include <linux/smp.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/proc-fns.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/processor.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/processor.h

## Purpose
Defines ARM processor/thread architectural constants and thread_struct state used by scheduler and ptrace-facing code.

## Important APIs, Types, And Functions
Key declarations include struct debug_info {; struct perf_event *hbp[ARM_MAX_HBP_SLOTS];; struct thread_struct {; unsigned long address;; unsigned long trap_no;; unsigned long error_code;. Important macros/constants include __ASM_ARM_PROCESSOR_H, STACK_TOP, STACK_TOP_MAX, INIT_THREAD, start_thread(regs,pc,sp), task_pt_regs(p), KSTK_EIP(tsk), KSTK_ESP(tsk), ARCH_HAS_PREFETCH, ARCH_HAS_PREFETCHW. It depends directly on #include <asm/hw_breakpoint.h>, #include <asm/ptrace.h>, #include <asm/types.h>, #include <asm/unified.h>, #include <asm/vdso/processor.h>.

## Control Flow
Task setup initializes CPU context, restart blocks, and execution-domain state; scheduler switch code saves/restores the fields declared here.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/hw_breakpoint.h>, #include <asm/ptrace.h>, #include <asm/types.h>, #include <asm/unified.h>, #include <asm/vdso/processor.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/procinfo.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/procinfo.h

## Purpose
Defines ARM CPU/procinfo records used during boot-time CPU matching and processor-function table selection.

## Important APIs, Types, And Functions
Key declarations include struct cpu_tlb_fns;; struct cpu_user_fns;; struct cpu_cache_fns;; struct processor;; struct proc_info_list {; unsigned int cpu_val;. Important macros/constants include __ASM_PROCINFO_H. It depends directly on #include <asm/elf.h>.

## Control Flow
Early assembly and C setup compare CPU IDs against proc_info_list entries, then install MMU/cache/proc function pointers for the matched core.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/elf.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/procinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/prom.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/prom.h

## Purpose
Provides ARM Open Firmware/devicetree boot integration declarations.

## Important APIs, Types, And Functions
Key declarations include extern const struct machine_desc *setup_machine_fdt(void *dt_virt);; extern void __init arm_dt_init_cpu_maps(void);; static inline const struct machine_desc *setup_machine_fdt(void *dt_virt); static inline void arm_dt_init_cpu_maps(void) { }. Important macros/constants include __ASMARM_PROM_H.

## Control Flow
Early boot code calls the declared DT setup helpers to parse machine data and pass it into platform discovery.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/prom.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/psci.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/psci.h

## Purpose
Declares ARM PSCI firmware integration used for CPU power, suspend, and system reset/off operations.

## Important APIs, Types, And Functions
Key declarations include extern const struct smp_operations psci_smp_ops;; static inline bool psci_smp_available(void) { return false; }. Important macros/constants include __ASM_ARM_PSCI_H.

## Control Flow
Platform setup detects PSCI conduit and function IDs, then SMP and power-management paths invoke firmware through SMC/HVC wrappers.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/psci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/ptdump.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/ptdump.h

## Purpose
Declares ARM page-table dump/debug structures and entry points.

## Important APIs, Types, And Functions
Key declarations include struct addr_marker {; unsigned long start_address;; struct ptdump_info {; struct mm_struct *mm;; unsigned long base_addr;; void ptdump_walk_pgd(struct seq_file *s, struct ptdump_info *info);. Important macros/constants include __ASM_PTDUMP_H, EFI_RUNTIME_MAP_END, arm_debug_checkwx(), arm_debug_checkwx(). It depends directly on #include <linux/mm_types.h>, #include <linux/seq_file.h>.

## Control Flow
Debugfs or diagnostic code walks kernel page tables and emits decoded ranges using the architecture page-table constants.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/mm_types.h>, #include <linux/seq_file.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/ptdump.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/ptrace.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/ptrace.h

## Purpose
Defines ARM register layout, processor mode/PSR bit constants, syscall-trace helpers, and register accessors for exceptions, ptrace, signals, and core dumps.

## Important APIs, Types, And Functions
Key declarations include struct pt_regs {; unsigned long uregs[18];; struct svc_pt_regs {; struct pt_regs regs;; static inline int valid_user_regs(struct pt_regs *regs); unsigned long mode = regs->ARM_cpsr & MODE_MASK;. Important macros/constants include __ASM_ARM_PTRACE_H, to_svc_pt_regs(r), user_mode(regs), thumb_mode(regs), thumb_mode(regs), isa_mode(regs), isa_mode(regs), processor_mode(regs), interrupts_enabled(regs), fast_interrupts_enabled(regs). It depends directly on #include <uapi/asm/ptrace.h>, #include <linux/bitfield.h>, #include <linux/types.h>, #include <linux/compiler.h>.

## Control Flow
Entry code fills pt_regs; ptrace and signal paths read/write ARM_rN fields and use helper macros to inspect mode, IRQ state, syscall numbers, and user-mode status.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <uapi/asm/ptrace.h>, #include <linux/bitfield.h>, #include <linux/types.h>, #include <linux/compiler.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/ptrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/seccomp.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/seccomp.h

## Purpose
Supplies ARM seccomp architecture constants and syscall argument extraction glue.

## Important APIs, Types, And Functions
Important macros/constants include _ASM_SECCOMP_H, SECCOMP_ARCH_NATIVE, SECCOMP_ARCH_NATIVE_NR, SECCOMP_ARCH_NATIVE_NAME. It depends directly on #include <asm-generic/seccomp.h>.

## Control Flow
Seccomp filters observe syscall numbers and arguments from pt_regs through generic seccomp code.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm-generic/seccomp.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/seccomp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/sections.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/sections.h

## Purpose
Extends generic section boundary declarations with ARM-specific symbols such as vectors and unwind/table ranges.

## Important APIs, Types, And Functions
Key declarations include extern char _exiprom[];; extern char __idmap_text_start[];; extern char __idmap_text_end[];; extern char __entry_text_start[];; extern char __entry_text_end[];; static inline bool in_entry_text(unsigned long addr). Important macros/constants include _ASM_ARM_SECTIONS_H. It depends directly on #include <asm-generic/sections.h>.

## Control Flow
Linker-script symbols are consumed by boot, module, exception-vector, and memory-freeing code after init.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm-generic/sections.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/sections.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/secure_cntvoff.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/secure_cntvoff.h

## Purpose
Declares secure-world counter offset support for systems that need CNTVOFF handling across secure firmware interactions.

## Important APIs, Types, And Functions
Key declarations include extern void secure_cntvoff_init(void);. Important macros/constants include __ASMARM_ARCH_CNTVOFF_H.

## Control Flow
Timer/firmware code can call the exported setup path when secure monitor support is present.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/secure_cntvoff.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/semihost.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/semihost.h

## Purpose
Defines ARM semihosting call helpers used for debug/early platform interaction with a host debugger.

## Important APIs, Types, And Functions
Key declarations include struct uart_port;; static inline void smh_putc(struct uart_port *port, unsigned char c). Important macros/constants include _ARM_SEMIHOST_H_, SEMIHOST_SWI, SEMIHOST_SWI.

## Control Flow
Callers issue semihosting operations through the architecture trap convention and pass operation numbers and argument blocks.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/semihost.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/set_memory.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/set_memory.h

## Purpose
Declares ARM set_memory_* APIs for changing kernel virtual-memory attributes such as RO/RW, NX/X, and cacheability.

## Important APIs, Types, And Functions
Key declarations include int set_memory_ro(unsigned long addr, int numpages);; int set_memory_rw(unsigned long addr, int numpages);; int set_memory_x(unsigned long addr, int numpages);; int set_memory_nx(unsigned long addr, int numpages);; int set_memory_valid(unsigned long addr, int numpages, int enable);; static inline int set_memory_ro(unsigned long addr, int numpages) { return 0; }. Important macros/constants include _ASMARM_SET_MEMORY_H.

## Control Flow
Module loader, BPF/text patching, and debug code call these helpers to update page attributes and flush TLB/cache state.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/set_memory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/setup.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/setup.h

## Purpose
Defines ARM boot parameter, machine setup, and command-line interfaces shared by early architecture setup.

## Important APIs, Types, And Functions
Key declarations include extern int arm_add_memory(u64 start, u64 size);; extern __printf(1, 2) void early_print(const char *str, ...);; extern void dump_machine_table(void);; extern void save_atags(const struct tag *tags);; static inline void save_atags(const struct tag *tags) { }; struct machine_desc;. Important macros/constants include __ASMARM_SETUP_H, __tag, __tagtable(tag,. It depends directly on #include <linux/screen_info.h>, #include <uapi/asm/setup.h>.

## Control Flow
Boot code consumes tags or device-tree input, initializes memory and machine descriptors, and exposes setup data to later init code.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/screen_info.h>, #include <uapi/asm/setup.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/shmparam.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/shmparam.h

## Purpose
Defines ARM shared-memory alignment requirements.

## Important APIs, Types, And Functions
Important macros/constants include _ASMARM_SHMPARAM_H, SHMLBA, __ARCH_FORCE_SHMLBA.

## Control Flow
System V shared-memory mmap placement uses SHMLBA so VIPT aliasing caches avoid harmful synonyms.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/shmparam.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/signal.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/signal.h

## Purpose
Provides ARM signal ABI declarations and includes UAPI signal definitions.

## Important APIs, Types, And Functions
Key declarations include typedef unsigned long old_sigset_t; /* at least 32 bits */; typedef struct {; unsigned long sig[_NSIG_WORDS];; void do_rseq_syscall(struct pt_regs *regs);; int do_work_pending(struct pt_regs *regs, unsigned int thread_flags,; int syscall);. Important macros/constants include _ASMARM_SIGNAL_H, _NSIG, _NSIG_BPW, _NSIG_WORDS, __ARCH_UAPI_SA_FLAGS, __ARCH_HAS_SA_RESTORER. It depends directly on #include <uapi/asm/signal.h>, #include <asm/sigcontext.h>.

## Control Flow
Signal delivery and return paths use the architecture stack frame definitions and generic signal constants.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <uapi/asm/signal.h>, #include <asm/sigcontext.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/simd.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/simd.h

## Purpose
Provides generic SIMD-in-kernel capability hooks for ARM, tying SIMD availability to NEON state management.

## Important APIs, Types, And Functions
Important macros/constants include _ASM_SIMD_H, scoped_ksimd(). It depends directly on #include <linux/cleanup.h>, #include <linux/compiler_attributes.h>, #include <linux/preempt.h>, #include <linux/types.h>, #include <asm/neon.h>.

## Control Flow
Callers use may_use_simd and kernel_neon_begin/end style guards before executing vector code.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/cleanup.h>, #include <linux/compiler_attributes.h>, #include <linux/preempt.h>, #include <linux/types.h>, #include <asm/neon.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/simd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/smp.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/smp.h

## Purpose
Declares ARM SMP boot, IPI, CPU hotplug, and secondary-start interfaces.

## Important APIs, Types, And Functions
Key declarations include struct seq_file;; extern void show_ipi_list(struct seq_file *, int);; void handle_IPI(int ipinr, struct pt_regs *regs);; extern void smp_init_cpus(void);; extern void set_smp_ipi_range(int ipi_base, int nr_ipi);; asmlinkage void secondary_start_kernel(struct task_struct *task);. Important macros/constants include __ASM_ARM_SMP_H, raw_smp_processor_id(), CPU_METHOD_OF_DECLARE(name,. It depends directly on #include <linux/threads.h>, #include <linux/cpumask.h>, #include <linux/thread_info.h>.

## Control Flow
Primary CPU platform code sets smp operations, starts secondary CPUs, handles IPIs, and coordinates hotplug callbacks through these declarations.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/threads.h>, #include <linux/cpumask.h>, #include <linux/thread_info.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/smp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/smp_plat.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/smp_plat.h

## Purpose
Supplies ARM platform SMP helpers for MPIDR affinity decoding and logical/physical CPU mapping.

## Important APIs, Types, And Functions
Key declarations include static inline bool is_smp(void); extern unsigned int smp_on_up;; static inline unsigned int smp_cpuid_part(int cpu); struct cpuinfo_arm *cpu_info = &per_cpu(cpu_data, cpu);; static inline int tlb_ops_need_broadcast(void); static inline int cache_ops_need_broadcast(void). Important macros/constants include __ASMARM_SMP_PLAT_H, tlb_ops_need_broadcast(), cache_ops_need_broadcast(), cpu_logical_map(cpu). It depends directly on #include <linux/cpumask.h>, #include <linux/err.h>, #include <asm/cpu.h>, #include <asm/cputype.h>.

## Control Flow
SMP setup reads MPIDR values, converts cluster/CPU affinity into linear indexes, and stores mappings used by hotplug and power-management code.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/cpumask.h>, #include <linux/err.h>, #include <asm/cpu.h>, #include <asm/cputype.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/smp_plat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/smp_scu.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/smp_scu.h

## Purpose
Declares Snoop Control Unit helper functions for ARM Cortex-A style SMP systems.

## Important APIs, Types, And Functions
Key declarations include static inline bool scu_a9_has_base(void); static inline unsigned long scu_a9_get_base(void); unsigned long pa;; unsigned int scu_get_core_count(void __iomem *);; int scu_power_mode(void __iomem *, unsigned int);; int scu_cpu_power_enable(void __iomem *, unsigned int);. Important macros/constants include __ASMARM_ARCH_SCU_H, SCU_PM_NORMAL, SCU_PM_DORMANT, SCU_PM_POWEROFF. It depends directly on #include <linux/errno.h>, #include <asm/cputype.h>.

## Control Flow
Platform SMP setup enables SCU coherency and queries core count through the memory-mapped SCU base.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/errno.h>, #include <asm/cputype.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/smp_scu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/smp_twd.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/smp_twd.h

## Purpose
Declares twd local timer setup for ARM SMP systems with a per-CPU private timer/watchdog block.

## Important APIs, Types, And Functions
Important macros/constants include __ASMARM_SMP_TWD_H, TWD_TIMER_LOAD, TWD_TIMER_COUNTER, TWD_TIMER_CONTROL, TWD_TIMER_INTSTAT, TWD_WDOG_LOAD, TWD_WDOG_COUNTER, TWD_WDOG_CONTROL, TWD_WDOG_INTSTAT, TWD_WDOG_RESETSTAT.

## Control Flow
Timer init registers the per-CPU local timer using the provided base address and IRQ.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/smp_twd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/sparsemem.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/sparsemem.h

## Purpose
Defines ARM sparsemem section sizing and physical address bit limits.

## Important APIs, Types, And Functions
Important macros/constants include ASMARM_SPARSEMEM_H, MAX_PHYSMEM_BITS, SECTION_SIZE_BITS. It depends directly on #include <asm/page.h>.

## Control Flow
Memory model code uses the constants to convert PFNs to sparsemem sections and size mem_section arrays.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/page.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/sparsemem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/spectre.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/spectre.h

## Purpose
Declares ARM Spectre mitigation selection, branch predictor hardening, and firmware workaround interfaces.

## Important APIs, Types, And Functions
Key declarations include enum {; enum {; enum {; void spectre_v2_update_state(unsigned int state, unsigned int methods);; static inline void spectre_v2_update_state(unsigned int state,; unsigned int methods). Important macros/constants include __ASM_SPECTRE_H.

## Control Flow
CPU bring-up and alternative patching choose mitigation callbacks; exception/user-copy paths use the resulting barriers or branch predictor sequences.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/spectre.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/spinlock.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/spinlock.h

## Purpose
Implements ARMv6+ ticket spinlocks and read/write locks using LDREX/STREX, WFE/SEV, and explicit memory barriers.

## Important APIs, Types, And Functions
Key declarations include static inline void dsb_sev(void); static inline void arch_spin_lock(arch_spinlock_t *lock); unsigned long tmp;; static inline int arch_spin_trylock(arch_spinlock_t *lock); unsigned long contended, res;; static inline void arch_spin_unlock(arch_spinlock_t *lock). Important macros/constants include __ASM_SPINLOCK_H, WFE(cond), WFE(cond), SEV, arch_spin_is_contended. It depends directly on #include <linux/prefetch.h>, #include <asm/barrier.h>, #include <asm/processor.h>.

## Control Flow
Lock acquisition atomically increments ticket counters or read counts, waits with WFE when contended, and unlock paths publish state with smp_mb plus dsb_sev to wake waiters.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/prefetch.h>, #include <asm/barrier.h>, #include <asm/processor.h>.

## Risks And Edge Cases
Ordering and wakeup details are concurrency-critical; missing barriers or broken WFE/SEV alternatives can deadlock SMP systems or expose protected data before lock acquisition is complete.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/spinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/spinlock_types.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/spinlock_types.h

## Purpose
Defines the ARM raw spinlock and rwlock storage layout, including ticket fields and initializer values.

## Important APIs, Types, And Functions
Key declarations include typedef struct {; struct __raw_tickets {; typedef struct {. Important macros/constants include __ASM_SPINLOCK_TYPES_H, TICKET_SHIFT, __ARCH_SPIN_LOCK_UNLOCKED, __ARCH_RW_LOCK_UNLOCKED.

## Control Flow
spinlock.h and generic locking code rely on the exact owner/next packing and rwlock integer representation.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Ordering and wakeup details are concurrency-critical; missing barriers or broken WFE/SEV alternatives can deadlock SMP systems or expose protected data before lock acquisition is complete.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/spinlock_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/stackprotector.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/stackprotector.h

## Purpose
Implements ARM stack canary initialization glue for CONFIG_STACKPROTECTOR.

## Important APIs, Types, And Functions
Key declarations include extern unsigned long __stack_chk_guard;; unsigned long canary = get_random_canary();. Important macros/constants include _ASM_STACKPROTECTOR_H. It depends directly on #include <asm/thread_info.h>.

## Control Flow
Task or CPU setup seeds the current canary from randomness and stores it where compiler-emitted stack-protector checks expect it.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/thread_info.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/stackprotector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/stacktrace.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/stacktrace.h

## Purpose
Defines ARM stack-frame layout and stack walking interfaces.

## Important APIs, Types, And Functions
Key declarations include struct stackframe {; unsigned long fp;; unsigned long sp;; unsigned long lr;; unsigned long pc;; unsigned long *lr_addr;. Important macros/constants include __ASM_STACKTRACE_H. It depends directly on #include <linux/llist.h>, #include <asm/ptrace.h>, #include <asm/sections.h>.

## Control Flow
Unwind/backtrace code walks frame pointers or unwind tables through the frame_tail/frame records and callback interfaces.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/llist.h>, #include <asm/ptrace.h>, #include <asm/sections.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/stacktrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/string.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/string.h

## Purpose
Declares ARM-optimized string/memory routines or selects generic implementations depending on configuration.

## Important APIs, Types, And Functions
Key declarations include extern char * strrchr(const char * s, int c);; extern char * strchr(const char * s, int c);; extern void * memcpy(void *, const void *, __kernel_size_t);; extern void *__memcpy(void *dest, const void *src, __kernel_size_t n);; extern void * memmove(void *, const void *, __kernel_size_t);; extern void *__memmove(void *dest, const void *src, __kernel_size_t n);. Important macros/constants include __ASM_ARM_STRING_H, __HAVE_ARCH_STRRCHR, __HAVE_ARCH_STRCHR, __HAVE_ARCH_MEMCPY, __HAVE_ARCH_MEMMOVE, __HAVE_ARCH_MEMCHR, __HAVE_ARCH_MEMSET, __HAVE_ARCH_MEMSET32, memcpy(dst,, memmove(dst,.

## Control Flow
The C library and kernel helpers bind memcpy, memmove, memset, and string operations to architecture routines when available.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/string.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/suspend.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/suspend.h

## Purpose
Declares ARM CPU suspend state structures and low-level suspend/resume entry points.

## Important APIs, Types, And Functions
Key declarations include struct sleep_save_sp {; extern void cpu_resume(void);; extern void cpu_resume_no_hyp(void);; extern void cpu_resume_arm(void);; extern int cpu_suspend(unsigned long, int (*)(unsigned long));; extern void __cpu_suspend_save(u32 *ptr, u32 ptrsz, u32 sp, u32 *save_ptr);. Important macros/constants include __ASM_ARM_SUSPEND_H. It depends directly on #include <linux/types.h>.

## Control Flow
Power-management code saves CPU context, calls firmware/platform suspend, then resumes through cpu_resume and restore helpers.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/types.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/suspend.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/swab.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/swab.h

## Purpose
Provides ARM byte-swap helpers or generic fallbacks for endian conversions.

## Important APIs, Types, And Functions
Key declarations include static inline __attribute_const__ __u32 __arch_swahb32(__u32 x); static inline __attribute_const__ __u32 __arch_swab32(__u32 x). Important macros/constants include __ASM_ARM_SWAB_H, __arch_swahb32, __arch_swab16(x), __arch_swab32. It depends directly on #include <uapi/asm/swab.h>.

## Control Flow
Callers use swab operations that may compile to efficient ARM rotate/rev instruction sequences.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <uapi/asm/swab.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/swab.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/switch_to.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/switch_to.h

## Purpose
Defines the ARM context-switch macro that invokes __switch_to with previous and next task/thread state.

## Important APIs, Types, And Functions
Key declarations include extern struct task_struct *__switch_to(struct task_struct *, struct thread_info *, struct thread_info *);. Important macros/constants include __ASM_ARM_SWITCH_TO_H, __complete_pending_tlbi(), __complete_pending_tlbi(), switch_to(prev,next,last). It depends directly on #include <linux/thread_info.h>, #include <asm/smp_plat.h>.

## Control Flow
The scheduler calls switch_to; low-level assembly saves callee-saved registers and restores the next task cpu_context.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/thread_info.h>, #include <asm/smp_plat.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/switch_to.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/sync_bitops.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/sync_bitops.h

## Purpose
Includes synchronized atomic bit operation definitions for ARM.

## Important APIs, Types, And Functions
Key declarations include int _sync_test_and_set_bit(int nr, volatile unsigned long * p);; int _sync_test_and_clear_bit(int nr, volatile unsigned long * p);; int _sync_test_and_change_bit(int nr, volatile unsigned long * p);. Important macros/constants include __ASM_SYNC_BITOPS_H__, sync_set_bit(nr,, sync_clear_bit(nr,, sync_change_bit(nr,, sync_test_bit(nr,, sync_test_and_set_bit(nr,, sync_test_and_clear_bit(nr,, sync_test_and_change_bit(nr,, arch_sync_cmpxchg(ptr,. It depends directly on #include <asm/bitops.h>.

## Control Flow
Callers needing ordered bit operations use these wrappers rather than relaxed non-atomic bit helpers.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/bitops.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/sync_bitops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/syscall.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/syscall.h

## Purpose
Defines ARM syscall inspection and mutation helpers for tracing, audit, seccomp, and restart handling.

## Important APIs, Types, And Functions
Key declarations include extern const unsigned long sys_call_table[];; static inline int syscall_get_nr(struct task_struct *task,; struct pt_regs *regs); static inline bool __in_oabi_syscall(struct task_struct *task); static inline bool in_oabi_syscall(void); static inline void syscall_rollback(struct task_struct *task,. Important macros/constants include _ASM_ARM_SYSCALL_H, NR_syscalls. It depends directly on #include <uapi/linux/audit.h> /* for AUDIT_ARCH_* */, #include <linux/elf.h> /* for ELF_EM */, #include <linux/err.h>, #include <linux/sched.h>, #include <asm/unistd.h>.

## Control Flow
Entry code populates pt_regs; tracing code reads syscall numbers/arguments, changes return values, and identifies ABI variants through these helpers.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <uapi/linux/audit.h> /* for AUDIT_ARCH_* */, #include <linux/elf.h> /* for ELF_EM */, #include <linux/err.h>, #include <linux/sched.h>, #include <asm/unistd.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/syscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/syscalls.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/syscalls.h

## Purpose
Declares ARM-specific syscall entry points not covered by generic syscall prototypes.

## Important APIs, Types, And Functions
Key declarations include struct pt_regs;; asmlinkage int sys_sigreturn(struct pt_regs *regs);; asmlinkage int sys_rt_sigreturn(struct pt_regs *regs);; asmlinkage long sys_arm_fadvise64_64(int fd, int advice,; struct oldabi_stat64;; asmlinkage long sys_oabi_stat64(const char __user * filename,. Important macros/constants include __ASM_SYSCALLS_H. It depends directly on #include <linux/linkage.h>, #include <linux/types.h>.

## Control Flow
The syscall table and compat/OABI paths reference these prototypes during build and entry dispatch.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/linkage.h>, #include <linux/types.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/syscalls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/system_info.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/system_info.h

## Purpose
Declares global ARM system identity variables such as processor ID, architecture, ELF hardware caps, and cache type.

## Important APIs, Types, And Functions
Key declarations include extern unsigned int system_rev;; extern const char *system_serial;; extern unsigned int system_serial_low;; extern unsigned int system_serial_high;; extern unsigned int mem_fclk_21285;; extern int __pure cpu_architecture(void);. Important macros/constants include __ASM_ARM_SYSTEM_INFO_H, CPU_ARCH_UNKNOWN, CPU_ARCH_ARMv3, CPU_ARCH_ARMv4, CPU_ARCH_ARMv4T, CPU_ARCH_ARMv5, CPU_ARCH_ARMv5T, CPU_ARCH_ARMv5TE, CPU_ARCH_ARMv5TEJ, CPU_ARCH_ARMv6.

## Control Flow
CPU detection fills these globals during boot; feature tests and proc/sysfs reporting read them later.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/system_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/system_misc.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/system_misc.h

## Purpose
Declares miscellaneous ARM system control hooks such as restart, idle, die handling, and process abort support.

## Important APIs, Types, And Functions
Key declarations include extern void cpu_init(void);; void soft_restart(unsigned long);; extern void (*arm_pm_idle)(void);; typedef void (*harden_branch_predictor_fn_t)(void);; static inline void harden_branch_predictor(void); extern unsigned int user_debug;. Important macros/constants include __ASM_ARM_SYSTEM_MISC_H, harden_branch_predictor(), UDBG_UNDEFINED, UDBG_SYSCALL, UDBG_BADABORT, UDBG_SEGV, UDBG_BUS. It depends directly on #include <linux/compiler.h>, #include <linux/linkage.h>, #include <linux/irqflags.h>, #include <linux/reboot.h>, #include <linux/percpu.h>.

## Control Flow
Platform and exception code route resets, fatal traps, and restart-mode selection through these architecture hooks.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/compiler.h>, #include <linux/linkage.h>, #include <linux/irqflags.h>, #include <linux/reboot.h>, #include <linux/percpu.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/system_misc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/tcm.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/tcm.h

## Purpose
Declares tightly coupled memory section markers, allocation helpers, and copy routines for ARM TCM support.

## Important APIs, Types, And Functions
Key declarations include void *tcm_alloc(size_t len);; void tcm_free(void *addr, size_t len);; void __init tcm_init(void);; static inline void tcm_init(void). Important macros/constants include __ASMARM_TCM_H, __tcmdata, __tcmconst, __tcmfunc, __tcmlocalfunc. It depends directly on #include <linux/compiler.h>.

## Control Flow
Boot/linker code maps ITCM/DTCM sections at fixed virtual addresses and platform code can allocate or copy data into TCM.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/compiler.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/tcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/text-patching.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/text-patching.h

## Purpose
Declares ARM kernel text patching helpers for modifying instructions at runtime.

## Important APIs, Types, And Functions
Key declarations include void patch_text(void *addr, unsigned int insn);; void __patch_text_real(void *addr, unsigned int insn, bool remap);; static inline void __patch_text(void *addr, unsigned int insn); static inline void __patch_text_early(void *addr, unsigned int insn). Important macros/constants include _ARM_KERNEL_PATCH_H.

## Control Flow
Alternatives, probes, and mitigation code patch instruction words with cache/TLB synchronization so CPUs execute the new text safely.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/text-patching.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/therm.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/therm.h

## Purpose
Declares ARM thermal or SoC-specific temperature support hook points when present.

## Important APIs, Types, And Functions
Key declarations include struct therm {; int hi;; int lo;. Important macros/constants include __ASM_THERM_H, CMD_SET_THERMOSTATE, CMD_GET_THERMOSTATE, CMD_GET_STATUS, CMD_GET_TEMPERATURE, CMD_SET_THERMOSTATE2, CMD_GET_THERMOSTATE2, CMD_GET_TEMPERATURE2, CMD_GET_FAN, CMD_SET_FAN.

## Control Flow
Platform thermal drivers can include this header for architecture-visible thermal integration.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/therm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/thread_info.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/thread_info.h

## Purpose
Defines ARM low-level thread_info, saved CPU register context, thread flag bits, syscall-work masks, stack sizing, and VFP/IWMMXT task-state hooks.

## Important APIs, Types, And Functions
Key declarations include struct task_struct;; struct cpu_context_save {; struct thread_info {; unsigned long flags; /* low level flags */; struct cpu_context_save cpu_context; /* cpu context */; unsigned long tp_value[2]; /* TLS registers */. Important macros/constants include __ASM_ARM_THREAD_INFO_H, THREAD_SIZE_ORDER, THREAD_SIZE_ORDER, THREAD_SIZE, THREAD_START_SP, THREAD_ALIGN, THREAD_ALIGN, OVERFLOW_STACK_SIZE, INIT_THREAD_INFO(tsk), thread_saved_pc(tsk). It depends directly on #include <linux/compiler.h>, #include <asm/fpstate.h>, #include <asm/page.h>, #include <asm/types.h>, #include <asm/traps.h>.

## Control Flow
Entry assembly and scheduler code access fixed offsets in thread_info, while signal/FPU code preserves or restores VFP/IWMMXT state around task switches and user transitions.

## State And Persistence
State persists per task in thread_info: flags, preempt count, CPU number, domain, saved CPU context, TLS values, and floating-point/copressor state.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/compiler.h>, #include <asm/fpstate.h>, #include <asm/page.h>, #include <asm/types.h>, #include <asm/traps.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/thread_info.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/thread_notify.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/thread_notify.h

## Purpose
Defines notifier infrastructure for ARM thread lifecycle events.

## Important APIs, Types, And Functions
Key declarations include static inline int thread_register_notifier(struct notifier_block *n); extern struct atomic_notifier_head thread_notify_head;; static inline void thread_unregister_notifier(struct notifier_block *n); extern struct atomic_notifier_head thread_notify_head;; static inline void thread_notify(unsigned long rc, struct thread_info *thread); extern struct atomic_notifier_head thread_notify_head;. Important macros/constants include ASMARM_THREAD_NOTIFY_H, THREAD_NOTIFY_FLUSH, THREAD_NOTIFY_EXIT, THREAD_NOTIFY_SWITCH, THREAD_NOTIFY_COPY. It depends directly on #include <linux/notifier.h>, #include <asm/thread_info.h>.

## Control Flow
Subsystems register callbacks to observe thread flush, copy, switch, and release events for coprocessor or platform state.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/notifier.h>, #include <asm/thread_info.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/thread_notify.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/timex.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/timex.h

## Purpose
Defines ARM clock tick type and timer frequency assumptions for generic timekeeping.

## Important APIs, Types, And Functions
Key declarations include typedef unsigned long cycles_t;. Important macros/constants include _ASMARM_TIMEX_H, get_cycles(), random_get_entropy().

## Control Flow
Timekeeping code includes these constants when converting cycle counter values and configuring legacy timer paths.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/timex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/tlb.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/tlb.h

## Purpose
Provides ARM TLB-gather integration with generic MMU page-table teardown.

## Important APIs, Types, And Functions
Key declarations include static inline void; struct ptdesc *ptdesc = page_ptdesc(pte);; static inline void; struct ptdesc *ptdesc = virt_to_ptdesc(pmdp);. Important macros/constants include __ASMARM_TLB_H, tlb_flush(tlb). It depends directly on #include <asm/cacheflush.h>, #include <linux/pagemap.h>, #include <asm-generic/tlb.h>, #include <asm/tlbflush.h>, #include <asm-generic/tlb.h>.

## Control Flow
Unmap paths batch freed page tables and TLB invalidations through generic tlb_gather_mmu hooks plus ARM cache/TLB requirements.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/cacheflush.h>, #include <linux/pagemap.h>, #include <asm-generic/tlb.h>, #include <asm/tlbflush.h>, #include <asm-generic/tlb.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Signals include ARM allnoconfig/defconfig builds across MMU/NoMMU and LPAE variants, boot tests, vmalloc/module loading, mmap/mprotect/hugetlb where applicable, and MM selftests that exercise faults and TLB shootdowns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/tlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/tlbflush.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/tlbflush.h

## Purpose
Defines ARM TLB model flags, CPU-specific flush function dispatch, and generic flush_tlb_* helpers for full, mm, range, page, kernel-range, and ASID invalidation.

## Important APIs, Types, And Functions
Key declarations include struct cpu_tlb_fns {; void (*flush_user_range)(unsigned long, unsigned long, struct vm_area_struct *);; void (*flush_kern_range)(unsigned long, unsigned long);; unsigned long tlb_flags;; extern void __cpu_flush_user_tlb_range(unsigned long, unsigned long, struct vm_area_struct *);; extern void __cpu_flush_kern_tlb_range(unsigned long, unsigned long);. Important macros/constants include _ASMARM_TLBFLUSH_H, TLB_V4_U_PAGE, TLB_V4_D_PAGE, TLB_V4_I_PAGE, TLB_V6_U_PAGE, TLB_V6_D_PAGE, TLB_V6_I_PAGE, TLB_V4_U_FULL, TLB_V4_D_FULL, TLB_V4_I_FULL. It depends directly on #include <asm/glue.h>, #include <linux/sched.h>.

## Control Flow
Build-time CPU TLB selection sets possible/always flags; runtime flush helpers clean data or outer cache when required, call CPU-specific assembly range flushers, and issue barriers/broadcast operations according to SMP and architecture flags.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated with the generic Linux MM, scheduler, exception, and cache/TLB subsystems. Dependencies include #include <asm/glue.h>, #include <linux/sched.h>, CP15 processor helpers, and configuration choices such as CONFIG_MMU, CONFIG_ARM_LPAE, CONFIG_SMP, and CPU feature selections.

## Risks And Edge Cases
Bit definitions and barriers are ABI-critical. Incorrect masks, missing cache/TLB maintenance, wrong ASID handling, or bad user-access bounds can cause silent memory corruption, stale translations, privilege bypass, or hard-to-debug boot failures.

## Test Signals
Signals include ARM allnoconfig/defconfig builds across MMU/NoMMU and LPAE variants, boot tests, vmalloc/module loading, mmap/mprotect/hugetlb where applicable, and MM selftests that exercise faults and TLB shootdowns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/tlbflush.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/tls.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/tls.h

## Purpose
Defines ARM TLS register access, user helper page conventions, and thread TLS save/restore hooks.

## Important APIs, Types, And Functions
Key declarations include static inline void set_tls(unsigned long val); struct thread_info *thread;; static inline unsigned long get_tpuser(void); unsigned long reg = 0;; static inline void set_tpuser(unsigned long val); static inline void flush_tls(void). Important macros/constants include __ASMARM_TLS_H, tls_emu, has_tls_reg, defer_tls_reg_update, switch_tls, tls_emu, has_tls_reg, defer_tls_reg_update, switch_tls, tls_emu. Assembly macros include .macro switch_tls_none, base, tp, tpuser, tmp1, tmp2, .macro switch_tls_v6k, base, tp, tpuser, tmp1, tmp2, .macro switch_tls_v6, base, tp, tpuser, tmp1, tmp2, .macro switch_tls_software, base, tp, tpuser, tmp1, tmp2. It depends directly on #include <linux/compiler.h>, #include <asm/thread_info.h>, #include <asm/asm-offsets.h>, #include <asm/smp_plat.h>.

## Control Flow
Context-switch and exec paths update per-task tp_value slots and write CP15/thread pointer state for EABI/OABI userland.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/compiler.h>, #include <asm/thread_info.h>, #include <asm/asm-offsets.h>, #include <asm/smp_plat.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/tls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/topology.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/topology.h

## Purpose
Provides ARM CPU topology hooks and default scheduling topology integration.

## Important APIs, Types, And Functions
Key declarations include static inline void init_cpu_topology(void) { }; static inline void store_cpu_topology(unsigned int cpuid) { }. Important macros/constants include _ASM_ARM_TOPOLOGY_H, arch_set_freq_scale, arch_scale_freq_capacity, arch_scale_freq_invariant, arch_scale_freq_ref, arch_scale_cpu_capacity, arch_update_cpu_topology, arch_scale_hw_pressure, arch_update_hw_pressure. It depends directly on #include <linux/cpumask.h>, #include <linux/arch_topology.h>, #include <asm-generic/topology.h>.

## Control Flow
SMP setup can populate topology from MPIDR or device tree so scheduler domains understand clusters/cores.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/cpumask.h>, #include <linux/arch_topology.h>, #include <asm-generic/topology.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/topology.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/traps.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/traps.h

## Purpose
Declares ARM exception/trap registration, undefined-instruction hooks, die handling, and pt_regs reporting interfaces.

## Important APIs, Types, And Functions
Key declarations include struct pt_regs;; struct task_struct;; struct undef_hook {; struct list_head node;; int (*fn)(struct pt_regs *regs, unsigned int instr);; void register_undef_hook(struct undef_hook *hook);. Important macros/constants include _ASMARM_TRAP_H. It depends directly on #include <linux/linkage.h>, #include <linux/list.h>.

## Control Flow
Exception entry calls trap handlers; subsystems such as VFP/IWMMXT/probes register undef hooks that match instruction masks and processor modes.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/linkage.h>, #include <linux/list.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/traps.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/uaccess-asm.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/uaccess-asm.h

## Purpose
Defines assembly macros and constants for ARM user-access routines, including fault-table labels and address-limit checks.

## Important APIs, Types, And Functions
Important macros/constants include __ASM_UACCESS_ASM_H__, DACR(x...), DACR(x...), PAN(x...), PAN(x...). Assembly macros include .macro csdb, .macro check_uaccess, addr:req, size:req, limit:req, tmp:req, bad:req, .macro uaccess_mask_range_ptr, addr:req, size:req, limit:req, tmp:req, .macro uaccess_disable, tmp, isb=1, .macro uaccess_enable, tmp, isb=1, .macro uaccess_disable, tmp, isb=1, .macro uaccess_enable, tmp, isb=1, .macro uaccess_disable, tmp, isb=1. It depends directly on #include <asm/asm-offsets.h>, #include <asm/domain.h>, #include <asm/page.h>, #include <asm/thread_info.h>.

## Control Flow
Low-level copy/get/put user assembly includes these macros to validate user addresses and branch to exception fixups.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/asm-offsets.h>, #include <asm/domain.h>, #include <asm/page.h>, #include <asm/thread_info.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Signals include uaccess fault-injection tests, copy_to/from_user and get_user/put_user behavior across valid and invalid pointers, seccomp/ptrace syscall tests, and Spectre/PAN configuration boot tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/uaccess-asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/uaccess.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/uaccess.h

## Purpose
Implements ARM user-memory access API, including PAN enable/restore hooks, range masking, get_user/put_user assembly callouts, raw copy helpers, clear_user, and Spectre-aware access behavior.

## Important APIs, Types, And Functions
Key declarations include unsigned int old_domain = get_domain();; unsigned int old_ttbcr = cpu_get_ttbcr();; static inline void uaccess_restore(unsigned int flags); static inline unsigned int uaccess_save_and_enable(void); static inline void uaccess_restore(unsigned int flags); extern int __get_user_bad(void);. Important macros/constants include _ASMARM_UACCESS_H, __inttype(x), uaccess_mask_range_ptr(ptr,, __get_user_x(__r2,, __get_user_x_32t(__r2,, __get_user_x_32t, __get_user_x_64t(__r2,, __get_user_x_64t, get_user(x,, get_user(x,. It depends directly on #include <linux/kernel.h>, #include <linux/string.h>, #include <asm/page.h>, #include <asm/domain.h>, #include <linux/unaligned.h>, #include <asm/unified.h>.

## Control Flow
Public get_user/put_user paths call might_fault, temporarily enable user access through domain or TTBR0 PAN controls, dispatch by operand size to assembly helpers, restore access restrictions, and rely on exception tables to return -EFAULT and zero failed reads.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated with the generic Linux MM, scheduler, exception, and cache/TLB subsystems. Dependencies include #include <linux/kernel.h>, #include <linux/string.h>, #include <asm/page.h>, #include <asm/domain.h>, #include <linux/unaligned.h>, #include <asm/unified.h>, #include <asm/pgtable.h>, #include <asm/proc-fns.h>, CP15 processor helpers, and configuration choices such as CONFIG_MMU, CONFIG_ARM_LPAE, CONFIG_SMP, and CPU feature selections.

## Risks And Edge Cases
Bit definitions and barriers are ABI-critical. Incorrect masks, missing cache/TLB maintenance, wrong ASID handling, or bad user-access bounds can cause silent memory corruption, stale translations, privilege bypass, or hard-to-debug boot failures.

## Test Signals
Signals include uaccess fault-injection tests, copy_to/from_user and get_user/put_user behavior across valid and invalid pointers, seccomp/ptrace syscall tests, and Spectre/PAN configuration boot tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/uaccess.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/ucontext.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/ucontext.h

## Purpose
Defines ARM signal ucontext linkage by including the UAPI ucontext layout.

## Important APIs, Types, And Functions
Key declarations include struct ucontext {; unsigned long uc_flags;; struct ucontext *uc_link;; struct sigcontext uc_mcontext;; unsigned long uc_regspace[128] __attribute__((__aligned__(8)));; struct iwmmxt_sigframe {. Important macros/constants include _ASMARM_UCONTEXT_H, DUMMY_MAGIC, IWMMXT_MAGIC, IWMMXT_STORAGE_SIZE, VFP_MAGIC, VFP_STORAGE_SIZE. It depends directly on #include <asm/fpstate.h>, #include <asm/user.h>.

## Control Flow
Signal delivery and sigreturn use the UAPI frame shape to save and restore user register/FPU state.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/fpstate.h>, #include <asm/user.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/ucontext.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/unified.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/unified.h

## Purpose
Provides assembler compatibility macros for unified ARM/Thumb syntax.

## Important APIs, Types, And Functions
Important macros/constants include __ASM_UNIFIED_H, AR_CLASS(x...), M_CLASS(x...), AR_CLASS(x...), M_CLASS(x...), PSR_ISETSTATE, ARM(x...), THUMB(x...), W(instr), WASM(instr).

## Control Flow
Assembly headers include it so macros assemble correctly across ARM and Thumb-2 kernel builds.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/unified.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/unistd.h

## Purpose
Defines ARM syscall-number selection, ABI compatibility wants, ignored legacy syscalls, and inclusion of generated syscall tables.

## Important APIs, Types, And Functions
Important macros/constants include __ASM_ARM_UNISTD_H, __ARCH_WANT_NEW_STAT, __ARCH_WANT_STAT64, __ARCH_WANT_SYS_GETHOSTNAME, __ARCH_WANT_SYS_PAUSE, __ARCH_WANT_SYS_GETPGRP, __ARCH_WANT_SYS_NICE, __ARCH_WANT_SYS_SIGPENDING. It depends directly on #include <uapi/asm/unistd.h>, #include <asm/unistd-nr.h>.

## Control Flow
Build-time syscall table generation and entry code use the __ARCH_WANT_* and __IGNORE_* definitions to expose ARM-compatible system calls.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <uapi/asm/unistd.h>, #include <asm/unistd-nr.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/unistd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/unwind.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/unwind.h

## Purpose
Defines ARM exception unwind table structures, unwind reason codes, table registration, and backtrace entry points.

## Important APIs, Types, And Functions
Key declarations include enum unwind_reason_code {; struct unwind_idx {; unsigned long addr_offset;; unsigned long insn;; struct unwind_table {; struct list_head list;. Important macros/constants include __ASM_UNWIND_H, UNWIND(code...), UNWIND(code...).

## Control Flow
Built-in and module unwind tables are registered, then oops/backtrace code walks unwind_idx entries or emits AEABI personality references when CONFIG_ARM_UNWIND is enabled.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/unwind.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/uprobes.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/uprobes.h

## Purpose
Defines ARM uprobes breakpoint opcodes, XOL slot size, per-task saved trap state, and arch_uprobe handler hooks.

## Important APIs, Types, And Functions
Key declarations include typedef u32 uprobe_opcode_t;; struct arch_uprobe_task {; unsigned long saved_trap_no;; struct arch_uprobe {; unsigned long ixol[2];; void (*prehandler)(struct arch_uprobe *auprobe,. Important macros/constants include _ASM_UPROBES_H, MAX_UINSN_BYTES, UPROBE_XOL_SLOT_BYTES, UPROBE_SWBP_ARM_INSN, UPROBE_SS_ARM_INSN, UPROBE_SWBP_INSN, UPROBE_SWBP_INSN_SIZE. It depends directly on #include <asm/probes.h>, #include <asm/opcodes.h>.

## Control Flow
Uprobe installation copies and decodes target instructions, replaces them with the ARM breakpoint opcode, and emulates/single-steps through pre/post handlers.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/probes.h>, #include <asm/opcodes.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/uprobes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/user.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/user.h

## Purpose
Defines legacy ARM user core-dump structures, including general register, FPA, VFP, and VFP exception state layouts visible to debuggers.

## Important APIs, Types, And Functions
Key declarations include struct user_fp {; struct fp_reg {; unsigned int sign1:1;; unsigned int unused:15;; unsigned int sign2:1;; unsigned int exponent:14;. Important macros/constants include _ARM_USER_H. It depends directly on #include <asm/page.h>, #include <asm/ptrace.h>.

## Control Flow
Core dump and ptrace consumers read these structures to interpret saved user CPU and floating-point state.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/page.h>, #include <asm/ptrace.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/user.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/v7m.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/v7m.h

## Purpose
Defines ARMv7-M system-control, exception, cache, MPU register offsets, exception-return bits, and restart hook declarations.

## Important APIs, Types, And Functions
Key declarations include enum reboot_mode;; void armv7m_restart(enum reboot_mode mode, const char *cmd);. Important macros/constants include V7M_SCS_ICTR, V7M_SCS_ICTR_INTLINESNUM_MASK, BASEADDR_V7M_SCB, V7M_SCB_CPUID, V7M_SCB_ICSR, V7M_SCB_ICSR_PENDSVSET, V7M_SCB_ICSR_PENDSVCLR, V7M_SCB_ICSR_RETTOBASE, V7M_SCB_ICSR_VECTACTIVE, V7M_SCB_VTOR.

## Control Flow
v7-M boot and exception code programs SCB/MPU/cache registers and uses armv7m_restart for system reset.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/v7m.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/vdso.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/vdso.h

## Purpose
Declares ARM vDSO page count and installation hook for mapping fast time helpers into a process.

## Important APIs, Types, And Functions
Key declarations include struct mm_struct;; void arm_install_vdso(struct mm_struct *mm, unsigned long addr);; extern unsigned int vdso_total_pages;; static inline void arm_install_vdso(struct mm_struct *mm, unsigned long addr). Important macros/constants include __ASM_VDSO_H, __VDSO_PAGES, vdso_total_pages.

## Control Flow
During mm setup, arm_install_vdso maps the vDSO image and records its address in mm_context_t when CONFIG_VDSO is enabled.

## State And Persistence
State is the per-mm vDSO mapping address and shared vDSO time-data pages maintained by kernel timekeeping.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
vDSO code must remain safe for userspace execution and match kernel time-data layout; unsupported clock modes must fall back cleanly to syscalls.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/vdso.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/vdso/clocksource.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/vdso/clocksource.h

## Purpose
Defines ARM vDSO-supported clock modes for generic vDSO timekeeping.

## Important APIs, Types, And Functions
Important macros/constants include __ASM_VDSOCLOCKSOURCE_H, VDSO_ARCH_CLOCKMODES.

## Control Flow
The generic vDSO code compiles in ARM clocksource mode bits to decide whether high-resolution user time reads are available.

## State And Persistence
State is the per-mm vDSO mapping address and shared vDSO time-data pages maintained by kernel timekeeping.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
vDSO code must remain safe for userspace execution and match kernel time-data layout; unsupported clock modes must fall back cleanly to syscalls.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/vdso/clocksource.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/vdso/cp15.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/vdso/cp15.h

## Purpose
Provides vDSO-safe CP15 system-register read/write macros for ARM, including CNTVCT and cache/branch maintenance registers.

## Important APIs, Types, And Functions
Important macros/constants include __ASM_VDSO_CP15_H, __ACCESS_CP15(CRn,, __ACCESS_CP15_64(Op1,, __read_sysreg(r,, read_sysreg(...), __write_sysreg(v,, write_sysreg(v,, BPIALL, ICIALLU, CNTVCT. It depends directly on #include <linux/stringify.h>.

## Control Flow
vDSO and low-level code issue mrc/mcr or mrrc/mcrr instructions through typed macros rather than open-coded assembly.

## State And Persistence
State is the per-mm vDSO mapping address and shared vDSO time-data pages maintained by kernel timekeeping.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/stringify.h>.

## Risks And Edge Cases
vDSO code must remain safe for userspace execution and match kernel time-data layout; unsupported clock modes must fall back cleanly to syscalls.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/vdso/cp15.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/vdso/gettimeofday.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/vdso/gettimeofday.h

## Purpose
Implements ARM wrappers around generic vDSO clock_gettime/gettimeofday/getres helpers and high-resolution capability checks.

## Important APIs, Types, And Functions
Key declarations include struct __kernel_old_timeval *_tv,; struct timezone *_tz); struct __kernel_timespec *_ts); struct old_timespec32 *_ts); struct __kernel_timespec *_ts); struct old_timespec32 *_ts). Important macros/constants include __ASM_VDSO_GETTIMEOFDAY_H, VDSO_HAS_CLOCK_GETRES, __arch_vdso_hres_capable. It depends directly on #include <asm/barrier.h>, #include <asm/errno.h>, #include <asm/unistd.h>, #include <asm/vdso/cp15.h>, #include <vdso/clocksource.h>, #include <vdso/time32.h>.

## Control Flow
User vDSO entry points call generic time namespace helpers when the clock mode supports direct reads; otherwise they return fallback errors to enter the kernel.

## State And Persistence
State is the per-mm vDSO mapping address and shared vDSO time-data pages maintained by kernel timekeeping.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/barrier.h>, #include <asm/errno.h>, #include <asm/unistd.h>, #include <asm/vdso/cp15.h>, #include <vdso/clocksource.h>, #include <vdso/time32.h>, #include <uapi/linux/time.h>.

## Risks And Edge Cases
vDSO code must remain safe for userspace execution and match kernel time-data layout; unsupported clock modes must fall back cleanly to syscalls.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/vdso/gettimeofday.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/vdso/processor.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/vdso/processor.h

## Purpose
Defines the vDSO cpu_relax primitive for ARM user-space helper code.

## Important APIs, Types, And Functions
Important macros/constants include __ASM_VDSO_PROCESSOR_H, cpu_relax(), cpu_relax().

## Control Flow
When target architecture supports yield, cpu_relax emits it; otherwise it is a compiler barrier.

## State And Persistence
State is the per-mm vDSO mapping address and shared vDSO time-data pages maintained by kernel timekeeping.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
vDSO code must remain safe for userspace execution and match kernel time-data layout; unsupported clock modes must fall back cleanly to syscalls.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/vdso/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/vdso/vsyscall.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/vdso/vsyscall.h

## Purpose
Provides ARM architecture hook for synchronizing vDSO time data.

## Important APIs, Types, And Functions
Key declarations include void __arch_sync_vdso_time_data(struct vdso_time_data *vdata). Important macros/constants include __ASM_VDSO_VSYSCALL_H, __arch_sync_vdso_time_data. It depends directly on #include <vdso/datapage.h>, #include <asm/cacheflush.h>, #include <asm-generic/vdso/vsyscall.h>.

## Control Flow
Kernel timekeeping updates call __arch_sync_vdso_time_data, which currently has no extra ARM-specific work.

## State And Persistence
State is the per-mm vDSO mapping address and shared vDSO time-data pages maintained by kernel timekeeping.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <vdso/datapage.h>, #include <asm/cacheflush.h>, #include <asm-generic/vdso/vsyscall.h>.

## Risks And Edge Cases
vDSO code must remain safe for userspace execution and match kernel time-data layout; unsupported clock modes must fall back cleanly to syscalls.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/vdso/vsyscall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/vermagic.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/vermagic.h

## Purpose
Builds the ARM module vermagic string from architecture version, phys/virt patching mode, and Thumb-2 status.

## Important APIs, Types, And Functions
Important macros/constants include _ASM_VERMAGIC_H, MODULE_ARCH_VERMAGIC_ARMVSN, MODULE_ARCH_VERMAGIC_P2V, MODULE_ARCH_VERMAGIC_P2V, MODULE_ARCH_VERMAGIC_ARMTHUMB, MODULE_ARCH_VERMAGIC_ARMTHUMB, MODULE_ARCH_VERMAGIC. It depends directly on #include <linux/stringify.h>.

## Control Flow
Module loading compares this string so incompatible ARM module binaries are rejected.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/stringify.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/vermagic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/vfp.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/vfp.h

## Purpose
Defines VFP/FPSCR/FPEXC/MVFR bit fields and vfp_disable declaration for ARM floating-point support.

## Important APIs, Types, And Functions
Key declarations include void vfp_disable(void);. Important macros/constants include __ASM_VFP_H, FPSID_IMPLEMENTER_BIT, FPSID_IMPLEMENTER_MASK, FPSID_SOFTWARE, FPSID_FORMAT_BIT, FPSID_FORMAT_MASK, FPSID_NODOUBLE, FPSID_ARCH_BIT, FPSID_ARCH_MASK, FPSID_CPUID_ARCH_MASK.

## Control Flow
VFP exception, context-switch, and feature-detection code decodes CP10/CP11 state using these masks.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/vfp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/vfpmacros.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/vfpmacros.h

## Purpose
Provides assembly macros for moving VFP system registers and saving/restoring VFP register banks.

## Important APIs, Types, And Functions
Assembly macros include .macro VFPFMRX, rd, sysreg, cond, .macro VFPFMXR, sysreg, rd, cond, .macro VFPFLDMIA, base, tmp, .macro VFPFSTMIA, base, tmp. It depends directly on #include <asm/hwcap.h>, #include <asm/vfp.h>.

## Control Flow
Low-level VFP context-switch code expands VFPFMRX/VFPFMXR and FLDMIA/FSTMIA sequences with CPU-specific register counts.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/hwcap.h>, #include <asm/vfp.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/vfpmacros.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/vga.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/vga.h

## Purpose
Defines ARM VGA memory mapping helpers and vgacon screen-info declarations.

## Important APIs, Types, And Functions
Key declarations include extern unsigned long vga_base;; extern struct screen_info vgacon_screen_info;. Important macros/constants include ASMARM_VGA_H, VGA_MAP_MEM(x,s), vga_readb(x), vga_writeb(x,y). It depends directly on #include <linux/io.h>.

## Control Flow
VGA console code maps VGA memory through vga_base and performs volatile byte reads/writes.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/io.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/vga.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/virt.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/virt.h

## Purpose
Defines ARM virtualization-mode detection, boot CPU mode synchronization, HVC stub call numbers, and hypervisor availability helpers.

## Important APIs, Types, And Functions
Key declarations include extern int __boot_cpu_mode;; static inline void sync_boot_mode(void); void hyp_mode_check(void);; static inline bool is_hyp_mode_available(void); static inline bool is_hyp_mode_mismatched(void); static inline bool is_kernel_in_hyp_mode(void). Important macros/constants include VIRT_H, BOOT_CPU_MODE_MISMATCH, __boot_cpu_mode, sync_boot_mode(), HVC_SET_VECTORS, HVC_SOFT_RESTART, HVC_STUB_ERR. It depends directly on #include <asm/ptrace.h>, #include <asm/cacheflush.h>.

## Control Flow
Boot code records whether CPUs entered in SVC or HYP mode, checks mismatches on secondary CPUs, and HYP stubs use HVC_SET_VECTORS or HVC_SOFT_RESTART.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm/ptrace.h>, #include <asm/cacheflush.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/virt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/vmalloc.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/vmalloc.h

## Purpose
Provides the ARM vmalloc header hook, currently deferring to generic vmalloc behavior.

## Important APIs, Types, And Functions
Important macros/constants include _ASM_ARM_VMALLOC_H.

## Control Flow
No runtime flow is defined here; pgtable.h supplies the ARM VMALLOC address range.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include the surrounding ARM architecture build and generic kernel headers.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/vmalloc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/vmlinux.lds.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/vmlinux.lds.h

## Purpose
Defines ARM linker-script macros for CPU/init/MMU section retention, proc_info, idmap text, unwind sections, exception vectors overlays, stubs, assertions, and TCM placement.

## Important APIs, Types, And Functions
Important macros/constants include ARM_CPU_DISCARD(x), ARM_CPU_KEEP(x), ARM_CPU_DISCARD(x), ARM_CPU_KEEP(x), ARM_EXIT_KEEP(x), ARM_EXIT_DISCARD(x), ARM_EXIT_KEEP(x), ARM_EXIT_DISCARD(x), ARM_MMU_KEEP(x), ARM_MMU_DISCARD(x). It depends directly on #include <asm-generic/vmlinux.lds.h>.

## Control Flow
The vmlinux linker script expands these macros to keep or discard sections based on configuration, place vectors at 0xffff0000 overlays, expose LMA symbols, and verify size/alignment constraints.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <asm-generic/vmlinux.lds.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/vmlinux.lds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/word-at-a-time.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/word-at-a-time.h

## Purpose
Implements ARM word-at-a-time zero-byte detection and optional unaligned zeropadded kernel loads for optimized string routines.

## Important APIs, Types, And Functions
Key declarations include struct word_at_a_time {; static inline unsigned long has_zero(unsigned long a, unsigned long *bits,; unsigned long mask = ((a - c->one_bits) & ~a) & c->high_bits;; static inline unsigned long create_zero_mask(unsigned long bits); static inline unsigned long find_zero(unsigned long mask); unsigned long ret;. Important macros/constants include __ASM_ARM_WORD_AT_A_TIME_H, WORD_AT_A_TIME_CONSTANTS, prep_zero_mask(a,, zero_bytemask(mask). It depends directly on #include <linux/bitops.h>, #include <linux/wordpart.h>, #include <asm-generic/word-at-a-time.h>.

## Control Flow
Little-endian builds use x86-style one/high-bit arithmetic and CLZ or fallback math to locate zero bytes; DCACHE_WORD_ACCESS builds use exception-table fixups for page-crossing unaligned loads.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM architecture code and generic kernel subsystems that include this header. Direct dependencies include #include <linux/bitops.h>, #include <linux/wordpart.h>, #include <asm-generic/word-at-a-time.h>.

## Risks And Edge Cases
Most risk is configuration and ABI drift: these headers are consumed by assembly, linker scripts, generic kernel code, or userspace-visible ABIs, so field layout and constants must remain synchronized with their callers.

## Test Signals
Primary signals are compile coverage for the relevant ARM Kconfig combinations plus boot/runtime tests of the subsystem that includes the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/word-at-a-time.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/xen/events.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/xen/events.h

## Purpose
Provides ARM architecture definitions for events.h.

## Important APIs, Types, And Functions
Key declarations include enum ipi_vector {; static inline int xen_irqs_disabled(struct pt_regs *regs); static inline bool xen_support_evtchn_rebind(void). Important macros/constants include _ASM_ARM_XEN_EVENTS_H, xchg_xen_ulong(ptr,. It depends directly on #include <asm/ptrace.h>, #include <asm/atomic.h>.

## Control Flow
The header is included by ARM architecture or generic kernel code; most behavior is selected at compile time through configuration and inline helpers.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM Xen guest support and generic Xen code. Dependencies are #include <asm/ptrace.h>, #include <asm/atomic.h>; this keeps common Xen include paths architecture-neutral.

## Risks And Edge Cases
The wrapper must track Xen ARM header contracts exactly; mismatches break guest builds or runtime hypervisor interactions.

## Test Signals
Signals are ARM Xen guest build coverage and booting under Xen with event channels, grant/page helpers, and swiotlb paths active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/xen/events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/xen/hypercall.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/xen/hypercall.h

## Purpose
Provides the ARM architecture include shim for Xen hypercall definitions.

## Important APIs, Types, And Functions
It depends directly on #include <xen/arm/hypercall.h>.

## Control Flow
There is no local control flow beyond forwarding to xen/arm headers; ARM Xen code includes this path for architecture-neutral include names.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM Xen guest support and generic Xen code. Dependencies are #include <xen/arm/hypercall.h>; this keeps common Xen include paths architecture-neutral.

## Risks And Edge Cases
The wrapper must track Xen ARM header contracts exactly; mismatches break guest builds or runtime hypervisor interactions.

## Test Signals
Signals are ARM Xen guest build coverage and booting under Xen with event channels, grant/page helpers, and swiotlb paths active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/xen/hypercall.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/xen/hypervisor.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/xen/hypervisor.h

## Purpose
Provides the ARM architecture include shim for Xen hypervisor definitions.

## Important APIs, Types, And Functions
It depends directly on #include <xen/arm/hypervisor.h>.

## Control Flow
There is no local control flow beyond forwarding to xen/arm headers; ARM Xen code includes this path for architecture-neutral include names.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM Xen guest support and generic Xen code. Dependencies are #include <xen/arm/hypervisor.h>; this keeps common Xen include paths architecture-neutral.

## Risks And Edge Cases
The wrapper must track Xen ARM header contracts exactly; mismatches break guest builds or runtime hypervisor interactions.

## Test Signals
Signals are ARM Xen guest build coverage and booting under Xen with event channels, grant/page helpers, and swiotlb paths active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/xen/hypervisor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/xen/interface.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/xen/interface.h

## Purpose
Provides the ARM architecture include shim for Xen interface definitions.

## Important APIs, Types, And Functions
It depends directly on #include <xen/arm/interface.h>.

## Control Flow
There is no local control flow beyond forwarding to xen/arm headers; ARM Xen code includes this path for architecture-neutral include names.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM Xen guest support and generic Xen code. Dependencies are #include <xen/arm/interface.h>; this keeps common Xen include paths architecture-neutral.

## Risks And Edge Cases
The wrapper must track Xen ARM header contracts exactly; mismatches break guest builds or runtime hypervisor interactions.

## Test Signals
Signals are ARM Xen guest build coverage and booting under Xen with event channels, grant/page helpers, and swiotlb paths active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/xen/interface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/xen/page.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/xen/page.h

## Purpose
Provides the ARM architecture include shim for Xen page definitions.

## Important APIs, Types, And Functions
Key declarations include static inline bool xen_kernel_unmapped_at_usr(void). It depends directly on #include <xen/arm/page.h>.

## Control Flow
There is no local control flow beyond forwarding to xen/arm headers; ARM Xen code includes this path for architecture-neutral include names.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM Xen guest support and generic Xen code. Dependencies are #include <xen/arm/page.h>; this keeps common Xen include paths architecture-neutral.

## Risks And Edge Cases
The wrapper must track Xen ARM header contracts exactly; mismatches break guest builds or runtime hypervisor interactions.

## Test Signals
Signals are ARM Xen guest build coverage and booting under Xen with event channels, grant/page helpers, and swiotlb paths active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/xen/page.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/xen/swiotlb-xen.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/xen/swiotlb-xen.h

## Purpose
Provides the ARM architecture include shim for Xen swiotlb-xen definitions.

## Important APIs, Types, And Functions
It depends directly on #include <xen/arm/swiotlb-xen.h>.

## Control Flow
There is no local control flow beyond forwarding to xen/arm headers; ARM Xen code includes this path for architecture-neutral include names.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM Xen guest support and generic Xen code. Dependencies are #include <xen/arm/swiotlb-xen.h>; this keeps common Xen include paths architecture-neutral.

## Risks And Edge Cases
The wrapper must track Xen ARM header contracts exactly; mismatches break guest builds or runtime hypervisor interactions.

## Test Signals
Signals are ARM Xen guest build coverage and booting under Xen with event channels, grant/page helpers, and swiotlb paths active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/xen/swiotlb-xen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/xen/xen-ops.h -->
# sources/distributed-fs/ceph-client/arch/arm/include/asm/xen/xen-ops.h

## Purpose
Provides the ARM architecture include shim for Xen xen-ops definitions.

## Important APIs, Types, And Functions
It depends directly on #include <xen/arm/xen-ops.h>.

## Control Flow
There is no local control flow beyond forwarding to xen/arm headers; ARM Xen code includes this path for architecture-neutral include names.

## State And Persistence
The file mostly defines compile-time constants, type layouts, inline helpers, or extern declarations; persistent state lives in the subsystem implementation that includes it.

## Dependencies And Integration Points
Integrated by ARM Xen guest support and generic Xen code. Dependencies are #include <xen/arm/xen-ops.h>; this keeps common Xen include paths architecture-neutral.

## Risks And Edge Cases
The wrapper must track Xen ARM header contracts exactly; mismatches break guest builds or runtime hypervisor interactions.

## Test Signals
Signals are ARM Xen guest build coverage and booting under Xen with event channels, grant/page helpers, and swiotlb paths active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/asm/xen/xen-ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/8250.S -->
# sources/distributed-fs/ceph-client/arch/arm/include/debug/8250.S

## Purpose
Defines low-level early-printk/debug macro support for the generic 8250/16550 UART. It supplies the standard addruart, senduart, busyuart, waituarttxrdy, and waituartcts macro contract consumed by ARM head/decompressor/debug assembly.

## Important APIs, Types, And Functions
Important macros/constants include UART_SHIFT. Assembly macros include .macro addruart, rp, rv, tmp, .macro store, rd, rx:vararg, .macro load, rd, rx:vararg, .macro store, rd, rx:vararg, .macro load, rd, rx:vararg, .macro senduart,rd,rx, .macro busyuart,rd,rx, .macro waituarttxrdy,rd,rx. It depends directly on #include <linux/serial_reg.h>.

## Control Flow
Early boot or decompressor code expands addruart to derive physical/virtual debug addresses, senduart to write one byte/word, and busyuart or wait macros to poll transmitter state before continuing. The macros run before normal drivers or clocks may be available.

## State And Persistence
No normal kernel persistence. Some macros poll hardware registers; brcmstb additionally caches detected UART physical/virtual addresses in shared early-boot storage when built for zImage.

## Dependencies And Integration Points
Integrated by ARM decompressor/head/debug assembly through the standard debug macro names. Dependencies are #include <linux/serial_reg.h> plus CONFIG_DEBUG_UART_* or platform register layout constants.

## Risks And Edge Cases
Register offsets, endian handling, physical/virtual address assumptions, and polling bits must match the SoC before the serial driver exists; a wrong value can hang very early boot or lose panic/decompressor output.

## Test Signals
Test signals are successful decompressor/earlycon output on the target SoC, build coverage for the selected CONFIG_DEBUG_* option, and boot logs that continue past early MMU enablement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/8250.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/asm9260.S -->
# sources/distributed-fs/ceph-client/arch/arm/include/debug/asm9260.S

## Purpose
Defines low-level early-printk/debug macro support for the Alphascale ASM9260 UART. It supplies the standard addruart, senduart, busyuart, waituarttxrdy, and waituartcts macro contract consumed by ARM head/decompressor/debug assembly.

## Important APIs, Types, And Functions
Assembly macros include .macro addruart, rp, rv, tmp, .macro waituarttxrdy,rd,rx, .macro waituartcts,rd,rx, .macro senduart,rd,rx, .macro busyuart,rd,rx.

## Control Flow
Early boot or decompressor code expands addruart to derive physical/virtual debug addresses, senduart to write one byte/word, and busyuart or wait macros to poll transmitter state before continuing. The macros run before normal drivers or clocks may be available.

## State And Persistence
No normal kernel persistence. Some macros poll hardware registers; brcmstb additionally caches detected UART physical/virtual addresses in shared early-boot storage when built for zImage.

## Dependencies And Integration Points
Integrated by ARM decompressor/head/debug assembly through the standard debug macro names. Dependencies are the surrounding ARM architecture build and generic kernel headers plus CONFIG_DEBUG_UART_* or platform register layout constants.

## Risks And Edge Cases
Register offsets, endian handling, physical/virtual address assumptions, and polling bits must match the SoC before the serial driver exists; a wrong value can hang very early boot or lose panic/decompressor output.

## Test Signals
Test signals are successful decompressor/earlycon output on the target SoC, build coverage for the selected CONFIG_DEBUG_* option, and boot logs that continue past early MMU enablement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/asm9260.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/at91.S -->
# sources/distributed-fs/ceph-client/arch/arm/include/debug/at91.S

## Purpose
Defines low-level early-printk/debug macro support for the Atmel AT91 DBGU. It supplies the standard addruart, senduart, busyuart, waituarttxrdy, and waituartcts macro contract consumed by ARM head/decompressor/debug assembly.

## Important APIs, Types, And Functions
Important macros/constants include AT91_DBGU_SR, AT91_DBGU_THR, AT91_DBGU_TXRDY, AT91_DBGU_TXEMPTY. Assembly macros include .macro addruart, rp, rv, tmp, .macro senduart,rd,rx, .macro waituarttxrdy,rd,rx, .macro waituartcts,rd,rx, .macro busyuart,rd,rx.

## Control Flow
Early boot or decompressor code expands addruart to derive physical/virtual debug addresses, senduart to write one byte/word, and busyuart or wait macros to poll transmitter state before continuing. The macros run before normal drivers or clocks may be available.

## State And Persistence
No normal kernel persistence. Some macros poll hardware registers; brcmstb additionally caches detected UART physical/virtual addresses in shared early-boot storage when built for zImage.

## Dependencies And Integration Points
Integrated by ARM decompressor/head/debug assembly through the standard debug macro names. Dependencies are the surrounding ARM architecture build and generic kernel headers plus CONFIG_DEBUG_UART_* or platform register layout constants.

## Risks And Edge Cases
Register offsets, endian handling, physical/virtual address assumptions, and polling bits must match the SoC before the serial driver exists; a wrong value can hang very early boot or lose panic/decompressor output.

## Test Signals
Test signals are successful decompressor/earlycon output on the target SoC, build coverage for the selected CONFIG_DEBUG_* option, and boot logs that continue past early MMU enablement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/at91.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/bcm63xx.S -->
# sources/distributed-fs/ceph-client/arch/arm/include/debug/bcm63xx.S

## Purpose
Defines low-level early-printk/debug macro support for the Broadcom BCM63xx UART. It supplies the standard addruart, senduart, busyuart, waituarttxrdy, and waituartcts macro contract consumed by ARM head/decompressor/debug assembly.

## Important APIs, Types, And Functions
Assembly macros include .macro addruart, rp, rv, tmp, .macro senduart, rd, rx, .macro waituarttxrdy, rd, rx, .macro waituartcts, rd, rx, .macro busyuart, rd, rx. It depends directly on #include <linux/serial_bcm63xx.h>.

## Control Flow
Early boot or decompressor code expands addruart to derive physical/virtual debug addresses, senduart to write one byte/word, and busyuart or wait macros to poll transmitter state before continuing. The macros run before normal drivers or clocks may be available.

## State And Persistence
No normal kernel persistence. Some macros poll hardware registers; brcmstb additionally caches detected UART physical/virtual addresses in shared early-boot storage when built for zImage.

## Dependencies And Integration Points
Integrated by ARM decompressor/head/debug assembly through the standard debug macro names. Dependencies are #include <linux/serial_bcm63xx.h> plus CONFIG_DEBUG_UART_* or platform register layout constants.

## Risks And Edge Cases
Register offsets, endian handling, physical/virtual address assumptions, and polling bits must match the SoC before the serial driver exists; a wrong value can hang very early boot or lose panic/decompressor output.

## Test Signals
Test signals are successful decompressor/earlycon output on the target SoC, build coverage for the selected CONFIG_DEBUG_* option, and boot logs that continue past early MMU enablement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/bcm63xx.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/brcmstb.S -->
# sources/distributed-fs/ceph-client/arch/arm/include/debug/brcmstb.S

## Purpose
Defines low-level early-printk/debug macro support for the Broadcom STB UART family auto-detection. It supplies the standard addruart, senduart, busyuart, waituarttxrdy, and waituartcts macro contract consumed by ARM head/decompressor/debug assembly.

## Important APIs, Types, And Functions
Important macros/constants include REG_PHYS_BASE, REG_PHYS_BASE_V7, REG_VIRT_BASE, REG_PHYS_ADDR(x), REG_PHYS_ADDR_V7(x), SUN_TOP_CTRL_BASE, SUN_TOP_CTRL_BASE_V7, UARTA_3390, UARTA_72116, UARTA_7250. Assembly macros include .macro  addruart, rp, rv, tmp, .macro store, rd, rx:vararg, .macro load, rd, rx:vararg, .macro senduart,rd,rx, .macro busyuart,rd,rx, .macro waituarttxrdy,rd,rx, .macro waituartcts,rd,rx. It depends directly on #include <linux/serial_reg.h>, #include <asm/cputype.h>.

## Control Flow
Early boot or decompressor code expands addruart to derive physical/virtual debug addresses, senduart to write one byte/word, and busyuart or wait macros to poll transmitter state before continuing. The macros run before normal drivers or clocks may be available.

## State And Persistence
No normal kernel persistence. Some macros poll hardware registers; brcmstb additionally caches detected UART physical/virtual addresses in shared early-boot storage when built for zImage.

## Dependencies And Integration Points
Integrated by ARM decompressor/head/debug assembly through the standard debug macro names. Dependencies are #include <linux/serial_reg.h>, #include <asm/cputype.h> plus CONFIG_DEBUG_UART_* or platform register layout constants.

## Risks And Edge Cases
Register offsets, endian handling, physical/virtual address assumptions, and polling bits must match the SoC before the serial driver exists; a wrong value can hang very early boot or lose panic/decompressor output.

## Test Signals
Test signals are successful decompressor/earlycon output on the target SoC, build coverage for the selected CONFIG_DEBUG_* option, and boot logs that continue past early MMU enablement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/brcmstb.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/clps711x.S -->
# sources/distributed-fs/ceph-client/arch/arm/include/debug/clps711x.S

## Purpose
Defines low-level early-printk/debug macro support for the Cirrus Logic CLPS711x UART. It supplies the standard addruart, senduart, busyuart, waituarttxrdy, and waituartcts macro contract consumed by ARM head/decompressor/debug assembly.

## Important APIs, Types, And Functions
Important macros/constants include CLPS711X_UART_PADDR, CLPS711X_UART_VADDR, CLPS711X_UART_PADDR, CLPS711X_UART_VADDR, SYSFLG, SYSFLG_UBUSY, UARTDR. Assembly macros include .macro addruart, rp, rv, tmp, .macro waituartcts,rd,rx, .macro waituarttxrdy,rd,rx, .macro senduart,rd,rx, .macro busyuart,rd,rx.

## Control Flow
Early boot or decompressor code expands addruart to derive physical/virtual debug addresses, senduart to write one byte/word, and busyuart or wait macros to poll transmitter state before continuing. The macros run before normal drivers or clocks may be available.

## State And Persistence
No normal kernel persistence. Some macros poll hardware registers; brcmstb additionally caches detected UART physical/virtual addresses in shared early-boot storage when built for zImage.

## Dependencies And Integration Points
Integrated by ARM decompressor/head/debug assembly through the standard debug macro names. Dependencies are the surrounding ARM architecture build and generic kernel headers plus CONFIG_DEBUG_UART_* or platform register layout constants.

## Risks And Edge Cases
Register offsets, endian handling, physical/virtual address assumptions, and polling bits must match the SoC before the serial driver exists; a wrong value can hang very early boot or lose panic/decompressor output.

## Test Signals
Test signals are successful decompressor/earlycon output on the target SoC, build coverage for the selected CONFIG_DEBUG_* option, and boot logs that continue past early MMU enablement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/clps711x.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/dc21285.S -->
# sources/distributed-fs/ceph-client/arch/arm/include/debug/dc21285.S

## Purpose
Defines low-level early-printk/debug macro support for the DEC21285/Footbridge UART. It supplies the standard addruart, senduart, busyuart, waituarttxrdy, and waituartcts macro contract consumed by ARM head/decompressor/debug assembly.

## Important APIs, Types, And Functions
Assembly macros include .macro addruart, rp, rv, tmp, .macro senduart,rd,rx, .macro busyuart,rd,rx, .macro waituartcts,rd,rx, .macro waituarttxrdy,rd,rx. It depends directly on #include <asm/hardware/dec21285.h>, #include <mach/hardware.h>.

## Control Flow
Early boot or decompressor code expands addruart to derive physical/virtual debug addresses, senduart to write one byte/word, and busyuart or wait macros to poll transmitter state before continuing. The macros run before normal drivers or clocks may be available.

## State And Persistence
No normal kernel persistence. Some macros poll hardware registers; brcmstb additionally caches detected UART physical/virtual addresses in shared early-boot storage when built for zImage.

## Dependencies And Integration Points
Integrated by ARM decompressor/head/debug assembly through the standard debug macro names. Dependencies are #include <asm/hardware/dec21285.h>, #include <mach/hardware.h> plus CONFIG_DEBUG_UART_* or platform register layout constants.

## Risks And Edge Cases
Register offsets, endian handling, physical/virtual address assumptions, and polling bits must match the SoC before the serial driver exists; a wrong value can hang very early boot or lose panic/decompressor output.

## Test Signals
Test signals are successful decompressor/earlycon output on the target SoC, build coverage for the selected CONFIG_DEBUG_* option, and boot logs that continue past early MMU enablement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/dc21285.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/digicolor.S -->
# sources/distributed-fs/ceph-client/arch/arm/include/debug/digicolor.S

## Purpose
Defines low-level early-printk/debug macro support for the Conexant Digicolor USART. It supplies the standard addruart, senduart, busyuart, waituarttxrdy, and waituartcts macro contract consumed by ARM head/decompressor/debug assembly.

## Important APIs, Types, And Functions
Important macros/constants include UA0_STATUS, UA0_EMI_REC, UA0_STATUS_TX_READY. Assembly macros include .macro addruart, rp, rv, tmp, .macro senduart,rd,rx, .macro waituartcts,rd,rx, .macro waituarttxrdy,rd,rx, .macro busyuart,rd,rx.

## Control Flow
Early boot or decompressor code expands addruart to derive physical/virtual debug addresses, senduart to write one byte/word, and busyuart or wait macros to poll transmitter state before continuing. The macros run before normal drivers or clocks may be available.

## State And Persistence
No normal kernel persistence. Some macros poll hardware registers; brcmstb additionally caches detected UART physical/virtual addresses in shared early-boot storage when built for zImage.

## Dependencies And Integration Points
Integrated by ARM decompressor/head/debug assembly through the standard debug macro names. Dependencies are the surrounding ARM architecture build and generic kernel headers plus CONFIG_DEBUG_UART_* or platform register layout constants.

## Risks And Edge Cases
Register offsets, endian handling, physical/virtual address assumptions, and polling bits must match the SoC before the serial driver exists; a wrong value can hang very early boot or lose panic/decompressor output.

## Test Signals
Test signals are successful decompressor/earlycon output on the target SoC, build coverage for the selected CONFIG_DEBUG_* option, and boot logs that continue past early MMU enablement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/digicolor.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/exynos.S -->
# sources/distributed-fs/ceph-client/arch/arm/include/debug/exynos.S

## Purpose
Defines low-level early-printk/debug macro support for the Samsung Exynos UART. It supplies the standard addruart, senduart, busyuart, waituarttxrdy, and waituartcts macro contract consumed by ARM head/decompressor/debug assembly.

## Important APIs, Types, And Functions
Important macros/constants include S3C_ADDR_BASE, S3C_VA_UART, EXYNOS4_PA_UART, EXYNOS5_PA_UART, fifo_full, fifo_level. Assembly macros include .macro addruart, rp, rv, tmp. It depends directly on #include <debug/samsung.S>.

## Control Flow
Early boot or decompressor code expands addruart to derive physical/virtual debug addresses, senduart to write one byte/word, and busyuart or wait macros to poll transmitter state before continuing. The macros run before normal drivers or clocks may be available.

## State And Persistence
No normal kernel persistence. Some macros poll hardware registers; brcmstb additionally caches detected UART physical/virtual addresses in shared early-boot storage when built for zImage.

## Dependencies And Integration Points
Integrated by ARM decompressor/head/debug assembly through the standard debug macro names. Dependencies are #include <debug/samsung.S> plus CONFIG_DEBUG_UART_* or platform register layout constants.

## Risks And Edge Cases
Register offsets, endian handling, physical/virtual address assumptions, and polling bits must match the SoC before the serial driver exists; a wrong value can hang very early boot or lose panic/decompressor output.

## Test Signals
Test signals are successful decompressor/earlycon output on the target SoC, build coverage for the selected CONFIG_DEBUG_* option, and boot logs that continue past early MMU enablement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/exynos.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/icedcc.S -->
# sources/distributed-fs/ceph-client/arch/arm/include/debug/icedcc.S

## Purpose
Defines low-level early-printk/debug macro support for the ARM EmbeddedICE DCC debug channel. It supplies the standard addruart, senduart, busyuart, waituarttxrdy, and waituartcts macro contract consumed by ARM head/decompressor/debug assembly.

## Important APIs, Types, And Functions
Assembly macros include .macro addruart, rp, rv, tmp, .macro senduart, rd, rx, .macro busyuart, rd, rx, .macro waituartcts, rd, rx, .macro waituarttxrdy, rd, rx, .macro senduart, rd, rx, .macro busyuart, rd, rx, .macro waituartcts, rd, rx.

## Control Flow
Early boot or decompressor code expands addruart to derive physical/virtual debug addresses, senduart to write one byte/word, and busyuart or wait macros to poll transmitter state before continuing. The macros run before normal drivers or clocks may be available.

## State And Persistence
No normal kernel persistence. Some macros poll hardware registers; brcmstb additionally caches detected UART physical/virtual addresses in shared early-boot storage when built for zImage.

## Dependencies And Integration Points
Integrated by ARM decompressor/head/debug assembly through the standard debug macro names. Dependencies are the surrounding ARM architecture build and generic kernel headers plus CONFIG_DEBUG_UART_* or platform register layout constants.

## Risks And Edge Cases
Register offsets, endian handling, physical/virtual address assumptions, and polling bits must match the SoC before the serial driver exists; a wrong value can hang very early boot or lose panic/decompressor output.

## Test Signals
Test signals are successful decompressor/earlycon output on the target SoC, build coverage for the selected CONFIG_DEBUG_* option, and boot logs that continue past early MMU enablement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/include/debug/icedcc.S -->
