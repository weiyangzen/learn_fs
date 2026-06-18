# sources/distributed-fs/ceph-client/tools/include/asm/atomic.h

## Purpose

This header selects an architecture-specific atomic implementation for x86 tools builds or falls back to the generic GCC implementation.

## APIs, State, and Dependencies

On `__i386__` or `__x86_64__`, it includes `../../arch/x86/include/asm/atomic.h`; otherwise it includes `<asm-generic/atomic-gcc.h>`. It defines no APIs directly and has no state.

## Risks and Test Signals

The relative include path must remain valid in the tools source tree. Atomic semantics can differ between architecture and generic paths, so tests should compile atomic users on x86 and at least one fallback architecture.
