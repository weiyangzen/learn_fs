# sources/distributed-fs/ceph-client/include/net/raw.h

Purpose: declares IPv4 raw socket protocol state, hash table, receive/error paths, proc iteration, and socket-specific fields.

Important APIs and types: `struct raw_hashinfo` holds a spinlock and 256 hash buckets. `struct raw_sock` embeds `inet_sock` first and adds ICMP filter, multicast routing table, and NUMA drop counters. APIs match sockets, abort, deliver ICMP errors, local-deliver raw packets, receive skbs, hash/unhash sockets, initialize raw support, and expose proc iteration. Helpers compute netns/protocol hash and bound-device matching with L3 master accept behavior.

Control flow: raw sockets are hashed by protocol/netns, incoming IP packets are delivered to matching sockets, ICMP errors are dispatched, and procfs walks buckets.

State and persistence: per-netns/global hash table membership, socket filter/table/drop counters, and proc iterator state are runtime only.

Dependencies and integration points: depends on inet sockets, protocol dispatcher, netns hashing, ICMP, hash functions, procfs, and optional L3 master devices.

Risks and test signals: risks include hash lock contention, incorrect bound-device match, ICMP filter behavior, raw socket teardown races, and proc iteration while unhashing. Test raw socket bind/send/receive, ICMP errors, L3 master sysctl, multicast table field, proc output, and namespace isolation.
