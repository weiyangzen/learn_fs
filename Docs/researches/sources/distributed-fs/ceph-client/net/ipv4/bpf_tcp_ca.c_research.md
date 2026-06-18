# sources/distributed-fs/ceph-client/net/ipv4/bpf_tcp_ca.c

## Purpose
`bpf_tcp_ca.c` enables BPF `struct_ops` programs to implement TCP congestion-control algorithms through the kernel `tcp_congestion_ops` interface.

## Important APIs, types, and functions
The central registration object is `bpf_tcp_congestion_ops`, backed by verifier ops `bpf_tcp_ca_verifier_ops` and CFI stubs in `__bpf_ops_tcp_congestion_ops`. Initialization discovers BTF IDs in `bpf_tcp_ca_init()`. Verifier helpers are `bpf_tcp_ca_is_valid_access()`, `bpf_tcp_ca_btf_struct_access()`, and `bpf_tcp_ca_get_func_proto()`. Struct-ops lifecycle hooks are `bpf_tcp_ca_init_member()`, `bpf_tcp_ca_reg()`, `bpf_tcp_ca_unreg()`, `bpf_tcp_ca_update()`, and `bpf_tcp_ca_validate()`. `bpf_tcp_ca_kfunc_set` exposes selected Reno/congestion helpers as kfuncs. `bpf_tcp_ca_kfunc_init()` registers kfuncs and struct_ops at late init.

## Control flow
During init, the file resolves BTF types for `sock`, `tcp_sock`, and `tcp_congestion_ops`. The verifier promotes safe `struct sock *` BTF context pointers to `tcp_sock *`, limits write access to selected pacing, congestion-window, ECN, app-limited, ACK pending, and CA-private fields, and exposes a constrained helper set. BPF object initialization copies only valid congestion-control flags and a valid BPF object name. Register/update/unregister operations delegate to TCP congestion-control core functions. Runtime callbacks are dispatched through BPF struct_ops, with C stubs present for CFI-compatible function pointers.

## State and persistence
Global runtime state stores BTF type pointers and IDs plus the registered BPF struct_ops descriptor. Individual BPF congestion controls are registered in TCP core state through BPF links; persistence is only as long as the BPF object/link and kernel runtime.

## Dependencies and integration points
The file depends on BPF verifier infrastructure, BTF, BPF struct_ops, BPF socket storage helpers, TCP congestion-control registration, TCP helper kfuncs, and the Makefile condition requiring BPF JIT plus BPF syscall support.

## Risks and invariants
Verifier access restrictions are security-critical because BPF programs receive live TCP socket pointers. `setsockopt()` and `getsockopt()` are intentionally unavailable from `release()` callbacks to prevent resource allocation or surprising side effects during teardown. Field offsets are BTF-driven; struct layout changes must keep allowed writes intentional. TCP core validation remains the final gate before registration.

## Test signals
Selftests should load BPF TCP congestion-control struct_ops, verify registration/update/unregistration, exercise allowed and denied field writes, confirm `sock` pointer promotion to `tcp_sock`, call exposed kfuncs, test helper availability differences for `release()`, use BPF sk storage, and run traffic to confirm callbacks affect congestion behavior.
