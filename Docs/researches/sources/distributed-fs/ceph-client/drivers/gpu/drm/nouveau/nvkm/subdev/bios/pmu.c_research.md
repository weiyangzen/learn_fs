<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/pmu.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/pmu.c

### Purpose

Parser for PMU firmware/script metadata in the VBIOS. It exposes PMU table headers and per-entry data to the PMU subdevice.

### Important APIs, types, and functions

`nvbios_pmuTe/Tp()` and entry parse helpers decode table version/header/count/length and PMU-specific fields declared in `pmu.h`.

### Control flow

The table is located through BIT metadata, validated by version, and indexed using standard header plus entry length arithmetic. Decoded records tell PMU code where firmware or init data is located.

### State and persistence behavior

No persistent state. PMU subdevice owns firmware/runtime state after consuming decoded metadata.

### Dependencies and integration points

Depends on BIT parsing and generic BIOS readers. It integrates with the NVKM PMU loader and power-management firmware setup.

### Risks

Unsupported table versions or bad offsets can prevent PMU firmware load or cause use of wrong firmware data.

### Test signals

Source read size: 102 lines, 3350 bytes. PMU firmware load tests, VBIOS parser fixtures, power-management init on supported GPUs, and missing-table fallback tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/pmu.c -->
