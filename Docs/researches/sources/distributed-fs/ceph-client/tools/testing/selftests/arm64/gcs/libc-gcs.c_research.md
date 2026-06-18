<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/libc-gcs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/libc-gcs.c

Purpose: libc-based GCS harness test covering calls, threads, ptrace access, mapped shadow stacks, stack switching, overflow faults, invalid mapping sizes, and invalid mprotect.

Important APIs and functions: `gcs_recurse` prevents tail-call optimization and creates GCS entries. Tests include `can_call_function`, `gcs_enabled_thread`, `gcs_find_terminator`, `ptrace_read_write`, map fixture tests `stack_capped`, `stack_terminated`, `not_writeable`, `stack_switch`, `stack_overflow`, invalid map fixture `do_map`, and invalid mprotect tests. Uses `map_shadow_stack`, `gcsss1/gcsss2`, `PTRACE_GETREGSET NT_ARM_GCS`, `PTRACE_PEEKDATA/POKEDATA`, `process_vm_readv`, pthreads, and mprotect.

Control flow: main skips if no GCS, forcibly enables GCS using raw syscall if not already enabled, then exits through the kselftest harness to avoid returning through libc in an unsupported GCS configuration. Harness fixtures map stacks at multiple sizes/flags and validate token/marker behavior and pivot semantics.

State and persistence: process GCS state, pthread child state, traced child GCS memory, and temporary mapped shadow stacks. No files.

Dependencies and integration: requires libc/pthread, `gcs-util.h`, kselftest harness, and kernel support for GCS ptrace/mapping APIs.

Risks: enabling GCS in a libc process is delicate when libc lacks GCS awareness; the code uses raw syscalls and `exit` to reduce return-path hazards. The fixture variant `s3k_marker` actually uses 4 KiB, likely a label typo.

Test signals: harness assertions and expected SIGSEGV tests validate read/write protections, stack switching, overflow faulting, invalid map rejection, and ptrace visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/gcs/libc-gcs.c -->
