# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/priv.h

## Purpose
Defines the private PCI subdevice function table and declares shared generation helper functions.

## Important APIs, Types, And Functions
Defines `nvkm_pci(p)`, `struct nvkm_pci_func`, and `nvkm_pci_new_`. Declares MSI rearm helpers, G84/GF100/GK104 PCIe helper APIs, and common PCIe lifecycle functions.

## Control Flow
No executable control flow exists.

## State And Persistence
The `nvkm_pci_func` layout is the persistent cross-file callback contract for config aperture, init, MSI rearm, and PCIe operations.

## Dependencies And Integration Points
Includes public `<subdev/pci.h>`. Used by every PCI implementation file.

## Risks And Test Signals
Risk is ABI-like callback drift between declaration and implementation. Build tests catch signatures; runtime PCIe/MSI tests catch semantic mismatches in populated callback tables.
