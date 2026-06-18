# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/octeon_ep/octep_cnxk_pf.c Research

## Purpose
`octep_cnxk_pf.c` provides CNXK physical-function hardware operations for the Octeon EP NIC driver. It is the CNXK counterpart to the CN9K PF file, with CNXK register offsets, interrupt layout, RX watermark handling, soft reset, and queue setup details.

## Important APIs, Types, And Functions
The exported entry point is `octep_device_setup_cnxk_pf()`, which fills the `oct->hw_ops` table. Key helpers are `cnxk_dump_regs()`, `cnxk_reset_iq()`, `cnxk_reset_oq()`, `octep_reset_io_queues_cnxk_pf()`, `octep_setup_pci_window_regs_cnxk_pf()`, `octep_configure_ring_mapping_cnxk_pf()`, `octep_init_config_cnxk_pf()`, `octep_setup_iq_regs_cnxk_pf()`, `octep_setup_oq_regs_cnxk_pf()`, `octep_setup_mbox_regs_cnxk_pf()`, mailbox/OEI pollers and interrupt handlers, error interrupt handlers, `octep_soft_reset_cnxk_pf()`, `octep_reinit_regs_cnxk_pf()`, interrupt enable/disable, IQ read-index update, queue enable/disable, and register dump helpers.

## Control Flow
Setup installs all CNXK ops, initializes PCI window registers, reads the PCIe port from `CNXK_SDP_MAC_NUMBER`, initializes configuration from CNXK PF/VF ring CSRs, maps PF rings, and marks firmware status running through a PCI window write. IQ setup waits for idle, configures 64-byte instructions and endian/size settings, writes descriptor base/size, stores queue MMIO pointers, resets completion count, and programs interrupt levels. OQ setup waits for idle, programs maximum watermark first, writes descriptor base/size, retries base programming for up to about 10 seconds if hardware does not latch it, configures packet buffer size, stores credit/count pointers, programs interrupt coalescing, and then sets the configured backpressure watermark.

Interrupt flow mirrors CN9K but uses CNXK register names and a CNXK non-IOQ MSI-X layout with OEI entries and a trailing IOQ name. PF/VF mailbox interrupts schedule per-VF mailbox work, OEI handles control mailbox and heartbeat, IOQ interrupts schedule NAPI, and error handlers log/clear ring, VF, DMA, PP, and misc error registers. Soft reset writes firmware status downing, asserts a chip-domain reset, delays briefly, and restores the window write mask.

## State, Persistence, And Dependencies
State persists in hardware CSRs, `oct->conf`, `oct->hw_ops`, per-queue register pointers, `oct->pcie_port`, heartbeat state, and mailbox/control work items. Dependencies include CNXK register definitions, common Octeon device and queue structures, PCI SR-IOV capability reads, jiffies/time helpers for OQ register retry, workqueue scheduling, and NAPI.

## Integration Points
Common Octeon probe code selects `octep_device_setup_cnxk_pf()` for CNXK PF PCI IDs. The common Tx/Rx datapath uses the installed queue operations and read-index callback. Control mailbox processing is driven by OEI events queued here. SR-IOV PF/VF mailbox support depends on the mailbox register setup and mailbox interrupt handlers.

## Risks
The idle waits for IQ/OQ setup have no explicit timeout; only the OQ descriptor-base latch retry is bounded. Interrupt masks still use 64-bit shifts based on `srn + i`, so ring numbering must stay within the mask model. `octep_setup_oq_regs_cnxk_pf()` can return `-EFAULT` or `-EAGAIN`, so callers must respect OQ setup failure or the queue may run with stale DMA base. The PF/VF mailbox poller only checks one mailbox interrupt register, unlike CN9K's two-register handling, so VF/ring topology assumptions are chip-specific and should not be generalized blindly.

## Test Signals
Exercise CNXK probe/remove, queue setup with descriptor-base retry, RX watermark/backpressure programming, soft reset and reinit, OEI control mailbox and heartbeat events, PF/VF mailbox delivery across supported VF counts, IOQ NAPI scheduling, all non-IOQ error interrupt handlers, register dump output, traffic before/after reset, and failure paths when OQ base programming returns `ULLONG_MAX` or times out.
