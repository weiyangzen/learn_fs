# sources/distributed-fs/ceph-client/include/net/netns/ipv4.h

Purpose: Defines the large per-network-namespace IPv4 state block, including hot-path TCP/IP sysctls, routing/FIB data, fragment/peer state, multicast routing, ICMP/IGMP controls, local port ranges, and address generation state.

Important APIs/types/functions: Supporting structs include `local_ports`, `ping_group_range`, `inet_timewait_death_row`, optional multipath hash seed, and `udp_tunnel_gro`. `struct netns_ipv4` stores cacheline-grouped TCP/IP sysctls, ICMP limiter state, TCP death row, UDP table, GRO tunnel sockets, sysctl headers, device configs, router-alert chain, FIB rules/tables/hash/info state, multicast routing state, notifier ops, route generation ids, siphash key, address lists, and delayed address checking work.

Control flow: IPv4/TCP/UDP routing and protocol paths read these per-net fields. Sysctl writes update behavior. FIB and multicast routing code mutate tables under their locks. Address and route changes bump generation counters and schedule delayed work.

State and persistence: Runtime per-net state only, but it is long-lived for the namespace. Several fields are hot-path cacheline organized and protected by atomic, mutex, spinlock, RCU, or seqlock mechanisms.

Dependencies/integration: Depends on TCP/UDP, FIB/routing, inet fragments, peers, sysctl/proc, multicast routing, l3mdev, multipath, notifier, address configuration, and siphash.

Risks/test signals: Test cacheline-sensitive field changes, sysctl isolation, route generation invalidation, FIB notifier sequencing, multicast table cleanup, local port range reserved-port behavior, timewait limits, UDP tunnel GRO availability, and namespace teardown with delayed work.
