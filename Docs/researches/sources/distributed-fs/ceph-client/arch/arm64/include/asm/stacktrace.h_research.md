# sources/distributed-fs/ceph-client/arch/arm64/include/asm/stacktrace.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/stacktrace.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/stacktrace.h` Defines arm64 stack discovery helpers for task, IRQ, overflow, SDEI, and EFI runtime stacks plus backtrace entry points. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
dump_backtrace(), irq_stack_ptr, stackinfo_get_irq(), on_irq_stack(), stackinfo_get_task(), on_task_stack(), on_thread_stack(), overflow_stack, stackinfo_get_overflow(), SDEI stack helpers, efi_rt_stack_top, stackinfo_get_efi(). The file is 120 lines / 2905 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Helpers compute low/high stack bounds from per-CPU pointers or task stack base and call common stackinfo_on_stack. Unwinder code uses these stack_info ranges to validate frame records and legal stack transitions.

### State, Persistence, And Dependencies
Persistent state includes per-CPU IRQ/overflow/SDEI stack pointers and EFI runtime stack top. Header functions are read-only. Depends on percpu, sched/task_stack, llist, memory, pointer_auth, ptrace, sdei, stacktrace/common; integrates with dump_backtrace, perf/ftrace, oops reporting, SDEI, EFI runtime, and overflow handling.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Wrong stack bounds can hide frames or permit invalid unwinds; per-CPU pointer reads must match active stack context.

### Test Signals
Run stacktrace selftests, oops/backtrace paths, IRQ/SDEI/EFI stack unwinds, overflow stack tests, and KASAN stack checks.
