## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/Kbuild

### Purpose
This Kbuild fragment builds the NVKM device engine core and platform-specific device transport layers.

### Important APIs, types, and functions
It appends `acpi.o`, `base.o`, `ctrl.o`, `pci.o`, `tegra.o`, and `user.o` under `nvkm/engine/device/` to `nvkm-y`.

### Control flow
There is no runtime flow. Build inclusion makes device construction, control object methods, ACPI hooks, PCI/Tegra backends, and user object support available.

### State and persistence behavior
The file controls object inclusion only. Runtime device state is implemented by the compiled sources.

### Dependencies
It depends on top-level `engine/Kbuild` and the listed source files.

### Integration points
This is the build entry for `device/base.c`, the central chipset database used by the rest of NVKM. The platform files provide concrete `nvkm_device_func` backends.

### Risks
Omitting `base.o` or platform backends breaks Nouveau device construction. Adding a new platform backend requires this build file to be updated.

### Test signals
Kernel build/link checks, PCI and Tegra probe tests, control-object ioctl tests, and ACPI notifier build coverage validate this fragment.
