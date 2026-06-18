# sources/distributed-fs/ceph-client/drivers/uio/uio_pci_generic_sva.c

## Purpose
`uio_pci_generic_sva.c` is a generic PCI UIO driver variant that binds a PCI device to the current process address space with IOMMU Shared Virtual Addressing on UIO open, exposes the assigned PASID through sysfs, and maps PCI memory BARs for userspace.

## Important APIs, Types, And Functions
- `struct uio_pci_sva_dev` stores `pdev`, embedded `uio_info`, `iommu_sva *sva_handle`, and `pasid`.
- `uio_pci_sva_open()` detaches any existing IOMMU domain and calls `iommu_sva_bind_device(&pdev->dev, current->mm)`.
- `uio_pci_sva_release()` calls `iommu_sva_unbind_device()`.
- `probe()` enables PCI, sets a 64-bit coherent DMA mask, enables bus mastering, allocates MSI/MSI-X vectors when available, fills UIO memory maps, and registers UIO.
- `pasid_show()` exports `udev->pasid`; `uio_pci_sva_attr_groups` attaches it to the PCI driver device.

## Control Flow
Binding is dynamic because `id_table` is `NULL`. Probe enables the device, configures DMA, sets bus master, optionally allocates one MSI or MSI-X vector, initializes UIO callbacks and memory maps, registers the UIO device, and stores `udev` in PCI driver data. When userspace opens the UIO device, the driver binds the PCI device to `current->mm` through SVA and records the PASID. On release it unbinds that SVA handle.

## State And Persistence Behavior
Per-device runtime state includes the PASID and SVA handle for the currently open userspace address space. This state is not persistent and should be valid only between open and release. The device remains bus-master capable after probe until remove or external reset.

## Dependencies And Integration Points
The driver integrates PCI, UIO, DMA mask setup, MSI/MSI-X allocation, and Linux IOMMU SVA APIs. Userspace consumes BAR mappings, UIO interrupts, and the `pasid` sysfs attribute to coordinate device-side address-space tagging.

## Risks And Edge Cases
The implementation mixes devm allocation/registration with manual `kfree()` in error/remove paths, which is a lifetime risk. It does not request PCI regions before mapping resource descriptors and remove calls `pci_release_regions()` despite no matching request in probe. `info.irq = 0` may be set for polling fallback instead of `UIO_IRQ_NONE`. `uio_pci_sva_release()` unconditionally unbinds `sva_handle` and does not clear it. There is no locking around PASID/SVA state for multiple opens. Detaching an existing IOMMU domain on open is a broad side effect.

## Test Signals
Build only where IOMMU SVA is available. Bind a capable PCIe device, open `/dev/uioX`, and verify `pasid` becomes non-negative. Close and reopen from another process and confirm unbind/rebind behavior. Exercise probe failure paths with no MSI vectors and with no IOMMU SVA support. Use kmemleak/KASAN or devres debugging to catch the devm/manual-free mismatch.
