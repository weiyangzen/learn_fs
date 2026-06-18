<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadowpci.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadowpci.c

### Purpose

PCI ROM shadow backend. It maps or enables the PCI expansion ROM and copies VBIOS bytes through the shadow-source interface.

### Important APIs, types, and functions

`nvbios_pcirom` defines init/read/size/fini callbacks. The implementation handles PCI ROM enable/map lifetime and reports available ROM size.

### Control flow

Init obtains access to the PCI ROM resource, read copies offsets into the BIOS buffer, and fini releases/unmaps the PCI ROM. `shadow.c` scores the copied image afterward.

### State and persistence behavior

Backend mapping state is temporary. If selected, only the copied BIOS buffer persists.

### Dependencies and integration points

Depends on Linux PCI ROM helpers and the NVKM device's PCI handle. It is a primary source on discrete PCI/PCIe GPUs.

### Risks

PCI ROM access can be disabled, truncated, or unavailable after firmware handoff. Mapping lifetime and enable/disable ordering must be correct.

### Test signals

Source read size: 134 lines, 3173 bytes. Discrete GPU boot tests, PCI ROM access failure fallback, runtime PM/suspend interactions, and comparison with `/sys/bus/pci/.../rom` dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadowpci.c -->
