# sources/distributed-fs/ceph-client/net/smc/smc_ib.c

## Purpose
`smc_ib.c` is the SMC-R RDMA/InfiniBand client layer. It discovers RoCE devices and ports, tracks PNET IDs and network-device indexes, creates protection domains, completion queues, queue pairs, memory regions, and DMA mappings, transitions QPs through INIT/RTR/RTS, and notifies the SMC core when ports or devices appear, disappear, or lose valid GIDs.

## Important APIs, Types, and Functions
Global state includes `smc_ib_devices` and `local_systemid`. Public functions include `smc_ib_register_client()`, `smc_ib_unregister_client()`, `smc_ib_setup_per_ibdev()`, `smc_ib_create_protection_domain()`, `smc_ib_create_queue_pair()`, `smc_ib_ready_link()`, QP state modifiers, `smc_ib_determine_gid()`, `smc_ib_find_route()`, memory-region and DMA-sync helpers, `smc_ib_ndev_change()`, and `smcr_nl_get_device()`. The RDMA client callbacks are `smc_ib_add_dev()` and `smc_ib_remove_dev()`.

## Control Flow
Registration initializes a random local system ID prefix and calls `ib_register_client()`. Device add allocates `struct smc_ib_device`, registers an IB event handler, derives PNET IDs from device/port or the PNET table, records netdev ifindexes, and schedules port attribute work. Port event work refreshes `ib_port_attr` and MAC, marks ports going away on errors, calls `smcr_port_err()` on loss, calls `smcr_port_add()` on activation, and verifies existing link GIDs. Link creation uses `smc_ib_create_protection_domain()`, `smc_ib_create_queue_pair()`, and `smc_ib_ready_link()` to transition QPs and post initial receives. Device removal unregisters from lists, terminates affected SMC-R groups, destroys per-device CQs, unregisters event handlers, and frees state.

## State and Persistence
State is in-memory per RDMA device: port attributes, CQ pointers, tasklets owned by WR code, MACs, PNET IDs, port going-away bitmaps, link counters, netdev ifindexes, and a mutex protecting setup/cleanup. Memory mappings are represented in `smc_buf_desc` SG tables and MRs per link index. No durable state is written.

## Dependencies and Integration Points
The file integrates RDMA verbs/cache APIs, IPv4 route and neighbour lookup, VLAN/netdevice APIs, SMC PNET lookup, SMC core link failover/termination, SMC WR CQ handlers, and generic netlink device dump output. `smc_core.c` calls it during link and buffer setup, while RDMA event callbacks call back into core for failover and termination.

## Risks
RDMA device events can arrive in IRQ context and are deferred to workqueues, so port bitmaps and going-away flags must avoid lost transitions. GID selection differs between SMC-R v1 RoCE and SMC-R v2 RoCE UDP encapsulation, including route and subnet checks; mistakes can bind a link to an unusable GID or gateway. DMA mapping assumes the SMC protocol can use one contiguous DMA mapping result; partial or chained mappings must fail cleanly. Device removal must wait for link counters to drain to avoid freeing RDMA resources still used by links.

## Test Signals
Exercise RoCE device add/remove, port up/down, GID change, VLAN and non-VLAN paths, SMC-R v1 and v2 route selection, gateway and direct modes, QP fatal events, memory registration/unregistration under traffic, netlink device dumps, and module unload while links are active. Lockdep, KASAN, RDMA resource leak checks, and failover traffic continuity are strong signals.
