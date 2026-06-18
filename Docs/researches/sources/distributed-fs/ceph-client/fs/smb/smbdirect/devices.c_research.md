## sources/distributed-fs/ceph-client/fs/smb/smbdirect/devices.c

Purpose: Tracks RDMA devices usable for SMBDirect and provides net-device capability lookup so higher layers can decide whether a network interface can support SMBDirect over IB/RoCE or iWARP.

Important APIs and functions: `smbdirect_devices_init()` registers an `ib_client`; `smbdirect_devices_exit()` unregisters it and clears the tracked device list. `smbdirect_netdev_rdma_capable_node_type()` is exported for netdev capability lookup. Internal callbacks `smbdirect_ib_client_add()`, `smbdirect_ib_client_remove()`, and `smbdirect_ib_client_rename()` maintain `smbdirect_globals.devices.list`. `smbdirect_ib_device_rdma_capable_node_type()` filters devices by FRWR support and RDMA node type.

Control flow: On module init, the IB client add callback logs device capabilities, ignores devices lacking FRWR or supported node type, allocates a `smbdirect_device`, stores the `ib_device` and name copy, and adds it under a write lock. Remove/rename callbacks update the same list. Capability lookup first scans tracked IB devices and their ports for a matching netdev, then falls back to `ib_device_get_by_netdev()`. It also checks lower devices for bridge/VLAN netdevs and treats IPoIB ARPHRD_INFINIBAND as IB-capable.

State and persistence: Maintains an in-memory global list protected by `rwlock_t`. Each entry stores an `ib_device *` and a stable name copy used for remove/rename logging. No persistent state exists; the list is rebuilt by IB client registration.

Dependencies and integration points: Depends on RDMA core device/client APIs, netdevice APIs for lower-device traversal, `smbdirect_frwr_is_supported()` from `socket.c`, and global module state from `internal.h`. It integrates with module init/exit in `main.c` and callers that need `RDMA_NODE_*` answers for interfaces.

Risks and edge cases: Netdev-to-IB mapping can race with device removal, so reference handling through `ib_device_get_netdev()`/`dev_put()` and `ib_device_get_by_netdev()`/`ib_device_put()` is important. Bridge/VLAN lookup returns the first capable lower device and may not represent all paths. Device add logs substantial capability data, which is useful for diagnosis but can be noisy on systems with many RDMA devices.

Test signals: Test add/remove/rename callbacks, FRWR-unsupported devices, RoCE/IB/iWARP node types, bridge and VLAN lower devices, IPoIB fallback, no-device netdevs, and module unload after devices have been tracked.
