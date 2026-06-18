# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_atomfirmware.c

## Purpose
`amdgpu_atomfirmware.c` parses newer ATOM firmware master data/command tables, mainly used by Vega10 and later devices. It extracts firmware capabilities, scratch register offsets, VRAM/UMC/integrated-system memory information, UMA carveout choices, ECC/RAS data, clock references, GFX topology, firmware-reserved framebuffer size, and executes the newer ASIC init command table.

## Important APIs, types, and functions
Public helpers include `amdgpu_atomfirmware_query_firmware_capability()`, `amdgpu_atomfirmware_gpu_virtualization_supported()`, `amdgpu_atomfirmware_scratch_regs_init()`, `amdgpu_atomfirmware_allocate_fb_scratch()`, `amdgpu_atomfirmware_get_integrated_system_info()`, `amdgpu_atomfirmware_get_umc_info()`, `amdgpu_atomfirmware_get_vram_info()`, `amdgpu_atomfirmware_get_uma_carveout_info()`, `amdgpu_atomfirmware_mem_ecc_supported()`, `amdgpu_atomfirmware_sram_ecc_supported()`, `amdgpu_atomfirmware_dynamic_boot_config_supported()`, `amdgpu_atomfirmware_ras_rom_addr()`, `amdgpu_atomfirmware_get_clock_info()`, `amdgpu_atomfirmware_get_gfx_info()`, `amdgpu_atomfirmware_mem_training_supported()`, `amdgpu_atomfirmware_get_fw_reserved_fb_size()`, and `amdgpu_atomfirmware_asic_init()`. Internal unions cover revisioned `firmware_info`, `igp_info`, `umc_info`, `vram_info`, `vram_module`, `smu_info`, and `gfx_info` tables.

## Control flow
Most helpers compute a v2.1 master-table index with `get_index_into_master_table()`, call `amdgpu_atom_parse_data_header()` or `amdgpu_atom_parse_cmd_header()`, check table revision, cast `ctx->bios + data_offset` to the matching revisioned structure, then copy selected little-endian fields into AMDGPU runtime state or caller outputs. Firmware capability is cached in `adev->mode_info.firmware_flags` by `amdgpu_atombios_init()`, and later helpers test that cache for virtualization, SRAM ECC, dynamic boot config, and memory training.

`amdgpu_atomfirmware_allocate_fb_scratch()` parses `vram_usagebyfirmware` v2.1/v2.2, creates SR-IOV firmware/driver VRAM reservations when requested, skips reservation parsing for dynamic critical-region VFs, and allocates ATOM interpreter scratch memory with a 20 KiB fallback. Memory-info helpers select APU integrated-system tables, UMC tables, or dGPU VRAM module tables and convert ATOM memory type encodings to AMDGPU VRAM type enums. Clock info combines firmware, SMU, UMC, and Navi+ GFX table data to initialize default clocks and SPLL/MPLL reference parameters. ASIC init builds an `asic_init_ps_allocation_v2_1` parameter block from boot clocks and calls `amdgpu_atom_execute_table()`.

## State and persistence behavior
This file updates runtime fields in `adev->mode_info`, `adev->clock`, `adev->pm`, `adev->gfx.config`, `adev->gfx.cu_info`, `adev->bios_scratch_reg_offset`, `adev->ras_default_ecc_enabled`, and TTM VRAM reservation state. It allocates `ctx->scratch` in system memory. It reads firmware tables from the in-memory VBIOS only and does not persist derived state outside the driver/hardware runtime.

## Dependencies and integration points
It depends on ATOM firmware table definitions, `amdgpu_atom_parse_*()` and `amdgpu_atom_execute_table()`, TTM VRAM reservation helpers, RAS state, scratch register access, SMU/UMC/GFX table contracts, and SoC generation enums such as `CHIP_NAVI10`. It is selected by `amdgpu_atombios_init()` when `adev->is_atom_fw` is true and feeds memory, RAS, display/clock, and ASIC initialization code.

## Risks and edge cases
Revision handling is intentionally strict; unsupported `frev`/`crev` combinations return `-EINVAL` or false. Firmware-controlled offsets and module sizes must be valid; malformed VRAM module chains or module IDs can cause wrong memory geometry. Several helpers rely on `bios_scratch_reg_offset` being initialized before reading module/vendor scratch values. `amdgpu_atomfirmware_get_clock_info()` calls `BUG()` for unexpected Navi+ GFX table revisions, which makes malformed or future firmware especially risky. SR-IOV reservation flag interpretation must match firmware semantics to avoid reserving wrong VRAM ranges.

## Test signals
Signals include boot/probe on Vega, Navi, and newer ASICs with different firmware table revisions; APU integrated-system and UMA carveout parsing; UMC and VRAM module memory-width/type/vendor results; ECC/RAS capability detection; firmware-reserved framebuffer size; dynamic boot and memory-training capability bits; SR-IOV VF dynamic critical-region behavior; ASIC init command execution; malformed table revision tests; and comparing parsed clocks/GFX topology with hardware discovery.
