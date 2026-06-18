# sources/distributed-fs/ceph-client/arch/riscv/kernel/kernel_mode_vector.c

Purpose: Provides guarded kernel-mode vector access for RISC-V vector instructions.

Important APIs/types/functions: Implements vector begin/end helpers, vector nesting/ownership handling, preemption hooks, and state save/restore interactions for kernel vector users.

Control flow: A kernel vector user enters a protected section that disables preemption or records nesting, saves any live user vector state as needed, enables VS state, runs vector code, then restores status and nesting state on exit. Optional preemptive vector support coordinates with trap entry/exit.

State and persistence: Temporarily mutates VS bits, per-task vector flags, CPU vector context, and nesting counters. User vector state persists in task structures.

Dependencies and integration points: Depends on RISC-V vector support, `entry.S` vector nesting hooks, scheduler context switching, signal/ptrace vector state, and kernel vector consumers.

Risks and test signals: Incorrect nesting or preemption handling corrupts vector registers across tasks. Test vector user tasks concurrent with kernel vector users, preemption stress, signal delivery with vector state, and configs with/without `CONFIG_RISCV_ISA_V_PREEMPTIVE`.
