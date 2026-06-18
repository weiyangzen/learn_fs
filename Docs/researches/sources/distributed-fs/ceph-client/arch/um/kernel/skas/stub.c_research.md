# sources/distributed-fs/ceph-client/arch/um/kernel/skas/stub.c

## Purpose
Implements code that is mapped into each UML userspace helper process. It executes queued mmap/munmap operations and, in seccomp mode, handles SIGSYS/SIGALRM/fault signals cooperatively with the UML kernel through shared `stub_data` and futexes.

## Important APIs, Types, and Functions
`syscall_handler()` executes `STUB_SYSCALL_MMAP` and `STUB_SYSCALL_MUNMAP` requests, optionally translating compact FD indexes. `stub_syscall_handler()` runs queued syscalls and traps back to the kernel in ptrace mode. `stub_signal_interrupt()` records signal/mcontext offsets, wakes the kernel, waits for futex handoff, receives FDs, flushes syscalls, and restores architecture state. `stub_signal_restorer()` performs raw `rt_sigreturn`.

## Control Flow, State, and Persistence
State is shared in `struct stub_data`: signal number, siginfo/mcontext offsets, futex state, syscall queue, errors, FD map, restart flag, and arch scratch data. The seccomp path alternates FUTEX_IN_CHILD/FUTEX_IN_KERN ownership until the host updates register/mapping state.

## Dependencies and Integration Points
Built into the `.__syscall_stub` section and mapped by `stub_exe.c`. It relies on raw syscall wrappers, seccomp-filter allowances, `stub-data.h`, and host coordination in `os-Linux/skas/process.c` and `os-Linux/skas/mem.c`.

## Risks and Test Signals
The file explicitly documents security limitations: userspace reaching stub code may access physical memory or interfere with scheduling. Test seccomp and ptrace modes, mmap/munmap batching, FD passing, signal delivery, malicious user IP attempts, and futex wake/wait races.
