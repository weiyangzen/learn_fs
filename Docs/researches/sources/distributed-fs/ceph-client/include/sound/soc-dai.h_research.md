<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/soc-dai.h -->
# sources/distributed-fs/ceph-client/include/sound/soc-dai.h

## Purpose
`soc-dai.h` defines the ASoC Digital Audio Interface API: physical audio formats, clocking, TDM, stream mapping, DAI driver callbacks, DAI runtime state, PCM/compressed lifecycle wrappers, and helper accessors.

## Important APIs, types, and functions
Macros define DAI formats, clock gating, signal polarity, provider/consumer roles, possible-format bitmaps, TDM idle modes, standard AC97 formats, and clock directions. APIs configure sysclk, clkdiv, PLL, BCLK ratio, DAI format, TDM slots/idle, channel maps, tristate, prepare, digital mute, stream validity, active counts, PCM lifecycle, compressed lifecycle, and DAI lookup/name. `struct snd_soc_dai_ops` and `struct snd_soc_cdai_ops` hold driver callbacks. `struct snd_soc_dai_driver` declares static capabilities and symmetry requirements. `struct snd_soc_dai` stores runtime streams, component, driver, symmetry state, active counts, DMA data, widgets, and private data.

## Control flow
Machine drivers and ASoC core configure DAIs during card init and `hw_params`, then call startup, hw_params, prepare, trigger, hw_free, and shutdown around streams. The core updates active counts, DAPM widgets, DMA data, mute state, and compressed callbacks through wrapper functions.

## State and persistence behavior
DAI runtime state includes per-direction active counts, TDM masks, DMA data, DAPM widgets, symmetry values, marks for rollback, probe state, and private data. It persists while the component is registered.

## Dependencies and integration points
It depends on ALSA PCM/compress types, ASoC component/runtime/card structures, DAPM widgets, and SoundWire or other bus-specific stream pointers via `set_stream()`/`get_stream()`.

## Risks and test signals
Risks include old master/slave naming confusion, format bitmap priority mistakes, `set_stream()` dereferencing missing ops, trigger callbacks receiving duplicate STOP commands, TDM slot mask translation errors, symmetry enforcement mismatches, and active count underflow. Test signals include all DAI format combinations, auto-selectable format priority, provider/consumer parsing, TDM slots/idle, channel maps, mute-on-trigger behavior, playback/capture-only DAIs, compressed streams, and rollback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/soc-dai.h -->
