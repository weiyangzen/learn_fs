# sources/distributed-fs/ceph-client/drivers/ata/sata_promise.c

## Purpose
Implements the libata low-level driver for Promise SATA/PATA TX2/TX4/TX4000 controllers. It supports first- and second-generation Promise SATA adapters, optional PATA ports, Promise packet command submission, SATA SCR access and hotplug, PATA cable detection, DMA/ATAPI filtering, port reset quirks, and shared PCI interrupt handling.

## Important APIs, Types, And Functions
- `pdc_port_info` and `pdc_ata_pci_tbl` map Promise board variants to SATA, PATA, generation, and port-count flags.
- `struct pdc_port_priv` holds the coherent 128-byte command packet and DMA address; `struct pdc_host_priv` provides `hard_reset_lock` for serialized port hardreset register toggles.
- Port ops are layered as `pdc_common_ops`, `pdc_sata_ops`, `pdc_old_sata_ops`, and `pdc_pata_ops`.
- Command preparation and issue are handled by `pdc_qc_prep`, `pdc_fill_sg`, `pdc_atapi_pkt`, `pdc_packet_start`, and `pdc_qc_issue`, with packet helpers supplied by `sata_promise.h`.
- Reset/EH/IRQ helpers include `pdc_reset_port`, `pdc_sata_hardreset`, `pdc_pata_softreset`, `pdc_error_handler`, `pdc_post_internal_cmd`, `pdc_error_intr`, `pdc_host_intr`, and `pdc_interrupt`.
- Probe/setup functions include `pdc_common_port_start`, `pdc_sata_port_start`, `pdc_ata_setup_port`, `pdc_host_init`, and `pdc_ata_init_one`.

## Control Flow
Probe enables the PCI device, maps the MMIO BAR, selects two or four SATA/PATA ports from board flags and a flash-control PATA-present bit, allocates a libata host plus private reset lock, assigns per-port ATA and SCR MMIO windows including special SATAII TX4 port remapping, initializes global Promise registers and hotplug masks, sets a 32-bit ATA DMA mask, and activates the host with `pdc_interrupt`.

Port start allocates standard BMDMA resources plus a coherent Promise command packet. Gen II SATA start additionally adjusts `PHYMODE4`. For DMA and most no-data commands, `pdc_qc_prep` builds an ASIC packet with a PRD table pointer, taskfile register writes, optional LBA48 fields, final command register write, or ATAPI packet sequence. `pdc_qc_issue` submits the packet by writing a sequence register and `PDC_PKT_SUBMIT`; polling or CDB-interrupt cases fall back to SFF issue.

The interrupt handler serializes on `host->lock`, reads and clears Gen II hotplug flags, reads/acks the sequence interrupt mask, freezes ports with plug/unplug status, and dispatches packet interrupts to `pdc_host_intr`. `pdc_host_intr` checks per-port global error bits, maps them to libata error classes, snapshots SError for SATA links, resets the port, and aborts; otherwise it waits idle and completes DMA/no-data packet commands. Error handling resets the Promise port before invoking libata SFF EH unless the port is already frozen.

## State And Persistence
Per-port persistent state is the coherent packet buffer, the standard BMDMA PRD table, MMIO taskfile/SCR addresses, and libata flags for generation/port type. Host persistent state is the hard-reset spinlock and mapped BAR. Hardware state persists in sequence interrupt masks, hotplug control/status bits, flash/TBG/slew registers, per-port control/status reset and DMA-enable bits, FPDMA control/status flags, SATA error/link-layer registers, and PCI-control hardreset bits. The driver uses managed allocations and `ata_pci_remove_one`, so teardown is mostly devres/libata-managed.

## Dependencies And Integration Points
The file depends on libata SFF/BMDMA helpers, SCSI host templates, PCI managed mapping and DMA-mask APIs, Promise packet construction helpers from `sata_promise.h`, ATA/SCSI command constants, and libata EH/SCR/hotplug APIs. It integrates with libata via custom taskfile load/execute wrappers that warn on DMA use, custom ATAPI DMA filters, port-specific freeze/thaw hooks, hardreset/softreset callbacks, and shared IRQ activation.

## Risks And Edge Cases
The hardware has a known PRD/ASIC bug requiring `PDC_MAX_PRD = LIBATA_MAX_PRD - 1` and an extra split when the final PRD length exceeds `41*4`. PRDs are 32-bit only, so DMA addresses are truncated after the driver restricts the DMA mask. Gen I SATA cannot use ATAPI DMA, and even Gen II filters ATAPI DMA to a whitelist plus a `WRITE_10` high-LBA PIO exception. SATA hardreset cannot reliably acquire the first D2H register FIS and relies on follow-up SRST. Hotplug register access must stay serialized under the host lock. Gen II FPDMA reset requires byte-sized writes because full-register writes are unsafe while NCQ runs.

## Test Signals
Useful tests include probe of two-port, four-port, SATA+PATA, and SATAII TX4 remapped boards; PATA cable detection; DMA packet issue and completion; no-data packet issue outside polling/CDB-interrupt cases; ATAPI DMA whitelist/PIO fallback behavior; 64 KiB PRD splitting and final-entry ASIC bug split; Gen II hotplug freeze/thaw masking; port reset after packet errors and internal commands; SATA hardreset followed by SRST; and shared IRQ behavior with empty masks or `0xffffffff` reads.
