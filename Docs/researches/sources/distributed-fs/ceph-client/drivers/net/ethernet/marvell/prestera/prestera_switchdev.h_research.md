# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_switchdev.h

## Purpose
This header declares the Prestera switchdev bridge-offload interface. It is the small public API used by Prestera core/netdev code to initialize switchdev support and react when a Prestera port joins or leaves a Linux bridge.

## Important APIs, types, and functions
The exports are `prestera_switchdev_init()`, `prestera_switchdev_fini()`, `prestera_bridge_port_join()`, and `prestera_bridge_port_leave()`. The join API receives the bridge netdev, Prestera port, and extack for user-visible error reporting. The leave API receives the bridge netdev and Prestera port.

## Control flow
Switch setup calls init after core switch data structures are ready and before bridge events are expected. Port upper-device handling calls bridge-port join/leave as bridge relationships change. Switch teardown calls fini after ports are removed from bridge contexts.

## State and persistence behavior
The header exposes no state; implementation-private state is held in `sw->swdev`. Hardware bridge state is created and removed by the implementation.

## Dependencies and integration points
The declarations rely on `struct prestera_switch`, `struct prestera_port`, `struct net_device`, and `struct netlink_ext_ack` being visible to users. It integrates Prestera port lifecycle code with Linux switchdev bridge offload.

## Risks and edge cases
Callers must not call join before `prestera_switchdev_init()`, and leave must match a previous join. The header does not express bridge mode limitations; callers learn those through runtime errors and extack/log messages.

## Test signals
Compile coverage should catch signature drift. Integration tests should exercise netdev upper join/leave sequences and verify init/fini lifecycle ordering around bridge events.
