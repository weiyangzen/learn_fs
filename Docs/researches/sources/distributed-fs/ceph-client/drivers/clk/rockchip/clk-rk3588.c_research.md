# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3588.c

## Purpose

`clk-rk3588.c` is the Rockchip clock-controller driver for the RK3588 CRU. It describes the SoC clock topology for Linux common clock consumers: PLLs, CPU clocks, fixed factors, muxes, dividers, fractional clocks, gates, MMC phase clocks, linked late gates, soft reset setup, and restart handling. The file is mostly static hardware description, but RK3588 has a two-stage registration path because many clocks must be available very early while some cross-domain `GATE_LINK` clocks are registered later from a platform driver.

The driver covers the top-level derived frequency roots, little and big CPU clusters, DSU/debug clocks, PMU clocks, audio, bus, center/DDR helper clocks, GPU, NPU, ISP/VI, video encode/decode, AV1, RGA, VDPU, NVM, SDIO/SDMMC/eMMC, USB, PCIe/PHP, GMAC, SATA, HDMI/eDP/DP/DSI/VOP, HDCP/TRNG, pipe PHY references, GPIO, I2C, SPI, UART, PWM, timers, watchdogs, ADCs, CAN, crypto-adjacent OTP/TRNG, and other internal fabric clocks.

## Important APIs, Types, And Data

- `enum rk3588_plls` indexes B0/B1/Little CPU PLLs plus V0PLL, AUPLL, CPLL, GPLL, NPLL, and PPLL in `rk3588_pll_clks[]`.
- `rk3588_pll_rates[]` is the shared RK3588 PLL rate table, spanning CPU-scale rates up to 2.52 GHz down to 96 MHz, including fractional audio/display-oriented rates.
- CPU clock rate macros (`RK3588_CPUB01CLK_RATE`, `RK3588_CPUB23CLK_RATE`, `RK3588_CPULCLK_RATE`) encode the pre-mux and post-mux register writes needed to switch clusters safely while changing PLL rates. The companion `rockchip_cpuclk_reg_data` objects describe per-core dividers and mux fields for the two big-core pairs and the four little cores.
- Parent-name arrays (`PNAME(...)`) define the CCF parent graph for PLLs, generated top roots, audio fractional sources, external MCLK inputs, display PHY pixel parents, GMAC PTP input options, PMU roots, and pipe PHY references.
- `rk3588_pll_clks[]` declares PLL register offsets, mode register bits, lock status offset (`RK3588_GRF_SOC_STATUS0`), and `CLK_IGNORE_UNUSED` policy for core PLLs that must not be disabled opportunistically.
- `rk3588_early_clk_branches[]` contains almost the entire clock tree using Rockchip helper macros such as `FACTOR`, `COMPOSITE`, `COMPOSITE_NODIV`, `COMPOSITE_NOMUX`, `COMPOSITE_HALFDIV`, `COMPOSITE_FRACMUX`, `GATE`, `MUX`, and `MMC`.
- Fractional mux helper branches such as `rk3588_uart*_fracmux`, `rk3588_i2s*_fracmux`, `rk3588_spdif*_fracmux`, and `rk3588_hdmirx_aud_fracmux` provide the final mux stage that can select integer source, fractional divider, external input, or 12/24 MHz fallback.
- `rk3588_clk_branches[]` holds late `GATE_LINK` descriptors. These model clocks whose enablement depends on another clock ID, such as ISP1 linked to VI roots, USB linked to VO1USB roots, video blocks linked to VDPU roots, and display GRF gates linked to VO roots.
- `MFLAGS`, `DFLAGS`, and `GFLAGS` consistently request hiword write masking for mux/divider/gate register writes, with gates using set-to-disable semantics.

## Control Flow

Early boot matching uses `CLK_OF_DECLARE_DRIVER(rk3588_cru, "rockchip,rk3588-cru", rk3588_clk_early_init)`. `rk3588_clk_early_init()` finds the maximum clock ID across both early and late branch arrays, maps the CRU region with `of_iomap()`, creates an early Rockchip clock provider with `rockchip_clk_init_early()`, stores it in the file-static `early_ctx`, registers all PLLs, registers three CPU clocks (`armclk_l`, `armclk_b01`, `armclk_b23`), registers the early branch table, and publishes the OF clock provider.

At `core_initcall`, `rockchip_clk_rk3588_drv_register()` registers a platform driver for the same compatible. Its probe reuses `early_ctx`, registers late linked branches with `rockchip_clk_register_late_branches()`, calls `rockchip_clk_finalize()`, initializes resets through `rk3588_rst_init()`, registers the restart notifier at `RK3588_GLB_SRST_FST`, then removes and re-adds the OF clock provider so newly registered clocks are visible and default parent/rate assignments can be applied.

After registration, runtime control is delegated to the CCF and Rockchip clock helpers. Consumer rate changes traverse mux/divider/fractional/PLL parents according to `CLK_SET_RATE_PARENT` and `CLK_SET_RATE_NO_REPARENT` flags. Gate enables update hiword-mask gate registers. MMC phase clocks program SDMMC/SDIO tuning registers. Restart requests flow through the Rockchip restart notifier.

## State And Persistence Behavior

The driver has one file-static pointer, `early_ctx`, used to bridge early OF_DECLARE registration and the later platform probe. All other long-lived software state is owned by the common clock framework and Rockchip provider after registration. The actual mutable clock state lives in RK3588 CRU, PMU CRU, GRF/status, gate, mux, divider, fractional divider, PLL, MMC phase, reset, and restart registers.

Important persistence details include:

- Early clocks are available before normal driver probing. Late clocks depend on the platform probe seeing the same device node and a valid `early_ctx`.
- The file uses many `CLK_IS_CRITICAL`, `CLK_IGNORE_UNUSED`, and read-only divider flags to protect fabric, CPU, DSU, PMU, DDR, debug, PHY, and firmware-sensitive clocks from CCF cleanup or accidental reprogramming.
- Several display pixel clocks use `CLK_SET_RATE_NO_REPARENT`, which preserves selected PHY/PLL parent relationships while allowing rate propagation.
- Linked gates encode dependency state across domains, so enabling one exposed clock can also keep an upstream domain/root clock prepared.
- The driver does not persist configuration across reboot; it reconstructs the provider from hardware and static tables at boot.

## Dependencies And Integration Points

The file depends on Linux OF address mapping, platform driver registration, CCF provider APIs, Rockchip clock helpers in `clk.h`, RK3588 DT binding IDs in `dt-bindings/clock/rockchip,rk3588-cru.h`, and RK3588 reset helper declarations such as `rk3588_rst_init()`. Device tree must expose a `rockchip,rk3588-cru` node and named external parents consumed by the clock graph, including oscillator inputs, SCMI SD clock, audio MCLK inputs, HDMI/DP/pipe PHY clocks, GMAC PTP IO clocks, and other PHY/output clocks.

Consumers include CPUfreq, serial, I2C, SPI, PWM, timers, watchdogs, GPIO debounce, SARADC/TSADC, CAN, SDHCI/DW-MMC/eMMC/SFC, USB host/OTG, PCIe/SATA, GMAC, audio I2S/SPDIF/PDM/VAD, display VOP/DSI/eDP/HDMI/DP/HDCP, video encode/decode, AV1, RGA/IEP/JPEG, ISP/VI/CSI/fisheye, GPU, NPU, DDR helper firmware, PMU firmware, restart, and reset-controller consumers.

## Risks And Edge Cases

- The early/late split is sensitive to `early_ctx`. If early init fails but the platform driver still probes, `clk_rk3588_probe()` would dereference a null or invalid context.
- Binding IDs and array entries are ABI. Moving or mislabeling an ID can break existing device-tree consumers.
- Register offsets and bit positions are highly dense. A wrong mux, divider, gate, PLL mode bit, or linked gate target can affect unrelated hardware domains.
- `GATE_LINK` dependencies are easy to under-specify. Missing links can allow a downstream peripheral clock to enable without a required root/domain clock.
- External parents such as PHY pixel clocks, audio MCLK inputs, pipe clocks, GMAC reference inputs, and `scmi_cclk_sd` must match provider names and probe order.
- Fractional audio/UART clocks depend on safe parent rates. Parent-rate changes can disturb serial baud or audio sample-rate accuracy if consumers do not coordinate.
- Critical and ignore-unused flags are part of boot stability. Removing them can break DDR, PMU, debug, display, USB PHY, or firmware-owned paths.

## Test Signals

Useful validation starts with boot logs showing successful RK3588 CRU early init and later `clk-rk3588` probe, no provider replacement warnings, and a populated `/sys/kernel/debug/clk/clk_summary`. Rate tests should cover CPU cluster transitions, top roots, UART fractional rates, I2S/SPDIF audio rates, VOP display pixel clocks, SDMMC/SDIO/eMMC MMC phase clocks, GPU/NPU/video/ISP roots, and GMAC/PCIe/USB PHY reference clocks. Functional tests should exercise serial consoles, storage, USB, PCIe/SATA, Ethernet, display pipelines, audio playback/capture, camera capture, video encode/decode, GPU/NPU workloads, suspend/resume, and restart. Reset tests should verify `rk3588_rst_init()`-provided reset lines without hangs.
