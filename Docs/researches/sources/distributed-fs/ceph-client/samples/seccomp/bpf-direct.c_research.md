# sources/distributed-fs/ceph-client/samples/seccomp/bpf-direct.c

## Purpose

This x86-only user-space sample installs a seccomp BPF filter directly with raw `sock_filter` instructions and demonstrates `SECCOMP_RET_TRAP` by emulating writes to stderr in a SIGSYS handler.

## Important APIs, Types, and Functions

Key functions are `install_emulator()`, `emulator()`, `install_filter()`, and `main()`. It uses `sigaction(SIGSYS)`, `ucontext_t` register access, `prctl(PR_SET_NO_NEW_PRIVS)`, `prctl(PR_SET_SECCOMP, SECCOMP_MODE_FILTER)`, BPF macros, `struct seccomp_data` offsets, and raw `syscall()`.

## Control Flow

The program installs a SIGSYS handler, then installs a filter allowing exit, sigreturn, stdin reads, stdout writes, trapping stderr writes, and killing other syscalls. It writes a prompt, reads a name, writes a greeting, and attempts a stderr write. The trap handler checks that the syscall is `write` to stderr, writes `[ERR] ` and the original buffer to stdout, and sets the syscall result register.

## State and Persistence Behavior

Seccomp mode is process-persistent after installation. The signal handler remains installed. No filesystem state is persisted.

## Dependencies and Integration Points

It is compiled only with full behavior on i386/x86_64 and uses architecture-specific syscall argument registers. It depends on seccomp filter support.

## Risks and Edge Cases

Register names and syscall numbers are architecture-sensitive. The handler performs writes from signal context for demonstration and does not fully handle EINTR or partial writes. Unsupported architectures return failure through a stub main.

## Test Signals

Run on x86, enter input, and confirm stderr output is redirected with `[ERR]`. Attempts to add disallowed syscalls should kill the process.
