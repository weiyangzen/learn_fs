<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/mmconfig_32.c -->
# sources/distributed-fs/ceph-client/arch/x86/pci/mmconfig_32.c

## Purpose
`mmconfig_32.c` implements the 32-bit x86 ECAM config-space accessor. Because 32-bit kernels cannot cheaply keep all ECAM space permanently mapped, it maps one device's 4KB extended config page at a fixed virtual address on demand.

## Important APIs, types, and functions
The file defines `pci_mmcfg_read()`, `pci_mmcfg_write()`, `pci_exp_set_dev_base()`, `get_base_addr()`, `pci_mmcfg` raw-ops table, `pci_mmcfg_arch_init()`, `pci_mmcfg_arch_free()`, `pci_mmcfg_arch_map()`, and `pci_mmcfg_arch_unmap()`. State is `mmcfg_last_accessed_device` and `mmcfg_last_accessed_cpu`.

## Control flow
Each read/write validates bus, devfn, and register bounds, looks up the region under RCU, locks `pci_config_lock`, maps the target device page into `FIX_PCIE_MCFG` if the cached device/cpu differs, performs byte/word/dword MMIO access, then unlocks and drops RCU. Architecture init installs `raw_pci_ext_ops = &pci_mmcfg`.

## State and persistence behavior
The fixmap mapping is cached per last device and CPU to avoid repeated `set_fixmap_nocache()` calls. Unmap invalidates that cache when a region is deleted. No per-region virtual mapping is stored on 32-bit.

## Dependencies and integration points
It depends on `pci_mmcfg_list` lookup from the shared file, fixmap slot `FIX_PCIE_MCFG`, `pci_config_lock`, RCU, and generic raw PCI extended ops. It coexists with type-1 access for conventional config space.

## Risks and edge cases
All accesses serialize on `pci_config_lock`, and the cached fixmap is CPU-sensitive. Invalid region lookup returns `-EINVAL` and all-ones reads. The physical base is stored as `u32`, so 32-bit ECAM above 4GB is intentionally unsupported by earlier validation.

## Test signals
32-bit boots with ECAM-enabled hardware, extended PCI capability reads, concurrent config access stress, ECAM hot-delete invalidation, and `pci=nommconf` fallback checks are appropriate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/pci/mmconfig_32.c -->
