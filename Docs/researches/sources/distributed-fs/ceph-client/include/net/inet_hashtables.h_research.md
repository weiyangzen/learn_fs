# sources/distributed-fs/ceph-client/include/net/inet_hashtables.h

Purpose: defines IPv4/common INET bind, listen, established, and connect hash infrastructure for TCP/UDP-like sockets.

Important APIs/types: hash structures include `inet_ehash_bucket`, `inet_bind_bucket`, `inet_bind2_bucket`, bind hash buckets, listener buckets, and `inet_hashinfo`. Helpers compute bind and port/address hashes, allocate/free per-net hashinfo, create/destroy/find bind buckets, decide when bhash2 applies, update/reset bound source address, bind/hash/unhash sockets, inherit ports, and look up established/listener sockets. Lookup helpers include skb stealing, reuseport lookup, BPF sk_lookup, combined port/address macros, and `inet_match()`.

Control flow and state: bind inserts sockets into local-port and optionally port/address tables, with fastreuse flags to avoid expensive scans. Receive lookup tries established sockets, then listeners, with special handling for attached skb sockets and reuseport. Connect chooses ephemeral ports and checks time-wait conflicts through hash callbacks. Persistent state is in hash tables, buckets, socket nodes, refcounts, and RCU/nulls lists.

Dependencies and integration: depends on inet connection sock, sock, route, IP, TCP states, refcounting, byteorder, per-net hash secrets, BPF, and reuseport.

Risks: hash/list/refcount correctness is critical for socket demux and port reuse. Tests should cover bind conflict rules, bhash2 source-specific binds, wildcard listeners, reuseport, skb-steal, TCP_NEW_SYN_RECV/TIME_WAIT transitions, port inheritance, namespace isolation, and concurrent hash/unhash.
