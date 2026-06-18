## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/acpi.h

### Purpose
`acpi.h` declares the NVKM device ACPI init/fini hooks used internally by the device engine.

### Important APIs, types, and functions
It forward-declares `struct nvkm_device` and declares `nvkm_acpi_init()` and `nvkm_acpi_fini()`.

### Control flow
The header has no runtime flow.

### State and persistence behavior
It owns no state. The functions it declares manipulate notifier state stored in `struct nvkm_device`.

### Dependencies
It includes `core/os.h` for kernel/NVKM base definitions.

### Integration points
`device/base.c` includes this header to call ACPI setup/teardown around device lifecycle. `acpi.c` provides the implementation.

### Risks
Prototype drift between header and implementation would break builds. Keeping this private to the device engine avoids exposing ACPI hooks as broad public NVKM API.

### Test signals
Compile coverage of `base.c` and `acpi.c` with `CONFIG_ACPI` enabled and disabled validates the header.
