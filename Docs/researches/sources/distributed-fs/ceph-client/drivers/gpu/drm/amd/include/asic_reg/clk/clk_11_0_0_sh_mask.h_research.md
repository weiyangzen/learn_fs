<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_11_0_0_sh_mask.h -->
# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_11_0_0_sh_mask.h

## Purpose

`clk_11_0_0_sh_mask.h` defines the field positions and masks for the two registers named by `clk_11_0_0_offset.h`. It is generated hardware metadata for the `clk_clk3_0_SmuClkDec` block and supports safe decoding of CLK3 PLL request fields and CLK2 DFS divider control.

## Important APIs, Types, And Macros

There are no runtime APIs or types. The macro surface is:

- `CLK3_0_CLK3_CLK_PLL_REQ__FbMult_int__SHIFT`/`MASK`: 9-bit integer PLL feedback multiplier at bit 0.
- `CLK3_0_CLK3_CLK_PLL_REQ__PllSpineDiv__SHIFT`/`MASK`: 4-bit spine-divider field at bit 12.
- `CLK3_0_CLK3_CLK_PLL_REQ__FbMult_frac__SHIFT`/`MASK`: 16-bit fractional PLL feedback multiplier at bit 16.
- `CLK3_0_CLK3_CLK2_DFS_CNTL__CLK2_DIVIDER__SHIFT`/`MASK`: 7-bit CLK2 divider field at bit 0.

The field names match AMDGPU's `REG_GET`/`REG_SET` macro expectations.

## Control Flow

The only direct flow is the include guard. Consumer flow is generally read-only for diagnostics and clock calculation: read the PLL request register, extract multiplier fields, optionally combine them with reference-clock information, and read the DFS divider to determine the final clock. If a path programs the divider, it should use the mask to update only the divider field.

## State And Persistence Behavior

The file itself has no mutable state. It describes persistent hardware configuration fields. PLL multiplier and spine divider values influence the source clock. The DFS divider influences the clock output derived from that source. Changes made through these fields affect hardware behavior until changed by driver, firmware, power management, or reset.

## Dependencies

This header depends on the matching offsets, AMDGPU field-helper macro conventions, and unsigned 32-bit register access. Its values are ASIC-specific and must be synchronized with generated CLK 11.0.0 hardware definitions.

## Integration Points

Display clock-manager internal headers contain table macros for `CLK3_CLK_PLL_REQ` and `CLK3_CLK2_DFS_CNTL` and field macros for `FbMult_int`/`FbMult_frac`. Those table entries are consumed by clock-manager code when calculating display-related clock rates or reporting hardware clock state.

## Risks And Edge Cases

The `CLK2_DIVIDER` field is 7 bits wide, which differs from the 3-bit bypass selectors and 4-bit deep-sleep dividers found in other CLK generations. Consumers should not share field widths across generations by assumption. PLL calculations can be wrong if `PllSpineDiv` is ignored on hardware that requires it. Mask literals use `L` suffixes, so unsigned storage is preferred.

## Test Signals

Test signals include compile coverage for clock-manager macros, generated-header comparison, and readback tests that validate PLL multiplier and divider-derived clock frequencies. Edge testing should cover divider boundary values and confirm that field extraction does not include adjacent bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_11_0_0_sh_mask.h -->
