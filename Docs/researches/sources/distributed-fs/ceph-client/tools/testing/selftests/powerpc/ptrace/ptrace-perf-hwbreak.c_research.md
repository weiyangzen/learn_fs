# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-perf-hwbreak.c

## Purpose
`ptrace-perf-hwbreak.c` tests interactions between ptrace watchpoints and perf breakpoint counters on the same child, especially priority and instruction-resume semantics when both mechanisms watch the same or adjacent loads.

## Important APIs, Types, and Functions
Important helpers are syscall wrappers for ptrace, `ptrace_getreg_pc()`, `ptrace_setreg_pc()`, `perf_event_open()`, `perf_watchpoint_open()`, `perf_read_counter()`, `ppc_ptrace_init_breakpoint()`, `check_watchpoints()`, `ptrace_fork_child()`, `same_watch_addr_test()`, `perf_then_ptrace_test()`, and `main()`. It also consumes assembly labels from `ptrace-perf-asm.S`.

## Control Flow and State
The parent forks a stopped tracee, checks that at least two watchpoints are available, programs ptrace and perf watchpoints, then continues or single-steps child assembly helpers. For the same-address case, ptrace should trap before the load and perf should not count until the instruction actually executes. For the perf-then-ptrace case, the test validates ordering across consecutive load instructions and may adjust the child PC to known labels. State includes child PC/registers, perf fd counts, ptrace breakpoint handles, watched values, and wait statuses.

## Dependencies and Integration Points
It integrates perf `PERF_TYPE_BREAKPOINT`, powerpc ptrace hardware debug UAPI, assembly helper labels, waitpid signal control, and kselftest assertions.

## Risks and Test Signals
Risks are PC-label mismatch with assembly, ptrace/perf semantic changes, and hardware lacking multiple watchpoints. Passing signals show ptrace before-execute priority and perf after-execute counting remain coherent when both subsystems target nearby data accesses.
