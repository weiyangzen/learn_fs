# sources/distributed-fs/ceph-client/drivers/ata/pata_via.c

## Purpose
`pata_via.c` is a VIA PATA driver covering many southbridge generations from MWDMA-only devices through UDMA133 and SATA/PATA combined configurations. It discovers the real bridge model, applies generation quirks, computes timings with libata timing helpers, and works around device-register loss after control writes.

## Important APIs, Types, and Functions
Important data includes `via_isa_bridges[]`, DMI quirk tables, `struct via_port`, and flags such as `VIA_BAD_PREQ`, `VIA_BAD_CLK66`, `VIA_SET_FIFO`, `VIA_BAD_AST`, `VIA_NO_ENABLES`, and `VIA_SATA_PATA`. Main functions are `via_cable_detect()`, `via_pre_reset()`, `via_do_set_mode()`, `via_set_piomode()`, `via_set_dmamode()`, `via_mode_filter()`, `via_tf_load()`, `via_port_start()`, `via_config_fifo()`, `via_fixup()`, `via_init_one()`, and `via_reinit_one()`.

## Control Flow, State, and Persistence
Probe enables PCI, finds the matching VIA ISA bridge by vendor/device/revision, checks enabled channels unless the bridge lacks enable bits, chooses a port-info profile by UDMA capability, applies FIFO/clock fixups, and initializes BMDMA with the bridge config as host private data. Timing setup computes ATA timing from the requested PIO/DMA mode, merges peer 8-bit timing, optionally writes address setup, writes PIO active/recover registers, and programs UDMA control bytes according to UDMA generation. `via_port_start()` allocates `struct via_port`; `via_tf_load()` caches the device/head byte and rewrites it after control-register changes to counter hardware behavior.

## Dependencies and Integration Points
This file depends on PCI bridge discovery, DMI matching, libata timing math, BMDMA and SFF helpers, ACPI cable fallback, and libata mode filtering. Some IDs use `via_port_ops_noirq` with 32-bit data transfer for controllers that cannot tolerate IRQ unmasking.

## Risks and Test Signals
Risks include bridge misidentification because VIA reused IDE PCI IDs, incorrect cable results on SATA/PATA combined ports, unsafe ATAPI DMA on known-bad boards, PREQ/FIFO and 66 MHz clock errata regressions, and stale cached device register state. Tests should cover all UDMA mask classes, bridge revisions and single-channel IDs, DMI cable/ATAPI quirks, Transcend SSD UDMA filtering, LBA48 taskfile loading after `nIEN` changes, suspend/resume fixups, and hotplug or ACPI cable-detect behavior on SATA/PATA combined hardware.
