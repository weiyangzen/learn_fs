<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_main.c -->
# sources/distributed-fs/ceph-client/net/hsr/hsr_main.c

## Purpose
Provides HSR/PRP module initialization, netdevice event handling, port lookup, and protocol version export.

## APIs, Types, and Functions
Defines notifier `hsr_nb`, module init/exit functions `hsr_init()` and `hsr_exit()`, helper `hsr_slave_empty()`, notifier callback `hsr_netdev_notify()`, exported `hsr_get_version()`, and `hsr_port_get_hsr()`.

## Control Flow, State, and Persistence
The netdevice notifier maps events to the affected HSR port or master. UP/DOWN/CHANGE events recompute carrier, operstate, and supervision timers. CHANGENAME renames debugfs for master devices. CHANGEADDR on a slave updates master and, for PRP, slave B addresses, then recreates the self node so looped self frames are recognized. CHANGEMTU on slaves clamps the master MTU to the smallest slave MTU minus tag length. UNREGISTER removes non-master ports and deletes the master device if no slaves remain. PRE_TYPE_CHANGE rejects changing slave Ethernet type. Module init verifies HSR tag size, registers the notifier, and initializes HSR netlink; exit tears down netlink, debugfs root, and notifier. Persistent module state is the registered notifier and netlink family; per-device state is managed in `hsr_priv`.

## Dependencies and Integration
Depends on rtnetlink notifier infrastructure, HSR device/slave/netlink/frame registry APIs, debugfs rename/remove helpers, and net_device lifetimes. It exports version and master-detection utilities for other kernel users.

## Risks and Test Signals
Risks include notifier ordering during unregister, self-node update failure after slave MAC changes, PRP MAC synchronization side effects, automatic master removal when slaves disappear, MTU updates bypassing normal change paths, and PRE_TYPE_CHANGE blocking legitimate transitions. Test signals include module load/unload, slave carrier changes, slave MAC change in HSR and PRP modes, slave MTU change, slave unregister removing the master when empty, debugfs rename, type-change rejection, and `hsr_get_version()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/hsr/hsr_main.c -->
