<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/processor_64.h -->
# sources/distributed-fs/ceph-client/arch/x86/um/asm/processor_64.h

## Purpose
`processor_64.h` defines the smaller 64-bit UML architecture thread state.

## Important APIs, types, and functions
It provides `struct arch_thread`, `INIT_ARCH_THREAD`, `STACKSLOTS_PER_LINE`, empty `arch_flush_thread()`/`arch_copy_thread()`, and inline `current_sp()`/`current_bp()`.

## Control flow
64-bit FS/GS base state lives in the saved ptrace register array, so flush/copy hooks do not need TLS descriptor management.

## State and persistence behavior
Persistent per-task state is debug registers, sequence number, and last fault info.

## Dependencies and integration points
It depends on `struct faultinfo` and register-offset definitions used elsewhere.

## Risks and edge cases
The main risk is assuming no extra per-thread x86 state needs copy/flush as host ABI evolves.

## Test signals
Signals are 64-bit context-switch, arch_prctl, and ptrace tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/asm/processor_64.h -->
