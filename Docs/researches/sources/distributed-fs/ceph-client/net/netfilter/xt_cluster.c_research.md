# sources/distributed-fs/ceph-client/net/netfilter/xt_cluster.c

Purpose: `cluster` match distributes conntracked flows across nodes by hashing original source address and checking a node mask.

Important APIs/types/functions: IPv4/IPv6 hash helpers, `xt_cluster_hash()`, `xt_cluster_is_multicast_addr()`, `xt_cluster_mt()`, `xt_cluster_mt_checkentry()`, and destroy.

Control flow: runtime may convert multicast packet type to host for unicast destinations, obtains conntrack or master conntrack, hashes original source address with seed, scales to total nodes, checks node mask, and applies inversion. Check validates total nodes/mask and pins conntrack.

State and persistence: no private dynamic state; conntrack netns ref per rule. Dependencies include nf_conntrack, jhash, IPv4/IPv6 headers, x_tables, and mirrored cluster network behavior. Risks: match mutates `pkt_type`, requires conntrack, node mask bounds, and multicast MAC assumptions. Test signals: IPv4/IPv6 hashing, master conntrack, no-ct false, inversion, invalid node masks, pkt_type correction, and ref cleanup.
