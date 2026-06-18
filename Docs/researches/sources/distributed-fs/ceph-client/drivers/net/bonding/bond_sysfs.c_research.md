<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/bonding/bond_sysfs.c -->
## sources/distributed-fs/ceph-client/drivers/net/bonding/bond_sysfs.c

Purpose: this file exposes bonding control and status through sysfs. It creates `/sys/class/net/bonding_masters` per network namespace for creating/deleting bond devices and installs the per-bond `bonding/` attribute group that mirrors most user-visible options and status fields.

Important APIs, types, and functions: `bonding_show_bonds()` and `bonding_store_bonds()` implement the class attribute. `bonding_sysfs_store_option()` is the generic writer that maps an attribute name to a `bond_option` and calls `bond_opt_tryset_rtnl()`. The many `bonding_show_*()` functions expose option values and read-only status such as `mii_status`, `ad_aggregator`, `ad_num_ports`, `ad_actor_key`, `ad_partner_key`, and `ad_partner_mac`. Lifecycle hooks are `bond_create_sysfs()`, `bond_destroy_sysfs()`, and `bond_prepare_sysfs_group()`.

Control flow: writes to `bonding_masters` parse a leading `+` or `-`, validate the interface name, and call `bond_create()` or `unregister_netdevice()` under RTNL for deletion. Per-bond attribute writes duplicate the user buffer, resolve the option by attribute name, and delegate all parsing and mutation to `bond_options.c`. Show methods read `struct bonding` state, often under RCU for slave lists or active/primary pointers, format symbolic names through `bond_opt_get_val()`, and return empty output for mode-inapplicable privileged 802.3ad attributes.

State and persistence: the file owns no option state; it exposes live `bond->params`, RCU slave lists, carrier state, active aggregator info, and queue ids. It stores a copy of `class_attr_bonding_masters` inside `struct bond_net` so each namespace has its own sysfs file identity. Per-bond sysfs groups are attached through `dev->sysfs_groups[0]` before netdevice registration.

Dependencies and integration points: it depends on netdev class sysfs helpers, RTNL, namespace-aware sysfs file creation/removal, RCU, `bond_options.c`, `bond_create()`, `bond_enslave()`/`bond_release()` through the options backend, 802.3ad query helpers, and capability checks for sensitive LACP data.

Risks: sysfs writes use `rtnl_trylock()` through the option backend, so busy RTNL surfaces as `restart_syscall()`. Attribute names must stay aligned with `bond_opts[].name`, except aliases such as `num_grat_arp` and `num_unsol_na`. Show paths must fit into one page and use truncation markers for large slave lists. `bonding_masters` preserves legacy behavior by ignoring `-EEXIST`, which means repeated module loads can have partial class-control visibility.

Test signals: verify `+bond0` and `-bond0` through `bonding_masters`, per-namespace isolation, all per-bond option writes and reads, page-size truncation for many slaves, privileged and unprivileged reads of 802.3ad fields, active slave and primary updates under RCU, and successful sysfs cleanup on namespace and module teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/bonding/bond_sysfs.c -->
