# sources/distributed-fs/ceph-client/drivers/parisc/lba_pci.c

## Purpose
This file is the PCI Lower Bus Adapter host-bridge driver for PA-RISC systems using Elroy, Mercury, and Quicksilver LBAs. It implements PCI config-space access workarounds, I/O port accessors, firmware resource discovery, PCI root-bus creation, I/O SAPIC interrupt fixup, and host-bridge resource registration.

## Important APIs, Types, And Functions
PCI config ops are `elroy_cfg_read/write()` and `mercury_cfg_read/write()`, with helper workarounds in `lba_rd_cfg()` and `lba_wr_cfg()`. PCI BIOS integration is `lba_fixup_bus()` in `lba_bios_ops`. Resource discovery is split between `lba_pat_resources()` and `lba_legacy_resources()`. Hardware setup is `lba_hw_init()`. Probe is `lba_driver_probe()`. I/O port ops are `lba_astro_port_ops` and, on 64-bit PAT systems, `lba_pat_port_ops`. `lba_set_iregs()` is exported to SBA initialization to program LBA IBASE/IMASK routing. PCI quirks hide unusable Diva/Tosca onboard devices.

## Control Flow
`lba_init()` registers the PA-RISC bridge driver. Probe maps LBA registers, identifies chip revision, selects config ops, registers the integrated I/O SAPIC, allocates `struct lba_device`, registers HBA data, initializes hardware, discovers I/O/MMIO/bus resources through PAT or legacy firmware paths, truncates colliding LMMIO ranges, builds a root-bus resource list, creates the PCI root bus, scans children, optionally assigns PAT resources, enables later probe skipping on fragile Elroy config cycles, and adds discovered devices. During bus fixup, resources are claimed, device BARs are virtualized/claimed, PCI bridges are initialized, and non-bridge devices receive IRQs through `iosapic_fixup_irq()`.

## State And Persistence
Per-LBA state includes hardware revision, mapped register base, HBA resources, bus-number resource, I/O port translation base, IOSAPIC handle, IOMMU pointer from SBA, and flags such as `LBA_FLAG_SKIP_PROBE`. Global state includes `astro_iop_base`, `lba_next_bus`, and selected global PCI port/bios hooks. Hardware state includes LBA error config, arbitration masks, hard/soft fail mode, PCI reset state, and IBASE/IMASK registers programmed by SBA.

## Dependencies And Integration Points
The driver depends on PA-RISC PDC/PAT firmware, Linux PCI core root-bus APIs, I/O SAPIC IRQ routing, SBA IOMMU/resource helpers, PA-RISC HBA structures, and architecture register definitions in `asm/ropes.h`. It is the central integration point between platform firmware and normal Linux PCI enumeration.

## Risks
Elroy config access is highly workaround-sensitive: early revisions require disabling DMA arbitration, smart mode, probe writes, and error-status clearing to avoid fatal master aborts. PAT and legacy resource discovery have different address translations and collision behavior. Resource collisions can be truncated or logged without hard failure. Global PCI port hooks assume compatible host-bridge ordering. The `global_ioc_cnt` style issue is in SBA, but LBA relies on correct SBA parent initialization for DMA. Hiding devices by zeroing `dev->device` is effective but non-obvious to later fixups.

## Test Signals
Signals include root bus creation, stable config reads without HPMC, correct bus numbering, resource trees for I/O/LMMIO/ELMMIO, successful BAR claims, IRQ assignment through IOSAPIC, functional devices behind PCI-PCI bridges, PAT resource assignment for uninitialized devices, and correct I/O port access on both legacy and PAT firmware. Tests should include early Elroy revisions, Mercury/Quicksilver, C8000 LMMIO extension, and Diva/Tosca quirks.
