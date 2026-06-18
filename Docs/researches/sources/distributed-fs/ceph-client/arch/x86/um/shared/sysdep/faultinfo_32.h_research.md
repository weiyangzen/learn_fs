<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/faultinfo_32.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/faultinfo_32.h

## Purpose
`faultinfo_32.h` defines or selects x86 UML fault metadata extracted from host traps.

## Important APIs, types, and functions
It provides `struct faultinfo`, `FAULT_WRITE`, `FAULT_ADDRESS`, `SEGV_IS_FIXABLE`, `PTRACE_FULL_FAULTINFO`, and the nofault backtrack macro where bitness-specific.

## Control flow
Signal/ptrace code fills the structure from host trap context; fault handlers inspect it to decide page fault handling and fixups.

## State and persistence behavior
State is either none for macros/layout headers or per-stub/per-register data structures declared here and stored by callers.

## Dependencies and integration points
It depends on generated user constants, host libc/kernel ABI definitions, and bitness-specific x86 register layouts.

## Risks and edge cases
The main risk is layout mismatch with assembly, host ptrace, or signal-frame structures, which can break context restore or fault recovery.

## Test signals
Signals are UML boot, syscall-stub execution, ptrace/register tests, signal/fault handling, and generated-offset rebuilds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/faultinfo_32.h -->
