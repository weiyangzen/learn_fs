# sources/distributed-fs/ceph-client/net/ipv6/inet6_hashtables.c

Purpose: implements IPv6 transport socket hash operations for established lookups, listener selection, reuseport, BPF sk_lookup redirection, and active-connect port hashing.

Important APIs, types, and functions: `inet6_init_ehash_secret()`, `inet6_ehashfn()`, `__inet6_lookup_established()`, `inet6_lookup_listener()`, `inet6_lookup()`, `inet6_lookup_reuseport()`, `inet6_lookup_run_sk_lookup()`, and `inet6_hash_connect()`. Internal helpers include `compute_score()`, `inet6_lhash2_lookup()`, `__inet6_check_established()`, and `inet6_sk_port_offset()`.

Control flow: established lookup computes the ehash over local/remote IPv6 addresses, ports, and net hash mix; it walks the nulls hlist under RCU, validates `inet6_match()`, takes a ref, and revalidates after ref acquisition. Listener lookup first gives BPF sk_lookup a chance to redirect, then searches address-specific and wildcard listener buckets, choosing the highest score for address/device/CPU affinity and optionally applying SO_REUSEPORT selection. Active connect initializes hash secrets, derives an ephemeral-port offset from secure IPv6 port hashing, precomputes the zero-local-port hash, and delegates range probing to `__inet_hash_connect()`.

State and persistence: global hash secrets are initialized once. Socket state lives in shared inet hashinfo tables owned by the TCP death row. The check-established path mutates `inet_num`, `inet_sport`, `sk_hash`, the ehash bucket, timewait recycling stats, and protocol in-use counters under bucket locks.

Dependencies and integration points: relies on `net->ipv4.tcp_death_row.hashinfo` for IPv6 TCP hash tables, reuseport core, BPF sk_lookup, secure sequence/port hashing, l3mdev-bound-device matching, and TCP timewait uniqueness logic.

Risks: nulls-list restarts are required when concurrent mutations move entries. RCU-only duplicate checks in `__inet6_check_established()` are intentionally advisory and must be followed by locked insertion. Listener scoring must keep wildcard fallback and bound-device semantics compatible with IPv4 behavior. Reuseport selection requires stable hash parity with UDP/TCP fallback paths.

Test signals: high-concurrency connect bind collisions, TIME_WAIT reuse, SO_REUSEPORT distribution with BPF and without BPF, VRF/l3mdev-bound sockets, wildcard vs address-specific listeners, and RCU/hash debug tests.
