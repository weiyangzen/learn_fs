<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/tls.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/tls.h

## Purpose
`tls.h` provides UML x86 sysdep definitions.

## Important APIs, types, and functions
It defines bitness-sensitive typedefs, constants, or externs used by host-facing UML code.

## Control flow
The definitions are selected at compile time and consumed by adjacent sysdep implementation files.

## State and persistence behavior
State is either none for macros/layout headers or per-stub/per-register data structures declared here and stored by callers.

## Dependencies and integration points
It depends on generated user constants, host libc/kernel ABI definitions, and bitness-specific x86 register layouts.

## Risks and edge cases
The main risk is layout mismatch with assembly, host ptrace, or signal-frame structures, which can break context restore or fault recovery.

## Test signals
Signals are UML boot, syscall-stub execution, ptrace/register tests, signal/fault handling, and generated-offset rebuilds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/tls.h -->
