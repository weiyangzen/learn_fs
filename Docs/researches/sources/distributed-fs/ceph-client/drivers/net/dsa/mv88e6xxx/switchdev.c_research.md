# sources/distributed-fs/ceph-client/drivers/net/dsa/mv88e6xxx/switchdev.c

## Purpose
Bridges mv88e6xxx hardware miss violations into Linux switchdev notifications, allowing locked FDB learning events to be reported to the bridge.

## Important APIs, Types, and Functions
Exports `mv88e6xxx_handle_miss_violation`. Internal helpers `__mv88e6xxx_find_vid` and `mv88e6xxx_find_vid` walk the VTU to map a filtering database ID back to a VLAN ID.

## Control Flow and State
On a miss violation, the code finds the VID for the supplied FID under the register lock, builds `switchdev_notifier_fdb_info` with `locked = true`, resolves the DSA port and its bridge port under RTNL, then calls `call_switchdev_notifiers(SWITCHDEV_FDB_ADD_TO_BRIDGE, ...)`. It does not persist state itself; the bridge/FDB layer handles the resulting notification.

## Dependencies and Integration Points
Depends on `global1.h` VTU walking, DSA port lookup, switchdev notifier APIs, RTNL locking, and ATU violation handling code that supplies the entry and FID.

## Risks and Test Signals
Risks include failing to find VID for valid FIDs, notifying after a port leaves a bridge, lock ordering between register lock and RTNL, and duplicate locked FDB events. Test signals include locked-port miss violation tests, bridge FDB notification observation, VLAN/FID mapping coverage, and port-unbridged error paths.
