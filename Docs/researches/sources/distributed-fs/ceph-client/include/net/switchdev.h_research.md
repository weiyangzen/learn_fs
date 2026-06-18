<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/switchdev.h -->
# sources/distributed-fs/ceph-client/include/net/switchdev.h

Purpose: Defines the switchdev API that lets bridge, VXLAN, MRP, VLAN, MDB, and FDB control-plane events be offloaded to switch ASIC drivers through notifier and object/attribute contracts.

Important APIs/types/functions: Attribute ids cover port STP/MST state, bridge flags, mrouter, ageing time, VLAN filtering/protocol, multicast disable, MRP role, and VLAN MSTI. Object ids cover port VLAN, port/host MDB, MRP ring/in roles, tests, and states. `struct switchdev_attr`, `struct switchdev_obj`, and specialized object structs carry offload requests. Notifier types cover FDB add/delete/offload/flush, port object add/delete, port attr set, VXLAN FDB events, and bridge-port offload replay. APIs include `switchdev_bridge_port_offload()`, `switchdev_bridge_port_unoffload()`, `switchdev_bridge_port_replay()`, `switchdev_deferred_process()`, port attr/object add/del, notifier registration/calls, and handler helpers for FDB/object/attr dispatch.

Control flow: Bridge or VXLAN code constructs a switchdev attr/object/notifier info and calls blocking or atomic notifiers. Drivers register notifier blocks, use handler helpers to filter supported devices and foreign devices, and perform offload callbacks. Deferred mode lets operations escape atomic context. With `CONFIG_NET_SWITCHDEV` disabled, inline stubs return `-EOPNOTSUPP`, `NOTIFY_DONE`, or no-op success as appropriate.

State and persistence behavior: This header defines event payloads rather than persistent global state. Persistent offload state is held by bridge core and drivers. `complete` callbacks and `complete_priv` let asynchronous/deferred operations report completion.

Dependencies/integration points: Depends on netdevice, notifier, list, and FIB headers. Integrates bridge VLAN/MDB/FDB code, VXLAN FDB, MRP, DSA, ASIC drivers, and netlink extack reporting.

Risks: Offload and software bridge state must remain synchronized. Deferred operations can race with device unregister or bridge teardown. Foreign-device filtering mistakes can program the wrong ASIC. Stub behavior under disabled config must be acceptable to callers.

Test signals: Bridge switchdev selftests, FDB/VLAN/MDB replay after port offload, deferred operation tests, extack checks, device unregister while offloaded, and disabled-config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/switchdev.h -->
