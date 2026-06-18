## sources/control-plane/mayastor/io-engine/src/bdev/nvme.rs

### Purpose
`nvme.rs` adapts local PCIe NVMe devices to the generic URI bdev create/destroy/probe API. It wraps SPDK `spdk_bdev_nvme_create()` for `pcie:///BDF`-style devices and validates host driver binding during probe.

### Important APIs, Types, And Functions
`NVMe` stores the PCI address-derived controller name and original URL. `TryFrom<&Url>` validates path segments. `GetName` returns the namespace bdev name by appending `n1`. `CreateDestroy` performs asynchronous SPDK creation and deletion. `Probe` checks `/sys` driver binding. `NvmeCreateContext` owns the transport id and namespace name output pointer array.

### Control Flow
`create()` rejects an existing controller name, fills default controller opts, builds a PCIe transport id with `traddr = name`, calls `spdk_bdev_nvme_create()`, waits for the create callback, then looks up `<name>n1` and adds the original URI alias. `destroy()` deletes the SPDK NVMe controller by base name if `<name>n1` exists and attempts to restore the alias if deletion fails. `probe()` accepts `vfio-pci` and `uio_pci_generic`, reports kernel-bound NVMe as `PciKernelBound`, and distinguishes unsupported PCI driver from non-NVMe PCI device.

### State, Persistence, And Dependencies
State is SPDK runtime controller/bdev state plus bdev alias metadata; nothing is persisted. Dependencies include sysfs, SPDK NVMe bdev FFI, `bdev_nvme_delete_async`, URI helpers, `UntypedBdev`, and callback conversion helpers.

### Integration Points
This is the legacy SPDK bdev path for local NVMe and is selected by URI parsing. Probe errors inform callers whether the device must be rebound to a userspace PCI driver before creation.

### Risks
The duplicate check uses the base controller name, while successful lookup uses `<name>n1`; naming mismatch can affect edge cases. The create callback ignores `bdev_count`, so a zero-namespace attach may fail later through the expect lookup rather than a structured error. Alias restoration on failed destroy is best effort.

### Test Signals
Test parsing empty paths, PCI transport id construction, sysfs probe outcomes for missing driver/kernel-bound/userspace-bound/unsupported driver, create callback errors, zero namespace behavior, alias addition failure logging, destroy missing bdev, and failed deletion alias restoration.
