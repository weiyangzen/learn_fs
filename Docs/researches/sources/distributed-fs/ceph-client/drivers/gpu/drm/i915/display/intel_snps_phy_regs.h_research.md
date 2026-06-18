# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_snps_phy_regs.h

## Purpose
`intel_snps_phy_regs.h` defines MMIO address helpers and bitfield masks for Synopsys PHY MPLLB, reference control, PSR lane power requests, and per-lane TX equalization registers.

## Important APIs, Types, And Functions
- Base address helpers: `_SNPS_PHY_A_BASE`, `_SNPS_PHY_B_BASE`, `_SNPS_PHY(phy)`, `_SNPS2(phy, reg)`, `_MMIO_SNPS(phy, reg)`, and `_MMIO_SNPS_LN(ln, phy, reg)`.
- MPLLB registers and fields: `SNPS_PHY_MPLLB_CP`, `SNPS_PHY_MPLLB_DIV`, `SNPS_PHY_MPLLB_FRACN1`, `SNPS_PHY_MPLLB_FRACN2`, `SNPS_PHY_MPLLB_SSCEN`, `SNPS_PHY_MPLLB_SSCSTEP`, `SNPS_PHY_MPLLB_DIV2`, and fields for force enable, divider clocks, V2I, VCO bucket, PMIX, DP2 mode, word div2, TX clock divider, reference divider, multiplier, HDMI divider, fractional-N, and SSC.
- Reference control: `SNPS_PHY_REF_CONTROL` and `SNPS_PHY_REF_CONTROL_REF_RANGE`.
- PSR power request: `SNPS_PHY_TX_REQ` and `SNPS_PHY_TX_REQ_LN_DIS_PWR_STATE_PSR`.
- Per-lane TX EQ: `SNPS_PHY_TX_EQ(ln, phy)` with main, post-cursor, and pre-cursor fields.

## Control Flow
The header has no executable control flow. Its macros convert PHY and lane indices into MMIO registers and provide masks used with `REG_FIELD_PREP()`, `REG_FIELD_GET()`, and read-modify-write helpers in the PHY implementation.

## State And Persistence
The file defines persistent hardware register locations and bit layouts but owns no software state. Values written through these macros persist in display PHY registers until changed by software, firmware, or reset.

## Dependencies And Integration Points
It depends on `intel_display_reg_defs.h` for MMIO and register field macros. It is consumed by `intel_snps_phy.c`, `intel_snps_hdmi_pll.c`, and any i915 code packing or reading Synopsys PHY PLL/equalization state.

## Risks And Edge Cases
Incorrect base address arithmetic or field masks directly corrupts MMIO programming. Lane addressing assumes a 0x10 stride. Some fields are read for verification but firmware-controlled, so software must not assume ownership of every bit. The macros currently cover PHY A/B base mapping through `_PHY()` and need review if future platforms expose more SNPS PHY instances or different offsets.

## Test Signals
Signals include register read/write traces during MPLLB enable/disable, field round-trip checks through `REG_FIELD_GET()`, successful PLL lock, correct TX EQ values per lane, PSR request field transitions, and absence of `intel_mpllb_state_verify()` mismatch warnings.
