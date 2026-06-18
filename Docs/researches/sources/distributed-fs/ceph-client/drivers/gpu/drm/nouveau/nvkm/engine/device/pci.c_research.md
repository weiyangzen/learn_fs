<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/pci.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/pci.c

Purpose: this file is the PCI-backed `nvkm_device` transport constructor for Nouveau. Most of the file is a static NVIDIA PCI ID database: top-level `nvkm_device_pci_10de[]` maps device IDs to marketing names and optional subsystem-specific override tables, while `nvkm_device_pci_vendor` entries can override the name and attach `struct nvkm_device_quirk` values such as TV GPIO or pin masks.

Important APIs and functions: `nvkm_device_pci_new()` is the exported constructor. It enables the `pci_dev`, matches vendor/device/subvendor/subdevice against the tables, allocates `struct nvkm_device_pci`, and calls `nvkm_device_ctor()` with the transport type (`NVKM_DEVICE_PCIE`, `NVKM_DEVICE_AGP`, or `NVKM_DEVICE_PCI`) and a stable BDF-derived handle. `nvkm_device_pci_func` supplies BAR address/size lookup, IRQ lookup, suspend/resume preinit/fini, destructor, and `cpu_coherent = !CONFIG_ARM`. BAR mapping is implemented through `nvkm_device_pci_resource_idx()`, which accounts for 64-bit BARs when translating Nouveau logical BARs (`PRI`, `FB`, `INST`) to PCI BAR indices.

Control flow: constructor enables PCI, resolves name/quirk, constructs the generic NVKM device, then sets a DMA mask based on `device.mmu->dma_bits` unless AGP forces 32-bit. If the high mask fails it falls back to 32-bit and updates `dma_bits`. Suspend `fini()` disables the PCI device except for poweroff and marks `pdev->suspend`; `preinit()` re-enables bus mastering on resume.

State and persistence: state is in the allocated `nvkm_device_pci`, especially `pdev`, `suspend`, and the embedded generic `device`. PCI enablement and DMA mask configuration affect kernel device state until teardown or suspend. The static PCI database has no runtime persistence.

Dependencies and integration points: depends on Linux PCI/resource/DMA APIs, `core/pci.h`, `priv.h`, and the generic device constructor. The rest of NVKM consumes the resulting `nvkm_device_func` to access BARs and IRQs without caring whether the backing transport is PCI.

Risks: the BAR index algorithm assumes Nouveau's logical BAR ordering matches probed PCI resources; new devices with unusual BAR layout need careful validation. Adding PCI IDs can change user-visible names or quirks, and wrong quirks may break legacy TV output. Constructor error paths after `nvkm_device_ctor()` do not explicitly disable the PCI device here, relying on higher-level cleanup expectations.

Test signals: probe a range of PCI, PCIe, and AGP NVIDIA devices and verify dmesg names, BAR sizes, IRQ, DMA mask width, suspend/resume, and fallback on systems limited to 32-bit DMA. PCI ID additions should be checked against `lspci -nn` subsystem IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/pci.c -->
