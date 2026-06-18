<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/os-Linux/registers.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/os-Linux/registers.c

## Purpose
`registers.c` handles host ptrace register-set discovery and floating-point register get/set for UML traced processes.

## Important APIs, types, and functions
`get_fp_registers()`, `put_fp_registers()`, `arch_init_registers()`, `get_thread_reg()`, globals `ptrace_regset` and `host_fp_size`.

## Control flow
Initialization probes `NT_X86_XSTATE`, falls back to legacy FP regsets, records host FP size, and later uses `PTRACE_GETREGSET`/`SETREGSET`.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/os-Linux/registers.c -->
