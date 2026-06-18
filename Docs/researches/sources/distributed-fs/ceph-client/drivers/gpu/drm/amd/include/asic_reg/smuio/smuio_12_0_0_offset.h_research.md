# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_12_0_0_offset.h

## Purpose

`smuio_12_0_0_offset.h` is a generated offset header for the two SMUIO/PWR registers needed by SMU 12 GFXOFF power-state handling. It names the SMUIO GFX miscellaneous control register and a PWR miscellaneous control/status register with the base indexes required by SOC15 access helpers.

## Important APIs, Types, and Macros

The header exports macro constants only:

- `mmSMUIO_GFX_MISC_CNTL` at offset `0x00c8`, base index `0`.
- `mmPWR_MISC_CNTL_STATUS` at offset `0x0183`, base index `1`.

There are no functions, data types, or variables.

## Control Flow

No control flow exists in the header. Its primary direct consumer, `pm/swsmu/smu12/smu_v12_0.c`, uses `mmSMUIO_GFX_MISC_CNTL` in `smu_v12_0_get_gfxoff_status()`:

- Read `RREG32_SOC15(SMUIO, 0, mmSMUIO_GFX_MISC_CNTL)`.
- Mask with `SMUIO_GFX_MISC_CNTL__PWR_GFXOFF_STATUS_MASK`.
- Shift by `SMUIO_GFX_MISC_CNTL__PWR_GFXOFF_STATUS__SHIFT`.
- Return the two-bit GFXOFF status value where nearby comments document `0 = GFXOFF`, `1 = transition out`, `2 = not in GFXOFF`, and `3 = transition in`.

The `mmPWR_MISC_CNTL_STATUS` macro is explicitly undefined/redefined handling in the same source area because similarly named PWR-block headers exist; its base index matters when the register is accessed through SOC15 helpers.

## State and Persistence Behavior

The header has no state. It identifies hardware registers:

- `SMUIO_GFX_MISC_CNTL` exposes current GFXOFF status in SMUIO.
- `PWR_MISC_CNTL_STATUS` exposes PWR-side GFX RLC CGPG enable and GFXOFF status fields when paired with the mask header.

The values are live hardware status/control fields, not persisted by the driver.

## Dependencies

This header is meaningful with `smuio_12_0_0_sh_mask.h` and SOC15 register access macros. Its include guard is `_smuio_12_0_0_OFFSET_HEADER`. Runtime code depends on `struct smu_context`, `struct amdgpu_device`, `RREG32_SOC15`, and SMU message paths that allow or disallow GFXOFF.

## Integration Points

Direct include:

- `drivers/gpu/drm/amd/pm/swsmu/smu12/smu_v12_0.c`

Functional integration:

- `smu_v12_0_get_gfxoff_status()` reads `mmSMUIO_GFX_MISC_CNTL`.
- `smu_v12_0_gfx_off_control()` sends SMU messages to allow/disallow GFXOFF, making accurate status reads from this register important for power-management diagnostics and policy decisions.

## Risks and Edge Cases

- `mmPWR_MISC_CNTL_STATUS_BASE_IDX` is `1`, unlike the related PWR 10.0 offset header where similar names may use another base. Wrong include ordering or macro collision can target the wrong instance.
- The same field names exist in SMUIO and PWR-flavored headers. Consumers must pair offsets and masks from the same intended IP/register block.
- GFXOFF status is a moving hardware state; tests must tolerate transitional values `1` and `3`.

## Test Signals

- Build `smu_v12_0.c` with both offset and mask headers included.
- Runtime GFXOFF allow/disallow tests should observe plausible transitions through `smu_v12_0_get_gfxoff_status()`.
- Power-management debug output or tracepoints that sample GFXOFF can reveal incorrect offsets by returning stuck or impossible status values.
- Header-regeneration diffs should confirm offset `0x00c8`/base `0` and offset `0x0183`/base `1` remain aligned with hardware documentation.
