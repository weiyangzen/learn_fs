<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/vdso_restorer.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/vdso_restorer.c

## Purpose

`vdso_restorer.c` tests 32-bit signal handling when user code supplies `sa_restorer == NULL`, requesting a kernel-provided vDSO signal restorer. It preserves an old ABI that modern libc rarely exercises.

## Important APIs, Types, and Functions

The file open-codes `struct real_sigaction` to avoid libc wrapper behavior. It resolves `linux-vdso.so.1` or `linux-gate.so.1` with `dlopen()`. It installs handlers through raw `SYS_rt_sigaction` and `SYS_sigaction` syscalls, then raises `SIGUSR1`. `handler_with_siginfo()` and `handler_without_siginfo()` set `handler_called`.

## Control Flow and State

`main()` skips if the vDSO cannot be found, installs an SA_SIGINFO action with no restorer, raises the signal, validates the handler returned, then repeats for a non-SA_SIGINFO handler. State is just the volatile `handler_called` flag and error count.

## Dependencies and Integration Points

It depends on 32-bit signal ABI, kernel vDSO restorer support, raw signal syscalls, and dynamic linker visibility of the vDSO. It is not relevant for native 64-bit userspace, which does not support this ABI.

## Risks and Test Signals

Risks include kernel rejection of NULL restorer, failure to choose vDSO restorer, or broken return from either handler style. Passing output confirms both handler forms execute and return successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/vdso_restorer.c -->
