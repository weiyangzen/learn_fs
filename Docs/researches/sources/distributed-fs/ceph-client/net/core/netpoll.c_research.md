<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netpoll.c -->
# sources/distributed-fs/ceph-client/net/core/netpoll.c

## Purpose
Low-level UDP packet output and polling framework used by netconsole, crash/debug paths, and other code that must transmit while normal networking progress may be impaired. It maintains emergency skb pools, polls NAPI/driver controller hooks, and constructs Ethernet/IP/UDP packets directly.

## APIs, Types, and Functions
Exported APIs include `netpoll_poll_dev()`, `netpoll_poll_disable()`, `netpoll_poll_enable()`, `netpoll_send_skb()`, `netpoll_send_udp()`, `__netpoll_setup()`, `netpoll_setup()`, `__netpoll_free()`, `do_netpoll_cleanup()`, and `netpoll_cleanup()`. Helpers include `queue_process()`, `poll_one_napi()`, `find_skb()`, `__netpoll_send_skb()`, `push_ipv4()`, `push_ipv6()`, `push_udp()`, and `push_eth()`.

## Control Flow, State, and Persistence
Setup resolves the egress device by name or MAC under RTNL, rejects slave devices and devices with `IFF_DISABLE_NETPOLL`, opens the device if needed, auto-fills local IPv4/IPv6 when unset, initializes a per-netpoll skb pool, and attaches/refcounts a per-netdevice `netpoll_info`. Sending first tries immediate hard-start xmit with IRQs disabled and no local NAPI recursion; on congestion it queues to `npinfo->txq` and schedules delayed work. Polling uses `npinfo->dev_lock`, optional driver `ndo_poll_controller`, budget-zero NAPI polling, and completion-queue cleanup. Cleanup decrements the shared `npinfo` refcount, clears `dev->npinfo` under RCU, cancels work, purges queues, flushes the local skb pool, and releases the held netdev.

## Dependencies and Integration
Depends on netdevice TX locks, NAPI state, softnet completion queues, IPv4/IPv6 address configuration, UDP checksums, VLAN handling, workqueues, RTNL/RCU synchronization, and optional driver netpoll setup/cleanup/poll hooks. The `carrier_timeout` module parameter controls wait time after opening an interface.

## Risks and Test Signals
Risks include IRQ-state assumptions, driver poll/xmit lock recursion, stale queue mappings after queue-count changes, RCU lifetime of `npinfo`, IPv6 local address auto-detection, and correct fallback during OOM. Test signals are UDP packet construction for IPv4 and IPv6, send under stopped TX queue with later workqueue drain, setup/cleanup refcounting for multiple netpoll users, `netpoll_poll_disable()` blocking polling during device state changes, and no local IP overwrite when caller supplied an IPv6 address whose first four bytes are zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/netpoll.c -->
