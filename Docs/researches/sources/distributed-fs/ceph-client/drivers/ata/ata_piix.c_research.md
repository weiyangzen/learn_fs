# sources/distributed-fs/ceph-client/drivers/ata/ata_piix.c

## Purpose
`ata_piix.c` is the Intel PIIX/ICH low-level libata driver for legacy Intel PATA and IDE-mode SATA controllers, plus selected virtualized variants. It programs PCI configuration timing registers for PATA, maps IDE-mode SATA ports onto libata ports, exposes optional SIDPR SCR access for newer ICH controllers, and encodes many platform and firmware quirks needed for older Intel chipsets.

## Important APIs, Types, And Functions
The driver registers `piix_pci_driver` through explicit `module_init()`/`module_exit()` so it can use `in_module_init` to reject hotplug of later SATA devices after initial module load. `piix_pci_tbl[]` maps PCI IDs to `enum piix_controller_ids`; `piix_port_info[]` maps those IDs to libata masks, flags, and port operations. `struct piix_map_db` describes SATA map register decoding; `struct piix_host_priv` stores the decoded SATA map, saved IOCFG register, and optional SIDPR MMIO pointer.

Important operations include `piix_set_timings()`, `piix_set_piomode()`, `do_pata_set_dmamode()`, `ich_pata_cable_detect()`, `piix_init_sata_map()`, `piix_init_sidpr()`, `piix_disable_ahci()`, `piix_check_450nx_errata()`, `piix_iocfg_bit18_quirk()`, `piix_ignore_devices_quirk()`, `piix_init_one()`, and `piix_remove_one()`. Port operation variants cover PATA, ICH PATA, SATA, VMware PATA, and SIDPR-capable SATA.

## Control Flow
Probe copies the selected `ata_port_info` into two host ports, enables the PCI device with managed PCI helpers, allocates `piix_host_priv`, and saves `PIIX_IOCFG` before any ACPI or quirk path can alter it. ICH6R AHCI-capable devices are forced out of AHCI mode through BAR5 `HOST_CTL` before libata setup. SATA controllers decode `ICH5_PMR` through the chipset-specific map table, possibly converting an IDE channel to PATA port info or marking slave devices possible.

After `ata_pci_bmdma_prepare_host()`, SATA probe enables PCS bits, tests and installs SIDPR SCR access when BAR5 index/data registers are usable, applies the Clevo IOCFG bit-18 quirk, re-enables INTx for controllers that need it, disables DMA masks on affected 450NX systems, enables parallel scan, applies Hyper-V ATA-ignore policy when requested, sets PCI bus master, and activates the host with `ata_pci_sff_activate_host()`. Removal restores saved IOCFG before delegating to `ata_pci_remove_one()`.

PATA mode programming uses PCI config registers under `piix_lock`. PIO setup writes master timing registers at `0x40/0x42`, the separate slave timing register at `0x44`, sets SITRE, and clears UDMA enable bits. DMA setup either programs UDMA enable/timing/clock fields at `0x48`, `0x4a`, and ICH `0x54`, or derives MWDMA from matching PIO timings. SATA SIDPR SCR access selects port/PMP/register through BAR5 index and reads/writes BAR5 data; LPM delegates to `sata_link_scr_lpm()`.

## State And Persistence
Persistent hardware state lives in PCI config space: IOCFG, PMR, PCS, timing, UDMA, INTx, and optional AHCI-global-control registers. The driver saves IOCFG in `hpriv->saved_iocfg` and restores it on remove because ACPI `_STM` can disturb cable bits. Runtime state includes decoded SATA maps, SIDPR MMIO mappings, host flags such as `PIIX_HOST_BROKEN_SUSPEND`, libata port masks, and module parameters `prefer_ms_hyperv` and `in_module_init`.

## Dependencies And Integration Points
The file depends on PCI, DMI, libata SFF/BMDMA helpers, tracepoints for BMDMA status, ACPI-sensitive suspend/resume helpers, and SCSI host registration. It integrates with old IDE-mode Intel firmware assumptions, platform DMI quirk databases, Hyper-V storage preference logic, and optional SATA SCR/LPM sysfs support through SIDPR-specific shost attributes.

## Risks And Edge Cases
The code is quirk-heavy. Incorrect PCI ID mapping or map-table decoding can expose nonexistent ports or hide real devices. Timing register writes are shared across master/slave and protected only by `piix_lock`; wrong bit selection can corrupt sibling-device timings. SIDPR access is probed defensively because some systems expose registers that do not work. Suspend/resume has special handling for known broken Toshiba/Sony systems. Global mutation of `piix_port_info[ent->driver_data].flags` for broken poweroff systems can affect later probes of the same controller type. Hyper-V ignore policy intentionally suppresses ATA disks while keeping emulated optical devices.

## Test Signals
Coverage should include PIIX/ICH PATA timing mode transitions, 40/80-wire cable detection including laptop short-cable entries, ICH5/ICH6/ICH8 SATA map values, PCS enabling delays, SIDPR success/failure paths, VMware BMDMA status masking, 450NX errata detection, Clevo IOCFG restore, Hyper-V/Virtual PC DMI behavior, suspend/resume on broken and normal systems, and removal restoring IOCFG. Useful runtime traces are port map logs, DMA mask changes, SCR read/write behavior, and libata EH after reset or PMP errors.
