# sources/distributed-fs/ceph-client/net/ipv6/netfilter/nf_conntrack_reasm.c

Purpose: Supplies IPv6 fragment reassembly for netfilter connection tracking and defragmentation users. It is parallel to the core IPv6 reassembly path but uses a netfilter-specific fragment cache, user keys, and sysctls under `net/netfilter`.

Important APIs, types, and functions: `nf_frags` is the module-wide `inet_frags` cache. `nf_frag_pernet()` retrieves per-net `struct nft_ct_frag6_pernet`. `nf_ct_frag6_gather()` is the exported entry point used by defrag hooks. Internal helpers include `fq_find()`, `nf_ct_frag6_queue()`, `nf_ct_frag6_reasm()`, and `find_prev_fhdr()`. Lifecycle exports are `nf_ct_frag6_init()` and `nf_ct_frag6_cleanup()`. Optional sysctls expose timeout/low/high thresholds.

Control flow: `nf_ct_frag6_gather()` ignores jumbo payloads, locates the fragment header and previous next-header field, rejects first fragments missing complete upper-layer headers, pulls the fragment header, and finds/creates a keyed queue. With the queue lock held, `nf_ct_frag6_queue()` validates offset/end, ECN, checksum state, last-fragment consistency, 8-byte alignment, and overlap/duplicate conditions before inserting into the generic fragment tree. When first and last fragments are present and `meat == len`, `nf_ct_frag6_reasm()` kills the queue, validates combined ECN, removes the fragment header, shifts headers, finishes generic reassembly, updates payload length/DS field/fragment metadata, and returns the completed skb.

State and persistence: Per-net fragment directory state stores live queues, memory thresholds, timeout, and sysctl header. Each queue tracks source/destination/id/user/iif, length, meat, ECN bits, max size, nhoffset, timestamps, and fragments. State is in-memory and timeout-driven only.

Dependencies and integration: Uses generic `inet_frags`, IPv6 fragment helpers, net namespace generic storage, RCU, queue spinlocks, sysctl, checksum helpers, and `IP6CB` metadata. It integrates through `nf_ct_frag6_gather()` with `nf_defrag_ipv6_hooks.c`.

Risks and test signals: High-risk areas include fragment overlap handling, first-fragment upper-layer truncation, ECN merge failure, checksum adjustment, queue memory accounting, and correct preservation/removal of extension headers. Tests should include duplicate fragments, overlaps, misaligned non-final fragments, oversize payloads, timeout expiry, link-local/multicast iif keying, conntrack zones/users, and successful reassembly feeding conntrack.
