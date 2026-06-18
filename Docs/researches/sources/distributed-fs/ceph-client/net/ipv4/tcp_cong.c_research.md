# sources/distributed-fs/ceph-client/net/ipv4/tcp_cong.c

## Purpose
`tcp_cong.c` is the core pluggable TCP congestion-control registry and the built-in Reno implementation. It manages registration, lookup, default and allowed algorithms, socket assignment and reinitialization, ECN negotiation for algorithms that need it, and shared cwnd growth helpers used by many modules and BPF struct_ops.

## Important APIs, Types, And Functions
The global registry is `tcp_cong_list`, protected for writes by `tcp_cong_list_lock` and read under RCU. Exported APIs include `tcp_register_congestion_control()`, `tcp_unregister_congestion_control()`, `tcp_update_congestion_control()`, `tcp_ca_get_key_by_name()`, `tcp_ca_get_name_by_key()`, `tcp_assign_congestion_control()`, `tcp_init_congestion_control()`, `tcp_cleanup_congestion_control()`, `tcp_set_default_congestion_control()`, `tcp_set_allowed_congestion_control()`, and `tcp_set_congestion_control()`. The shared kfunc/helpers are `tcp_slow_start()`, `tcp_cong_avoid_ai()`, `tcp_reno_cong_avoid()`, `tcp_reno_ssthresh()`, and `tcp_reno_undo_cwnd()`. `tcp_reno` is always non-restricted.

## Control Flow
Algorithms register by validating required callbacks, deriving a jhash key from the name, checking uniqueness, and appending to the RCU list. Socket creation uses `tcp_assign_congestion_control()` to take the netns default with module/BPF refcounting and zero private state. `tcp_init_congestion_control()` calls algorithm `.init` and sets ECN transmit mode. Switching a socket with `tcp_set_congestion_control()` checks destination lock, permissions, non-restricted flags, optional autoload, and module refs, then calls `tcp_reinit_congestion_control()`. Sysctl default changes use `xchg()` on `net->ipv4.tcp_congestion_control`; allowed-list changes parse and mark `TCP_CONG_NON_RESTRICTED`.

## State, Persistence, Dependencies, And Integration
Registry state is global RCU list membership and per-net default pointers. Per-socket state includes selected ops, private `icsk_ca_priv`, initialized flag, and user-set marker. The file depends on module loading, jhash, RCU, BPF module helpers, ECN helpers, tracepoints, and net namespace TCP settings. It is the integration point for all congestion-control modules in this group.

## Risks And Test Signals
Risks include duplicate key/name handling, module refcount lifetime, switching algorithms while initialized, restricted algorithm exposure outside `init_net`, RCU update ordering, and ECN state mismatches. Tests should register/unregister modules, autoload by name, set default and allowed algorithms, switch live sockets, verify cleanup `.release`, validate Reno cwnd behavior, verify kfunc availability for struct_ops, and ensure `TCP_CONG_NEEDS_ECN` triggers ECT negotiation.
