<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/stub_32.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/stub_32.h

## Purpose
`stub_32.h` defines syscall-stub support used by UML code executing in a traced host process.

## Important APIs, types, and functions
It provides `stub_syscall0..6`, `trap_myself()`, `get_stub_data()`, `stub_start()`, arch stub data, and seccomp restore helpers depending on bitness.

## Control flow
Stub code issues raw host syscalls, stores per-arch sync state, obtains its adjacent stub-data page, and traps back to the UML monitor when needed.

## State and persistence behavior
State is either none for macros/layout headers or per-stub/per-register data structures declared here and stored by callers.

## Dependencies and integration points
It depends on generated user constants, host libc/kernel ABI definitions, and bitness-specific x86 register layouts.

## Risks and edge cases
The main risk is layout mismatch with assembly, host ptrace, or signal-frame structures, which can break context restore or fault recovery.

## Test signals
Signals are UML boot, syscall-stub execution, ptrace/register tests, signal/fault handling, and generated-offset rebuilds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/shared/sysdep/stub_32.h -->
