<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/vdso/um_vdso.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/vdso/um_vdso.c

## Purpose
`um_vdso.c` implements UML vDSO time entry points as simple syscall trampolines so UML can trap them normally.

## Important APIs, types, and functions
Exports `__vdso_clock_gettime`, `clock_gettime` alias, `__vdso_gettimeofday`, `gettimeofday` alias, `__vdso_time`, and `time` alias.

## Control flow
Each function loads the corresponding syscall number and arguments into x86-64 syscall registers and executes `syscall`, returning the host/UML syscall result.

## State and persistence behavior
No persistent state exists; calls operate on user-provided time buffers.

## Dependencies and integration points
It depends on x86-64 syscall ABI, `asm/unistd.h`, and vDSO linker version exports.

## Risks and edge cases
Because these run in userspace, profiling/stack protector dependencies must be absent. Register clobbers must match syscall ABI.

## Test signals
Signals are userland calls to `clock_gettime`, `gettimeofday`, and `time` through the vDSO and fallback syscall behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/vdso/um_vdso.c -->
