# sources/distributed-fs/ceph-client/arch/s390/include/asm/percpu.h

Purpose: This header implements optimized s390 per-CPU access and atomic this_cpu operations using lowcore `percpu_offset` and architecture instructions.

Important APIs/types/functions: `__my_cpu_offset`, `arch_raw_cpu_ptr()`, simple compare-and-swap based operations, z196+ load-and-op sequences for 4/8-byte add/and/or, return variants, `arch_this_cpu_cmpxchg()`, `this_cpu_cmpxchg128()`, and `arch_this_cpu_xchg()` are defined before generic percpu inclusion.

Control flow: Per-CPU pointer calculation adds lowcore `percpu_offset` with an alternative for relocated lowcore. Mutating this_cpu operations disable preemption, operate on the raw CPU pointer, and re-enable preemption; newer march levels use atomic load-and-op instructions where available.

State and persistence: Persistent state is the per-CPU data area addressed through lowcore. The operations themselves only modify caller-selected per-CPU variables.

Dependencies and integration points: It depends on preemption control, cmpxchg helpers, march feature macros, lowcore, and alternatives.

Risks and test signals: Missing preemption protection could update the wrong CPU variable after migration, and instruction selection must match march baseline. Tests should include per-CPU selftests, 1/2/4/8/128-bit operations, relocated lowcore, preemptible kernels, and older march builds.
