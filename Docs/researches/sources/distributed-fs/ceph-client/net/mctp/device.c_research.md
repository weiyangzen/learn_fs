# sources/distributed-fs/ceph-client/net/mctp/device.c

Purpose: manages MCTP per-netdevice state, local EID addresses, RTNL address operations, link AF attributes, netdevice registration/unregistration, and driver-facing MCTP netdev registration helpers.

Important APIs and functions: `__mctp_dev_get()`, `mctp_dev_get_rtnl()`, `mctp_rtm_newaddr()/deladdr()`, `mctp_dev_hold()/put()`, `mctp_dev_set_key()/release_key()`, `mctp_register_netdev()/unregister_netdev()`, and init/exit for notifier, RTNL AF ops, and address message handlers.

Control flow and state: `mctp_add_dev()` allocates `mctp_dev`, initializes address lock and default net, attaches it to `dev->mctp_ptr` with RCU, and holds the netdevice. Address add/delete updates `mdev->addrs` under spinlock, sends RTNL notifications, and adds/removes local routes. Netdevice notifier auto-registers supported ARPHRD types and unregister removes routes/neighbours before dropping refs.

Dependencies and integration: used by route lookup/output, socket direct addressing, neighbour tables, and physical MCTP drivers. Integrates with RTNL, netdevice notifier, rtnl AF ops (`IFLA_MCTP_NET`, physical binding), and local route management.

Risks and test signals: address array replacement/removal must be safe for readers using `addrs_lock`; `mctp_rtm_deladdr()` memmoves the live array without reallocating. Device unregister relies on RTNL plus RCU/refcounts to protect readers. Tests should cover address add/delete notifications, local route synchronization, device unregister cleanup, and flow release callbacks.
