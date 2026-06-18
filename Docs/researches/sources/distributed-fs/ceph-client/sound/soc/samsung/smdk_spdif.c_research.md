# sources/distributed-fs/ceph-client/sound/soc/samsung/smdk_spdif.c

## Purpose
Legacy SMDK S/PDIF machine driver. It creates an S/PDIF DIT codec device and soc-audio card, manually programs the Samsung audio clock hierarchy, and configures S/PDIF clock rates for supported sample rates.

## Important APIs, Types, And Functions
- `set_audio_clock_heirachy()` obtains global clocks (`fout_epll`, `mout_epll`, `sclk_audio`, `sclk_spdif`) and sets their parents.
- `set_audio_clock_rate()` sets EPLL and S/PDIF source rates.
- `smdk_hw_params()` maps sample rates to PLL frequencies, uses 512fs, and calls `snd_soc_dai_set_sysclk()` with `SND_SOC_SPDIF_INT_MCLK`.
- `smdk_init()` allocates/registers platform devices for `spdif-dit` and `soc-audio`.

## Control Flow
Module init creates the DIT and soc-audio platform devices, associates the static card, and then sets the clock hierarchy. On stream setup, `hw_params` chooses 45.1584 MHz for 44.1 kHz or 49.152 MHz for 32/48/96 kHz families, sets source clocks, and tells the CPU DAI to use internal MCLK.

## State And Persistence
Static platform-device pointers persist until module exit. Clock parent/rate changes persist in the clock framework while the module is active.

## Dependencies And Integration Points
Depends on Samsung S/PDIF DAI, generic `spdif-dit` codec, legacy `soc-audio` platform-device registration, and global clock names.

## Risks And Edge Cases
- Legacy non-DT style with global `clk_get(NULL, ...)` names is fragile on modern systems.
- Function name has typo `heirachy`, harmless but visible.
- Only 32/44.1/48/96 kHz sample rates are accepted.
- Clock parent/rate calls ignore some return values.

## Test Signals
Module load/unload, platform-device creation cleanup on failures, playback at supported rates, unsupported-rate rejection, and clock parent/rate inspection.
