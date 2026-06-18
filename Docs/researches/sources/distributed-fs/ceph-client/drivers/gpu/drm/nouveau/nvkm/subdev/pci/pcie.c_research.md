# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/pci/pcie.c

## Purpose
Provides common PCIe speed/version policy: speed enum conversion, version raise during init, one-time max-speed logging, and requested link speed setting.

## Important APIs, Types, And Functions
Exports `nvkm_pcie_oneinit`, `nvkm_pcie_init`, and `nvkm_pcie_set_link`. Internal helpers are `nvkm_pcie_speed`, `nvkm_pcie_get_version`, `nvkm_pcie_get_max_version`, and `nvkm_pcie_set_version`.

## Control Flow
Init reads current and max version; if the card supports a higher version, it calls generation `set_version` and warns on failure. It then runs generation PCIe init and applies any stored requested speed/width. `nvkm_pcie_set_link` validates PCIe presence and callback availability, clamps requested speed to bus and card max, stores requested speed/width, skips if already current, and calls generation `set_link`.

## State And Persistence
Stores desired link speed/width in `pci->pcie`. Hardware link/version state persists through generation callbacks.

## Dependencies And Integration Points
Depends on Linux PCI bus speed reporting and `nvkm_pci_func.pcie` callbacks. All generation files with PCIe support plug into this policy.

## Risks And Test Signals
Risks include out-of-range speed-string indexing, unsupported 16 GT/s fallback to 8 GT/s, callback absence, clamping mistakes, and version raise failures. Test Gen1/Gen2/Gen3 boards, bus max lower than card max, stored requested speed across init, and non-PCIe/unsupported callbacks.
