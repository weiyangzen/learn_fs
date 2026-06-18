# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_cn9k_pf.c Research

## Purpose
`octep_cn9k_pf.c` provides the CN93/CN98 physical-function hardware operations for the Octeon EP NIC driver. It initializes chip-specific register windows, ring limits, queue registers, PF/VF mailbox registers, interrupt handlers, reset behavior, and the `oct->hw_ops` function table used by common driver code.

## Important APIs, Types, And Functions
The exported entry point is `octep_device_setup_cn93_pf()`. It installs hardware operations for IQ/OQ setup, PF/VF mailbox setup, non-IOQ and IOQ interrupt handlers, soft reset, register reinitialization, interrupt enable/disable, polling, IQ read-index updates, queue enable/disable/reset, and register dumps.

Important internal functions include `cn93_dump_regs()`, `cn93_reset_iq()`, `cn93_reset_oq()`, `octep_reset_io_queues_cn93_pf()`, `octep_setup_pci_window_regs_cn93_pf()`, `octep_configure_ring_mapping_cn93_pf()`, `octep_init_config_cn93_pf()`, `octep_setup_iq_regs_cn93_pf()`, `octep_setup_oq_regs_cn93_pf()`, `octep_setup_mbox_regs_cn93_pf()`, PF/VF mailbox and OEI poll/interrupt handlers, error interrupt handlers, `octep_soft_reset_cn93_pf()`, `octep_soft_reset_cn98_pf()`, and queue enable/disable helpers.

## Control Flow
Setup installs the ops table, sets PCI windowed CSR access pointers, reads `CN93_SDP_MAC_NUMBER` to determine the PCIe port, initializes configuration from hardware ring-info CSRs, maps PF rings to this function, and for CN93 marks firmware status as running through a window write. Configuration reads VF and PF ring topology, fills default IQ/OQ descriptor and coalescing values, configures MSI-X counts/names, computes control-mailbox BAR memory from BAR4 plus SR-IOV function link offset, and sets default firmware heartbeat policy.

Queue setup waits for ring idle, programs descriptor DMA base and ring size, stores doorbell/count/interrupt MMIO pointers into `struct octep_iq` or `struct octep_oq`, resets instruction counters, and configures interrupt thresholds. Runtime interrupt flow acknowledges PF/VF mailbox bits and schedules mailbox work per VF, acknowledges OEI events and queues control mailbox work or resets heartbeat miss count, logs and clears ring/DMA/MISC errors, and schedules NAPI for IOQ interrupts. Reinit reruns IQ/OQ setup, enables interrupts and queues, and posts RX credits.

## State, Persistence, And Dependencies
State is stored in `oct->conf`, `oct->hw_ops`, `oct->pcie_port`, PCI window register pointers, per-queue MMIO register pointers, PF/VF mailbox structures, heartbeat counters, and hardware CSRs. The code depends on CN9K register macros, common Octeon device structures, PCI SR-IOV capability access, NAPI, workqueues, and shared control/PF-VF mailbox tasks.

## Integration Points
Common probe code selects this setup function for CN93/CN98 PF PCI IDs. The common datapath calls the installed ops to program queues, enable interrupts, reset queues, update Tx completion indices, and dump registers. SR-IOV and mailbox code consume `setup_mbox_regs` and mailbox interrupt scheduling. Control-plane code relies on OEI mailbox events to schedule firmware message processing.

## Risks
Several idle waits spin without an explicit timeout, so wedged hardware can stall setup. Interrupt masks are built with `1ULL << (srn + i)`, so invalid ring numbering above 63 would overflow; CN93 has two mailbox registers but many other masks are single 64-bit values. CN98 deliberately skips soft reset, while CN93 performs a core-domain reset and manipulates firmware status around a documented hardware bug; wrong chip detection can produce stale firmware status or unexpected reset behavior. `octep_get_ethtool_stats()` later assumes queue stats for `OCTEP_MAX_QUEUES`, so active ring count consistency matters.

## Test Signals
Test CN93 and CN98 probe/remove, queue reset/setup/enable/disable, firmware reset and module removal after unexpected device reset, PF/VF mailbox interrupts for VFs above and below queue 64, OEI mailbox and heartbeat events, IOQ NAPI scheduling, ring error interrupt logging/clear, SR-IOV function-link-derived control mailbox address, register dumps, and recovery through `reinit_regs()` with traffic before and after reset.
