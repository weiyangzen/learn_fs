# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_12_0_0_sh_mask.h

## Purpose

`smuio_12_0_0_sh_mask.h` is the generated bitfield companion for the SMUIO 12.0.0 GFXOFF-related registers. It defines masks and shifts used to extract GFXOFF status and, for the PWR status register, the GFX RLC CGPG enable bit.

## Important APIs, Types, and Macros

The header exports only macros:

- `SMUIO_GFX_MISC_CNTL__PWR_GFXOFF_STATUS_MASK` (`0x00000006`) and `SMUIO_GFX_MISC_CNTL__PWR_GFXOFF_STATUS__SHIFT` (`1`) extract the two-bit GFXOFF state from `mmSMUIO_GFX_MISC_CNTL`.
- `PWR_MISC_CNTL_STATUS__PWR_GFX_RLC_CGPG_EN__SHIFT` / `_MASK` cover bit 0 of `mmPWR_MISC_CNTL_STATUS`.
- `PWR_MISC_CNTL_STATUS__PWR_GFXOFF_STATUS__SHIFT` / `_MASK` cover bits 1..2 of the PWR-side status register.

No functions, structs, enums, or variables are declared.

## Control Flow

This header contains no logic. In direct consumer code:

- `smu_v12_0_get_gfxoff_status()` reads `mmSMUIO_GFX_MISC_CNTL`, masks with `SMUIO_GFX_MISC_CNTL__PWR_GFXOFF_STATUS_MASK`, shifts by `SMUIO_GFX_MISC_CNTL__PWR_GFXOFF_STATUS__SHIFT`, and returns a status enum-like integer.
- GFXOFF control itself is performed by SMU messages (`AllowGfxOff` and `DisallowGfxOff`); this header supplies status extraction constants used to observe the result.

## State and Persistence Behavior

The macros are stateless. They describe live hardware fields:

- `PWR_GFXOFF_STATUS` is volatile power-state status and can transition while being sampled.
- `PWR_GFX_RLC_CGPG_EN` is a control/status bit for graphics RLC coarse-grain power gating.

The driver does not persist values from this header. State is stored in hardware and firmware-controlled registers.

## Dependencies

The header should be used with `smuio_12_0_0_offset.h`. The include guard is `_smuio_12_0_0_SH_MASK_HEADER`. Runtime usage depends on AMDGPU PM/SMU code, SOC15 MMIO helpers, and SMU firmware responses to GFXOFF allow/disallow messages.

## Integration Points

Direct include:

- `drivers/gpu/drm/amd/pm/swsmu/smu12/smu_v12_0.c`

Related cross-version integration:

- Similar `PWR_GFXOFF_STATUS` fields exist in SMU10, SMU11, SMU13, and SMUIO 15 headers and board-specific PPT files. This header is the SMUIO 12.0.0 variant used by the SMU12 path.

## Risks and Edge Cases

- Because both SMUIO and PWR registers expose a `PWR_GFXOFF_STATUS` field, mixing the wrong offset and mask set can return plausible but incorrect values.
- Status values are two-bit state codes; callers should not treat any nonzero value as a simple boolean.
- The mask names overlap with other generated headers, so include ordering and `#undef` handling in consumers are part of the integration contract.

## Test Signals

- Compile-time validation from `smu_v12_0.c` confirms the mask names are available.
- Runtime GFXOFF tests should check all documented status codes are interpreted consistently: `0`, `1`, `2`, and `3`.
- Power-management suspend/resume and idle tests can catch stale status extraction if the mask or shift changes.
- Static comparison with generated register specs should verify `0x00000006` remains the correct status mask for both exposed registers.
