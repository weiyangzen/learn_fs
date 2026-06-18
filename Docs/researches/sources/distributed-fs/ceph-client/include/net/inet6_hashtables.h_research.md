# sources/distributed-fs/ceph-client/include/net/inet6_hashtables.h

Purpose: declares IPv6 socket lookup and hash helpers for established, listener, reuseport, BPF sk_lookup, and skb-steal paths.

Important APIs/types: `inet6_init_ehash_secret()` initializes hash secret. `__inet6_ehashfn()` combines local and foreign IPv6 hashes, ports, and net hash. Lookup APIs include `__inet6_lookup_established()`, `inet6_lookup_reuseport()`, `inet6_lookup_listener()`, `inet6_lookup_run_sk_lookup()`, `__inet6_lookup()`, `__inet6_lookup_skb()`, and `inet6_lookup()`. `inet6_steal_sock()` mirrors IPv4 skb socket stealing and may switch to reuseport. `inet6_match()` validates namespace, addresses, ports, and bound-device constraints.

Control flow and state: receive code first tries an attached skb socket, handles prefetched TCP listeners/UDP closed sockets via reuseport, then falls back to established lookup and listener lookup. Refcount behavior differs for established versus listener sockets and must be tracked by callers.

Dependencies and integration: depends on IPv6 address types, jhash, inet sock, IPv6 helpers, per-net hash secret, reuseport, BPF sk_lookup, and device index functions.

Risks: refcounted and non-refcounted returns are easy to misuse. Bound device and v4-mapped address matching affect isolation. Tests should cover established/listener fallbacks, reuseport selection, BPF sk_lookup overrides, skb stolen sockets, refcount failure, l3mdev/sdif matching, and IPv4-mapped IPv6 sockets.
