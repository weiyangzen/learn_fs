# sources/distributed-fs/ceph-client/include/linux/hidden.h

## Purpose
`hidden.h` pushes GCC symbol visibility to `hidden` for position-independent code. It tells the compiler that external-linkage symbols referenced after this include will be resolved at link time, avoiding Global Offset Table indirections and associated relocation/COW overhead for kernel-style images built with `-fPIC` or older `-fPIE`.

## Important APIs, Types, And Functions
The file has no types or functions. Its single operative statement is `#pragma GCC visibility push(hidden)`.

## Control Flow And State
There is no runtime control flow and no data state. The effect is compile-time and persists until a corresponding visibility pop or end of translation unit. It changes symbol reference generation rather than kernel behavior.

## Dependencies And Integration Points
It depends on GCC-compatible visibility pragmas. It integrates with architecture/kernel build code that compiles position-independent objects but does not want default ELF symbol preemption semantics for internal kernel symbols.

## Risks
Because this is a push pragma, include placement matters. Including it too broadly can hide symbols that must remain externally visible to linkers, loaders, modules, or tooling. Including it without a matching pop in contexts that expect default visibility can create difficult link-time failures.

## Test Signals
Build affected architectures/configurations with PIE/PIC options, inspect symbol visibility and relocations, run module/link tests, and verify no exported symbol unexpectedly becomes hidden.
