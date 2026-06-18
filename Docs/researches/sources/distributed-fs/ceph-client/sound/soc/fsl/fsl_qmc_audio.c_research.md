# sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_qmc_audio.c

## Purpose

`sources/distributed-fs/ceph-client/sound/soc/fsl/fsl_qmc_audio.c` implements an ASoC component and dynamic DAI set for audio over Freescale QUICC Engine/CPM QMC transparent channels. It maps one or more QMC channels into ALSA PCM playback/capture streams, supports interleaved and non-interleaved access models, derives hardware constraints from QMC time-slot masks, submits cyclic QMC read/write transfers, and reports PCM position by completed periods. The source was read as a complete 974-line file.

## Important APIs, Types, and Functions

Private types are `struct qmc_dai`, `struct qmc_audio`, and `struct qmc_dai_prtd`. PCM platform callbacks include `qmc_audio_pcm_new`, `open`, `close`, `hw_params`, `trigger`, `pointer`, and `of_xlate_dai_name`. Transfer helpers include `qmc_audio_pcm_write_submit`, `qmc_audio_pcm_write_complete`, `qmc_audio_pcm_read_submit`, and `qmc_audio_pcm_read_complete`. DAI helpers include `qmc_dai_get_index`, `qmc_dai_get_data`, format/channel hardware rules, interleaved/non-interleaved constraint setup, `qmc_dai_startup`, `qmc_dai_hw_params`, `qmc_dai_trigger`, `qmc_audio_formats`, `qmc_audio_dai_parse`, and `qmc_audio_probe`.

## Control Flow

Probe counts child nodes, allocates matching `qmc_dai` and `snd_soc_dai_driver` arrays, parses each child `reg` and `fsl,qmc-chan` phandles, validates QMC transparent mode, consistent TX/RX slot counts and frame rates, and monotonic timeslot ordering, then builds DAI names, rates, channel ranges, and format masks. Component registration exposes all generated DAIs. PCM open installs hardware limits and allocates per-substream private data. DAI startup attaches the selected QMC DAI and installs interleaved constraints for a single QMC channel or non-interleaved constraints for multiple channels. PCM `hw_params` computes per-channel DMA buffer slices. DAI `hw_params` configures capture QMC max RX buffer size. PCM trigger start submits two initial read/write periods; completion callbacks submit the next period, wrap DMA addresses, update `buffer_ended`, and notify ALSA. DAI trigger starts/stops/resets the QMC channels.

## State and Persistence Behavior

Device state is devm-managed and persists for the platform device. Substream state is allocated on open and freed on close. `qmc_dai` tracks available channels plus currently used TX/RX channel counts. `qmc_dai_prtd` tracks buffer address windows, per-period size, channel count, current DMA address, and completed frame pointer. There is no regmap or runtime PM state in this driver; persistence is runtime memory and QMC channel state.

## Dependencies and Integration Points

The file depends on DMA mapping, OF platform, ALSA ASoC/PCM, and `soc/fsl/qe/qmc.h`. It integrates tightly with the QMC channel API: `qmc_chan_count_phandles`, `devm_qmc_chan_get_byphandles_index`, `qmc_chan_get_info`, `qmc_chan_get_ts_info`, `qmc_chan_set_param`, `qmc_chan_start`, `qmc_chan_stop`, `qmc_chan_reset`, `qmc_chan_write_submit`, and `qmc_chan_read_submit`. The OF compatible is `fsl,qmc-audio`.

## Risks and Edge Cases

The driver assumes completion callbacks can safely resubmit immediately and call `snd_pcm_period_elapsed`. Stop/pause paths do not explicitly cancel already submitted PCM-side transfers; channel stop/reset semantics must handle that. Interleaved versus non-interleaved constraints depend on QMC channel count and exact time-slot math. The source snapshot shows a doubled opening brace in `qmc_dai_constraints_noninterleaved`, a likely compile issue to verify. Little-endian PCM formats are intentionally skipped by `qmc_audio_formats`, so machine-driver expectations must match.

## Test Signals

Build with QMC support, probe a device tree with one and multiple QMC channels, verify generated DAI names through phandle translation, run interleaved and non-interleaved playback/capture, check period pointer progression and wraparound, test unsupported format/channel combinations, and exercise start/stop/suspend-like stop paths while transfers are queued.
