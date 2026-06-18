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
