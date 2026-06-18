# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/Kbuild

## Purpose
Lists PCI subdevice implementation objects included in the NVKM build.

## Important APIs, Types, And Functions
The file adds common AGP/base/PCIe objects and generation-specific PCI backends from NV04 through GH100.

## Control Flow
There is no runtime control flow. Kbuild appends each object to `nvkm-y`.

## State And Persistence
No runtime state is stored. Its effect is persistent build graph membership.

## Dependencies And Integration Points
Integrates with nouveau's aggregate Kbuild. The listed generation files provide `*_pci_new` constructors referenced by device tables.

## Risks And Test Signals
Risk is missing objects causing unresolved constructors or dead code after source changes. Test with allmodconfig-style nouveau builds and symbol resolution for each generation constructor.
