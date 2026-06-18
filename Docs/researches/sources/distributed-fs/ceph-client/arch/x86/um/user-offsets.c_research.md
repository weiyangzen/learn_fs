<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/user-offsets.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/user-offsets.c

## Purpose
`user-offsets.c` generates host register and syscall constants for UML user-space helper code.

## Important APIs, types, and functions
`foo()` emits `HOST_*`, `UM_FRAME_SIZE`, poll constants, and mmap protection constants through kbuild `DEFINE`/`COMMENT`.

## Control flow
Kbuild compiles to assembly and converts the definitions into `include/generated/user_constants.h`, shared by sysdep ptrace/stub code.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/user-offsets.c -->
