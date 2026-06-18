# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3368.c

## Purpose

`clk-rk3368.c` implements the RK3368 CRU clock provider. It exposes PLLs, separate big/little CPU clocks, bus and peripheral roots, display/video/audio/network/storage clocks, phase clocks for MMC-family controllers, critical clocks, soft resets, and restart support.

The driver is registered through `CLK_OF_DECLARE(rk3368_cru, "rockchip,rk3368-cru", rk3368_clk_init)`, so it is an early OF clock provider. It is structurally similar to other Rockchip CRU files but has two ARM clock domains: `ARMCLKB` and `ARMCLKL`.

## Important APIs, Types, And Functions

Key data and APIs:

- `enum rk3368_plls` indexes APLLB, APLLL, DPLL, CPLL, GPLL, and NPLL.
- `rk3368_pll_rates` provides PLL settings using the `RK3066_PLL_RATE` format.
- `rk3368_pll_clks` registers RK3066-style PLLs, with CPLL/GPLL/NPLL marked `ROCKCHIP_PLL_SYNC_RATE`.
- `rk3368_cpuclkb_data` and `rk3368_cpuclkl_data` describe the register layout for big and little CPU clusters.
- `rk3368_cpuclkb_rates` and `rk3368_cpuclkl_rates` define cluster rate/divider programming.
- `div_ddrphy_t` supplies a DDR PHY divider table for a non-linear divider mapping.
- `rk3368_clk_branches` is the main branch table for bus, DDR, audio, UART, video, VIO, GPU, peripheral, alive, and PMU clocks.
- `rk3368_critical_clocks` protects bus, PMU, DDR, OTG, and GRF/SGRF-adjacent clocks.
- `rk3368_clk_init()` performs CRU mapping and registration.

The file uses the common Rockchip macros `PLL`, `PNAME`, `MUX`, `DIV`, `GATE`, `COMPOSITE`, `COMPOSITE_FRACMUX`, `COMPOSITE_NOGATE`, `COMPOSITE_NOMUX`, `COMPOSITE_NOGATE_DIVTBL`, `FACTOR`, `FACTOR_GATE`, `MMC`, and `SGRF_GATE`.

## Control Flow

`rk3368_clk_init()` performs:

1. `of_iomap` of the CRU register block.
2. Clock table sizing from the maximum branch ID.
3. Provider allocation through `rockchip_clk_init`.
4. PLL registration for all six PLLs.
5. Branch registration for all mux/divider/gate/composite/MMC clocks.
6. Critical-clock protection.
7. Registration of `ARMCLKB` and `ARMCLKL` through two calls to `rockchip_clk_register_armclk`.
8. Registration of 15 hiword soft-reset registers at `RK3368_SOFTRST_CON(0)`.
9. Restart notifier registration using `RK3368_GLB_SRST_FST`.
10. OF provider publication.

Failures are handled early. If MMIO mapping fails, no cleanup is required. If provider allocation fails, the register mapping is released before returning.

## State And Persistence Behavior

The file has no disk-backed state. Its durable effects during runtime are CRU register programming and CCF registrations. PLL sync flags matter because parent rates may need to be synchronized with hardware state. Gate and divider writes use hiword-mask flags to update individual fields safely.

The critical list intentionally leaves infrastructure clocks enabled, including `aclk_bus`, `pclk_bus`, PMU and DDR clocks, `pclk_grf`, `pclk_sgrf`, and OTG-related paths. `SGRF_GATE(PCLK_WDT, ...)` marks watchdog access as secure-GRF controlled and therefore not normally controllable by this non-secure clock provider.

## Dependencies And Integration Points

Dependencies:

- RK3368 dt-binding IDs from `include/dt-bindings/clock/rk3368-cru.h`.
- Common Rockchip clock, PLL, CPU clock, MMC phase, reset, and restart support.
- OF-provided parent clocks such as `xin24m`, `xin32k`, `ext_gmac`, `ext_jtag`, `ext_isp`, `ext_vip`, and `ext_hsadc_tsp`.

Important consumers and integration surfaces:

- CPUfreq and SMP cluster clocking use `ARMCLKB` and `ARMCLKL`, independent PLL source gates, and divider programming for `aclkm`, `atclk`, and debug PCLK.
- DDR clocking uses DPLL/GPLL parents, `ddrphy_src`, `sclk_ddr`, `sclk_ddr4x`, and DDR controller/PHY gates.
- Audio uses I2S 8-channel, I2S 2-channel, SPDIF, and fractional muxes.
- UART0/1/3/4 use fractional paths; UART2 uses a simpler mux from `uart2_src` or `xin24m`.
- Display/video paths include VOP, VIP, ISP, eDP, HDMI, HDCP, MIPI DSI/CSI, RGA, VEPU/VDPU, HEVC, and VIO gates.
- Peripheral integration includes SPI0-2, SDMMC/SDIO/eMMC with phase clocks, NANDC, SFC, USB OTG/HSIC, GMAC, I2C, PWM, timers, ADCs, GPIO, mailbox, EFUSE, PMU, and alive-domain clocks.

## Risks And Edge Cases

- Big/little CPU clock registration has duplicated but offset-specific register data. A wrong offset in `RK3368_CLKSEL0` or `RK3368_CLKSEL1` affects only one cluster and can be hard to diagnose.
- The DDR divider table is a special-case mapping; replacing it with a linear divider would program wrong rates.
- Parent-name arrays include dummy or external names. Device-tree or board-level mismatches can leave clocks with unresolved parents.
- Secure GRF controlled watchdog gating cannot be managed normally; consumers must not assume a regular gate can enable it.
- Critical-clock underprotection can hang NoC, PMU, DDR, or debug infrastructure during unused-clock cleanup.
- PLL sync-rate flags on shared PLLs affect rate changes across consumers; incorrect flags risk rate drift or unexpected reprogramming.

## Test Signals

Validation should include:

- Boot on RK3368 without CRU map/init failures.
- `clk_summary` contains both `armclkb` and `armclkl`, PLLs, DDR roots, and critical bus/PMU clocks.
- CPUfreq or manual rate changes exercise both cluster rate tables.
- DDR stability under memory stress confirms DDR-related roots and gates.
- Console and non-console UARTs validate fractional and non-fractional UART paths.
- I2S/SPDIF playback checks audio fractional muxes.
- SDMMC/SDIO/eMMC operation and tuning validate `MMC` delay/phase entries.
- Display, ISP/VIP, HDMI/eDP/MIPI, and video codec workloads validate VIO/video branch layout.
- Reset consumers and reboot validate soft-reset and restart registration.
