# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3528.c

## Purpose

`clk-rk3528.c` is the RK3528 CRU platform driver. It registers PLLs, ARM clocking, matrix roots, UART/audio fractional clocks, bus/PMU/DDR/GPU/video/display/storage/network/peripheral clocks, optional VO/VPU GRF-backed MMC phase clocks, reset lookup-table support, restart handling, and OF provider publication.

The file is platform-driver only: `builtin_platform_driver_probe(clk_rk3528_driver, clk_rk3528_probe)` binds `rockchip,rk3528-cru`. This path uses managed MMIO mapping and device-managed allocation for auxiliary GRF table entries.

## Important APIs, Types, And Functions

Key data:

- `RK3528_GRF_SOC_STATUS0` is passed to PLL registration, likely for PLL lock/status handling through system GRF.
- `enum rk3528_plls` indexes APLL, CPLL, GPLL, PPLL, and DPLL.
- `rk3528_pll_rates` defines PLL programming points.
- `rk3528_cpuclk_rates` and `rk3528_cpuclk_data` define ARM clock rates and divider/mux register fields.
- `rk3528_pll_clks` registers PLLs, with PPLL marked `ROCKCHIP_PLL_FIXED_MODE` and DPLL using DDRPHY mode registers.
- `rk3528_clk_branches` is the main clock branch table.
- `rk3528_vo_clk_branches` contains VO-GRF MMC phase clocks for SDMMC.
- `rk3528_vpu_clk_branches` contains VPU-GRF MMC phase clocks for SDIO0/SDIO1.
- `clk_rk3528_probe()` performs all initialization.

The file uses many Rockchip macros: `COMPOSITE_NOMUX_HALFDIV`, `COMPOSITE_FRACMUX`, `COMPOSITE_NODIV`, `MUX`, `DIV`, `GATE`, `FACTOR`, `FACTOR_GATE`, and `MMC_GRF`. It also directly manipulates `ctx->aux_grf_table` via `hash_add` for auxiliary GRF regmaps.

## Control Flow

`clk_rk3528_probe()`:

1. Maps CRU MMIO with `devm_platform_ioremap_resource`.
2. Computes the base clock table size from `rk3528_clk_branches`.
3. Looks up optional `rockchip,rk3528-vo-grf`. If present, it expands `nr_clks` to cover `rk3528_vo_clk_branches`; if absent with `-ENODEV`, it continues; other errors abort probe.
4. Looks up optional `rockchip,rk3528-vpu-grf` with the same behavior for VPU clocks.
5. Allocates the Rockchip provider.
6. Registers PLLs with `RK3528_GRF_SOC_STATUS0`.
7. Registers `ARMCLK` from APLL/GPLL parents.
8. Registers main CRU branches.
9. If VO GRF exists, allocates a `rockchip_aux_grf`, stores `grf_type_vo`, adds it to `ctx->aux_grf_table`, and registers VO MMC phase branches.
10. If VPU GRF exists, repeats the process with `grf_type_vpu` and VPU MMC phase branches.
11. Initializes reset support through `rk3528_rst_init`.
12. Registers restart at `RK3528_GLB_SRST_FST`.
13. Publishes the OF clock provider.

All major failures return through `dev_err_probe`, making deferred-probe or error diagnosis visible to the device model.

## State And Persistence Behavior

Runtime state is in CRU/GRF registers, optional auxiliary GRF regmaps, the provider lookup table, and CCF objects. Optional VO/VPU GRF state affects only MMC phase clocks backed by those GRF regions; the main provider still registers when these optional GRFs are absent.

The driver marks many matrix, bus, PMU, DDR, GPU, VPU, VO, CRU, GRF, IOC, and PCLK roots as `CLK_IS_CRITICAL` or `CLK_IGNORE_UNUSED`. PPLL is fixed-mode, DPLL is associated with DDRPHY mode control, and DDR-related gates are critical.

## Dependencies And Integration Points

Dependencies:

- RK3528 dt-binding IDs from `include/dt-bindings/clock/rockchip,rk3528-cru.h`.
- Common Rockchip clock, PLL, CPU clock, auxiliary GRF, reset, and restart support.
- `rk3528_rst_init` from `rst-rk3528.c`.
- Syscon regmaps for optional `rockchip,rk3528-vo-grf` and `rockchip,rk3528-vpu-grf`.
- Device-tree parent clocks such as `xin24m`, `gmac0`, and PLL-derived parents.

Integration surfaces:

- CPUfreq uses `ARMCLK` over APLL/GPLL with ACLK_M_CORE and PCLK_DBG divider programming.
- DDR uses DPLL, DDRPHY mode registers, critical DDR controller/PHY/upctl/scramble/split clocks, and DDR monitor clocks.
- Matrix roots derive standard 50/100/150/200/250/300/339/400/500/600 MHz clocks for broad SoC consumers.
- UART0-7 use fractional muxes. I2S0-3/SAI and SPDIF use fractional muxes and MCLK gates.
- PMU domain includes MCU, PMU SRAM, I2C2, PMU HP timer, PMU IOC/CRU/GRF, watchdog, GPIO0, oscillator checker, mailbox, SCR key generator, PVTM, refout, 32 kHz, and DDR fail-safe clock.
- Media/peripheral domains include GPU, RKVDEC, RKVENC, VOP, VO, VPU, JPEG, VDPP, RGA2E, HDCP, HDMI/CVBS, USB host/OTG, PCIe, eMMC, SDMMC0, SDIO0/1, SFC, GMAC0/1, CAN, SPI, I2C, PDM, ACODEC, ADCs, TSADC, and GPIO debounce.
- MMC phase clocks for SDMMC/SDIO are split into optional VO/VPU GRF-backed branch arrays rather than the main CRU table.

## Risks And Edge Cases

- Optional VO/VPU GRFs are deliberately tolerated when absent only for `-ENODEV`. Other syscon errors abort probe. Board DTS errors can therefore remove MMC phase clocks or fail the entire clock provider depending on error type.
- `nr_clks` must include optional branch IDs before provider allocation. Forgetting to expand it would cause lookup-table overflows or missing phase clocks.
- Auxiliary GRF entries must use the correct `grf_type_vo`/`grf_type_vpu`; otherwise `MMC_GRF` branches write to the wrong regmap or fail to register.
- PPLL fixed mode and DPLL DDRPHY mode are hardware-specific. Treating them as normal PLLs can destabilize PCIe/network or DDR.
- Many clocks are marked critical because disabling them can break register access, memory, or power-management infrastructure. Cleanup changes require hardware testing.
- Duplicate clock names such as domain-local `clk_tsadc`/`clk_saradc` style entries should be reviewed with dt-binding consumers to avoid lookup confusion.

## Test Signals

Useful validation:

- Probe succeeds with and without optional VO/VPU GRF nodes; only non-`ENODEV` lookup failures should abort.
- `clk_summary` shows APLL/CPLL/GPLL/PPLL/DPLL, ARMCLK, matrix roots, DDR roots, PMU roots, and optional MMC phase clocks when GRFs exist.
- CPU rate changes validate `rk3528_cpuclk_rates`.
- DDR stress validates DPLL/DDR critical clocks.
- UART0-7 baud tests validate fractional muxes.
- I2S/SAI/SPDIF audio validates fractional audio clocks.
- SDMMC0/SDIO0/SDIO1 tuning validates VO/VPU `MMC_GRF` phase clocks.
- Display/video/GPU/VPU/RKVDEC/RKVENC/HDMI/CVBS/USB/PCIe/GMAC workloads exercise domain roots.
- Reset consumers validate `rk3528_rst_init`; reboot validates restart notifier registration.
