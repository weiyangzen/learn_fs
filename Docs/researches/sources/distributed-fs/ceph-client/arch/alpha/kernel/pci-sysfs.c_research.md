# sources/distributed-fs/ceph-client/arch/alpha/kernel/pci-sysfs.c

**Purpose:** Implements Alpha-specific PCI sysfs resource and legacy bus mmap/read/write support. Alpha has sparse and dense PCI address spaces, so this file exposes `resourceN_sparse`, `resourceN_dense`, or adjusted legacy names/sizes and maps them through the proper hose base.

**Important APIs/types/functions:** Exposes `pci_remove_resource_files()`, `pci_create_resource_files()`, `pci_mmap_legacy_page_range()`, `pci_adjust_legacy_attr()`, `pci_legacy_read()`, and `pci_legacy_write()`. Local helpers include `hose_mmap_page_range()`, `__pci_mmap_fits()`, `pci_mmap_resource()`, sparse/dense mmap wrappers, `sparse_mem_mmap_fits()`, `pci_create_one_attr()`, `pci_create_attr()`, `__legacy_mmap_fits()`, and `has_sparse()`.

**Control flow:** Resource creation iterates standard BARs, skips empty resources, determines whether sparse and/or dense files are needed based on hose bases and sparse address fit, allocates `bin_attribute` structures plus embedded names, and creates sysfs mmap files. The mmap path validates the requested VMA fits the BAR, translates resource to bus address, adjusts `vm_pgoff` for sparse scaling, adds the hose base, and calls `io_remap_pfn_range()`. Legacy mmap adjusts file names/sizes for sparse spaces and maps bus legacy I/O or memory. Legacy read/write add the hose I/O base then call `inb/inw/inl` or `outb/outw/outl` with alignment checks.

**State and persistence behavior:** Creates/removes sysfs binary attributes attached to `struct pci_dev`; mutates VMA offsets during mmap; performs legacy I/O port reads/writes. No persistent data beyond sysfs lifetime.

**Dependencies and integration points:** Integrates with generic PCI sysfs hooks, Alpha `struct pci_controller` bases, `pcibios_resource_to_bus()`, `iomem_is_exclusive()`, and Alpha I/O accessors.

**Risks:** Sparse mappings multiply sizes by 32 and shift offsets, so fit calculations must match hardware encoding. Resource allocation uses `GFP_ATOMIC`; failures must remove partial files. `pci_legacy_write()` appears to call `outb(port, val)`/`outw(port, val)`/`outl(port, val)` even though Alpha wrappers take `(value, port)`, which is a likely argument-order bug worth review.

**Test signals:** On sparse and dense Alpha hoses, inspect sysfs resource file names/sizes, mmap each BAR within and beyond range, test exclusive iomem rejection, legacy mmap/read/write alignment errors, and verify byte/word/dword legacy writes actually write the intended value to the intended port.
