# sources/distributed-fs/ceph-client/samples/bpf/syscall_tp_kern.c

Purpose: BPF tracepoint sample counting `open`, `openat`, and `openat2` syscall enter/exit events.

Important APIs/types/functions: syscall tracepoint argument structs, two BPF maps for counts, helper `count`, and handlers for `sys_enter_open`, `sys_enter_openat`, `sys_enter_openat2`, `sys_exit_open`, `sys_exit_openat`, and `sys_exit_openat2`.

Control flow: each handler calls `count` on the appropriate map, which increments a shared counter key for enter or exit events.

State and persistence: counts live in BPF maps while attached.

Dependencies and integration: loaded by `syscall_tp_user.c`, depends on syscall tracepoints and BPF tracepoint support.

Risks: tracepoint struct layouts must match kernel format. Some architectures may not expose all syscall variants the same way.

Test signals: user program runs test opens and verifies map counts match expected enter/exit counts.
