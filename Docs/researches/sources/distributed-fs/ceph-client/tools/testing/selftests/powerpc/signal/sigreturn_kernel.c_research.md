# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/signal/sigreturn_kernel.c

Purpose: tests that sigreturn cannot restore execution to kernel addresses or kernel privilege by modifying signal context.

Important APIs/types/functions: `sigusr1_handler()` rewrites `UCONTEXT_NIA()` and masks `UCONTEXT_MSR()`, `fork_child()` raises the signal in a child, and `expect_segv()` verifies SIGSEGV.

Control flow: the parent installs a SA_SIGINFO handler, then repeatedly forks children with crafted return addresses covering kernel segments, kernel virtual ranges, no-man's land around task limits, and 0xd/0xe/0xf spaces. A second pass also tries clearing `MSR_PR`. A final no-address-change case proves PR clearing alone is blocked without killing normal return.

State and persistence behavior: volatile globals carry the requested NIA and MSR mask into children after fork.

Dependencies and integration points: depends on powerpc context access macros from `utils.h` and standard wait status checks.

Risks and test signals: expected success is child death by SIGSEGV for bad addresses and normal exit for the PR-only case.
