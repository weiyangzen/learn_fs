# sources/distributed-fs/ceph-client/net/core/sock_reuseport.c

## Purpose
This file implements SO_REUSEPORT group storage, socket selection, optional BPF selection, listener shutdown migration support, and BPF program attach/detach for reuseport groups. It optimizes listener lookup by maintaining a compact RCU-visible socket array per group.

## APIs, Types, and Functions
The global state is `reuseport_lock` and `reuseport_ida`. Public APIs include `reuseport_alloc()`, `reuseport_add_sock()`, `reuseport_detach_sock()`, `reuseport_stop_listen_sock()`, `reuseport_select_sock()`, `reuseport_migrate_sock()`, `reuseport_attach_prog()`, `reuseport_detach_prog()`, `reuseport_has_conns_set()`, and `reuseport_update_incoming_cpu()`. Internal helpers manage active and closed sections of the flexible `struct sock_reuseport` socket array, including `__reuseport_add_sock()`, `__reuseport_detach_sock()`, `__reuseport_add_closed_sock()`, `__reuseport_detach_closed_sock()`, `reuseport_grow()`, `reuseport_resurrect()`, and `reuseport_select_sock_by_hash()`.

## Control Flow, State, and Persistence
Groups start with `INIT_SOCKS` slots, grow by doubling up to `U16_MAX`, and are published through each socket's `sk_reuseport_cb` RCU pointer. Active listeners are stored from the front of the array; closed listeners kept for TCP request migration are stored from the back. Shutdown-capable TCP listeners may move from active to closed instead of immediately detaching if `tcp_migrate_req` or a migrate-capable BPF program is active.

Selection takes an RCU snapshot of the group, optionally runs either a `BPF_PROG_TYPE_SK_REUSEPORT` program or classic reuseport filter, and falls back to reciprocal hash selection. Hash selection avoids established sockets and can prefer sockets with `sk_incoming_cpu` matching the current CPU. Migration selection chooses a new listener for established/SYN_RECV children, optionally using BPF with a synthetic skb, then takes a socket reference before returning.

Persistent state includes group IDs, `bind_inany`, `has_conns`, `incoming_cpu`, `synq_overflow_ts`, active/closed counts, and an RCU-protected BPF program pointer. Group storage is freed by `reuseport_free_rcu()` after detaching all sockets and dropping program references.

## Dependencies and Integration
Integrates with TCP listener state, inet bind-conflict logic, BPF reuseport programs, classic socket filters, IDA allocation, RCU, skb cloning/pull/push helpers, per-net TCP migration sysctl, and BPF sockarray detach notifications. `sock.c` calls reuseport detach during socket destruction and exposes `SO_INCOMING_CPU` and reuseport BPF options.

## Risks and Test Signals
Risks include group array races during grow/detach, incorrect active-versus-closed socket accounting, stale BPF program references, migration to an unsuitable listener, CPU-count imbalance for incoming CPU preference, and fallback behavior when BPF returns an invalid index. Test signals include SO_REUSEPORT bind/listen concurrency, BPF selection selftests, TCP request migration tests, shutdown/listen resurrect paths, KCSAN/RCU debug during grow and detach, and CPU-affinity selection tests.
