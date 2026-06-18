# sources/distributed-fs/ceph-client/drivers/net/ethernet/microsoft/mana/gdma_main.c

## Purpose
`gdma_main.c` is the core PCI/GDMA layer for the Microsoft Azure Network Adapter. It probes and removes the PCI device, maps BAR0, validates doorbell/shared-memory register windows, creates the hardware command channel, negotiates firmware capabilities, manages GDMA queues and DMA regions, sets up MSI-X interrupts, dispatches EQ/CQ events, handles service/recovery events, and registers the Ethernet and RDMA-facing GDMA devices.

## Important APIs, Types, and Functions
- Global state: `mana_debugfs_root` and `mana_dev_recovery_work`.
- PCI lifecycle: `mana_gd_probe()`, `mana_gd_remove()`, `mana_gd_suspend()`, `mana_gd_resume()`, `mana_gd_shutdown()`, `mana_driver_init()`, and `mana_driver_exit()`.
- Register setup: `mana_gd_init_pf_regs()`, `mana_gd_init_vf_regs()`, and `mana_gd_init_registers()`.
- Firmware command wrapper: `mana_gd_send_request()` delegates to `mana_hwc_send_request()`.
- Resource discovery: `mana_gd_verify_vf_version()`, `mana_gd_query_hwc_timeout()`, `mana_gd_query_max_resources()`, and `mana_gd_detect_devices()`.
- Memory, DMA region, queue, WQE, CQ, EQ, IRQ, and service/recovery helpers are exported or used internally to support MANA Ethernet/RDMA clients.

## Control Flow
Probe enables PCI, requests regions, configures 64-bit DMA, allocates and stores `struct gdma_context`, maps BAR0, initializes xarrays/debugfs, and calls `mana_gd_setup()`. Setup validates PF/VF register offsets, initializes the shared-memory channel, creates a service workqueue, allocates HWC IRQs, creates HWC, verifies firmware version/capabilities, queries maximum resources, allocates remaining IRQs, and detects MANA and MANA IB devices. Probe then calls `mana_probe()` for Ethernet and `mana_rdma_probe()` for RDMA, finally marking `GC_PROBE_SUCCEEDED`. Failures unwind in reverse order and may schedule delayed recovery on `-ETIMEDOUT` or `-EPROTO`.

The event path starts in `mana_gd_intr()`, which iterates registered EQs under RCU. `mana_gd_process_eq_events()` consumes up to five EQEs, validates owner bits, applies a read barrier, dispatches each EQE, advances the head, and rearms the EQ doorbell. Completion EQEs find the target CQ by ID in `gc->cq_table`; HWC initialization/data/service EQEs call registered callbacks; reset/reconfiguration events schedule service work.

Queue creation allocates coherent memory, creates a firmware DMA region for normal MANA queues, initializes software queue state, optionally creates a hardware EQ through firmware, tests EQ delivery, and registers IRQ context. WQE posting validates sizes and SGE counts, writes inline OOB and SGL data with ring-wrap handling, advances the queue head in GDMA basic units, and rings the doorbell.

## State and Persistence
Runtime state lives in `struct gdma_context` attached to `pci_set_drvdata()`: BAR mappings, doorbell geometry, shared-memory base, IRQ xarray, CQ table, HWC and MANA device structs, service workqueue, flags, and resource limits. Queue state lives in `struct gdma_queue` heads/tails, IDs, DMA memory descriptors, and callbacks. Persistent kernel-visible side effects are PCI driver registration, debugfs directories, IRQ registrations, DMA mappings, firmware-created DMA regions, and workqueue items.

## Dependencies and Integration Points
- Depends on PCI, MSI/MSI-X, IRQ affinity, DMA coherent memory, debugfs, workqueues, xarray, RCU, and CPU topology APIs.
- Includes and exports symbols under namespace `NET_MANA` for Ethernet/RDMA MANA code.
- Integrates with `hw_channel.c` for firmware requests, `shm_channel.o` for bootstrap shared memory, `mana_probe()/mana_remove()` for Ethernet, and `mana_rdma_probe()/mana_rdma_remove()` for RDMA.

## Risks and Edge Cases
- BAR validation is security-critical. The code checks doorbell page size, doorbell offset, SR-IOV base/shared-memory offsets, and doorbell ID bounds before MMIO arithmetic.
- Dynamic MSI-X handling has separate setup and cleanup paths; partial allocation failures must free requested IRQs and erase xarray entries without leaking affinity hints.
- EQ/CQ owner-bit overflow or wrong CQ mapping can drop events or stall completions.
- HWC timeouts are special: logging may be suppressed when timeout is deliberately zero, and recovery may reduce further HWC waits.
- Recovery work keeps PCI device references and must be drained on module exit to avoid use-after-free.

## Test Signals
- Build and module load/unload tests with both PF and VF IDs.
- Fault-injection for BAR sizes/offsets, DMA allocation failures, firmware status failures, timeout paths, and partial IRQ allocation.
- Runtime signals include successful HWC EQ test, resource query success, device list detection, debugfs directory creation/removal, and absence of leaked IRQ/DMA/debugfs resources after remove.
