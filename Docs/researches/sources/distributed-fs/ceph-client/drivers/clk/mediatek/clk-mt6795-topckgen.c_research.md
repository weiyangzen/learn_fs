# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt6795-topckgen.c

## Purpose

This MT6795 topckgen driver is the central non-PLL clock tree provider. It declares fixed clocks, fixed-factor PLL derivatives, top muxes, and audio mux/divider composites for bus, memory, multimedia, MFG, camera, UART, SPI, USB, MSDC, audio, PMIC, SCP, MJC, DPI, IRDA, CCI400, and display-related paths.

## Important APIs, types, and functions

Important objects include many `*_parents` arrays, `fixed_clks[]`, `top_divs[]`, `top_muxes[]`, `top_aud_divs[]`, and `topck_desc`. The custom macros `TOP_MUX_GATE_NOSR()` and `TOP_MUX_GATE()` wrap `MUX_GATE_CLR_SET_UPD_FLAGS()` to express clear/set/update muxes. The platform driver uses `mtk_clk_simple_probe()` and `mtk_clk_simple_remove()` for `"mediatek,mt6795-topckgen"`.

## Control flow, state, and persistence

Generic simple probe consumes `topck_desc`: it registers fixed clocks, fixed factors, muxes under `mt6795_top_clk_lock`, audio composites, and the OF provider. Muxes use `CLK_CFG_*` registers from `0x40` through `0xb0`; audio dividers use `0x120` through `0x12c`. Critical flags are applied to AXI, memory, DDRPHYCFG, and CCI400-related paths. Hardware state persists until reset.

## Dependencies and integration points

Dependencies are `clk-gate.h`, `clk-mtk.h`, `clk-mux.h`, and MT6795 bindings. It consumes PLL names from apmixedsys and provides parent clocks to infracfg, pericfg, MMSYS, MFG, VDEC, VENC, audio, display, USB, storage, and camera consumers. Dummy-rate fixed clocks represent external or product-specific rates that are intentionally not modeled.

## Risks and test signals

Risks include parent-order mistakes, missing `CLK_SET_RATE_PARENT` where rate propagation is required, incorrect critical flags, and divider/mux register overlap. Test with full boot, clock summary parent/rate validation, display DPI/DSI, audio I2S, MMC, USB, camera/display pipelines, and idle clock disabling.
