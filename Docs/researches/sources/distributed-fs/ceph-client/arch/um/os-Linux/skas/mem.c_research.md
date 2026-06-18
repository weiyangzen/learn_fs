# sources/distributed-fs/ceph-client/arch/um/os-Linux/skas/mem.c

## Purpose
Queues and flushes memory-management syscalls that must execute inside a UML userspace helper process, supporting both ptrace and seccomp transport.

## Important APIs, Types, and Functions
`init_syscall_regs()` builds register state to enter `stub_syscall_handler`. `syscall_stub_alloc()`, `map()`, and `unmap()` append mmap/munmap requests, compressing adjacent compatible operations. `syscall_stub_flush()` and `do_syscall_stub()` execute pending requests. `get_stub_fd()` maps host FDs to compact seccomp FD indexes. `syscall_stub_dump_error()` prints failed stub request details.

## Control Flow, State, and Persistence
Per-mm state lives in `mm_id`: `syscall_data_len`, `syscall_fd_num`, and `syscall_fd_map`; request payload lives in shared `stub_data`. Seccomp mode passes FDs over the mm socket and wakes the child via futex; ptrace mode sets registers and continues to the stub trap.

## Dependencies and Integration Points
Called by `kernel/tlb.c` for user mappings and by the SKAS userspace loop before running guest code. Depends on `stub.c`, `os-Linux/skas/process.c`, register templates, and fixed stub layout constants.

## Risks and Test Signals
Risks include queue overflow, compressed mapping offset mistakes, stale error state, FD map exhaustion, and seccomp/ptrace divergence. Test mmap-heavy workloads, mprotect/munmap batching, FD passing, stub failures, and ENOMEM diagnostics.
