# sources/distributed-fs/ceph-client/drivers/mfd/cs5535-mfd.c

### Purpose
`cs5535-mfd.c` is the core PCI MFD driver for AMD/NS CS5535 and CS5536 southbridge ISA functions. The southbridge exposes several legacy I/O BARs for SMBus, GPIO, multi-function general-purpose timers, power management, and ACPI; this driver translates the PCI BAR layout into platform child devices.

### Important APIs, Types, And Functions
The key type is `enum cs5535_mfd_bars`, which fixes BAR indices for SMB, GPIO, MFGPT, PMS, ACPI, and `NR_BARS`. Static state includes `cs5535_mfd_resources[NR_BARS]`, `cs5535_mfd_cells[]` for generic child devices, and `cs5535_olpc_mfd_cells[]` for OLPC ACPI children. Runtime entry points are `cs5535_mfd_probe()` and `cs5535_mfd_remove()`. PCI integration is through `cs5535_mfd_pci_tbl`, `cs5535_mfd_driver`, and `module_pci_driver()`.

### Control Flow
Probe enables the PCI device, copies each PCI BAR start/end into the matching static `struct resource` with `IORESOURCE_IO`, and requests the PMS BAR region. It then calls `mfd_add_devices()` to register `cs5535-smb`, `cs5535-gpio`, `cs5535-mfgpt`, and `cs5535-pms` platform children, each with one resource pointing at its BAR. On OLPC systems detected by `machine_is_olpc()`, probe also requests the ACPI BAR and adds `olpc-xo1-pm-acpi` and `olpc-xo1-sci-acpi`, both sharing the ACPI resource. Error handling unwinds in reverse order: release ACPI if needed, remove MFD children, release PMS, and disable PCI. Remove calls `mfd_remove_devices()`, releases ACPI on OLPC, releases PMS, and disables the PCI device.

### State, Persistence, And Dependencies
The driver stores BAR resources in a file-static array, so the resources persist for the lifetime of the module and are shared by the registered cells. It does not allocate per-device private data or persist configuration beyond requested PCI I/O regions and platform device registration. Dependencies include PCI core APIs, the MFD core, platform device creation inside `mfd_add_devices()`, Linux resource descriptors, `machine_is_olpc()` from `<asm/olpc.h>`, and PCI IDs for NS CS5535 ISA and AMD CS5536 ISA.

### Integration Points
The driver binds PCI devices with `PCI_VENDOR_ID_NS/PCI_DEVICE_ID_NS_CS5535_ISA` and `PCI_VENDOR_ID_AMD/PCI_DEVICE_ID_AMD_CS5536_ISA`. Child drivers bind by platform names `cs5535-smb`, `cs5535-gpio`, `cs5535-mfgpt`, `cs5535-pms`, and on OLPC, `olpc-xo1-pm-acpi` and `olpc-xo1-sci-acpi`. The BAR ordering is hardware-spec-defined and hardcoded, so the child drivers depend on this file mapping the correct I/O region to each cell.

### Risks
`cs5535_mfd_resources` is global rather than per-device, so the implementation assumes effectively one matching southbridge instance; multiple devices would overwrite shared resources. Only PMS and OLPC ACPI regions are explicitly requested by this driver; the other child resources are handed down without parent-level `pci_request_region()` calls, so resource ownership assumptions rely on child behavior and platform expectations. OLPC ACPI children share one ACPI BAR resource, which is intentional but requires non-conflicting child access. The success log always reports only `ARRAY_SIZE(cs5535_mfd_cells)`, so OLPC-specific devices are not reflected in the count.

### Test Signals
Validation should cover probe/remove on CS5535 and CS5536 hardware or emulation, with each child driver receiving the expected I/O start/end from its BAR. Error-injection tests around `pci_enable_device()`, `pci_request_region(PMS_BAR)`, `mfd_add_devices()`, ACPI BAR request, and OLPC MFD addition should verify reverse-order cleanup. OLPC-specific testing should confirm both ACPI children bind and can coexist on the shared ACPI resource. A resource audit should confirm no leaked PCI regions after failed probe or remove.
