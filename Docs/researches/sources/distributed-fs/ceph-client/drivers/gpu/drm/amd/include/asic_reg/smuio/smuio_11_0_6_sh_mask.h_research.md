# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/smuio/smuio_11_0_6_sh_mask.h

## Purpose

`smuio_11_0_6_sh_mask.h` is the SMUIO 11.0.6 generated shift/mask header for the ROM clock-gating and ROM indexed access registers named by `smuio_11_0_6_offset.h`. It provides the field constants needed to safely update `CGTT_ROM_CLK_CTRL0` and interpret `ROM_INDEX`/`ROM_DATA`.

## Important APIs, Types, and Macros

The header exports preprocessor macros only:

- `CGTT_ROM_CLK_CTRL0__ON_DELAY__SHIFT` and `ON_DELAY_MASK` cover the low 4-bit on-delay field.
- `CGTT_ROM_CLK_CTRL0__OFF_HYSTERESIS__SHIFT` and `OFF_HYSTERESIS_MASK` cover bits 4..11.
- `CGTT_ROM_CLK_CTRL0__SOFT_OVERRIDE1__SHIFT` / `SOFT_OVERRIDE1_MASK` and `SOFT_OVERRIDE0__SHIFT` / `SOFT_OVERRIDE0_MASK` cover bits 30 and 31. These are the fields AMDGPU toggles for ROM MGCG enable/disable.
- `ROM_INDEX__ROM_INDEX__SHIFT` and `ROM_INDEX__ROM_INDEX_MASK` define a 25-bit ROM index field (`0x01ffffff`).
- `ROM_DATA__ROM_DATA__SHIFT` and `ROM_DATA__ROM_DATA_MASK` expose the full 32-bit ROM data window.

There are no functions, types, or storage objects.

## Control Flow

The header contains no control flow. Runtime behavior is in `amdgpu/smuio_v11_0_6.c`:

- Read `mmCGTT_ROM_CLK_CTRL0`.
- If enabling and `AMD_CG_SUPPORT_ROM_MGCG` is set, clear both `SOFT_OVERRIDE` bits so hardware clock gating can operate.
- Otherwise set both override bits to force ROM clocking behavior.
- Write back only when the value differs.
- Report ROM MGCG support when `SOFT_OVERRIDE0` is clear.

The `ROM_INDEX` and `ROM_DATA` masks are available for indexed ROM access, although the helper currently exposes offsets rather than doing explicit field extraction in this file's direct consumer.

## State and Persistence Behavior

The macros have no state. They describe persistent hardware fields:

- `SOFT_OVERRIDE0/1` hold clock-gating override configuration until changed or reset.
- `ON_DELAY` and `OFF_HYSTERESIS` are timing fields for ROM clock-gating transitions.
- `ROM_INDEX` and `ROM_DATA` are transient ROM access fields.

## Dependencies

This header must be used with the 11.0.6 offset header so masks are applied to the correct register addresses. Runtime consumers depend on AMDGPU's SOC15 MMIO helpers and clock-gating flags. The include guard is `_smuio_11_0_6_SH_MASK_HEADER`.

## Integration Points

Direct include:

- `drivers/gpu/drm/amd/amdgpu/smuio_v11_0_6.c`

The constants integrate into `smuio_v11_0_6_funcs`, where ROM offset discovery and ROM MGCG state/control are exposed to the wider AMDGPU device layer.

## Risks and Edge Cases

- The `ROM_INDEX` mask is 25 bits in 11.0.6, unlike the 24-bit mask in some older SMUIO maps. Sharing ROM index manipulation code across versions without the right header can truncate or overrun the address field.
- Inverting the meaning of the soft override bits would flip clock-gating behavior. The current consumer treats cleared override bits as enabled MGCG and set bits as disabled/forced override.
- The APU skip in the consumer is important because `CGTT_ROM_CLK_CTRL0` is not available for APUs.

## Test Signals

- Compile `smuio_v11_0_6.c` to catch missing field macros.
- Exercise ROM clock-gating transitions and inspect `CGTT_ROM_CLK_CTRL0` before and after enable/disable.
- Verify `get_clock_gating_state()` reports `AMD_CG_SUPPORT_ROM_MGCG` when `SOFT_OVERRIDE0` is clear.
- VBIOS ROM-read testing provides indirect coverage for the ROM index/data field sizing.
