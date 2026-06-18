# sources/distributed-fs/ceph-client/arch/arm64/include/asm/thread_info.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/thread_info.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/thread_info.h` Defines low-level arm64 thread_info layout and TIF flag assignments consumed by entry assembly, scheduler, preemption, syscall, FP, MTE, SCS, and livepatch paths. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
struct thread_info, thread_saved_pc/sp/fp(), arch_setup_new_exec(), TIF_* flags, _TIF_* masks, _TIF_SYSCALL_WORK, INIT_SCS, INIT_THREAD_INFO(). The file is 130 lines / 4243 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Entry and scheduler code read flags and preempt_count directly from current_thread_info; syscall exit tests _TIF_SYSCALL_WORK; init macros seed foreign FP state, preempt count, and optional SCS pointers.

### State, Persistence, And Dependencies
Persistent per-task state includes flags, saved ttbr0 under SW PAN, preempt_count/need_resched, SCS pointers, MPAM partid/pmg, and cpu id. Depends on compiler, memory, stack_pointer, types; integrates with entry.S, preempt.h, processor.h, scheduler, FP/SVE/SME, MTE, seccomp, ptrace, livepatch, freezer, and MPAM.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Bit numbers and layout are assembly ABI; moving fields or flags breaks entry code. TIF_LAZY_MMU_PENDING coordinates pgtable barriers and must match pgtable.h.

### Test Signals
Build with SCS, SW_TTBR0_PAN, MPAM, compat, MTE, SVE/SME; run syscall-work, preemption, FP context, and entry/exit tests.
