# sources/distributed-fs/ceph-client/drivers/net/team/team_mode_activebackup.c

Purpose: implements the team active-backup mode, where a single configured active port handles Tx/Rx and other ports remain backups.

Important APIs/functions: `ab_init_module`/`ab_cleanup_module` register/unregister `ab_mode`. Mode ops are `ab_init`, `ab_exit`, `ab_receive`, `ab_transmit`, and `ab_port_leave`. The mode-specific option `activeport` is implemented by `ab_active_port_init`, `ab_active_port_get`, and `ab_active_port_set`.

Control flow: mode init registers the `activeport` option. Userspace sets `activeport` to a port ifindex; the setter finds that port and stores it in `ab_priv.active_port` using RCU assignment. Tx dereferences the active port under BH RCU context and queues to it, dropping if none exists or xmit fails. Rx accepts frames only from the active port; frames from backups use exact delivery. When the active port leaves, the pointer is cleared and the option instance is marked changed.

State and persistence: state is `struct ab_priv` in `team->mode_priv`, containing an RCU active-port pointer and the option instance used for change notification. It is in-memory only and reset on mode exit/change.

Dependencies and integration: depends on team core mode registration, option APIs, `team_dev_queue_xmit`, RCU pointer access, and generic-netlink option propagation through team core. It advertises `NETDEV_LAG_TX_TYPE_ACTIVEBACKUP`.

Risks: if userspace does not set `activeport`, all Tx packets are dropped. The mode intentionally does not rewrite slave MAC addresses, matching Kconfig help, so userspace must ensure appropriate MAC configuration. Active port removal must notify userspace or stale configuration can persist externally.

Test signals: set active port by ifindex, transmit and receive only through that port, remove the active port and verify option change and Tx drop behavior, try setting nonexistent ifindex, and verify backup-port Rx is exact-delivered rather than accepted by the team device.
