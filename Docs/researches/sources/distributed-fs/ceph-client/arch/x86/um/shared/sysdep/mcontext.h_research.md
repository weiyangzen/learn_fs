<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/mcontext.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/mcontext.h

## Purpose
`mcontext.h` declares host mcontext to UML register conversion APIs and fault-info extraction macros.

## Important APIs, types, and functions
It declares `get_regs_from_mc()`, `get_mc_from_regs()`, `get_stub_state()`, `set_stub_state()`, and `GET_FAULTINFO_FROM_MC()`.

## Control flow
Host signal handlers pass `ucontext_t` mcontext into these helpers so UML can save/restore interrupted guest register state.

## State and persistence behavior
State is either none for macros/layout headers or per-stub/per-register data structures declared here and stored by callers.

## Dependencies and integration points
It depends on generated user constants, host libc/kernel ABI definitions, and bitness-specific x86 register layouts.

## Risks and edge cases
The main risk is layout mismatch with assembly, host ptrace, or signal-frame structures, which can break context restore or fault recovery.

## Test signals
Signals are UML boot, syscall-stub execution, ptrace/register tests, signal/fault handling, and generated-offset rebuilds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/mcontext.h -->
