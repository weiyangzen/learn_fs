# sources/distributed-fs/ceph-client/net/netfilter/xt_connlimit.c

Purpose: `connlimit` match limits concurrent connections per masked source or destination address, including conntrack zone in the key.

Important APIs/types/functions: `connlimit_mt()`, `connlimit_mt_check()`, `connlimit_mt_destroy()`, `nf_conncount_init()`, `nf_conncount_count_skb()`, and `nf_conncount_destroy()`.

Control flow: check computes family-specific key length, pins conntrack, initializes hidden conncount data, and unwinds on failure. Runtime builds masked IPv4/IPv6 address key plus zone id, counts live connections, hotdrops on count failure, and compares `connections > limit` with optional inversion.

State and persistence: per-rule `nf_conncount_data` and conntrack netns ref. Dependencies include nf_conntrack_count, zones, IPv4/IPv6 headers, x_tables usersize hiding, and conntrack. Risks: count failure hotdrops, key length differences, zone-specific buckets, mask semantics, and private data cleanup. Test signals: IPv4/IPv6 source/dest keys, masks, inversion, zone counts, allocation/count failure, and destroy cleanup.
