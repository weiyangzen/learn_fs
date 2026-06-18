# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_atomfirmware.h

## Purpose
`amdgpu_atomfirmware.h` declares AMDGPU's helper interface for newer ATOM firmware tables. It lets other AMDGPU components query firmware capabilities, memory geometry, RAS/ECC support, clocks, GFX topology, framebuffer reservations, and ASIC init behavior without directly parsing the v2.1 master table layout.

## Important APIs, types, and functions
The header defines `get_index_into_master_table(master_table, table_name)` for computing table indices from master table structures. It declares helpers for firmware capability flags, GPU virtualization support, scratch register initialization, FB scratch allocation, integrated-system/UMC/VRAM/UMA carveout info, memory and SRAM ECC, RAS ROM address, memory training, dynamic boot config, firmware-reserved FB size, GFX/clock info, and `amdgpu_atomfirmware_asic_init()`.

## Control flow
There is no executable flow in the header. Callers include it to invoke the implementation in `amdgpu_atomfirmware.c`, typically after `amdgpu_atombios_init()` has parsed a VBIOS into `adev->mode_info.atom_context`.

## State and persistence behavior
The declared functions read VBIOS-backed ATOM firmware tables and update runtime `struct amdgpu_device` fields or caller-provided output buffers. The header itself owns no state and defines no persistent data.

## Dependencies and integration points
It depends on `struct amdgpu_device`, `struct amdgpu_uma_carveout_info`, and ATOM firmware structure definitions being available in includers. It is the interface between core AMDGPU initialization/power/RAS/memory code and the newer ATOM firmware parser.

## Risks and edge cases
The index macro depends on exact C structure layout of the ATOM master table definitions. If firmware table definitions change without matching implementation updates, callers can query the wrong table. The prototypes also imply that callers must tolerate `-EINVAL`, `-ENODEV`, or false for unsupported firmware revisions.

## Test signals
Build coverage across ASIC generations, probe-time parsing on atomfirmware devices, and targeted tests for missing or unsupported tables are the relevant signals.
