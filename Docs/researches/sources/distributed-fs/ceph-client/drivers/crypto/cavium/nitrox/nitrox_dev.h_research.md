# sources/distributed-fs/ceph-client/drivers/crypto/cavium/nitrox/nitrox_dev.h

Purpose: defines the central NITROX device model, queue structures, hardware-info structures, SR-IOV mailbox/VF state, device states, and CSR access helpers.

Important APIs and types: `struct nitrox_cmdq` represents command rings with response/backlog lists, doorbell/completion CSR addresses, DMA base, work item, counters, indices, and locks. `struct nitrox_hw`, `nitrox_stats`, `nitrox_q_vector`, `nitrox_vfdev`, `nitrox_iov`, and `nitrox_device` hold hardware identity, statistics, MSI-X vector/tasklet data, VF mailbox state, SR-IOV config, DMA pool, packet/AQM queues, and debugfs state. Inline helpers are `nitrox_read_csr()`, `nitrox_write_csr()`, `nitrox_ready()`, and `nitrox_vfdev_ready()`.

Control flow and state: state persists per PCI device and is mutated by probe, HAL config, request manager, ISR, SR-IOV, and crypto transform reference code.

Dependencies and integration points: depends on DMA, interrupt, PCI, networking-size constants, and all NITROX modules using `struct nitrox_device`.

Risks and test signals: risks include many locks/counters sharing one queue object, refcount/state ordering around device removal, SR-IOV mode changes while queues exist, and direct `readq()`/`writeq()` without accessors for barriers beyond MMIO semantics. Test signals include queue allocation on the correct NUMA node, atomic stats updates, device ready gating, VF state transitions, and no use-after-free with active crypto contexts.
