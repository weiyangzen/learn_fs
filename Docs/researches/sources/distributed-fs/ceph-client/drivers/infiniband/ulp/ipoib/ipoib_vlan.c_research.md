# sources/distributed-fs/ceph-client/drivers/infiniband/ulp/ipoib/ipoib_vlan.c

## Purpose
`ipoib_vlan.c` implements legacy sysfs P_Key child interface creation/deletion and the shared child-registration helper also used by rtnetlink. In IPoIB these "VLAN" children represent P_Key partition interfaces rather than Ethernet 802.1Q VLANs.

## Important APIs, Types, And Functions
`parent_show()` exposes the parent device name for legacy children. `is_child_unique()` enforces legacy uniqueness by P_Key while allowing RTNL children to duplicate P_Keys. `__ipoib_vlan_add()` is the shared registration core: it sets the private destructor, validates P_Key, links parent/P_Key/type state, checks uniqueness, registers the netdevice, and adds legacy sysfs attributes. `ipoib_vlan_add()` handles CAP_NET_ADMIN, rtnl locking, legacy interface naming, allocation, and registration. `ipoib_vlan_delete()` finds a matching legacy child and queues `ipoib_vlan_delete_task()` to unregister it from the global workqueue.

## Control Flow And State
Legacy creation is driven by the parent sysfs `create_child` attribute in `ipoib_main.c`. It constructs a name like `<parent>.%04x`, allocates an IPoIB netdev for the same HCA/port, assigns `rtnl_link_ops`, and registers it as `IPOIB_LEGACY_CHILD`. During registration, normal netdev init links the child into `ppriv->child_intfs`, inherits parent GID/MTU properties, and sets `IPOIB_FLAG_SUBINTERFACE`.

Deletion is asynchronous to avoid sysfs/rtnl deadlock. The sysfs callback takes rtnl with trylock only long enough to locate and remove the child from the parent's list, then queues work. The work item later takes rtnl and unregisters the device if it is still registered.

## Dependencies And Integration Points
The file depends on Linux capability checks, rtnl/netdevice registration, the global `ipoib_workqueue`, and shared allocation/init/free paths from `ipoib_main.c`. It is called by sysfs `create_child`/`delete_child` handlers and by netlink child creation through `__ipoib_vlan_add()`.

## Risks And Test Signals
Risks include double-free or destructor mismatches on registration failure, races with parent unregister, list removal before asynchronous unregister, legacy duplicate P_Key ambiguity, and rtnl/sysfs deadlocks. Test signals include creating/deleting legacy children, invalid P_Key values (`0`, `0x8000`, out of range), duplicate legacy P_Keys, duplicate RTNL P_Keys, parent removal while delete work is queued, and register_netdevice failure injection.
