<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_uli.c -->
# sources/distributed-fs/ceph-client/drivers/ata/sata_uli.c

## Purpose

This is the libata PCI driver for ULi/ALi M5289, M5287, and M5281 SATA controllers. It mostly relies on generic SFF/BMDMA setup, with controller-specific mapping for SATA SCR registers in PCI config space and extra port address setup for four-port M5287 hardware.

## Important APIs, types, and functions

`struct uli_priv` stores per-port SCR config-space base offsets. `uli_ops` inherits `ata_bmdma_port_ops`, supplies `uli_scr_read()`/`uli_scr_write()`, and disables hardreset with `ATA_OP_NULL`. `uli_init_one()` chooses two or four ports, initializes generic PCI SFF/BMDMA host state, patches ports 2/3 for M5287, fills SCR bases, and activates the host.

## Control flow

Probe enables PCI, determines port count from `ent->driver_data`, allocates an ata host and private SCR map, initializes the first two ports with generic SFF helpers, initializes BMDMA, then fills variant-specific SCR config offsets. For M5287, ports 2 and 3 are derived from standard BARs with offset taskfile and BMDMA windows. SCR access simply calculates `scr_cfg_addr[port] + sc_reg * 4` and reads/writes PCI config dwords.

## State and persistence behavior

State is limited to the private SCR base array, PCI config registers, and libata host state. There is no persistent state and no custom PM implementation.

## Dependencies and integration points

The file depends on PCI, generic libata SFF/BMDMA host initialization, PCI config access, and managed resource mappings from `ata_pci_sff_init_host()`.

## Risks

The driver suppresses hard reset, so recovery depends on soft/SFF paths. M5287 port 2/3 address derivation is manually encoded and easy to regress; one `ata_port_desc()` call describes `host->ports[2]` twice in the viewed source, likely a diagnostic copy/paste issue. SCR access only supports status/error/control and assumes correct config-space base offsets.

## Test signals

Build and boot each ULi variant, verify two- vs four-port enumeration, SCR read/write through libata link status, BMDMA interrupt I/O, soft reset/EH behavior without hardreset, and port 2/3 resource descriptions on M5287.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_uli.c -->
