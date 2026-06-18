## sources/distributed-fs/ceph-client/arch/arm64/kernel/sys_compat.c

### Purpose
`sys_compat.c` handles ARM-private compat syscalls that are not ordinary table entries, chiefly cache flush and TLS setup for AArch32 tasks.

### Important APIs, Types, And Functions
Important functions are `compat_arm_syscall`, `do_compat_cache_op`, and `__do_compat_cache_op`. It handles `__ARM_NR_compat_cacheflush`, `__ARM_NR_compat_set_tls`, and private syscall-number fallback.

### Control Flow
Cache flush validates range ordering, flags, and userspace accessibility, then cleans/invalidates user cache lines in page-sized chunks with rescheduling and fatal-signal checks. If erratum 1542419 applies, it performs an inner-shareable TLB invalidation using a reserved ASID before cache maintenance. TLS setup records the value in `current->thread.uw.tp_value`, uses a barrier against context-switch corruption, and writes `TPIDRRO_EL0`. Unknown private calls below the compat private end return `-ENOSYS`; others are treated as illegal instructions.

### State, Persistence, And Dependencies
State includes current task TLS fields, `TPIDRRO_EL0`, cache/TLB effects, and current fault/signal state. There is no persistent storage.

### Integration Points
Called by `syscall.c` when compat syscall numbers fall outside the table. It depends on cache maintenance, TLB flush, uaccess, scheduler rescheduling, and ARM compat ABI definitions.

### Risks
Cache maintenance over user ranges can fault, be interrupted, or interact with errata. Incorrect TLS ordering can corrupt AArch32 thread-local storage. Private syscall handling must preserve old ARM behavior.

### Test Signals
Run 32-bit cacheflush/TLS ABI tests, JIT self-modifying-code tests, fatal-signal interruption, invalid range/flags tests, and erratum-enabled builds.
