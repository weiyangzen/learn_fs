<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/os-Linux/tls.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/os-Linux/tls.c

## Purpose
`os-Linux/tls.c` is the host ptrace/syscall layer for i386 TLS descriptors.

## Important APIs, types, and functions
`check_host_supports_tls()`, `os_set_thread_area()`, and `os_get_thread_area()`.

## Control flow
Boot probes possible TLS GDT minima using `get_thread_area`; runtime ptrace helpers set/get child thread areas by entry number.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/os-Linux/tls.c -->
