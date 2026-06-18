# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/nv4c.c

## Purpose
Defines NV4C PCI backend with the standard `0x088000` config aperture and no generation-specific callbacks.

## Important APIs, Types, And Functions
Exports `nv4c_pci_new`.

## Control Flow
Construction delegates to common PCI setup; runtime behavior comes from common code only.

## State And Persistence
Common `struct nvkm_pci` state persists the config aperture and MSI/link state if applicable.

## Dependencies And Integration Points
Depends on `priv.h` and common PCI constructor.

## Risks And Test Signals
Risk is absence of MSI rearm or PCIe callbacks for hardware that might need them. Test config access and interrupt behavior on NV4C-class devices.
