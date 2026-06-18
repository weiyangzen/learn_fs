# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_casf_regs.h

## Purpose

`intel_casf_regs.h` defines the per-pipe MMIO addresses and bitfields used to program the Content Adaptive Sharpness Filter control register and sharpness LUT.

## Important APIs, Types, And Functions

The header defines `SHARPNESS_CTL(pipe)` from `_SHARPNESS_CTL_A/B`, with `FILTER_EN`, `FILTER_STRENGTH_MASK`, `FILTER_STRENGTH(x)`, `FILTER_SIZE_MASK`, and the three encoded filter sizes `SHARPNESS_FILTER_SIZE_3X3`, `SHARPNESS_FILTER_SIZE_5X5`, and `SHARPNESS_FILTER_SIZE_7X7`. It also defines `SHRPLUT_DATA(pipe)` and `SHRPLUT_INDEX(pipe)` with `INDEX_AUTO_INCR`, `INDEX_VALUE_MASK`, and `INDEX_VALUE(x)`.

## Control Flow And Integration

`intel_casf.c` uses `SHRPLUT_INDEX` with auto-increment to load the LUT, writes `SHRPLUT_DATA` entries in sequence, and writes `SHARPNESS_CTL` to enable/disable CASF and update strength/filter size. Readout uses the masks in this header to parse hardware state.

## State And Persistence

These definitions map to hardware state only. The control register persists enable, strength, and filter-size fields per pipe; the LUT registers are programmed by index/data access. The header itself contains no software state.

## Dependencies, Risks, And Test Signals

The only include is `intel_display_reg_defs.h`, which supplies `_MMIO_PIPE`, `REG_BIT`, `REG_GENMASK`, and `REG_FIELD_PREP`. Risks are register-address or bitfield drift against BSpec and the limited A/B base-address pattern if future hardware exposes more pipes differently. Tests should validate MMIO traces when enabling CASF, strength field updates via `FILTER_STRENGTH_MASK`, readout parsing, and LUT auto-increment programming.
