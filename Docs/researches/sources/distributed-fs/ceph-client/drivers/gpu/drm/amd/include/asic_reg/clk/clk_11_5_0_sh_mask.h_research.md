<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_11_5_0_sh_mask.h -->
# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_11_5_0_sh_mask.h

## Purpose

`clk_11_5_0_sh_mask.h` is the generated field-mask companion for `clk_11_5_0_offset.h`. It describes the bit layout of CLK1 PLL request, bypass-control, deep-sleep-control, and current-count registers in the CLK 11.5.0 generation. The header enables field extraction and read-modify-write operations in AMDGPU display clock code without hard-coded bit positions.

## Important APIs, Types, And Macros

There are no functions, structs, or enums. The field macros cover:

- `CLK1_0_CLK1_CLK_PLL_REQ__FbMult_int` at bits 0..8 and `FbMult_frac` at bits 16..31. Unlike CLK 10.0.2 and CLK 11.0.x PLL masks, this file does not define a `PllSpineDiv` field.
- `CLK1_0_CLK1_CLK0_BYPASS_CNTL` through `CLK1_0_CLK1_CLK3_BYPASS_CNTL`, each with a 3-bit `CLKx_BYPASS_SEL` and 4-bit `CLKx_BYPASS_DIV`.
- `CLK1_0_CLK1_CLK3_DS_CNTL__CLK3_DS_DIV_ID`, a 3-bit deep-sleep divider ID.
- `CLK1_0_CLK1_CLK3_ALLOW_DS__CLK3_ALLOW_DS`, a 1-bit deep-sleep allow flag.
- `CLK1_0_CLK1_CLK0_CURRENT_CNT` through `CLK1_0_CLK1_CLK3_CURRENT_CNT`, each exposing all 32 bits as `CURRENT_COUNT`.

## Control Flow

The header's only flow is its include guard. Runtime consumers read register values and pass them through field helpers. Typical paths extract PLL feedback values for frequency calculations, decode bypass selectors for diagnostics, read current-count registers for current clock rates, and inspect or program CLK3 deep-sleep bits.

## State And Persistence Behavior

The macros describe hardware state but do not store software state. PLL feedback and bypass/divider settings are persistent hardware configuration. Current-count fields are hardware readback. Deep-sleep allow and divider fields influence low-power entry and remain active until changed by driver, firmware, power transition, or reset.

## Dependencies

This file depends on matching offsets, AMDGPU field-helper conventions, and correct ASIC selection. It also depends on consumers noticing the missing `PllSpineDiv` field relative to nearby generations; generic PLL code must not unconditionally request that field for CLK 11.5.0.

## Integration Points

Display clock-manager code uses these field definitions through generated `CLK_SF`/`REG_GET` tables and clock debugging paths. The PLL fields feed clock derivation, bypass fields feed source reporting, current-count fields feed live frequency debug, and deep-sleep fields feed DCFCLK-style low-power state reporting.

## Risks And Edge Cases

The missing `PllSpineDiv` is the most important generation-specific difference. Code that assumes a spine divider exists because it is present in CLK 10.0.2 or CLK 11.0.x will fail to build or calculate incorrectly. Full-width current-count masks should be handled with unsigned values. Repeated bypass macros can be miswired across CLK0..CLK3 in register tables. As with all generated hardware metadata, manual edits can introduce silent hardware misprogramming.

## Test Signals

Validation should include build coverage of clock-manager tables for CLK 11.5.0, generated-header comparison, and runtime clock debug checks. Specific tests should confirm PLL frequency derivation without a spine-divider field, bypass decoding for all four clocks, and deep-sleep behavior for CLK3 during display idle transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_11_5_0_sh_mask.h -->
