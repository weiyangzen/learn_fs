<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_svw.c -->
# sources/distributed-fs/ceph-client/drivers/ata/sata_svw.c

## Purpose

This is the ServerWorks/Broadcom/Apple K2 libata SATA driver. It supports four- and eight-port MMIO controllers, maps taskfile/BMDMA/SCR registers with a fixed stride, works around DMA command ordering issues, and provides OF-derived port information on Apple systems.

## Important APIs, types, and functions

Hardware variants are selected by `k2_sata_pci_tbl` and `k2_port_info[]`. `k2_sata_ops` overrides soft/hard reset, taskfile load/read, status read, ATAPI DMA filtering, BMDMA setup/start, and SCR access. Important functions are `k2_sata_check_atapi_dma()`, `k2_sata_softreset()`, `k2_sata_hardreset()`, `k2_sata_tf_load()`, `k2_sata_tf_read()`, `k2_bmdma_setup_mmio()`, `k2_bmdma_start_mmio()`, `k2_sata_show_info()`, `k2_sata_setup_port()`, and `k2_sata_init_one()`.

## Control flow

Probe chooses four or eight ports and BAR position, enables PCI, rejects disabled functions with no BAR length, maps the MMIO BAR, assigns per-port taskfile/BMDMA/SCR addresses, sets a 32-bit ATA DMA mask, clears a Darwin-observed SICR1 bit, clears SATA error state, masks unused SATA interrupts, then activates with `ata_bmdma_interrupt()`. DMA setup writes the PRD address and direction. For ATA DMA, `k2_bmdma_start_mmio()` starts host DMA before issuing the ATA command, avoiding a documented data-corruption window where fast drives return data before the controller sees DMA start.

## State and persistence behavior

State is MMIO controller state, port flags such as `K2_FLAG_NO_ATAPI_DMA`, and live libata state. OF show-info lookup reads device-tree children for diagnostics only. No on-disk persistence exists.

## Dependencies and integration points

The driver depends on PCI, MMIO libata BMDMA helpers, SCSI command opcodes for ATAPI DMA filtering, and Open Firmware node helpers for `show_info`.

## Risks

The ATA DMA ordering workaround is essential for data integrity; changing command issue order can corrupt reads. ATAPI DMA is blocked on some variants and whitelisted only for read/write packet commands on others. Missing BAR resources can reflect firmware-disabled functions and must not be treated as normal mapped ports.

## Test signals

Run build/boot on Apple K2, Frodo, and BCM5785-like controllers, four/eight-port enumeration, DMA read stress with fast disks, ATAPI DMA command coverage, reset while DMA active, and OF show-info output. Monitor for BMDMA lost interrupts, data checksum errors, and link reset stability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_svw.c -->
