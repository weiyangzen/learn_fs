<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_sil.c -->
# sources/distributed-fs/ceph-client/drivers/ata/sata_sil.c

## Purpose

This is the libata PCI driver for first-generation Silicon Image SiI 3112/3512/3114 SATA controllers and ATI-branded variants. It maps the controller MMIO BAR, configures two or four SFF/BMDMA ports, applies device/controller errata, handles SATA IRQ quirks, and exposes the devices as SCSI disks through libata.

## Important APIs, types, and functions

The PCI binding is `sil_pci_driver` with `sil_pci_tbl`. `sil_port_info[]` selects flags for 3112, 3512, and 3114 boards, including `SIL_FLAG_NO_SATA_IRQ`, `SIL_FLAG_RERR_ON_DMA_ACT`, and `SIL_FLAG_MOD15WRITE`. `sil_ops` customizes device config, mode programming, DMA setup/start/stop, PRD preparation, freeze/thaw, and SCR access. Important helpers are `sil_fill_sg()`, `sil_set_mode()`, `sil_host_intr()`, `sil_interrupt()`, `sil_dev_config()`, `sil_init_controller()`, `sil_broken_system_poweroff()`, and `sil_init_one()`.

## Control flow

Probe determines port count, applies a DMI poweroff spindown quirk, allocates an ata host, enables and maps BAR5, sets a 32-bit ATA DMA mask, initializes per-port taskfile/BMDMA/SCR addresses from `sil_port[]`, initializes FIFO arbitration and errata bits, then activates the host with `sil_interrupt()`. Command flow uses normal SFF taskfile helpers but uses the second BMDMA register for Large Block Transfer start/stop. Interrupt handling scans every port's `bmdma2` register for DMA completion or SATA IRQ, clears SError immediately on affected chips, validates HSM state, stops DMA on completion, acknowledges BMDMA IRQs, and advances libata HSM.

## State and persistence behavior

State is PCI config/MMIO programming, per-port libata state, global module parameter `slow_down`, and detected drive quirks. It does not persist on disk. Resume calls `ata_pci_device_do_resume()`, re-runs controller initialization, and resumes the ata host.

## Dependencies and integration points

The driver integrates with PCI managed resource helpers, DMI matching, libata BMDMA32/SFF support, SCSI host exposure, and the kernel PCI PM path. Device-specific errata are keyed from IDENTIFY model strings and DMI data.

## Risks

The driver has several hardware errata paths: SATA IRQ masking may not work on some 3112s, R_ERR-on-DMA-activate requires SFIS config changes, Seagate mod15 write workarounds cap requests to 15 sectors, and Maxtor quirks limit UDMA. DMA descriptors truncate to 32-bit addresses. Freeze/thaw must coordinate SIEN, global interrupt mask, DMA enable, and taskfile accessibility. The viewed source contains a stray duplicated comment terminator near `sil_freeze()`, a potential compile risk if not removed in the actual build input.

## Test signals

Build with SiI SATA enabled, enumerate 2-port and 4-port controllers, run DMA read/write stress including large requests, verify Seagate/Maxtor quirk messages with matching model strings, test suspend/resume, SATA link change handling, and DMI spindown behavior. Watch for spurious IRQ rate limiting, HSM errors, and SError clear/freeze paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/sata_sil.c -->
