<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_10_0_2_sh_mask.h -->
# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_10_0_2_sh_mask.h

## Purpose

`clk_10_0_2_sh_mask.h` is the generated field-layout companion for `clk_10_0_2_offset.h`. It defines `*_SHIFT` and `*_MASK` macros for CLK1 PLL request, bypass control, deep-sleep control, and current-count registers in the `clk_clk1_0_SmuClkDec` block. It contains no executable logic; its purpose is to let AMDGPU code compose and decode 32-bit register values without embedding bit positions at call sites.

## Important APIs, Types, And Macros

There are no functions or types. The public surface is the macro convention:

- `CLK1_CLK_PLL_REQ__FbMult_int`, `PllSpineDiv`, and `FbMult_frac` fields define a 9-bit integer feedback multiplier, 4-bit spine divider at bit 12, and 16-bit fractional feedback multiplier at bit 16.
- `CLK1_CLK0_BYPASS_CNTL` through `CLK1_CLK3_BYPASS_CNTL` each provide `CLKx_BYPASS_SEL` in bits 0..2 and `CLKx_BYPASS_DIV` in bits 16..19.
- `CLK1_CLK3_DS_CNTL__CLK3_DS_DIV_ID` provides a 3-bit deep-sleep divider ID.
- `CLK1_CLK3_ALLOW_DS__CLK3_ALLOW_DS` exposes the deep-sleep allow bit at bit 0.
- `CLK1_CLK0_CURRENT_CNT` through `CLK1_CLK3_CURRENT_CNT` expose a full 32-bit `CURRENT_COUNT` field.

Consumers usually use these macros through AMDGPU field helpers such as `REG_GET`, `REG_SET`, or `get_reg_field_value`, or manually with `mask` and `shift` expressions.

## Control Flow

The header's only control flow is the `_clk_10_0_2_SH_MASK_HEADER` include guard. Runtime flow is entirely in consumers. A common read path is: read `mmCLK1_CLK_PLL_REQ`, extract `FbMult_int` and `FbMult_frac`, and derive a reference or display clock rate. Bypass reporting reads a `CLK1_CLKx_BYPASS_CNTL` register and extracts `CLKx_BYPASS_SEL`. Deep-sleep reporting reads `CLK1_CLK3_ALLOW_DS` or `CLK1_CLK3_DS_CNTL` and interprets the allow and divider fields.

## State And Persistence Behavior

The macros themselves are compile-time constants. They describe state stored in hardware registers. PLL fields and bypass/divider fields are configuration state; current-count fields are hardware measurement/readback state; the deep-sleep allow bit controls low-power behavior until hardware reset or subsequent driver/firmware programming. The file does not cache, allocate, or persist anything in software.

## Dependencies

This file depends on the matching CLK 10.0.2 offset header for register addresses and on AMDGPU register-field helpers that expect the `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` naming convention. It also depends on correct ASIC dispatch: the bit layout is only valid for hardware matching this generated CLK version.

## Integration Points

Display clock-manager code uses equivalent PLL request fields in multiple DCN generations to compute or report clock values. Local integration searches show clock-manager headers and C files use current-count, bypass-control, and deep-sleep fields to populate debug structures and logs. This header is therefore part of the low-level contract between generated ASIC register metadata and display clock observability/power management.

## Risks And Edge Cases

Incorrect masks silently mis-decode clocks or write adjacent fields. PLL fields are especially sensitive because frequency calculations depend on the exact fractional and integer multiplier widths. Bypass registers use repeated field names with only the clock number changing, which is a copy/paste risk in register tables. `CURRENT_COUNT_MASK` uses `0xFFFFFFFFL`; consumers should store values in unsigned fixed-width types to avoid signed-long surprises on 32-bit builds. For writable registers, callers should preserve reserved bits with read-modify-write because this header only describes known fields.

## Test Signals

Validation should build the display driver paths that include this header and compare generated masks against AMD's register database. Runtime checks include reading PLL fields and verifying derived frequencies, reading current-count registers under known clock states, toggling or observing deep-sleep allowance during display idle transitions, and checking bypass-source debug output for each CLK0..CLK3 register.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_10_0_2_sh_mask.h -->
