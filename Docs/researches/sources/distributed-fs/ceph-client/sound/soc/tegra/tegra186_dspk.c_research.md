# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra186_dspk.c

## Purpose
This ASoC component driver controls the Tegra186 Digital Speaker Controller, which converts PCM input from AHUB/CIF into oversampled PDM output. It exposes a CIF playback DAI, a DAP playback DAI, DAPM routing to a speaker endpoint, mixer controls for FIFO threshold/conversion/OSR/channel selection, and runtime PM with clock/regcache management.

## Important APIs, types, and functions
`struct tegra186_dspk` stores ALSA control values, the DSPK clock, and regmap. Control getters/setters update `rx_fifo_th`, `osr_val`, `lrsel`, `ch_sel`, `mono_to_stereo`, and `stereo_to_mono`. `tegra186_dspk_hw_params()` programs CIF format and thresholds, computes the DSPK clock rate, sets it, and writes core control fields. Runtime PM functions sync the regcache and enable/disable `clk_dspk`. Regmap access callbacks restrict read/write/volatile registers. Probe sets defaults, acquires `dspk` clock, maps registers, creates cached regmap, registers component/DAIs, and enables PM.

## Control flow
Probe initializes default OSR 64, left LR polarity, stereo channel selection, and mono-to-stereo zero fill. Userspace control changes update only driver memory. On `hw_params()` for the DAP DAI, the driver computes audio/client channel counts from channel select, accepts S16 or S24/S32 formats, clamps FIFO threshold to FIFO depth divided by channels minus one, fills `tegra_cif_conf`, calls `tegra_set_cif()`, computes `dspk_clk = (32 << osr_val) * sample_rate * 4`, sets the clock rate, and writes OSR/channel/LR polarity into `TEGRA186_DSPK_CORE_CTRL`. DAPM enables the RX widget through `TEGRA186_DSPK_ENABLE`.

## State and persistence
Regmap is `REGCACHE_FLAT`; runtime suspend marks it dirty and disables the clock, while resume enables the clock, leaves cache-only, and syncs registers. ALSA control values are stored in driver memory and committed during later `hw_params()` calls; they are not immediately written to hardware except through cached defaults and stream setup.

## Dependencies and integration points
The driver depends on `tegra186_dspk.h`, Tegra CIF helper `tegra_set_cif()`, clocks, regmap MMIO, runtime PM, ASoC DAI/DAPM/control infrastructure, and DT compatible `nvidia,tegra186-dspk`. DAPM route names integrate with AHUB/XBAR playback paths.

## Risks and edge cases
Control writes during an active stream may not take effect until the next `hw_params()`. FIFO threshold is silently clamped and persisted back to state. Clock rate calculation can overflow only at much larger rates than supported, but depends on clock provider acceptance. Channel select and conversion controls can create mismatches between ALSA channels and PDM output expectation. There is no capture path.

## Test signals
Exercise playback at 8-48 kHz, S16/S24/S32, mono and stereo, all OSR settings, left/right/stereo channel selection, conversion controls, FIFO threshold clamping, runtime PM resume after controls are changed, and DAPM route activation from XBAR through `SPK`.
