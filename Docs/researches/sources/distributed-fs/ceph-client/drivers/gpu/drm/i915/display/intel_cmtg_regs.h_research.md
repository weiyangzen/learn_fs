# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_cmtg_regs.h

## Purpose

`intel_cmtg_regs.h` defines the small set of MMIO registers and bitfields needed to identify and disable Common Primary Timing Generator state.

## Important APIs, Types, And Functions

The header defines `CMTG_CLK_SEL` and its A/B masks plus disabled encodings: `CMTG_CLK_SEL_A_MASK`, `CMTG_CLK_SEL_A_DISABLED`, `CMTG_CLK_SEL_B_MASK`, and `CMTG_CLK_SEL_B_DISABLED`. It also defines `TRANS_CMTG_CTL_A`, `TRANS_CMTG_CTL_B`, and the `CMTG_ENABLE` bit.

## Control Flow And Integration

`intel_cmtg.c` uses these definitions when clearing CMTG enable bits and resetting clock selection after disabling inherited CMTG state. Secondary-transcoder mode is defined in the broader display register header, so this file stays focused on CMTG-specific registers.

## State And Persistence

These are hardware register definitions only. The associated hardware state persists in the display engine until explicitly changed or reset. There is no software state in the header.

## Dependencies, Risks, And Test Signals

The header depends on `intel_display_reg_defs.h` for `_MMIO`, `REG_BIT`, `REG_GENMASK`, and `REG_FIELD_PREP`. Risks are incorrect masks or disabled encodings, especially as CMTG B and clock selection are platform-version dependent in the implementation. Tests should inspect MMIO writes during sanitize and compare the final CMTG clock selection and enable bits with expected disabled values.
