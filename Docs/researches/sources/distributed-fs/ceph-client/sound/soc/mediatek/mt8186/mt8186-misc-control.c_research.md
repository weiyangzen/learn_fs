# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-misc-control.c

## Purpose

`mt8186-misc-control.c` adds miscellaneous ALSA controls for the MT8186 AFE sine generator. These controls select loopback target, sample rate, amplitude, mute state, and frequency dividers by programming `AFE_SINEGEN_CON0` and `AFE_SINEGEN_CON2`. The complete 252-line file was read.

## Important APIs, Types, and Functions

The public entry point is `mt8186_add_misc_control(struct snd_soc_component *component)`, which calls `snd_soc_add_component_controls()` for `mt8186_afe_sgen_controls[]`.

Static data maps user-facing enum strings to register values: `mt8186_sgen_mode_str[]`, `mt8186_sgen_mode_idx[]`, `mt8186_sgen_rate_str[]`, `mt8186_sgen_rate_idx[]`, and `mt8186_sgen_amp_str[]`. Control callbacks are `mt8186_sgen_get()`, `mt8186_sgen_set()`, `mt8186_sgen_rate_get()`, `mt8186_sgen_rate_set()`, `mt8186_sgen_amplitude_get()`, and `mt8186_sgen_amplitude_set()`.

## Control Flow

When the AFE component registers miscellaneous controls, ALSA exposes `Audio_SineGen_Switch`, `Audio_SineGen_SampleRate`, `Audio_SineGen_Amplitude`, channel mute switches, and frequency divider controls. Mode changes validate the enum index, translate it through `mt8186_sgen_mode_idx[]`, and either enable DAC sine generation with a selected loopback mode or disable sine generation and set the loopback field to `0x3f`. Rate changes translate through `mt8186_sgen_rate_idx[]` and program both channel sine mode fields. Amplitude changes validate against `AMP_DIV_CH1_MASK` and write both channel amplitude fields.

## State and Persistence Behavior

The current mode, rate, and amplitude are cached in `afe_priv->sgen_mode`, `afe_priv->sgen_rate`, and `afe_priv->sgen_amplitude`. Register state is volatile. ALSA controls return 1 when a cached value changed and 0 for no-op updates.

## Dependencies and Integration Points

The file includes Linux delay/DMA/io/regmap headers, ASoC headers, common MediaTek AFE platform headers, and `mt8186-afe-common.h`. The sine generator controls are component-level controls rather than DAI-specific controls. They are useful for hardware bring-up, loopback testing, and path validation across the interconnection matrix.

## Risks and Edge Cases

Some mode table entries map to `-1`, which disables sine generation; user-visible enum labels therefore include values that are not active loopback targets. The code validates enum bounds but does not validate that `mt8186_sgen_rate_idx[rate]` is hardware-valid beyond the table. The amplitude callback compares the enum value against `AMP_DIV_CH1_MASK`, relying on enum ordering matching register encoding. Regmap write errors are ignored.

## Test Signals

After card probe, `amixer` should show all sine-generator controls. Changing `Audio_SineGen_Switch` should update `INNER_LOOP_BACK_MODE` and `DAC_EN`; selecting `OFF` or invalid-mapped entries should disable generation. Rate and amplitude controls should update both channel fields. Audio bring-up can verify audible or captured sine on selected loopback paths and mute/frequency divider controls.
