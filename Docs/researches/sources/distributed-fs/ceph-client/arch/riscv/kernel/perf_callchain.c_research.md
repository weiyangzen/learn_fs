# sources/distributed-fs/ceph-client/arch/riscv/kernel/perf_callchain.c

Purpose: Implements RISC-V perf callchain collection for kernel and user stack samples.

Important APIs/types/functions: Provides perf callchain walkers that collect return addresses from `pt_regs`, frame pointers, and user stack frames.

Control flow: Perf sampling starts from the interrupted PC and frame pointer, records kernel frames while valid, then optionally walks user frames using safe user access until bounds or errors stop the walk.

State and persistence: No persistent file-local state; samples are appended to perf callchain contexts.

Dependencies and integration points: Depends on perf core, RISC-V stacktrace/frame-pointer conventions, user access helpers, and `pt_regs`.

Risks and test signals: Invalid frame pointers, no-frame-pointer builds, and user memory faults can truncate or corrupt callchains. Test perf record/report for kernel/user workloads, signal stacks, compat tasks, and frame-pointer config changes.
