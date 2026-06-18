# Research Group: subset-b-001158

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-px30.c -->
# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-px30.c

## Purpose
`clk-px30.c` is the Linux common clock framework driver for the Rockchip PX30 CRU and PMUCRU blocks. It describes the SoC clock topology as tables of PLLs, muxes, dividers, fractional clocks, gates, MMC phase clocks, CPU clock operating points, reset controls, and restart hooks. The file is split across the normal CRU and a PMU clock controller because PX30 has always-on/PMU-domain clocks for RTC, Wi-Fi, UART0 PMU, USBPHY reference, MIPI DSI PHY reference, GPIO0 PMU, and related PMU buses.

## Important APIs, Types, And Functions
The core data structures are `rockchip_pll_rate_table`, `rockchip_cpuclk_rate_table`, `rockchip_cpuclk_reg_data`, `rockchip_pll_clock`, and `rockchip_clk_branch`. `px30_pll_rates` enumerates supported RK3328-style PLL rates, while `px30_cpuclk_rates` maps ARM rates to `PX30_CLKSEL0` divider programming for `aclk_core` and `pclk_dbg`. `px30_cpuclk_data` tells the Rockchip CPU clock helper where the core divider and alternate/main mux bits live. Parent arrays declared through `PNAME()` encode mux inputs such as APLL/GPLL for ARM, DPLL/GPLL for DDR, GPLL/CPLL/NPLL/USB480M for peripheral domains, and fractional clock parent sets for PDM, I2S, UARTs, VOP display clocks, RTC32K, and PMU clocks.

The main tables are `px30_pll_clks`, `px30_pmu_pll_clks`, `px30_clk_branches`, and `px30_clk_pmu_branches`. Branch macros include `MUX`, `GATE`, `FACTOR`, `COMPOSITE`, `COMPOSITE_NOMUX`, `COMPOSITE_NODIV`, `COMPOSITE_FRACMUX`, `COMPOSITE_NOMUX_HALFDIV`, `FACTOR_GATE`, `MMC`, and `SGRF_GATE`. `px30_clk_init()` initializes the main CRU and `px30_pmu_clk_init()` initializes the PMUCRU. They are bound through `CLK_OF_DECLARE()` compatibles `rockchip,px30-cru` and `rockchip,px30-pmucru`.

## Control Flow
At early OF clock setup, the matching `CLK_OF_DECLARE()` function maps the register resource with `of_iomap()`, computes the provider clock count with `rockchip_clk_find_max_clk_id() + 1`, and creates a provider with `rockchip_clk_init()`. The main CRU path registers PLLs against GRF status offset `PX30_GRF_SOC_STATUS0`, registers the large branch table, registers the ARM clock using `rockchip_clk_register_armclk()`, protects the critical clock-name list, registers 12 soft-reset registers, registers a restart notifier, and publishes the provider through `rockchip_clk_of_add_provider()`. The PMUCRU path performs the same mapping/provider setup for PMU branches and PMU PLLs, then publishes its provider; it does not register ARM clock, resets, or restart handling.

## State And Persistence Behavior
There is no explicit suspend/resume save area in this file. Persistent state is the CRU/PMUCRU register programming owned by the common clock framework after registration. Critical clocks are protected through `rockchip_clk_protect_critical()` to avoid runtime disable of bus, PMU, GPU NIU, USB, VO/VI, NPLL, UART2, and USB GRF clocks that are required for boot handoff or basic interconnect operation. Gate definitions use hiword-mask writes and `CLK_GATE_SET_TO_DISABLE`, reducing read/modify/write hazards on Rockchip write-mask registers. Some clocks are marked `CLK_IGNORE_UNUSED` where disabling them would break interconnect, debug, DDR, PMU, or always-on behavior.

## Dependencies And Integration Points
The driver depends on the Rockchip clock helper layer in `drivers/clk/rockchip/clk.h`, Linux OF address mapping, common clock provider APIs, and `dt-bindings/clock/px30-cru.h` IDs consumed by device tree nodes and peripheral drivers. It integrates with reset consumers through `rockchip_register_softrst()`, restart handling through `rockchip_register_restart_notifier()`, MMC timing through `MMC()` phase clocks, external clock inputs such as `xin24m`, `xin32k`, `jtag_clkin`, audio MCLK inputs, `gmac_clkin`, and PHY-provided USB480M, and PMU/secure GRF behavior through `SGRF_GATE` for `aclk_dmac`.

## Risks
Most risk is table correctness: wrong parent order, register offset, bit shift, gate polarity, or DT binding ID can silently break a peripheral. The split CRU/PMUCRU topology also risks duplicate or missing providers if device tree compatibles or clock IDs do not match. Fractional audio, UART, RTC32K, and display clocks are sensitive to parent choice and `CLK_SET_RATE_PARENT`; incorrect flags can cause rate requests to perturb shared PLLs. Several entries intentionally use dummy CPLL names or ignore-unused flags; changing them without board-level validation can regress boot, display, networking, or suspend handoff.

## Test Signals
Useful signals include early boot logs for CRU/PMUCRU mapping failures, `/sys/kernel/debug/clk/clk_summary` parent/rate/gate state, CPUfreq transitions across the listed ARM rates, serial console stability on UART2 and PMU UART0, MMC tuning for SDMMC/SDIO/eMMC drive/sample clocks, audio playback/capture for PDM/I2S fractional paths, display mode set for VOPB/VOPL fractional DCLKs, GMAC RMII/RGMII clock selection, reset-controller consumers probing, and watchdog/restart behavior through the registered global reset offset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-px30.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3036.c -->
# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3036.c

## Purpose
`clk-rk3036.c` provides the RK3036 CRU clock driver. It declares PLL rates, CPU clock divider programming, and branch clocks for a compact Rockchip SoC with CPU, DDR, peri, video/display, MMC, audio, UART, SPI, NAND/SFC, GPU, MAC, HDMI, USB PHY, timers, GPIO, I2C, PWM, and watchdog clocks. The file is primarily declarative, but it has one important initialization write that forces the shared UART PLL source to GPLL because the other selectable sources are treated as unstable or unsuitable.

## Important APIs, Types, And Functions
The main tables are `rk3036_pll_rates`, `rk3036_cpuclk_rates`, `rk3036_cpuclk_data`, `rk3036_pll_clks`, and `rk3036_clk_branches`. PLLs are described as RK3036 PLL instances for APLL, DPLL, and GPLL, with GPLL flagged `ROCKCHIP_PLL_SYNC_RATE`. CPU clock data maps the ARM clock mux and divider registers through `RK2928_CLKSEL_CON()` offsets. Parent-name arrays describe ARM selection from APLL/GPLL, bus and DDR source selections, USB480M selection, MMC source selection, audio fractional muxes, UART fractional muxes, MAC external clock selection, and LCDC/HDMI display routing.

The branch table uses Rockchip helper macros to register muxes, composites, gates, dividers, factors, fractional muxes, and MMC phase clocks. `rk3036_uart0_fracmux`, `rk3036_uart1_fracmux`, `rk3036_uart2_fracmux`, `rk3036_i2s_fracmux`, and `rk3036_spdif_fracmux` are standalone `rockchip_clk_branch` descriptors referenced by `COMPOSITE_FRACMUX()` entries. `rk3036_clk_init()` is the sole init function and is registered for `rockchip,rk3036-cru` with `CLK_OF_DECLARE()`.

## Control Flow
The OF init hook maps the CRU registers with `of_iomap()`. Before registering clocks, it writes `RK2928_CLKSEL_CON(13)` with `HIWORD_UPDATE(0x2, 0x3, 10)` so `uart_pll_clk` is sourced from GPLL. It then computes the provider size from `rk3036_clk_branches`, initializes the provider, registers PLLs with GRF status offset `RK3036_GRF_SOC_STATUS0`, registers branches, protects critical clocks, registers the ARM clock, registers 9 soft reset registers, registers the restart notifier, and adds the OF clock provider. Error handling logs mapping or provider-init failures and unmaps the CRU base if provider creation fails.

## State And Persistence Behavior
The only imperative state change outside framework registration is the UART parent selection write during init. After that, state is held in CRU registers managed by common clock operations. The critical list protects `aclk_cpu`, `aclk_peri`, `hclk_peri`, `pclk_peri`, `pclk_ddrupctl`, and `ddrphy`, reflecting the minimum fabric and DDR clocks that must not be disabled. There is no syscore suspend/resume state save in this driver, so suspend correctness depends on the platform preserving CRU state or on firmware/kernel code outside this file.

## Dependencies And Integration Points
The driver depends on `dt-bindings/clock/rk3036-cru.h` for numeric IDs, the Rockchip clock helper layer, common clock framework, OF mapping, and reset/restart helper APIs. Consumer integration includes CPUfreq via `ARMCLK`, reset controller clients via `rockchip_register_softrst()`, serial drivers through `SCLK_UART0..2` and `PCLK_UART0..2`, MMC/SDIO/eMMC through source and phase clocks, display through LCDC/HDMI clocks, Ethernet through MAC reference muxing, and audio through I2S/SPDIF fractional clocks.

## Risks
The UART pre-registration write is a notable boot-order risk: if the register offset or mux encoding is wrong, all UART source clocks can inherit a bad parent before the serial driver probes. MMC phase clock register definitions must match the SoC IO timing controls or storage tuning fails. Because many clocks share the RK2928 register macro family, a copy/paste error in offset or bit position can affect unrelated clock domains. Critical-clock coverage is intentionally narrow; removing ignore-unused from fabric or DDR-related gates can cause late boot hangs when unused-clock cleanup runs.

## Test Signals
Validate by booting with `clk_ignore_unused` both enabled and disabled for comparison, checking `clk_summary` for UART parent `uart_pll_clk -> gpll`, running serial console stress on all UARTs, CPUfreq transitions through the supported RK3036 rates, MMC/SDIO/eMMC enumeration and tuning, I2S/SPDIF rate changes using fractional parents, Ethernet link with internal and external RMII clocking where applicable, display scanout through LCDC/HDMI, reset controller users, and reboot through the RK2928 global soft reset path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3036.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3128.c -->
# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3128.c

## Purpose
`clk-rk3128.c` implements the CRU driver for the RK3126/RK3128 family. It shares a large common clock topology and then appends small SoC-specific branch tables for RK3126 and RK3128. The covered domains include PLLs, ARM clock dividers, DDR PHY, CPU/peripheral buses, crypto, video encode/decode, VIO/display, timers, PVTM, MIPI, MMC, CIF, I2S, SPDIF, UART, GMAC, TSP, NAND, PMU preclock, SFC, GPS, HDMI, and secure/peripheral gates.

## Important APIs, Types, And Functions
The driver uses `rk3128_pll_rates`, `rk3128_cpuclk_rates`, `rk3128_cpuclk_data`, `rk3128_pll_clks`, `common_clk_branches`, `rk3126_clk_branches`, and `rk3128_clk_branches`. It uses RK3036 PLL macros for APLL/DPLL/CPLL/GPLL, plus factor clocks `gpll_div2` and `gpll_div3` that feed many child muxes. Fractional mux descriptors cover I2S0, I2S1, SPDIF, and UART0-2. `rk3128_common_clk_init()` performs shared provider setup and registration, while `rk3126_clk_init()` and `rk3128_clk_init()` add the variant-specific branches and publish the provider. The two compatibles are `rockchip,rk3126-cru` and `rockchip,rk3128-cru`.

## Control Flow
For either compatible, the variant init function first computes the maximum clock ID required by its small SoC table, then calls `rk3128_common_clk_init()`. The common function maps the CRU, computes the common table max ID, initializes a provider sized to `max(common_nr_clks, soc_nr_clks)`, registers PLLs at `RK3128_GRF_SOC_STATUS0`, registers common branches, registers the ARM clock, registers 9 soft reset registers, and installs the restart notifier. The variant init then registers either RK3126-only secure timer/efuse/SGRF gates or RK3128-only SFC/GPS/HDMI gates, protects critical clocks, and adds the OF provider.

## State And Persistence Behavior
There is no explicit runtime state structure beyond the clock provider and no local suspend/resume save path. Clock state persists in CRU registers. Critical clocks protect CPU, HCLK/PCLK CPU, peri buses, VIO bridge, PMU preclock, and timer5. GPLL-derived factor clocks and DDR-related gates are marked to avoid unsafe disable in core paths. Since the same provider is used for both variants, the allocated clock array must include IDs from both the common and selected variant branches; the `max()` sizing in `rk3128_common_clk_init()` is the key state-safety detail.

## Dependencies And Integration Points
The file integrates with `dt-bindings/clock/rk3128-cru.h`, Rockchip clock helpers, OF mapping, common clock APIs, reset controller setup, and restart handling. It provides clock IDs for CPUfreq, DRM/VOP and display components, VPU/HEVC, crypto, MMC/SDIO/eMMC phase and source clocks, audio controllers, UARTs, GMAC, SPI/SFC/NAND storage, timers, GPIO/I2C/PWM/WDT/SARADC, and PMU/secure peripherals. Device tree compatibility selects the variant-specific surface.

## Risks
Variant split is the main risk: using the wrong compatible can omit SFC/GPS/HDMI clocks on RK3128 or secure timer/efuse/SGRF gates on RK3126. The clock provider sizing must remain synchronized with any new branch table IDs. Shared parent arrays containing GPLL dividers and USB480M require exact parent order because mux values are hardware encodings. Fractional audio/UART clocks can affect parent rates due to `CLK_SET_RATE_PARENT`. Critical clock omissions around `hclk_vio_h2p`, PMU, or timers can appear only during late unused-clock cleanup or suspend/resume.

## Test Signals
Check boot logs for one provider under the selected compatible, inspect `clk_summary` for `gpll_div2` and `gpll_div3` fanout, exercise CPUfreq over all listed ARM rates, verify RK3128 SFC/GPS/HDMI clocks only on RK3128 device trees, verify RK3126 secure gates only on RK3126, run MMC tuning and storage IO, audio playback/capture through I2S/SPDIF fractional paths, UART baud-rate changes, GMAC link and external clock parent selection, display mode set, reset users, and reboot through the RK2928 restart path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3128.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3188.c -->
# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3188.c

## Purpose
`clk-rk3188.c` supports multiple related Rockchip CRUs: RK3066A, RK3188A, and RK3188. It provides common clocks plus SoC-specific branch and PLL/CPU-clock definitions. The driver covers ARM/CPU buses, DDR, video encode/decode, LCDC/CIF/IPP/RGA, peripheral buses, USB PHYs, MAC, HSADC, SARADC, SPDIF, UARTs, SMC/SPI/MMC, timers, JTAG, GPIO/I2C/PWM, HDMI, GPU, HSIC, GPS, and variant-specific I2S/display arrangements. It also contains compatibility behavior for RK3188 PLL rate programming.

## Important APIs, Types, And Functions
The file defines `rk3188_pll_rates`, RK3066 and RK3188 CPU clock rate/data tables, two PLL arrays (`rk3066_pll_clks`, `rk3188_pll_clks`), common and variant branch arrays, divider tables (`div_core_peri_t`, `div_aclk_cpu_t`, `div_rk3188_aclk_core_t`), and fractional mux descriptors for HSADC, SPDIF, UART0-3, and I2S. `rk3188_common_clk_init()` handles shared provider setup. `rk3066a_clk_init()`, `rk3188a_clk_init()`, and `rk3188_clk_init()` are registered for `rockchip,rk3066a-cru`, `rockchip,rk3188a-cru`, and `rockchip,rk3188-cru`.

## Control Flow
Variant init starts by computing the selected branch table max ID and calling `rk3188_common_clk_init()`, which maps the CRU, initializes a provider sized for common plus variant clocks, registers common branches, soft resets, and restart notifier. RK3066A then registers RK3066 PLLs, RK3066A branches, the RK3066 CPU clock table, critical clocks, and the OF provider. RK3188A registers RK3188 PLLs and branches, registers the RK3188 ARM clock, then looks up `aclk_cpu_pre` and `gpll`, reparents `aclk_cpu_pre` from APLL to GPLL while preserving its current rate, protects critical clocks, and adds the provider. The `rk3188_clk_init()` wrapper first iterates every RK3188 PLL rate and sets `rate->nb = 1`, then delegates to the RK3188A path.

## State And Persistence Behavior
There is no syscore suspend/resume persistence block. The main local state changes are CRU registration, RK3188 rate-table mutation (`nb = 1` for each PLL rate), and the RK3188A reparenting of `aclk_cpu_pre`. That reparenting deliberately keeps `aclk_cpu_pre` off APLL to reduce CPU-clock coupling complexity while restoring the prior rate after parent change. Critical clocks protect CPU/peripheral/VIO buses and `sclk_mac_lbtest`. Common clock state is otherwise persisted in CRU registers and exposed through the common clock framework.

## Dependencies And Integration Points
The driver depends on `dt-bindings/clock/rk3188-cru.h`, Rockchip clock macros, CCF APIs including `__clk_lookup()`, `clk_get_rate()`, `clk_set_parent()`, and `clk_set_rate()`, OF register mapping, reset registration, and restart notifier registration. Consumers include CPUfreq, display/LCDC and image pipeline blocks, VPU, GPU, USB/HSIC, EMAC, HSADC/SARADC, audio, UARTs, MMC/SDIO/eMMC, SPI/SMC, timers, GPIO/I2C/PWM, HDMI, and GPS depending on the selected SoC.

## Risks
This file has several variant-specific hazards. The RK3188 wrapper mutates a shared static PLL rate table at boot; future reuse must account for that side effect. The `__clk_lookup()` reparenting is name-based and can warn or fail if earlier registration changes clock names. Reparenting `aclk_cpu_pre` while preserving rate depends on valid rate propagation through the selected parents. RK3066A and RK3188 use different CPU divider layouts, so mixing compatibles can break CPU/bus timing. Many branches use RK2928 register macros; offset reuse increases copy/paste risk.

## Test Signals
Boot each compatible separately and check for missing reparent warnings. Inspect `clk_summary` to confirm RK3188 `aclk_cpu_pre` parent is GPLL and rate is preserved. Exercise CPUfreq for both RK3066 and RK3188 tables, display paths for dual LCDC/CIF variants, I2S0/1/2 and SPDIF fractional rates, UART0-3 baud changes, MMC/SDIO/eMMC storage, USB OTG/host and HSIC, EMAC link, HSADC/SARADC, GPU/VPU clocks, reset users, and reboot through RK2928 global reset. For RK3188 specifically, validate PLL rates that require the modified `nb` field.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3188.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3228.c -->
# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3228.c

## Purpose
`clk-rk3228.c` is the CRU clock driver for RK3228. It models PLLs, CPU clock rates, bus dividers, peripheral and media clocks, HDMI PHY and USB480M clock inputs, GMAC/MACPHY clock paths, MMC phase controls, and a broad set of critical interconnect clocks. The SoC surface includes CPU, DDR, video encode/decode, VIO/VOP/RGA/IEP/HDCP, peripherals, UART/audio, GMAC/MACPHY, NAND/SFC/MMC, USB hosts/OTG, GPU, init memory, ROM, DDR monitor, analog codec PHY, and timers.

## Important APIs, Types, And Functions
Key data includes `rk3228_pll_rates`, `rk3228_cpuclk_rates`, `rk3228_cpuclk_data`, `rk3228_pll_clks`, `rk3228_clk_branches`, and fractional mux descriptors for I2S0/1/2, SPDIF, and UART0-2. Parent arrays encode APLL/GPLL/DPLL ARM choices, DPLL/GPLL/APLL DDR choices, CPLL/GPLL/HDMIPHY/USB480M source muxes, HDMI CEC, VOP DCLK selection, external GMAC and MACPHY paths, and audio/UART fractional alternatives. `rk3228_clk_init()` is the only init function and is declared for `rockchip,rk3228-cru`.

## Control Flow
The init hook maps the CRU, sizes the provider from the max branch ID, initializes the Rockchip clock provider, registers RK3036-type PLLs using `RK3228_GRF_SOC_STATUS0`, registers all branch clocks, protects the critical clock list, registers the ARM clock with the RK3228 CPU clock data/rates, registers 9 soft-reset registers, installs the restart notifier using `RK3228_GLB_SRST_FST`, and adds the provider. On mapping or provider initialization failure it logs an error and returns, unmapping only after provider-init failure.

## State And Persistence Behavior
No separate suspend/resume storage is implemented. Clock state lives in CRU registers and CCF structures. The critical list is unusually long and protects CPU/peripheral buses, RGA/IEP/VOP/HDCP/VIO NOCs, USB host arbiters, OTG PMU, GPU NOC, init memory/ROM, DDR controller/monitor/MSCH/PHY paths, analog codec PHY, and VPU/RKVDEC NOCs. This indicates heavy reliance on always-on interconnect clocks and careful unused-clock cleanup behavior. Hiword-mask flags are used for mux/divider/gate writes.

## Dependencies And Integration Points
The driver depends on `dt-bindings/clock/rk3228-cru.h`, Rockchip CCF helpers, OF mapping, reset helpers, and restart notifier support. Consumers include CPUfreq, video/display engines, HDMI/HDCP, VPU/RKVDEC, GPU, audio I2S/SPDIF, UART0-2, MMC/SDIO/eMMC with drive/sample phase clocks, SFC/NAND, USB host/OTG, GMAC and integrated MACPHY paths, analog codec PHY, timers, GPIO/I2C/PWM/SPI/WDT/SARADC, DDR monitor/control blocks, and reset-controller users.

## Risks
The main risks are parent encoding and critical-clock coverage. RK3228 can source several domains from HDMIPHY or USB480M, so mux ordering and `CLK_SET_RATE_PARENT` choices affect display, network, and peripheral stability. GMAC has both external-clock and MACPHY paths; selecting or gating the wrong branch can break Ethernet on only some board designs. The large critical list should not be casually pruned because many protected clocks are NOC/arbitration clocks that may not have direct leaf consumers. MMC phase register mistakes show up as storage tuning or high-speed-mode failures.

## Test Signals
Use `clk_summary` to verify HDMIPHY, USB480M, GMAC/MACPHY, VOP, and DDR/NOC clock parents. Exercise CPUfreq, HDMI/VOP modes, RGA/IEP/HDCP users where available, VPU/RKVDEC decode, GPU, I2S/SPDIF fractional audio, UART0-2, all MMC interfaces with tuning, SFC/NAND, USB host/OTG, GMAC link with internal and external reference configurations, reset controller consumers, late unused-clock cleanup, and restart through the RK3228 global soft reset path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3228.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3288.c -->
# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3288.c

## Purpose
`clk-rk3288.c` is the CRU driver for RK3288 and RK3288W. It describes a large clock tree for a Cortex-A17-class Rockchip SoC and includes explicit suspend/resume register preservation for CRU state lost or modified by maskrom during fastboot wake. It covers APLL/DPLL/CPLL/GPLL/NPLL, ARM and debug dividers, CPU/peripheral/VIO buses, GPU, VPU/video, RGA, crypto, display interfaces, audio, UARTs, MMC, USB PHYs, HSIC, GMAC, EDP/HDMI/VIP/ISP, timers, PMU/alive domains, and variant-specific `hclk_vio` parent selection.

## Important APIs, Types, And Functions
Important definitions include `rk3288_variant`, `rk3288_pll_rates`, `rk3288_cpuclk_rates`, `rk3288_cpuclk_data`, `rk3288_pll_clks`, `rk3288_clk_branches`, `rk3288w_hclkvio_branch`, `rk3288_hclkvio_branch`, and the suspend state arrays `rk3288_saved_cru_reg_ids` / `rk3288_saved_cru_regs`. Fractional mux descriptors cover I2S, SPDIF, SPDIF 8-channel, and UART0-4. `rk3288_clk_suspend()`, `rk3288_clk_resume()`, and `rk3288_clk_shutdown()` manage low-power and restart PLL mode state. `rk3288_common_init()` registers the provider for both variants, with `rk3288_clk_init()` and `rk3288w_clk_init()` bound to their OF compatibles.

## Control Flow
Common init maps the CRU into the file-global `rk3288_cru_base`, initializes the provider, registers PLLs against `RK3288_GRF_SOC_STATUS1`, registers the main branch table, adds the RK3288 or RK3288W `hclk_vio` divider branch depending on compatible, protects critical clocks, registers the ARM clock, registers 12 soft-reset registers, registers a restart notifier with `rk3288_clk_shutdown()` as shutdown callback, registers syscore ops, and publishes the OF provider. During system suspend, syscore saves selected CRU registers, forces `aclk_dmac1` on for deep sleep entry, and switches PLLs other than DPLL to slow mode. During resume it restores saved registers in reverse order using hiword writes. Shutdown also switches PLLs to slow mode before restart.

## State And Persistence Behavior
This file has the strongest persistence behavior in the group. `rk3288_cru_base` and saved register arrays are global state used by syscore callbacks. Saved registers include PLL mode, ARM clock select registers, selected peripheral clock selects, and a gate register for DMAC1. The comments explain that maskrom resets some CRU registers during wake, so the driver proactively saves and restores them. Critical clocks protect CPU/peri/VIO/RGA interconnect, alive/PMU clocks, OTG PMU, and `pclk_rkpwm` because PWM regulators may depend on it during handoff.

## Dependencies And Integration Points
The driver depends on `dt-bindings/clock/rk3288-cru.h`, Rockchip clock helpers, OF mapping, CCF, reset and restart helpers, and `linux/syscore_ops.h`. Consumer integration includes CPUfreq, GPU, VPU/codec, DRM display paths, HDMI/eDP/VIP/ISP, audio I2S/SPDIF including 8-channel SPDIF, UART0-4, MMC/SDIO/eMMC phase clocks, USB/HSIC PHY clocks, GMAC, crypto, timers, PMU/alive GPIO/PWM/WDT/I2C/SPI/SARADC blocks, and suspend/resume infrastructure. The RK3288W compatible changes the `hclk_vio` parent from `aclk_vio0` to `aclk_vio1`.

## Risks
Suspend/resume ordering is high risk: saving the wrong registers, restoring in the wrong order, or losing hiword-mask semantics can break resume clocks. The slow-mode writes intentionally affect multiple PLLs; incorrect masks can destabilize DRAM or CPU. Global `rk3288_cru_base` assumes one CRU instance. Variant-specific `hclk_vio` branch selection can break display/camera/peripheral buses on RK3288W if the wrong compatible is used. Parent names containing `unstable:usbphy480m_src` signal a deliberately constrained or problematic parent; consumers should not depend on it casually.

## Test Signals
Beyond normal boot, test suspend-to-RAM/deep sleep and resume repeatedly with display, storage, network, and serial active. Check that `aclk_dmac1` gate state is restored after resume. Verify restart path reliability. Inspect `clk_summary` before suspend, during late resume if possible, and after resume for PLL modes and key parent restoration. Exercise CPUfreq, GPU/VPU/display, HDMI/eDP/VIP/ISP clocks, UART0-4, MMC tuning, USB/HSIC, GMAC, audio fractional rates, PWM regulator boards, reset-controller users, and both RK3288 and RK3288W compatibles for `hclk_vio` selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3288.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3308.c -->
# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3308.c

## Purpose
`clk-rk3308.c` implements the RK3308 CRU clock driver. RK3308 is audio-heavy, and the file reflects that with extensive PDM, I2S 8-channel TX/RX, I2S 2-channel, SPDIF TX/RX, fractional mux, and external MCLK routing. It also covers CPU, DDR, bus/peripheral fabrics, VOP display, NAND/SFC/MMC, MAC, RTC32K, USBPHY reference, Wi-Fi, UART0-4, timers, ADC/OTP/PWM/CAN/one-wire, and reset/restart support.

## Important APIs, Types, And Functions
The core definitions are `rk3308_pll_rates`, `rk3308_cpuclk_rates`, `rk3308_cpuclk_data`, `rk3308_pll_clks`, and `rk3308_clk_branches`. PLLs include APLL, DPLL, VPLL0, VPLL1, and GPLL. Parent arrays emphasize DPLL/VPLL0/VPLL1 combinations, USB480M/xin24m fallbacks, UART fractional muxes, NAND/MMC divide-by-50 alternatives, MAC external clock selection, DDR standby muxing, RTC32K fractional/divider options, Wi-Fi oscillator/source switching, and the many audio TX/RX muxes. Fractional mux descriptors exist for UART0-4, VOP DCLK, RTC32K, PDM, every I2S TX/RX path, I2S 2-channel paths, and SPDIF TX/RX. `rk3308_clk_init()` is the only init function and is registered for `rockchip,rk3308-cru`.

## Control Flow
The init function maps the CRU, computes the provider clock count from `rk3308_clk_branches`, initializes the provider, registers PLLs with `RK3308_GRF_SOC_STATUS0`, registers all branches, protects critical clocks, registers the ARM clock, registers 10 soft-reset registers, installs the restart notifier for `RK3308_GLB_SRST_FST`, and adds the OF clock provider. The branch table itself declares the clock graph in domain order, with source composites followed by leaf gates and bus gates.

## State And Persistence Behavior
No local suspend/resume save logic is present. Clock state persists through CRU registers and common clock framework state. Critical clocks protect `aclk_bus`, `hclk_bus`, `pclk_bus`, `aclk_peri`, `hclk_peri`, `pclk_peri`, `hclk_audio`, `pclk_audio`, `sclk_ddrc`, and `clk_ddrphy4x`, showing that both the main fabric and audio fabric must survive unused-clock cleanup. Many audio clocks use `CLK_SET_RATE_PARENT`, so rate requests can propagate to VPLL/DPLL parents. Hiword-mask flags are consistently used for mux/divider/gate writes.

## Dependencies And Integration Points
The driver depends on `dt-bindings/clock/rk3308-cru.h`, Rockchip clock helper macros, OF mapping, CCF provider registration, reset controller helpers, and restart notifier support. Consumers include CPUfreq, DDR controller/PHY, ALSA audio controllers for PDM/I2S/SPDIF, display/VOP, NAND/SFC/MMC/SDIO/eMMC including drive/sample phases, MAC, UART0-4, Wi-Fi, USBPHY, RTC, timers, GPIO/I2C/SPI/PWM/ADC/OTP/CAN/one-wire, and reset-controller users.

## Risks
The audio graph is the dominant risk. There are many parallel TX/RX fractional paths and external MCLK parents; a parent-order or mux-width error may affect only one sample-rate direction or one I2S instance. Shared VPLL/DPLL parents mean audio rate changes can interact with other domains if flags are wrong. RTC32K has multiple possible sources, so low-power or wake behavior depends on correct muxing. MAC external/internal clock selection and MMC divide-by-50 alternatives are board- and timing-sensitive. Critical audio bus clocks should not be pruned without full audio validation.

## Test Signals
Check `clk_summary` for VPLL0/VPLL1/DPLL fanout and all audio mux parents. Run playback and capture across PDM, I2S0-3 8-channel TX/RX, I2S0-1 2-channel, SPDIF TX/RX, and external MCLK configurations at common 44.1 kHz and 48 kHz families. Exercise UART0-4 baud changes, VOP display clock changes, MMC/SDIO/eMMC tuning, NAND/SFC, MAC link with external clock, RTC32K source behavior, Wi-Fi and USBPHY reference clocks, CPUfreq, reset users, late unused-clock cleanup, and restart through RK3308 global soft reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-rk3308.c -->
