# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_bios.c

## Purpose
`amdgpu_bios.c` locates, reads, validates, and releases the AMD GPU VBIOS image. It supports APU and dGPU retrieval paths including PCI ROM BAR, VRAM BAR copies, platform ROM resources, ACPI ATRM and VFCT tables, ASIC ROM register reads, disabled ROM BAR access, and SR-IOV dynamic critical-region VBIOS data.

## Important APIs, types, and functions
External entry points include `amdgpu_get_bios()`, `amdgpu_bios_release()`, `amdgpu_read_bios()`, and `amdgpu_soc15_read_bios_from_rom()`. Internal helpers include `check_atom_bios()`, `amdgpu_read_bios_from_vram()`, `amdgpu_read_bios_from_rom()`, `amdgpu_read_platform_bios()`, ACPI `amdgpu_atrm_get_bios()`/`amdgpu_acpi_vfct_bios()`, `amdgpu_read_disabled_bios()`, `amdgpu_get_bios_apu()`, `amdgpu_get_bios_dgpu()`, and `amdgpu_prefer_rom_resource()`.

## Control flow
All read paths allocate or duplicate a candidate VBIOS into `adev->bios`, set `adev->bios_size` when appropriate, and validate it with `check_atom_bios()`. Validation checks the `0x55 0xaa` ROM signature, reads the ATOM header offset at `0x48`, verifies the buffer is large enough, and accepts `ATOM` or byte-swapped `MOTA`.

APU lookup tries VFCT, VRAM BAR, PCI ROM BAR, then platform ROM. dGPU lookup tries ACPI ATRM, VFCT, VRAM BAR for SR-IOV, ROM BAR/platform in an order influenced by `IORESOURCE_ROM_SHADOW`, ASIC-specific ROM reads, and disabled ROM BAR reads. `amdgpu_get_bios()` selects APU or dGPU order and marks `adev->is_atom_fw` for Vega10 and newer ASICs. `amdgpu_soc15_read_bios_from_rom()` is a low-level helper that reads 32-bit ROM data through SMUIO index/data registers, with optional NBIO ROM offset.

## State and persistence behavior
The file owns the heap buffer `adev->bios` and size `adev->bios_size` until released. It also sets `adev->is_atom_fw` after successful lookup. The VBIOS image is copied from firmware/platform/hardware sources into kernel memory; no on-disk persistence is created.

## Dependencies and integration points
It depends on PCI ROM mapping/resource APIs, IO remapping, ACPI ATRM/VFCT tables, AMDGPU SR-IOV dynamic data helpers, ASIC `read_bios_from_rom`/`read_disabled_bios` callbacks, SMUIO/NBIO register callbacks, and ATOM parser expectations. It runs before `amdgpu_atombios_init()` consumes `adev->bios`.

## Risks and edge cases
The retrieval order is platform-sensitive. Some systems expose stale or shadowed ROM resources; hence the ROM/platform preference check. ATRM reads a fixed 256 KiB buffer in 4 KiB pages and validates the full allocation, even if the ACPI method returned less than a page at the end. VFCT parsing must reject short or truncated ACPI tables. VRAM BAR reads assume a 256 KiB copy unless SR-IOV dynamic data returns a size. `check_atom_bios()` is necessary but not a complete bounds validation for all later ATOM table offsets.

## Test signals
Signals include BIOS retrieval on APUs, dGPUs, PX/ATRM laptops, UEFI VFCT systems, SR-IOV VFs with and without dynamic critical regions, shadow ROM platforms, disabled-ROM fallback, SoC15 register ROM reads, malformed signature/header rejection, and release/retry paths that leave `adev->bios` and `bios_size` consistent.
