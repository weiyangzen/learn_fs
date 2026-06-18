<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_if.c -->
# sources/distributed-fs/ceph-client/net/bridge/br_if.c

Purpose: implements bridge and bridge-port lifecycle operations exposed to userspace and other bridge subsystems. It creates and deletes bridge netdevices, enslaves and releases lower devices, manages port object lifetime, promiscuous/all-multicast mode, headroom, MTU, feature recomputation, local FDB entries, STP port enablement, multicast port context, netpoll, sysfs, upper-device links, and backup-port relationships.

Important APIs, types, and functions:

- Bridge device management: `br_add_bridge()`, `br_del_bridge()`, and `br_dev_delete()`.
- Port management: `br_add_if()`, `br_del_if()`, `new_nbp()`, `del_nbp()`, `destroy_nbp_rcu()`, and the `brport_ktype` kobject type.
- Port/link state helpers: `br_port_carrier_check()`, `br_port_flags_change()`, `br_port_flag_is_set()`, `nbp_backup_change()`, and `nbp_backup_clear()`.
- Promiscuity and filtering helpers: `br_manage_promisc()`, `br_port_set_promisc()`, `br_port_clear_promisc()`, `nbp_delete_promisc()`, and `nbp_update_port_count()`.
- Device shape helpers: `port_cost()`, `br_mtu_auto_adjust()`, `br_features_recompute()`, `get_max_headroom()`, and `update_headroom()`.

Core control flow:

- `br_add_bridge()` allocates a `struct net_bridge` embedded in a netdevice with `br_dev_setup()`, assigns the target net namespace, attaches `br_link_ops`, and registers the device.
- `br_add_if()` validates that the lower device is a usable Ethernet device, is not itself a bridge, has no master, and is allowed to be bridged. It allocates a `struct net_bridge_port`, joins the device, enables all-multicast, creates kobject/sysfs state, enables netpoll, installs the bridge RX handler, links the bridge as upper master, disables LRO, adds the port to `br->port_list` under RCU, adjusts promiscuity/static FDB filters, headroom, local FDB entries, VLAN state, STP state, notifications, MTU, and master features. Each failure label unwinds only the pieces already installed.
- `del_nbp()` is the inverse port teardown. It removes sysfs links, clears promiscuity or static filters, disables STP, deletes MRP and CFM state, notifies link deletion, removes the port from the RCU list, updates headroom, flushes VLANs and FDB entries, processes deferred switchdev work, clears backup links, unlinks the upper device, clears `IFF_BRIDGE_PORT`, unregisters the RX handler, deletes multicast context, removes kobject state, disables netpoll, and frees through RCU.
- `br_dev_delete()` deletes all ports, uninitializes MST, recalculates neighbour suppression, removes bridge-local FDB entries, cancels FDB GC, removes bridge sysfs, and queues netdevice unregister.
- `br_port_carrier_check()` updates path cost from ethtool link speed when not admin-set and enables/disables STP state when lower carrier changes and the bridge is running.
- `br_manage_promisc()` decides whether ports can leave promiscuous mode based on bridge promiscuity, VLAN filtering, auto-port count, and unicast-filter support. Static FDB entries are synced to hardware filters before clearing promiscuity.

State and persistence behavior:

- Port membership persists in `br->port_list` and lower device upper links until `br_del_if()`, bridge deletion, or error unwind. Readers use RCU; administrative mutation is under RTNL.
- Port objects have kobject lifetime plus an RCU grace period before final `netdev_put()` and free. The RX handler marks the lower netdevice as a bridge port for `br_port_get_*()` helpers.
- Bridge-wide `auto_cnt`, needed headroom, MTU user flag, local FDB entries, multicast contexts, VLAN contexts, STP timers, MRP/CFM state, and backup redirection counters are updated as derived runtime state.
- No disk persistence is involved; userspace must recreate bridge topology after restart.

Dependencies and integration points:

- This file connects rtnetlink/ioctl bridge operations to netdevice core, sysfs, kobjects, STP, FDB, VLAN, multicast snooping, MRP, CFM, switchdev, DSA RX-handler selection, netpoll, ethtool, and net namespace ownership.
- `br_ioctl.c` calls `br_add_bridge()`, `br_del_bridge()`, `br_add_if()`, and `br_del_if()` for legacy interfaces.
- `br_input.c` depends on the RX handler installed here and on `IFF_BRIDGE_PORT`.
- `br_fdb.c` is called for local address insertion, port flushing, and static filter sync/unsync.

Risks and edge cases:

- The `br_add_if()` unwind path is long and order-sensitive. A new resource added in the middle must be unwound in the correct reverse order to avoid leaks, stale upper links, or active RX handlers on rejected devices.
- Promiscuity optimization depends on device `IFF_UNICAST_FLT` capacity and static FDB sync success. Failure can reduce filtering precision or require promiscuous fallback.
- Port deletion must coordinate RCU packet readers, switchdev deferred work, netpoll, sysfs/kobject lifetime, and netdevice references.
- Bridge MTU and headroom are derived from member ports unless user-set; adding/removing unusual devices can change bridge packet constraints.
- Backup-port counters must be cleared both for a port's own backup and for other ports redirecting to it.

Test signals:

- Add and remove valid and invalid lower devices, including non-Ethernet, bridge-as-port, busy-master, `IFF_DONT_BRIDGE`, and devices with RX handler conflicts.
- Verify error-unwind paths with injected failures in sysfs, netpoll, upper-link, VLAN initialization, and address notification.
- Check port carrier transitions update STP state and path cost.
- Validate static FDB filter sync when toggling VLAN filtering, bridge promiscuity, and port flags.
- Confirm bridge MTU/headroom/features after adding and deleting ports with different MTUs, headrooms, and feature sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bridge/br_if.c -->
