# sources/distributed-fs/ceph-client/arch/arm64/include/asm/percpu.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/percpu.h -->
## sources/distributed-fs/ceph-client/arch/arm64/include/asm/percpu.h

### Purpose
`percpu.h` implements ARM64 optimized per-CPU accessors using TPIDR-based offsets, hyp/kernel variants, LSE/LLSC operations, and fallback generic per-CPU support.

### Important APIs, Types, And Functions
Exports include `set_my_cpu_offset()`, `__hyp_my_cpu_offset()`, `__kern_my_cpu_offset()`, `__my_cpu_offset`, generated `__percpu_read/write_*`, per-CPU add/and/or/xchg/cmpxchg helpers, `this_cpu_*` operations for 1/2/4/8/128-byte sizes, `__hyp_per_cpu_offset()`, `per_cpu_offset()`, and raw aliases for some configurations.

### Control Flow
Per-CPU operations compute the current CPU base from a system register or hyp offset, then perform inline loads/stores or atomic updates. Alternative/LSE machinery chooses the instruction sequence where supported.

### State, Persistence, And Dependencies
State is per-CPU storage and CPU-local offset registers. It depends on preemption control, `asm/alternative.h`, `cmpxchg`, stack pointer helpers, sysregs, and LSE support.

### Integration Points
Used pervasively by scheduler, counters, locks, networking, KVM host data, and filesystem statistics.

### Risks
Preemption safety is critical: using current-CPU access across migration corrupts another CPU's slot. LSE/LLSC constraints and 128-bit cmpxchg must match CPU support.

### Test Signals
Run percpu selftests, preemption and CPU hotplug stress, KVM hyp per-CPU access tests, and atomic operation stress on LSE/non-LSE hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/include/asm/percpu.h -->
