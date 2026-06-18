# sources/distributed-fs/ceph-client/include/net/ipv6_frag.h

Purpose: Defines IPv6 reassembly queue metadata and inline helpers for fragment hash-table integration, expiration, and upper-layer-header truncation checks.

Important APIs/types/functions: `ip6_defrag_users` enumerates local delivery and conntrack bridge/input/output users, with high-offset variants for conntrack namespaces. `frag_queue` embeds `inet_frag_queue` and adds input ifindex, next-header offset, and ECN accumulation. `ip6frag_init`, key/object hash functions, compare function, `ip6frag_expire_frag_queue`, and `ipv6frag_thdr_truncated` are the core helpers.

Control flow: Reassembly creates queues keyed by `frag_v6_compare_key`; rhashtable uses the hash/compare helpers. Expiration locks the queue, marks drop, kills or flushes it, updates IPv6 reassembly failure/timeout stats, and sends ICMPv6 time exceeded only if the first fragment arrived and a head skb can be pulled. Truncation checking walks extension headers and verifies enough bytes exist for TCP/UDP/ICMP or at least one byte for unknown L4.

State and persistence: Fragment queues are in-memory per-frag-directory state with queue flags, locks, refs, ECN, ifindex, and skb trees. Expiration mutates flags and refs and frees the head skb.

Dependencies/integration: Depends on `inet_frag`, IPv6 extension parsing, ICMPv6, addrconf device stats, RCU device lookup, and skb drop reasons.

Risks: Expire path must avoid dead fqdir and hold/release refs correctly; head skb extraction is needed because skb `dev` aliases rbnode storage; ICMP should not be emitted for missing-first-fragment queues. Test signals include fragment timeout with and without first fragment, conntrack defrag users, truncated L4 first fragments, ECN accumulation, dead namespace/fqdir exit, and stats increments.
