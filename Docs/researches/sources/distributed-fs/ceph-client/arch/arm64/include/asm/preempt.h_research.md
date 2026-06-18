# sources/distributed-fs/ceph-client/arch/arm64/include/asm/preempt.h
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/preempt.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm64/include/asm/preempt.h` Defines arm64 preemption-count storage semantics using thread_info fields and a separate need_resched bit encoded in the 64-bit preempt_count word. It is part of the arm64 Linux architecture layer carried under the distributed filesystem Ceph client source tree, so its effect on Ceph is indirect but foundational: page cache, networking, DMA, scheduling, traps, and memory safety all depend on these architecture contracts being correct.

### Important APIs, Types, And Functions
PREEMPT_NEED_RESCHED, PREEMPT_ENABLED, preempt_count(), preempt_count_set(), init_task_preempt_count(), init_idle_preempt_count(), set/clear/test_preempt_need_resched(), __preempt_count_add/sub(), __preempt_count_dec_and_test(), should_resched(), preempt_schedule(), dynamic_preempt_schedule(). The file is 102 lines / 2685 bytes, and its exported surface is primarily an include-time ABI for implementation files and generic kernel subsystems.

### Control Flow
Fast paths read/write current_thread_info()->preempt fields with READ_ONCE/WRITE_ONCE. decrement-and-test updates count only, then rechecks the full word to catch interrupt-side need_resched changes between non-atomic operations.

### State, Persistence, And Dependencies
State is per-task thread_info preempt_count/need_resched. No persistence outside task lifetime. Depends on linux/thread_info.h and scheduler preemption core; used by interrupt, softirq, scheduler, and low-level entry/exit code.

### Integration Points
This header is consumed by arm64 architecture implementation files and generic Linux subsystems rather than by Ceph protocol code directly. It integrates with boot, exception entry, MM, scheduler, KVM, tracing, syscall, signal, CPU feature, or firmware paths as described above, providing the low-level behavior on which higher-level distributed filesystem I/O relies.

### Risks
Non-atomic split-field updates are subtle; endian layout must match assembly; incorrect need_resched polarity can break scheduling or preempt in unsafe regions.

### Test Signals
Run PREEMPT, PREEMPT_DYNAMIC, lockdep, scheduler stress, irq/preempt tracing, and big-endian build coverage.
