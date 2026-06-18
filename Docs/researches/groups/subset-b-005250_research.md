# subset-b-005250 Research

Grouped source research for Chelsio CSIostor FCoE driver files under `sources/distributed-fs/ceph-client/drivers/scsi/csiostor/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_hw.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_hw.h

## Purpose
`csio_hw.h` is the central hardware contract for the Chelsio FCoE storage driver. It defines the per-PCI-function `struct csio_hw`, queue sizing, interrupt modes, event queue objects, physical-port state, firmware capability/link abstractions, FCoE resource accounting, hardware state-machine events, register access helpers, logging helpers, and the cross-module APIs used by initialization, interrupt, mailbox, SCSI, work-request, lnode, and rnode code.

## Important APIs, Types, and Constants
- Hardware limits include `CSIO_MAX_PPORTS`, `CSIO_MAX_SCSI_QSETS`, `CSIO_MAX_MSIX_VECS`, `CSIO_MAX_QUEUE`, `CSIO_MAX_LUN`, and the T6 firmware floor `CSIO_MIN_T6_FW`.
- Queue constants define interrupt, firmware-event, and management queue sizes, including `CSIO_INTR_IQSIZE`, `CSIO_FWEVT_IQSIZE`, `CSIO_FWEVT_FLBUFS`, `CSIO_MGMT_EQSIZE`, and `CSIO_MGMT_IQSIZE`.
- `struct csio_scsi_qset` records ingress/egress queue indices and vector index for each port/CPU SCSI queue pair.
- `enum csio_evt` and `struct csio_evt_msg` define the slow-path event queue used for firmware events, mailbox completions, state-change notifications, and rnode device-loss work.
- `struct csio_mgmtm` tracks management ELS/CT queues, outstanding requests, timer, and stats.
- `struct link_config`, `enum fw_caps`, `enum cc_pause`, and `enum cc_fec` normalize firmware link capability formats into driver-side link state.
- `struct csio_pport` stores per-physical-port identifiers, MAC, link status/speed, module type, and current `link_config`.
- `struct csio_fcoe_res_info` mirrors firmware FCoE resource limits and usage for exchanges, sessions, FCFs, and VNPs.
- `enum csio_hw_ev` names hardware state-machine inputs for configure/init/reset/download/remove/suspend/resume and PCI error recovery.
- `struct csio_hw_stats` records event queue counts, interrupt anomalies, mailbox/PL interrupt anomalies, error counts, and per-hardware-event counts.
- `struct csio_hw` is the main persistent in-memory object. It owns state-machine state, spinlock, SCSI/work-request/mailbox/management submodules, BAR mapping, SCSI queue sets, event queues, lnode lists, firmware/board identity, FCoE resources, memory pools, DMA pool, interrupt mode/vector metadata, chip ops, debugfs root, and stats.
- Register macros `csio_rd_reg*()` and `csio_wr_reg*()` wrap MMIO accesses through `hw->regstart`.
- Public APIs include hardware lifecycle (`csio_hw_init`, `csio_hw_start`, `csio_hw_stop`, `csio_hw_reset`, `csio_hw_exit`), interrupt management (`csio_request_irqs`, `csio_intr_enable`, `csio_intr_disable`, `csio_hw_slow_intr_handler`, `csio_hw_intr_disable`), firmware-event queue handling (`csio_fwevtq_handler`, `csio_evtq_worker`, `csio_enqueue_evt`, `csio_evtq_flush`), queue configuration (`csio_config_queues`), and link capability conversion helpers.

## Control Flow and State
The header declares the shared state transitions rather than implementing them. `struct csio_hw.sm` is the top-level hardware state machine, driven by `enum csio_hw_ev`. Initialization code allocates and initializes `csio_hw`, starts the hardware state machine, configures queues, and registers SCSI hosts. Interrupt code checks `CSIO_HWF_*` flags and schedules `evtq_work`. Mailbox code uses `hw->mbm`, `CSIO_HWF_HOST_INTR_ENABLED`, and `CSIO_HWF_HW_INTR_ENABLED` to decide whether asynchronous mailbox commands may be issued.

`hw->flags` is the key volatile state bitmap:
- `CSIO_HWF_MASTER` identifies the function that can perform master firmware operations.
- `CSIO_HWF_HW_INTR_ENABLED` and `CSIO_HWF_HOST_INTR_ENABLED` track hardware-side and host-side interrupt enablement.
- `CSIO_HWF_FWEVT_PENDING` and `CSIO_HWF_FWEVT_STOP` gate slow-path firmware event processing.
- `CSIO_HWF_Q_MEM_ALLOCED` and `CSIO_HWF_Q_FW_ALLOCED` separate host queue-memory allocation from firmware queue creation.
- `CSIO_HWF_VPD_VALID`, `CSIO_HWF_DEVID_CACHED`, `CSIO_HWF_USING_SOFT_PARAMS`, and `CSIO_HWF_ROOT_NO_RELAXED_ORDERING` capture initialization-time facts used by hardware and mailbox setup.

## Dependencies and Integration Points
The file depends on Linux PCI, device, workqueue, mempool, IO, spinlock, and SCSI FC transport headers. Driver-local dependencies include `t4_hw.h`, `t4_regs.h`, `t4_msg.h`, `csio_hw_chip.h`, `csio_wr.h`, `csio_mb.h`, `csio_scsi.h`, and `csio_defs.h`. It is included by most CSIostor implementation files and is the common integration point for chip-specific ops (`struct csio_hw_chip_ops`), mailbox command handling, work-request queues, SCSI completion paths, and lnode/rnode discovery.

## Risks and Edge Cases
- `struct csio_hw` is large and embeds arrays sized by `CSIO_MAX_PPORTS * CSIO_MAX_SCSI_CPU`; queue/vector calculations must stay within these compile-time bounds.
- State flags are mutated under `hw->lock` in many paths but not all helper macros enforce locking; misuse can race interrupt/workqueue paths.
- MMIO macros assume `hw->regstart` is valid and mapped; teardown must disable interrupts/work before `iounmap`.
- `csio_core_ticks_to_us()` and `csio_us_to_core_ticks()` depend on valid `hw->vpd.cclk`.
- `CSIO_GLBL_INTR_MASK` must match supported hardware interrupt cause bits; missing bits can hide fatal conditions.

## Test Signals
Useful validation signals include successful probe/start with expected `hw->fwrev_str`, correct interrupt mode selection, queue allocation flags transitioning to set states, nonzero event free-list accounting, link up/down events updating `pport`, and absence of unexpected interrupt/event stats. Fault-injection tests should cover queue allocation failure, mailbox timeout, PCI channel offline, event queue overflow, and reset/remove teardown ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_hw_chip.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_hw_chip.h

## Purpose
`csio_hw_chip.h` defines chip-generation identification, firmware/config filenames, PCI device-table helpers, firmware version macros, memory-window constants, interrupt descriptor records, and the chip-specific operations table used by the hardware layer. It lets generic CSIostor code call T5/T6-specific register and memory routines through `struct csio_hw_chip_ops`.

## Important APIs, Types, and Constants
- Chip/device constants: `CSIO_HW_T5`, `CSIO_T5_FCOE_ASIC`, `CSIO_HW_T6`, `CSIO_T6_FCOE_ASIC`, and `CSIO_HW_CHIP_MASK`.
- Firmware assets: `FW_FNAME_T5`, `FW_CFG_NAME_T5`, `FW_FNAME_T6`, and `FW_CFG_NAME_T6`.
- `CHELSIO_CHIP_CODE`, `CHELSIO_CHIP_VERSION`, and `CHELSIO_CHIP_RELEASE` encode/decode chip revision values.
- `enum chip_type` names supported T5/T6 revisions.
- `csio_is_t5()` and `csio_is_t6()` classify PCI device IDs after masking.
- `CSIO_DEVICE()` builds PCI table entries for Chelsio devices.
- `FW_VERSION()` and `FW_INTFVER()` bridge generated firmware version headers into driver comparisons.
- `struct fw_info` packages chip ID, firmware filename/module name, and expected `fw_hdr`.
- Memory constants include `MEM_EDC0`, `MEM_EDC1`, `MEM_MC`, `MEM_MC0`, `MEM_MC1`, `MEMWIN_APERTURE`, and `MEMWIN_BASE`.
- `struct intr_info` describes slow-path interrupt cause bits with message, stat index, and fatality.
- `struct csio_hw_chip_ops` exposes chip-specific methods for memory-window setup, PCIe interrupt handling, flash config address lookup, MC/EDC reads, generic memory read/write, and debugfs external memory creation.

## Control Flow and State
This header holds no persistent runtime state beyond type definitions. Runtime selection happens in hardware initialization, which fills `hw->chip_ops` with the externally defined `t5_ops` for supported T5/T6 paths. Generic code then calls `hw->chip_ops` from debugfs, interrupt handling, firmware config loading, and memory access paths.

## Dependencies and Integration Points
It includes `csio_defs.h`, `t4fw_api.h`, and `t4fw_version.h`, and forward-declares `struct csio_hw`. `csio_hw_t5.c` implements the exported `t5_ops`; `csio_init.c` uses `FW_FNAME_T5/FW_FNAME_T6` in module firmware declarations; PCI probe uses `csio_is_t5()`/`csio_is_t6()`.

## Risks and Edge Cases
- `csio_is_t5()` and `csio_is_t6()` compare only the masked chip-generation value, so callers must mask the PCI device with `CSIO_HW_CHIP_MASK`.
- T6 constants are declared, but this subset only includes the T5 ops implementation; generic code must ensure the selected ops are valid for the actual chip.
- Firmware filenames and version macros depend on external firmware headers and installed firmware blobs.
- `struct intr_info.stat_idx` is a raw index; users must keep it synchronized with the stats structures they increment.

## Test Signals
Probe should accept only masked T5/T6 IDs. Firmware loading tests should confirm the declared `MODULE_FIRMWARE()` names exist. Chip-op tests should verify `hw->chip_ops` is non-null and methods match the generation being probed. Interrupt tests can validate that `intr_info` tables log fatal and nonfatal causes correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_hw_chip.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_hw_t5.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_hw_t5.c

## Purpose
`csio_hw_t5.c` implements the chip-operation table for Chelsio T5-class hardware. It handles PCIe memory-window programming, PCIe slow-path interrupt decoding, flash configuration address lookup, backdoor MC/EDC memory reads, generic adapter memory read/write through PCIe windows, and debugfs exposure of external memory regions.

## Important APIs and Functions
- `csio_t5_set_mem_win()` programs a T5 PCIe memory access window at `MEMWIN_BASE` with `MEMWIN_APERTURE` and reads it back to flush propagation.
- `csio_t5_pcie_intr_handler()` checks `PCIE_INT_CAUSE_A` against a static `intr_info` table of PCIe parity/queue/DMA errors; fatal bits call `csio_hw_fatal_err()`.
- `csio_t5_flash_cfg_addr()` returns `FLASH_CFG_START` for firmware configuration lookup.
- `csio_t5_mc_read()` uses MC BIST command/status registers to read a 64-byte aligned memory-controller block and optional ECC word.
- `csio_t5_edc_read()` performs the equivalent BIST read for EDC memory, with local T5 EDC register stride macros.
- `csio_t5_memory_rw()` maps EDC/MC memory type and offset into the PCIe memory window and loops over aperture-sized windows to read/write 32-bit words.
- `csio_t5_dfs_create_ext_mem()` adds debugfs files for `mc0` and `mc1` when the corresponding external-memory enable bits are set.
- `t5_ops` exports these functions through `struct csio_hw_chip_ops`.

## Control Flow and State
This file operates on `struct csio_hw` but does not own long-lived state. Its memory-window functions mutate adapter registers via MMIO. MC/EDC reads first verify no BIST is active, program aligned address/length/pattern fields, start BIST, wait for completion through `csio_hw_wait_op_done_val()`, then copy status registers into caller-provided buffers in network byte order. `csio_t5_memory_rw()` computes memory offsets from MA BAR size registers, moves a PCIe memory window over the requested region, and transfers words until `len` is exhausted.

## Dependencies and Integration Points
The file includes `csio_hw.h` and `csio_init.h`. It relies on register macros from `t4_regs.h` and bitfield macros from the T4/T5 hardware headers. Debugfs integration calls `csio_add_debugfs_mem()`. Fatal PCIe error reporting flows into `csio_hw_fatal_err()`. The exported `t5_ops` is selected by the generic hardware initialization path.

## Risks and Edge Cases
- `csio_t5_memory_rw()` rejects unaligned `addr` or `len`, but assumes `buf` points to enough 32-bit storage.
- Memory-type offset calculation depends on EDC/MC size registers; incorrect hardware values can map to the wrong adapter region.
- MC/EDC BIST reads return `-EBUSY` if a BIST is already running and rely on a fixed wait loop of ten one-unit polls.
- `csio_t5_edc_read()` uses `EDC_DATA(i) + idx`, which is compact but easy to misread; register layout changes would need careful review.
- PCIe interrupt handling treats most parity errors as fatal, so false positives can force adapter reset.

## Test Signals
Debugfs memory files should appear for enabled EDC/MC regions and return data without kernel faults. Tests should cover unaligned memory read/write rejection, busy BIST handling, PCIe fatal interrupt injection, and memory-window programming readback. Hardware bring-up logs should show `t5_ops` functions succeeding before queue and FCoE initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_hw_t5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_init.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_init.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_init.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_init.h

## Purpose
`csio_init.h` is the OS-integration header for the CSIostor driver. It exposes module identity strings, FC transport templates, SCSI host/lnode lifecycle helpers, interrupt callback entry points used by the work-request layer, debugfs helpers, and lock-wrapped SCSI request/free-list helpers.

## Important APIs, Types, and Constants
- Module metadata constants: `CSIO_DRV_AUTHOR`, `CSIO_DRV_DESC`, and `CSIO_DRV_VERSION`.
- External FC transport templates: `csio_fc_transport_funcs` and `csio_fc_transport_vport_funcs`.
- Attribute setup: `csio_fchost_attr_init()`.
- INTx work-request callbacks: `csio_scsi_intx_handler()` and `csio_fwevt_intx_handler()`.
- Lnode request control: `csio_lnodes_block_request()`, `csio_lnodes_unblock_request()`, `csio_lnodes_block_by_port()`, and `csio_lnodes_unblock_by_port()`.
- SCSI host lifecycle: `csio_shost_init()`, `csio_shost_exit()`, and `csio_lnodes_exit()`.
- Debugfs memory helper: `csio_add_debugfs_mem()`.
- `csio_ln_to_shost()` converts embedded `struct csio_lnode` hostdata back to `struct Scsi_Host`.
- Lock helpers `csio_get_scsi_ioreq_lock()`, `csio_put_scsi_ioreq_lock()`, `csio_put_scsi_ioreq_list_lock()`, and `csio_put_scsi_ddp_list_lock()` serialize SCSI I/O request and DDP freelist operations.

## Control Flow and State
This header does not own state. It provides inline wrappers used in interrupt and completion paths: request freelist operations lock `scsim->freelist_lock`; DDP list return locks `hw->lock`. SCSI host conversion assumes `struct csio_lnode` is stored in `Scsi_Host.hostdata`.

## Dependencies and Integration Points
It includes Linux PCI, Ethernet, SCSI, SCSI host, and FC transport headers plus `csio_scsi.h`, `csio_lnode.h`, `csio_rnode.h`, and `csio_hw.h`. It is consumed by initialization, interrupt, chip/debugfs, and management code that needs OS-facing lifecycle functions.

## Risks and Edge Cases
- The lock helpers accept `hw` in some cases only to match calling conventions; callers must pass the correct `scsim` for the hardware instance.
- `csio_ln_to_shost()` depends on the exact allocation pattern in `csio_shost_init()`; embedding changes would break conversion.
- The DDP-list helper locks `hw->lock`, while other request-list helpers lock `scsim->freelist_lock`; mixing these in new code can introduce lock-order concerns.

## Test Signals
Compile coverage is important because this header ties many modules together. Runtime signals include successful SCSI host conversion in completion/removal paths, no double-free on ioreq list return, and no lockdep issues in interrupt-context use of the inline helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_init.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_isr.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_isr.c

## Purpose
`csio_isr.c` implements the interrupt service layer for CSIostor. It handles non-data/slow-path interrupts, firmware event queue interrupts, SCSI completion queue interrupts, combined INTx/MSI interrupts, MSI-X vector naming and requesting, interrupt mode selection, MSI-X vector reduction/affinity distribution, and interrupt teardown.

## Important APIs and Functions
- `csio_nondata_isr()` handles MSI-X non-data interrupts: slow hardware interrupt causes, mailbox ISR, and scheduling of the event worker.
- `csio_fwevt_handler()` drains the firmware-event ingress queue through `csio_fwevtq_handler()` and schedules `evtq_work`.
- `csio_fwevt_isr()` is the MSI-X firmware-event ISR; `csio_fwevt_intx_handler()` is the work-request callback used in INTx mode.
- `csio_process_scsi_cmpl()` converts SCSI completion WRs into driver request state transitions, including abort/close special handling and protection against double completion after abort timeout races.
- `csio_scsi_isr_handler()` drains an ingress queue with `csio_wr_process_iq()`, invokes each completed request callback, frees DDP buffers if used, and returns ioreqs to the SCSI freelist.
- `csio_scsi_isr()` is the MSI-X SCSI ISR; `csio_scsi_intx_handler()` is the INTx callback.
- `csio_fcoe_isr()` is the shared INTx/MSI ISR for slow-path, forward interrupt queue, mailbox, and firmware event scheduling.
- `csio_request_irqs()` requests either one INTx/MSI line or the MSI-X vector set for non-data, firmware event, and per-port/per-CPU SCSI queues.
- `csio_enable_msix()` allocates MSI-X vectors with affinity sets and reduces queue sets if fewer vectors are available.
- `csio_intr_enable()` chooses MSI-X, MSI, or INTx based on `csio_msi`, firmware queue limits, and vector allocation results.
- `csio_intr_disable()` disables hardware interrupts, frees requested IRQs when asked, frees vectors, and clears host interrupt state.

## Control Flow and State
The preferred MSI-X flow splits work by vector: non-data handles slow hardware and mailbox events, firmware-event handles FCoE/port/mailbox event queue messages, and each SCSI vector handles one ingress queue. In MSI/INTx mode, `csio_fcoe_isr()` disables INTx at the PF if needed, handles slow interrupts, processes the forward interrupt queue, handles mailbox completion, then schedules the event worker when new firmware events are pending.

`CSIO_HWF_FWEVT_PENDING` prevents redundant scheduling of `hw->evtq_work`. `hw->intr_mode`, `hw->msix_entries`, `hw->sqset[*][*].intr_idx`, `hw->fwevt_intr_idx`, and `hw->nondata_intr_idx` persist the interrupt topology selected during queue configuration.

## Dependencies and Integration Points
The file uses Linux interrupt, PCI, CPU affinity, and cpumask APIs. It integrates with `csio_hw_slow_intr_handler()`, mailbox ISR/completions, work-request ingress processing, SCSI completion state machine, and queue/IRQ data allocated by `csio_config_queues()`.

## Risks and Edge Cases
- All ISR paths first reject null device data and offline PCI channels; missing this check in new handlers could touch dead MMIO.
- `csio_process_scsi_cmpl()` explicitly handles abort timeout races by checking whether `csio_scsi_cmnd(ioreq)` is null; regressions could double-complete commands.
- `csio_request_irqs()` frees vectors on partial MSI-X request failure using already assigned `dev_id`s; vector count and `entryp[k]` must remain synchronized.
- `csio_intr_disable(free=true)` loops over `hw->num_sqsets + CSIO_EXTRA_VECS`; this must match the number of successfully requested vectors after any queue-set reduction.
- MSI/INTx fallback can reduce SCSI queue sets when firmware supports fewer IQs; tests should cover low-vector and low-queue firmware configurations.

## Test Signals
Runtime signals include correct interrupt mode log, requested vector names, SCSI completion callbacks firing once per command, firmware events processed by `evtq_work`, and mailbox completions moving from ISR to event worker. Fault tests should inject PCI channel offline, partial IRQ request failure, low MSI-X vector count, abort completion races, and INTx interrupt masking/unmasking behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_isr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_lnode.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_lnode.c

## Purpose
`csio_lnode.c` implements local FCoE node management. It translates firmware link/rdev events into local-node state transitions, reads FCF/VNP parameters, starts/stops FCoE links, manages physical and NPIV lnode relationships, drives rnode state fan-out, performs FDMI management registration, handles ELS/CT management completions, exposes FC transport async events, and initializes/exits lnode resources.

## Important APIs and Functions
- Tunables: `csio_fcoe_rnodes` limits remote nodes and `csio_fdmi_enable` controls FDMI registration.
- Lookup helpers: `csio_ln_lookup_by_portid()`, `csio_ln_lookup_by_vnpi()`, and `csio_lnode_lookup_by_wwpn()` find physical or child lnodes.
- FDMI helpers build DHBA, DPRT, RHBA, and RPA CT requests through callbacks `csio_ln_fdmi_dhba_cbfn()`, `csio_ln_fdmi_dprt_cbfn()`, `csio_ln_fdmi_rhba_cbfn()`, and `csio_ln_fdmi_done()`.
- `csio_ln_vnp_read()` and `csio_ln_vnp_read_cbfn()` issue/read firmware VNP state, updating MAC, NPort ID, WWNN/WWPN, and service parameters.
- `csio_fcoe_enable_link()` sends FCoE link up/down mailbox commands and records WWNs and physical MAC on link-up responses.
- `csio_ln_read_fcf_entry()` and `csio_ln_read_fcf_cbfn()` read and persist FCF parameters.
- `csio_handle_link_up()` and `csio_handle_link_down()` process firmware link events and post lnode state-machine events.
- `csio_post_event_rns()`, `csio_cleanup_rns()`, `csio_post_event_lns()`, and `csio_ln_down()` cascade events to remote nodes and child NPIV lnodes.
- State handlers `csio_lns_uninit()`, `csio_lns_online()`, `csio_lns_ready()`, and `csio_lns_offline()` implement local-node lifecycle.
- `csio_get_phy_port_stats()` reads FCoE port stats over three mailbox reads.
- `csio_fcoe_fwevt_handler()` demultiplexes firmware FCoE link commands, RDEV payloads, and ELS/CT completions.
- Public lifecycle APIs include `csio_lnode_start()`, `csio_lnode_stop()`, `csio_lnode_close()`, `csio_lnode_init()`, and `csio_lnode_exit()`.
- Management request helpers `csio_ln_prep_ecwr()`, `csio_ln_mgmt_submit_wr()`, and `csio_ln_mgmt_submit_req()` build and submit ELS/CT work requests through the management EQ.

## Control Flow and State
Firmware link-up events call `csio_handle_link_up()`, associate or allocate an lnode for the VNP, set `fcf_flowid`/`vnp_flowid`, and post `CSIO_LNE_LINKUP`. In `uninit` or `offline`, link-up moves the lnode to `online`, reads FCF info for physical lnodes, and reads VNP parameters. Later RDEV fabric-login events map through `fwevt_to_lnevt` to `CSIO_LNE_FAB_INIT_DONE`, moving `online` to `ready` and sending FC link-up async notifications.

Link-down and driver stop paths post `CSIO_LNE_LINK_DOWN` or `CSIO_LNE_DOWN_LINK`, move ready lnodes to `offline`, fan out `CSIO_RNFE_DOWN` to rnodes, send FC link-down notifications, and remove physical FCF list entries. Close paths move lnodes to `uninit` and close rnodes. `csio_notify_lnodes()` is called by hardware state changes to start, stop, reset, or remove all lnodes.

## State and Persistence Behavior
Each `struct csio_lnode` persists WWNs, NPort ID, MAC, FCF/VNP flowids, FCF info reference, FDMI management request/DMA buffer, child list, rnode list, FC transport state, target discovery counters, flags, and stats. Root and non-root physical lnodes own FCF info allocations; NPIV lnodes share the parent's FCF info by kref. FDMI allocates one `csio_ioreq` and a 2048-byte coherent DMA buffer per eligible physical lnode.

## Dependencies and Integration Points
The file integrates with mailbox command builders, work-request submission, SCSI target discovery, FC transport async events, kernel UTS name for FDMI OS/host attributes, and rnode registration. `csio_fcoe_fwevt_handler()` is called from the firmware-event worker in the hardware module. `csio_lnode_start()`/`stop()` are invoked by probe, hardware notifications, and port disable/enable flows.

## Risks and Edge Cases
- In `csio_handle_link_up()`, the allocation path for a new VN-Port drops and reacquires `hw->lock`; code must ensure the intended `ln` pointer is updated after allocation.
- FDMI uses a single `ln->mgmt_req`; overlapping FDMI sequences on one lnode would contend for the same request/DMA buffer.
- `csio_ln_mgmt_submit_req()` uses `BUG_ON(pld_len > pld->len)`, so malformed callers can crash the kernel instead of returning an error.
- State handlers contain TODO comments for hardware reset on FCF/VNP read failure; current behavior increments errors but may leave the lnode partly online.
- FCF info reference handling differs between root, physical non-root, and NPIV lnodes; teardown ordering must avoid kref underflow or leaks.
- Management WR completion trusts the firmware cookie as an `ioreq` pointer after validating active queue membership.

## Test Signals
Important tests include link-up to ready transition, link-down to offline transition, repeated link-up/down drops, invalid FCF/VNP/rdev IDs, FDMI enable/disable, management WR completion, NPIV child allocation/removal, and SCSI scan completion heuristics in `csio_scan_done()`. Runtime signals include FC async link events, correct WWPN/WWNN attributes, FCF list membership, rnode close fan-out, and no lingering management active queue entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_lnode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_lnode.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_lnode.h

## Purpose
`csio_lnode.h` defines the local FCoE node data model and public lnode API. It describes FCF records, local-node flags, FC transport events, lnode statistics, service parameters, the `struct csio_lnode` layout, logging/access macros, hardware-to-lnode notifications, and functions used by hardware, SCSI, FC transport, and rnode code.

## Important APIs, Types, and Constants
- Limits: `CSIO_FCOE_MAX_NPIV` and `CSIO_FCOE_MAX_RNODES`.
- Tunables: `csio_fcoe_rnodes` and `csio_fdmi_enable`.
- `struct csio_fcf_info` stores FCF priority, MAC/name/fabric identifiers, VLAN, FCoE size, FC-MAP, FKA, FCFI, login/capability bits, port ID, SPMA MAC, and kref.
- Lnode flags include `CSIO_LNF_FIPSUPP`, `CSIO_LNF_NPIVSUPP`, `CSIO_LNF_LINK_ENABLE`, and `CSIO_LNF_FDMI_ENABLE`.
- `enum csio_ln_fc_evt` names FC transport async events: link up/down, RSCN, and attribute update.
- `struct csio_lnode_stats` records link, error, event, rnode, FDMI, request, and byte counters.
- `struct csio_lnode_params` stores R_A_TOV, FCFI, and logging level.
- `struct csio_service_parms` stores common/class FC service parameters plus WWPN/WWNN and vendor version.
- `struct csio_lnode` owns state-machine state, hardware pointer, port/device IDs, FCF list/reference, management request, MAC/NPort ID/service parameters, firmware flow IDs, child/parent relationships, pending completions, rnode list, target scan counters, FC vport, FC host statistics, stats, and params.
- Public APIs include firmware event handling, readiness/state formatting, WWPN lookup, physical port stats, scan completion, hardware notifications, port disable/enable, FC async events, FDMI start, lnode start/stop/close/init/exit.

## Control Flow and State
The first field of `struct csio_lnode` is `struct csio_sm`, allowing generic state-machine helpers and list embedding. Physical lnodes are siblings on `hw->sln_head`; NPIV lnodes are children on a physical lnode's `cln_head`. `pln == NULL` identifies physical lnodes, while `pln != NULL` identifies NPIV. Flow IDs connect driver objects to firmware FCF/VNP state, and flags record whether link and FDMI operations are enabled.

## Dependencies and Integration Points
The header depends on Linux kref, timers, workqueue, SCSI FC ELS definitions, `csio_defs.h`, and `csio_hw.h`. It is included by initialization, mailbox, rnode, SCSI, attribute, and hardware event code. FC transport code consumes `struct fc_vport`, `struct fc_host_statistics`, and lnode WWN/service parameter fields.

## Risks and Edge Cases
- `struct csio_lnode` is embedded in `Scsi_Host.hostdata`; allocation and conversion must remain consistent with `csio_ln_to_shost()`.
- FCF info lifetime is shared through kref for NPIV children; parent teardown must coordinate with children.
- `stats.n_evt_fw` is indexed by firmware event causes up to `PROTO_ERR_IMPL_LOGO`; callers must bounds-check firmware causes.
- The macros `csio_ln_wwpn()` and `csio_ln_wwnn()` expose raw byte arrays; callers must preserve FC byte ordering.

## Test Signals
Tests should assert correct physical/NPIV classification, child count changes, FCF kref behavior, state string output, WWPN lookup across siblings/children, target scan counters, and FC host attribute updates after VNP read. Runtime counters should reflect link up/down, rnode allocation/free, FDMI errors, and dropped/unexpected firmware events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_lnode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_mb.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_mb.c

## Purpose
`csio_mb.c` implements firmware mailbox command construction, response parsing, asynchronous mailbox queueing, polling-mode mailbox execution, mailbox interrupt handling, timeout/cancel behavior, and firmware event handling for generic port/debug events. It is the firmware control-plane encoder/transport for hardware setup, queue allocation, FCoE link/VNP/FCF/stats operations, and adapter state changes.

## Important APIs and Functions
- Basic helpers: `csio_mb_fw_retval()`, `csio_mb_hello()`, `csio_mb_process_hello_rsp()`, `csio_mb_bye()`, `csio_mb_reset()`, `csio_mb_params()`, `csio_mb_process_read_params_rsp()`, `csio_mb_ldst()`, `csio_mb_caps_config()`, `csio_mb_port()`, `csio_mb_process_read_port_rsp()`, and `csio_mb_initialize()`.
- Queue mailbox helpers: `csio_mb_iq_alloc_write()`, `csio_mb_iq_alloc_write_rsp()`, `csio_mb_iq_free()`, `csio_mb_eq_ofld_alloc_write()`, `csio_mb_eq_ofld_alloc_write_rsp()`, and `csio_mb_eq_ofld_free()`.
- FCoE helpers: `csio_write_fcoe_link_cond_init_mb()`, `csio_fcoe_read_res_info_init_mb()`, `csio_fcoe_vnp_alloc_init_mb()`, `csio_fcoe_vnp_read_init_mb()`, `csio_fcoe_vnp_free_init_mb()`, `csio_fcoe_read_fcf_init_mb()`, `csio_fcoe_read_portparams_init_mb()`, and `csio_mb_process_portparams_rsp()`.
- Interrupt control: `csio_mb_intr_enable()` and `csio_mb_intr_disable()`.
- Firmware debug support: `csio_mb_dump_fw_dbg()`, `csio_mb_debug_cmd_handler()`.
- Mailbox engine: `csio_mb_issue()`, `csio_mb_completions()`, `csio_mb_isr_handler()`, `csio_mb_tmo_handler()`, `csio_mb_cancel_all()`, `csio_mbm_init()`, and `csio_mbm_exit()`.
- Firmware event helper: `csio_mb_fwevt_handler()` processes async `FW_PORT_CMD` link/module changes and `FW_DEBUG_CMD`.

## Control Flow and State
Command builder functions initialize `struct csio_mb` using `CSIO_INIT_MBP()`, fill firmware command structures in big-endian format, and set optional callbacks/private pointers. `csio_mb_issue()` is the central path. For synchronous commands (`mb_cbfn == NULL`), it writes mailbox registers, gives ownership to firmware, then polls until ownership returns or timeout expires. For asynchronous commands, it requires host and hardware interrupts to be enabled, queues if another mailbox is current, otherwise writes the command, records `mbm->mcurrent`, arms the timer, and notifies firmware with interrupt request.

`csio_mb_isr_handler()` validates PL/CIM mailbox causes, clears low-level then high-level cause registers, copies the response into `mbm->mcurrent`, clears mailbox ownership, moves the command to `mbm->cbfn_q`, and enqueues a `CSIO_EVT_MBX` event for worker-thread completion. `csio_mb_tmo_handler()` marks the current command with `FW_ETIMEDOUT`; `csio_mb_cancel_all()` marks current, queued, and callback-pending commands with `FW_HOSTERROR` and moves them to a callback queue.

## State and Persistence Behavior
`struct csio_mbm` stores the active mailbox pointer, pending request queue, callback queue, timer, interrupt index, and stats. Command payloads persist in each `struct csio_mb` until the caller callback or synchronous issue path consumes the response. The module keeps no disk state; all persistence is firmware/hardware side effects and in-memory driver queues.

## Dependencies and Integration Points
The file depends on Linux delay/jiffies APIs and SCSI FC headers, plus driver-local `csio_hw`, `csio_lnode`, `csio_rnode`, `csio_wr`, and firmware API headers. Hardware initialization uses HELLO/BYE/RESET/PARAMS/CAPS/PORT/INITIALIZE helpers. Work-request queue setup uses IQ/EQ helpers. Lnode discovery uses FCoE link/VNP/FCF/stats helpers. ISR and event-worker code use mailbox engine functions for completions.

## Risks and Edge Cases
- `csio_mb_issue()` assumes callers hold `hw->lock`; misuse can corrupt `mbm->mcurrent` or request queues.
- Async mailbox issue fails if interrupts are not enabled, so initialization order is critical.
- Queuing behavior for async commands only works when an active mailbox exists; unavailable hardware ownership with no `mcurrent` logs an error.
- `csio_mb_iq_alloc()` assigns `fl0size` twice, once from `fl0size` and then from `fl1size`, which looks suspicious and should be checked against firmware structure expectations.
- `csio_mb_process_portparams_rsp()` copies stats in chunks by index; off-by-one mistakes in `idx`/`nstats` would corrupt the assembled stats view.
- Firmware debug commands can arrive during mailbox polling/ISR and are handled specially, but repeated debug commands can delay ordinary completion.

## Test Signals
Tests should cover synchronous mailbox success/error/timeout, async mailbox queuing and callback ordering, timer timeout race with ISR completion, cancellation on hardware teardown, firmware debug mailbox handling, port link/module event updates, queue allocation response parsing, and FCoE stats assembly over three reads. Runtime counters `n_req`, `n_rsp`, `n_activeq`, `n_cbfnq`, `n_tmo`, `n_cancel`, and `n_err` provide direct observability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_mb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_mb.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_mb.h

## Purpose
`csio_mb.h` declares the mailbox module interface and data structures. It defines mailbox sizing/timing, device mastership/ownership/state enums, firmware parameter macros, mailbox/request manager structures, stats, command-builder APIs, response parsers, interrupt controls, issue/completion/timeout/cancel functions, and FCoE-specific mailbox helpers.

## Important APIs, Types, and Constants
- Constants: `CSIO_MB_MAX_REGS`, `CSIO_MAX_MB_SIZE`, `CSIO_MB_POLL_FREQ`, `CSIO_MB_DEFAULT_TMO`, `CSIO_STATS_OFFSET`, and `CSIO_NUM_STATS_PER_MB`.
- `struct fw_fcoe_port_cmd_params` carries port stats read parameters.
- `CSIO_DUMP_MB()` logs mailbox register contents for debugging.
- Enums `csio_dev_master`, `csio_mb_owner`, and `csio_dev_state` model firmware HELLO ownership and state.
- `FW_PARAM_DEV()` and `FW_PARAM_PFVF()` construct firmware parameter mnemonics.
- `CSIO_INIT_MBP()` zeroes and initializes a `struct csio_mb` command with timeout, private pointer, callback, list head, and size.
- `struct csio_mb` stores the firmware-format 64-byte mailbox payload, timeout, completion object, callback, owner private pointer, and list linkage.
- `struct csio_mbm` stores async mailbox number, interrupt index, timer, hardware pointer, request/callback queues, current command, queue count, and stats.
- The declarations cover generic firmware commands, queue allocation/free, FCoE link/VNP/FCF/stats commands, module init/exit, interrupt enable/disable, issue/completion/event/ISR/timeout/cancel.

## Control Flow and State
The header defines the command lifecycle contract: callers initialize a mailbox payload with a helper, then submit it via `csio_mb_issue()`. If `mb_cbfn` is null, completion is synchronous/polled; otherwise completion is interrupt-driven and later delivered through `csio_mb_completions()`. `struct csio_mbm` is embedded in `struct csio_hw`, making mailbox state per hardware function.

## Dependencies and Integration Points
It includes firmware API headers `t4fw_api.h` and `t4fw_api_stor.h`, plus `csio_defs.h`. It forward-declares queue parameter structures from the work-request layer and depends on `struct csio_hw`, `struct csio_lnode`, and `struct fw_fcoe_port_stats` users in implementation files.

## Risks and Edge Cases
- `CSIO_INIT_MBP()` sets `mb_size = sizeof(*cmdp)`; commands that expect full 64-byte transfers must override `mb_size`, as stats reads do.
- `CSIO_DUMP_MB()` performs eight 64-bit MMIO reads and should remain debug-gated.
- The mailbox payload is a raw `__be64[8]`; every command builder must handle endian conversion correctly.
- Async callback ownership of `struct csio_mb` memory is external; callbacks and timeout/cancel paths must agree on who frees or reuses the object.

## Test Signals
Compile tests should ensure all command helper declarations match implementations. Runtime tests should validate synchronous and asynchronous mailbox behavior, correct timeout values, callback invocation, stats counter increments, queue response parsing, FCoE command formatting, and absence of pending `req_q`/`cbfn_q` entries at module exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_mb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_rnode.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_rnode.c

## Purpose
`csio_rnode.c` implements remote FCoE node management. It maps firmware remote-device events to rnode state-machine events, allocates and frees rnodes, reconciles firmware flow IDs with WWPN/NPort identity, validates remote parameters and roles, registers/unregisters FC rports with the transport layer, handles device-loss cleanup, and maintains rnode lifecycle state for SCSI target visibility.

## Important APIs and Functions
- Event mapping `fwevt_to_rnevt[]` translates firmware causes such as PLOGI/PRLI/LOGO/RSCN device-lost into `enum csio_rn_ev`.
- `csio_is_rnode_ready()` tests ready state; `csio_is_rnode_uninit()` is the internal uninitialized-state test.
- Lookup helpers include `csio_rn_lookup()`, `csio_rn_lookup_wwpn()`, and public `csio_rnode_lookup_portid()`.
- Duplicate detection `csio_rn_dup_flowid()` scans sibling lnodes for active rnodes using the same firmware flowid.
- Allocation/free helpers `csio_alloc_rnode()`, `csio_free_rnode()`, `csio_get_rnode()`, and public `csio_put_rnode()` manage the hardware rnode mempool and lnode rnode list.
- `csio_confirm_rnode()` is the central reconciliation routine for new firmware `fcoe_rdev_entry` data.
- `csio_rn_verify_rparams()` validates rport type, expected DID for fabric/name-server ports, nonzero WWNN/WWPN for normal/name-server ports, service class, FCP target/initiator flags, NPIV support, and copies remote identity into the rnode.
- `__csio_reg_rnode()` and `__csio_unreg_rnode()` call FC transport registration functions outside `hw->lock` and maintain target counters.
- State handlers `csio_rns_uninit()`, `csio_rns_ready()`, `csio_rns_offline()`, and `csio_rns_disappeared()` implement remote-node lifecycle.
- Public event APIs: `csio_rnode_fwevt_handler()` handles firmware event causes; `csio_rnode_devloss_handler()` closes/free disappeared rnodes.
- Initialization/exit: `csio_rnode_init()` inserts rnodes into `ln->rnhead`; `csio_rnode_exit()` removes them and asserts no host completions remain.

## Control Flow and State
Firmware RDEV payloads are first routed by lnode code to `csio_confirm_rnode()`, which finds an existing rnode by flowid, WWPN, or NPort ID for well-known ports, or allocates a new one. Once `rn->rdev_entry` is set, `csio_rnode_fwevt_handler()` maps the firmware cause to a state-machine event. Login/PLOGI events from uninit/offline/disappeared validate parameters and transition to ready with FC rport registration. PRLI events in ready refresh registration. DOWN/LOGO/NAME_MISSING events unregister the rport and move to offline or disappeared. CLOSE moves back to uninit and allows the rnode to be freed.

## State and Persistence Behavior
Each rnode stores owning lnode, firmware flowid, host completion queue, FC NPort ID, FCP flags, current/previous firmware event, role bitmap, firmware rdev entry pointer, service parameters, FC transport `rport`, supported class/frame size/SCSI ID, and stats. It is linked through the embedded `sm.sm_list` on `ln->rnhead` and allocated from `hw->rnode_mempool`.

## Dependencies and Integration Points
The file depends on SCSI FC transport and FC ELS/FS headers plus `csio_hw.h`, `csio_lnode.h`, and `csio_rnode.h`. Registration functions `csio_reg_rnode()` and `csio_unreg_rnode()` are declared in the header and implemented elsewhere. SCSI cleanup integrates through `csio_scsi_cleanup_io_q()` when unregistering rnodes with pending host completions. FDMI can be triggered when the management-server NPort appears.

## Risks and Edge Cases
- Identity reconciliation is complex: duplicate flow IDs across lnodes, same WWPN with changed SSNI, and well-known address relogin all take different branches.
- `csio_put_rnode()` asserts the rnode is uninit; callers must post CLOSE before freeing.
- `__csio_unreg_rnode()` decrements `ln->last_scan_ntgts` along with `n_scsi_tgts`; underflow is possible if counters are already zero or inconsistent.
- `csio_rn_verify_rparams()` indexes `clsp[fc_class - 1]`; malformed firmware class zero would underflow.
- Rnode registration/unregistration intentionally drops `hw->lock`, so surrounding state must remain valid across transport calls.

## Test Signals
Tests should cover fabric/name-server/regular/FDMI rport types, PRLI target/initiator flags, invalid DIDs, zero WWNs, duplicate flowid detection, WWPN relogin with changed flowid, LOGO/DOWN/NAME_MISSING/CLOSE transitions, device-loss delayed cleanup, and pending host completion cleanup on unregister. Runtime signals include FC rport registration/unregistration, target count changes, rnode allocation/free stats, and state string output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_rnode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_rnode.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_rnode.h

## Purpose
`csio_rnode.h` defines the remote FCoE node interface. It names rnode state-machine events, statistics, role flags, the `struct csio_rnode` layout, identity/access macros, and public functions for lookup, confirmation, firmware event handling, registration, unregistration, and device-loss handling.

## Important APIs, Types, and Constants
- `enum csio_rn_ev` includes login, PRLI, received PLOGI/PRLI/LOGO/PRLO, down, close, and name-missing events.
- `struct csio_rnode_stats` tracks error, invalid/nomem errors, unexpected/dropped events, firmware event counts, state-machine event counts, and LUN/target reset stats.
- Role flags: `CSIO_RNFR_INITIATOR`, `CSIO_RNFR_TARGET`, `CSIO_RNFR_FABRIC`, `CSIO_RNFR_NS`, and `CSIO_RNFR_NPORT`.
- `struct csio_rnode` stores state-machine linkage, owning lnode, firmware flowid, pending host completion queue, FC identifiers, FCP flags, current/previous event, role, firmware rdev entry pointer, service parameters, FC transport rport attributes, and stats.
- Access macros expose flowid, WWPN, WWNN, and owning lnode.
- Public APIs include readiness/state string helpers, port-ID lookup, rnode confirmation from firmware entry, firmware event handling, put/free, FC transport register/unregister, and device-loss handling.

## Control Flow and State
Like lnodes, rnodes embed `struct csio_sm` as the first field so they can be state-machine objects and list nodes. They are owned by a single lnode and linked into that lnode's `rnhead`. Firmware flow IDs and FC WWNs/NPort IDs are used together to reconcile relogin and changed-session cases. Role flags determine whether the rnode becomes a SCSI target, fabric object, name server, initiator, or generic NPort.

## Dependencies and Integration Points
The header includes `csio_defs.h` and depends on types from firmware storage APIs, FC transport, and lnode definitions through including users. It is consumed by lnode, SCSI, attribute, and transport integration code.

## Risks and Edge Cases
- `stats.n_evt_fw` is sized to `PROTO_ERR_IMPL_LOGO + 1`; firmware event values must be validated before indexing.
- `host_cmpl_q` must be drained before `csio_rnode_exit()`; the implementation asserts this.
- The public `csio_reg_rnode()`/`csio_unreg_rnode()` functions interact with FC transport and must tolerate repeated or out-of-order firmware events.
- `rdev_entry` points into firmware event payload ownership; lifetime assumptions are enforced by current event processing and should not be extended casually.

## Test Signals
Validation should include state transitions to ready/offline/disappeared/uninit, state string output, lookup by NPort ID, flowid/WWPN confirmation behavior, role flag mapping, FC rport registration side effects, and device-loss cleanup. SCSI reset counters and event stats provide additional observability during error handling tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_rnode.h -->
