# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-pllv3.c

## Purpose
Implements multiple i.MX PLLv3 variants: generic USB-style 20x/22x PLLs, SYS PLLs, audio/video fractional PLLs, VF610 fractional PLLs, ENET fixed-rate PLLs, and i.MX7-specific power/offset variants.

## Important APIs, Types, And Functions
`struct clk_pllv3` stores base address, power bit semantics, divider mask/shift, reference clock, and numerator/denominator offsets. The file provides variant-specific ops: `clk_pllv3_ops`, `clk_pllv3_sys_ops`, `clk_pllv3_av_ops`, `clk_pllv3_vf610_ops`, and `clk_pllv3_enet_ops`. Factory `imx_clk_hw_pllv3()` selects ops and offsets from `enum imx_pllv3_type`.

## Control Flow
Prepare toggles the configured power bit and waits for lock if powered. Generic set-rate selects 20x or 22x parent multiplier. SYS set-rate clamps to parent*54/2..parent*108/2. AV and DDR variants compute integer and fractional numerator/denominator fields. VF610 converts between 20/22 integer plus 30-bit fraction. ENET returns a fixed reference rate.

## State And Persistence Behavior
All clock settings are in PLL hardware registers. The driver stores no saved PM state. Variant data is encoded in each clock object at registration.

## Dependencies And Integration Points
Used by i.MX6/i.MX7/i.MXRT clock trees. Depends on common clock framework, MMIO, polling, delay helpers, and exported factory symbol.

## Risks
Power-bit polarity differs by variant (`powerup_set`). Fractional math must respect denominator limits. ENET PLL recalc ignores parent and returns fixed board-specific rates. Lock polling is required after set-rate and prepare.

## Test Signals
Variant-specific rate tests for SYS/USB/AV/VF610/ENET, lock timeout injection, i.MX7 ENET/DDR power-bit behavior, and consumers such as USB, video, audio, ENET, and system PLL roots.
