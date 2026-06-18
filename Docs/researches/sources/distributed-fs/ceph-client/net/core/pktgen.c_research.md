<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/pktgen.c -->
# sources/distributed-fs/ceph-client/net/core/pktgen.c

## Purpose
Kernel packet generator module for traffic generation and packet path testing. It creates per-network-namespace `/proc/net/pktgen` controls, per-online-CPU generator threads, and per-device generator configurations that can emit crafted IPv4/IPv6 UDP packets through hard-start-xmit, qdisc, or receive-path injection.

## APIs, Types, and Functions
Important types are `struct pktgen_net`, `struct pktgen_thread`, `struct pktgen_dev`, `struct flow_state`, `struct imix_pkt`, and on-wire `struct pktgen_hdr`. Control files use `pgctrl_write()`, `pktgen_thread_write()`, and `pktgen_if_write()`. Runtime functions include `pktgen_setup_dev()`, `pktgen_setup_inject()`, `mod_cur_headers()`, `fill_packet_ipv4()`, `fill_packet_ipv6()`, `pktgen_finalize_skb()`, `pktgen_xmit()`, `pktgen_thread_worker()`, `pktgen_add_device()`, `pktgen_remove_device()`, and pernet/module init/exit.

## Control Flow, State, and Persistence
Module init registers pernet state and a netdevice notifier. Each netns creates `/proc/net/pktgen/pgctrl` and one `kpktgend_N` file/thread per online CPU. Users add devices to a thread, then per-device proc writes configure sizes, IMIX weights, delays/rates, counts, flags, IPv4/IPv6 ranges, UDP ports, MAC iteration, MPLS, VLAN/SVLAN, queue mapping, SKB sharing, NUMA node, xmit mode, and optional IPsec. `start` posts `T_RUN`; worker threads initialize current addresses and counters, then repeatedly pick the next due device, build or reuse an skb, optionally wait until `next_tx`, transmit by the selected mode, update counters/sequence numbers, and stop when count is reached. Device unregister marks matching generators for removal; namespace exit stops threads and removes proc entries.

## Dependencies and Integration
Depends on procfs, pernet operations, kthreads, netdevice refs/notifiers, RCU-protected device lists, TX queue locks, skb allocation/frags, IPv4/IPv6/UDP checksum helpers, VLAN/MPLS header construction, random number helpers, high-resolution timers, NUMA allocation, and optional XFRM/IPsec. It directly exercises device start_xmit, `dev_queue_xmit()`, and `netif_receive_skb()`.

## Risks and Test Signals
Risks include a very broad proc parser surface, expected single-controller semantics, lock ordering between global thread lock and per-thread if lock, skb reuse/refcount bugs with `F_SHARED`, burst and clone constraints, generated header correctness for combinations of IPv6/MPLS/VLAN/IPsec/frags, device removal races, and CPU hotplug limitations because threads are created for online CPUs at namespace init. Test signals are proc command parsing and result strings, add/remove under notifier events, finite count completion with pps/bps results, xmit modes, shared/unshared skb behavior, queue mapping bounds correction, IMIX distribution counts, checksum modes, and cleanup on namespace/module exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/pktgen.c -->
