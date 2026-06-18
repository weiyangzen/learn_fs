# sources/distributed-fs/ceph-client/sound/soc/mxs/mxs-sgtl5000.c

Purpose: implements the MXS board machine driver for SGTL5000 codec connections over SAIF.

Important APIs/types/functions: `mxs_sgtl5000_hw_params` chooses MCLK ratio and sets codec/CPU clocks. DAI links are declared for playback and capture with SGTL5000 and SAIF components. Probe parses DT codec/cpu phandles and registers `snd_soc_card`.

Control flow: on hw_params, the driver uses 256fs MCLK at 96 kHz and 512fs otherwise, sets SGTL5000 sysclk, sets SAIF sysclk/MCLK, and relies on the SAIF DAI for clock generation. Probe fills link component OF nodes from DT and registers the card; remove clears card drvdata.

State and persistence: card/link structures are static, with runtime OF-node assignments during probe. Clock state lives in SGTL5000 and SAIF drivers.

Dependencies and integration: depends on `mxs-saif` exported MCLK behavior, SGTL5000 codec driver, DT bindings for `audio-codec`/`cpu-dai`, DAPM headphone/speaker/mic widgets, and ASoC card registration.

Risks: static card/link data can be problematic if multiple instances are probed. Clock ratio assumptions are SGTL5000-specific. Missing DT phandles fail probe.

Test signals: card registration on MXS boards, 44.1/48/96 kHz playback with correct MCLK, DAPM widget visibility, and probe deferral behavior when codec or CPU DAI is not ready.
