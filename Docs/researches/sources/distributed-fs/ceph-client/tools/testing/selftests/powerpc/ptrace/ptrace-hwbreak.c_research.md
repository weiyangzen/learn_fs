# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-hwbreak.c

## Purpose
`ptrace-hwbreak.c` tests ptrace-managed powerpc hardware breakpoints using both legacy `PTRACE_SET_DEBUGREG` and `PPC_PTRACE_SETHWDEBUG`. It covers exact and range watchpoints, aligned and unaligned ranges, kernel accesses to user buffers, DAWR maximum length, and multiple watchpoints.

## Important APIs, Types, and Functions
Important routines are `get_dbginfo()`, `dawr_present()`, `write_var()`, `read_var()`, `test_workload()`, `check_success()`, `ptrace_set_debugreg()`, `ptrace_sethwdebug()`, `ptrace_delhwdebug()`, `get_ppc_hw_breakpoint()`, many `test_sethwdebug_*()` cases, `ptrace_hwbreak()`, and `main()`.

## Control Flow and State
The child calls `PTRACE_TRACEME`, stops for the parent, then executes a scripted sequence of watched loads/stores. The parent programs each watchpoint before continuing the child, waits for SIGTRAP, validates `siginfo.si_addr` against the expected watched range, single-steps non-8xx children past before-execute watchpoints, deletes handles when needed, and advances to the next case. State includes watched globals/arrays, DAWR feature flags, ptrace handles, signal status, and child register execution state.

## Dependencies and Integration Points
It integrates with powerpc ptrace debug UAPI, DAWR/DABR hardware, syscall `getcwd` for kernel access to userspace, signal delivery, and kselftest macros.

## Risks and Test Signals
Risks include randomized accesses hiding edge failures, hardware-specific before/after execute behavior, incorrect 8xx special handling, and watchpoint slot exhaustion. A pass means ptrace reports SIGTRAP at addresses within expected aligned ranges for every watchpoint mode.
