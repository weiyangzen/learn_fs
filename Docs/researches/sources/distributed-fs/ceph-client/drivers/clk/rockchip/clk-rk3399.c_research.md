# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3399.c

## Purpose

`clk-rk3399.c` provides clock/reset support for the RK3399 CRU and PMUCRU. It models a large RK3399 clock tree, including main-domain PLLs, PMU-domain PPLL, two CPU clusters, DDRC, CCI/debug, USB/PCIe/GMAC, audio, UART, display, ISP, VOP, video codecs, peripheral roots, critical clocks, soft resets, and restart support.

Unlike simpler early-only CRU files, this file includes both `CLK_OF_DECLARE` hooks and a built-in platform driver. The platform driver dispatches to the same init functions based on `rockchip,rk3399-cru` or `rockchip,rk3399-pmucru` match data, while the `CLK_OF_DECLARE` hooks preserve early clock-provider availability.

## Important APIs, Types, And Functions

Key structures:

- `enum rk3399_plls` indexes main CRU PLLs: LPLL, BPLL, DPLL, CPLL, GPLL, NPLL, and VPLL.
- `enum rk3399_pmu_plls` indexes PMUCRU PPLL.
- `rk3399_pll_rates` defines RK3399 PLL programming points.
- `rk3399_pll_clks` and `rk3399_pmu_pll_clks` describe main and PMU PLL blocks using `PLL(pll_rk3399, ...)`.
- `rk3399_cpuclkl_data`, `rk3399_cpuclkb_data`, `rk3399_cpuclkl_rates`, and `rk3399_cpuclkb_rates` describe little and big cluster ARM clocks.
- `rk3399_clk_branches` is the main CRU branch table.
- `rk3399_clk_pmu_branches` is the PMUCRU branch table.
- `rk3399_cru_critical_clocks` and `rk3399_pmucru_critical_clocks` protect essential infrastructure.
- `rk3399_clk_init()` initializes the main CRU.
- `rk3399_pmu_clk_init()` initializes the PMUCRU.
- `clk_rk3399_probe()` calls the proper init function from `device_get_match_data`.

The file uses advanced Rockchip branch helpers including `COMPOSITE_FRACMUX_NOGATE`, `COMPOSITE_DDRCLK`, `INVERTER`, `MMC`, `SGRF_GATE`, and many normal mux/divider/gate/composite macros.

## Control Flow

Main CRU initialization:

1. `rk3399_clk_init()` maps the CRU with `of_iomap`.
2. It sizes the provider from `rk3399_clk_branches`.
3. It allocates a provider and registers main PLLs.
4. It registers main branches.
5. It registers `ARMCLKL` and `ARMCLKB` with separate parent muxes, rate tables, and CPU register data.
6. It protects main critical clocks.
7. It registers 21 hiword soft-reset registers at `RK3399_SOFTRST_CON(0)`.
8. It registers the restart notifier at `RK3399_GLB_SRST_FST`.
9. It publishes the OF clock provider.

PMUCRU initialization:

1. `rk3399_pmu_clk_init()` maps the PMU CRU region.
2. It sizes and allocates a separate provider.
3. It registers PPLL and PMU branches.
4. It protects PMU critical clocks.
5. It registers two PMU soft-reset registers.
6. It publishes the PMU OF clock provider.

The platform driver has a tiny probe path: match data holds a function pointer, and probe invokes it for the node. The platform driver is marked `suppress_bind_attrs = true`, fitting the built-in clock-provider role.

## State And Persistence Behavior

Runtime state is held in CRU/PMUCRU registers and CCF registrations. The file creates two independent provider contexts when both CRU and PMUCRU are present. Register writes use hiword update flags for muxes, dividers, gates, and inverters. PLLs are synchronized to hardware via `ROCKCHIP_PLL_SYNC_RATE` for shared PLLs, while CPU PLLs are managed by CPU clock registration.

The critical lists are broad. The main CRU protects CCI, GIC, HDCP NoCs, peripheral roots, eMMC NoC, DDRC, and both ARM clocks. The PMUCRU protects PPLL, PMU PCLK source, CM0S source, timer source, and PMU PWM PCLK. These are safety guards against common-clock unused cleanup and runtime disable.

## Dependencies And Integration Points

Dependencies:

- RK3399 dt-binding clock IDs from `include/dt-bindings/clock/rk3399-cru.h`.
- Common Rockchip CCF helpers for PLLs, CPU clocks, DDR clocks, fractional muxes, MMC phase clocks, SGRF gates, reset, and restart.
- OF/platform bus matching through `CLK_OF_DECLARE`, `of_device_id`, and `builtin_platform_driver_probe`.
- Parent clocks and external inputs such as `xin24m`, `xin32k`, USB PHY 480 MHz outputs, PCIe PHY reference, GMAC input, and display/audio external parents.

Integration surfaces:

- CPUfreq uses `ARMCLKL` and `ARMCLKB`, with parent muxes over LPLL/BPLL/DPLL/GPLL-derived sources and per-cluster divider writes.
- DDR clocking uses `COMPOSITE_DDRCLK(SCLK_DDRC, ...)` and DPLL/BPLL/LPLL/GPLL paths.
- PMU island clocks serve GPIO0/1, PMU I2C/SPI/UART4, CM0S, timers, mailbox, PMU watchdog, PMU SRAM/NoC, and low-power infrastructure.
- High-speed I/O includes USB2/USB3, Type-C PHY reference/core clocks, PCIe, GMAC/RMII, HSIC, eMMC/SD/SDIO, SFC, and SPI.
- Media/display includes VOP0/VOP1 fractional display clocks, HDMI/DP/eDP/HDCP, ISP0/1, CIF, RGA, IEP, VDU, VCODEC, GPU, VIO, MIPI DPHY, and test clock outputs.
- Audio and serial include SPDIF, I2S0/1/2, I2S output muxing, UART0-4 fractional paths, and peripheral PCLK gates.

## Risks And Edge Cases

- Dual registration paths mean early OF init and platform-driver probing must not create harmful duplicate providers. The file intentionally points both mechanisms at the same init routines; any framework behavior change around duplicate init would need review.
- There are two provider contexts with separate reset-controller ranges and critical-clock lists. Cross-domain consumers must reference the right compatible node.
- Clock names and IDs are numerous. Misordered dt-binding IDs or branch IDs can break unrelated consumers.
- DDRC, CCI, GIC, NoC, and PMU clocks are critical. Removing protection can lead to hangs during boot, suspend, or unused-clock pruning.
- Fractional display/audio/UART paths depend on correct parent and divider programming; minor register-field errors surface as baud drift, audio clock drift, or display timing failures.
- `COMPOSITE_DDRCLK` and CPU clock transitions have hardware-specific ordering expectations hidden in common Rockchip helpers; table changes should be tested on hardware.

## Test Signals

Good validation coverage includes:

- Boot with both `rockchip,rk3399-cru` and `rockchip,rk3399-pmucru` present and no duplicate-provider warnings.
- `clk_summary` shows main CRU and PMUCRU PLLs, both ARM clocks, DDRC, PMU roots, and protected critical clocks.
- CPUfreq on little and big clusters validates rate tables.
- Suspend/resume or low-power testing checks PMUCRU, 32 kHz, CM0S, timer, and PMU peripheral clocks.
- Memory stress validates DDRC clocking.
- Display tests across HDMI/DP/eDP/VOP0/VOP1 validate fractional display clocks.
- UART, I2S, SPDIF, SD/eMMC/SDIO, USB3, PCIe, GMAC, GPU, ISP, and codec workloads exercise the broad branch table.
- Reset-controller consumers and reboot validate the main and PMU soft-reset registrations plus restart notifier.
