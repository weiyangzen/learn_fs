# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3506.c

## Purpose

`clk-rk3506.c` provides the RK3506 CRU clock provider. It describes a modern Rockchip clock tree with GPLL, V0PLL, V1PLL, a multi-PLL ARM clock, matrix/fractional roots, audio/voice/ASRC clocks, storage/network/display/video/peripheral roots, PMU clocks, 32 kHz generation, reset initialization, restart handling, and a PVTPLL source initialization write.

The file supports both early OF initialization through `CLK_OF_DECLARE(rk3506_cru, "rockchip,rk3506-cru", rk3506_clk_init)` and built-in platform-driver probing through `clk_rk3506_driver`. The platform path simply calls the same init routine selected from match data.

## Important APIs, Types, And Functions

Important data:

- `PVTPLL_SRC_SEL_PVTPLL` is a hiword update value used after provider registration to select the PVTPLL source.
- `enum rk3506_plls` enumerates GPLL, V0PLL, and V1PLL.
- `rk3506_pll_rates` defines RK3328-style PLL rates.
- `rk3506_cpuclk_rates` defines ARM-clock parent rates and ACLK/PCLK divider writes.
- `rk3506_pll_clks` registers the three PLLs with `PLL(pll_rk3328, ...)`.
- `rk3506_armclk` is a branch-level ARMCLK mux over `"armclk_pll"` and `"clk_core_pvtpll"` with `CLK_IS_CRITICAL | CLK_SET_RATE_PARENT`.
- `rk3506_clk_branches` contains all branch descriptions.
- `rk3506_clk_init()` initializes the provider.
- `clk_rk3506_probe()` dispatches platform matches.

This driver uses `rockchip_clk_register_armclk_multi_pll` rather than the older single-PLL CPU clock registration. It also calls `rk3506_rst_init(np, reg_base)`, supplied by `rst-rk3506.c`, which registers a reset lookup table instead of a simple contiguous soft-reset block.

## Control Flow

`rk3506_clk_init()` performs:

1. Compute `clk_nr_clks` from the maximum ID in `rk3506_clk_branches`.
2. Map the CRU with `of_iomap`.
3. Allocate the Rockchip provider with `rockchip_clk_init`.
4. Register GPLL, V0PLL, and V1PLL.
5. Register the multi-PLL ARM clock with `rockchip_clk_register_armclk_multi_pll`.
6. Register all branch clocks.
7. Initialize resets through `rk3506_rst_init`.
8. Register restart at `RK3506_GLB_SRST_FST`.
9. Publish the provider.
10. Write `PVTPLL_SRC_SEL_PVTPLL` to `RK3506_CLKSEL_CON(15)` to select the PVTPLL source.

The platform probe obtains match data and calls this same init function. Error handling mirrors older CRU files for mapping and provider-allocation failures.

## State And Persistence Behavior

The driver stores no persistent state outside hardware registers and CCF objects. The final explicit `writel_relaxed` changes the core PVTPLL selection in CRU register state after CCF setup. Because this write is outside the declarative branch registration, it is an important side effect to preserve in refactors.

Several roots are `CLK_IS_CRITICAL`, including 24 MHz and PLL gates, core/bus roots, DDRC, high-speed and low-speed peripheral roots, PMU roots, 32 kHz clocks, CRU/PMU PCLKs, and IO-controller clocks. These clocks are expected to survive unused-clock cleanup.

## Dependencies And Integration Points

Dependencies:

- RK3506 dt-binding IDs from `include/dt-bindings/clock/rockchip,rk3506-cru.h`.
- Common Rockchip clock provider, PLL, branch, multi-PLL ARM clock, reset, and restart code.
- `rk3506_rst_init` from the matching reset driver.
- Device-tree parent clocks such as `xin24m`, external SAI MCLK/SCLK inputs, `dummy_vop_dclk`, and `clk_pll_ref_io`.

Integration surfaces:

- CPU clocking uses `armclk_pll`, `clk_core_pvtpll`, and the post-init PVTPLL source write.
- Matrix roots and fractional matrix clocks feed UART, voice, and common clock domains.
- Audio/voice includes SAI0-4, SPDIF TX/RX, PDM, ASRC MCLK/LRCK, DSM, audio ADC, and voice fractional matrices.
- Storage/network includes SDMMC, FSPI, dual MAC clocks, MAC PTP roots, USB OTG, USB PHY, and OTPC clocks.
- PMU/low-power includes 32 kHz muxing, RC clock, touch key, GPIO0, PMU HP timer, PMU CRU/GRF, PWM0, reference outputs, and PHY reference muxes.
- Display/video includes VOP, DSI host, DPHY, RGA, TSADC, and VIO roots.
- Resets are not a simple register count; reset IDs are mapped by `rst-rk3506.c`.

## Risks And Edge Cases

- The explicit PVTPLL source write can be missed because most of the file is declarative. Removing or moving it may leave ARM clock muxing on the wrong source.
- `rockchip_clk_register_armclk_multi_pll` expects a branch description and rate table rather than CPU reg-data. Incorrect conversion to the older API would lose multi-parent behavior.
- The clock tree uses many matrix and fractional intermediate clocks. Parent-name mismatches can break UART/audio/ASRC rate propagation.
- Critical roots are numerous and power-domain sensitive. Over-aggressive cleanup can break DDR, PMU, core, CRU, IO-controller, or bus access.
- Reset handling is delegated to a lookup-table reset driver; replacing it with `rockchip_register_softrst` would not preserve non-contiguous reset IDs.
- Board files must provide external audio and VOP dummy/real parents consistently with the parent names.

## Test Signals

Recommended signals:

- Boot on RK3506 with no CRU map/init errors and with the platform driver not double-registering clocks after early init.
- `clk_summary` shows GPLL/V0PLL/V1PLL, `armclk`, matrix roots, PMU/32 kHz roots, and critical roots.
- CPU rate transitions validate the multi-PLL ARM clock and PVTPLL selection.
- Audio tests across SAI, SPDIF, PDM, ASRC, DSM, and audio ADC validate fractional/matrix parents.
- SDMMC/FSPI, USB, GMAC0/1, MAC PTP, OTPC, DSI/VOP/RGA, and ADC workloads validate peripheral clocks.
- Reset-controller consumers validate `rk3506_rst_init`.
- Reboot validates restart notifier registration.
