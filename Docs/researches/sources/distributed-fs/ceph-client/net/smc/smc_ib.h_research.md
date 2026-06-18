# sources/distributed-fs/ceph-client/net/smc/smc_ib.h

## Purpose
`smc_ib.h` defines the SMC-R RDMA device abstraction and declares the RDMA helper API used by core, LLC, PNET, and netlink code.

## Important APIs, Types, and Functions
The header defines `SMC_MAX_PORTS`, `SMC_GID_SIZE`, `SMC_IB_MAX_SEND_SGE`, `struct smc_ib_devices`, and `struct smc_ib_device`. It declares the global `smc_ib_devices` and `smc_lgr_list`. Inline helpers are `smc_ib_gid_to_ipv4()` and `smc_ib_net()`. Function declarations cover RDMA client registration, port activity, protection domains, QPs, QP readiness and error transitions, per-device setup, memory region registration, SG DMA mapping/syncing, GID determination, route lookup, local system ID validity, netdevice change handling, and netlink device dumping.

## Control Flow
The header establishes the flow expected by callers: discover/track devices through `smc_ib_register_client()`, initialize per-device CQs lazily through `smc_ib_setup_per_ibdev()`, create PD/QP resources per link, move QPs into a usable state with `smc_ib_ready_link()`, map buffers and MRs per link index, and call error/cleanup APIs during link teardown.

## State and Persistence
`struct smc_ib_device` keeps device-list linkage, RDMA device pointer, per-port attrs, CQs, tasklets, MAC and PNET IDs, initialized flag, work item, port masks, link counters, deletion wait queue, setup mutex, per-port link counters, and netdev ifindexes. The state is transient and tied to the RDMA client lifetime.

## Dependencies and Integration Points
The header depends on interrupt, Ethernet, mutex, wait, RDMA verbs, and SMC public headers. It is included by `smc_core.h`, `smc_ib.c`, and other SMC modules needing RDMA state. `smc_ib_net()` uses RDMA core network namespace state, and `smc_ib_gid_to_ipv4()` is used by SMC-R v2 routing and LLC add-link logic.

## Risks
The two-port maximum is encoded in arrays and counters, so any future hardware or protocol expansion needs careful resizing. Callers must use one-based RDMA port numbers when indexing with `ibport - 1`. DMA sync helpers require correct direction and link index. `smc_ib_net()` can return NULL if device state is absent, so callers need valid RDMA device lifetime.

## Test Signals
Compile with RDMA and IPv6 variations, then run SMC-R traffic over one and two ports, verify PNET table interactions, netdevice index updates, GID-to-IPv4 extraction for v2, and cleanup after RDMA client unregister.
