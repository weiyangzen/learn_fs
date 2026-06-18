<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/os-Linux/mcontext.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/os-Linux/mcontext.c

## Purpose
`mcontext.c` translates between host signal `mcontext_t` frames and UML `uml_pt_regs`, including floating-point/XSTATE and stub state.

## Important APIs, types, and functions
Important APIs are `get_regs_from_mc()`, `mc_set_rip()`, `get_mc_from_regs()`, `get_stub_state()`, and `set_stub_state()`.

## Control flow
Signal/stub paths copy GPRs between host ucontext and UML register arrays, locate FP state on the stub signal stack, copy XSTATE with size checks, convert i387/fxsave on 32-bit, and mark FS/GS base sync on 64-bit.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/os-Linux/mcontext.c -->
