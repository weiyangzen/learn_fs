# Research: subset-b-001161

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3588.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3588.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rv1103b.c -->
# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rv1103b.c

## Purpose

`clk-rv1103b.c` is the CRU driver for Rockchip RV1103B. It registers the SoC's PLLs, CPU clock, clock branches, restart notifier, and OF clock provider using the Rockchip clock framework. The file is table-driven and tuned for a small camera/AI-oriented SoC with PMU, VI/ISP, VEPU, NPU, peripheral, DDR, storage, audio, UART, and always-on low-speed clock domains.

The driver exposes clock IDs from `dt-bindings/clock/rockchip,rv1103b-cru.h` to device-tree consumers. It also performs a small post-registration hardware initialization step that selects PVTPLL sources for CPU, NPU, VI, and VEPU paths.

## Important APIs, Types, And Data

- `enum rv1103b_plls` declares `dpll` and `gpll`; both are registered from `rv1103b_pll_clks[]` using `pll_rk3328` descriptors and `rv1103b_pll_rates[]`.
- `rv1103b_pll_rates[]` contains a compact RK3036-style rate table for 1.2 GHz, 1.188 GHz, and 1.0 GHz. PLL lock status is read through `RV1103B_GRF_SOC_STATUS0`.
- CPU-rate macros encode ACLK core and PCLK debug divisors in `RV1103B_CORECLKSEL_CON(2)`. `rv1103b_cpuclk_rates[]` lists supported CPU parent rates from 1.608 GHz down to 396 MHz with associated bus/debug dividers.
- Parent arrays define derived GPLL divider parents, low-speed PMU roots, UART fractional muxes, SAI/audio muxes, NPU/VEPU/ISP PVTPLL alternatives, storage/peripheral parents, 32 kHz sources, and IO output muxes.
- `rv1103b_clk_uart0_fracmux`, `rv1103b_clk_uart1_fracmux`, and `rv1103b_clk_uart2_fracmux` are final mux stages for UART integer, fractional, and 24 MHz parents.
- `rv1103b_rcdiv_pmu_fracmux` finalizes the `clk_32k` selection from RC-divided, RTC, or IO 32 kHz sources.
- `rv1103b_clk_branches[]` is the main descriptor array. It contains GPLL fixed divisors, UART/SPI/I2C/PWM/timer/watchdog/GPIO/ADC/storage gates, SAI and audio codec clocks, VI/ISP/CSI/VICAP clocks, VEPU/NPU roots, DDR monitor clocks, PMU and PMU1 low-power clocks, crypto/RNG/OTP/RGA/GMAC/USB/decompress clocks, and IO-output clocks.
- `rv1103b_armclk` is a mux between `armclk_gpll` and `clk_core_pvtpll`, registered with `rockchip_clk_register_armclk_multi_pll()` so CPU clocking can switch between multiple PLL sources.

## Control Flow

`CLK_OF_DECLARE(rv1103b_cru, "rockchip,rv1103b-cru", rv1103b_clk_init)` installs an early OF init hook. `rv1103b_clk_init()` computes the number of clock slots from the maximum ID in `rv1103b_clk_branches[]`, maps the CRU register range with `of_iomap()`, creates a Rockchip clock provider with `rockchip_clk_init()`, and returns early with an error message on mapping or provider setup failure.

On success, it registers PLLs with `rockchip_clk_register_plls()`, registers the main branch table, registers the multi-PLL CPU clock, registers a restart notifier at `RV1103B_GLB_SRST_FST`, and publishes the provider with `rockchip_clk_of_add_provider()`. Finally it writes `PVTPLL_SRC_SEL_PVTPLL` to the CPU, NPU, VI, and VEPU clock-select registers so those domains use PVTPLL sources where their muxes expose them.

At runtime, CCF consumers use the registered clocks. Rockchip helper ops update mux, divider, fractional, gate, and PLL registers with hiword masks; restart is handled by the common Rockchip restart notifier path.

## State And Persistence Behavior

The file keeps no dynamic private state after init. Provider and clock state is owned by the Rockchip clock framework. Mutable state is in CRU and PMU CRU registers: PLL configuration and mode bits, divider/mux fields, fractional divider registers, gate registers, CPU clock dividers, restart register, and the PVTPLL source-selection fields explicitly written at the end of init.

Several descriptors affect state behavior:

- `CLK_IS_CRITICAL` protects PLLs and key bus/root clocks such as `armclk_gpll`, LSCLK roots, VI source roots, PERI roots, PMU root, DDR root, and SRAM-related clocks.
- `CLK_SET_RATE_PARENT` on UART, SAI, NPU/VEPU/ISP PVTPLL root muxes, MIPI output, and 32 kHz mux paths allows leaf requests to propagate into source clocks.
- `CLK_SET_RATE_NO_REPARENT` on `clk_32k` avoids unexpected source switching after the selected 32 kHz parent is established.
- The PVTPLL writes are persistent only until reset or later firmware/driver writes; there is no suspend-time save/restore in this file.

## Dependencies And Integration Points

The driver depends on OF address mapping, Linux CCF, Rockchip clock helpers, and the RV1103B clock binding header. Device tree must provide the `rockchip,rv1103b-cru` node and external parent names used in the graph, including `xin24m`, `clk_rc_osc_io`, `clk_32k_rtc`, `clk_32k_io`, SAI IO clocks, MIPI reference outputs, USB UTMI IO clocks, SPI2AHB IO clock, and PVTPLL clocks (`clk_core_pvtpll`, `clk_npu_pvtpll`, `clk_vepu_pvtpll`, `clk_isp_pvtpll_src`).

Consumer integration includes CPUfreq, low-power MCU and PMU firmware, UART0-2, I2C0-4, SPI, PWM, timers, watchdogs, GPIO debounce, SARADC/TSADC, SAI/audio codec, NPU/RKNN, VEPU, ISP/VICAP/CSI, eMMC/SDMMC/SFC, DDR monitor, USB OTG/PHY, crypto/RNG/OTP, RGA, GMAC, decompressor, spinlock, mailboxes, and restart.

## Risks And Edge Cases

- The PVTPLL source writes after provider registration are direct `writel_relaxed()` calls. If a PVTPLL parent is absent, unprepared, or not rate-compatible, CPU/NPU/VI/VEPU consumers can see unexpected clocks.
- The computed clock count depends on branch IDs only; if a future CPU or PLL clock ID exceeds the branch maximum, the provider allocation could be too small.
- The file uses both `RV1103B_*` and some `RK3568_PMU_CLKSEL_CON` register macros for PMU 32 kHz and GPIO debounce paths. Those aliases must match the RV1103B register layout.
- Fractional UART and SAI clocks are parent-rate sensitive, especially because `RV1103B_FRAC_MAX_PRATE` indicates fractional parent-rate constraints even though the constant is not directly referenced in this file.
- Critical clock flags are required for low-speed roots, DDR, VI, and peripheral fabric; dropping them can make late unused-clock cleanup break boot or firmware paths.
- As with all Rockchip clock tables, incorrect binding ID, gate bit, mux width, or divider field can silently affect unrelated hardware.

## Test Signals

Validation should show successful early init for `rockchip,rv1103b-cru`, registered PLLs, a populated clock summary, and no missing-parent messages. Rate tests should exercise CPU frequency changes, UART baud-rate generation through fractional muxes, SAI/audio rates, 32 kHz source selection, storage clocks, ISP/VEPU/NPU roots, and MIPI output clocks. Functional tests should cover serial console, storage boot, camera capture, video encode, RKNN/NPU workloads, audio, USB OTG, GMAC, crypto/RNG/OTP access, timers/watchdogs, GPIO debounce wake paths, and restart behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rv1103b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rv1108.c -->
# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rv1108.c

## Purpose

`clk-rv1108.c` is the Rockchip CRU driver for RV1108. It publishes PLLs, the ARM clock, clock branches, critical-clock protection, soft resets, restart support, and MMC phase clocks to Linux. The clock tree covers a compact multimedia SoC with CPU/core, bus, PMU wrapper, DDR, peripheral, video input/output, video encode/decode, DSP, audio, storage, USB, GMAC, crypto, ADCs, PWM/I2C/SPI/UART, and camera interface clocks.

The file is structured as one OF-declared init routine plus static data tables. Consumers use IDs from `dt-bindings/clock/rv1108-cru.h`; the hardware programming is handled by generic Rockchip CCF helpers.

## Important APIs, Types, And Data

- `enum rv1108_plls` declares APLL, DPLL, and GPLL. `rv1108_pll_clks[]` registers them as `pll_rk3399` PLLs with per-PLL control/mode offsets and lock status at `RV1108_GRF_SOC_STATUS0`. DPLL is registered with a null rate table, reflecting a more fixed or firmware/DDR-owned role.
- `rv1108_pll_rates[]` is a broad RK3036-style rate table from 1.608 GHz to 96 MHz, used by APLL and GPLL.
- `rv1108_cpuclk_rates[]` maps CPU parent rates to core/peripheral dividers, while `rv1108_cpuclk_data` describes the single-core ARM mux/divider fields.
- Parent arrays model PLL variants for core and DDR, USB480M and HDMI PHY inputs, video/display pixel parents, VIO/VIP external clocks, I2S fractional/external parents, GMAC external reference selection, CVBS/HDMI/DSI/CIF sources, DSP parents, MMC parents, and common peripheral roots.
- Fractional mux branches exist for UART0-2 and I2S0-2. They select integer source, fractional source, external IO source where supported, or 12/24 MHz fallback.
- `rv1108_clk_branches[]` describes the full clock tree with Rockchip macros. It includes gate-only PLL domain outputs, core/debug clocks, RKVENC/RKVDEC/VPU roots, PMU clocks, WiFi/CIF/MIPI clocks, DSP clocks, VIO/VOP/HDMI/DSI/CVBS/RGA/ISP clocks, I2S/audio clocks, bus/peripheral roots, UART/SPI/I2C/PWM/timer/watchdog/GPIO/ADC/crypto/DMAC clocks, DDR clocks, SDMMC/SDIO/eMMC/NAND/SFC clocks, USB, GMAC, and MMC drive/sample phase controls.
- `rv1108_critical_clocks[]` names fabric, DDR, PMU, and PHY clocks that are protected after branch registration.
- `MFLAGS`, `DFLAGS`, `GFLAGS`, and `IFLAGS` request hiword-mask writes for muxes, dividers, gates, and inverter controls.

## Control Flow

`CLK_OF_DECLARE(rv1108_cru, "rockchip,rv1108-cru", rv1108_clk_init)` registers the init hook. `rv1108_clk_init()` maps the CRU register range with `of_iomap()`, creates a provider sized to `CLK_NR_CLKS`, registers PLL descriptors, registers all branch descriptors, protects critical clocks by name, registers the ARM clock with `rockchip_clk_register_armclk()`, registers 13 banks of soft resets starting at `RV1108_SOFTRST_CON(0)`, registers the restart notifier at `RV1108_GLB_SRST_FST`, and adds the OF provider.

After init, all operational paths run through the CCF. PLL operations change APLL/GPLL rates, CPU clock operations perform safe mux/divider transitions, composite clocks program mux/divider/gate fields, fractional muxes handle precise audio/serial rates, MMC clocks program sampling/drive phases, reset consumers use the registered soft reset controller, and restart uses the Rockchip notifier.

## State And Persistence Behavior

The driver has no dynamic private state. Persistent state for the booted kernel lives in CCF registrations and reset-controller registration; mutable hardware state lives in CRU registers. This includes PLL mode/config/status, clock-select mux and divider registers, fractional divider registers, gate registers, inverter fields for VIP input, MMC phase registers, soft reset registers, and the global soft reset register used for restart.

Important state choices include:

- Many core, bus, DDR, PMU, and NIU clocks are `CLK_IGNORE_UNUSED`, reflecting clocks needed by firmware, debug, memory, or interconnect paths even without explicit consumers.
- Critical-clock protection by name is applied after branch registration, adding an additional guard around fabric and DDR paths.
- Read-only dividers are used for CPU/debug-derived clocks and DDR-derived paths where the driver should expose the rate without reprogramming the divider.
- DPLL has no rate table in this driver, so consumers should not expect normal dynamic DPLL rate changes through this file.

## Dependencies And Integration Points

The file depends on Linux OF/IO mapping, CCF provider APIs, Rockchip clock and reset helpers, and `dt-bindings/clock/rv1108-cru.h`. Device tree must provide `rockchip,rv1108-cru` plus external parent clocks named in the parent arrays, including USB PHY, HDMI PHY, external GMAC, external I2S, VIP/CIF/HDMI/CVBS inputs, and oscillator inputs.

Consumer integration includes CPUfreq, UART0-2, I2C1-3 plus PMU I2C0, SPI, PWM, timers, watchdogs, GPIO, TSADC/SARADC, crypto, DMAC, DDR controller/monitor, PMU wrapper, USB host/OTG/PHY, SDMMC/SDIO/eMMC/NAND/SFC, GMAC, I2S audio, VOP/HDMI/DSI/CVBS display, CIF/MIPI/ISP camera paths, RGA/IEP, RKVENC/RKVDEC/VPU media engines, DSP, reset consumers, and restart.

## Risks And Edge Cases

- Several clocks have ID `0` because they are internal-only. Accidentally assigning public IDs or changing names can alter provider ABI or debugfs expectations.
- DPLL is likely DDR-sensitive. Adding a rate table or allowing ordinary consumers to retune it could destabilize memory.
- External parents (`usbphy`, `hdmiphy`, `ext_gmac`, `ext_i2s`, `ext_vip`, CIF/HDMI/CVBS inputs) must exist and match DT naming; missing parents can break media, Ethernet, or display.
- The file contains hardware-specific muxes and even an inverter for `pclk_vip`; incorrect polarity or mux values can produce hard-to-debug capture/display failures.
- Several critical paths are protected by both `CLK_IGNORE_UNUSED` and `rv1108_critical_clocks[]`. Removing either can cause late boot failures when unused clocks are disabled.
- MMC drive/sample phase clocks must match the controller tuning registers. Wrong phase register offsets can cause intermittent SD/eMMC data corruption.

## Test Signals

Good test signals include clean boot with `rockchip,rv1108-cru`, no missing parent messages, visible APLL/GPLL/ARM/bus/peripheral clocks in clk summary, and registered reset lines. Functional validation should cover CPU rate changes, serial baud rates, I2S fractional audio, SDMMC/SDIO/eMMC tuning and data transfer, NAND/SFC access, USB, GMAC, display through VOP/HDMI/DSI/CVBS, camera CIF/MIPI/ISP capture, video encode/decode, DSP clocks if used, crypto, ADCs, timers/watchdogs, suspend/resume, soft reset toggles, and restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rv1108.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rv1126.c -->
# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rv1126.c

## Purpose

`clk-rv1126.c` is the Rockchip clock driver for RV1126. It registers both the main CRU and the PMUCRU using a platform-driver probe that dispatches to compatible-specific init functions. The driver describes PLLs, CPU clocking, PMU clocks, main-domain branches, critical-clock protection, soft resets, restart handling, MMC phase clocks, GMAC mode muxing, and GRF/SGRF-backed gates and muxes.

The hardware coverage is broad for a vision SoC: PMU always-on clocks, CPU/core, bus, SCR/JTAG, UART/I2C/SPI/PWM/GPIO/ADC/timer/watchdog/CAN/decompress/OTP, audio I2S/PDM/AUDPWM/codec, VI/ISP/CSI, JPEG/VDEC/IVE, VO/RGA/VOP/DSI/IEP, PHP/storage/USB/GMAC, DDR, top/PHY clocks, and low-power reference clocks.

## Important APIs, Types, And Data

- `enum rv1126_pmu_plls` declares the PMU GPLL. `enum rv1126_plls` declares main APLL, DPLL, CPLL, and HPLL.
- `rv1126_pll_rates[]` provides a shared RK3036-style PLL table from 1.608 GHz to 96 MHz. DPLL is registered without a rate table, indicating DDR-sensitive or externally controlled use.
- CPU clock data uses `rv1126_cpuclk_rates[]` and `rv1126_cpuclk_data` to map ARM parent rates to ACLK core and PCLK debug dividers for a single-core ARM clock.
- Parent arrays define PMU 32 kHz and WiFi sources, USB/MIPI PHY references, ARM PLL parents, bus roots, UART fractional parents, I2S/audio fractional and IO parents, VOP pixel fractional parents, GMAC RGMII/RMII/mode parents, and DDR clock parents.
- `rgmii_mux_idx[]` supplies a non-linear mux table for `MUXTBL(RGMII_MODE_CLK, ...)`, mapping logical RGMII mode selections to hardware encodings.
- `rv1126_pmu_pll_clks[]` and `rv1126_pll_clks[]` register PMU and main PLLs separately against their own register spaces.
- PMU fractional mux helpers cover RTC 32 kHz and UART1. Main fractional mux helpers cover UART0/2/3/4/5, I2S0 TX/RX, I2S1, I2S2, AUDPWM, and VOP DCLK.
- `rv1126_clk_pmu_branches[]` describes PMUCRU clocks: PMU bus, RTC/div32k, WiFi, UART1, I2C0/2, PWM0/1, SPI0, GPIO0 debounce, PMUPVTM, USB/MIPI PHY refs, PMU/PMUGRF/PMUSGRF/PMUCRU, chip version OTP, and scrkeygen.
- `rv1126_clk_branches[]` describes the main CRU. It includes USB480M selection, CPU/debug, bus and SGRF gates, UART0/2-5, I2C1/3-5, SPI1, PWM2, GPIO1-4, ADC/timer/spinlock/decompress/CAN/OTP, CPU/NPU TSADC, audio, VO/display, PHP/storage, USB, GMAC, top PHY gates, DDR, and internal NIU fabric gates.
- `rv1126_cru_critical_clocks[]` protects PLLs and important fabric, DDR, USB, JPEG, and VDEC interconnect clocks.
- `struct clk_rv1126_inits` stores a function pointer used as `of_match` data to select `rv1126_clk_init()` or `rv1126_pmu_clk_init()`.

## Control Flow

`builtin_platform_driver_probe(clk_rv1126_driver, clk_rv1126_probe)` registers a built-in platform probe. The match table contains `rockchip,rv1126-cru` and `rockchip,rv1126-pmucru`, each with a pointer to the appropriate init wrapper. `clk_rv1126_probe()` obtains match data with `of_device_get_match_data()`, returns `-EINVAL` if absent, and invokes the selected init function.

`rv1126_pmu_clk_init()` maps the PMUCRU register region, initializes a provider sized to `CLKPMU_NR_CLKS`, registers the PMU GPLL, registers PMU branches, registers two banks of PMU soft resets, and adds the OF provider.

`rv1126_clk_init()` maps the main CRU region, creates a provider sized to `CLK_NR_CLKS`, registers APLL/DPLL/CPLL/HPLL, registers the ARM clock, registers main branches, registers 15 soft reset banks, registers restart at `RV1126_GLB_SRST_FST`, protects critical clocks, and adds the OF provider.

Runtime behavior is framework-driven: CCF consumers request rates or enables, Rockchip ops program mux/divider/fractional/gate/GRF fields, MMC phase ops program sample/drive registers, reset consumers assert/deassert registered soft resets, and restart uses the Rockchip restart notifier.

## State And Persistence Behavior

The driver keeps no heap or file-static runtime state. The platform device match data selects an init path, and after init the CCF and reset frameworks own software state. Mutable hardware state is held in PMUCRU and CRU PLL, mux, divider, gate, fractional divider, GRF mux, SGRF gate, MMC phase, soft reset, and global reset registers.

Important behavior:

- PMUCRU and CRU are independent providers with separate register mappings and clock ID spaces.
- Critical clocks include PLLs and bus roots that must survive unused-clock cleanup.
- GRF-backed muxes and SGRF-backed gates mean not all clock control bits live in the CRU register block; syscon/GRF access through Rockchip helpers must be available.
- DPLL has no rate table, matching its DDR clock role.
- GMAC clocking has multiple mode-dependent paths: internal divider, external RGMII inputs, RGMII/RMII dividers, non-linear RGMII mux encoding, and no-reparent constraints on the final GMAC source/tx-rx muxes.

## Dependencies And Integration Points

The file depends on platform devices, OF matching, OF address mapping, Linux CCF, Rockchip clock/reset helpers, GRF/SGRF helper support in `clk.h`, and `dt-bindings/clock/rockchip,rv1126-cru.h`. Device tree must provide both main `rockchip,rv1126-cru` and PMU `rockchip,rv1126-pmucru` nodes where needed, plus external parent clocks such as oscillator inputs, USB480M PHY, WiFi oscillator, I2S MCLK inputs, JTAG IO clock, GMAC RGMII input clocks, and MIPI/USB PHY reference inputs.

Consumers include CPUfreq, PMU firmware, UART/I2C/SPI/PWM/GPIO/timer/watchdog/CAN/ADC, audio I2S/PDM/AUDPWM/codec, SDMMC/SDIO/eMMC/NAND/SFC, USB host/OTG/PHY, GMAC, display VOP/DSI/IEP/RGA, camera and ISP/CSI, JPEG/VDEC/IVE media engines, DDR controller/monitor, OTP/scrkeygen, reset consumers, and restart.

## Risks And Edge Cases

- Main CRU and PMUCRU must both bind when consumers reference clocks across domains. Missing PMUCRU can break UART1, PMU GPIO, WiFi, PHY refs, and 32 kHz clocks.
- `rv1126_pmu_clk_init()` returns after failed `rockchip_clk_init()` without `iounmap(reg_base)`, unlike the main CRU path. That is an init-time leak on failure.
- GRF and SGRF-backed controls (`MUXGRF`, `SGRF_GATE`) rely on correct syscon integration and register offsets such as `RV1126_GRF_IOFUNC_CON1`; bad GRF access can break GMAC or security-owned gates.
- GMAC mode selection is complex. Wrong mux table indices, external clock parents, or no-reparent constraints can break RGMII/RMII timing.
- DPLL/DDR clocks are exposed but not normally rate-programmable. Treating them like ordinary PLLs risks memory instability.
- Critical-clock names must match registered clock names. A typo silently weakens protection against unused-clock cleanup.
- Fractional audio/UART/VOP clocks are sensitive to parent rates and reparenting rules. Incorrect parent choice can cause serial baud drift, audio sample-rate error, or display pixel-clock failure.

## Test Signals

Validation should show both `rockchip,rv1126-cru` and `rockchip,rv1126-pmucru` probing successfully, populated clock summaries for both providers, protected critical clocks, and registered main/PMU reset controllers. Rate tests should cover ARM clock changes, UART0-5 and UART1 PMU fractional rates, I2S/PDM/AUDPWM audio rates, VOP DCLK fractional rates, SDMMC/SDIO/eMMC phases, GMAC RGMII/RMII modes, USB480M selection, 32 kHz/RTC sources, and DDR clock readout. Functional tests should exercise storage, USB, GMAC, camera/ISP/CSI, JPEG/VDEC/IVE, display, audio, serial, PMU wake clocks, GPIO debounce, ADCs, timers/watchdogs, OTP/security gates, soft resets, suspend/resume, and restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rv1126.c -->
