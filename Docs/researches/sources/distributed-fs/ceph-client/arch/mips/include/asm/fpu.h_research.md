# sources/distributed-fs/ceph-client/arch/mips/include/asm/fpu.h


### Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/fpu.h` MIPS FPU ownership, context, emulator, FCSR, and feature-gated FP support. It is part of the MIPS architecture layer carried in the distributed Ceph client source tree, so its Ceph impact is indirect: storage, networking, page cache, DMA, syscall, timer, and interrupt behavior depend on these kernel architecture contracts being correct.

### Important APIs, Types, And Functions
File size: 343 lines / 7567 bytes. macros/constants: `_ASM_FPU_H`, `FPU_FR_MASK`, `__disable_fpu`, `clear_fpu_owner`; types/functions/declarations: `enum fpu_mode {`, `extern void _save_fp(struct task_struct *);`, `extern void _restore_fp(struct task_struct *);`, `static inline int __enable_fpu(enum fpu_mode mode)`, `static inline int __is_fpu_owner(void)`, `static inline int is_fpu_owner(void)`, `static inline int __own_fpu(void)`, `enum fpu_mode mode;`, `static inline int own_fpu_inatomic(int restore)`, `static inline int own_fpu(int restore)`, `static inline void lose_fpu_inatomic(int save, struct task_struct *tsk)`, `static inline void lose_fpu(int save)`, `static inline bool init_fp_ctx(struct task_struct *target)`, `static inline void save_fp(struct task_struct *tsk)`, `static inline void restore_fp(struct task_struct *tsk)`, `static inline union fpureg *get_fpu_regs(struct task_struct *tsk)`, `static inline int __enable_fpu(enum fpu_mode mode)`, `static inline void __disable_fpu(void)`.

### Control Flow
This header is primarily included into platform, architecture, driver, or low-level subsystem translation units. Runtime control flow is therefore in the including code: it expands these constants, inline helpers, or prototypes while boot code, interrupt handlers, MMU paths, firmware calls, device drivers, emulators, or instrumentation paths perform the actual work. Preprocessor configuration selects important behavior, so 32-bit versus 64-bit, platform, CPU feature, endian, and optional subsystem configs must all be considered.

### State, Persistence, And Dependencies
The header itself has no filesystem persistence. The state it affects is kernel memory, task/thread context, CPU registers, page tables, firmware tables, interrupt-controller state, DMA/cache state, or MMIO hardware registers depending on the including subsystem. Direct dependencies: `<linux/sched.h>`, `<linux/sched/task_stack.h>`, `<linux/ptrace.h>`, `<linux/thread_info.h>`, `<linux/bitops.h>`, `<asm/mipsregs.h>`, `<asm/cpu.h>`, `<asm/cpu-features.h>`.

### Integration Points
Used by context switch, traps, KVM, signal/ptrace, and soft-FPU emulation. In this source tree it supports the lower kernel substrate that a Ceph client relies on for block and network I/O, memory management, process ABI, synchronization, and platform boot.

### Risks
Lazy ownership, FR mode, exception, or emulation bugs leak or corrupt userspace FP state. Additional common risks are configuration-specific build gaps, endian or address-width assumptions, stale ABI constants, missing barriers around CPU/MMIO state, and weak test coverage for older MIPS boards.

### Test Signals
Cross-build representative MIPS 32-bit, 64-bit, endian, platform, and feature configurations that include this header. Boot the relevant board or emulator when available; exercise the named subsystem with interrupt, DMA, MMU, firmware, ABI, tracing, KVM, or device-driver selftests; inspect generated assembly for inline barrier/atomic/MMIO helpers where applicable.
