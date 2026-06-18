# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/device.c

## Purpose
`device.c` registers the MANA auxiliary RDMA driver, wires RDMA core operations, probes MANA RDMA/Ethernet auxiliary devices, and tears them down.

## Important APIs, Types, And Functions
`mana_ib_dev_ops` maps RDMA core verbs to MANA implementations for PD, ucontext, AH, CQ, QP, WQ, MR, mmap, query, posting, and notification. `mana_ib_stats_ops`, `mana_ib_device_stats_ops`, and `mana_ib_dev_dm_ops` are optional op sets. `mana_ib_probe()` allocates `struct mana_ib_dev`, queries capabilities, creates RNIC EQs/adapter when applicable, binds net devices to IB ports, creates the AV DMA pool, and registers the IB device. `mana_ib_remove()` drains GSI sends for RNIC, unregisters, destroys pools/adapters/EQs, and deallocates.

## Control Flow
Probe starts with `ib_alloc_device()` and base ops. For RNIC auxiliary devices it sets one initial port, derives node GUID from the primary netdev, queries RNIC caps, installs stats/device-memory ops, creates EQs and adapter, expands to multi-port if firmware supports it, associates each IB port with a primary netdev, configures each MAC in firmware, and registers a netdevice notifier. For Ethernet auxiliary devices it uses all MANA ports and Ethernet capability query. Both paths create an AV pool and call `ib_register_device()`. Unwind labels reverse setup based on RNIC mode.

## State And Persistence
`struct mana_ib_dev` owns `adapter_handle`, EQ pointers, the QP xarray, capability cache, AV DMA pool, netdevice notifier, and netdevice tracker. Port/netdev associations are registered with RDMA core and MAC/IP address state is configured in firmware. No state is persisted across module unload.

## Dependencies And Integration Points
The module imports `NET_MANA`, binds auxiliary IDs `mana.rdma` and `mana.eth`, uses MANA core GDMA and netdev contexts, RDMA core device registration, netdevice notifier handling, and address configuration helpers.

## Risks
Probe unwind after configuring several port MACs calls `mana_ib_gd_destroy_rnic_adapter()` but does not individually remove MACs; firmware adapter teardown must own that cleanup. `mana_ib_netdev_event()` handles only `NETDEV_CHANGEUPPER`; other link/address events rely on RDMA core or other paths. RNIC and Ethernet modes share many ops even though not all operations are meaningful in both modes, so mode checks in individual files are important.

## Test Signals
Test probe/remove for `mana.rdma` and `mana.eth`, capability query failures, EQ/adapter creation failures, multi-port setup, missing netdev on one port, notifier registration failure, AV pool allocation failure, netdev upper changes, device stats feature gating, and removal with outstanding GSI shadow sends.
