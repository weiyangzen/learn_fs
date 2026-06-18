<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/soc.h -->
# sources/distributed-fs/ceph-client/include/sound/soc.h

## Purpose
`soc.h` is the umbrella ALSA SoC core header. It defines control-construction macros, card/component registration APIs, PCM/compress runtime contracts, DAI-link and card structures, mixer/enum/private control types, OF parsing helpers, runtime/locking helpers, and includes the DAPM, DPCM, topology, DAI, component, card, and jack sub-APIs.

## Important APIs, types, and functions
The header provides extensive `SOC_*` and `SND_SOC_BYTES*` macros for mixer, enum, TLV, byte, strobe, signed, range, stereo, and custom controls. Registration APIs include `snd_soc_register_card()`, `devm_snd_soc_register_card()`, deferrable card registration, component initialization/registration/unregistration, component lookup, PCM/compress creation, runtime lookup, runtime action, hardware calculation, DAI format setting, frame/BCLK calculations, AC97 helpers, and control helpers. Core types include `snd_soc_pcm_stream`, `snd_soc_ops`, `snd_soc_compr_ops`, `snd_soc_dai_link_component`, `snd_soc_dai_link_ch_map`, `snd_soc_dai_link`, `snd_soc_codec_conf`, `snd_soc_aux_dev`, `snd_soc_card`, `snd_soc_pcm_runtime`, `soc_mixer_control`, `soc_bytes`, `soc_bytes_ext`, `soc_mreg_control`, and `soc_enum`. It also declares OF parsing helpers, DAI lookup/registration helpers, DAI-link macros, DAPM/DPCM mutex wrappers using `_Generic`, PM ops, and debugfs root.

## Control flow
Machine and component drivers use this header to declare controls, DAI links, cards, components, and runtime callbacks. Probe registers components and cards, creates runtimes and PCMs from DAI links, attaches controls and DAPM routes, configures formats/clocks from firmware or machine data, and drives stream callbacks through link/component/DAI layers. Teardown unregisters cards/components and removes runtime state.

## State and persistence behavior
`snd_soc_card` owns card-level runtime state: registered links, runtimes, components, aux devices, controls, DAPM graph/lists, mutexes, debugfs, PM work, PCI SSID, topology shortname, and driver data. `snd_soc_pcm_runtime` owns per-link PCM/compress, DPCM, DAI arrays, delayed close work, components, pmdown time, marks, and flags. Control structs encode register, mask, range, TLV, enum, topology object, and byte-control state. Everything is runtime kernel state.

## Dependencies and integration points
It depends on Linux device, mutex, notifier, OF, workqueue, platform, regmap, ALSA core/control/PCM/compress/AC97, and the ASoC subheaders. It is the common include used across ASoC machine, codec, platform, DSP, topology, DAPM, and DPCM code.

## Risks and test signals
Risks include macro private-value lifetime assumptions, invalid DAI link component arrays, CPU/codec/platform count mismatches, multi-codec channel maps, devm teardown ordering, OF reference leaks, lock misuse across card/DAPM/DPCM mutexes, control min/max/sign/invert mistakes, topology dynamic-object cleanup, and PCM rollback path bugs. Test signals include card/component registration and devm teardown, all control macro variants, OF DAI-link parsing, single and multi-CPU/codec links, no-platform links, DPCM FE/BE links, AC97-enabled/disabled builds, suspend/resume/poweroff, format/BCLK calculations, runtime activation counts, and lockdep coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/soc.h -->
