# sources/distributed-fs/ceph-client/include/linux/restart_block.h

Purpose: this header defines common state used to restart interrupted system calls after signal handling.

Important APIs/types/functions: `enum timespec_type` differentiates native and compat remaining-time pointers. `struct restart_block` stores architecture data, a restart function pointer, and a union for futex wait, nanosleep, and poll restart parameters. It declares `do_no_restart_syscall()`.

Control flow: when an interruptible syscall needs restart, kernel code fills the current task's restart block with operation-specific fields and a function. After signal handling, restart logic invokes `fn(restart_block *)`, which resumes or completes the syscall with saved parameters such as futex addresses, timeout expiry, nanosleep remaining-time pointer, or poll fd list/end time.

State and persistence: restart data persists in the task across return-to-user/signal boundaries. It contains user pointers and absolute expiry times, so it must remain valid only under syscall restart rules.

Dependencies and integration points: depends on compiler/user annotations, time64 types, futex, nanosleep, poll, signal return paths, and architecture syscall restart code.

Risks: stale user pointers, wrong compat/native timespec handling, and timeout recomputation errors can break ABI-visible syscall behavior. Test signals include interrupted `nanosleep`, `poll`, and futex waits under signals, compat 32-bit tests, and restart/no-restart syscall paths.
