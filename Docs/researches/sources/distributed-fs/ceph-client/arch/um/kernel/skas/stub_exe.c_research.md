# sources/distributed-fs/ceph-client/arch/um/kernel/skas/stub_exe.c

## Purpose
Defines the tiny executable image launched as `uml-userspace`. It maps the syscall stub code/data at fixed guest addresses, installs signal handling, optionally installs a seccomp filter, and then stops/traps for kernel control.

## Important APIs, Types, and Functions
`real_init()` reads `stub_init_data` from stdin, maps stub code and data with fixed shared mappings, sets alternate signal stack, registers SIGSEGV or seccomp signal handlers, installs seccomp BPF when requested, or uses `PTRACE_TRACEME` plus SIGSTOP in ptrace mode. `_start()` adjusts the startup stack through `stub_start(real_init)`.

## Control Flow, State, and Persistence
The executable starts with raw syscalls only. It inherits a socket/stdin for init data and, in seccomp mode, retains FD 0 for FD passing. It persists as the long-lived host process backing a UML mm context.

## Dependencies and Integration Points
Uses generated asm offsets, raw syscall helpers, `stub-data.h`, `sysdep/stub.h`, seccomp BPF constants, and fixed layout constants such as `STUB_START`. It is linked by the SKAS Makefile and embedded by `stub_exe_embed.S`.

## Risks and Test Signals
Risks are wrong fixed mappings, unsupported syscalls in the BPF allowlist, close-range incompatibility, bad signal-restorer setup, and insecure seccomp policy. Test stub startup in ptrace/seccomp modes, old kernels/libcs, i386/x86_64, noexec tempdir fallback, and signal fault paths.
