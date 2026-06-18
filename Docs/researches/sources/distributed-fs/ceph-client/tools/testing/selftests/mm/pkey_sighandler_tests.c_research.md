# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/pkey_sighandler_tests.c

Purpose: exercises Linux signal delivery and return behavior when pkey 0, which normally protects the process stack and libraries, is disabled or when alternate stacks use different pkeys.

Important APIs and functions: `syscall_raw()` and `clone_raw()` avoid glibc when pkey 0 is inaccessible; `pkey_reg_restrictive_default()` builds restrictive register state; handlers record `siginfo`; tests cover SIGSEGV with pkey 0 disabled, inaccessible stacks, alternate-stack delivery, PKRU/POR preservation after SIGUSR1, and sigreturn from an altstack.

Control flow: `main()` skips without pkey support and runs five function-pointer tests. Some tests use detached pthreads; others use raw `clone()` to avoid glibc rseq and stack assumptions.

State and dependencies: shared state is a mutex/condition variable and global `siginfo`; custom stacks and altstacks are transient. Depends on `pkey-helpers.h`, raw architecture syscalls, `pthread`, `sigaltstack`, pkey syscalls, and kselftest TAP.

Risks and test signals: passing signals prove handlers run with a safe initial pkey register and sigreturn restores application state. Fragility comes from syscall calling conventions and stack accessibility assumptions.
