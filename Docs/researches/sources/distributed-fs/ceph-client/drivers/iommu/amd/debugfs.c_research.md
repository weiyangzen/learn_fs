# sources/distributed-fs/ceph-client/drivers/iommu/amd/debugfs.c

## Purpose

This file exposes AMD IOMMU diagnostic state through debugfs when `CONFIG_AMD_IOMMU_DEBUGFS` is enabled. It provides per-IOMMU files for reading arbitrary MMIO and PCI capability registers and dumping command buffers, plus global files for selecting a device ID and dumping that device's DTE and interrupt-remapping table.

## Important APIs And Functions

`amd_iommu_debugfs_setup()` creates `debug/iommu/amd`, per-IOMMU directories named `iommuNN`, and files `mmio`, `capability`, `cmdbuf`, `devid`, `devtbl`, and `irqtbl`. `iommu_mmio_write()` validates and stores an MMIO offset in `iommu->dbg_mmio_offset`; `iommu_mmio_show()` reads a 64-bit register with `readq()`. `iommu_capability_write()` stores a PCI capability offset in `iommu->dbg_cap_offset`, and `iommu_capability_show()` reads a config dword at `cap_ptr + offset`.

`iommu_cmdbuf_show()` locks `iommu->lock`, reads command-buffer head/tail registers, and prints all `CMD_BUFFER_ENTRIES`. `devid_write()` parses `seg:bus:slot.func` or `bus:slot.func`, validates it against PCI segment tables and reverse lookup, and stores the packed SBDF in global `sbdf`; `devid_show()` reports the selected device. `dump_dte()` prints the selected device table entry. `dump_irte()` obtains the IRQ lookup table and DTE interrupt-table length, locks the remap table, and delegates to `dump_128_irte()` or `dump_32_irte()` based on guest interrupt mode. `iommu_irqtbl_show()` also checks global `irq_remapping_enabled`.

## Control Flow And State

The setup function runs after AMD IOMMU initialization. User interaction is two-step for device-specific files: write a device ID to `devid`, then read `devtbl` or `irqtbl`. Per-IOMMU MMIO/capability files similarly store the selected offset before readback. State is diagnostic-only but mutable: `sbdf` is a single global selector shared across readers, and per-IOMMU debug offsets are stored in `struct amd_iommu`.

## Dependencies And Integration Points

The file depends on generic IOMMU debugfs root `iommu_debugfs_dir`, AMD global IOMMU/PCI-segment lists, DTE accessors, IRQ remapping state, and IRTE type definitions. It integrates with debugfs seq-file show/store helpers and PCI config access.

## Risks

The primary risk is information exposure and unsafe low-level introspection, which is why Kconfig warns against production use. The global `sbdf` selector is not per-open and can race between concurrent users. MMIO reads are bounded by `mmio_phys_end` but still allow broad register inspection. Command-buffer and IRTE dumps can be stale relative to hardware activity. The IRTE dump trusts DTE length fields after validation against known 512/2K encodings.

## Test Signals

Test with `CONFIG_IOMMU_DEBUGFS=y` and `CONFIG_AMD_IOMMU_DEBUGFS=y`; verify directory creation after AMD IOMMU init, valid/invalid writes to `mmio`, `capability`, and `devid`, command-buffer dumps under load, DTE dumps for known PCI devices, and graceful messages when IRQ remapping is disabled or no valid device is selected. Concurrency testing should check that locks prevent torn command/IRTE dumps while acknowledging the global selector semantics.
