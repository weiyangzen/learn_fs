<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/pci/pci.c -->
## sources/distributed-fs/ceph-client/arch/loongarch/pci/pci.c

### Purpose
`pci.c` implements LoongArch generic PCI hooks, default ECAM address construction, cache-line sizing, MSI/IRQ setup, VGA fixups, and Loongson GPU DMA-hang workarounds.

### Important APIs, Types, And Functions
Functions are `raw_pci_read()`, `raw_pci_write()`, `mcfg_addr_init()`, `pcibios_device_add()`, `pcibios_alloc_irq()`, and init/fixup helpers. PCI fixups are registered for Loongson display controller and GPU device IDs using `DECLARE_PCI_FIXUP_*`.

### Control Flow
Raw config access looks up a domain/bus and delegates to bus ops. `pcibios_init()` sets `pci_dfl_cache_line_size` from the last-level CPU cache. Device add finds the PCH MSI domain and assigns it. IRQ allocation defers to ACPI unless MSI is enabled. VGA fixup chooses a non-Loongson VGA device as default. GPU DMA-hang fixups map display-controller registers behind the GPU, save CRTC enable state early, disable outputs, then restore outputs at final fixup time with polling.

### State, Persistence, And Dependencies
State includes PCI default cache-line size, per-device MSI domain, VGA default device, static `crtc_status`, temporary ioremaps, and device registers. Dependencies include PCI core, ACPI IRQ code, Loongson PCH MSI lookup, IO accessors, and cacheinfo.

### Integration Points
Called by generic PCI enumeration and fixup infrastructure. `acpi.c` uses `mcfg_addr_init()`. Display/GPU workarounds affect Loongson hardware during PCI probing.

### Risks
Config access returns `-EINVAL` when bus lookup fails. MSI domain lookup can return `NULL` on firmware/domain mismatch. GPU workaround assumes device-function layout and BAR/register offsets; wrong assumptions can write unrelated MMIO.

### Test Signals
Boot PCI/ACPI LoongArch systems, enumerate MSI devices, test legacy INTx fallback, validate VGA arbitration, exercise affected Loongson GPUs, and run PCI config-space access tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/pci/pci.c -->
