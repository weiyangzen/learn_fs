# sources/distributed-fs/ceph-client/arch/parisc/include/asm/switch_to.h

Purpose: defines the PA-RISC scheduler context-switch wrapper.

Important APIs/types/functions: declares `_switch_to(prev, next)` and defines `switch_to(prev, next, last)` to call the low-level implementation and return the previous task.

Control flow: the scheduler invokes `switch_to`; assembly/C low-level code saves current callee-saved state, loads next task state, and returns with `last` set.

State and persistence: task register state persists in `thread_struct` and kernel stacks. Dependencies and integration: scheduler core, processor/thread layout, and low-level context-switch assembly.

Risks and test signals: register-save mismatches corrupt tasks. Test scheduler stress, fork/exit loops, preemption, and FP/register preservation tests.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
