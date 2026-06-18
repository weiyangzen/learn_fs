<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/ptrace_64.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/ptrace_64.h

## Purpose
`ptrace_64.h` maps host ptrace register arrays to UML register accessor macros.

## Important APIs, types, and functions
It defines `REGS_*`, `UPT_*`, syscall-argument macros, host register indices, USER-area offsets, and `struct uml_pt_regs` where applicable.

## Control flow
All UML signal/syscall/ptrace paths access saved registers through these macros, with bitness-specific argument order for i386 versus x86-64.

## State and persistence behavior
State is either none for macros/layout headers or per-stub/per-register data structures declared here and stored by callers.

## Dependencies and integration points
It depends on generated user constants, host libc/kernel ABI definitions, and bitness-specific x86 register layouts.

## Risks and edge cases
The main risk is layout mismatch with assembly, host ptrace, or signal-frame structures, which can break context restore or fault recovery.

## Test signals
Signals are UML boot, syscall-stub execution, ptrace/register tests, signal/fault handling, and generated-offset rebuilds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/ptrace_64.h -->
