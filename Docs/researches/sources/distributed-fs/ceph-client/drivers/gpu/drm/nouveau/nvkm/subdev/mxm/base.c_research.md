# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/mxm/base.c

## Purpose
Constructs the NVKM MXM subdevice and locates a valid MXM System Information Structure from ROM/I2C, ACPI DSM, or ACPI WMI. It decides whether later DCB sanitization should run.

## Important APIs, Types, And Functions
Key functions are `mxm_shadow_rom_fetch`, `mxm_shadow_rom`, `mxm_shadow_dsm`, `wmi_wmmx_mxmi`, `mxm_shadow_wmi`, `mxm_shadow`, and exported `nvkm_mxm_new_`. The `_mxm_shadow` table orders ROM, DSM, and WMI providers according to build configuration.

## Control Flow
`nvkm_mxm_new_` reads the MXM VBIOS table and version. If no VBIOS MXM data exists it exits successfully with no work. Otherwise it calls `mxm_shadow`, which tries each provider, validates the resulting `mxm->mxms` with `mxms_valid`, and frees failed candidates. Successful discovery logs MXMS version, optionally dumps descriptors, and sets `MXM_SANITISE_DCB` unless `NvMXMDCB=false`.

## State And Persistence
Owns `struct nvkm_mxm`, `mxm->mxms` allocated from ROM/ACPI data, and `mxm->action`. The SIS blob persists for later MXM parsing and DCB sanitization.

## Dependencies And Integration Points
Depends on BIOS MXM helpers, I2C bus lookup, ACPI DSM/WMI APIs when enabled, and `core/option.h`. `nv50.c` consumes `mxm->action` and the parsed MXMS data.

## Risks And Test Signals
Risks include malformed ACPI buffers, bad length fields before allocation, checksum/signature failures, systems requiring exact DSM revision, and silent fallback when SIS is absent. Test MXM laptops with ROM, DSM, and WMI paths; invalid checksum tables; `NvMXMDCB=0`; and ACPI-disabled builds.
