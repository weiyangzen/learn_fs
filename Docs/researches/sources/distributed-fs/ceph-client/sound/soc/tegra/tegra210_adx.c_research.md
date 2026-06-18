# sources/distributed-fs/ceph-client/sound/soc/tegra/tegra210_adx.c

## Purpose
Implements the Tegra ADX ASoC driver, a 1-to-4 audio demultiplexer that receives one AHUB stream and emits up to four TX streams. It programs CIF endpoints, byte-map RAM, byte-enable masks, DAPM routes, and SoC-specific register maps for Tegra210 and Tegra264.

## APIs, Types, and Functions
The platform API is `tegra210_adx_platform_probe()`, remove, runtime PM callbacks, OF match data, and `module_platform_driver()`. DAI ops are split between input (`tegra210_adx_in_hw_params()`, `tegra210_adx_startup()`) and output (`tegra210_adx_out_hw_params()`). `tegra210_adx_set_audio_cif()` validates channel/format and writes the appropriate CIF. `tegra210_adx_write_map_ram()` pushes cached byte mapping and byte masks into hardware. Mixer controls use `tegra210_adx_get_byte_map()` and `tegra210_adx_put_byte_map()` for byte-map entries 0-63, with Tegra264 adding 64-127 in component probe. Regmap accessors differ between Tegra210 and Tegra264 because the CFG RAM registers move.

## Control Flow, State, and Persistence
Probe selects `tegra210_adx_soc_data`, maps MMIO, initializes cached regmap, allocates `map` and `byte_mask`, adjusts the input DAI channel maximum to SoC capacity, registers one RX CIF plus four TX CIF DAIs, and enables runtime PM. Startup waits for the module to be disabled, asserts soft reset, and waits for reset completion. `hw_params` maps ALSA formats to CIF bit widths and uses `tegra264_set_cif()` when `max_ch` is 32. Byte-map controls keep software state in `adx->map` and `adx->byte_mask`; value 256 means disabled and is represented as a zero byte with the corresponding mask bit clear. Runtime resume syncs regcache and then writes map RAM/masks because RAM contents are not represented solely by normal regcache state.

## Dependencies and Integration
Depends on ASoC DAI/component/DAPM APIs, regmap, runtime PM, platform OF matching, ALSA PCM params, and `tegra_cif`. DAPM routes connect `XBAR-TX` to `RX`, then to `TX1` through `TX4`, and back to AHUB-facing XBAR RX widgets.

## Risks and Test Signals
Risks include the byte-map put callback returning no change when only the stored byte changes but enable mask does not, global mutation of `tegra210_adx_dais[TEGRA_ADX_IN_DAI_ID]`, duplicate macro definitions for `STREAM_ROUTES` and `ADX_ROUTES`, out-of-range byte-map values being accepted as the disabled sentinel, and missed error handling from regmap writes. Test signals include ADX reset timeout logs, correct byte-map persistence after runtime resume, Tegra264 exposure of controls 64-127, valid 1-32 channel CIF setup on Tegra264, and DAPM route activation from one input to each TX output.
