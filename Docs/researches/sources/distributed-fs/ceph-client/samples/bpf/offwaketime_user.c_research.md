# sources/distributed-fs/ceph-client/samples/bpf/offwaketime_user.c

Purpose: userspace loader and stack printer for off-wake-time tracing.

Important APIs/types/functions: map FDs, `print_ksym`, `struct key_t`, `print_stack`, `print_stacks`, signal handler `int_exit`, and `main` with libbpf load/attach.

Control flow: loads and attaches BPF programs, sleeps for a delay loop, then iterates aggregate count map and stack map to print waker and target stacks with symbol names.

State and persistence: BPF maps store counts/stacks; process uses trace helper symbol tables for printing.

Dependencies and integration: pairs with `offwaketime.bpf.c` and `trace_helpers`, requires kallsyms access, stack traces, and BPF privileges.

Risks: symbol resolution may be unavailable under restricted kallsyms settings. Stack IDs can be missing or stale. Signal handler exits directly after printing.

Test signals: run during blocked workload, confirm stack output contains waker and target frames and counts increase.
