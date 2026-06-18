# sources/distributed-fs/ceph-client/include/net/netns/sctp.h

Purpose: Defines per-network-namespace SCTP state, statistics, sockets, address lists, timers, and extensive protocol sysctl defaults.

Important APIs/types/functions: `struct netns_sctp` includes SNMP stats, proc/sysctl headers, control socket, UDP tunnel sockets/ports, local address lists and wait queues, address timers/locks, auto-ASCONF list, and many protocol parameters: RTO, burst, cookies, SACK, heartbeat, PLPMTUD, retransmission limits, failover, accounting policies, addip/auth/reconfig/interleave/ECN flags, scope policy, receive-window update threshold, autoclose, and optional l3mdev accept.

Control flow: SCTP init creates control/tunnel sockets and fills defaults. Address notifier paths update lists under locks and timers. Protocol operations read namespace parameters for association behavior, retransmission, auth, encapsulation, and accounting.

State and persistence: Runtime per-net state with timers, sockets, locks, lists, and stats. Sysctls change values during namespace lifetime.

Dependencies/integration: Depends on SCTP core, SNMP stats, procfs/sysctl, UDP tunneling, timers, socket layer, address notification, and l3mdev.

Risks/test signals: Test namespace teardown with timers/sockets, UDP encapsulation ports, address add/delete races, sysctl validation, failover policies, auth/addip/reconfig flags, and stats accounting.
