# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/macsec.c

## Purpose
`macsec.c` bridges RoCE GID programming with mlx5 MACsec offload steering. When RoCE UDP-encap GIDs are added on offloaded MACsec netdevs, it installs MACsec-aware RoCE steering rules, handles security association add/delete events, and manages ambiguous physical-vs-MACsec GID slots.

## Important APIs, Types, And Functions
The exported functions are `mlx5r_macsec_init_gids_and_devlist()`, `mlx5r_macsec_dealloc_gids()`, `mlx5r_macsec_event_register()`, `mlx5r_macsec_event_unregister()`, `mlx5r_add_gid_macsec_operations()`, and `mlx5r_del_gid_macsec_operations()`. `struct mlx5_reserved_gids` records a MACsec GID index and referenced physical GID attribute for ambiguous IP handling. `struct mlx5_macsec_device` tracks one MACsec netdev, its RoCE GID list, and TX/RX SA rule lists. `struct mlx5_roce_gids` stores a saved GID index and IPv4/IPv6 socket address.

## Control Flow
Initialization checks `mlx5_is_macsec_roce_supported()`, allocates `reserved_gids` arrays per RDMA port sized by the RoCE address table, initializes entries to `-1`, and initializes the MACsec device list and mutex. Event registration attaches a blocking notifier to `mdev->macsec_nh`. On SA-added events, `handle_macsec_gids()` finds or creates the MACsec-device record and installs SA rules for every saved RoCE GID. On SA-deleted events, `del_sa_roce_rule()` removes matching TX/RX SA rules.

GID add operations ignore non-RoCE-v2 GIDs and unsupported devices. They RCU-read `attr->ndev`, require an offloaded MACsec netdev, hold a netdev reference, then serialize on `dev->macsec.lock`. The code finds/creates the MACsec device, tries to find a physical GID with the same GID value, clears that physical hardware GID if found, records the physical GID in `reserved_gids`, adds MACsec RoCE steering, saves the RoCE GID address, and returns. GID delete reverses the ambiguity handling and removes steering/list entries.

## State And Persistence Behavior
All state is in memory: per-port `reserved_gids`, `dev->macsec.macsec_devices_list`, per-device GID and SA-rule lists, notifier registration, and referenced `ib_gid_attr` objects. Firmware or flow-steering state is changed through mlx5 MACsec rule helpers and `set_roce_addr()`. There is no disk persistence.

## Dependencies And Integration Points
`main.c` calls the add/delete hooks from `mlx5_ib_add_gid()` and `mlx5_ib_del_gid()`, initializes/deallocates MACsec state in the init stage, and registers/unregisters the notifier in the device-notifier stage. The file depends on Linux MACsec netdev helpers, RDMA GID cache APIs, mlx5 MACsec flow-steering helpers, and `set_roce_addr()` from `main.c`.

## Risks
Reference lifetimes are sensitive: physical GIDs found through `rdma_find_gid()` must be released exactly once, and MACsec netdev references are paired with `dev_hold()/dev_put()`. Ambiguous GID handling temporarily clears a physical GID slot; failure paths must restore it. `get_macsec_device()` creates records even in delete paths, so unexpected delete events can allocate empty records before `cleanup_macsec_device()` removes them. Concurrency relies on the MACsec mutex after RCU netdev lookup.

## Test Signals
Test adding/removing RoCE v2 GIDs on offloaded MACsec netdevs, SA add/delete notifier replay, duplicate/ambiguous GID addresses, IPv4-mapped and IPv6 GIDs, unsupported MACsec capability paths, and teardown with outstanding saved GIDs or SA rules.
