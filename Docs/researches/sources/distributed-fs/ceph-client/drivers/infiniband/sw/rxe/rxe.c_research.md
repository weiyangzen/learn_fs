# sources/distributed-fs/ceph-client/drivers/infiniband/sw/rxe/rxe.c

## Purpose
`rxe.c` is the RXE module/device lifecycle file. It initializes soft-RoCE device attributes, port attributes, object pools, multicast/mmap state, RDMA link operations, module-level namespace/net notifiers, and registration with the RDMA core.

## Important APIs, types, and functions
Key functions are `rxe_dealloc()`, `rxe_init_device_param()`, `rxe_init_port_param()`, `rxe_init_ports()`, `rxe_init_pools()`, `rxe_init()`, `rxe_set_mtu()`, `rxe_add()`, `rxe_newlink()`, `rxe_dellink()`, `rxe_module_init()`, and `rxe_module_exit()`. It defines RDMA link ops of type `"rxe"` and optional ODP device ops for `advise_mr`.

## Control flow
Module init creates the RXE workqueue, initializes namespace support, registers net notifiers, and registers RDMA link ops. `rdma link add ... type rxe netdev ...` enters `rxe_newlink()`, which rejects VLAN devices, prevents duplicate RXE devices on the same netdev, initializes networking, and delegates to `rxe_net_add()`. `rxe_add()` initializes attributes/pools/locks/multicast state, sets MTU from the parent netdev, attaches link ops, and registers the IB device. Module exit unregisters link ops, unregisters the RXE driver, tears down networking/workqueue/namespace state, and logs unload.

## State and persistence
Per-device state includes RDMA device attributes, raw GID derived from the parent MAC or random address, one port's attributes, object pools for all RXE object types, mmap offsets and pending maps, multicast RB tree, counters, and locks. State is in-memory and tied to the RDMA link/device lifetime.

## Dependencies and integration points
RXE integrates with RDMA netlink link ops, the network device layer, address configuration helpers, RXE net/namespace modules, RDMA core registration, object pools, multicast, mmap, and optional ODP capability advertisement.

## Risks
Device lifetime spans netdev notifiers, RDMA link deletion, object pool cleanup, and module unload. Duplicate device detection must balance the `ib_device_get_by_netdev()` reference with `ib_device_put()`. Random GID fallback for devices without hardware addresses can affect connection identity. ODP capability bits must match actual compiled support.

## Test signals
Test module load/unload, `rdma link add/delete`, duplicate and VLAN rejection, netdev down/up/MTU changes, ODP capability advertisement with and without ODP config, object leak warnings in `rxe_dealloc()`, and namespace cleanup.
