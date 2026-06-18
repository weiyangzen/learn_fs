# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/bxt_dpio_phy_regs.h

Purpose: defines Broxton DPIO PHY MMIO register addresses and bitfields for i915 display PHY and PLL programming.

Important APIs/types: macros map PHY base addresses, channel/lane addressing, port PLL enable/status, PLL divisor/fraction/gain/lock fields, common lane registers, reference calibration registers, PCS lane/group registers, and TX lane/group swing/de-emphasis/DCC/latency fields.

Control flow: no executable control flow. Display PHY/PLL code includes this header to calculate register addresses for specific PHY, channel, port, and lane operations.

State and persistence: hardware state lives in the BXT PHY registers addressed here. The header itself stores no state.

Dependencies and integration points: depends on `intel_display_reg_defs.h` for `_MMIO`, `_MMIO_PORT`, `_PICK_EVEN_2RANGES`, `_PIPE`, `REG_BIT`, `REG_GENMASK`, and `REG_FIELD_PREP`. Used by Broxton display PHY and DPLL management code.

Risks: address selection is highly platform-specific. PHY0/PHY1/PHY2 base mapping and channel/lane offset math must match silicon. Misprogramming PLL or TX fields can prevent display link lock or damage signal integrity.

Test signals: BXT PHY power good, PLL lock, GRC calibration, DP/HDMI link bring-up, lane swing/de-emphasis tuning, and register readback on Broxton hardware.
