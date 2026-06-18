# sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_init.c

## Purpose
`csio_init.c` owns Linux module initialization, PCI driver registration, per-device allocation and teardown, debugfs setup, PCI resource enablement, queue configuration, SCSI host creation/removal, lnode blocking/unblocking, and PCI error recovery for the Chelsio FCoE storage driver.

## Important APIs and Functions
- Debugfs: `csio_mem_read()`, `csio_add_debugfs_mem()`, `csio_setup_debugfs()`, `csio_dfs_create()`, `csio_dfs_destroy()`, `csio_dfs_init()`, and `csio_dfs_exit()` expose adapter EDC/MC memory through chip ops.
- PCI setup: `csio_pci_init()` enables memory BARs, requests regions, sets bus mastering/MWI, and negotiates 64-bit then 32-bit DMA masks. `csio_pci_exit()` releases these resources.
- Worker setup: `csio_hw_init_workers()` initializes `hw->evtq_work`; `csio_hw_exit_workers()` cancels it synchronously.
- Queue lifecycle: `csio_config_queues()` allocates host queue memory, selects interrupt mode, sizes per-port/per-CPU SCSI queue sets, allocates FW-event/management/SCSI queues, creates firmware queues, and requests IRQs. `csio_create_queues()` registers already allocated queue objects with firmware.
- Resource lifecycle: `csio_resource_alloc()` creates mailbox and rnode mempools plus the SCSI DMA response pool. `csio_resource_free()` destroys them.
- Hardware lifecycle: `csio_hw_alloc()` allocates `struct csio_hw`, maps BAR0, initializes workers and hardware modules, and creates per-device debugfs. `csio_hw_free()` disables interrupts, cancels workers, exits hardware modules, unmaps BAR0, removes debugfs, and frees pools.
- SCSI host lifecycle: `csio_shost_init()` allocates the right physical/vport SCSI host template, initializes lnode state, sets queue limits, attaches FC transport, and calls `scsi_add_host_with_dma()`. `csio_shost_exit()` removes FC/SCSI host state, flushes queued events, exits the lnode, and drops the host reference.
- Lnode operations: `csio_lnodes_block_request()`, `csio_lnodes_unblock_request()`, `csio_lnodes_block_by_port()`, `csio_lnodes_unblock_by_port()`, and `csio_lnodes_exit()` snapshot lnode lists under `hw->lock`, then block/unblock/remove hosts outside the list traversal.
- Probe/remove/error recovery: `csio_probe_one()`, `csio_remove_one()`, `csio_pci_error_detected()`, `csio_pci_slot_reset()`, and `csio_pci_resume()` implement the PCI callback paths.
- Module entry/exit: `csio_init()` attaches FC transports and registers the PCI driver; `csio_exit()` unregisters PCI/debugfs/transports. The file declares module metadata and firmware dependencies.

## Control Flow and State
Module load creates the root debugfs directory, attaches physical and vport FC transport templates, and registers `csio_pci_driver`. On probe, the driver filters for T5/T6 IDs, enables PCI resources, allocates/maps/initializes `csio_hw`, records relaxed-ordering state, starts the hardware state machine, then creates and starts one physical lnode/SCSI host per physical port. After each lnode starts, `csio_lnode_init_post()` initializes FC host attributes and scans the SCSI host.

Removal and error paths block SCSI requests before stopping hardware or posting PCI-error events, then unblock only long enough for normal teardown routines to drain/complete, remove lnodes, free hardware, and release PCI resources. PCI error recovery tears down lnodes and interrupts on detection, re-enables/restores PCI state on slot reset, posts `CSIO_HWE_PCIERR_SLOT_RESET`, and recreates lnodes on resume if hardware reaches ready state.

## State and Persistence Behavior
All runtime state is in kernel memory. `csio_debugfs_root`, `csio_fcoe_transport`, and `csio_fcoe_transport_vport` are module-global handles. Per-device state lives in `struct csio_hw` and is attached with `pci_set_drvdata()`. Queue allocation state is tracked by `CSIO_HWF_Q_MEM_ALLOCED` and `CSIO_HWF_Q_FW_ALLOCED`; interrupt state is tracked by `hw->intr_mode` and host/hardware interrupt flags. `hw->num_lns`, `hw->rln`, `hw->sln_head`, and each lnode's child list are mutated during host creation/removal.

## Dependencies and Integration Points
This file integrates with Linux PCI, DMA API, debugfs, SCSI mid-layer, FC transport, module infrastructure, and PCI error recovery. Driver-local dependencies include `csio_hw`, `csio_wr`, `csio_mb`, `csio_scsi`, `csio_lnode`, `csio_rnode`, and FC transport attribute code from other CSIostor files. Queue creation calls into `csio_wr_*`; host templates and tunables come from SCSI code; lnode start/stop calls into FCoE mailbox paths.

## Risks and Edge Cases
- `csio_config_queues()` calls `csio_intr_enable()` before all queues are allocated; failure paths must reliably disable interrupts and free partially created resources.
- `csio_create_queues()` marks `CSIO_HWF_Q_FW_ALLOCED` only after all firmware queue creation succeeds, but partial failures rely on `csio_wr_destroy_queues(hw, true)`.
- Lnode list snapshot arrays are allocated with `hw->num_lns`; races with lnode creation/removal would overflow if not serialized by higher-level lifecycle expectations.
- `csio_probe_one()` returns success in debug mode after `csio_hw_start()` returns `-EINVAL`, leaving hardware allocated but not normal-host initialized; this path needs operational clarity.
- PCI resume failure calls `csio_hw_free()` but does not release PCI regions in that function; ownership is tied to the outer PCI lifecycle.

## Test Signals
Probe tests should verify PCI enablement, BAR mapping, `pci_set_drvdata()`, queue flags, IRQ request success, SCSI host registration, FC host scan, and clean unwind at each forced failure point. Remove and PCI error tests should assert requests are blocked, events flushed, lnodes unregistered, interrupts freed, workers canceled, and no debugfs or DMA/mempool resources remain. Runtime signals include link scan completion, correct number of SCSI hosts for `hw->num_pports`, and stable behavior under MSI-X/MSI/INTx modes.
