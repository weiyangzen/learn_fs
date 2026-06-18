# subset-b-000871 research

Grouped research report for the requested x86 Ceph client headers. Each section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/extable_fixup_types.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/extable_fixup_types.h

## Purpose
Exception-table fixup type encoding for x86 fault recovery. It defines packed type/register/flag/immediate fields used by assembly exception table annotations. The header is 71 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: None visible in this header.

Notable constants/macros: `#define _ASM_X86_EXTABLE_FIXUP_TYPES_H`; `#define EX_DATA_TYPE_MASK ((int)0x000000FF)`; `#define EX_DATA_REG_MASK ((int)0x00000F00)`; `#define EX_DATA_FLAG_MASK ((int)0x0000F000)`; `#define EX_DATA_IMM_MASK ((int)0xFFFF0000)`; `#define EX_DATA_REG_SHIFT 8`; `#define EX_DATA_FLAG_SHIFT 12`; `#define EX_DATA_IMM_SHIFT 16`; `#define EX_DATA_REG(reg) ((reg) << EX_DATA_REG_SHIFT)`; `#define EX_DATA_FLAG(flag) ((flag) << EX_DATA_FLAG_SHIFT)`; `#define EX_DATA_IMM(imm) ((imm) << EX_DATA_IMM_SHIFT)`; `#define EX_REG_DS EX_DATA_REG(8)`; `#define EX_REG_ES EX_DATA_REG(9)`; `#define EX_REG_FS EX_DATA_REG(10)`; `#define EX_REG_GS EX_DATA_REG(11)`; `#define EX_FLAG_CLEAR_AX EX_DATA_FLAG(1)`; `#define EX_FLAG_CLEAR_DX EX_DATA_FLAG(2)`; `#define EX_FLAG_CLEAR_AX_DX EX_DATA_FLAG(3)`

Notable declarations and inline helpers: `#define _ASM_X86_EXTABLE_FIXUP_TYPES_H`; `#define EX_DATA_TYPE_MASK ((int)0x000000FF)`; `#define EX_DATA_REG_MASK ((int)0x00000F00)`; `#define EX_DATA_FLAG_MASK ((int)0x0000F000)`; `#define EX_DATA_IMM_MASK ((int)0xFFFF0000)`; `#define EX_DATA_REG_SHIFT 8`; `#define EX_DATA_FLAG_SHIFT 12`; `#define EX_DATA_IMM_SHIFT 16`; `#define EX_DATA_REG(reg) ((reg) << EX_DATA_REG_SHIFT)`; `#define EX_DATA_FLAG(flag) ((flag) << EX_DATA_FLAG_SHIFT)`; `#define EX_DATA_IMM(imm) ((imm) << EX_DATA_IMM_SHIFT)`; `#define EX_REG_DS EX_DATA_REG(8)`; `#define EX_REG_ES EX_DATA_REG(9)`; `#define EX_REG_FS EX_DATA_REG(10)`; `#define EX_REG_GS EX_DATA_REG(11)`; `#define EX_FLAG_CLEAR_AX EX_DATA_FLAG(1)`; `#define EX_FLAG_CLEAR_DX EX_DATA_FLAG(2)`; `#define EX_FLAG_CLEAR_AX_DX EX_DATA_FLAG(3)`; `#define EX_TYPE_NONE 0`; `#define EX_TYPE_DEFAULT 1`; `#define EX_TYPE_FAULT 2`; `#define EX_TYPE_UACCESS 3`; `#define EX_TYPE_CLEAR_FS 5`; `#define EX_TYPE_FPU_RESTORE 6`

## Control Flow
No runtime control flow; macros compose fixup metadata consumed by the exception table search and fixup handlers after a faulting instruction.

## State and Persistence
Persistent state is absent; correctness is in the numeric ABI shared with assembly, uaccess, MSR, BPF, FPU restore, SGX, and ERETU fixups.

## Dependencies and Integration Points
Integrated by asm/extable.h users through _ASM_EXTABLE_TYPE* macros and by fault handlers decoding EX_TYPE_* and EX_DATA_* fields.

## Risks
Risks are ABI drift, sign-extension mistakes in EX_DATA_IMM, and mismatches between annotated register fields and recovery code.

## Test Signals
Build tests should assemble all extable users; fault-injection should cover uaccess, MSR safe access, FPU restore, MCE-safe, pop, and zeropad paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/extable_fixup_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fixmap.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/fixmap.h

## Purpose
Compile-time fixed virtual address layout for x86 early boot, APIC/MMIO, kmap-local, GHES, vsyscall, and early ioremap users. The header is 200 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/kmap_size.h>`; `#include <linux/kernel.h>`; `#include <asm/apicdef.h>`; `#include <asm/page.h>`; `#include <asm/pgtable_types.h>`; `#include <linux/threads.h>`; `#include <uapi/asm/vsyscall.h>`; `#include <asm-generic/fixmap.h>`

Notable constants/macros: `#define _ASM_X86_FIXMAP_H`; `#define FIXMAP_PMD_TOP 507`; `#define FIXADDR_TOP ((unsigned long)__FIXADDR_TOP)`; `#define FIXADDR_TOP (round_up(VSYSCALL_ADDR + PAGE_SIZE, 1<<PMD_SHIFT) - \`; `#define NR_FIX_BTMAPS 64`; `#define FIX_BTMAPS_SLOTS 8`; `#define TOTAL_FIX_BTMAPS (NR_FIX_BTMAPS * FIX_BTMAPS_SLOTS)`; `#define FIXADDR_SIZE (__end_of_permanent_fixed_addresses << PAGE_SHIFT)`; `#define FIXADDR_START (FIXADDR_TOP - FIXADDR_SIZE)`; `#define FIXADDR_TOT_SIZE (__end_of_fixed_addresses << PAGE_SHIFT)`; `#define FIXADDR_TOT_START (FIXADDR_TOP - FIXADDR_TOT_SIZE)`; `#define FIXMAP_PAGE_NOCACHE PAGE_KERNEL_IO_NOCACHE`; `#define __late_set_fixmap(idx, phys, flags) __set_fixmap(idx, phys, flags)`; `#define __late_clear_fixmap(idx) __set_fixmap(idx, 0, __pgprot(0))`

Notable declarations and inline helpers: `#define _ASM_X86_FIXMAP_H`; `# define FIXMAP_PMD_NUM 2`; `# define KM_PMDS (KM_MAX_IDX * ((CONFIG_NR_CPUS + 511) / 512))`; `# define FIXMAP_PMD_NUM (KM_PMDS + 2)`; `#define FIXMAP_PMD_TOP 507`; `extern unsigned long __FIXADDR_TOP;`; `#define FIXADDR_TOP ((unsigned long)__FIXADDR_TOP)`; `#define FIXADDR_TOP (round_up(VSYSCALL_ADDR + PAGE_SIZE, 1<<PMD_SHIFT) - \`; `enum fixed_addresses {`; `#define NR_FIX_BTMAPS 64`; `#define FIX_BTMAPS_SLOTS 8`; `#define TOTAL_FIX_BTMAPS (NR_FIX_BTMAPS * FIX_BTMAPS_SLOTS)`; `extern void reserve_top_address(unsigned long reserve);`; `#define FIXADDR_SIZE (__end_of_permanent_fixed_addresses << PAGE_SHIFT)`; `#define FIXADDR_START (FIXADDR_TOP - FIXADDR_SIZE)`; `#define FIXADDR_TOT_SIZE (__end_of_fixed_addresses << PAGE_SHIFT)`; `#define FIXADDR_TOT_START (FIXADDR_TOP - FIXADDR_TOT_SIZE)`; `extern int fixmaps_set;`; `extern pte_t *pkmap_page_table;`; `void __native_set_fixmap(enum fixed_addresses idx, pte_t pte);`; `void native_set_fixmap(unsigned /* enum fixed_addresses */ idx,`; `static inline void __set_fixmap(enum fixed_addresses idx,`; `#define FIXMAP_PAGE_NOCACHE PAGE_KERNEL_IO_NOCACHE`; `void __init *early_memremap_encrypted(resource_size_t phys_addr,`

## Control Flow
Callers convert fixed-address enum indices into top-down virtual addresses and bind/unbind physical pages with native_set_fixmap(), __set_fixmap(), or early/late wrappers.

## State and Persistence
State is global page-table state plus fixmaps_set and pkmap_page_table; mappings persist until explicitly cleared or superseded by boot/runtime phases.

## Dependencies and Integration Points
Depends on page-table types, APIC limits, kmap sizing, vsyscall layout, memory encryption attributes, and asm-generic fixmap helpers.

## Risks
Risks include enum ordering changes, PMD coverage errors, missing encryption/decryption attributes, and overlap with vmalloc or vsyscall space.

## Test Signals
Boot tests should exercise early_ioremap, APIC/IO-APIC mapping, kmap-local debug modes, encrypted/decrypted early memremap, and x86_32 FIXADDR_TOP reservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fixmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/floppy.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/floppy.h

## Purpose
x86-specific floppy driver glue for ISA DMA, virtual DMA fallback, PIO interrupt handling, CMOS drive type reads, and controller constants. The header is 296 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/sizes.h>`; `#include <linux/vmalloc.h>`

Notable constants/macros: `#define _ASM_X86_FLOPPY_H`; `#define _CROSS_64KB(a, s, vdma) \`; `#define SW fd_routine[use_virtual_dma & 1]`; `#define CSW fd_routine[can_use_virtual_dma & 1]`; `#define fd_request_dma() CSW._request_dma(FLOPPY_DMA, "floppy")`; `#define fd_free_dma() CSW._free_dma(FLOPPY_DMA)`; `#define fd_enable_irq() enable_irq(FLOPPY_IRQ)`; `#define fd_disable_irq() disable_irq(FLOPPY_IRQ)`; `#define fd_free_irq() free_irq(FLOPPY_IRQ, NULL)`; `#define fd_get_dma_residue() SW._get_dma_residue(FLOPPY_DMA)`; `#define fd_dma_mem_alloc(size) SW._dma_mem_alloc(size)`; `#define fd_dma_setup(addr, size, mode, io) SW._dma_setup(addr, size, mode, io)`; `#define FLOPPY_CAN_FALLBACK_ON_NODMA`; `#define nodma_mem_alloc(size) vdma_mem_alloc(size)`; `#define fd_dma_mem_free(addr, size) _fd_dma_mem_free(addr, size)`; `#define fd_chose_dma_mode(addr, size) _fd_chose_dma_mode(addr, size)`; `#define FLOPPY0_TYPE \`; `#define FLOPPY1_TYPE \`

Notable declarations and inline helpers: `#define _ASM_X86_FLOPPY_H`; `#define _CROSS_64KB(a, s, vdma) \`; `#define SW fd_routine[use_virtual_dma & 1]`; `#define CSW fd_routine[can_use_virtual_dma & 1]`; `#define fd_request_dma() CSW._request_dma(FLOPPY_DMA, "floppy")`; `#define fd_free_dma() CSW._free_dma(FLOPPY_DMA)`; `#define fd_enable_irq() enable_irq(FLOPPY_IRQ)`; `#define fd_disable_irq() disable_irq(FLOPPY_IRQ)`; `#define fd_free_irq() free_irq(FLOPPY_IRQ, NULL)`; `#define fd_get_dma_residue() SW._get_dma_residue(FLOPPY_DMA)`; `#define fd_dma_mem_alloc(size) SW._dma_mem_alloc(size)`; `#define fd_dma_setup(addr, size, mode, io) SW._dma_setup(addr, size, mode, io)`; `#define FLOPPY_CAN_FALLBACK_ON_NODMA`; `static int virtual_dma_count;`; `static int virtual_dma_residue;`; `static char *virtual_dma_addr;`; `static int virtual_dma_mode;`; `static int doing_pdma;`; `static inline u8 fd_inb(u16 base, u16 reg)`; `u8 ret = inb_p(base + reg);`; `static inline void fd_outb(u8 value, u16 base, u16 reg)`; `static irqreturn_t floppy_hardint(int irq, void *dev_id)`; `unsigned char st;`; `static int calls;`

## Control Flow
The driver chooses hard DMA or virtual DMA, installs either floppy_interrupt or floppy_hardint, and the PIO interrupt loop drains/fills the FIFO until DMA status clears.

## State and Persistence
State is file-local static virtual_dma_* counters, current port/mode, doing_pdma, and FDC base addresses; CMOS reads are protected by rtc_lock.

## Dependencies and Integration Points
Integrates with legacy floppy core, ISA DMA APIs, IRQ request/free, port I/O helpers, vmalloc/free_pages, high_memory, and CMOS RTC access.

## Risks
Risks include residue accounting bugs, 64K boundary and 16MB ISA DMA constraints, IRQ handler races, stale virtual_dma_port assumptions, and very low hardware coverage.

## Test Signals
Tests need boot/module load on DMA and no-DMA paths, boundary-crossing buffers, vmalloc buffers, read/write interrupt residue behavior, and CMOS type detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/floppy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu.h

## Purpose
Top-level x86 FPU include that exposes the public FPU API and declares kernel FPU availability. The header is 13 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/fpu/api.h>`

Notable constants/macros: `#define _ASM_X86_FPU_H`; `#define kernel_fpu_available() true`

Notable declarations and inline helpers: `#define _ASM_X86_FPU_H`; `#define kernel_fpu_available() true`

## Control Flow
No independent control flow; it includes asm/fpu/api.h and maps kernel_fpu_available() to true on x86.

## State and Persistence
No state is stored here; state lives in task fpu/fpstate structures and per-CPU ownership variables declared below the API layer.

## Dependencies and Integration Points
Integrated by generic kernel code that checks kernel_fpu_available() before using kernel_fpu_begin()/end().

## Risks
Risk is mainly semantic: consumers may treat availability as permission, but context rules still require irq_fpu_usable() and locking discipline.

## Test Signals
Compile coverage should include generic FPU users and configurations with/without extended xstate support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/api.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/api.h

## Purpose
Public in-kernel FPU API for kernel FPU sections, fpregs locking/loading, boot/resume init, exception handling, xfeature queries, KVM guest fpstate, and xstate prctl. The header is 180 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/bottom_half.h>`; `#include <asm/fpu/types.h>`

Notable constants/macros: `#define _ASM_X86_FPU_API_H`; `#define KFPU_387 _BITUL(0) /* 387 state will be initialized */`; `#define KFPU_MXCSR _BITUL(1) /* MXCSR will be initialized */`

Notable declarations and inline helpers: `#define _ASM_X86_FPU_API_H`; `#define KFPU_387 _BITUL(0) /* 387 state will be initialized */`; `#define KFPU_MXCSR _BITUL(1) /* MXCSR will be initialized */`; `extern void kernel_fpu_begin_mask(unsigned int kfpu_mask);`; `extern void kernel_fpu_end(void);`; `extern bool irq_fpu_usable(void);`; `extern void fpregs_mark_activate(void);`; `static inline void kernel_fpu_begin(void)`; `static inline void fpregs_lock(void)`; `static inline void fpregs_unlock(void)`; `void fpregs_lock_and_load(void);`; `extern void fpregs_assert_state_consistent(void);`; `static inline void fpregs_assert_state_consistent(void) { }`; `extern void switch_fpu_return(void);`; `extern int cpu_has_xfeatures(u64 xfeatures_mask, const char **feature_name);`; `extern int fpu__exception_code(struct fpu *fpu, int trap_nr);`; `extern void fpu_sync_fpstate(struct fpu *fpu);`; `extern void fpu_reset_from_exception_fixup(void);`; `extern void fpu__init_cpu(void);`; `extern void fpu__init_system(void);`; `extern void fpu__init_check_bugs(void);`; `extern void fpu__resume_cpu(void);`; `extern void fpstate_init_soft(struct swregs_state *soft);`; `static inline void fpstate_init_soft(struct swregs_state *soft) {}`

## Control Flow
kernel_fpu_begin() selects 64-bit MXCSR-only default or 32-bit 387+MXCSR, fpregs_lock() disables BH or preemption for RT, and KVM helpers swap guest/task fpstates around vCPU entry/exit.

## State and Persistence
State touched through per-CPU kernel_fpu_allowed and fpu_fpregs_owner_ctx plus task fpu/fpstate buffers, guest fpstate allocation, XFD, and confidential-guest flags.

## Dependencies and Integration Points
Depends on bottom-half/preempt semantics, fpu/types.h, xstate helpers, KVM, signal/prctl, CPU hotplug, and exception fixups.

## Risks
Risks include using FPU in invalid IRQ/NMI contexts, missing fpregs_lock discipline, RT preemption assumptions, guest XFD desynchronization, and leaked dynamic fpstate.

## Test Signals
Tests should cover kernel_fpu_begin/end nesting rules, irq_fpu_usable contexts, CPU hotplug/resume, ptrace/signal state sync, KVM guest fpstate swap, AMX/XFD prctl behavior, and debug consistency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/regset.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/regset.h

## Purpose
Ptrace/core-dump regset declarations for x87, FXSR, software FPU, xstate, and xstate metadata exposure. The header is 23 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/regset.h>`

Notable constants/macros: `#define _ASM_X86_FPU_REGSET_H`; `#define xstateregs_active regset_fpregs_active`

Notable declarations and inline helpers: `#define _ASM_X86_FPU_REGSET_H`; `extern user_regset_active_fn regset_fpregs_active, regset_xregset_fpregs_active,`; `extern user_regset_get2_fn fpregs_get, xfpregs_get, fpregs_soft_get,`; `extern user_regset_set_fn fpregs_set, xfpregs_set, fpregs_soft_set,`; `#define xstateregs_active regset_fpregs_active`

## Control Flow
No local logic; it exports regset active/get/set callback symbols selected by ptrace, coredump, and compat regset tables.

## State and Persistence
State is task FPU state marshalled through regset callbacks; aliases map xstateregs_active to regset_fpregs_active when needed.

## Dependencies and Integration Points
Depends on linux/regset.h and the implementation in arch/x86/kernel/fpu/regset.c.

## Risks
Risks are UABI size/layout mismatches, inactive-state reporting errors, and divergence between native, compat, and xstate regsets.

## Test Signals
Tests should include ptrace get/set for FP/FX/XSTATE, coredump notes, inactive tasks, compat tasks, and CPUs with/without XSAVE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/regset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/sched.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/sched.h

## Purpose
Scheduler-facing FPU hooks for saving, dropping, cloning, flushing, and switching task FPU ownership. The header is 55 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/sched.h>`; `#include <asm/cpufeature.h>`; `#include <asm/fpu/types.h>`; `#include <asm/trace/fpu.h>`

Notable constants/macros: `#define _ASM_X86_FPU_SCHED_H`

Notable declarations and inline helpers: `#define _ASM_X86_FPU_SCHED_H`; `extern void save_fpregs_to_fpstate(struct fpu *fpu);`; `extern void fpu__drop(struct task_struct *tsk);`; `extern int fpu_clone(struct task_struct *dst, u64 clone_flags, bool minimal,`; `unsigned long shstk_addr);`; `extern void fpu_flush_thread(void);`; `static inline void switch_fpu(struct task_struct *old, int cpu)`; `struct fpu *old_fpu = x86_task_fpu(old);`

## Control Flow
switch_fpu() saves old task registers only when TIF_NEED_FPU_LOAD is clear, records AVX512 timestamp when relevant, and marks next task for lazy restore on return to userspace.

## State and Persistence
Persistent state is task->thread.fpu, last_cpu, fpstate contents, TIF_NEED_FPU_LOAD, and optional AVX512 timing metadata.

## Dependencies and Integration Points
Integrates with scheduler context switches, trace_fpu hooks, cpufeature bits, clone/exec/thread flush paths, and lazy FPU restore return path.

## Risks
Risks include stale register ownership, missed saves before kernel FPU use, timestamp skew, clone/minimal-copy bugs, and feature-dependent lazy restore regressions.

## Test Signals
Tests should exercise context switches under FP/SSE/AVX/AVX512 load, clone/exec, ptrace after switch, preemption around kernel FPU, and debug FPU consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/sched.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/signal.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/signal.h

## Purpose
Signal-frame FPU UABI helpers for sizing, copying, restoring, and converting 32-bit/FXSR FPU state. The header is 37 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/compat.h>`; `#include <linux/user.h>`; `#include <asm/fpu/types.h>`

Notable constants/macros: `#define _ASM_X86_FPU_SIGNAL_H`

Notable declarations and inline helpers: `#define _ASM_X86_FPU_SIGNAL_H`; `# define user_i387_ia32_struct user_i387_struct`; `# define user32_fxsr_struct user_fxsr_struct`; `extern void convert_from_fxsr(struct user_i387_ia32_struct *env,`; `struct task_struct *tsk);`; `extern void convert_to_fxsr(struct fxregs_state *fxsave,`; `unsigned long`; `unsigned long *buf_fx, unsigned long *size);`; `unsigned long fpu__get_fpstate_size(void);`; `extern bool copy_fpstate_to_sigframe(void __user *buf, void __user *fp, int size, u32 pkru);`; `extern void fpu__clear_user_states(struct fpu *fpu);`; `extern bool fpu__restore_sig(void __user *buf, int ia32_frame);`; `extern void restore_fpregs_from_fpstate(struct fpstate *fpstate, u64 mask);`

## Control Flow
Signal setup computes fpstate size, copies fpstate and PKRU to user sigframes, and restore paths validate user buffers before loading fpstate registers.

## State and Persistence
State is task FPU state serialized into user signal frames and restored after signal return; no filesystem persistence.

## Dependencies and Integration Points
Depends on compat/user structures, fpu/types.h, uaccess, PKRU, xstate masks, and restore_fpregs_from_fpstate().

## Risks
Risks include accepting malformed xstate, compat conversion mistakes, sigframe size mismatches for dynamic features, and PKRU restore ordering.

## Test Signals
Tests should cover native and ia32 signal delivery/return, altstack frames, XSAVE feature combinations, AMX dynamic size, bad user buffers, and PKRU preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/types.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/types.h

## Purpose
Canonical x86 FPU/xstate data model: legacy FSAVE/FXSAVE/software states, XSAVE feature masks, extended component layouts, task fpstate, permissions, and guest FPU containers. The header is 647 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/page_types.h>`

Notable constants/macros: `#define _ASM_X86_FPU_TYPES_H`; `#define MXCSR_DEFAULT 0x1f80`; `#define MXCSR_AND_FLAGS_SIZE sizeof(u64)`; `#define XFEATURE_MASK_FP (1 << XFEATURE_FP)`; `#define XFEATURE_MASK_SSE (1 << XFEATURE_SSE)`; `#define XFEATURE_MASK_YMM (1 << XFEATURE_YMM)`; `#define XFEATURE_MASK_BNDREGS (1 << XFEATURE_BNDREGS)`; `#define XFEATURE_MASK_BNDCSR (1 << XFEATURE_BNDCSR)`; `#define XFEATURE_MASK_OPMASK (1 << XFEATURE_OPMASK)`; `#define XFEATURE_MASK_ZMM_Hi256 (1 << XFEATURE_ZMM_Hi256)`; `#define XFEATURE_MASK_Hi16_ZMM (1 << XFEATURE_Hi16_ZMM)`; `#define XFEATURE_MASK_PT (1 << XFEATURE_PT_UNIMPLEMENTED_SO_FAR)`; `#define XFEATURE_MASK_PKRU (1 << XFEATURE_PKRU)`; `#define XFEATURE_MASK_PASID (1 << XFEATURE_PASID)`; `#define XFEATURE_MASK_CET_USER (1 << XFEATURE_CET_USER)`; `#define XFEATURE_MASK_CET_KERNEL (1 << XFEATURE_CET_KERNEL)`; `#define XFEATURE_MASK_LBR (1 << XFEATURE_LBR)`; `#define XFEATURE_MASK_XTILE_CFG (1 << XFEATURE_XTILE_CFG)`

Notable declarations and inline helpers: `#define _ASM_X86_FPU_TYPES_H`; `struct fregs_state {`; `u32 cwd; /* FPU Control Word */`; `u32 swd; /* FPU Status Word */`; `u32 twd; /* FPU Tag Word */`; `u32 fip; /* FPU IP Offset */`; `u32 fcs; /* FPU IP Selector */`; `u32 foo; /* FPU Operand Pointer Offset */`; `u32 fos; /* FPU Operand Pointer Selector */`; `u32 st_space[20];`; `u32 status;`; `struct fxregs_state {`; `u16 cwd; /* Control Word */`; `u16 swd; /* Status Word */`; `u16 twd; /* Tag Word */`; `u16 fop; /* Last Instruction Opcode */`; `union {`; `struct {`; `u64 rip; /* Instruction Pointer */`; `u64 rdp; /* Data Pointer */`; `u32 foo; /* FPU Operand Offset */`; `u32 fos; /* FPU Operand Selector */`; `u32 mxcsr; /* MXCSR Register State */`; `u32 mxcsr_mask; /* MXCSR Mask */`

## Control Flow
No executable control flow; structure layout and feature masks drive save/restore, signal, ptrace, prctl, scheduler, and KVM decisions across the FPU subsystem.

## State and Persistence
State is task-local struct fpu and struct fpstate, optional dynamic/vmalloc fpstate buffers, permission bitmaps, guest fpstate, XFD, and boot-time fpu_state_config globals.

## Dependencies and Integration Points
Depends on page sizing, CPU xfeature enumeration, XSAVE UABI, KVM, CET, AMX, APX, PKRU, PASID, LBR, MPX, and memory alignment rules.

## Risks
Risks are severe because layouts are ABI-sensitive: adding fields after dynamic regs, wrong xfeature masks, compacted/non-compacted confusion, or guest/user feature leakage can corrupt context or UABI.

## Test Signals
Tests need compile-time layout checks, ptrace/signal/core-dump ABI validation, context-switch stress for all xfeatures, KVM guest feature negotiation, dynamic AMX/APX permission expansion, and confidential guest paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/xcr.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/xcr.h

## Purpose
Inline wrappers for XGETBV/XSETBV and querying XINUSE state for XSAVE-enabled CPUs. The header is 35 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: None visible in this header.

Notable constants/macros: `#define _ASM_X86_FPU_XCR_H`; `#define XCR_XFEATURE_ENABLED_MASK 0x00000000`; `#define XCR_XFEATURE_IN_USE_MASK 0x00000001`

Notable declarations and inline helpers: `#define _ASM_X86_FPU_XCR_H`; `#define XCR_XFEATURE_ENABLED_MASK 0x00000000`; `#define XCR_XFEATURE_IN_USE_MASK 0x00000001`; `static __always_inline u64 xgetbv(u32 index)`; `u32 eax, edx;`; `static inline void xsetbv(u32 index, u64 value)`; `u32 eax = value;`; `u32 edx = value >> 32;`; `static __always_inline u64 xfeatures_in_use(void)`

## Control Flow
xgetbv() and xsetbv() emit raw instructions with 64-bit split registers; xfeatures_in_use() reads XCR_XFEATURE_IN_USE_MASK.

## State and Persistence
No software state; hardware XCR registers persist per CPU and control enabled/in-use xstate components.

## Dependencies and Integration Points
Integrated by FPU initialization, xstate enablement, CPU feature setup, and diagnostics that need XCR0/XINUSE.

## Risks
Risks are executing on unsupported CPUs, writing illegal XCR values, and reading in contexts where xstate is not initialized.

## Test Signals
Tests should boot on XSAVE and non-XSAVE CPUs, validate XCR0 masks during FPU init, and exercise xfeatures_in_use after using extended states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/xcr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/xstate.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/xstate.h

## Purpose
XSAVE policy header defining supported/restored/user/supervisor feature masks, XSAVE area constants, xstate size dynamism, and low-level save/restore entry points. The header is 134 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/uaccess.h>`; `#include <linux/types.h>`; `#include <asm/processor.h>`; `#include <asm/fpu/api.h>`; `#include <asm/user.h>`

Notable constants/macros: `#define __ASM_X86_XSAVE_H`; `#define XFEATURE_MASK_EXTEND (~(XFEATURE_MASK_FPSSE | (1ULL << 63)))`; `#define FXSAVE_SIZE 512`; `#define XSAVE_HDR_SIZE 64`; `#define XSAVE_HDR_OFFSET FXSAVE_SIZE`; `#define XSAVE_YMM_SIZE 256`; `#define XSAVE_YMM_OFFSET (XSAVE_HDR_SIZE + XSAVE_HDR_OFFSET)`; `#define XSAVE_ALIGNMENT 64`; `#define XFEATURE_MASK_USER_SUPPORTED (XFEATURE_MASK_FP | \`; `#define XFEATURE_MASK_USER_RESTORE \`; `#define XFEATURE_MASK_USER_DYNAMIC XFEATURE_MASK_XTILE_DATA`; `#define XFEATURE_MASK_GUEST_SUPERVISOR XFEATURE_MASK_CET_KERNEL`; `#define XFEATURE_MASK_SUPERVISOR_SUPPORTED (XFEATURE_MASK_PASID | \`; `#define XFEATURE_MASK_INDEPENDENT (XFEATURE_MASK_LBR)`; `#define XFEATURE_MASK_SUPERVISOR_UNSUPPORTED (XFEATURE_MASK_PT)`; `#define XFEATURE_MASK_SUPERVISOR_ALL (XFEATURE_MASK_SUPERVISOR_SUPPORTED | \`; `#define XFEATURE_MASK_FPSTATE (XFEATURE_MASK_USER_RESTORE | \`; `#define XFEATURE_MASK_SIGFRAME_INITOPT (XFEATURE_MASK_XTILE | \`

Notable declarations and inline helpers: `#define __ASM_X86_XSAVE_H`; `#define XFEATURE_MASK_EXTEND (~(XFEATURE_MASK_FPSSE | (1ULL << 63)))`; `#define FXSAVE_SIZE 512`; `#define XSAVE_HDR_SIZE 64`; `#define XSAVE_HDR_OFFSET FXSAVE_SIZE`; `#define XSAVE_YMM_SIZE 256`; `#define XSAVE_YMM_OFFSET (XSAVE_HDR_SIZE + XSAVE_HDR_OFFSET)`; `#define XSAVE_ALIGNMENT 64`; `#define XFEATURE_MASK_USER_SUPPORTED (XFEATURE_MASK_FP | \`; `#define XFEATURE_MASK_USER_RESTORE \`; `#define XFEATURE_MASK_USER_DYNAMIC XFEATURE_MASK_XTILE_DATA`; `#define XFEATURE_MASK_GUEST_SUPERVISOR XFEATURE_MASK_CET_KERNEL`; `#define XFEATURE_MASK_SUPERVISOR_SUPPORTED (XFEATURE_MASK_PASID | \`; `#define XFEATURE_MASK_INDEPENDENT (XFEATURE_MASK_LBR)`; `#define XFEATURE_MASK_SUPERVISOR_UNSUPPORTED (XFEATURE_MASK_PT)`; `#define XFEATURE_MASK_SUPERVISOR_ALL (XFEATURE_MASK_SUPERVISOR_SUPPORTED | \`; `#define XFEATURE_MASK_FPSTATE (XFEATURE_MASK_USER_RESTORE | \`; `#define XFEATURE_MASK_SIGFRAME_INITOPT (XFEATURE_MASK_XTILE | \`; `extern u64 xstate_fx_sw_bytes[USER_XSTATE_FX_SW_WORDS];`; `extern void __init update_regset_xstate_info(unsigned int size,`; `u64 xstate_mask);`; `int xfeature_size(int xfeature_nr);`; `void xsaves(struct xregs_state *xsave, u64 mask);`; `void xrstors(struct xregs_state *xsave, u64 mask);`

## Control Flow
Code saves/restores selected masks through xsaves()/xrstors(), resolves component addresses with xfeature_size()/get_xsave_addr(), and gates dynamic sizing through static keys.

## State and Persistence
State is boot-computed xstate_fx_sw_bytes, fpu state size configs, XFD-enabled dynamic features, and per-task fpstate masks.

## Dependencies and Integration Points
Depends on uaccess, processor features, fpu API/types, user ABI structures, static keys, and XSAVE instruction support.

## Risks
Risks include exposing unsupported supervisor features, wrong signal-frame init optimization, dynamic-size static-key mistakes, and inconsistent guest/user masks.

## Test Signals
Tests should cover xstate enumeration on varied CPUs, AMX dynamic allocation, supervisor PASID/CET paths, KVM guest masks, sigframe restore masks, and CPUs without XSAVE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fpu/xstate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/frame.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/frame.h

## Purpose
Assembler/C macros for frame-pointer prologues and encoded pt_regs frame pointers used by unwinding. The header is 113 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/asm.h>`

Notable constants/macros: `#define _ASM_X86_FRAME_H`; `#define FRAME_BEGIN \`; `#define FRAME_END "pop %" _ASM_BP "\n"`; `#define ENCODE_FRAME_POINTER \`; `#define FRAME_OFFSET __ASM_SEL(4, 8)`; `#define ENCODE_FRAME_POINTER`; `#define FRAME_BEGIN`; `#define FRAME_END`; `#define FRAME_OFFSET 0`

Notable declarations and inline helpers: `#define _ASM_X86_FRAME_H`; `#define FRAME_BEGIN \`; `#define FRAME_END "pop %" _ASM_BP "\n"`; `#define ENCODE_FRAME_POINTER \`; `static inline unsigned long encode_frame_pointer(struct pt_regs *regs)`; `#define FRAME_OFFSET __ASM_SEL(4, 8)`; `#define ENCODE_FRAME_POINTER`; `#define FRAME_BEGIN`; `#define FRAME_END`; `#define FRAME_OFFSET 0`

## Control Flow
FRAME_BEGIN/END emit rbp/ebp setup when frame pointers are enabled; ENCODE_FRAME_POINTER stores a tagged pt_regs pointer for exception-entry unwinders.

## State and Persistence
No persistent state; correctness is encoded in stack layout conventions and FRAME_OFFSET constants.

## Dependencies and Integration Points
Integrates with entry assembly, objtool/unwinder, pt_regs layout, and callable non-leaf assembly routines.

## Risks
Risks include corrupting original bp before register save, architecture tag mismatch, and unreliable stack traces if assembly omits macros.

## Test Signals
Tests should include objtool validation, ORC/frame-pointer unwinds through exceptions/interrupts, and 32-bit/64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/frame.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fred.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/fred.h

## Purpose
Flexible Return and Event Delivery definitions for FRED opcodes, stack-frame layout, entrypoints, RSP0 synchronization, and KVM event injection. The header is 119 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/const.h>`; `#include <asm/asm.h>`; `#include <asm/msr.h>`; `#include <asm/trapnr.h>`; `#include <linux/kernel.h>`; `#include <linux/sched/task_stack.h>`; `#include <asm/ptrace.h>`

Notable constants/macros: `#define ASM_X86_FRED_H`; `#define ERETS _ASM_BYTES(0xf2,0x0f,0x01,0xca)`; `#define ERETU _ASM_BYTES(0xf3,0x0f,0x01,0xca)`; `#define FRED_STACK_FRAME_RSP_MASK _AT(unsigned long, (~0x3f))`; `#define FRED_CONFIG_REDZONE_AMOUNT 1`; `#define FRED_CONFIG_REDZONE (_AT(unsigned long, FRED_CONFIG_REDZONE_AMOUNT) << 6)`; `#define FRED_CONFIG_INT_STKLVL(l) (_AT(unsigned long, l) << 9)`; `#define FRED_CONFIG_ENTRYPOINT(p) _AT(unsigned long, (p))`

Notable declarations and inline helpers: `#define ASM_X86_FRED_H`; `#define ERETS _ASM_BYTES(0xf2,0x0f,0x01,0xca)`; `#define ERETU _ASM_BYTES(0xf3,0x0f,0x01,0xca)`; `#define FRED_STACK_FRAME_RSP_MASK _AT(unsigned long, (~0x3f))`; `#define FRED_CONFIG_REDZONE_AMOUNT 1`; `#define FRED_CONFIG_REDZONE (_AT(unsigned long, FRED_CONFIG_REDZONE_AMOUNT) << 6)`; `#define FRED_CONFIG_INT_STKLVL(l) (_AT(unsigned long, l) << 9)`; `#define FRED_CONFIG_ENTRYPOINT(p) _AT(unsigned long, (p))`; `struct fred_info {`; `unsigned long edata;`; `unsigned long resv;`; `struct fred_frame {`; `struct pt_regs regs;`; `struct fred_info info;`; `static __always_inline struct fred_info *fred_info(struct pt_regs *regs)`; `static __always_inline unsigned long fred_event_data(struct pt_regs *regs)`; `void asm_fred_entrypoint_user(void);`; `void asm_fred_entrypoint_kernel(void);`; `void asm_fred_entry_from_kvm(struct fred_ss);`; `static __always_inline void fred_entry_from_kvm(unsigned int type, unsigned int vector)`; `struct fred_ss ss = {`; `void cpu_init_fred_exceptions(void);`; `void cpu_init_fred_rsps(void);`; `void fred_complete_exception_setup(void);`

## Control Flow
FRED entry code builds a fred_frame containing pt_regs plus event data; fred_update_rsp0 writes MSR_IA32_FRED_RSP0 only when current task stack top changes.

## State and Persistence
State is per-CPU fred_rsp0 and hardware FRED MSRs; event data is transient in the FRED stack frame.

## Dependencies and Integration Points
Depends on MSR accessors, trap numbers, pt_regs, task stack layout, CPU feature checks, and KVM FRED injection helpers.

## Risks
Risks include stale RSP0 after task switch, wrong event type/vector encoding, binutils opcode compatibility, and divergence from IDT paths.

## Test Signals
Tests should cover boot with FRED enabled/disabled, exception/interrupt delivery, NMI/KVM injected events, task switch RSP0 updates, and fallback stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fred.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fsgsbase.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/fsgsbase.h

## Purpose
64-bit FS/GS base helpers for task state and CPU register/MSR access with optional FSGSBASE instruction use. The header is 85 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/msr.h>`; `#include <asm/cpufeature.h>`

Notable constants/macros: `#define _ASM_FSGSBASE_H`

Notable declarations and inline helpers: `#define _ASM_FSGSBASE_H`; `extern unsigned long x86_fsbase_read_task(struct task_struct *task);`; `extern unsigned long x86_gsbase_read_task(struct task_struct *task);`; `extern void x86_fsbase_write_task(struct task_struct *task, unsigned long fsbase);`; `extern void x86_gsbase_write_task(struct task_struct *task, unsigned long gsbase);`; `static __always_inline unsigned long rdfsbase(void)`; `unsigned long fsbase;`; `static __always_inline unsigned long rdgsbase(void)`; `unsigned long gsbase;`; `static __always_inline void wrfsbase(unsigned long fsbase)`; `static __always_inline void wrgsbase(unsigned long gsbase)`; `static inline unsigned long x86_fsbase_read_cpu(void)`; `static inline void x86_fsbase_write_cpu(unsigned long fsbase)`; `extern unsigned long x86_gsbase_read_cpu_inactive(void);`; `extern void x86_gsbase_write_cpu_inactive(unsigned long gsbase);`; `extern unsigned long x86_fsgsbase_read_task(struct task_struct *task,`; `unsigned short selector);`

## Control Flow
Inline CPU helpers choose RDFSBASE/WRFSBASE when supported or MSR_FS_BASE fallback; GS inactive base is delegated to external helpers because swapgs state matters.

## State and Persistence
State is task thread FS/GS base and CPU FS/GS base registers/MSRs; changes persist across context switch state management.

## Dependencies and Integration Points
Depends on cpufeature checks, MSR access, task_struct thread state, and ptrace/arch_prctl paths.

## Risks
Risks include using instruction helpers without feature checks, confusing active/inactive GS base, and races when reading running tasks.

## Test Signals
Tests should cover arch_prctl, ptrace stopped tasks, context switches, FSGSBASE-enabled and MSR-only CPUs, and swapgs-sensitive kernel GS paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/fsgsbase.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/ftrace.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/ftrace.h

## Purpose
x86 ftrace integration for fentry address adjustment, dynamic direct-call metadata, graph tracing, syscall name matching, and compat syscall filtering. The header is 164 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/ptrace.h>`; `#include <linux/ftrace_regs.h>`; `#include <linux/compat.h>`

Notable constants/macros: `#define _ASM_X86_FTRACE_H`; `#define MCOUNT_INSN_SIZE 5 /* sizeof mcount call */`; `#define ARCH_SUPPORTS_FTRACE_OPS 1`; `#define ftrace_get_symaddr(fentry_ip) arch_ftrace_get_symaddr(fentry_ip)`; `#define arch_ftrace_partial_regs(regs) do { \`; `#define arch_ftrace_fill_perf_regs(fregs, _regs) do { \`; `#define ftrace_regs_set_instruction_pointer(fregs, _ip) \`; `#define ftrace_graph_func ftrace_graph_func`; `#define FTRACE_GRAPH_TRAMP_ADDR FTRACE_GRAPH_ADDR`; `#define arch_ftrace_set_direct_caller(fregs, addr) \`; `#define ARCH_HAS_SYSCALL_MATCH_SYM_NAME`; `#define ARCH_TRACE_IGNORE_COMPAT_SYSCALLS 1`

Notable declarations and inline helpers: `#define _ASM_X86_FTRACE_H`; `# define MCOUNT_ADDR ((unsigned long)(__fentry__))`; `#define MCOUNT_INSN_SIZE 5 /* sizeof mcount call */`; `# define FTRACE_MCOUNT_MAX_OFFSET ENDBR_INSN_SIZE`; `#define ARCH_SUPPORTS_FTRACE_OPS 1`; `extern void __fentry__(void);`; `static inline unsigned long ftrace_call_adjust(unsigned long addr)`; `static inline unsigned long arch_ftrace_get_symaddr(unsigned long fentry_ip)`; `#define ftrace_get_symaddr(fentry_ip) arch_ftrace_get_symaddr(fentry_ip)`; `static __always_inline struct pt_regs *`; `#define arch_ftrace_partial_regs(regs) do { \`; `#define arch_ftrace_fill_perf_regs(fregs, _regs) do { \`; `#define ftrace_regs_set_instruction_pointer(fregs, _ip) \`; `static __always_inline unsigned long`; `struct ftrace_ops;`; `#define ftrace_graph_func ftrace_graph_func`; `void ftrace_graph_func(unsigned long ip, unsigned long parent_ip,`; `struct ftrace_ops *op, struct ftrace_regs *fregs);`; `#define FTRACE_GRAPH_TRAMP_ADDR FTRACE_GRAPH_ADDR`; `static inline void`; `#define arch_ftrace_set_direct_caller(fregs, addr) \`; `struct dyn_arch_ftrace {`; `void prepare_ftrace_return(unsigned long ip, unsigned long *parent,`; `unsigned long frame_pointer);`

## Control Flow
When dynamic ftrace is enabled, fentry IPs are adjusted around ENDBR, ftrace_regs are mapped to pt_regs, direct caller fields are filled, and graph return preparation hooks patch return paths.

## State and Persistence
State is dynamic ftrace records, per-call saved regs, dyn_arch_ftrace flags, and ftrace ops memory protection state managed elsewhere.

## Dependencies and Integration Points
Depends on ptrace regs, IBT ENDBR detection, function tracer config, ftrace_regs, graph tracer, syscall naming, and compat task detection.

## Risks
Risks include off-by-ENDBR symbol resolution, partial-register assumptions, incorrect direct-call IP storage, and tracing compat syscalls unexpectedly.

## Test Signals
Tests should run dynamic ftrace, function graph, direct trampolines, perf regs collection, IBT-enabled kernels, and compat syscall tracing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/ftrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/futex.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/futex.h

## Purpose
x86 futex atomic user-memory operations and cmpxchg helpers implemented with inline assembly and exception-table recovery. The header is 98 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/futex.h>`; `#include <linux/uaccess.h>`; `#include <asm/asm.h>`; `#include <asm/errno.h>`; `#include <asm/processor.h>`; `#include <asm/smap.h>`

Notable constants/macros: `#define _ASM_X86_FUTEX_H`; `#define unsafe_atomic_op1(insn, oval, uaddr, oparg, label) \`; `#define unsafe_atomic_op2(insn, oval, uaddr, oparg, label) \`

Notable declarations and inline helpers: `#define _ASM_X86_FUTEX_H`; `#define unsafe_atomic_op1(insn, oval, uaddr, oparg, label) \`; `int oldval = 0, ret; \`; `#define unsafe_atomic_op2(insn, oval, uaddr, oparg, label) \`; `int oldval = 0, ret, tem; \`; `static __always_inline int arch_futex_atomic_op_inuser(int op, int oparg, int *oval,`; `u32 __user *uaddr)`; `static inline int futex_atomic_cmpxchg_inatomic(u32 *uval, u32 __user *uaddr,`; `u32 oldval, u32 newval)`; `int ret = 0;`

## Control Flow
arch_futex_atomic_op_inuser() scopes user access, runs xchg/xadd/CAS loops for FUTEX_OP_* and jumps to -EFAULT fixups on user faults; cmpxchg helpers compare and exchange u32 futex words.

## State and Persistence
State is user-space futex words modified atomically; kernel local old-value outputs report prior state and errors.

## Dependencies and Integration Points
Depends on futex core, uaccess scopes, SMAP handling, LOCK_PREFIX, processor alternatives, and extable EX_TYPE_EFAULT_REG encoding.

## Risks
Risks include missing user access protection, wrong condition handling, ABA-style user races expected by futex semantics, and assembly constraint/extable mistakes.

## Test Signals
Tests should include futex atomic ops on valid and faulting addresses, concurrent wait/wake stress, SMAP-enabled builds, 32/64-bit builds, and all FUTEX_OP condition codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/futex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/gart.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/gart.h

## Purpose
GART/IOMMU aperture declarations and helpers for older AMD64-style DMA remapping and AGP aperture handling. The header is 113 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/e820/api.h>`

Notable constants/macros: `#define _ASM_X86_GART_H`; `#define GPTE_VALID 1`; `#define GPTE_COHERENT 2`; `#define GARTEN (1<<0)`; `#define DISGARTCPU (1<<4)`; `#define DISGARTIO (1<<5)`; `#define DISTLBWALKPRB (1<<6)`; `#define INVGART (1<<0)`; `#define GARTPTEERR (1<<1)`; `#define AMD64_GARTAPERTURECTL 0x90`; `#define AMD64_GARTAPERTUREBASE 0x94`; `#define AMD64_GARTTABLEBASE 0x98`; `#define AMD64_GARTCACHECTL 0x9c`; `#define gart_iommu_aperture 0`; `#define gart_iommu_aperture_allowed 0`; `#define gart_iommu_aperture_disabled 1`

Notable declarations and inline helpers: `#define _ASM_X86_GART_H`; `extern void set_up_gart_resume(u32, u32);`; `extern int fallback_aper_order;`; `extern int fallback_aper_force;`; `extern int fix_aperture;`; `#define GPTE_VALID 1`; `#define GPTE_COHERENT 2`; `#define GARTEN (1<<0)`; `#define DISGARTCPU (1<<4)`; `#define DISGARTIO (1<<5)`; `#define DISTLBWALKPRB (1<<6)`; `#define INVGART (1<<0)`; `#define GARTPTEERR (1<<1)`; `#define AMD64_GARTAPERTURECTL 0x90`; `#define AMD64_GARTAPERTUREBASE 0x94`; `#define AMD64_GARTTABLEBASE 0x98`; `#define AMD64_GARTCACHECTL 0x9c`; `extern int gart_iommu_aperture;`; `extern int gart_iommu_aperture_allowed;`; `extern int gart_iommu_aperture_disabled;`; `extern void early_gart_iommu_check(void);`; `extern int gart_iommu_init(void);`; `extern void __init gart_parse_options(char *);`; `void gart_iommu_hole_init(void);`

## Control Flow
Callers query aperture_valid(), gart_iommu_aperture, fallback_aper_order, and AGP bridge apertures to decide whether a GART aperture can back DMA remapping.

## State and Persistence
State is global aperture configuration, fallback order, AGP bridge aperture list, and aperture_resource tracked at boot/runtime.

## Dependencies and Integration Points
Depends on PCI, resource management, e820/memory setup, SWIOTLB/IOMMU selection, and AMD64 GART implementation files.

## Risks
Risks include stale legacy hardware assumptions, aperture overlap with RAM/MMIO, and bad fallback sizing causing DMA failures.

## Test Signals
Tests should boot legacy GART-capable systems or emulation, validate aperture reservation, DMA mapping fallback, AGP aperture discovery, and no-IOMMU configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/gart.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/genapic.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/genapic.h

## Purpose
Compatibility include that forwards generic APIC users to asm/apic.h. The header is 1 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/apic.h>`

Notable constants/macros: None visible in this header.

Notable declarations and inline helpers: None visible in this header.

## Control Flow
No control flow or state; it is a one-line include shim.

## State and Persistence
State and persistence are inherited from APIC code, not this file.

## Dependencies and Integration Points
Integrated by older code that still includes genapic.h after APIC header consolidation.

## Risks
Risk is limited to include-order or stale dependency assumptions.

## Test Signals
Test signal is compile coverage of legacy include users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/genapic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/geode.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/geode.h

## Purpose
AMD Geode SoC helper declarations for MSR access and GPIO register operations. The header is 33 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/processor.h>`; `#include <linux/io.h>`; `#include <linux/cs5535.h>`

Notable constants/macros: `#define _ASM_X86_GEODE_H`

Notable declarations and inline helpers: `#define _ASM_X86_GEODE_H`; `static inline int is_geode_gx(void)`; `static inline int is_geode_lx(void)`; `static inline int is_geode(void)`

## Control Flow
Wrappers expose geode-specific MSR read/write and GPIO set/clear methods used by board/platform drivers.

## State and Persistence
State lives in Geode chipset MSRs and GPIO registers; no software persistence is stored here.

## Dependencies and Integration Points
Depends on linux/io.h, MSR access, and platform drivers for Geode-era x86 systems.

## Risks
Risks include wrong GPIO mask operations, unavailable hardware coverage, and unsafe use on non-Geode systems.

## Test Signals
Tests should compile Geode configs and, on hardware, verify GPIO set/clear and MSR access paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/geode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/gsseg.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/gsseg.h

## Purpose
Helpers for GS-segment based percpu addressing in 32-bit and 64-bit x86 contexts. The header is 66 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/types.h>`; `#include <asm/asm.h>`; `#include <asm/cpufeature.h>`; `#include <asm/alternative.h>`; `#include <asm/processor.h>`; `#include <asm/nops.h>`

Notable constants/macros: `#define _ASM_X86_GSSEG_H`; `#define LKGS_DI _ASM_BYTES(0xf2,0x0f,0x00,0xf7)`

Notable declarations and inline helpers: `#define _ASM_X86_GSSEG_H`; `extern asmlinkage void asm_load_gs_index(u16 selector);`; `#define LKGS_DI _ASM_BYTES(0xf2,0x0f,0x00,0xf7)`; `static inline void native_lkgs(unsigned int selector)`; `u16 sel = selector;`; `static inline void native_load_gs_index(unsigned int selector)`; `unsigned long flags;`; `static inline void __init lkgs_init(void)`; `static inline void load_gs_index(unsigned int selector)`

## Control Flow
Macros and inline assembly access percpu/current data through GS-relative offsets or alternate segment forms depending on configuration.

## State and Persistence
State is implicit in CPU segment base and percpu layout; callers read/write per-CPU memory rather than file-local state.

## Dependencies and Integration Points
Depends on asm/percpu, segment setup, FSGSBASE/swapgs conventions, and compiler asm constraints.

## Risks
Risks include wrong segment assumption across user/kernel transitions, incorrect offset size, and hard-to-debug percpu corruption.

## Test Signals
Tests should cover percpu access on 32-bit/64-bit, context switches, interrupt entry, and configs with different segment-base mechanisms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/gsseg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/hardirq.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/hardirq.h

## Purpose
x86 hardirq accounting declarations and per-CPU IRQ stack metadata. The header is 97 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/threads.h>`

Notable constants/macros: `#define _ASM_X86_HARDIRQ_H`; `#define __ARCH_IRQ_STAT`; `#define inc_irq_stat(member) this_cpu_inc(irq_stat.member)`; `#define arch_irq_stat_cpu arch_irq_stat_cpu`; `#define arch_irq_stat arch_irq_stat`; `#define local_softirq_pending_ref __softirq_pending`

Notable declarations and inline helpers: `#define _ASM_X86_HARDIRQ_H`; `typedef struct {`; `u8 kvm_cpu_l1tf_flush_l1d;`; `unsigned int __nmi_count; /* arch dependent */`; `unsigned int apic_timer_irqs; /* arch dependent */`; `unsigned int irq_spurious_count;`; `unsigned int icr_read_retry_count;`; `unsigned int kvm_posted_intr_ipis;`; `unsigned int kvm_posted_intr_wakeup_ipis;`; `unsigned int kvm_posted_intr_nested_ipis;`; `unsigned int perf_guest_mediated_pmis;`; `unsigned int x86_platform_ipis; /* arch dependent */`; `unsigned int apic_perf_irqs;`; `unsigned int apic_irq_work_irqs;`; `unsigned int irq_resched_count;`; `unsigned int irq_call_count;`; `unsigned int irq_tlb_count;`; `unsigned int irq_thermal_count;`; `unsigned int irq_threshold_count;`; `unsigned int irq_deferred_error_count;`; `unsigned int irq_hv_callback_count;`; `unsigned int irq_hv_reenlightenment_count;`; `unsigned int hyperv_stimer0_count;`; `unsigned int posted_msi_notification_count;`

## Control Flow
The interrupt entry code increments/decrements hardirq state through generic code while x86 uses per-CPU irq_stack_ptr and irq_count fields where configured.

## State and Persistence
State is per-CPU hardirq counters and IRQ stack pointers, consumed by entry, lockdep, RCU, and stack-switching paths.

## Dependencies and Integration Points
Depends on linux/threads, irq_cpustat, cache alignment, SMP/percpu, and x86_64 IRQ stack setup.

## Risks
Risks include counter imbalance, wrong stack pointer initialization, and RCU/lockdep seeing incorrect interrupt context.

## Test Signals
Tests should stress nested interrupts, softirq from hardirq, CPU hotplug, lockdep IRQ state checks, and 32/64-bit stack configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/hardirq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/highmem.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/highmem.h

## Purpose
32-bit highmem mapping constants and helpers for permanent kmap and temporary kmap-local support. The header is 73 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/interrupt.h>`; `#include <linux/threads.h>`; `#include <asm/tlbflush.h>`; `#include <asm/fixmap.h>`; `#include <asm/pgtable_areas.h>`

Notable constants/macros: `#define _ASM_X86_HIGHMEM_H`; `#define LAST_PKMAP_MASK (LAST_PKMAP-1)`; `#define PKMAP_NR(virt) ((virt-PKMAP_BASE) >> PAGE_SHIFT)`; `#define PKMAP_ADDR(nr) (PKMAP_BASE + ((nr) << PAGE_SHIFT))`; `#define flush_cache_kmaps() do { } while (0)`; `#define arch_kmap_local_post_map(vaddr, pteval) \`; `#define arch_kmap_local_post_unmap(vaddr) \`

Notable declarations and inline helpers: `#define _ASM_X86_HIGHMEM_H`; `extern unsigned long highstart_pfn, highend_pfn;`; `#define LAST_PKMAP_MASK (LAST_PKMAP-1)`; `#define PKMAP_NR(virt) ((virt-PKMAP_BASE) >> PAGE_SHIFT)`; `#define PKMAP_ADDR(nr) (PKMAP_BASE + ((nr) << PAGE_SHIFT))`; `#define flush_cache_kmaps() do { } while (0)`; `#define arch_kmap_local_post_map(vaddr, pteval) \`; `#define arch_kmap_local_post_unmap(vaddr) \`

## Control Flow
Highmem users map pages through pkmap/fixmap slots and convert kmap virtual addresses back to pages; on non-highmem paths most behavior is absent.

## State and Persistence
State is pkmap_page_table and kmap-local fixmap slots, with mappings managed by highmem core.

## Dependencies and Integration Points
Depends on fixmap, pgtable, kmap_size, page flags, and x86_32 memory layout.

## Risks
Risks include stale temporary mappings, wrong page-table attributes, and 32-bit-only assumptions leaking into generic code.

## Test Signals
Tests should cover HIGHMEM32 configs, kmap/kunmap, kmap_local nesting, debug forced-map mode, and highmem I/O paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/highmem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/hpet.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/hpet.h

## Purpose
HPET timer declarations, ID constants, and boot/runtime hooks for x86 high precision event timers. The header is 102 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/msi.h>`; `#include <linux/interrupt.h>`

Notable constants/macros: `#define _ASM_X86_HPET_H`; `#define HPET_MMAP_SIZE 1024`; `#define HPET_ID 0x000`; `#define HPET_PERIOD 0x004`; `#define HPET_CFG 0x010`; `#define HPET_STATUS 0x020`; `#define HPET_COUNTER 0x0f0`; `#define HPET_Tn_CFG(n) (0x100 + 0x20 * n)`; `#define HPET_Tn_CMP(n) (0x108 + 0x20 * n)`; `#define HPET_Tn_ROUTE(n) (0x110 + 0x20 * n)`; `#define HPET_T0_CFG 0x100`; `#define HPET_T0_CMP 0x108`; `#define HPET_T0_ROUTE 0x110`; `#define HPET_T1_CFG 0x120`; `#define HPET_T1_CMP 0x128`; `#define HPET_T1_ROUTE 0x130`; `#define HPET_T2_CFG 0x140`; `#define HPET_T2_CMP 0x148`

Notable declarations and inline helpers: `#define _ASM_X86_HPET_H`; `#define HPET_MMAP_SIZE 1024`; `#define HPET_ID 0x000`; `#define HPET_PERIOD 0x004`; `#define HPET_CFG 0x010`; `#define HPET_STATUS 0x020`; `#define HPET_COUNTER 0x0f0`; `#define HPET_Tn_CFG(n) (0x100 + 0x20 * n)`; `#define HPET_Tn_CMP(n) (0x108 + 0x20 * n)`; `#define HPET_Tn_ROUTE(n) (0x110 + 0x20 * n)`; `#define HPET_T0_CFG 0x100`; `#define HPET_T0_CMP 0x108`; `#define HPET_T0_ROUTE 0x110`; `#define HPET_T1_CFG 0x120`; `#define HPET_T1_CMP 0x128`; `#define HPET_T1_ROUTE 0x130`; `#define HPET_T2_CFG 0x140`; `#define HPET_T2_CMP 0x148`; `#define HPET_T2_ROUTE 0x150`; `#define HPET_ID_REV 0x000000ff`; `#define HPET_ID_NUMBER 0x00001f00`; `#define HPET_ID_64BIT 0x00002000`; `#define HPET_ID_LEGSUP 0x00008000`; `#define HPET_ID_VENDOR 0xffff0000`

## Control Flow
Boot code probes HPET address/configuration, initializes clockevent/clocksource paths, may force or disable HPET, and exposes MSI/remapping support where available.

## State and Persistence
State is global HPET enablement, memory-mapped HPET registers, legacy replacement mode, and per-channel timer allocation managed by implementation files.

## Dependencies and Integration Points
Depends on io mapping, APIC/IRQ routing, ACPI/platform timer discovery, clockevents, and x86 boot parameters.

## Risks
Risks include broken firmware tables, unsafe MMIO mapping, interrupt routing failures, and clocksource instability.

## Test Signals
Tests should boot with hpet=on/off/force, validate clocksource selection, periodic/oneshot timers, MSI HPET channels, suspend/resume, and systems without HPET.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/hpet.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/hugetlb.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/hugetlb.h

## Purpose
Thin x86 hugetlb include that delegates hugepage architecture hooks to generic pgtable/page definitions. The header is 10 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/page.h>`; `#include <asm-generic/hugetlb.h>`

Notable constants/macros: `#define _ASM_X86_HUGETLB_H`; `#define hugepages_supported() boot_cpu_has(X86_FEATURE_PSE)`

Notable declarations and inline helpers: `#define _ASM_X86_HUGETLB_H`; `#define hugepages_supported() boot_cpu_has(X86_FEATURE_PSE)`

## Control Flow
Control flow is absent; it exposes architecture declarations or empty behavior depending on config through included definitions.

## State and Persistence
State is managed by hugetlb/mm core and page tables, not this header.

## Dependencies and Integration Points
Depends on asm/page.h, pgtable conventions, and generic hugetlb integration.

## Risks
Risks are mostly compile-time include drift and page-size configuration mismatches.

## Test Signals
Tests should include hugetlbfs mmap, hugepage fault/unmap, and x86 page-size variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/hugetlb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/hw_breakpoint.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/hw_breakpoint.h

## Purpose
x86 hardware breakpoint interface for debug-register slot counts, masks, validation, and perf breakpoint integration. The header is 77 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <uapi/asm/hw_breakpoint.h>`; `#include <linux/kdebug.h>`; `#include <linux/percpu.h>`; `#include <linux/list.h>`

Notable constants/macros: `#define _I386_HW_BREAKPOINT_H`; `#define __ARCH_HW_BREAKPOINT_H`; `#define X86_BREAKPOINT_LEN_X 0x40`; `#define X86_BREAKPOINT_LEN_1 0x40`; `#define X86_BREAKPOINT_LEN_2 0x44`; `#define X86_BREAKPOINT_LEN_4 0x4c`; `#define X86_BREAKPOINT_LEN_8 0x48`; `#define X86_BREAKPOINT_EXECUTE 0x80`; `#define X86_BREAKPOINT_WRITE 0x81`; `#define X86_BREAKPOINT_RW 0x83`; `#define HBP_NUM 4`; `#define hw_breakpoint_slots(type) (HBP_NUM)`

Notable declarations and inline helpers: `#define _I386_HW_BREAKPOINT_H`; `#define __ARCH_HW_BREAKPOINT_H`; `struct arch_hw_breakpoint {`; `unsigned long address;`; `unsigned long mask;`; `u8 len;`; `u8 type;`; `#define X86_BREAKPOINT_LEN_X 0x40`; `#define X86_BREAKPOINT_LEN_1 0x40`; `#define X86_BREAKPOINT_LEN_2 0x44`; `#define X86_BREAKPOINT_LEN_4 0x4c`; `#define X86_BREAKPOINT_LEN_8 0x48`; `#define X86_BREAKPOINT_EXECUTE 0x80`; `#define X86_BREAKPOINT_WRITE 0x81`; `#define X86_BREAKPOINT_RW 0x83`; `#define HBP_NUM 4`; `#define hw_breakpoint_slots(type) (HBP_NUM)`; `struct perf_event_attr;`; `struct perf_event;`; `struct pmu;`; `extern int arch_check_bp_in_kernelspace(struct arch_hw_breakpoint *hw);`; `extern int hw_breakpoint_arch_parse(struct perf_event *bp,`; `struct arch_hw_breakpoint *hw);`; `extern int hw_breakpoint_exceptions_notify(struct notifier_block *unused,`

## Control Flow
Breakpoint setup validates lengths/types, encodes DR7 control bits, and coordinates debug register access through implementation functions declared here.

## State and Persistence
State lives in CPU debug registers DR0-DR7, per-task/perf breakpoint metadata, and ptrace-visible debug state.

## Dependencies and Integration Points
Depends on perf_event, ptrace, debug exception handling, processor debug registers, and notifier paths.

## Risks
Risks include leaking debug registers across tasks, wrong length/type encoding, recursion in #DB handling, and conflicts with kgdb/kprobes.

## Test Signals
Tests should cover perf breakpoints, ptrace watchpoints, task switch isolation, invalid ranges, single-step interactions, and virtualization/debug exceptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/hw_breakpoint.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/hw_irq.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/hw_irq.h

## Purpose
x86 hardware IRQ/vector allocation structures, vector-to-desc mapping, APIC acknowledgement hooks, and interrupt statistics. The header is 135 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/irq_vectors.h>`; `#include <linux/percpu.h>`; `#include <linux/profile.h>`; `#include <linux/smp.h>`; `#include <linux/atomic.h>`; `#include <asm/irq.h>`; `#include <asm/sections.h>`

Notable constants/macros: `#define _ASM_X86_HW_IRQ_H`; `#define trace_irq_entries_start irq_entries_start`; `#define VECTOR_UNUSED NULL`; `#define VECTOR_SHUTDOWN ((void *)-1L)`; `#define VECTOR_RETRIGGERED ((void *)-2L)`

Notable declarations and inline helpers: `#define _ASM_X86_HW_IRQ_H`; `struct irq_data;`; `struct pci_dev;`; `struct msi_desc;`; `enum irq_alloc_type {`; `struct ioapic_alloc_info {`; `int pin;`; `int node;`; `u32 is_level : 1;`; `u32 active_low : 1;`; `u32 valid : 1;`; `struct uv_alloc_info {`; `int limit;`; `int blade;`; `unsigned long offset;`; `struct irq_alloc_info {`; `enum irq_alloc_type type;`; `u32 flags;`; `u32 devid;`; `struct msi_desc *desc;`; `void *data;`; `union {`; `struct ioapic_alloc_info ioapic;`; `struct uv_alloc_info uv;`

## Control Flow
IRQ domain allocation fills irq_alloc_info, vector assignment records irq_cfg per IRQ, and entry stubs use per-CPU vector_irq arrays to dispatch vectors.

## State and Persistence
State is per-CPU vector_irq, irq_cfg mappings, irq_err_count/irq_mis_count, and vector cleanup state.

## Dependencies and Integration Points
Depends on irq_vectors.h, irqdomain hierarchy, APIC, MSI descriptors, SMP, percpu storage, and tracing symbols for entry stubs.

## Risks
Risks include vector leaks, stale vector cleanup after migration, incorrect IRQ allocation type data, and interrupt stats hiding routing bugs.

## Test Signals
Tests should exercise IO-APIC, MSI/MSI-X, CPU affinity changes, hotplug, vector exhaustion, spurious/error interrupts, and tracing entry symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/hw_irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/hyperv_timer.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/hyperv_timer.h

## Purpose
Hyper-V synthetic timer declarations for x86 guest clockevent integration. The header is 9 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/msr.h>`

Notable constants/macros: `#define _ASM_X86_HYPERV_TIMER_H`; `#define hv_get_raw_timer() rdtsc_ordered()`

Notable declarations and inline helpers: `#define _ASM_X86_HYPERV_TIMER_H`; `#define hv_get_raw_timer() rdtsc_ordered()`

## Control Flow
The implementation registers per-CPU synthetic timer devices and receives Hyper-V timer callbacks through architecture vector plumbing.

## State and Persistence
State lives in Hyper-V synthetic timer MSRs/messages and clockevent device data managed outside this header.

## Dependencies and Integration Points
Depends on CONFIG_HYPERV, Hyper-V vector definitions, clockevents, and hypervisor callback setup.

## Risks
Risks include missing callback vector routing, CPU hotplug timer state loss, and guest clock drift under reenlightenment.

## Test Signals
Tests should boot on Hyper-V, validate stimer interrupts, CPU hotplug, suspend/resume or reenlightenment, and non-Hyper-V compile stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/hyperv_timer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/hypervisor.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/hypervisor.h

## Purpose
Common x86 hypervisor detection and initialization interface for VMware, Hyper-V, Xen, KVM, Jailhouse, ACRN, bhyve, and native mode. The header is 85 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/kvm_para.h>`; `#include <asm/x86_init.h>`; `#include <asm/xen/hypervisor.h>`

Notable constants/macros: `#define _ASM_X86_HYPERVISOR_H`

Notable declarations and inline helpers: `#define _ASM_X86_HYPERVISOR_H`; `enum x86_hypervisor_type {`; `struct hypervisor_x86 {`; `enum x86_hypervisor_type type;`; `struct x86_hyper_init init;`; `struct x86_hyper_runtime runtime;`; `bool ignore_nopv;`; `extern const struct hypervisor_x86 x86_hyper_vmware;`; `extern const struct hypervisor_x86 x86_hyper_ms_hyperv;`; `extern const struct hypervisor_x86 x86_hyper_xen_pv;`; `extern const struct hypervisor_x86 x86_hyper_kvm;`; `extern const struct hypervisor_x86 x86_hyper_jailhouse;`; `extern const struct hypervisor_x86 x86_hyper_acrn;`; `extern const struct hypervisor_x86 x86_hyper_bhyve;`; `extern struct hypervisor_x86 x86_hyper_xen_hvm;`; `extern bool nopv;`; `extern enum x86_hypervisor_type x86_hyper_type;`; `extern void init_hypervisor_platform(void);`; `static inline bool hypervisor_is_type(enum x86_hypervisor_type type)`; `static inline void init_hypervisor_platform(void) { }`

## Control Flow
init_hypervisor_platform() selects a detected hypervisor descriptor and applies init/runtime callbacks unless nopv disables paravirtualization for descriptors that honor it.

## State and Persistence
State is global x86_hyper_type, nopv, and registered hypervisor_x86 descriptors with init/runtime callback tables.

## Dependencies and Integration Points
Depends on kvm_para, x86_init, Xen hypervisor hooks, CPUID/vendor detection, and early boot init ordering.

## Risks
Risks include mis-detection, wrong callback ordering, nopv bypass for ignore_nopv descriptors, and native fallback behavior changing guest boot.

## Test Signals
Tests should boot native and each supported guest type, verify nopv behavior, CPUID detection, callback installation, and paravirt feature exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/hypervisor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/i8259.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/i8259.h

## Purpose
Legacy 8259A PIC interface for ISA IRQ initialization, masking, vector setup, and shutdown. The header is 87 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/delay.h>`; `#include <asm/io.h>`

Notable constants/macros: `#define _ASM_X86_I8259_H`; `#define __byte(x, y) (((unsigned char *)&(y))[x])`; `#define cached_master_mask (__byte(0, cached_irq_mask))`; `#define cached_slave_mask (__byte(1, cached_irq_mask))`; `#define PIC_MASTER_CMD 0x20`; `#define PIC_MASTER_IMR 0x21`; `#define PIC_MASTER_ISR PIC_MASTER_CMD`; `#define PIC_MASTER_POLL PIC_MASTER_ISR`; `#define PIC_MASTER_OCW3 PIC_MASTER_ISR`; `#define PIC_SLAVE_CMD 0xa0`; `#define PIC_SLAVE_IMR 0xa1`; `#define PIC_ELCR1 0x4d0`; `#define PIC_ELCR2 0x4d1`; `#define PIC_CASCADE_IR 2`; `#define MASTER_ICW4_DEFAULT 0x01`; `#define SLAVE_ICW4_DEFAULT 0x01`; `#define PIC_ICW4_AEOI 2`

Notable declarations and inline helpers: `#define _ASM_X86_I8259_H`; `extern unsigned int cached_irq_mask;`; `#define __byte(x, y) (((unsigned char *)&(y))[x])`; `#define cached_master_mask (__byte(0, cached_irq_mask))`; `#define cached_slave_mask (__byte(1, cached_irq_mask))`; `#define PIC_MASTER_CMD 0x20`; `#define PIC_MASTER_IMR 0x21`; `#define PIC_MASTER_ISR PIC_MASTER_CMD`; `#define PIC_MASTER_POLL PIC_MASTER_ISR`; `#define PIC_MASTER_OCW3 PIC_MASTER_ISR`; `#define PIC_SLAVE_CMD 0xa0`; `#define PIC_SLAVE_IMR 0xa1`; `#define PIC_ELCR1 0x4d0`; `#define PIC_ELCR2 0x4d1`; `#define PIC_CASCADE_IR 2`; `#define MASTER_ICW4_DEFAULT 0x01`; `#define SLAVE_ICW4_DEFAULT 0x01`; `#define PIC_ICW4_AEOI 2`; `extern raw_spinlock_t i8259A_lock;`; `static inline unsigned char inb_pic(unsigned int port)`; `unsigned char value = inb(port);`; `static inline void outb_pic(unsigned char value, unsigned int port)`; `extern struct irq_chip i8259A_chip;`; `struct legacy_pic {`

## Control Flow
Initialization programs master/slave PICs, sets legacy vector bases, masks/unmasks IRQ lines, and cooperates with IO-APIC or virtual wire modes.

## State and Persistence
State is PIC mask registers, cached interrupt masks, and legacy IRQ routing state in implementation files.

## Dependencies and Integration Points
Depends on port I/O, irqdesc, irqdomain/IO-APIC transition code, APIC mode setup, and legacy ISA drivers.

## Risks
Risks include incorrect masking during APIC handoff, spurious IRQ7/15 behavior, and broken legacy systems or VMs.

## Test Signals
Tests should cover no-APIC boots, virtualized PIC, ISA IRQ devices, mask/unmask operations, spurious IRQ handling, and shutdown/reboot paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/i8259.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/ia32.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/ia32.h

## Purpose
IA32 emulation helpers and syscall/compat declarations for running 32-bit user programs on 64-bit kernels. The header is 92 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/compat.h>`; `#include <uapi/asm/sigcontext.h>`

Notable constants/macros: `#define _ASM_X86_IA32_H`; `#define STAT64_HAS_BROKEN_ST_INO 1`

Notable declarations and inline helpers: `#define _ASM_X86_IA32_H`; `struct ucontext_ia32 {`; `unsigned int uc_flags;`; `unsigned int uc_link;`; `struct sigcontext_32 uc_mcontext;`; `struct stat64 {`; `unsigned long long st_dev;`; `unsigned char __pad0[4];`; `#define STAT64_HAS_BROKEN_ST_INO 1`; `unsigned int __st_ino;`; `unsigned int st_mode;`; `unsigned int st_nlink;`; `unsigned int st_uid;`; `unsigned int st_gid;`; `unsigned long long st_rdev;`; `unsigned char __pad3[4];`; `unsigned int st_blksize;`; `unsigned st_atime;`; `unsigned st_atime_nsec;`; `unsigned st_mtime;`; `unsigned st_mtime_nsec;`; `unsigned st_ctime;`; `unsigned st_ctime_nsec;`; `unsigned long long st_ino;`

## Control Flow
Compat entry code routes int80/syscall/sysenter and signal/personality handling through declared helpers and IA32-specific structures.

## State and Persistence
State is compat task thread state, pt_regs interpretation, syscall tables, and signal frame data handled elsewhere.

## Dependencies and Integration Points
Depends on CONFIG_IA32_EMULATION, compat types, ptrace/user ABI, vdso/vsyscall, and entry_64 compat paths.

## Risks
Risks include ABI regressions, wrong register truncation/sign extension, and missing compat syscall or signal behavior.

## Test Signals
Tests should run 32-bit userspace, int80/sysenter/syscall paths, ptrace, signals, seccomp/audit, and x32/ia32 boundary cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/ia32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/ibt.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/ibt.h

## Purpose
Indirect Branch Tracking support helpers for ENDBR instruction bytes, validation, sealing, and objtool/runtime integration. The header is 117 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/types.h>`

Notable constants/macros: `#define _ASM_X86_IBT_H`; `#define HAS_KERNEL_IBT 1`; `#define ASM_ENDBR "endbr64\n\t"`; `#define ASM_ENDBR "endbr32\n\t"`; `#define __noendbr __attribute__((nocf_check))`; `#define IBT_NOSEAL(fname) \`; `#define ENDBR endbr64`; `#define ENDBR endbr32`; `#define HAS_KERNEL_IBT 0`; `#define ASM_ENDBR`; `#define IBT_NOSEAL(name)`; `#define __noendbr`; `#define ENDBR`; `#define ENDBR_INSN_SIZE (4*HAS_KERNEL_IBT)`

Notable declarations and inline helpers: `#define _ASM_X86_IBT_H`; `#define HAS_KERNEL_IBT 1`; `#define ASM_ENDBR "endbr64\n\t"`; `#define ASM_ENDBR "endbr32\n\t"`; `#define __noendbr __attribute__((nocf_check))`; `#define IBT_NOSEAL(fname) \`; `static __always_inline __attribute_const__ u32 gen_endbr(void)`; `u32 endbr;`; `static __always_inline __attribute_const__ u32 gen_endbr_poison(void)`; `static inline bool __is_endbr(u32 val)`; `extern __noendbr bool is_endbr(u32 *val);`; `extern __noendbr u64 ibt_save(bool disable);`; `extern __noendbr void ibt_restore(u64 save);`; `#define ENDBR endbr64`; `#define ENDBR endbr32`; `#define HAS_KERNEL_IBT 0`; `#define ASM_ENDBR`; `#define IBT_NOSEAL(name)`; `#define __noendbr`; `static inline bool is_endbr(u32 *val) { return false; }`; `static inline u64 ibt_save(bool disable) { return 0; }`; `static inline void ibt_restore(u64 save) { }`; `#define ENDBR`; `#define ENDBR_INSN_SIZE (4*HAS_KERNEL_IBT)`

## Control Flow
Helpers detect ENDBR at function entries, let ftrace adjust symbol addresses, and provide macros or stubs depending on CET/IBT config.

## State and Persistence
State is code text contents and metadata used for sealing or validation; no mutable state is stored in the header.

## Dependencies and Integration Points
Depends on CET config, objtool, alternatives/text patching, ftrace, module loading, and compiler-generated ENDBR.

## Risks
Risks include misidentifying function entry addresses, breaking tracing/kprobes on ENDBR-prefixed functions, and weak coverage on non-IBT builds.

## Test Signals
Tests should boot IBT-enabled kernels, load modules, run ftrace/kprobes/livepatch, validate objtool warnings, and ensure non-IBT stubs compile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/ibt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/idtentry.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/idtentry.h

## Purpose
Central x86 interrupt/exception entry declaration framework for C handlers, assembly stubs, FRED dispatch, system vectors, IST/NMI/MCE/VC special cases, and common IRQ stubs. The header is 781 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/trapnr.h>`; `#include <linux/entry-common.h>`; `#include <linux/hardirq.h>`; `#include <asm/irq_stack.h>`

Notable constants/macros: `#define _ASM_X86_IDTENTRY_H`; `#define IDT_ALIGN (8 * (1 + HAS_KERNEL_IBT))`; `#define DECLARE_IDTENTRY(vector, func) \`; `#define DEFINE_IDTENTRY(func) \`; `#define DECLARE_IDTENTRY_SW DECLARE_IDTENTRY`; `#define DEFINE_IDTENTRY_SW DEFINE_IDTENTRY`; `#define DECLARE_IDTENTRY_ERRORCODE(vector, func) \`; `#define DEFINE_IDTENTRY_ERRORCODE(func) \`; `#define DECLARE_IDTENTRY_RAW(vector, func) \`; `#define DEFINE_IDTENTRY_RAW(func) \`; `#define DEFINE_FREDENTRY_RAW(func) \`; `#define DECLARE_IDTENTRY_RAW_ERRORCODE(vector, func) \`; `#define DEFINE_IDTENTRY_RAW_ERRORCODE(func) \`; `#define DECLARE_IDTENTRY_IRQ(vector, func) \`; `#define DEFINE_IDTENTRY_IRQ(func) \`; `#define DECLARE_IDTENTRY_SYSVEC(vector, func) \`; `#define DEFINE_IDTENTRY_SYSVEC(func) \`; `#define DEFINE_IDTENTRY_SYSVEC_SIMPLE(func) \`

Notable declarations and inline helpers: `#define _ASM_X86_IDTENTRY_H`; `#define IDT_ALIGN (8 * (1 + HAS_KERNEL_IBT))`; `typedef void (*idtentry_t)(struct pt_regs *regs);`; `#define DECLARE_IDTENTRY(vector, func) \`; `asmlinkage void asm_##func(void); \`; `asmlinkage void xen_asm_##func(void); \`; `void fred_##func(struct pt_regs *regs); \`; `#define DEFINE_IDTENTRY(func) \`; `static __always_inline void __##func(struct pt_regs *regs); \`; `static __always_inline void __##func(struct pt_regs *regs)`; `#define DECLARE_IDTENTRY_SW DECLARE_IDTENTRY`; `#define DEFINE_IDTENTRY_SW DEFINE_IDTENTRY`; `#define DECLARE_IDTENTRY_ERRORCODE(vector, func) \`; `#define DEFINE_IDTENTRY_ERRORCODE(func) \`; `static __always_inline void __##func(struct pt_regs *regs, \`; `unsigned long error_code); \`; `unsigned long error_code) \`; `unsigned long error_code)`; `#define DECLARE_IDTENTRY_RAW(vector, func) \`; `#define DEFINE_IDTENTRY_RAW(func) \`; `#define DEFINE_FREDENTRY_RAW(func) \`; `#define DECLARE_IDTENTRY_RAW_ERRORCODE(vector, func) \`; `#define DEFINE_IDTENTRY_RAW_ERRORCODE(func) \`; `#define DECLARE_IDTENTRY_IRQ(vector, func) \`

## Control Flow
DECLARE_* macros emit either C prototypes or assembly stubs; DEFINE_* wrappers run irqentry_enter/exit, instrumentation windows, IRQ-stack switching, L1D flush marking, and raw special-case handlers.

## State and Persistence
State is mostly entry-stack/register state plus IDT/FRED installed function pointers; generated stubs form part of the binary ABI between assembly and C.

## Dependencies and Integration Points
Depends on trap numbers, irq_stack.h, entry-common, hardirq, APIC vectors, KVM, Xen, TDX, SEV-ES #VC, FRED, IBT alignment, and assembler macro support.

## Risks
Risks are high: wrong macro variant can enable instrumentation too early, skip irq accounting, mishandle error codes, break IST/NMI safety, or desynchronize C and assembly symbols.

## Test Signals
Tests should cover every exception vector, common/spurious IRQs, system IPIs, NMI/MCE/#DB/#DF/#VC/#VE, Xen/KVM/Hyper-V variants, FRED and non-FRED boots, objtool noinstr validation, and tracing entry symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/idtentry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/imr.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/imr.h

## Purpose
Intel Isolated Memory Region declarations for firmware/platform memory protection windows. The header is 56 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/types.h>`

Notable constants/macros: `#define _IMR_H`; `#define IMR_ESRAM_FLUSH BIT(31)`; `#define IMR_CPU_SNOOP BIT(30) /* Applicable only to write */`; `#define IMR_RMU BIT(29)`; `#define IMR_VC1_SAI_ID3 BIT(15)`; `#define IMR_VC1_SAI_ID2 BIT(14)`; `#define IMR_VC1_SAI_ID1 BIT(13)`; `#define IMR_VC1_SAI_ID0 BIT(12)`; `#define IMR_VC0_SAI_ID3 BIT(11)`; `#define IMR_VC0_SAI_ID2 BIT(10)`; `#define IMR_VC0_SAI_ID1 BIT(9)`; `#define IMR_VC0_SAI_ID0 BIT(8)`; `#define IMR_CPU_0 BIT(1) /* SMM mode */`; `#define IMR_CPU BIT(0) /* Non SMM mode */`; `#define IMR_ACCESS_NONE 0`; `#define IMR_READ_ACCESS_ALL 0xBFFFFFFF`; `#define IMR_WRITE_ACCESS_ALL 0xFFFFFFFF`; `#define QUARK_X1000_IMR_MAX 0x08`

Notable declarations and inline helpers: `#define _IMR_H`; `#define IMR_ESRAM_FLUSH BIT(31)`; `#define IMR_CPU_SNOOP BIT(30) /* Applicable only to write */`; `#define IMR_RMU BIT(29)`; `#define IMR_VC1_SAI_ID3 BIT(15)`; `#define IMR_VC1_SAI_ID2 BIT(14)`; `#define IMR_VC1_SAI_ID1 BIT(13)`; `#define IMR_VC1_SAI_ID0 BIT(12)`; `#define IMR_VC0_SAI_ID3 BIT(11)`; `#define IMR_VC0_SAI_ID2 BIT(10)`; `#define IMR_VC0_SAI_ID1 BIT(9)`; `#define IMR_VC0_SAI_ID0 BIT(8)`; `#define IMR_CPU_0 BIT(1) /* SMM mode */`; `#define IMR_CPU BIT(0) /* Non SMM mode */`; `#define IMR_ACCESS_NONE 0`; `#define IMR_READ_ACCESS_ALL 0xBFFFFFFF`; `#define IMR_WRITE_ACCESS_ALL 0xFFFFFFFF`; `#define QUARK_X1000_IMR_MAX 0x08`; `#define QUARK_X1000_IMR_REGBASE 0x40`; `#define IMR_ALIGN 0x400`; `#define IMR_MASK (IMR_ALIGN - 1)`; `int imr_add_range(phys_addr_t base, size_t size,`; `unsigned int rmask, unsigned int wmask);`; `int imr_remove_range(phys_addr_t base, size_t size);`

## Control Flow
The IMR implementation initializes region descriptors and programs hardware registers to protect selected physical memory ranges.

## State and Persistence
State is hardware IMR register configuration and any tracked reserved regions in implementation files.

## Dependencies and Integration Points
Depends on Intel platform support, resource reservations, firmware memory maps, and low-level MMIO/MSR access.

## Risks
Risks include overlapping protected ranges, locking out legitimate kernel/device access, and platform-specific register semantics.

## Test Signals
Tests should run on IMR-capable platforms, validate reserved/protected ranges, boot memory map interactions, and disabled-feature builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/imr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/inat.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/inat.h

## Purpose
Instruction attribute table interface used by the x86 instruction decoder to classify prefixes, opcodes, ModRM, immediates, and escape maps. The header is 266 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/inat_types.h> /* __ignore_sync_check__ */`

Notable constants/macros: `#define _ASM_X86_INAT_H`; `#define INAT_OPCODE_TABLE_SIZE 256`; `#define INAT_GROUP_TABLE_SIZE 8`; `#define INAT_PFX_OPNDSZ 1 /* 0x66 */ /* LPFX1 */`; `#define INAT_PFX_REPE 2 /* 0xF3 */ /* LPFX2 */`; `#define INAT_PFX_REPNE 3 /* 0xF2 */ /* LPFX3 */`; `#define INAT_PFX_LOCK 4 /* 0xF0 */`; `#define INAT_PFX_CS 5 /* 0x2E */`; `#define INAT_PFX_DS 6 /* 0x3E */`; `#define INAT_PFX_ES 7 /* 0x26 */`; `#define INAT_PFX_FS 8 /* 0x64 */`; `#define INAT_PFX_GS 9 /* 0x65 */`; `#define INAT_PFX_SS 10 /* 0x36 */`; `#define INAT_PFX_ADDRSZ 11 /* 0x67 */`; `#define INAT_PFX_REX 12 /* 0x4X */`; `#define INAT_PFX_VEX2 13 /* 2-bytes VEX prefix */`; `#define INAT_PFX_VEX3 14 /* 3-bytes VEX prefix */`; `#define INAT_PFX_EVEX 15 /* EVEX prefix */`

Notable declarations and inline helpers: `#define _ASM_X86_INAT_H`; `#define INAT_OPCODE_TABLE_SIZE 256`; `#define INAT_GROUP_TABLE_SIZE 8`; `#define INAT_PFX_OPNDSZ 1 /* 0x66 */ /* LPFX1 */`; `#define INAT_PFX_REPE 2 /* 0xF3 */ /* LPFX2 */`; `#define INAT_PFX_REPNE 3 /* 0xF2 */ /* LPFX3 */`; `#define INAT_PFX_LOCK 4 /* 0xF0 */`; `#define INAT_PFX_CS 5 /* 0x2E */`; `#define INAT_PFX_DS 6 /* 0x3E */`; `#define INAT_PFX_ES 7 /* 0x26 */`; `#define INAT_PFX_FS 8 /* 0x64 */`; `#define INAT_PFX_GS 9 /* 0x65 */`; `#define INAT_PFX_SS 10 /* 0x36 */`; `#define INAT_PFX_ADDRSZ 11 /* 0x67 */`; `#define INAT_PFX_REX 12 /* 0x4X */`; `#define INAT_PFX_VEX2 13 /* 2-bytes VEX prefix */`; `#define INAT_PFX_VEX3 14 /* 3-bytes VEX prefix */`; `#define INAT_PFX_EVEX 15 /* EVEX prefix */`; `#define INAT_PFX_REX2 16 /* 0xD5 */`; `#define INAT_PFX_XOP 17 /* 0x8F */`; `#define INAT_LSTPFX_MAX 3`; `#define INAT_LGCPFX_MAX 11`; `#define INAT_IMM_BYTE 1`; `#define INAT_IMM_WORD 2`

## Control Flow
Decoder code queries inat_get_* helpers to progress from prefixes to opcode attributes, group attributes, AVX/XOP/EVEX maps, and immediate/displacement sizing.

## State and Persistence
State is generated read-only inat tables and compact bitfields; the header itself only defines accessors and bit tests.

## Dependencies and Integration Points
Depends on inat_types.h, generated opcode attribute tables, insn.h, kprobes, uprobes, alternatives, and instruction emulation users.

## Risks
Risks include generated-table mismatch with decoder macros, incomplete new opcode coverage, and wrong group handling producing unsafe instruction lengths.

## Test Signals
Tests should run insn decoder selftests, kprobe/uprobes decode cases, alternatives patching, AVX/EVEX/APX opcodes, and malformed-byte fuzzing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/inat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/inat_types.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/inat_types.h

## Purpose
Primitive integer typedefs for instruction attribute and byte/value fields shared by inat and insn decoder headers. The header is 15 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: None visible in this header.

Notable constants/macros: `#define _ASM_X86_INAT_TYPES_H`

Notable declarations and inline helpers: `#define _ASM_X86_INAT_TYPES_H`; `typedef unsigned int insn_attr_t;`; `typedef unsigned char insn_byte_t;`; `typedef signed int insn_value_t;`

## Control Flow
No control flow; it fixes the width of insn_attr_t, insn_byte_t, and insn_value_t.

## State and Persistence
State is absent; ABI is compile-time type size and signedness.

## Dependencies and Integration Points
Depends on linux/types.h and consumers in inat.h and insn.h.

## Risks
Risks are type-width changes breaking generated tables or instruction field packing.

## Test Signals
Test signal is build coverage and decoder selftests across 32-bit and 64-bit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/inat_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/init.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/init.h

## Purpose
x86 init-section annotations and architecture initialization declarations. The header is 20 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: None visible in this header.

Notable constants/macros: `#define _ASM_X86_INIT_H`

Notable declarations and inline helpers: `#define _ASM_X86_INIT_H`; `struct x86_mapping_info {`; `void *(*alloc_pgt_page)(void *); /* allocate buf for page table */`; `void (*free_pgt_page)(void *, void *); /* free buf for page table */`; `void *context; /* context for alloc_pgt_page */`; `unsigned long page_flag; /* page flag for PMD or PUD entry */`; `unsigned long offset; /* ident mapping offset */`; `bool direct_gbpages; /* PUD level 1GB page support */`; `unsigned long kernpg_flag; /* kernel pagetable flag override */`; `int kernel_ident_mapping_init(struct x86_mapping_info *info, pgd_t *pgd_page,`; `unsigned long pstart, unsigned long pend);`; `void kernel_ident_mapping_free(struct x86_mapping_info *info, pgd_t *pgd);`

## Control Flow
No complex control flow; macros/declarations mark code or data for init-time lifetime and expose architecture init hooks.

## State and Persistence
State is boot-only code/data that may be freed after init; callers must not retain pointers after init memory release.

## Dependencies and Integration Points
Depends on linux/init.h conventions and x86 boot/setup code.

## Risks
Risks include marking runtime-needed code as __init or missing __init annotations that waste memory.

## Test Signals
Tests should include section mismatch builds, boot smoke tests, CPU hotplug after init, and module/linker warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/insn-eval.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/insn-eval.h

## Purpose
Instruction evaluation helpers for fault/emulation paths that need effective addresses, segment bases, register pointers, and instruction-relative calculations. The header is 49 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/compiler.h>`; `#include <linux/bug.h>`; `#include <linux/err.h>`; `#include <asm/ptrace.h>`

Notable constants/macros: `#define _ASM_X86_INSN_EVAL_H`; `#define INSN_CODE_SEG_ADDR_SZ(params) ((params >> 4) & 0xf)`; `#define INSN_CODE_SEG_OPND_SZ(params) (params & 0xf)`; `#define INSN_CODE_SEG_PARAMS(oper_sz, addr_sz) (oper_sz | (addr_sz << 4))`

Notable declarations and inline helpers: `#define _ASM_X86_INSN_EVAL_H`; `#define INSN_CODE_SEG_ADDR_SZ(params) ((params >> 4) & 0xf)`; `#define INSN_CODE_SEG_OPND_SZ(params) (params & 0xf)`; `#define INSN_CODE_SEG_PARAMS(oper_sz, addr_sz) (oper_sz | (addr_sz << 4))`; `int pt_regs_offset(struct pt_regs *regs, int regno);`; `bool insn_has_rep_prefix(struct insn *insn);`; `void __user *insn_get_addr_ref(struct insn *insn, struct pt_regs *regs);`; `int insn_get_modrm_rm_off(struct insn *insn, struct pt_regs *regs);`; `int insn_get_modrm_reg_off(struct insn *insn, struct pt_regs *regs);`; `unsigned long *insn_get_modrm_reg_ptr(struct insn *insn, struct pt_regs *regs);`; `unsigned long insn_get_seg_base(struct pt_regs *regs, int seg_reg_idx);`; `int insn_get_code_seg_params(struct pt_regs *regs);`; `int insn_get_effective_ip(struct pt_regs *regs, unsigned long *ip);`; `int insn_fetch_from_user(struct pt_regs *regs,`; `unsigned char buf[MAX_INSN_SIZE]);`; `int insn_fetch_from_user_inatomic(struct pt_regs *regs,`; `bool insn_decode_from_regs(struct insn *insn, struct pt_regs *regs,`; `unsigned char buf[MAX_INSN_SIZE], int buf_size);`; `enum insn_mmio_type {`; `enum insn_mmio_type insn_decode_mmio(struct insn *insn, int *bytes);`; `bool insn_is_nop(struct insn *insn);`

## Control Flow
Exception handlers decode an instruction, resolve ModRM/SIB/displacement and segment context, then compute memory references or register operands for fixups/emulation.

## State and Persistence
State is transient pt_regs plus decoded insn data; no persistent storage is defined here.

## Dependencies and Integration Points
Depends on insn.h, ptrace registers, segment/FSGS state, uaccess-safe memory probing, and exception/fixup users such as UMIP or SEV-ES.

## Risks
Risks include wrong address-size/sign-extension rules, segment-base mistakes, and unsafe register pointer mapping in fault contexts.

## Test Signals
Tests should cover effective-address decoding for ModRM/SIB/RIP-relative forms, 32/64-bit modes, segment overrides, user/kernel regs, and malformed instructions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/insn-eval.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/insn.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/insn.h

## Purpose
Core x86 instruction decoder data structures and APIs for incremental decoding of prefixes, REX/REX2, VEX/XOP/EVEX, opcode, ModRM/SIB, displacement, immediates, and length. The header is 344 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/byteorder.h>`; `#include <asm/inat.h> /* __ignore_sync_check__ */`

Notable constants/macros: `#define _ASM_X86_INSN_H`; `#define MAX_INSN_SIZE 15`; `#define X86_MODRM_MOD(modrm) (((modrm) & 0xc0) >> 6)`; `#define X86_MODRM_REG(modrm) (((modrm) & 0x38) >> 3)`; `#define X86_MODRM_RM(modrm) ((modrm) & 0x07)`; `#define X86_SIB_SCALE(sib) (((sib) & 0xc0) >> 6)`; `#define X86_SIB_INDEX(sib) (((sib) & 0x38) >> 3)`; `#define X86_SIB_BASE(sib) ((sib) & 0x07)`; `#define X86_REX2_M(rex) ((rex) & 0x80) /* REX2 M0 */`; `#define X86_REX2_R(rex) ((rex) & 0x40) /* REX2 R4 */`; `#define X86_REX2_X(rex) ((rex) & 0x20) /* REX2 X4 */`; `#define X86_REX2_B(rex) ((rex) & 0x10) /* REX2 B4 */`; `#define X86_REX_W(rex) ((rex) & 8) /* REX or REX2 W */`; `#define X86_REX_R(rex) ((rex) & 4) /* REX or REX2 R3 */`; `#define X86_REX_X(rex) ((rex) & 2) /* REX or REX2 X3 */`; `#define X86_REX_B(rex) ((rex) & 1) /* REX or REX2 B3 */`; `#define X86_VEX_W(vex) ((vex) & 0x80) /* VEX3 Byte2 */`; `#define X86_VEX_R(vex) ((vex) & 0x80) /* VEX2/3 Byte1 */`

Notable declarations and inline helpers: `#define _ASM_X86_INSN_H`; `struct insn_field {`; `union {`; `unsigned char got;`; `unsigned char nbytes;`; `static inline void insn_field_set(struct insn_field *p, insn_value_t v,`; `unsigned char n)`; `static inline void insn_set_byte(struct insn_field *p, unsigned char n,`; `struct insn {`; `struct insn_field prefixes; /*`; `struct insn_field rex_prefix; /* REX prefix */`; `struct insn_field vex_prefix; /* VEX prefix */`; `struct insn_field xop_prefix; /* XOP prefix */`; `struct insn_field opcode; /*`; `struct insn_field modrm;`; `struct insn_field sib;`; `struct insn_field displacement;`; `struct insn_field immediate;`; `struct insn_field moffset1; /* for 64bit MOV */`; `struct insn_field immediate1; /* for 64bit imm or off16/32 */`; `struct insn_field moffset2; /* for 64bit MOV */`; `struct insn_field immediate2; /* for 64bit imm or seg16 */`; `int emulate_prefix_size;`; `unsigned char opnd_bytes;`

## Control Flow
Callers initialize struct insn with a byte buffer, lazily request fields, and the decoder advances next_byte until length/attributes are known; helper accessors expose prefix-map bits and addressing flags.

## State and Persistence
State is per-decode struct insn and read-only inat tables; no global persistence.

## Dependencies and Integration Points
Depends on byte order, inat.h generated attributes, MAX_INSN_SIZE rules, and kernel/32/64-bit decode mode selection.

## Risks
Risks include length miscalculation, endian handling errors, new opcode prefix gaps, and unsafe consumers trusting partially decoded fields.

## Test Signals
Tests should include decoder selftests, random-byte fuzzing, EVEX/VEX/XOP/REX2/APX cases, RIP-relative detection, and kprobe/alternative patch users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/insn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/inst.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/inst.h

## Purpose
Assembly instruction encoding macros for emitting x86 opcodes that assemblers may not understand or that need mode-dependent forms. The header is 148 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: None visible in this header.

Notable constants/macros: `#define X86_ASM_INST_H`; `#define REG_NUM_INVALID 100`; `#define REG_TYPE_R32 0`; `#define REG_TYPE_R64 1`; `#define REG_TYPE_INVALID 100`

Notable declarations and inline helpers: `#define X86_ASM_INST_H`; `#define REG_NUM_INVALID 100`; `#define REG_TYPE_R32 0`; `#define REG_TYPE_R64 1`; `#define REG_TYPE_INVALID 100`

## Control Flow
Control flow is compile-time: macros select byte sequences or instruction mnemonics for alternatives, barriers, and feature-specific assembly.

## State and Persistence
State is absent except emitted text bytes in the kernel image.

## Dependencies and Integration Points
Depends on asm.h, assembler capability, CPU feature code, and low-level entry/alternative assembly users.

## Risks
Risks include wrong byte encodings, assembler-version mismatches, and incompatibility with objtool/unwind expectations.

## Test Signals
Tests should include assembler builds with supported binutils versions, objdump byte verification, objtool validation, and boot on CPUs using the emitted instructions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/inst.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/intel-family.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/intel-family.h

## Purpose
Intel CPU family/model ID catalog used by feature quirks, drivers, mitigations, and platform matching. The header is 227 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: None visible in this header.

Notable constants/macros: `#define _ASM_X86_INTEL_FAMILY_H`; `#define IFM(_fam, _model) VFM_MAKE(X86_VENDOR_INTEL, _fam, _model)`; `#define INTEL_ANY IFM(X86_FAMILY_ANY, X86_MODEL_ANY)`; `#define INTEL_FAM5_START IFM(5, 0x00) /* Notational marker, also P5 A-step */`; `#define INTEL_PENTIUM_75 IFM(5, 0x02) /* P54C */`; `#define INTEL_PENTIUM_MMX IFM(5, 0x04) /* P55C */`; `#define INTEL_QUARK_X1000 IFM(5, 0x09) /* Quark X1000 SoC */`; `#define INTEL_PENTIUM_PRO IFM(6, 0x01)`; `#define INTEL_PENTIUM_II_KLAMATH IFM(6, 0x03)`; `#define INTEL_PENTIUM_III_DESCHUTES IFM(6, 0x05)`; `#define INTEL_PENTIUM_III_TUALATIN IFM(6, 0x0B)`; `#define INTEL_PENTIUM_M_DOTHAN IFM(6, 0x0D)`; `#define INTEL_CORE_YONAH IFM(6, 0x0E)`; `#define INTEL_CORE2_MEROM IFM(6, 0x0F)`; `#define INTEL_CORE2_MEROM_L IFM(6, 0x16)`; `#define INTEL_CORE2_PENRYN IFM(6, 0x17)`; `#define INTEL_CORE2_DUNNINGTON IFM(6, 0x1D)`; `#define INTEL_NEHALEM IFM(6, 0x1E)`

Notable declarations and inline helpers: `#define _ASM_X86_INTEL_FAMILY_H`; `#define IFM(_fam, _model) VFM_MAKE(X86_VENDOR_INTEL, _fam, _model)`; `#define INTEL_ANY IFM(X86_FAMILY_ANY, X86_MODEL_ANY)`; `#define INTEL_FAM5_START IFM(5, 0x00) /* Notational marker, also P5 A-step */`; `#define INTEL_PENTIUM_75 IFM(5, 0x02) /* P54C */`; `#define INTEL_PENTIUM_MMX IFM(5, 0x04) /* P55C */`; `#define INTEL_QUARK_X1000 IFM(5, 0x09) /* Quark X1000 SoC */`; `#define INTEL_PENTIUM_PRO IFM(6, 0x01)`; `#define INTEL_PENTIUM_II_KLAMATH IFM(6, 0x03)`; `#define INTEL_PENTIUM_III_DESCHUTES IFM(6, 0x05)`; `#define INTEL_PENTIUM_III_TUALATIN IFM(6, 0x0B)`; `#define INTEL_PENTIUM_M_DOTHAN IFM(6, 0x0D)`; `#define INTEL_CORE_YONAH IFM(6, 0x0E)`; `#define INTEL_CORE2_MEROM IFM(6, 0x0F)`; `#define INTEL_CORE2_MEROM_L IFM(6, 0x16)`; `#define INTEL_CORE2_PENRYN IFM(6, 0x17)`; `#define INTEL_CORE2_DUNNINGTON IFM(6, 0x1D)`; `#define INTEL_NEHALEM IFM(6, 0x1E)`; `#define INTEL_NEHALEM_G IFM(6, 0x1F) /* Auburndale / Havendale */`; `#define INTEL_NEHALEM_EP IFM(6, 0x1A)`; `#define INTEL_NEHALEM_EX IFM(6, 0x2E)`; `#define INTEL_WESTMERE IFM(6, 0x25)`; `#define INTEL_WESTMERE_EP IFM(6, 0x2C)`; `#define INTEL_WESTMERE_EX IFM(6, 0x2F)`

## Control Flow
No runtime flow; constants encode CPUID family/model values for processors from legacy Core/Atom through modern server/client families.

## State and Persistence
State is absent; the header is a shared numeric ABI for CPUID matching.

## Dependencies and Integration Points
Depends on CPUID decoding users throughout arch/x86, drivers, perf, power, and security mitigation code.

## Risks
Risks include duplicate/wrong model numbers, missing aliases for steppings, and downstream quirks silently not applying.

## Test Signals
Tests should include compile coverage, CPUID matching on affected hardware, quirk unit checks where available, and review against Intel CPUID documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/intel-family.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/intel-mid.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/intel-mid.h

## Purpose
Intel MID platform helper declarations for legacy mobile/SoC detection and platform initialization. The header is 23 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/pci.h>`

Notable constants/macros: `#define _ASM_X86_INTEL_MID_H`; `#define INTEL_MID_PWR_LSS_OFFSET 4`; `#define INTEL_MID_PWR_LSS_TYPE (1 << 7)`

Notable declarations and inline helpers: `#define _ASM_X86_INTEL_MID_H`; `extern int intel_mid_pci_init(void);`; `extern int intel_mid_pci_set_power_state(struct pci_dev *pdev, pci_power_t state);`; `extern pci_power_t intel_mid_pci_get_power_state(struct pci_dev *pdev);`; `extern void intel_mid_pwr_power_off(void);`; `#define INTEL_MID_PWR_LSS_OFFSET 4`; `#define INTEL_MID_PWR_LSS_TYPE (1 << 7)`; `extern int intel_mid_pwr_get_lss_id(struct pci_dev *pdev);`

## Control Flow
Boot/platform code uses these declarations to detect MID variants and install SoC-specific callbacks or device setup.

## State and Persistence
State is global platform type/callback data in implementation files, not this header.

## Dependencies and Integration Points
Depends on x86 platform init, device enumeration, and legacy Intel MID support code.

## Risks
Risks include stale platform IDs, wrong init ordering, and bitrot due to rare hardware.

## Test Signals
Tests should compile MID configs and boot available MID/SoC hardware or emulation for platform detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/intel-mid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/intel_ds.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/intel_ds.h

## Purpose
Intel Debug Store/PEBS/BTS structure declarations for perf and low-level CPU tracing support. The header is 47 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/percpu-defs.h>`

Notable constants/macros: `#define _ASM_INTEL_DS_H`; `#define BTS_BUFFER_SIZE (PAGE_SIZE << 4)`; `#define PEBS_BUFFER_SHIFT 4`; `#define PEBS_BUFFER_SIZE (PAGE_SIZE << PEBS_BUFFER_SHIFT)`; `#define ARCH_PEBS_THRESH_MULTI ((PEBS_BUFFER_SIZE - PAGE_SIZE) >> PEBS_BUFFER_SHIFT)`; `#define ARCH_PEBS_THRESH_SINGLE 1`; `#define MAX_PEBS_EVENTS_FMT4 8`; `#define MAX_PEBS_EVENTS 32`; `#define MAX_PEBS_EVENTS_MASK GENMASK_ULL(MAX_PEBS_EVENTS - 1, 0)`; `#define MAX_FIXED_PEBS_EVENTS 16`

Notable declarations and inline helpers: `#define _ASM_INTEL_DS_H`; `#define BTS_BUFFER_SIZE (PAGE_SIZE << 4)`; `#define PEBS_BUFFER_SHIFT 4`; `#define PEBS_BUFFER_SIZE (PAGE_SIZE << PEBS_BUFFER_SHIFT)`; `#define ARCH_PEBS_THRESH_MULTI ((PEBS_BUFFER_SIZE - PAGE_SIZE) >> PEBS_BUFFER_SHIFT)`; `#define ARCH_PEBS_THRESH_SINGLE 1`; `#define MAX_PEBS_EVENTS_FMT4 8`; `#define MAX_PEBS_EVENTS 32`; `#define MAX_PEBS_EVENTS_MASK GENMASK_ULL(MAX_PEBS_EVENTS - 1, 0)`; `#define MAX_FIXED_PEBS_EVENTS 16`; `struct debug_store {`; `u64 bts_buffer_base;`; `u64 bts_index;`; `u64 bts_absolute_maximum;`; `u64 bts_interrupt_threshold;`; `u64 pebs_buffer_base;`; `u64 pebs_index;`; `u64 pebs_absolute_maximum;`; `u64 pebs_interrupt_threshold;`; `u64 pebs_event_reset[MAX_PEBS_EVENTS + MAX_FIXED_PEBS_EVENTS];`; `struct debug_store_buffers {`

## Control Flow
Perf configures DS buffers and CPU debug-store MSRs using these layouts to collect branch trace or precise event records.

## State and Persistence
State lives in per-CPU DS buffer memory and debug-store MSRs; records persist only until perf consumes or overwrites them.

## Dependencies and Integration Points
Depends on perf_event, Intel PMU, MSR access, CPU model quirks, and context-switch/debug handling.

## Risks
Risks include record layout mismatch, buffer overflow accounting, and CPU-model differences in PEBS/branch formats.

## Test Signals
Tests should run perf record with PEBS/BTS where supported, context-switch stress, NMI sampling, and CPU model matrix validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/intel_ds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/intel_pt.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/intel_pt.h

## Purpose
Intel Processor Trace helper declarations and MSR/format constants for perf PT integration. The header is 41 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: None visible in this header.

Notable constants/macros: `#define _ASM_X86_INTEL_PT_H`; `#define PT_CPUID_LEAVES 2`; `#define PT_CPUID_REGS_NUM 4 /* number of registers (eax, ebx, ecx, edx) */`

Notable declarations and inline helpers: `#define _ASM_X86_INTEL_PT_H`; `#define PT_CPUID_LEAVES 2`; `#define PT_CPUID_REGS_NUM 4 /* number of registers (eax, ebx, ecx, edx) */`; `enum pt_capabilities {`; `void cpu_emergency_stop_pt(void);`; `extern u32 intel_pt_validate_hw_cap(enum pt_capabilities cap);`; `extern u32 intel_pt_validate_cap(u32 *caps, enum pt_capabilities cap);`; `extern int is_intel_pt_event(struct perf_event *event);`; `static inline void cpu_emergency_stop_pt(void) {}`; `static inline u32 intel_pt_validate_hw_cap(enum pt_capabilities cap) { return 0; }`; `static inline u32 intel_pt_validate_cap(u32 *caps, enum pt_capabilities capability) { return 0; }`; `static inline int is_intel_pt_event(struct perf_event *event) { return 0; }`

## Control Flow
Perf PT code configures trace address ranges, output buffers, and MSRs based on these constants and CPU capabilities.

## State and Persistence
State is PT MSR configuration plus perf AUX buffer state managed by Intel PT implementation.

## Dependencies and Integration Points
Depends on perf AUX infrastructure, Intel PMU, CPUID feature detection, MSRs, and virtualization restrictions.

## Risks
Risks include invalid MSR programming, trace packet format drift, and AUX buffer synchronization bugs.

## Test Signals
Tests should run perf intel_pt traces, snapshot/full modes, CPU hotplug, virtualization constraints, and unsupported CPU fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/intel_pt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/intel_punit_ipc.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/intel_punit_ipc.h

## Purpose
Intel P-unit IPC interface declarations for SoC power/clock/thermal register messaging. The header is 95 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: None visible in this header.

Notable constants/macros: `#define _ASM_X86_INTEL_PUNIT_IPC_H_`; `#define IPC_TYPE_OFFSET 6`; `#define IPC_PUNIT_BIOS_CMD_BASE (BIOS_IPC << IPC_TYPE_OFFSET)`; `#define IPC_PUNIT_GTD_CMD_BASE (GTDDRIVER_IPC << IPC_TYPE_OFFSET)`; `#define IPC_PUNIT_ISPD_CMD_BASE (ISPDRIVER_IPC << IPC_TYPE_OFFSET)`; `#define IPC_PUNIT_CMD_TYPE_MASK (RESERVED_IPC << IPC_TYPE_OFFSET)`; `#define IPC_PUNIT_BIOS_ZERO (IPC_PUNIT_BIOS_CMD_BASE | 0x00)`; `#define IPC_PUNIT_BIOS_VR_INTERFACE (IPC_PUNIT_BIOS_CMD_BASE | 0x01)`; `#define IPC_PUNIT_BIOS_READ_PCS (IPC_PUNIT_BIOS_CMD_BASE | 0x02)`; `#define IPC_PUNIT_BIOS_WRITE_PCS (IPC_PUNIT_BIOS_CMD_BASE | 0x03)`; `#define IPC_PUNIT_BIOS_READ_PCU_CONFIG (IPC_PUNIT_BIOS_CMD_BASE | 0x04)`; `#define IPC_PUNIT_BIOS_WRITE_PCU_CONFIG (IPC_PUNIT_BIOS_CMD_BASE | 0x05)`; `#define IPC_PUNIT_BIOS_READ_PL1_SETTING (IPC_PUNIT_BIOS_CMD_BASE | 0x06)`; `#define IPC_PUNIT_BIOS_WRITE_PL1_SETTING (IPC_PUNIT_BIOS_CMD_BASE | 0x07)`; `#define IPC_PUNIT_BIOS_TRIGGER_VDD_RAM (IPC_PUNIT_BIOS_CMD_BASE | 0x08)`; `#define IPC_PUNIT_BIOS_READ_TELE_INFO (IPC_PUNIT_BIOS_CMD_BASE | 0x09)`; `#define IPC_PUNIT_BIOS_READ_TELE_TRACE_CTRL (IPC_PUNIT_BIOS_CMD_BASE | 0x0a)`; `#define IPC_PUNIT_BIOS_WRITE_TELE_TRACE_CTRL (IPC_PUNIT_BIOS_CMD_BASE | 0x0b)`

Notable declarations and inline helpers: `#define _ASM_X86_INTEL_PUNIT_IPC_H_`; `typedef enum {`; `#define IPC_TYPE_OFFSET 6`; `#define IPC_PUNIT_BIOS_CMD_BASE (BIOS_IPC << IPC_TYPE_OFFSET)`; `#define IPC_PUNIT_GTD_CMD_BASE (GTDDRIVER_IPC << IPC_TYPE_OFFSET)`; `#define IPC_PUNIT_ISPD_CMD_BASE (ISPDRIVER_IPC << IPC_TYPE_OFFSET)`; `#define IPC_PUNIT_CMD_TYPE_MASK (RESERVED_IPC << IPC_TYPE_OFFSET)`; `#define IPC_PUNIT_BIOS_ZERO (IPC_PUNIT_BIOS_CMD_BASE | 0x00)`; `#define IPC_PUNIT_BIOS_VR_INTERFACE (IPC_PUNIT_BIOS_CMD_BASE | 0x01)`; `#define IPC_PUNIT_BIOS_READ_PCS (IPC_PUNIT_BIOS_CMD_BASE | 0x02)`; `#define IPC_PUNIT_BIOS_WRITE_PCS (IPC_PUNIT_BIOS_CMD_BASE | 0x03)`; `#define IPC_PUNIT_BIOS_READ_PCU_CONFIG (IPC_PUNIT_BIOS_CMD_BASE | 0x04)`; `#define IPC_PUNIT_BIOS_WRITE_PCU_CONFIG (IPC_PUNIT_BIOS_CMD_BASE | 0x05)`; `#define IPC_PUNIT_BIOS_READ_PL1_SETTING (IPC_PUNIT_BIOS_CMD_BASE | 0x06)`; `#define IPC_PUNIT_BIOS_WRITE_PL1_SETTING (IPC_PUNIT_BIOS_CMD_BASE | 0x07)`; `#define IPC_PUNIT_BIOS_TRIGGER_VDD_RAM (IPC_PUNIT_BIOS_CMD_BASE | 0x08)`; `#define IPC_PUNIT_BIOS_READ_TELE_INFO (IPC_PUNIT_BIOS_CMD_BASE | 0x09)`; `#define IPC_PUNIT_BIOS_READ_TELE_TRACE_CTRL (IPC_PUNIT_BIOS_CMD_BASE | 0x0a)`; `#define IPC_PUNIT_BIOS_WRITE_TELE_TRACE_CTRL (IPC_PUNIT_BIOS_CMD_BASE | 0x0b)`; `#define IPC_PUNIT_BIOS_READ_TELE_EVENT_CTRL (IPC_PUNIT_BIOS_CMD_BASE | 0x0c)`; `#define IPC_PUNIT_BIOS_WRITE_TELE_EVENT_CTRL (IPC_PUNIT_BIOS_CMD_BASE | 0x0d)`; `#define IPC_PUNIT_BIOS_READ_TELE_TRACE (IPC_PUNIT_BIOS_CMD_BASE | 0x0e)`; `#define IPC_PUNIT_BIOS_WRITE_TELE_TRACE (IPC_PUNIT_BIOS_CMD_BASE | 0x0f)`; `#define IPC_PUNIT_BIOS_READ_TELE_EVENT (IPC_PUNIT_BIOS_CMD_BASE | 0x10)`

## Control Flow
Clients acquire the IPC path and issue read/write/command operations to P-unit firmware-controlled registers.

## State and Persistence
State is serialized through P-unit IPC hardware/mailbox and driver locks in the implementation, with no local state here.

## Dependencies and Integration Points
Depends on platform devices, IOSF/PMIC coordination, Intel SoC power drivers, and firmware mailbox semantics.

## Risks
Risks include command timeouts, lock ordering with PMIC/IOSF users, and platform register differences.

## Test Signals
Tests should cover supported SoC probe, read/write commands, timeout/error paths, concurrent clients, suspend/resume, and missing-device stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/intel_punit_ipc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/intel_telemetry.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/intel_telemetry.h

## Purpose
Intel telemetry interface declarations for SoC telemetry event/configuration access. The header is 102 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/platform_data/x86/intel_scu_ipc.h>`

Notable constants/macros: `#define INTEL_TELEMETRY_H`; `#define TELEM_MAX_EVENTS_SRAM 28`; `#define TELEM_MAX_OS_ALLOCATED_EVENTS 20`

Notable declarations and inline helpers: `#define INTEL_TELEMETRY_H`; `#define TELEM_MAX_EVENTS_SRAM 28`; `#define TELEM_MAX_OS_ALLOCATED_EVENTS 20`; `enum telemetry_unit {`; `struct telemetry_evtlog {`; `u32 telem_evtid;`; `u64 telem_evtlog;`; `struct telemetry_evtconfig {`; `u32 *evtmap;`; `u8 num_evts;`; `u8 period;`; `struct telemetry_evtmap {`; `u32 evt_id;`; `struct telemetry_unit_config {`; `struct telemetry_evtmap *telem_evts;`; `void __iomem *regmap;`; `u8 ssram_evts_used;`; `u8 curr_period;`; `u8 max_period;`; `u8 min_period;`; `struct telemetry_plt_config {`; `struct telemetry_unit_config pss_config;`; `struct telemetry_unit_config ioss_config;`; `struct mutex telem_trace_lock;`

## Control Flow
Telemetry users configure sampling/events and read telemetry data through platform-specific backend functions.

## State and Persistence
State is telemetry hardware configuration, event masks, and buffers managed by implementation files.

## Dependencies and Integration Points
Depends on Intel SoC platform drivers, IPC/IOSF-style access paths, and power/thermal subsystems.

## Risks
Risks include unsupported platform access, stale event IDs, and races with firmware-managed telemetry state.

## Test Signals
Tests should include platform probe, telemetry read/config calls, invalid event handling, suspend/resume, and non-supported build stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/intel_telemetry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/invpcid.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/invpcid.h

## Purpose
Inline INVPCID instruction wrapper and descriptor type definitions for precise TLB invalidation. The header is 50 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: None visible in this header.

Notable constants/macros: `#define _ASM_X86_INVPCID`; `#define INVPCID_TYPE_INDIV_ADDR 0`; `#define INVPCID_TYPE_SINGLE_CTXT 1`; `#define INVPCID_TYPE_ALL_INCL_GLOBAL 2`; `#define INVPCID_TYPE_ALL_NON_GLOBAL 3`

Notable declarations and inline helpers: `#define _ASM_X86_INVPCID`; `static inline void __invpcid(unsigned long pcid, unsigned long addr,`; `unsigned long type)`; `struct { u64 d[2]; } desc = { { pcid, addr } };`; `#define INVPCID_TYPE_INDIV_ADDR 0`; `#define INVPCID_TYPE_SINGLE_CTXT 1`; `#define INVPCID_TYPE_ALL_INCL_GLOBAL 2`; `#define INVPCID_TYPE_ALL_NON_GLOBAL 3`; `static inline void invpcid_flush_one(unsigned long pcid,`; `unsigned long addr)`; `static inline void invpcid_flush_single_context(unsigned long pcid)`; `static inline void invpcid_flush_all(void)`; `static inline void invpcid_flush_all_nonglobals(void)`

## Control Flow
Callers build an invpcid_desc with PCID/address and invoke invpcid(type, desc) for individual address, single context, all contexts, or global invalidation.

## State and Persistence
State affected is CPU TLB/PCID state; no software state persists in the header.

## Dependencies and Integration Points
Depends on CPU INVPCID feature checks, CR4 PCIDE, TLB flush code, and inline asm memory clobber semantics.

## Risks
Risks include executing without feature support, wrong descriptor packing/alignment, and insufficient barriers around page-table changes.

## Test Signals
Tests should cover PCID-enabled TLB flush paths, KVM/VMX interactions, hugepage invalidations, and fallback on CPUs without INVPCID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/invpcid.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/io.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/io.h

## Purpose
x86 I/O API for port I/O instructions, string I/O, IO delay, MMIO read/write, ioremap variants, ISA translation, memcpy_to/fromio, and memory encryption aware mappings. The header is 400 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/string.h>`; `#include <linux/compiler.h>`; `#include <linux/cc_platform.h>`; `#include <asm/page.h>`; `#include <asm/early_ioremap.h>`; `#include <asm/pgtable_types.h>`; `#include <asm/shared/io.h>`; `#include <asm/special_insns.h>`

Notable constants/macros: `#define _ASM_X86_IO_H`; `#define build_mmio_read(name, size, type, reg, barrier) \`; `#define build_mmio_write(name, size, type, reg, barrier) \`; `#define readb readb`; `#define readw readw`; `#define readl readl`; `#define readb_relaxed(a) __readb(a)`; `#define readw_relaxed(a) __readw(a)`; `#define readl_relaxed(a) __readl(a)`; `#define __raw_readb __readb`; `#define __raw_readw __readw`; `#define __raw_readl __readl`; `#define writeb writeb`; `#define writew writew`; `#define writel writel`; `#define writeb_relaxed(v, a) __writeb(v, a)`; `#define writew_relaxed(v, a) __writew(v, a)`; `#define writel_relaxed(v, a) __writel(v, a)`

Notable declarations and inline helpers: `#define _ASM_X86_IO_H`; `#define build_mmio_read(name, size, type, reg, barrier) \`; `static inline type name(const volatile void __iomem *addr) \`; `#define build_mmio_write(name, size, type, reg, barrier) \`; `static inline void name(type val, volatile void __iomem *addr) \`; `#define readb readb`; `#define readw readw`; `#define readl readl`; `#define readb_relaxed(a) __readb(a)`; `#define readw_relaxed(a) __readw(a)`; `#define readl_relaxed(a) __readl(a)`; `#define __raw_readb __readb`; `#define __raw_readw __readw`; `#define __raw_readl __readl`; `#define writeb writeb`; `#define writew writew`; `#define writel writel`; `#define writeb_relaxed(v, a) __writeb(v, a)`; `#define writew_relaxed(v, a) __writew(v, a)`; `#define writel_relaxed(v, a) __writel(v, a)`; `#define __raw_writeb __writeb`; `#define __raw_writew __writew`; `#define __raw_writel __writel`; `#define readq_relaxed(a) __readq(a)`

## Control Flow
Inline port helpers emit in/out instructions; MMIO helpers use volatile accesses and barriers; ioremap variants select cache/encryption attributes and resource mapping behavior.

## State and Persistence
State is hardware device I/O ports, MMIO mappings, and page-table attributes established by ioremap; no local persistent data.

## Dependencies and Integration Points
Depends on asm barriers, pgtable/cache attributes, memtype/PAT, encryption masks, uaccess-like volatile semantics, and generic io.h integration.

## Risks
Risks include missing ordering, wrong cacheability/encryption attributes, unsafe ISA address translation, and device-specific side effects from access width.

## Test Signals
Tests should cover port I/O users, MMIO read/write ordering, ioremap_uc/wc/cache/encrypted/decrypted variants, memcpy_io, resource conflicts, and device driver smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/io_apic.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/io_apic.h

## Purpose
IO-APIC declarations, routing-entry formats, pin/IRQ mapping, domain setup, and legacy interrupt routing hooks. The header is 218 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/types.h>`; `#include <asm/mpspec.h>`; `#include <asm/apicdef.h>`; `#include <asm/irq_vectors.h>`; `#include <asm/x86_init.h>`

Notable constants/macros: `#define _ASM_X86_IO_APIC_H`; `#define IOAPIC_MAP_ALLOC 0x1`; `#define IOAPIC_MAP_CHECK 0x2`; `#define IO_APIC_IRQ(x) (((x) >= NR_IRQS_LEGACY) || ((1 << (x)) & io_apic_irqs))`; `#define io_apic_assign_pci_irqs \`; `#define IO_APIC_IRQ(x) 0`; `#define io_apic_assign_pci_irqs 0`; `#define setup_ioapic_ids_from_mpc x86_init_noop`; `#define nr_ioapics (0)`; `#define gsi_top (NR_IRQS_LEGACY)`; `#define native_io_apic_read NULL`; `#define native_restore_boot_irq_mode NULL`

Notable declarations and inline helpers: `#define _ASM_X86_IO_APIC_H`; `union IO_APIC_reg_00 {`; `u32 raw;`; `struct {`; `u32 __reserved_2 : 14,`; `union IO_APIC_reg_01 {`; `u32 version : 8,`; `union IO_APIC_reg_02 {`; `u32 __reserved_2 : 24,`; `union IO_APIC_reg_03 {`; `u32 boot_DT : 1,`; `struct IO_APIC_route_entry {`; `union {`; `u64 vector : 8,`; `u64 ir_shared_0 : 8,`; `u64 w1 : 32,`; `struct irq_alloc_info;`; `struct ioapic_domain_cfg;`; `#define IOAPIC_MAP_ALLOC 0x1`; `#define IOAPIC_MAP_CHECK 0x2`; `extern int nr_ioapics;`; `extern int mpc_ioapic_id(int ioapic);`; `extern unsigned int mpc_ioapic_addr(int ioapic);`; `extern int mp_irq_entries;`

## Control Flow
Boot code discovers IO-APICs, creates domains, maps GSI pins to vectors, configures trigger/polarity, and masks/acks/retriggers interrupts through these APIs.

## State and Persistence
State is IO-APIC MMIO registers, mp_ioapics metadata, pin-to-IRQ mappings, EOI routing, and irqdomain allocation data.

## Dependencies and Integration Points
Depends on ACPI/MPS tables, APIC/vector code, irqdomain, irq_remapping, MSI/legacy IRQ logic, and SMP CPU masks.

## Risks
Risks include wrong polarity/trigger, pin mapping conflicts, EOI delivery bugs, and interactions with interrupt remapping or PIC handoff.

## Test Signals
Tests should boot ACPI and MPS systems, exercise level/edge IRQs, IO-APIC hot paths, CPU affinity, irq remapping, suspend/resume, and no-IOAPIC fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/io_apic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/io_bitmap.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/io_bitmap.h

## Purpose
Task I/O permission bitmap layout and helpers for x86 TSS-based port I/O access control. The header is 52 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/refcount.h>`; `#include <asm/processor.h>`; `#include <asm/paravirt.h>`

Notable constants/macros: `#define _ASM_X86_IOBITMAP_H`; `#define tss_update_io_bitmap native_tss_update_io_bitmap`; `#define tss_invalidate_io_bitmap native_tss_invalidate_io_bitmap`

Notable declarations and inline helpers: `#define _ASM_X86_IOBITMAP_H`; `struct io_bitmap {`; `u64 sequence;`; `unsigned int max;`; `unsigned long bitmap[IO_BITMAP_LONGS];`; `struct task_struct;`; `void io_bitmap_share(struct task_struct *tsk);`; `void io_bitmap_exit(struct task_struct *tsk);`; `static inline void native_tss_invalidate_io_bitmap(void)`; `void native_tss_update_io_bitmap(void);`; `#define tss_update_io_bitmap native_tss_update_io_bitmap`; `#define tss_invalidate_io_bitmap native_tss_invalidate_io_bitmap`; `static inline void io_bitmap_share(struct task_struct *tsk) { }`; `static inline void io_bitmap_exit(struct task_struct *tsk) { }`; `static inline void tss_update_io_bitmap(void) { }`

## Control Flow
Context switch and ioperm/iopl paths copy or invalidate per-task bitmaps and update the TSS I/O bitmap base so user port I/O traps or succeeds.

## State and Persistence
State is per-task io_bitmap data, TSS bitmap storage, and thread flags indicating bitmap validity.

## Dependencies and Integration Points
Depends on processor/TSS layout, thread_struct, syscall ioperm/iopl handling, and context switch code.

## Risks
Risks include stale bitmap permissions after exec/fork, bitmap overrun beyond TSS limit, and privilege escalation through incorrect invalidation.

## Test Signals
Tests should cover ioperm/iopl syscalls, fork/exec inheritance, context switch isolation, invalid port ranges, and 32-bit compat.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/io_bitmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/iomap.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/iomap.h

## Purpose
x86-specific iomap resource helper declarations for write-combining mappings. The header is 22 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/fs.h>`; `#include <linux/mm.h>`; `#include <linux/uaccess.h>`; `#include <linux/highmem.h>`; `#include <asm/cacheflush.h>`; `#include <asm/tlbflush.h>`

Notable constants/macros: `#define _ASM_X86_IOMAP_H`

Notable declarations and inline helpers: `#define _ASM_X86_IOMAP_H`; `void __iomem *__iomap_local_pfn_prot(unsigned long pfn, pgprot_t prot);`; `int iomap_create_wc(resource_size_t base, unsigned long size, pgprot_t *prot);`; `void iomap_free(resource_size_t base, unsigned long size);`

## Control Flow
iomap_create_wc() creates or adjusts WC pgprot mappings for a physical resource range; iomap_free() tears them down.

## State and Persistence
State is resource mapping/memtype state managed by PAT/ioremap internals.

## Dependencies and Integration Points
Depends on resource_size_t, pgprot_t, PAT memtype tracking, and generic iomap users.

## Risks
Risks include WC alias conflicts, leaking memtype reservations, and wrong resource size alignment.

## Test Signals
Tests should exercise framebuffer or PCI BAR WC mappings, overlapping aliases, unmap/free paths, and PAT-disabled fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/iomap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/iommu.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/iommu.h

## Purpose
x86 IOMMU global declarations and DMA-remapping policy flags for Intel/AMD IOMMU, SWIOTLB, and overflow handling. The header is 40 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/acpi.h>`; `#include <asm/e820/api.h>`

Notable constants/macros: `#define _ASM_X86_IOMMU_H`; `#define x86_swiotlb_enable false`; `#define DMAR_OPERATION_TIMEOUT ((cycles_t) tsc_khz*10*1000)`

Notable declarations and inline helpers: `#define _ASM_X86_IOMMU_H`; `extern int force_iommu, no_iommu;`; `extern int iommu_detected;`; `extern int iommu_merge;`; `extern int panic_on_overflow;`; `extern bool amd_iommu_snp_en;`; `extern bool x86_swiotlb_enable;`; `#define x86_swiotlb_enable false`; `#define DMAR_OPERATION_TIMEOUT ((cycles_t) tsc_khz*10*1000)`; `static inline int __init`; `u64 start = rmrr->base_address;`; `u64 end = rmrr->end_address + 1;`; `int entry_type;`

## Control Flow
Boot code sets force/no-IOMMU/detected/merge flags, detects ACPI/DMAR/IOMMU hardware, and times out hardware operations using TSC-derived limits.

## State and Persistence
State is global IOMMU policy flags, detected hardware state, SNP/IOMMU flags, and SWIOTLB enablement.

## Dependencies and Integration Points
Depends on ACPI, e820, TSC calibration, DMA mapping subsystems, AMD/Intel IOMMU drivers, and kernel command-line policy.

## Risks
Risks include bad boot-parameter interaction, overflow panic policy surprises, timeout scaling errors before TSC init, and SNP/SWIOTLB mismatches.

## Test Signals
Tests should boot with iommu=on/off/force, AMD and Intel IOMMUs, SWIOTLB fallback, DMA stress, SNP guests, and timeout/error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/iommu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/iosf_mbi.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/iosf_mbi.h

## Purpose
Intel IOSF sideband Message Bus Interface API for register reads/writes, P-unit locking, PMIC bus access notifications, and SoC unit/opcode constants. The header is 246 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/notifier.h>`

Notable constants/macros: `#define IOSF_MBI_SYMS_H`; `#define MBI_MCR_OFFSET 0xD0`; `#define MBI_MDR_OFFSET 0xD4`; `#define MBI_MCRX_OFFSET 0xD8`; `#define MBI_RD_MASK 0xFEFFFFFF`; `#define MBI_WR_MASK 0X01000000`; `#define MBI_MASK_HI 0xFFFFFF00`; `#define MBI_MASK_LO 0x000000FF`; `#define MBI_ENABLE 0xF0`; `#define MBI_MMIO_READ 0x00`; `#define MBI_MMIO_WRITE 0x01`; `#define MBI_CFG_READ 0x04`; `#define MBI_CFG_WRITE 0x05`; `#define MBI_CR_READ 0x06`; `#define MBI_CR_WRITE 0x07`; `#define MBI_REG_READ 0x10`; `#define MBI_REG_WRITE 0x11`; `#define MBI_ESRAM_READ 0x12`

Notable declarations and inline helpers: `#define IOSF_MBI_SYMS_H`; `#define MBI_MCR_OFFSET 0xD0`; `#define MBI_MDR_OFFSET 0xD4`; `#define MBI_MCRX_OFFSET 0xD8`; `#define MBI_RD_MASK 0xFEFFFFFF`; `#define MBI_WR_MASK 0X01000000`; `#define MBI_MASK_HI 0xFFFFFF00`; `#define MBI_MASK_LO 0x000000FF`; `#define MBI_ENABLE 0xF0`; `#define MBI_MMIO_READ 0x00`; `#define MBI_MMIO_WRITE 0x01`; `#define MBI_CFG_READ 0x04`; `#define MBI_CFG_WRITE 0x05`; `#define MBI_CR_READ 0x06`; `#define MBI_CR_WRITE 0x07`; `#define MBI_REG_READ 0x10`; `#define MBI_REG_WRITE 0x11`; `#define MBI_ESRAM_READ 0x12`; `#define MBI_ESRAM_WRITE 0x13`; `#define BT_MBI_UNIT_AUNIT 0x00`; `#define BT_MBI_UNIT_SMC 0x01`; `#define BT_MBI_UNIT_CPU 0x02`; `#define BT_MBI_UNIT_BUNIT 0x03`; `#define BT_MBI_UNIT_PMC 0x04`

## Control Flow
Clients call iosf_mbi_read/write/modify with port/opcode/offset; PMIC and P-unit helpers serialize bus access and notify registered blockers around PMIC transactions.

## State and Persistence
State is IOSF hardware registers, P-unit lock ownership, and notifier-chain registration stored in implementation files.

## Dependencies and Integration Points
Depends on notifier chains, Intel SoC platform support, P-unit/PMIC drivers, and sideband PCI/MMIO accessors.

## Risks
Risks include deadlocks around P-unit acquisition, unbalanced PMIC bus blocking, unsupported port/opcode access, and silent -EPROBE_DEFER/-ENODEV behavior in stubs.

## Test Signals
Tests should cover read/write/modify on supported SoCs, notifier registration/unregistration, lock assertion, concurrent PMIC/P-unit users, and disabled-config stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/iosf_mbi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/irq.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/irq.h

## Purpose
Top-level x86 IRQ declarations for legacy IRQ canonicalization, IRQ stack init, IRQ fixups, backtrace IPIs, and native IRQ initialization. The header is 50 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/apicdef.h>`; `#include <asm/irq_vectors.h>`

Notable constants/macros: `#define _ASM_X86_IRQ_H`; `#define __irq_entry __invalid_section`; `#define arch_trigger_cpumask_backtrace arch_trigger_cpumask_backtrace`

Notable declarations and inline helpers: `#define _ASM_X86_IRQ_H`; `#define __irq_entry __invalid_section`; `static inline int irq_canonicalize(int irq)`; `extern int irq_init_percpu_irqstack(unsigned int cpu);`; `struct irq_desc;`; `extern void fixup_irqs(void);`; `extern void kvm_set_posted_intr_wakeup_handler(void (*handler)(void));`; `extern void (*x86_platform_ipi_callback)(void);`; `extern void native_init_IRQ(void);`; `extern void __handle_irq(struct irq_desc *desc, struct pt_regs *regs);`; `extern void init_ISA_irqs(void);`; `void arch_trigger_cpumask_backtrace(const struct cpumask *mask,`; `int exclude_cpu);`; `#define arch_trigger_cpumask_backtrace arch_trigger_cpumask_backtrace`

## Control Flow
Boot code calls native_init_IRQ()/init_ISA_irqs(), CPU bringup initializes per-CPU IRQ stacks, and runtime fixup/backtrace handlers route interrupts after CPU/hotplug changes.

## State and Persistence
State is IRQ descriptors, per-CPU IRQ stacks, platform IPI callback pointer, and posted interrupt wakeup handler.

## Dependencies and Integration Points
Depends on APIC definitions, irq_vectors.h, irq_desc, KVM posted interrupts, SMP cpumasks, and generic IRQ core.

## Risks
Risks include failing to move IRQs off offline CPUs, bad IRQ stack allocation, and platform IPI callback misuse.

## Test Signals
Tests should cover IRQ init, CPU hotplug fixup_irqs, posted interrupt wakeup, NMI/backtrace IPIs, and legacy ISA IRQ setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/irq_remapping.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/irq_remapping.h

## Purpose
Interrupt remapping interface for Intel/AMD IOMMU-backed IRQ domains and posted interrupt metadata. The header is 98 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/irqdomain.h>`; `#include <asm/hw_irq.h>`; `#include <asm/io_apic.h>`

Notable constants/macros: `#define __X86_IRQ_REMAPPING_H`; `#define intel_ack_posted_msi_irq NULL`

Notable declarations and inline helpers: `#define __X86_IRQ_REMAPPING_H`; `struct msi_msg;`; `struct irq_alloc_info;`; `enum irq_remap_cap {`; `enum {`; `struct amd_iommu_pi_data {`; `u64 vapic_addr; /* Physical address of the vCPU's vAPIC. */`; `u32 ga_tag;`; `u32 vector; /* Guest vector of the interrupt */`; `int cpu;`; `bool ga_log_intr;`; `bool is_guest_mode;`; `void *ir_data;`; `struct intel_iommu_pi_data {`; `u64 pi_desc_addr; /* Physical address of PI Descriptor */`; `extern raw_spinlock_t irq_2_ir_lock;`; `extern bool irq_remapping_cap(enum irq_remap_cap cap);`; `extern void set_irq_remapping_broken(void);`; `extern int irq_remapping_prepare(void);`; `extern int irq_remapping_enable(void);`; `extern void irq_remapping_disable(void);`; `extern int irq_remapping_reenable(int);`; `extern int irq_remap_enable_fault_handling(void);`; `extern void panic_if_irq_remap(const char *msg);`

## Control Flow
Boot enables/remaps IRQs, exposes capability checks, creates parent vector domains, and uses AMD/Intel PI data structures to target vCPU posted interrupts.

## State and Persistence
State is remapping hardware tables, irq_2_ir_lock protected mappings, enable_posted_msi, and per-interrupt PI data.

## Dependencies and Integration Points
Depends on irqdomain, hw_irq, io_apic, IOMMU drivers, MSI, KVM posted interrupts, and x2APIC/xAPIC modes.

## Risks
Risks include enabling x2APIC without remapping, stale PI descriptors, remap fault handling gaps, and fallback stubs masking missing hardware.

## Test Signals
Tests should boot with Intel/AMD IRQ remapping, x2APIC, MSI/MSI-X, KVM posted interrupts, remap fault injection, and no-remap fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/irq_remapping.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/irq_stack.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/irq_stack.h

## Purpose
x86 IRQ stack switching macros for running hard IRQ, system vector, and softirq work on the per-CPU interrupt stack. The header is 241 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/ptrace.h>`; `#include <linux/objtool.h>`; `#include <asm/processor.h>`

Notable constants/macros: `#define _ASM_X86_IRQ_STACK_H`; `#define call_on_stack(stack, func, asm_call, argconstr...) \`; `#define ASM_CALL_ARG0 \`; `#define ASM_CALL_ARG1 \`; `#define ASM_CALL_ARG2 \`; `#define ASM_CALL_ARG3 \`; `#define call_on_irqstack(func, asm_call, argconstr...) \`; `#define assert_function_type(func, proto) \`; `#define assert_arg_type(arg, proto) \`; `#define call_on_irqstack_cond(func, regs, asm_call, constr, c_args...) \`; `#define ASM_CALL_SYSVEC \`; `#define SYSVEC_CONSTRAINTS , [arg1] "r" (regs)`; `#define run_sysvec_on_irqstack_cond(func, regs) \`; `#define ASM_CALL_IRQ \`; `#define IRQ_CONSTRAINTS , [arg1] "r" (regs), [arg2] "r" ((unsigned long)vector)`; `#define run_irq_on_irqstack_cond(func, regs, vector) \`; `#define do_softirq_own_stack() \`

Notable declarations and inline helpers: `#define _ASM_X86_IRQ_STACK_H`; `#define call_on_stack(stack, func, asm_call, argconstr...) \`; `#define ASM_CALL_ARG0 \`; `#define ASM_CALL_ARG1 \`; `#define ASM_CALL_ARG2 \`; `#define ASM_CALL_ARG3 \`; `#define call_on_irqstack(func, asm_call, argconstr...) \`; `#define assert_function_type(func, proto) \`; `#define assert_arg_type(arg, proto) \`; `#define call_on_irqstack_cond(func, regs, asm_call, constr, c_args...) \`; `#define ASM_CALL_SYSVEC \`; `#define SYSVEC_CONSTRAINTS , [arg1] "r" (regs)`; `#define run_sysvec_on_irqstack_cond(func, regs) \`; `#define ASM_CALL_IRQ \`; `#define IRQ_CONSTRAINTS , [arg1] "r" (regs), [arg2] "r" ((unsigned long)vector)`; `#define run_irq_on_irqstack_cond(func, regs, vector) \`; `#define do_softirq_own_stack() \`

## Control Flow
call_on_stack() saves the original SP at the top of the IRQ stack, switches stacks, invokes typed assembly call glue, restores SP, and conditionally avoids switching when already on the IRQ stack or from user mode.

## State and Persistence
State is per-CPU hardirq_stack_ptr and transient stack linkage for unwinders.

## Dependencies and Integration Points
Depends on objtool noinstr expectations, pt_regs, processor stack layout, hardirq state, and idtentry system vector wrappers.

## Risks
Risks include broken unwinding, wrong argument constraints, stack corruption, and running instrumented code before entry state is valid.

## Test Signals
Tests should cover nested IRQs, sysvec/device IRQs, softirq own stack, objtool validation, unwinds through IRQ stack, and 32-bit fallback macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/irq_stack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/irq_vectors.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/irq_vectors.h

## Purpose
x86 interrupt vector number map and NR_IRQS sizing policy for exceptions, external IRQs, APIC system vectors, Hyper-V, KVM, posted MSI, and legacy IRQs. The header is 148 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/threads.h>`

Notable constants/macros: `#define _ASM_X86_IRQ_VECTORS_H`; `#define NMI_VECTOR 0x02`; `#define FIRST_EXTERNAL_VECTOR 0x20`; `#define IA32_SYSCALL_VECTOR 0x80`; `#define ISA_IRQ_VECTOR(irq) (((FIRST_EXTERNAL_VECTOR + 16) & ~15) + irq)`; `#define SPURIOUS_APIC_VECTOR 0xff`; `#define ERROR_APIC_VECTOR 0xfe`; `#define RESCHEDULE_VECTOR 0xfd`; `#define CALL_FUNCTION_VECTOR 0xfc`; `#define CALL_FUNCTION_SINGLE_VECTOR 0xfb`; `#define THERMAL_APIC_VECTOR 0xfa`; `#define THRESHOLD_APIC_VECTOR 0xf9`; `#define REBOOT_VECTOR 0xf8`; `#define X86_PLATFORM_IPI_VECTOR 0xf7`; `#define IRQ_WORK_VECTOR 0xf6`; `#define PERF_GUEST_MEDIATED_PMI_VECTOR 0xf5`; `#define DEFERRED_ERROR_VECTOR 0xf4`; `#define HYPERVISOR_CALLBACK_VECTOR 0xf3`

Notable declarations and inline helpers: `#define _ASM_X86_IRQ_VECTORS_H`; `#define NMI_VECTOR 0x02`; `#define FIRST_EXTERNAL_VECTOR 0x20`; `#define IA32_SYSCALL_VECTOR 0x80`; `#define ISA_IRQ_VECTOR(irq) (((FIRST_EXTERNAL_VECTOR + 16) & ~15) + irq)`; `#define SPURIOUS_APIC_VECTOR 0xff`; `#define ERROR_APIC_VECTOR 0xfe`; `#define RESCHEDULE_VECTOR 0xfd`; `#define CALL_FUNCTION_VECTOR 0xfc`; `#define CALL_FUNCTION_SINGLE_VECTOR 0xfb`; `#define THERMAL_APIC_VECTOR 0xfa`; `#define THRESHOLD_APIC_VECTOR 0xf9`; `#define REBOOT_VECTOR 0xf8`; `#define X86_PLATFORM_IPI_VECTOR 0xf7`; `#define IRQ_WORK_VECTOR 0xf6`; `#define PERF_GUEST_MEDIATED_PMI_VECTOR 0xf5`; `#define DEFERRED_ERROR_VECTOR 0xf4`; `#define HYPERVISOR_CALLBACK_VECTOR 0xf3`; `#define POSTED_INTR_VECTOR 0xf2`; `#define POSTED_INTR_WAKEUP_VECTOR 0xf1`; `#define POSTED_INTR_NESTED_VECTOR 0xf0`; `#define MANAGED_IRQ_SHUTDOWN_VECTOR 0xef`; `#define HYPERV_REENLIGHTENMENT_VECTOR 0xee`; `#define HYPERV_STIMER0_VECTOR 0xed`

## Control Flow
No runtime flow; constants partition 0..255 vectors into exception, external, and reserved system-vector ranges and size IRQ space by IO-APIC/CPU limits.

## State and Persistence
State is absent but the constants form a binary contract for IDT entries, APIC routing, and IRQ allocation.

## Dependencies and Integration Points
Depends on CONFIG_* vector users, NR_CPUS, MAX_IO_APICS, SMP, IO-APIC, Hyper-V, KVM, and local APIC support.

## Risks
Risks include vector collisions, insufficient NR_IRQS sizing, and config-dependent FIRST_SYSTEM_VECTOR shifts breaking entry declarations.

## Test Signals
Tests should compile vector-heavy configs, boot SMP/APIC systems, allocate many MSI vectors, exercise Hyper-V/KVM posted vectors, and verify no overlap assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/irq_vectors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/irq_work.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/irq_work.h

## Purpose
Architecture hook telling generic irq_work whether x86 can deliver irq_work through an interrupt vector. The header is 19 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/cpufeature.h>`

Notable constants/macros: `#define _ASM_IRQ_WORK_H`

Notable declarations and inline helpers: `#define _ASM_IRQ_WORK_H`; `static inline bool arch_irq_work_has_interrupt(void)`

## Control Flow
The helper returns true when local APIC/IRQ_WORK_VECTOR support is available, otherwise false for fallback behavior.

## State and Persistence
State is absent; behavior is based on build/CPU feature configuration.

## Dependencies and Integration Points
Depends on cpufeature/local APIC configuration and generic irq_work core.

## Risks
Risks are missed wakeups or slower fallback if capability is misreported.

## Test Signals
Tests should run irq_work selftests on APIC and non-APIC configs, including CPU hotplug and nohz contexts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/irq_work.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/irqdomain.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/irqdomain.h

## Purpose
x86 IRQ domain declarations for vector, IO-APIC, HPET, and PCI MSI domains. The header is 64 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/irqdomain.h>`; `#include <asm/hw_irq.h>`

Notable constants/macros: `#define _ASM_IRQDOMAIN_H`; `#define native_create_pci_msi_domain NULL`; `#define x86_pci_msi_default_domain NULL`

Notable declarations and inline helpers: `#define _ASM_IRQDOMAIN_H`; `enum {`; `extern int x86_fwspec_is_ioapic(struct irq_fwspec *fwspec);`; `extern int x86_fwspec_is_hpet(struct irq_fwspec *fwspec);`; `extern struct irq_domain *x86_vector_domain;`; `extern void init_irq_alloc_info(struct irq_alloc_info *info,`; `extern void copy_irq_alloc_info(struct irq_alloc_info *dst,`; `struct irq_alloc_info *src);`; `struct device_node;`; `struct irq_data;`; `enum ioapic_domain_type {`; `struct ioapic_domain_cfg {`; `enum ioapic_domain_type type;`; `struct device_node *dev;`; `extern const struct irq_domain_ops mp_ioapic_irqdomain_ops;`; `extern int mp_irqdomain_alloc(struct irq_domain *domain, unsigned int virq,`; `unsigned int nr_irqs, void *arg);`; `extern void mp_irqdomain_free(struct irq_domain *domain, unsigned int virq,`; `unsigned int nr_irqs);`; `extern int mp_irqdomain_activate(struct irq_domain *domain,`; `struct irq_data *irq_data, bool reserve);`; `extern void mp_irqdomain_deactivate(struct irq_domain *domain,`; `struct irq_data *irq_data);`; `extern int mp_irqdomain_ioapic_idx(struct irq_domain *domain);`

## Control Flow
Allocation helpers initialize/copy irq_alloc_info, IO-APIC domain ops allocate/free/activate pins, and MSI domain creation installs native PCI MSI routing.

## State and Persistence
State is x86_vector_domain, x86_pci_msi_default_domain, IO-APIC domain config, and per-domain allocation metadata.

## Dependencies and Integration Points
Depends on linux/irqdomain, hw_irq allocation info, IO-APIC, HPET, PCI MSI, and hierarchical IRQ domains.

## Risks
Risks include parent-domain mismatches, incorrect fwspec classification, leaked virqs, and MSI domain absence under config variants.

## Test Signals
Tests should cover IO-APIC domain allocation, HPET IRQs, PCI MSI/MSI-X, domain activate/deactivate, ACPI fwspec parsing, and CONFIG_PCI_MSI stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/irqdomain.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/irqflags.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/irqflags.h

## Purpose
Low-level x86 interrupt flag helpers for saving/restoring EFLAGS/RFLAGS.IF, enabling/disabling IRQs, halt/safe_halt, and paravirt-aware arch wrappers. The header is 163 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/processor-flags.h>`; `#include <asm/nospec-branch.h>`; `#include <asm/paravirt.h>`; `#include <linux/types.h>`

Notable constants/macros: `#define _X86_IRQFLAGS_H_`; `#define SAVE_FLAGS pushfq; popq %rax`

Notable declarations and inline helpers: `#define _X86_IRQFLAGS_H_`; `extern inline unsigned long native_save_fl(void);`; `extern __always_inline unsigned long native_save_fl(void)`; `unsigned long flags;`; `static __always_inline void native_irq_disable(void)`; `static __always_inline void native_irq_enable(void)`; `static __always_inline void native_safe_halt(void)`; `static __always_inline void native_halt(void)`; `static __always_inline int native_irqs_disabled_flags(unsigned long flags)`; `static __always_inline unsigned long native_local_irq_save(void)`; `unsigned long flags = native_save_fl();`; `static __always_inline void native_local_irq_restore(unsigned long flags)`; `static __always_inline void arch_safe_halt(void)`; `static __always_inline void halt(void)`; `static __always_inline unsigned long arch_local_save_flags(void)`; `static __always_inline void arch_local_irq_disable(void)`; `static __always_inline void arch_local_irq_enable(void)`; `static __always_inline unsigned long arch_local_irq_save(void)`; `unsigned long flags = arch_local_save_flags();`; `#define SAVE_FLAGS pushfq; popq %rax`; `static __always_inline int arch_irqs_disabled_flags(unsigned long flags)`; `static __always_inline int arch_irqs_disabled(void)`; `static __always_inline void arch_local_irq_restore(unsigned long flags)`

## Control Flow
Native helpers emit pushf/pop, cli, sti, sti;hlt, hlt, and save/restore sequences; arch wrappers either call native or paravirt versions depending on config.

## State and Persistence
State affected is CPU interrupt-enable flag and halt state; saved flags values are transient per caller.

## Dependencies and Integration Points
Depends on processor flags, paravirt patching, nospec branch headers, and generic local_irq APIs.

## Risks
Risks include restoring stale flags, enabling interrupts too early in entry/exit, paravirt mismatch, and unsafe halt with interrupts disabled.

## Test Signals
Tests should cover local_irq_save/restore nesting, lockdep IRQ state, idle halt paths, paravirt guests, and objtool/noinstr entry users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/irqflags.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/ist.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/ist.h

## Purpose
Interrupt Stack Table information declaration and UAPI include for x86 special exception stacks. The header is 14 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <uapi/asm/ist.h>`

Notable constants/macros: `#define _ASM_X86_IST_H`

Notable declarations and inline helpers: `#define _ASM_X86_IST_H`; `extern struct ist_info ist_info;`

## Control Flow
No local control flow; it exposes global ist_info for code that reports or configures IST stack layout.

## State and Persistence
State is the global IST layout metadata and TSS IST pointers managed by CPU init/entry code.

## Dependencies and Integration Points
Depends on uapi/asm/ist.h and x86_64 exception stack setup.

## Risks
Risks include stale IST metadata relative to actual TSS stacks and config-only compile gaps.

## Test Signals
Tests should cover NMI/DB/MCE/DF stack setup, debugfs/proc reporting if present, and x86_64 builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/ist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/jailhouse_para.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/jailhouse_para.h

## Purpose
Jailhouse hypervisor paravirtualization detection helper. The header is 26 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/types.h>`

Notable constants/macros: `#define _ASM_X86_JAILHOUSE_PARA_H`

Notable declarations and inline helpers: `#define _ASM_X86_JAILHOUSE_PARA_H`; `bool jailhouse_paravirt(void);`; `static inline bool jailhouse_paravirt(void)`

## Control Flow
jailhouse_paravirt() reports true only when Jailhouse guest support is configured and detected; otherwise it compiles to false.

## State and Persistence
State is global hypervisor detection state in the Jailhouse implementation.

## Dependencies and Integration Points
Depends on CONFIG_JAILHOUSE_GUEST and x86 hypervisor detection.

## Risks
Risks are minimal, but false positives can install wrong paravirt behavior and false negatives skip required guest quirks.

## Test Signals
Tests should boot Jailhouse and non-Jailhouse guests and compile disabled stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/jailhouse_para.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/jump_label.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/jump_label.h

## Purpose
x86 static key/jump label assembly encoding for branch and nop patch sites plus jump-table entries. The header is 61 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/asm.h>`; `#include <asm/nops.h>`; `#include <linux/stringify.h>`; `#include <linux/types.h>`

Notable constants/macros: `#define _ASM_X86_JUMP_LABEL_H`; `#define HAVE_JUMP_LABEL_BATCH`; `#define JUMP_TABLE_ENTRY(key, label) \`; `#define ARCH_STATIC_BRANCH_ASM(key, label) \`

Notable declarations and inline helpers: `#define _ASM_X86_JUMP_LABEL_H`; `#define HAVE_JUMP_LABEL_BATCH`; `#define JUMP_TABLE_ENTRY(key, label) \`; `#define ARCH_STATIC_BRANCH_ASM(key, label) \`; `static __always_inline bool arch_static_branch(struct static_key * const key, const bool branch)`; `static __always_inline bool arch_static_branch_jump(struct static_key * const key, const bool branch)`; `extern int arch_jump_entry_size(struct jump_entry *entry);`

## Control Flow
ARCH_STATIC_BRANCH_ASM emits a patchable nop/jump sequence and JUMP_TABLE_ENTRY records code/target/key triples for runtime text patching.

## State and Persistence
State is kernel text patched at runtime and __jump_table metadata keyed by static_key values.

## Dependencies and Integration Points
Depends on asm/nops, text patching, static keys, alternatives, module loading, and compiler inline asm constraints.

## Risks
Risks include wrong instruction length, bad relocation entries, patching races, and module jump-table mismatch.

## Test Signals
Tests should run static key selftests, module load/unload with static branches, SMP patching stress, and objdump/text-poke validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/jump_label.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kasan.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/kasan.h

## Purpose
x86 KASAN shadow memory layout and init declarations. The header is 41 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/const.h>`

Notable constants/macros: `#define _ASM_X86_KASAN_H`; `#define KASAN_SHADOW_OFFSET _AC(CONFIG_KASAN_SHADOW_OFFSET, UL)`; `#define KASAN_SHADOW_SCALE_SHIFT 3`; `#define KASAN_SHADOW_START (KASAN_SHADOW_OFFSET + \`; `#define KASAN_SHADOW_END (KASAN_SHADOW_START + \`

Notable declarations and inline helpers: `#define _ASM_X86_KASAN_H`; `#define KASAN_SHADOW_OFFSET _AC(CONFIG_KASAN_SHADOW_OFFSET, UL)`; `#define KASAN_SHADOW_SCALE_SHIFT 3`; `#define KASAN_SHADOW_START (KASAN_SHADOW_OFFSET + \`; `#define KASAN_SHADOW_END (KASAN_SHADOW_START + \`; `void __init kasan_early_init(void);`; `void __init kasan_init(void);`; `void __init kasan_populate_shadow_for_vaddr(void *va, size_t size, int nid);`; `static inline void kasan_early_init(void) { }`; `static inline void kasan_init(void) { }`; `static inline void kasan_populate_shadow_for_vaddr(void *va, size_t size,`; `int nid) { }`

## Control Flow
Boot KASAN code computes shadow start/end from CONFIG_KASAN_SHADOW_OFFSET, populates early shadow mappings, and later initializes full shadow coverage.

## State and Persistence
State is KASAN shadow memory mappings and per-address shadow bytes maintained by sanitizer runtime.

## Dependencies and Integration Points
Depends on virtual address layout, page tables, memory initialization, NUMA node population, and generic KASAN.

## Risks
Risks include wrong shadow range for 5-level paging or KASLR, missing early mappings, and false positives/negatives from unpopulated shadow.

## Test Signals
Tests should boot KASAN configs, run kasan tests, exercise vmalloc/module/direct-map shadow, NUMA population, and KASLR/LA57 combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kasan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kaslr.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/kaslr.h

## Purpose
x86 KASLR declarations for random values, physical/virtual memory randomization, and trampoline randomization. The header is 15 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: None visible in this header.

Notable constants/macros: `#define _ASM_KASLR_H_`

Notable declarations and inline helpers: `#define _ASM_KASLR_H_`; `unsigned long kaslr_get_random_long(const char *purpose);`; `void kernel_randomize_memory(void);`; `void init_trampoline_kaslr(void);`; `static inline void kernel_randomize_memory(void) { }`; `static inline void init_trampoline_kaslr(void) {}`

## Control Flow
Boot code obtains purpose-labeled random longs and applies kernel memory and trampoline layout randomization when RANDOMIZE_MEMORY is enabled.

## State and Persistence
State is boot-chosen randomized physical/virtual offsets and trampoline placement; fixed after boot.

## Dependencies and Integration Points
Depends on early entropy, boot parameters, memory map parsing, page-table setup, and CONFIG_RANDOMIZE_MEMORY.

## Risks
Risks include weak early entropy, collisions with reserved regions, and runtime code assuming fixed addresses.

## Test Signals
Tests should boot repeatedly and compare layout variance, validate no overlap with reserved memory, test nokaslr, and cover hibernation/kexec interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kaslr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kbdleds.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/kbdleds.h

## Purpose
Default keyboard LED selection helper for x86 boot options. The header is 18 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/setup.h>`

Notable constants/macros: `#define _ASM_X86_KBDLEDS_H`

Notable declarations and inline helpers: `#define _ASM_X86_KBDLEDS_H`; `static inline int kbd_defleds(void)`

## Control Flow
kbd_defleds() returns configured default LED bits, typically influenced by boot/setup state.

## State and Persistence
State is boot setup data consulted through asm/setup.h; no mutable state is held here.

## Dependencies and Integration Points
Depends on keyboard/VT console code and x86 setup header values.

## Risks
Risks are minor: incorrect default LED state or compile drift with setup fields.

## Test Signals
Tests should verify boot parameter/default LED behavior and compile keyboard-disabled configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kbdleds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kdebug.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/kdebug.h

## Purpose
x86 die/oops/debug notification declarations and enums for exception diagnostics. The header is 45 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/notifier.h>`

Notable constants/macros: `#define _ASM_X86_KDEBUG_H`

Notable declarations and inline helpers: `#define _ASM_X86_KDEBUG_H`; `struct pt_regs;`; `enum die_val {`; `enum show_regs_mode {`; `extern void die(const char *, struct pt_regs *,long);`; `void die_addr(const char *str, struct pt_regs *regs, long err, long gp_addr);`; `extern int __must_check __die(const char *, struct pt_regs *, long);`; `extern void show_stack_regs(struct pt_regs *regs);`; `extern void __show_regs(struct pt_regs *regs, enum show_regs_mode,`; `extern void show_iret_regs(struct pt_regs *regs, const char *log_lvl);`; `extern unsigned long oops_begin(void);`; `extern void oops_end(unsigned long, struct pt_regs *, int signr);`

## Control Flow
Exception paths call die()/__die()/die_addr(), notify die chains with enum die_val reasons, print registers/stacks, and bracket oops reporting with oops_begin/end.

## State and Persistence
State includes notifier chains, oops-in-progress state, console/lock handling, and pt_regs snapshots managed elsewhere.

## Dependencies and Integration Points
Depends on linux/notifier, pt_regs, trap handlers, printk/oops infrastructure, and debug exception users.

## Risks
Risks include notifier recursion, deadlocks during oops, leaking bad register data, and wrong die reason classification.

## Test Signals
Tests should cover WARN/oops paths, die notifiers, NMI/MCE/debug exceptions, panic-on-oops, and show_regs modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kdebug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kexec-bzimage64.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/kexec-bzimage64.h

## Purpose
Declaration of the x86-64 bzImage kexec file loader operations. The header is 7 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: None visible in this header.

Notable constants/macros: `#define _ASM_KEXEC_BZIMAGE64_H`

Notable declarations and inline helpers: `#define _ASM_KEXEC_BZIMAGE64_H`; `extern const struct kexec_file_ops kexec_bzImage64_ops;`

## Control Flow
No local control flow; the kexec file loader references kexec_bzImage64_ops to parse and load bzImage kernels.

## State and Persistence
State is kimage load metadata managed by kexec file code.

## Dependencies and Integration Points
Depends on CONFIG_KEXEC_FILE, bzImage parser, purgatory, and kexec.h architecture structures.

## Risks
Risks are compile/link breakage if ops are unavailable or loader ABI changes.

## Test Signals
Tests should load bzImage through kexec_file_load, verify signature/purgatory paths, and compile disabled configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kexec-bzimage64.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kexec.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/kexec.h

## Purpose
x86 kexec/crash-kernel architecture contract for relocation code, crash register capture, kimage architecture data, purgatory relocation, and crash hotplug support. The header is 237 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/bits.h>`; `#include <linux/string.h>`; `#include <linux/kernel.h>`; `#include <asm/asm.h>`; `#include <asm/page.h>`; `#include <asm/ptrace.h>`

Notable constants/macros: `#define _ASM_X86_KEXEC_H`; `#define RELOC_KERNEL_PRESERVE_CONTEXT BIT(0)`; `#define RELOC_KERNEL_CACHE_INCOHERENT BIT(1)`; `#define ARCH_HAS_KIMAGE_ARCH`; `#define arch_kexec_post_alloc_pages arch_kexec_post_alloc_pages`; `#define arch_kexec_pre_free_pages arch_kexec_pre_free_pages`; `#define arch_kexec_protect_crashkres arch_kexec_protect_crashkres`; `#define arch_kexec_unprotect_crashkres arch_kexec_unprotect_crashkres`; `#define arch_kexec_apply_relocations_add arch_kexec_apply_relocations_add`; `#define arch_kimage_file_post_load_cleanup arch_kimage_file_post_load_cleanup`; `#define arch_crash_handle_hotplug_event arch_crash_handle_hotplug_event`; `#define arch_crash_hotplug_support arch_crash_hotplug_support`; `#define crash_get_elfcorehdr_size arch_crash_get_elfcorehdr_size`

Notable declarations and inline helpers: `#define _ASM_X86_KEXEC_H`; `# define PA_CONTROL_PAGE 0`; `# define VA_CONTROL_PAGE 1`; `# define PA_PGD 2`; `# define PA_SWAP_PAGE 3`; `# define PAGES_NR 4`; `# define KEXEC_DEBUG_EXC_HANDLER_SIZE 6 /* PUSHI, PUSHI, 2-byte JMP */`; `#define RELOC_KERNEL_PRESERVE_CONTEXT BIT(0)`; `#define RELOC_KERNEL_CACHE_INCOHERENT BIT(1)`; `# define KEXEC_CONTROL_PAGE_SIZE 4096`; `# define KEXEC_CONTROL_CODE_MAX_SIZE 2048`; `struct kimage;`; `# define KEXEC_SOURCE_MEMORY_LIMIT (-1UL)`; `# define KEXEC_DESTINATION_MEMORY_LIMIT (-1UL)`; `# define KEXEC_CONTROL_MEMORY_LIMIT TASK_SIZE`; `# define KEXEC_ARCH KEXEC_ARCH_386`; `# define vmcore_elf_check_arch_cross(x) ((x)->e_machine == EM_X86_64)`; `# define KEXEC_SOURCE_MEMORY_LIMIT (MAXMEM-1)`; `# define KEXEC_DESTINATION_MEMORY_LIMIT (MAXMEM-1)`; `# define KEXEC_CONTROL_MEMORY_LIMIT (MAXMEM-1)`; `# define KEXEC_ARCH KEXEC_ARCH_X86_64`; `extern unsigned long kexec_va_control_page;`; `extern unsigned long kexec_pa_table_page;`; `extern unsigned long kexec_pa_swap_page;`

## Control Flow
Normal kexec prepares control pages and jumps through relocate_kernel; crash paths capture pt_regs, protect crash memory, build ELF core headers, and optionally shoot down CPUs via NMI.

## State and Persistence
State is kimage_arch metadata, control/swap/table pages, crashk resource protection, preserved context flags, and debug IDT/serial settings.

## Dependencies and Integration Points
Depends on page layout, ptrace regs, ELF/purgatory, memory encryption/cache coherency, CPU hotplug, NMI shootdown, and kexec_file loader ops.

## Risks
Risks include relocation page corruption, bad crash register capture, wrong 32/64-bit entry register setup, cache incoherency, and crash hotplug races.

## Test Signals
Tests should run kexec and kdump, file_load bzImage, crash hotplug, encrypted memory guests, serial debug, CPU offline/online, and relocation/purgatory validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kexec.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kfence.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/kfence.h

## Purpose
x86 KFENCE page-table protection helpers for guard pages and pool initialization. The header is 93 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <linux/bug.h>`; `#include <linux/kfence.h>`; `#include <asm/pgalloc.h>`; `#include <asm/pgtable.h>`; `#include <asm/set_memory.h>`; `#include <asm/tlbflush.h>`

Notable constants/macros: `#define _ASM_X86_KFENCE_H`

Notable declarations and inline helpers: `#define _ASM_X86_KFENCE_H`; `static inline bool arch_kfence_init_pool(void)`; `unsigned long addr;`; `unsigned int level;`; `static inline bool kfence_protect_page(unsigned long addr, bool protect)`

## Control Flow
arch_kfence_init_pool() validates pool mapping assumptions and kfence_protect_page() toggles page present/protection bits, flushes TLBs, and updates direct map attributes.

## State and Persistence
State is page-table protection state for KFENCE pool pages; no separate metadata is stored here.

## Dependencies and Integration Points
Depends on pgalloc/pgtable, set_memory, tlbflush, bug checks, and generic KFENCE allocator.

## Risks
Risks include failing to flush TLBs, corrupting direct-map attributes, and architecture page-table assumptions under debug configs.

## Test Signals
Tests should run KFENCE selftests, allocation/free guard faults, page protection toggling, SMP TLB stress, and boot with KFENCE disabled/enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kfence.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kgdb.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/kgdb.h

## Purpose
x86 KGDB register numbering, breakpoint instruction, buffer sizing, and low-level trap declarations. The header is 92 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/ptrace.h>`

Notable constants/macros: `#define _ASM_X86_KGDB_H`; `#define BUFMAX 1024`; `#define GDB_ORIG_AX 41`; `#define DBG_MAX_REG_NUM 16`; `#define NUMREGBYTES ((GDB_GS+1)*4)`; `#define GDB_ORIG_AX 57`; `#define DBG_MAX_REG_NUM 24`; `#define NUMREGBYTES ((17 * 8) + (5 * 4))`; `#define BREAK_INSTR_SIZE 1`; `#define CACHE_FLUSH_IS_SAFE 1`; `#define GDB_ADJUSTS_BREAK_OFFSET`

Notable declarations and inline helpers: `#define _ASM_X86_KGDB_H`; `#define BUFMAX 1024`; `enum regnames {`; `#define GDB_ORIG_AX 41`; `#define DBG_MAX_REG_NUM 16`; `#define NUMREGBYTES ((GDB_GS+1)*4)`; `#define GDB_ORIG_AX 57`; `#define DBG_MAX_REG_NUM 24`; `#define NUMREGBYTES ((17 * 8) + (5 * 4))`; `static inline void arch_kgdb_breakpoint(void)`; `#define BREAK_INSTR_SIZE 1`; `#define CACHE_FLUSH_IS_SAFE 1`; `#define GDB_ADJUSTS_BREAK_OFFSET`; `extern int kgdb_ll_trap(int cmd, const char *str,`; `struct pt_regs *regs, long err, int trap, int sig);`

## Control Flow
KGDB maps pt_regs to GDB register order, plants int3 breakpoints, and handles low-level serial/debug trap commands through kgdb_ll_trap().

## State and Persistence
State is debugger connection state, saved registers, and breakpoint patch sites managed by KGDB core.

## Dependencies and Integration Points
Depends on ptrace registers, int3 handling, cache coherency assumptions, and 32/64-bit GDB remote protocol layouts.

## Risks
Risks include wrong register numbering, breakpoint offset adjustment, conflicts with kprobes/ftrace, and unsafe debugging in NMI-like contexts.

## Test Signals
Tests should connect gdb over kgdboc, read/write registers, set breakpoints, single-step, test 32/64-bit layouts, and coexist with kprobes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kgdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kmsan.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/kmsan.h

## Purpose
x86 KMSAN metadata mapping helpers for shadow/origin lookup and address validity. The header is 102 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm/cpu_entry_area.h>`; `#include <asm/processor.h>`; `#include <linux/mmzone.h>`

Notable constants/macros: `#define _ASM_X86_KMSAN_H`

Notable declarations and inline helpers: `#define _ASM_X86_KMSAN_H`; `static inline void *arch_kmsan_get_meta_or_null(void *addr, bool is_origin)`; `unsigned long addr64 = (unsigned long)addr;`; `unsigned long off;`; `int cpu;`; `static inline bool kmsan_phys_addr_valid(unsigned long addr)`; `static inline bool kmsan_virt_addr_valid(void *addr)`; `unsigned long x = (unsigned long)addr;`; `unsigned long y = x - __START_KERNEL_map;`; `bool ret;`

## Control Flow
arch_kmsan_get_meta_or_null() maps CPU entry area and other supported virtual addresses to shadow/origin metadata; validity helpers gate physical/virtual regions.

## State and Persistence
State is per-CPU CPU-entry-area shadow/origin arrays and KMSAN metadata mappings maintained by sanitizer runtime.

## Dependencies and Integration Points
Depends on cpu_entry_area layout, processor address classification, mmzone/phys validation, and generic KMSAN.

## Risks
Risks include missing metadata for entry stacks, wrong physical validity boundaries, and sanitizer false reports in low-level entry code.

## Test Signals
Tests should boot KMSAN configs, run KMSAN tests, exercise interrupts/syscalls using CPU entry area, vmalloc/direct-map accesses, and invalid physical addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kmsan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kprobes.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/kprobes.h

## Purpose
x86 kprobes architecture data for instruction slots, optimized probes, previous-probe tracking, and trap handlers. The header is 123 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: `#include <asm-generic/kprobes.h>`; `#include <linux/types.h>`; `#include <linux/ptrace.h>`; `#include <linux/percpu.h>`; `#include <asm/text-patching.h>`; `#include <asm/insn.h>`

Notable constants/macros: `#define _ASM_X86_KPROBES_H`; `#define __ARCH_WANT_KPROBES_INSN_SLOT`; `#define MAX_STACK_SIZE 64`; `#define CUR_STACK_SIZE(ADDR) \`; `#define MIN_STACK_SIZE(ADDR) \`; `#define flush_insn_slot(p) do { } while (0)`; `#define MAX_OPTIMIZED_LENGTH (MAX_INSN_SIZE + DISP32_SIZE)`; `#define MAX_OPTINSN_SIZE \`

Notable declarations and inline helpers: `#define _ASM_X86_KPROBES_H`; `#define __ARCH_WANT_KPROBES_INSN_SLOT`; `struct pt_regs;`; `struct kprobe;`; `typedef u8 kprobe_opcode_t;`; `#define MAX_STACK_SIZE 64`; `#define CUR_STACK_SIZE(ADDR) \`; `#define MIN_STACK_SIZE(ADDR) \`; `#define flush_insn_slot(p) do { } while (0)`; `extern __visible kprobe_opcode_t optprobe_template_entry[];`; `extern __visible kprobe_opcode_t optprobe_template_clac[];`; `extern __visible kprobe_opcode_t optprobe_template_val[];`; `extern __visible kprobe_opcode_t optprobe_template_call[];`; `extern __visible kprobe_opcode_t optprobe_template_end[];`; `#define MAX_OPTIMIZED_LENGTH (MAX_INSN_SIZE + DISP32_SIZE)`; `#define MAX_OPTINSN_SIZE \`; `extern const int kretprobe_blacklist_size;`; `void arch_remove_kprobe(struct kprobe *p);`; `struct arch_specific_insn {`; `unsigned boostable:1;`; `unsigned char size; /* The size of insn */`; `union {`; `unsigned char opcode;`; `struct {`

## Control Flow
Kprobe preparation decodes copied instructions, records fixups/relocations, patches int3 or optimized detour templates, and trap handlers dispatch pre/post/fault processing.

## State and Persistence
State is per-probe arch_specific_insn, optimized instruction buffers, per-CPU kprobe_ctlblk/current probe tracking, and patched text slots.

## Dependencies and Integration Points
Depends on generic kprobes, text patching, insn decoder, pt_regs, optprobe templates, int3/debug exception handling, and retprobe blacklist.

## Risks
Risks include probing unsafe instructions, bad RIP-relative relocation, stack-size checks, text patch races, and conflicts with ftrace/kgdb/livepatch.

## Test Signals
Tests should run kprobe selftests, optimized/unoptimized probes, kretprobes, RIP-relative instructions, fault injection, blacklist coverage, and module probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kprobes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kvm-x86-ops.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/kvm-x86-ops.h

## Purpose
KVM x86 operation list header used to generate the kvm_x86_ops structure, wrappers, and static calls for VMX/SVM backends. The header is 156 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: None visible in this header.

Notable constants/macros: None visible in this header.

Notable declarations and inline helpers: None visible in this header.

## Control Flow
The file is repeatedly included with KVM_X86_OP macros defined differently; each line declares a required, optional, or optional-ret0 backend operation in stable order.

## State and Persistence
State is not stored here, but the operation table controls backend dispatch for vCPU creation, run, MMU, interrupts, MSR, nested virtualization, and feature hooks.

## Dependencies and Integration Points
Depends on KVM core macro inclusion discipline, VMX/SVM implementations, static_call generation, and operation table structure layout.

## Risks
Risks include changing order or optionality without matching backends, missing required ops, and silent ret0 defaults hiding backend feature gaps.

## Test Signals
Tests should compile VMX and SVM, run KVM unit tests, nested virtualization, migration/state save, APIC/MSR/MMU paths, and static_call dispatch validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kvm-x86-ops.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kvm-x86-pmu-ops.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/kvm-x86-pmu-ops.h

## Purpose
KVM x86 PMU operation list header for generating backend PMU callbacks. The header is 33 lines and is part of the Ceph client copy of the Linux x86 architecture tree.

## Important APIs, Types, and Functions
Key includes: None visible in this header.

Notable constants/macros: None visible in this header.

Notable declarations and inline helpers: None visible in this header.

## Control Flow
Like kvm-x86-ops.h, it is macro-included to declare required and optional PMU operations for Intel/AMD virtual PMU behavior.

## State and Persistence
State is backend PMU dispatch metadata; actual PMU state is in vCPU PMU structures and hardware MSRs.

## Dependencies and Integration Points
Depends on KVM PMU core, VMX/SVM PMU implementations, perf_event, CPUID model exposure, and macro inclusion conventions.

## Risks
Risks include backend operation mismatch, optional callback default behavior hiding unsupported PMU features, and ABI changes to virtual PMU state.

## Test Signals
Tests should run KVM PMU unit tests, perf in guests, Intel/AMD vPMU configs, migration of PMU state, and disabled-vPMU fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/kvm-x86-pmu-ops.h -->
