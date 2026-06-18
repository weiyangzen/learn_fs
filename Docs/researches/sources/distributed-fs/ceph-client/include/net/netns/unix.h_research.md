# sources/distributed-fs/ceph-client/include/net/netns/unix.h

Purpose: Defines per-network-namespace AF_UNIX state.

Important APIs/types/functions: `struct unix_table` stores spinlock and bucket arrays. `struct netns_unix` embeds the table, `sysctl_max_dgram_qlen`, and sysctl header `ctl`.

Control flow: AF_UNIX bind/connect/listen paths hash sockets into namespace-local buckets protected by bucket locks. Sysctl controls datagram queue length, and cleanup/proc paths consult the same table.

State and persistence: Runtime per-net UNIX socket hash table and datagram queue sysctl.

Dependencies/integration: Depends on AF_UNIX socket core, procfs, namespace lifecycle, and socket garbage collection.

Risks/test signals: Test abstract namespace isolation, hash bucket lock allocation/cleanup, datagram queue sysctl, garbage collection across namespaces, and bind collisions.
