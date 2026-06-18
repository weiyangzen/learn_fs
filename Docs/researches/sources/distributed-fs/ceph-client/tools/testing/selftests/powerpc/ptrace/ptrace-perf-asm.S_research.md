# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-perf-asm.S

## Purpose
`ptrace-perf-asm.S` provides tiny, label-rich child workloads for `ptrace-perf-hwbreak.c`. The labels let the C test reason precisely about watched load instructions and trap points.

## Important APIs, Types, and Functions
It exports `same_watch_addr_child` and `perf_then_ptrace_child`, plus instruction labels such as `same_watch_addr_load`, `same_watch_addr_trap`, `perf_then_ptrace_load1`, `perf_then_ptrace_load2`, and `perf_then_ptrace_trap`.

## Control Flow and State
The first helper loads from one watched address and traps. The second loads from one address, immediately loads from a second address, then traps. State is limited to registers and watched memory values supplied by the C caller.

## Dependencies and Integration Points
It depends on `ppc-asm.h` function macros and is linked with `ptrace-perf-hwbreak.c`. The exported labels are part of the test contract.

## Risks and Test Signals
Risks are instruction scheduling changes, label removal, or ABI mismatch. Test signals are deterministic child PC values at load and trap labels and correct ptrace/perf watchpoint ordering.
