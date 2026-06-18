# sources/distributed-fs/ceph-client/include/net/dst_ops.h

Read `sources/distributed-fs/ceph-client/include/net/dst_ops.h` completely for this pass (73 lines, 2116 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/dst_ops.h_research.md`.

Purpose: declares the protocol-specific operation table backing `dst_entry` objects and small helpers for per-protocol destination cache accounting.

Important APIs/types/functions: `struct dst_ops` contains address family, GC threshold, callbacks for GC, route validation, default advertised MSS, MTU, metrics copy-on-write, destroy, device ifdown, negative advice, link failure, PMTU update, redirect, local output, neighbor lookup, neighbor confirmation, the dst slab cache, and a per-CPU entry counter. Helpers are `dst_entries_get_fast()`, `dst_entries_get_slow()`, `dst_entries_add()`, `dst_entries_init()`, `dst_entries_destroy()`, plus `DST_PERCPU_COUNTER_BATCH`.

Control flow: IPv4, IPv6, blackhole, and other route implementations fill a `dst_ops` table. Generic dst code delegates route validation, output properties, metrics COW, teardown, PMTU, redirect, and neighbor lookup through these callbacks. Allocation/destruction paths update the per-CPU entry counter.

State and persistence: `dst_ops` instances are usually per protocol/netns static or long-lived runtime objects. The per-CPU counter tracks approximate/summed live dst entries; the kmem cache pointer owns allocation backing.

Dependencies and integration points: depends on percpu counters, cache alignment, netdevice, skb, sock, and net namespace types. It is paired with `dst.h` and IPv4/IPv6 route implementations.

Risks: missing callbacks can crash callers that do not null-check, while optional callbacks must be checked by helpers. Counter initialization/destruction must match netns/protocol lifecycle. `dst_entries_get_fast()` is approximate; policy decisions requiring exact counts should use the slow sum. Callback semantics must match protocol expectations for PMTU/redirect/neigh lookup.

Test signals: protocol route allocation/destruction counter tests, callback coverage for IPv4/IPv6/blackhole dsts, GC threshold behavior, metrics COW, PMTU/redirect callbacks, neighbor lookup error normalization, and netns teardown with percpu counter destruction.
