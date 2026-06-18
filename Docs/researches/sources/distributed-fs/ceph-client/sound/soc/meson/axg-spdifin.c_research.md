# sources/distributed-fs/ceph-client/sound/soc/meson/axg-spdifin.c

Purpose: Implements the AXG SPDIF input DAI and component controls. It configures input mode-detection timers/thresholds, exposes volatile capture-rate and IEC958 channel-status controls, handles reset sequencing, and registers capture capabilities derived from supported SPDIF modes.

Important APIs and functions: Runtime ops are `axg_spdifin_dai_probe()`, `axg_spdifin_dai_remove()`, and `axg_spdifin_prepare()`. Mode helpers include `axg_spdifin_sample_mode_config()`, `axg_spdifin_mode_timer()`, `axg_spdifin_write_timer()`, and `axg_spdifin_write_threshold()`. Controls include `axg_spdifin_rate_lock_get()`, `axg_spdifin_get_status()`, and IEC958 mask/status info callbacks. `axg_spdifin_get_dai_drv()` dynamically builds the DAI rate mask from mode rates.

Control flow: Probe maps registers, gets pclk/refclk, creates a DAI driver with IEC958 subframe capture format and mode-derived rate bits, and registers the component. DAI probe enables pclk, sets the reference clock, programs a 1 ms base timer, calculates timers and thresholds for seven sample-rate modes, enables refclk, and enables the SPDIFIN block. Prepare applies out/in reset sequencing. Controls read current mode/max-width status to report locked rate and read channel-status bytes by selecting status banks.

State and persistence: `struct axg_spdifin` stores config, regmap, and clocks. Mode thresholds persist in `SPDIFIN_CTRL2/4/5/6`; enable/reset/status selection persist in `SPDIFIN_CTRL0`. Captured channel status is volatile hardware state.

Dependencies and integration points: Depends on regmap MMIO, clock APIs, ALSA IEC958 control conventions, and AXG card capture routes. Compatible `amlogic,axg-spdifin` selects the seven standard rates and a 333333333 Hz reference.

Risks: The source comments document unreliable mode-change IRQ behavior, so the driver deliberately avoids stopping streams based on detected rate changes. Rate-lock is informational and may be zero during no-signal or glitches. Threshold math depends on actual refclk rate after `clk_set_rate()`. Capture accepts only IEC958 subframe format.

Test signals: Capture at 32/44.1/48/88.2/96/176.4/192 kHz, no-signal handling, volatile `Capture Rate Lock`, IEC958 status reads for both channel-status sources, reset prepare sequencing, and clock/regmap traces for mode timers.
