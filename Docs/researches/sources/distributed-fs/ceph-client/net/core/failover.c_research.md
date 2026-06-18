# sources/distributed-fs/ceph-client/net/core/failover.c

Purpose: Generic failover infrastructure for paravirtual networking and accelerated datapath live migration. It associates a failover master netdevice with Ethernet slave devices that share the same permanent MAC address and forwards slave registration, unregister, link-change, and name-change events to driver-provided failover operations.

Important APIs, types, and functions: Global state is `failover_list` protected by `failover_lock`. Public exports are `failover_register()`, `failover_unregister()`, and `failover_slave_unregister()`. Internal helpers include `failover_get_bymac()`, `failover_slave_register()`, `failover_slave_link_change()`, `failover_slave_name_change()`, `failover_event()`, and `failover_existing_slave_register()`.

Control flow and state: `failover_register()` validates an Ethernet master and ops table, allocates a `struct failover`, stores ops and master via RCU assignment, holds the master netdevice, marks it `IFF_FAILOVER`, inserts it in the global list, then scans existing devices in the same net namespace for MAC-matching slaves. Slave registration checks Ethernet type and matching master, calls optional pre-register, installs an RX handler, links the slave as an active-backup upper/lower relationship, marks `IFF_FAILOVER_SLAVE | IFF_NO_ADDRCONF`, then calls the driver's `slave_register()` hook. Failure unwinds upper link, flags, and RX handler. Unregister reverses the relationship and invokes driver hooks.

Dependencies and integration points: The module depends on netdevice notifiers, RTNL, Ethernet permanent addresses, LAG upper info, RX handler registration, upper/lower device links, `netdev_lock_ops()` during existing-slave scan, and driver-supplied `struct failover_ops`.

Risks: Matching by permanent MAC is simple but can bind unexpected devices if MAC assignment is wrong. Registration unwind must keep RX handler, upper link, and flags consistent. `failover_get_bymac()` returns a master without taking a new reference; callers rely on RTNL and failover list lifetime. Existing-slave scan locks RTNL and then per-device ops locks, so lock ordering must stay aligned with netdevice core rules.

Test signals: Register a failover master before and after slave creation; verify RX handler and upper link installation; exercise pre-register and register failure unwind; unregister slaves and masters in both orders; link/name change callbacks only when master is running; and module init/exit notifier registration without leaks.
