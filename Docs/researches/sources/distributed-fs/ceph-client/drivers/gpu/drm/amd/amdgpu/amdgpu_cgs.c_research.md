# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_cgs.c

## Purpose
`amdgpu_cgs.c` implements AMDGPU's Common Graphics Services adapter. It wraps register access and firmware lookup behind `struct cgs_ops` so older power-management/SMU-facing code can interact with AMDGPU devices through the CGS abstraction.

## Important APIs, types, and functions
The public lifecycle functions are `amdgpu_cgs_create_device()` and `amdgpu_cgs_destroy_device()`. Internal ops include direct register reads/writes, indirect register reads/writes for PCIE/SMC/UVD/DIDT/GC CAC/SE CAC spaces, firmware type conversion, firmware version lookup, and `amdgpu_cgs_get_firmware_info()`. `struct amdgpu_cgs_device` embeds `struct cgs_device` and stores the backing `struct amdgpu_device`.

## Control flow
Creation allocates an `amdgpu_cgs_device`, installs `amdgpu_cgs_ops`, and stores `adev`. Register ops translate CGS calls to AMDGPU MMIO macros. Firmware info first handles non-SMU microcode by converting CGS firmware IDs to `AMDGPU_UCODE_ID`, reading the already-loaded firmware header, returning kernel pointer, image size, MC address, version, firmware version, and feature version, with special handling for MEC jump tables. SMU firmware requests choose ASIC-specific firmware filenames when `adev->pm.fw` is not loaded, request the firmware, optionally register it for PSP loading, parse the SMC firmware header, print it, update PM firmware version, and return image metadata.

## State and persistence behavior
The CGS wrapper owns one heap allocation per CGS device. Firmware info reads and may populate runtime firmware state in `adev->pm.fw`, `adev->pm.fw_version`, `adev->firmware.ucode[AMDGPU_UCODE_ID_SMC]`, and `adev->firmware.fw_size`. Register accesses directly read or mutate hardware registers. There is no durable persistence.

## Dependencies and integration points
It depends on CGS interfaces, AMDGPU register macros, firmware request/release helpers, AMDGPU ucode header layouts, PM/SMU firmware storage, PSP firmware loading state, PCI device/revision IDs, and ASIC enums. It integrates with legacy SMU/power-management components that expect CGS operations rather than native AMDGPU calls.

## Risks and edge cases
Firmware filename selection is a large ASIC/revision switch and can break new revisions if not updated. Audio endpoint indirect register access is explicitly unimplemented. Unsupported indirect spaces call `BUG()`, which is severe for bad callers. SMU firmware loading mutates shared `adev->pm.fw` state and must align with broader firmware loading policy. MEC JT1/JT2 sizing and offsets depend on firmware header fields being sane.

## Test signals
Signals include CGS creation/destruction, register read/write smoke tests for each supported indirect space, firmware info queries for SDMA/CP/RLC/MEC and SMU IDs across supported ASICs, missing firmware failure paths, PSP load-type accounting, kicker firmware selection by PCI revision/device, and rejection of unsupported firmware IDs.
