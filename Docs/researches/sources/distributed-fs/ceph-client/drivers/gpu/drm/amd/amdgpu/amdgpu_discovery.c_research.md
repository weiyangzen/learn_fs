# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_discovery.c

## Purpose

`amdgpu_discovery.c` is the AMDGPU hardware discovery and IP-block selection implementation. It loads the IP discovery binary from firmware, VRAM TMR, or system memory, validates binary and table signatures/checksums, extracts register base addresses and IP versions, applies harvest information, exposes discovery topology through sysfs and devcoredump, and finally registers the correct AMDGPU IP block implementations for the detected ASIC.

This file is a boot-time bridge between hardware/firmware discovery data and the rest of the driver. Most later AMDGPU subsystems depend on `adev->reg_offset`, `adev->ip_versions`, masks such as `adev->gfx.xcc_mask` and `adev->sdma.sdma_mask`, family/APU flags, and function tables selected here.

## Important APIs, types, and functions

- `amdgpu_discovery_set_ip_blocks(struct amdgpu_device *adev)` is the public entry point. It handles legacy fixed tables for older ASICs, dynamic discovery for newer/default ASICs, sysfs setup, family flag selection, NBIO/HDP/DF/SMUIO/LSDMA function table selection, and ordered IP block registration.
- `amdgpu_discovery_fini(struct amdgpu_device *adev)` tears down discovery sysfs and frees `adev->discovery.bin`.
- `amdgpu_discovery_dump(struct amdgpu_device *adev, struct drm_printer *p)` serializes the sysfs discovery object tree into a DRM printer for devcoredump/debugging.
- `amdgpu_discovery_get_nps_info(...)` returns NPS memory partition type and ranges, optionally refreshing from VRAM instead of using the cached discovery binary.
- `amdgpu_discovery_init()` allocates and loads `adev->discovery.bin`, checks the binary signature, validates binary checksum, and validates key tables including IP discovery, GC, harvest, VCN, and MALL.
- `amdgpu_discovery_reg_base_init()` parses the IP discovery table, converts base-address endianness in place, fills `adev->reg_offset[hw_ip][instance]`, records IP versions, and counts/masks VCN, JPEG, SDMA, VPE, UMC, and GC/XCC instances.
- `amdgpu_discovery_harvest_ip()`, `amdgpu_discovery_read_harvest_bit_per_ip()`, and `amdgpu_discovery_read_from_harvest_table()` apply disabled-IP information to VCN/JPEG instance masks, UMC active mask, GC XCC mask, SDMA mask, DMU harvest mask, and optional ISP state.
- `amdgpu_discovery_get_gfx_info()`, `amdgpu_discovery_get_mall_info()`, and `amdgpu_discovery_get_vcn_info()` parse auxiliary tables into `adev->gfx.config`, `adev->gfx.cu_info`, `adev->gmc.mall_size`, and VCN codec disable masks.
- Sysfs helper structures `ip_discovery_top`, `ip_die_entry`, `ip_hw_id`, and `ip_hw_instance` model `/sys/.../ip_discovery/die/<die>/<hw_id>/<instance>/` with read-only attributes such as `hw_id`, `major`, `minor`, `revision`, `harvest`, `num_base_addresses`, and `base_addr`.
- `amdgpu_discovery_set_*_ip_blocks()` functions map discovered IP versions to concrete implementation descriptors such as `gmc_v11_0_ip_block`, `gfx_v12_0_ip_block`, `sdma_v7_0_ip_block`, `dm_ip_block`, `mes_v12_1_ip_block`, and media/ISP/VPE blocks.

## Control flow

The dynamic path starts in `amdgpu_discovery_set_ip_blocks()`. For modern/default ASICs it calls `amdgpu_discovery_reg_base_init()`, which calls `amdgpu_discovery_init()` before parsing. `amdgpu_discovery_init()` obtains TMR location and size from registers, SR-IOV critical region data, PSP scratch registers, or ACPI fallback, allocates the discovery buffer, chooses a firmware filename when required, otherwise reads from VRAM or system memory, verifies signature and checksums, and validates supported tables.

After binary load, `amdgpu_discovery_reg_base_init()` walks dies and IP entries. For every valid IP instance it records instance masks, normalizes 32-bit and 64-bit base addresses, updates the register-base array, and records full IP versions including variant/subrevision when the table version supports them. Harvest handling then removes disabled instances from the masks. Auxiliary info tables enrich GFX, MALL, VCN, and NPS state.

`amdgpu_discovery_set_ip_blocks()` then initializes SOC-specific config for special families, creates the sysfs discovery tree, classifies the ASIC family and APU flags from GC version, selects function tables for NBIO/HDP/DF/SMUIO/LSDMA, and adds IP blocks in dependency order: common, GMC, PSP/IH ordering adjusted for SR-IOV, SMU depending on firmware load path, display, GC, SDMA, RAS, optional late SMU, media, MES, VPE, UMSCH-MM, and ISP.

Legacy ASIC cases such as VEGA10, VEGA12, RAVEN, VEGA20, ARCTURUS, ALDEBARAN, and some CYAN_SKILLFISH paths bypass full dynamic parsing for functional setup, use hard-coded register base and IP version assignments, and treat discovery binary initialization as non-fatal sysfs/debug support.

## State and persistence behavior

Persistent driver state is stored in `adev->discovery`, `adev->ip_versions`, `adev->reg_offset`, `adev->gfx`, `adev->gmc`, `adev->umc`, `adev->vcn`, `adev->jpeg`, `adev->sdma`, `adev->vpe`, `adev->harvest_ip_mask`, `adev->family`, `adev->flags`, and per-subsystem function-table pointers. The discovery binary remains cached in `adev->discovery.bin` until `amdgpu_discovery_fini()`.

The sysfs state is dynamically allocated and rooted at `adev->discovery.ip_top`; it is reference-counted through kobjects/ksets and explicitly traversed/free-walked by `amdgpu_discovery_sysfs_fini()`. Debugfs blob state references the same discovery binary buffer through `adev->discovery.debugfs_blob`.

The file mutates discovery table base-address fields in place after endian conversion. That makes later sysfs base-address exposure and `adev->reg_offset` use host-order lower 32-bit base values rather than raw firmware encoding.

## Dependencies and integration points

This file depends on AMD discovery table layouts from `discovery.h`, AMDGPU core device state from `amdgpu.h`, IP version constants, register helpers such as `RREG32`, VRAM access via `amdgpu_device_vram_access()`, firmware loading via `firmware_request_nowarn()`, ACPI TMR fallback, SR-IOV helpers, RAS boot status query, and a large set of IP block descriptor headers.

It integrates with sysfs/kobject infrastructure, DRM logging and devcoredump printers, debugfs blob wrappers, GMC/UMC/GFX/VCN/JPEG/SDMA/MES/VPE/ISP state, display manager selection, firmware loading policy, and the AMDGPU IP block initialization sequence. Failures here often prevent the driver from selecting later hardware implementations.

## Risks and edge cases

- Discovery binary validation is critical. Bad offsets, checksums, unsupported binary header versions, or malformed table sizes can stop initialization or hide optional tables.
- Some legacy paths ignore discovery initialization failures because they are only needed for sysfs; modern/default paths return errors and can block device bring-up.
- SR-IOV changes TMR source, display path, and PSP/IH ordering. Regressions can affect VF boot even if bare metal still works.
- The parser relies on table-provided counts and flexible-size IP entries. Validation catches out-of-range `instance_number` and `hw_id`, but corruption around offsets/counts remains a high-risk area.
- Harvest data controls instance masks and can disable complete media/IP blocks. Board-specific quirks such as Navy Flounder VCN harvesting are easy to break when adding new ASIC IDs.
- IP version switch tables are large and must be kept synchronized with new block implementations. Missing one case usually returns `-EINVAL` with "Failed to add ..." logs.
- Sysfs object lifetime uses embedded kobjects and manual list traversal under kset list locks. Leaks or double puts would show up during device removal or failed sysfs initialization.

## Test signals

Useful validation signals include boot logs containing discovery source and checksum errors, successful AMDGPU probe on each covered ASIC family, `/sys/.../ip_discovery` hierarchy correctness, devcoredump `HW IP Discovery` output, `dmesg` errors from each `Failed to add ... ip block` branch, SR-IOV VF initialization, RAS boot status fallback on discovery v4 failures, and graphics/media/SDMA/MES smoke tests that indirectly prove IP versions, register bases, and masks were populated correctly.
