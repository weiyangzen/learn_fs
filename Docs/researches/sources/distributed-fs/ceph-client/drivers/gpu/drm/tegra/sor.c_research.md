# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/sor.c

## Purpose

`sor.c` implements the Tegra Serial Output Resource display encoder driver. It supports HDMI, DisplayPort, and eDP/LVDS-style panel paths across multiple Tegra SoC generations, programming SOR registers, clocks, reset/runtime PM, regulators, display-controller routing, DP AUX/link training, HDMI infoframes/SCDC, HDA audio handoff, debugfs register/CRC dumps, and host1x client registration.

## Important APIs, Types, and Functions

- `struct tegra_sor` is the main device state: host1x client, `tegra_output`, MMIO base, SoC data, clocks, reset, DP AUX/link, HDMI settings, regulators, delayed SCDC work, and HDA audio format.
- `struct tegra_sor_soc` and `struct tegra_sor_regs` describe per-SoC capabilities, register offsets, lane maps, link training tables, and HDMI production settings for Tegra124/132/210/186/194.
- `tegra_sor_readl()` and `tegra_sor_writel()` wrap MMIO and emit `trace_sor_*` tracepoints.
- `tegra_sor_dp_link_apply_training()` and `tegra_sor_dp_link_configure()` implement `drm_dp_link_ops` by programming training pattern, drive current, pre-emphasis, post-cursor, link speed, lane count, framing, and lane power sequencing.
- `tegra_sor_compute_config()` calculates DP transfer-unit parameters, watermarks, and blanking symbols from display mode, bpc, link rate, and lane count; `tegra_sor_apply_config()` writes those values.
- `tegra_sor_hdmi_enable()` / `tegra_sor_hdmi_disable()` and `tegra_sor_dp_enable()` / `tegra_sor_dp_disable()` are the DRM encoder helper enable/disable paths.
- `tegra_sor_connector_*()` implements connector state allocation/duplication, detection, mode probing, debugfs registration, and mode validation.
- `tegra_sor_init()` and `tegra_sor_exit()` integrate the SOR as a host1x client and create DRM connectors/encoders.
- `tegra_sor_probe()` and `tegra_sor_remove()` are platform-driver lifecycle hooks; `tegra_sor_suspend()`/`resume()` handle system sleep.
- `tegra_sor_irq()` handles HDA scratch interrupts and toggles HDMI audio programming through `sor->ops`.

## Control Flow

Probe allocates `struct tegra_sor`, selects SoC data from device tree, duplicates SoC HDMI settings, resolves an optional DPAUX phandle, chooses HDMI or DP operations, parses `nvidia,interface` and optional `nvidia,xbar-cfg`, probes the shared `tegra_output`, enables required regulators, maps MMIO, requests IRQ, resolves reset and clocks, switches the output clock to a safe parent, enables runtime PM, initializes the host1x client, optionally registers a local pad clock implementation for older SoCs, and registers the client.

Host1x initialization creates a DRM connector and simple encoder. HDMI without DPAUX uses HDMI-A/TMDS helpers; DPAUX with a panel becomes eDP; DPAUX without a panel becomes DisplayPort. The init path attaches DPAUX, performs a firmware-handover reset when available, enables module/safe/DP clocks, and leaves the device ready for atomic enable.

HDMI enable resumes the host1x client, selects a safe clock, powers the I/O pad, brings up the SOR PLL and lanes, programs link speed for HDMI 1.x versus HDMI 2.0 clocking, configures XBAR and clocks, sets output rate, writes HDMI control, AVI infoframes, production PLL/lane settings, DC color depth and routing, powers up and attaches SOR, enables DC-to-SOR output, starts HDMI SCDC scrambling for high-TMDS modes, and prepares HDA audio. Disable reverses audio/SCDC, detach, DC routing, SOR power, I/O pad, and host1x runtime state.

DP enable resumes the client, powers pads and DPAUX, probes and filters DP link rates, chooses a link, prepares an eDP panel if present, powers PLLs, configures DP clocking and XBAR, sets DP protocol and link control, calibrates termination, trains the link, powers the sink link, computes/applies TU configuration, programs mode timing, powers up/attaches SOR, enables DC routing, wakes the head, and enables the panel. DP disable powers down panel/link/aux and tears the hardware state down.

## State and Persistence Behavior

The persistent state is `struct tegra_sor`, held as platform driver data and embedded host1x/DRM output state. Runtime mutable state includes connector state (`struct tegra_sor_state` with link speed, pixel clock, bpc), DP link training state, HDMI production settings, SCDC delayed-work state, audio format derived from HDA scratch registers, and debugfs file allocations. Hardware state persists in SOR, DC, DPAUX, PLL, pad, regulator, and clock settings until disable/suspend/reset paths rewrite it.

PM state is split: host1x client runtime suspend/resume asserts/deasserts reset and gates `sor->clk`; DRM encoder enable/disable calls host1x resume/suspend around active output; system suspend disables HDMI supply after output suspend and re-enables it before output resume. The SCDC worker keeps rechecking sink scrambling every five seconds while `scdc_enabled` is true.

## Dependencies and Integration Points

This file depends on host1x client registration, Tegra display-controller helpers (`dc.h`), shared Tegra DRM output helpers, DPAUX/DP helpers, Tegra PMC I/O pad power APIs, reset/clock/regulator frameworks, DRM connector/encoder/atomic helpers, DRM DP/SCDC/EDID/ELD helpers, debugfs, and tracepoints from `trace.h`. Device-tree bindings provide compatible strings, `nvidia,dpaux`, `nvidia,panel`, `nvidia,interface`, clock names, reset, IRQ, MMIO resource, and regulator names.

It integrates with HDA audio through scratch interrupts and ELD buffer writes, with `tegra_hda_parse_format()`, and with display routing through `tegra_dc_*` register access and atomic clock setup.

## Risks and Edge Cases

- HDMI and DP enable paths often log errors and continue rather than unwinding immediately, so partial hardware programming can persist after failures.
- Several register sequences are annotated as not in the TRM or TODO, including timing programming and XBAR/preamble details; regressions may be hardware-specific and hard to cover without boards.
- `tegra_sor_probe()` calls `devm_kmemdup()` even when `soc->num_settings` is zero; the surrounding code assumes this succeeds, so SoCs without HDMI settings should be reviewed for zero-size allocation semantics.
- Busy polling and `while (true)` loops around lane sequence state rely on hardware eventually clearing bits; some paths have no explicit timeout.
- DP TU/watermark math is sensitive to zero/overflow and lane-rate combinations; it clamps high watermarks but malformed modes or link data can still produce invalid programming.
- The HDA IRQ path dereferences `sor->ops->audio_enable`/disable only after checking the function pointers, but audio scratch interrupts on non-audio ops still depend on interrupt mask setup.
- Connector mode validation returns `MODE_OK` unconditionally; bad modes are mostly filtered by link selection/clock setup later.

## Test Signals

Useful tests include device-tree probe permutations for HDMI, DP, eDP, and missing clocks/regulators; KUnit-style tests around `tegra_sor_compute_config()` and connector state duplication; tracepoint inspection for expected register access; DP link training on RBR/HBR/HBR2 sinks; HDMI 2.0 SCDC scrambling persistence; suspend/resume and runtime PM lockdep checks; debugfs `crc`/`regs` active/inactive behavior; and board tests across Tegra124/210/186/194 lane maps and clock providers.
