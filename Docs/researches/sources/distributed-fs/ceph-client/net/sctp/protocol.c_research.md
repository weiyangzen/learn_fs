# sources/distributed-fs/ceph-client/net/sctp/protocol.c

## Purpose
`protocol.c` initializes and tears down SCTP protocol support and provides the IPv4 AF/PF implementation. It owns global caches, hash tables, per-net defaults, local address tracking, IPv4 routing/transmit helpers, UDP tunneling sockets, AF/PF registration, socket protocol registration, and module init/exit.

## Important APIs, Types, And Functions
Important exported or cross-file APIs include `sctp_copy_local_addr_list()`, `sctp_addr_wq_mgmt()`, `sctp_udp_sock_start()`, `sctp_udp_sock_stop()`, `sctp_register_af()`, `sctp_get_af_specific()`, `sctp_get_pf_specific()`, and `sctp_register_pf()`. Static initialization functions include `sctp_defaults_init()`, `sctp_defaults_exit()`, `sctp_ctrlsock_init()`, `sctp_ctrlsock_exit()`, and module-level `sctp_init()`/`sctp_exit()`.

The IPv4 AF/PF tables are `sctp_af_inet` and `sctp_pf_inet`, with helpers for address copy/parse/compare/scope, bind/send verification, route lookup, source address selection, ECN, skb msgname construction, and `sctp_v4_xmit()`. Socket registrations include `sctp_seqpacket_protosw`, `sctp_stream_protosw`, `sctp_protocol`, and `inet_seqpacket_ops`.

## Control Flow
Module init creates bind-bucket and chunk slab caches, initializes global counters and association IDR, computes memory sysctls, allocates endpoint and bind-port hash tables, initializes the transport rhashtable, registers global sysctls, registers IPv4/IPv6 AF/PF tables and stream scheduler ops, registers per-net default setup, registers IPv4/IPv6 socket protosw entries, creates per-net control sockets, registers IPv4/IPv6 protocol handlers, and finally registers SCTP offload. Each failure label unwinds the subset already initialized.

Per-net defaults set SCTP timers, retransmit limits, feature defaults (ADDIP, PR-SCTP, RECONF, AUTH, ECN, UDP encapsulation, scope policy, L3 master accept), sysctls, MIBs, proc entries, debug object counters, local address list, ASCONF address wait queue, and address wait timer. Exit frees address queues/lists, proc subtree, MIBs, and sysctls.

IPv4 address notifiers maintain `net->sctp.local_addr_list` under RCU and queue ASCONF notifications. The address wait timer batches add/delete events and invokes `sctp_asconf_mgmt()` for auto-ASCONF sockets bound to all addresses. `sctp_v4_get_dst()` performs route lookup and verifies/selects a source address from the association bind list; `sctp_v4_xmit()` sends either native SCTP with `__ip_queue_xmit()` or UDP-encapsulated SCTP with `udp_tunnel_xmit_skb()`.

## State And Persistence
Persistent runtime state includes global SCTP caches, hash tables, AF/PF function pointers, per-net defaults/sysctls, local address lists, address wait queues, control sockets, UDP tunnel sockets, MIBs, and module parameter `sctp_checksum_disable` exposed as `no_checksums`. All state is in memory and removed on net namespace exit or module unload.

## Dependencies And Integration Points
The file integrates with IPv4/IPv6 core protocol registries, socket protosw, `struct proto` definitions from socket code, sysctl, procfs, net namespaces, inet address notifiers, route lookup, UDP tunnel helpers, SCTP input/output, stream scheduler registration, slab/percpu allocation, and SCTP offload registration.

## Risks
Initialization ordering is fragile because many later pieces assume AF/PF tables, hash tables, per-net fields, and control sockets exist. Unwind labels must stay paired with successful init steps. Address notifier and ASCONF queue logic must handle add/delete flapping and IPv6 DAD delays without leaking entries. Route/source selection must not choose an address outside the bind list unless explicitly allowed. The `no_checksums` parameter is dangerous for real networks because it disables SCTP checksum verification/computation.

## Test Signals
Test module load/unload, IPv4 and IPv6 socket creation for `SOCK_SEQPACKET` and `SOCK_STREAM`, per-net namespace init/exit, sysctl defaults, proc creation, local address list population, address add/delete ASCONF batching, UDP tunnel socket start/stop, IPv4 PMTU/ECN/DSCP transmit behavior, source address selection from multihomed bind lists, failure injection at each init step, and `no_checksums` behavior on receive/transmit.
