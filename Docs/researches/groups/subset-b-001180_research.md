# subset-b-001180 sunxi-ng CCU driver research

This grouped report covers the requested Allwinner sunxi-ng clock-control files. Each section preserves the source path in its title and is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun6i-a31.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun6i-a31.c

## Purpose

This file is the Common Clock Framework provider for the Allwinner A31/A31s main CCU. It models PLL roots, CPU/AHB/APB bus clocks, peripheral bus gates, storage and MMC phase clocks, display/media clocks, DRAM and MBUS clocks, GPU clocks, external clock outputs, and reset lines.

## Important APIs, types, and functions

The file is mostly declarative CCU data built with `SUNXI_CCU_*` macros and explicit `struct ccu_div`, `struct ccu_mp`, and `struct ccu_common` objects. Key tables are `sun6i_a31_ccu_clks`, `sun6i_a31_hw_clks`, `sun6i_a31_ccu_resets`, and `sun6i_a31_ccu_desc`. The entry point is `sun6i_a31_ccu_probe()`, bound by compatible `allwinner,sun6i-a31-ccu`, and registered through `module_platform_driver()`.

## Control flow, state, and persistence

Probe maps the CCU register block, forces PLL-Audio-1x divider bits to 1x, forces the MIPI PLL into MIPI mode, forces AHB1 to PLL6/prediv 3, then calls `devm_sunxi_ccu_probe()`. After registration it installs `sun6i_a31_cpu_nb`, a CPU mux notifier that temporarily bypasses CPU clocking to the 24 MHz oscillator during CPU PLL rate changes. Runtime state is hardware register state plus devm-managed CCF/reset registrations; there is no persistent storage beyond register values until reset.

## Dependencies and integration points

The driver depends on the sunxi-ng CCU helpers (`ccu_common`, gate/div/mp/mult/mux/nk/nkm/nkmp/nm/phase/sdm/reset) and binding IDs from `ccu-sun6i-a31.h`. It integrates with DT clock/reset consumers across MMC/NAND/SPI/I2C/UART, USB PHY/OHCI/EHCI/OTG, display back/front ends, LCD, HDMI, MIPI DSI/CSI, CSI, VE, GPU, codec/SPDIF/digital mic/DAUDIO, DRAM, MBUS, and external clock-output users.

## Risks and test signals

Risks concentrate in parent ordering, register bit positions, and the forced pre-probe register writes. The MIPI mode write clears mode-related bits, and mistakes there can break DSI/CSI. Audio PLL SDM intentionally hardcodes the variable divider, so rate-name mismatches are expected but exact audio rates must be checked. Test with A31/A31s boot, `clk_summary`, cpufreq transitions, MMC sampling/output phase tuning, display/HDMI/MIPI paths, USB PHYs, audio sample-rate clocks, and reset-controlled peripheral probe/unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun6i-a31.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun6i-a31.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun6i-a31.h

## Purpose

This private header supplies the internal clock-index namespace for `ccu-sun6i-a31.c`. It bridges public dt-binding clock/reset IDs with non-exported internal IDs needed by the onecell array.

## Important APIs, types, and functions

It includes `dt-bindings/clock/sun6i-a31-ccu.h` and `dt-bindings/reset/sun6i-a31-ccu.h`, then defines internal IDs such as `CLK_PLL_CPU`, `CLK_PLL_AUDIO_BASE`, `CLK_PLL_AUDIO_*`, `CLK_PLL_VIDEO*`, `CLK_PLL_VE`, `CLK_PLL_DDR`, `CLK_PLL_GPU`, `CLK_PLL9`, `CLK_PLL10`, bus clocks `CLK_AXI`/`CLK_AHB1`/`CLK_APB*`, DRAM clocks `CLK_MDFS`/`CLK_SDRAM*`, MBUS clocks, and `CLK_NUMBER`.

## Control flow, state, and persistence

There is no runtime control flow or state. The defines must match the array slots populated by `sun6i_a31_hw_clks`.

## Dependencies and integration points

The header is consumed by the A31 CCU implementation and implicitly by the DT binding contract. Comments identify clock ranges exported by the public binding versus private slots used only inside the driver.

## Risks and test signals

Wrong numeric IDs create miswired OF clock providers even if registration succeeds. `CLK_NUMBER` must remain one past the last exported/internal slot. Test signals are successful boot without missing-provider errors and consumers resolving the expected clock names/IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun6i-a31.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun6i-rtc.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun6i-rtc.c

## Purpose

This file provides a reusable RTC-domain CCU setup for newer Allwinner RTC blocks, currently matched for H616, R329, and A523 style RTC compatibles. It models the internal 16 MHz RC oscillator, derived/calibrated 32 kHz clocks, external 32 kHz gate, RTC 32 kHz mux, 24 MHz-derived 32 kHz gate, and osc32k fanout.

## Important APIs, types, and functions

The main exported function is `sun6i_rtc_ccu_probe(struct device *dev, void __iomem *reg)`, not a standalone platform-driver probe. Key local types and data are `struct sun6i_rtc_match_data`, `sun6i_rtc_ccu_match`, `sun6i_rtc_ccu_desc`, `sun6i_rtc_ccu_hw_clks`, and the custom ops `ccu_iosc_ops` and `ccu_iosc_32k_ops`. Custom callbacks implement IOSC enable/disable/is_enabled, rate recalculation, accuracy reporting, and calibration prepare/unprepare.

## Control flow, state, and persistence

`sun6i_rtc_ccu_probe()` first verifies the device matches the newer RTC variants, selects per-compatible match data, and stores calibration support in the file-scope `have_iosc_calibration`. If an external 32 kHz oscillator is supported, it obtains it by `ext-osc32k` or by old unnamed binding fallback and connects `ext_osc32k_gate_clk` to the parent hardware. If no external oscillator is present, it removes that exported hw slot and narrows the osc32k mux to one parent. H616 can also force `rtc-32k` to a single parent. Finally it fills fanout parent data and calls `devm_sunxi_ccu_probe()`.

## Dependencies and integration points

The file depends on Linux clk APIs, OF matching, `linux/clk/sunxi-ng.h`, and the generic CCU gate/div/mux helpers. It integrates with RTC drivers that map the RTC register block and invoke this helper, with firmware clocks named `hosc`, `losc`, `iosc`, `pll-32k`, and optional `ext-osc32k`, and with consumers needing stable 32 kHz RTC/fanout clocks.

## Risks and test signals

Important risks are global mutable init data and the static `have_iosc_calibration`, which is acceptable for one RTC CCU instance but would be fragile if multiple differing instances were registered. Calibration register interpretation affects reported IOSC rates and 32 kHz accuracy. Test on each compatible with and without external oscillator properties, verify `rtc-32k` remains critical, check clk rates around 32768 Hz, confirm fanout parent selection, and watch for orphaned `ext-osc32k-gate` behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun6i-rtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun6i-rtc.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun6i-rtc.h

## Purpose

This header assigns private clock IDs for the RTC CCU helper beyond the public `sun6i-rtc` dt-binding IDs.

## Important APIs, types, and functions

It includes `dt-bindings/clock/sun6i-rtc.h` and defines `CLK_IOSC_32K`, `CLK_EXT_OSC32K_GATE`, `CLK_OSC24M_32K`, `CLK_RTC_32K`, and `CLK_NUMBER`.

## Control flow, state, and persistence

There is no executable logic. The constants index the `sun6i_rtc_ccu_hw_clks.hws` onecell slots populated in `ccu-sun6i-rtc.c`.

## Dependencies and integration points

The header is internal to the RTC CCU implementation and extends the public binding namespace without changing DT-visible names directly.

## Risks and test signals

The main risk is ID drift between this header and the onecell initializer. Test by verifying all exported RTC clocks resolve and no consumer receives the wrong hw clock for an ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun6i-rtc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-a23-a33.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-a23-a33.h

## Purpose

This shared private header defines the clock index layout used by both the A23 and A33 CCU drivers.

## Important APIs, types, and functions

It includes `dt-bindings/clock/sun8i-a23-a33-ccu.h` and `dt-bindings/reset/sun8i-a23-a33-ccu.h`, then defines internal IDs for PLLs, CPUX, AXI/AHB/APB buses, DRAM/MBUS, and the `CLK_NUMBER` expression based on `CLK_ATS`.

## Control flow, state, and persistence

There is no runtime behavior. The A23 and A33 source files use these constants to initialize their `clk_hw_onecell_data` arrays.

## Dependencies and integration points

The file couples two related SoC drivers to the common DT binding. Comments mark public binding ranges where individual bus and module clocks are exported.

## Risks and test signals

Because this header is shared, adding an A33-only or A23-only clock requires care to keep both onecell tables and `CLK_NUMBER` coherent. Test by booting both compatibles and checking that all binding IDs resolve to the expected clock names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-a23-a33.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-a23.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-a23.c

## Purpose

This is the main CCU provider for the Allwinner A23. It declares CPU, audio, video, VE, DDR, peripheral, GPU, MIPI, HSIC, DE PLLs, CPU/AHB/APB buses, bus gates, MMC/NAND/SPI/I2S/USB clocks, display/camera/media clocks, DRAM gates, MBUS, GPU, and reset lines.

## Important APIs, types, and functions

Important data includes `sun8i_a23_ccu_clks`, fixed-factor audio/peripheral/video clocks, `sun8i_a23_hw_clks`, `sun8i_a23_ccu_resets`, and `sun8i_a23_ccu_desc`. The entry point is `sun8i_a23_ccu_probe()`, bound to `allwinner,sun8i-a23-ccu`.

## Control flow, state, and persistence

Probe maps MMIO, forces the PLL-Audio-1x divider field to 1, clears the PLL-MIPI HDMI-mode bit so the driver can model only MIPI mode, then delegates registration to `devm_sunxi_ccu_probe()`. The registered state is devm-managed CCF/reset objects backed by hardware CCU registers; no software persistence exists.

## Dependencies and integration points

The driver uses the generic sunxi-ng CCU helpers plus the shared A23/A33 binding header. It provides clocks for CPUX, bus fabric, MMC phase tuning, NAND/SPI/I2C/UART, USB HSIC/OHCI/PHY, codec/I2S, MIPI DSI/DPHY, LCD, CSI, VE, display engine front/back ends, DRC, GPU, MBUS, and reset consumers.

## Risks and test signals

Risks include the intentionally simplified audio PLL divider, unsupported MIPI HDMI mode, TODO parent uncertainty for some USB clocks, and mux table encodings for display/camera clocks. Test with A23 boot, `clk_summary`, MMC tuning, display/MIPI, camera, USB HSIC/OHCI, audio rates, and reset-driven peripheral probes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-a23.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-a33.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-a33.c

## Purpose

This is the Allwinner A33 main CCU provider. It is close to the A23 driver but adds A33-specific clocks such as `pll-ddr1`, a `pll-ddr` mux, SAT/SS gates, `dram` as an explicit critical clock, `ac-dig-4x`, and A33-specific reset coverage.

## Important APIs, types, and functions

The major objects are `pll_cpux_clk`, `pll_audio_base_clk`, PLL/video/VE/DDR/peripheral/GPU/MIPI/HSIC/DE clocks, `pll_ddr1_clk`, `pll_ddr_clk`, `sun8i_a33_ccu_clks`, `sun8i_a33_hw_clks`, `sun8i_a33_ccu_resets`, and `sun8i_a33_ccu_desc`. `sun8i_a33_ccu_probe()` is the platform probe, matched by `allwinner,sun8i-a33-ccu`. CPU rate-change helpers are `sun8i_a33_pll_cpu_nb` and `sun8i_a33_cpu_nb`.

## Control flow, state, and persistence

Probe maps registers, forces audio PLL 1x divider to 1, forces PLL-MIPI to MIPI mode, registers the CCU, then registers notifiers to gate/ungate PLL CPU and reparent CPUX to the 24 MHz oscillator during PLL rate changes. Hardware register state and CCF/reset registrations are the only state.

## Dependencies and integration points

The driver depends on the shared A23/A33 header and sunxi-ng CCU primitives. Consumers include CPU/cpufreq, DRAM/MBUS, LCD/DSI/CSI/display engine, VE/GPU, SS crypto/security, NAND/MMC/SPI, USB, I2S/codec, I2C/UART, and reset-controller clients.

## Risks and test signals

Risks include CPU transition notifier correctness, PLL DDR parent switching, critical DRAM/MBUS flags, and mode-forcing writes for audio/MIPI. Test with cpufreq stress, suspend/resume, DRAM-heavy workloads, display/camera/USB/audio paths, and reset assertions for the additional SS/SAT blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-a33.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-a83t.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-a83t.c

## Purpose

This file implements the Allwinner A83T main CCU. It supports a dual-cluster CPU clock tree, a shared PLL lock register, audio/video/VE/DDR/peripheral/GPU/HSIC/DE/video1 PLLs, AHB/APB buses, AHB2 routing, CCI400, media/display/camera/HDMI/MIPI/GPU clocks, and reset lines.

## Important APIs, types, and functions

Key objects include `pll_c0cpux_clk`, `pll_c1cpux_clk`, `pll_audio_clk`, other PLL `ccu_nkmp` instances using `CCU_FEATURE_LOCK_REG`, cluster muxes `c0cpux_clk` and `c1cpux_clk`, `cci400_clk`, `sun8i_a83t_ccu_clks`, `sun8i_a83t_hw_clks`, and `sun8i_a83t_ccu_resets`. `sun8i_a83t_cpu_pll_fixup()` normalizes CPU PLL P dividers, and `sun8i_a83t_ccu_probe()` is the platform probe for `allwinner,sun8i-a83t-ccu`.

## Control flow, state, and persistence

Probe maps MMIO, enforces audio PLL d1/d2 defaults, runs CPU PLL fixups for both clusters so P is not used, and registers the CCU with `devm_sunxi_ccu_probe()`. The fixup lowers N to reset value 17 before clearing P if the P divider was active, avoiding a sudden over-rate. State is contained in CCU registers and registered clock/reset providers.

## Dependencies and integration points

The driver uses ccu mult/nkmp/nm/mp/mux/div/gate/phase/reset helpers and the A83T dt bindings. It integrates with SMP/cpufreq, CCI400, EMAC/EHCI/OHCI/USB HSIC, MMC/NAND/SPI, audio I2S/TDM/SPDIF, display TCON/HDMI/MIPI DSI, CSI/MIPI CSI, VE, GPU, MBUS, and reset consumers.

## Risks and test signals

The largest risks are CPU PLL modeling simplifications, shared lock-register bit mapping, AHB2 predivider behavior, and `usb-hsic-12m` predivider modeling. Test both CPU clusters under cpufreq, validate CCI400 remains critical, boot display/HDMI/MIPI/CSI paths, exercise USB/EMAC/MMC/audio, and inspect `clk_summary` for lock-backed PLLs and expected parent rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-a83t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-a83t.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-a83t.h

## Purpose

This private header defines the internal onecell clock IDs for the A83T CCU driver.

## Important APIs, types, and functions

It includes A83T clock/reset dt bindings and assigns internal IDs for cluster PLLs, audio/video/VE/DDR/GPU/HSIC/video1 PLLs, CPUX outputs, AXI/AHB/APB buses, `CLK_CCI400`, `CLK_DRAM`, `CLK_MBUS`, and `CLK_NUMBER`.

## Control flow, state, and persistence

There is no runtime logic. The constants must match `sun8i_a83t_hw_clks`.

## Dependencies and integration points

The header sits between the public DT binding and the source file’s private clock slots, especially for internal PLLs and non-exported bus clocks.

## Risks and test signals

Index drift can silently expose the wrong clock to DT consumers. Check `CLK_NUMBER` and all explicit onecell assignments whenever binding IDs change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-a83t.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-de2.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-de2.c

## Purpose

This file implements the CCU for Allwinner display-engine 2/3/3.3 clock blocks. It provides mixer, writeback, and rotation bus/module gates plus intermediate dividers, with descriptor variants for A83T, H3, R40, V3s, A64, H5, H6, and H616 DE33.

## Important APIs, types, and functions

Important objects are shared clock definitions `bus_mixer*`, `bus_wb`, `bus_rot`, `mixer*`, `wb`, `rot`, divider variants parented by either `de` or `pll-de`, variant-specific `clk_hw_onecell_data`, reset maps, and `sunxi_ccu_desc` instances. The entry point is `sunxi_de2_clk_probe()`, matched by `sunxi_de2_clk_ids`.

## Control flow, state, and persistence

Probe obtains variant match data, maps registers, gets parent `bus` and `mod` clocks, gets an exclusive reset, enables bus and module clocks, deasserts reset, optionally writes two DE33-specific unknown initialization registers for H616, then registers the CCU. Error paths assert reset and disable prepared clocks. Successful probe deliberately leaves bus/mod clocks enabled so the DE CCU registers remain accessible.

## Dependencies and integration points

The driver depends on `clk`, `reset`, OF matching, and sunxi-ng CCU helpers. It integrates with the main CCU as a consumer of the parent bus/mod clocks and as a provider to DRM/display-engine users for mixers, writeback, and rotation.

## Risks and test signals

Risks include variant matrix mistakes, shared reset-line comments for mixer1/writeback, wrong parent choice between `de` and `pll-de`, and the opaque DE33 initialization writes. Test with DRM display bring-up on each compatible, writeback/rotation where present, reset handling on probe failure, and `clk_summary` showing expected exposed IDs for one-mixer versus two-mixer variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-de2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-de2.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-de2.h

## Purpose

This header defines private intermediate-divider IDs and variant-specific clock counts for the DE2 CCU driver.

## Important APIs, types, and functions

It includes `dt-bindings/clock/sun8i-de2.h` and `dt-bindings/reset/sun8i-de2.h`, defines `CLK_MIXER0_DIV`, `CLK_MIXER1_DIV`, `CLK_WB_DIV`, `CLK_ROT_DIV`, `CLK_NUMBER_WITH_ROT`, and `CLK_NUMBER_WITHOUT_ROT`.

## Control flow, state, and persistence

There is no runtime behavior. The IDs let the driver expose module gates and also keep intermediate dividers in the onecell data.

## Dependencies and integration points

The header is internal to `ccu-sun8i-de2.c`; public display-engine consumers use the dt-binding IDs while the driver uses the private divider slots for parent relationships.

## Risks and test signals

Variant counts must match whether rotation exists. A wrong count can hide valid clocks or expose uninitialized slots. Test by resolving clocks for one-mixer, two-mixer, and rotation-capable display engines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-de2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-h3.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-h3.c

## Purpose

This file provides the main CCU for Allwinner H3 and H5. It models CPU/audio/video/VE/DDR/peripheral/GPU/DE PLLs, bus fabric, AHB2, peripheral bus gates, THS, storage/module clocks, USB gates, H3/H5-specific DRAM clock handling, display/camera/media clocks, MBUS, GPU, and resets.

## Important APIs, types, and functions

Key tables are `sun8i_h3_ccu_clks`, `sun8i_h3_hw_clks`, `sun50i_h5_hw_clks`, `sun8i_h3_ccu_resets`, `sun50i_h5_ccu_resets`, `sun8i_h3_ccu_desc`, and `sun50i_h5_ccu_desc`. The entry point `sun8i_h3_ccu_probe()` selects descriptor data from `of_device_get_match_data()`. CPU rate-change helpers are `sun8i_h3_pll_cpu_nb` and `sun8i_h3_cpu_nb`.

## Control flow, state, and persistence

Probe maps MMIO, forces the audio PLL 1x divider to 1, registers the selected H3/H5 descriptor, then registers a PLL notifier to gate/ungate CPU PLL after rate changes and a mux notifier to reparent CPUX to the 24 MHz oscillator during changes. H3 uses a fixed-factor `dram` clock because its MDFS hardware is broken; H5 uses a real mux/divider. Runtime state is CCU register bits and devm-managed CCF/reset providers.

## Dependencies and integration points

The file depends on sunxi-ng CCU primitives and H3/H5 clock/reset bindings. It feeds cpufreq, DRAM/MBUS, USB PHY/OHCI/EHCI/OTG, EMAC/EPHY, MMC/NAND/SPI/TS/CE, THS, I2C/UART/SCR, I2S/SPDIF/codec, VE, display engine/TCON/TVE/HDMI/deinterlace, CSI, and GPU users.

## Risks and test signals

Important risks are H3 versus H5 onecell differences, the H3 fixed DRAM workaround, reset map differences such as SCR1 on H5, CPU rate-change notifier coverage, and audio PLL simplification. Test both H3 and H5 boot, cpufreq, Ethernet, USB port matrix, MMC tuning, thermal sensor clocking, display/HDMI/TVE, and idle clock disabling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-h3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-h3.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-h3.h

## Purpose

This private header defines the H3/H5 CCU internal clock IDs and variant-specific onecell sizes.

## Important APIs, types, and functions

It includes `dt-bindings/clock/sun8i-h3-ccu.h` and `dt-bindings/reset/sun8i-h3-ccu.h`, defines internal PLL/audio/bus IDs, and provides `CLK_NUMBER_H3` and `CLK_NUMBER_H5`.

## Control flow, state, and persistence

There is no executable code. The constants index the H3 and H5 onecell arrays in `ccu-sun8i-h3.c`.

## Dependencies and integration points

The header must stay aligned with both public binding IDs and the two descriptor variants. Comments indicate which clock families are exported by binding ranges.

## Risks and test signals

The main risk is H3/H5 count or ID mismatch, especially for H5-only `CLK_BUS_SCR1`. Test by resolving all H3 and H5 binding clocks and checking no out-of-range onecell access occurs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-h3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-r.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-r.c

## Purpose

This file implements PRCM/R-domain CCU support for A83T, H3, and A64-class SoCs. It provides AR100, AHB0/APB0, APB0 peripheral gates, IR module clock variants, and reset lines in the low-power domain.

## Important APIs, types, and functions

Key definitions are `ar100_clk`, fixed-factor `ahb0_clk`, `apb0_clk`, APB0 gate clocks, generic `ir_clk`, A83T-specific `a83t_ir_clk`, per-variant `clk_hw_onecell_data`, reset maps, and descriptors. `sun8i_r_ccu_probe()` selects descriptor data by compatible and calls `devm_sunxi_ccu_probe()`.

## Control flow, state, and persistence

Probe only fetches match data, maps MMIO, and registers the selected descriptor. Variant data changes which IR clock implementation and which APB0 gates/resets are exported. State is register-backed clock/reset state in the PRCM block.

## Dependencies and integration points

The file depends on OF/platform APIs and sunxi-ng div/gate/mp/nm/reset helpers. It consumes firmware-named parents such as `losc`, `hosc`, `pll-periph`, and `iosc`, and provides clocks for AR100 firmware/remote processor paths, PIO, IR, timers, RSB, UART, I2C, and TWD consumers.

## Risks and test signals

Risks include variant mismatches in APB0_RSB availability, A83T IR fixed predivider behavior, and parent-name requirements from firmware. Test on all three compatibles, check AR100 rate selection, IR carrier rates, RSB/I2C/UART low-power peripherals, reset assertions, and suspend/resume low-power-domain behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-r.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-r.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-r.h

## Purpose

This header defines internal clock IDs for the sun8i PRCM/R-domain CCU driver.

## Important APIs, types, and functions

It includes `dt-bindings/clock/sun8i-r-ccu.h` and `dt-bindings/reset/sun8i-r-ccu.h`, defines private `CLK_AHB0` and `CLK_APB0`, and sets `CLK_NUMBER` to `CLK_IR + 1`.

## Control flow, state, and persistence

There is no runtime code. The IDs are used by the variant onecell arrays in `ccu-sun8i-r.c`.

## Dependencies and integration points

The header extends the public R-domain binding with internal bus-clock slots that are not exported as standalone binding IDs.

## Risks and test signals

Incorrect IDs can miswire AR100/APB0/peripheral gates. Test with `clk_summary` and DT consumers for all R-domain clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-r.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-r40.c -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-r40.c

## Purpose

This is the large main CCU provider for the Allwinner R40. It models CPU/audio/video/VE/DDR/peripheral/SATA/GPU/MIPI/DE PLLs, 12 MHz derived oscillator, bus fabric, a broad peripheral gate set, storage/module clocks, SATA and GMAC-related clocking, USB, IR, DRAM/MBUS, display/TV/camera/media clocks, external outputs, resets, and a constrained regmap for GMAC configuration.

## Important APIs, types, and functions

Important objects include `pll_cpu_clk`, `pll_audio_base_clk`, video/VE/DDR/peripheral/SATA/GPU/MIPI/DE PLL clocks, `pll_periph0_sata_clk`, `pll_sata_out_clk`, `cpu_clk`, bus gates, module clocks, `sun8i_r40_ccu_clks`, fixed-factor clocks, `sun8i_r40_hw_clks`, `sun8i_r40_ccu_resets`, and `sun8i_r40_ccu_desc`. The probe is `sun8i_r40_ccu_probe()`. CPU transition helpers are `sun8i_r40_pll_cpu_nb` and `sun8i_r40_cpu_nb`. GMAC integration uses `sun8i_r40_ccu_regmap_accessible_reg()` and `sun8i_r40_ccu_regmap_config`.

## Control flow, state, and persistence

Probe maps MMIO, forces PLL-Audio-1x divider to 1, forces PLL-MIPI to MIPI mode, forces OHCI 12 MHz parent selection to 12 MHz divided from 48 MHz, writes the keyed SYS 32 kHz parent selection to use RTC LOSC output, creates a devm regmap exposing only the GMAC config register, registers the CCU, and installs CPU PLL/mux notifiers for rate changes. State is hardware register state, a devm regmap, and CCF/reset providers.

## Dependencies and integration points

The driver depends on sunxi-ng CCU helpers, Linux regmap, and R40 dt bindings. It integrates with cpufreq, GMAC/dwmac-sun8i via restricted regmap, SATA, USB PHY/OHCI/EHCI/OTG, MMC/NAND/SPI/TS/CE, display engine, TCON LCD/TV, TVE/TVD, HDMI, DSI DPHY, CSI0/CSI1, GPU, codec/I2S/AC97/SPDIF, THS/keypad/IR, I2C/UART/CAN/SCR/PS2, DRAM/MBUS, and reset consumers.

## Risks and test signals

Risk areas are numerous: TODO PLL constraint ranges are not fully encoded, MIPI HDMI mode is unsupported, OHCI and SYS 32 kHz force-writes must match board expectations, the GMAC regmap intentionally exposes only one register, and critical DRAM/MBUS/CPU paths must stay enabled. Test with R40 boot, cpufreq transitions, SATA, GMAC, USB port matrix, display/TV/HDMI/CSI, audio clocks, MMC/storage, thermal/keypad/IR, reset consumers, and regmap access from the Ethernet driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-r40.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-r40.h -->
# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-r40.h

## Purpose

This private header defines the internal clock-index layout for the R40 CCU driver.

## Important APIs, types, and functions

It includes `dt-bindings/clock/sun8i-r40-ccu.h` and `dt-bindings/reset/sun8i-r40-ccu.h`, then defines IDs for `CLK_OSC_12M`, PLL CPU/audio/video/VE/DDR/peripheral/SATA/GPU/MIPI/DE clocks, bus clocks, `CLK_DRAM`, and `CLK_NUMBER`.

## Control flow, state, and persistence

There is no executable behavior. The constants map directly to slots in `sun8i_r40_hw_clks`.

## Dependencies and integration points

The header connects public binding IDs to private internal slots used by the R40 CCU source. Comments mark large exported ranges for bus/module/DRAM clocks.

## Risks and test signals

Index mistakes are high impact because the R40 onecell table is large. `CLK_NUMBER` must track `CLK_OUTB + 1`, and all skipped public-exported IDs must remain intentionally handled by the binding. Test by resolving all R40 binding clocks and checking no consumer receives a mismatched parent or rate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun8i-r40.h -->
