<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/bonding/bond_sysfs_slave.c -->
## sources/distributed-fs/ceph-client/drivers/net/bonding/bond_sysfs_slave.c

Purpose: this file adds read-only sysfs attributes to each bonding slave kobject. It gives per-slave visibility into active/backup role, MII status, link failure count, permanent hardware address, queue id, and selected 802.3ad operational state.

Important APIs, types, and functions: `struct slave_attribute` wraps a sysfs `struct attribute` and a slave-specific show callback. `SLAVE_ATTR_RO()` defines attributes for `state`, `mii_status`, `link_failure_count`, `perm_hwaddr`, `queue_id`, `ad_aggregator_id`, `ad_actor_oper_port_state`, and `ad_partner_oper_port_state`. `slave_sysfs_ops` routes generic kobject reads through `slave_show()`. Exported lifecycle helpers are `bond_sysfs_slave_add()` and `bond_sysfs_slave_del()`.

Control flow: slave creation calls `bond_sysfs_slave_add()`, which registers all files on `slave->kobj`. A read converts the kobject to `struct slave`, converts the attribute to `struct slave_attribute`, and invokes the stored callback. 802.3ad fields check bond mode and aggregator presence before returning numeric state; otherwise they return `N/A`.

State and persistence: no independent state is stored. The attributes reflect live `struct slave` fields: role from `bond_slave_state()`, link from `slave->link`, counters, `perm_hwaddr`, `queue_id`, and `SLAVE_AD_INFO(slave)->port` data. Aggregator lookup uses RCU where a pointer dereference needs protection.

Dependencies and integration points: it depends on the bonding slave kobject model, `to_slave()`, sysfs file creation/removal, RCU for aggregator access, and 802.3ad per-port state structures in `<net/bonding.h>`.

Risks: all attributes are read-only, but they still expose rapidly changing data without a global lock. Non-802.3ad modes must consistently return `N/A` for LACP fields. Queue id uses `READ_ONCE()` because option writes can update it concurrently.

Test signals: enslave and release devices while checking file creation/removal, read state transitions between active and backup, verify queue id changes after `bonding/queue_id` writes, confirm link failure counter increments, and validate 802.3ad `N/A` versus populated aggregator/port-state output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/bonding/bond_sysfs_slave.c -->
