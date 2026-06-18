<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/tls_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/um/tls_32.c

## Purpose
`tls_32.c` implements 32-bit UML TLS descriptor management and `set_thread_area`/`get_thread_area` emulation.

## Important APIs, types, and functions
Important functions are `do_set_thread_area()`, `get_free_idx()`, `load_TLS()`, `needs_TLS_update()`, `clear_flushed_tls()`, `arch_switch_tls()`, `arch_set_tls()`, syscall handlers, ptrace thread-area helpers, and `__setup_host_supports_tls()`.

## Control flow
Boot probes host TLS support. Runtime stores guest TLS descriptors in task state, flushes them to host via ptrace or seccomp stub sync on context switch, and services syscalls/ptrace by reading/writing the task TLS array.

## State and persistence behavior
State is per-task saved register/TLS/fault/FP data or host-probed globals where the file defines them; otherwise state is transient local syscall/signal handling data.

## Dependencies and integration points
It depends on UML task/thread structures, generated register offsets, host ptrace/ucontext/syscall APIs, and bitness-specific x86 ABI headers.

## Risks and edge cases
Risks center on ABI drift: wrong register offsets, selector validation, FP/XSTATE sizing, or signal-frame layout can corrupt user state or break ptrace/core dumps.

## Test signals
Signals include UML boot, ptrace selftests, signal delivery/return tests, TLS/arch_prctl tests, syscall-table smoke tests, and core-dump/register inspection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/um/tls_32.c -->
