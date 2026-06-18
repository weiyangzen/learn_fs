<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/nx_stack.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/x86/nx_stack.c

## Purpose

`nx_stack.c` verifies that the userspace stack is non-executable when the binary is linked with a no-exec-stack PT_GNU_STACK policy. It fills stack pages with `INT3` bytes and tries to execute through them, expecting instruction-fetch faults rather than breakpoints.

## Important APIs, Types, and Functions

The assembly helpers `make_stack1()` and `make_stack2()` use `rep stosb` with direction flag changes to paint the stack with `0xcc`. `sigsegv()` drives the state machine by rewriting `RIP/EIP` and `RDI/EDI` in the signal context. `sigtrap()` is the failure path for executable stack pages. `main()` installs SA_SIGINFO handlers, caps `RLIMIT_STACK`, allocates an alternate signal stack with `mmap()` and `sigaltstack()`, and starts the downward stack overwrite.

## Control Flow and State

`test_state` advances from clearing below the current stack pointer, to clearing the other direction, to probing each page, to final success. `stack_min_addr` records the low bound found by the first fault. The test never returns from the first helper in ordinary control flow; it progresses through signal context edits. No persistent state survives the process.

## Dependencies and Integration Points

The test depends on x86 ucontext register layout, signal delivery on an alternate stack, the kernel's stack expansion and NX page protections, and the build system supplying no-exec-stack linking. It is part of the x86 selftest suite.

## Risks and Test Signals

The main risks are executable user stacks, failure to clear DF before signal handlers, stack-limit assumptions, and altstack exhaustion. A pass prints that all stack pages are NX. A `SIGTRAP` means an `INT3` on the stack executed and the test fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/x86/nx_stack.c -->
