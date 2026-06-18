<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_sis.c -->
# sources/distributed-fs/ceph-client/drivers/ata/sata_sis.c

## Purpose

This is the libata PCI driver for SiS 180/181/182/965/966/968/680 SATA controllers. It handles controllers that expose SATA SCRs either through PCI config space or IO-mapped BAR5, and it coordinates with `pata_sis` for combined PATA/SATA operating modes.

## Important APIs, types, and functions

The public binding is `sis_pci_driver`; supported IDs are in `sis_pci_tbl`. `sis_port_info` and `sis_ops` provide the base BMDMA SATA port description plus SCR hooks. `get_scr_cfg_addr()` calculates PCI config SCR offsets by port, device ID, PMP index, and combined-mode register state. `sis_scr_read()` and `sis_scr_write()` dispatch to PCI config helpers or MMIO. `sis_init_one()` is the main probe/configuration path.

## Control flow

Probe enables the PCI device, checks `SIS_GENCTL` to decide whether SCRs are IO mapped, forces config-space SCR mode if BAR5 is absent or too small, reads `SIS_PMR`, and selects pure SATA, combined mode, or PATA-backed port info. It prepares a BMDMA ata host, initializes slave links when the SATA mode supports master/slave slots, maps BAR5 if needed, assigns per-port SCR bases, enables bus mastering and INTx, then activates the host with the generic BMDMA interrupt handler.

## State and persistence behavior

State is PCI config bits, selected port flags, SCR address mappings, and libata port state. There is no persistent storage. PM uses generic `ata_pci_device_suspend()` and `ata_pci_device_resume()`.

## Dependencies and integration points

The driver depends on PCI config access, managed PCI BMDMA preparation, libata BMDMA helpers, and `sis_info133_for_sata` declared in `sis.h` and implemented by `pata_sis.c` for PATA-mode ports.

## Risks

SCR_ERROR is unavailable in PCI config SCR mode and returns `-EINVAL`; callers must tolerate that. Combined mode changes port layout and may expose slave devices, so incorrect PMR interpretation can hide devices or select the wrong `ata_port_info`. Changing `GENCTL_IOMAPPED_SCR` on broken BAR layouts is necessary but risky if firmware/hardware assumptions differ.

## Test signals

Compile with both SATA SiS and PATA SiS support, boot SiS 180/182/1182/1183 variants, test pure SATA and combined modes, verify SCR reads in both config and IO-mapped modes, run libata reset/EH, and test suspend/resume. Detection messages in dmesg should match chipset mode and port visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_sis.c -->
