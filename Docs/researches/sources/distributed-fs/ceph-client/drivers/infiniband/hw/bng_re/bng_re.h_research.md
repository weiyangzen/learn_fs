<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_re.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_re.h

## Purpose
Defines top-level driver identity constants and core runtime structures for the Broadcom `bng_re` RoCE provider.

## Important APIs, Types, And Functions
- `BNG_RE_ADEV_NAME` is `bng_en`, used with `.rdma` for auxiliary-device matching.
- `BNG_RE_DESC` describes the module as `Broadcom 800G RoCE Driver`.
- `rdev_to_dev()` converts an `rdev` pointer to the embedded `ib_device`'s Linux device pointer.
- MSI-X constants define minimum and maximum RoCE vectors and CREQ NQ index.
- `struct bng_re_nq_db`, `bng_re_nq`, and `bng_re_nq_record` model notification queues, doorbells, MSI-X records, load accounting, tasklets, and CQ notification workqueues.
- `struct bng_re_en_dev_info` stores the RDMA device and BNGE auxiliary device associated with an auxiliary-bus instance.
- `struct bng_re_ring_attr` describes ring allocation inputs passed to HWRM ring allocation.
- `struct bng_re_dev` is the main per-device object embedding `ib_device` and all driver subsystems.

## Control Flow
The header has no executable flow, but it shapes the flow in `bng_dev.c`: auxiliary probe allocates `bng_re_en_dev_info`, `bng_re_dev_add()` allocates `bng_re_dev`, and initialization fills resource, firmware, stats, debugfs, and MSI-X fields.

## State And Persistence
`struct bng_re_dev` is the key persistent state container for a probed device. It stores flags for netdev registration and RCFW enablement, netdev/auxiliary pointers, chip context, resource manager, firmware channel, notification-queue record, device attributes, debugfs dentry, and stats context. `struct bng_re_nq_record` stores MSI-X entries copied from BNGE and per-vector NQ state.

## Dependencies And Integration Points
Includes `bng_res.h` and references RDMA core, BNGE auxiliary structures, PCI, netdevice, debugfs, workqueue, tasklet, mutex, and cpumask types. It is included by device, firmware, resource, and debugfs implementation files.

## Risks And Edge Cases
Several NQ fields are defined before full NQ implementation appears in this subset, so initialization and teardown must eventually cover tasklets, IRQs, workqueues, and load locking. `BNGE_INVALID_STATS_CTX_ID` is `-1` but stored in unsigned stats fields elsewhere, making sentinel interpretation dependent on casts. Structure ownership crosses RDMA and Ethernet drivers, so auxiliary device lifetime assumptions are important.

## Test Signals
Compilation across `bng_dev.c`, `bng_fw.c`, `bng_res.c`, and `bng_debugfs.c` validates structural consistency. Runtime probe/remove tests should confirm `bng_re_dev` fields are initialized before use and reset/freed in teardown, especially flags, `nqr`, debugfs, stats, and RCFW state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_re.h -->
