# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/base.c

## Purpose
Provides the common NVKM PCI subdevice lifecycle, config-space helpers, AGP/PCIe initialization hooks, ROM shadow control, MSI enablement, and constructor.

## Important APIs, Types, And Functions
Exports `nvkm_pci_msi_rearm`, `nvkm_pci_rd32`, `nvkm_pci_wr08`, `nvkm_pci_wr32`, `nvkm_pci_mask`, `nvkm_pci_rom_shadow`, and `nvkm_pci_new_`. Internal lifecycle hooks are `nvkm_pci_preinit`, `nvkm_pci_oneinit`, `nvkm_pci_init`, `nvkm_pci_fini`, and `nvkm_pci_dtor`.

## Control Flow
Constructor allocates `struct nvkm_pci`, stores generation callbacks, initializes PCIe speed/width to -1, sets up AGP if needed, chooses MSI eligibility with chipset/bridge/big-endian exclusions and `NvMSI`, then enables MSI only if a rearm callback exists. Init initializes AGP or PCIe, runs generation init, and rearms pending MSI.

## State And Persistence
Persists `pci->func`, Linux `pci_dev`, AGP state, MSI state, and requested PCIe link state. Config writes modify device hardware registers.

## Dependencies And Integration Points
Depends on core PCI device access, AGP helpers, PCIe helpers, and generation-specific `nvkm_pci_func` tables. Device constructors call `nvkm_pci_new_`.

## Risks And Test Signals
Risks include MSI enabled on unsupported bridges, config aperture mismatch, AGP/PCIe init ordering, ROM shadow bit mistakes, and resource cleanup on constructor failures. Test MSI on/off, big-endian builds, AGP devices, PCIe link setup, module unload, and config read/write smoke tests.
