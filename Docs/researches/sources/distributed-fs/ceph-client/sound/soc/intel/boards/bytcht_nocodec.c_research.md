# sources/distributed-fs/ceph-client/sound/soc/intel/boards/bytcht_nocodec.c

## Purpose
This minimal Baytrail/Cherrytrail machine driver exposes SSP2 I2S signals on MinnowBoard Max/Up low-speed connectors without managing a real codec. It creates dummy codec routes and pins so raw I2S playback/capture can be used.

## Important APIs, Types, and Functions
DAPM widgets define a dummy `Mic` and `Speaker`; controls expose pin switches. `codec_fixup()` fixes the back end to 48 kHz stereo S24_LE and programs SSP2 as two-slot 24-bit I2S. `aif1_startup()` constrains FE rates through a `snd_pcm_hw_constraint_list` containing only 48000. The DAI links use dummy codecs for the FE links and the SSP2 BE.

## Control Flow and Integration
The card contains two dynamic FEs (`Audio Port`, `Deep-Buffer Audio Port`) and one no-PCM BE named `SSP2-LowSpeed Connector`, all with `ignore_suspend = 1`. Probe sets the card device, registers it with `devm_snd_soc_register_card()`, and stores the card in platform driver data.

## State, Persistence, and Dependencies
There is no codec state, no jack state, and no external GPIO or clock ownership. Persistent hardware state is limited to CPU DAI format and TDM-slot setup when streams are active. Dependencies are the ASoC core, Atom SST DPCM platform, and DAI names from `sst-atom-controls.h`.

## Risks and Test Signals
Risks are mostly misuse risks: no codec power management, no external amplifier control, and no board-specific electrical safety beyond SSP2 configuration. Test signals include card registration on supported boards, visible 48 kHz FE PCMs, correct SSP2 waveform on the connector, and no suspend blocking because links intentionally ignore suspend.
