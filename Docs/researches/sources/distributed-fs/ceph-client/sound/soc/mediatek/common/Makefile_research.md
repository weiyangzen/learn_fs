# sources/distributed-fs/ceph-client/sound/soc/mediatek/common/Makefile

## Purpose
Builds MediaTek shared AFE, SOF, sound-card, ADDA helper, and BTCVSD objects.

## Important APIs, Types, And Functions
`snd-soc-mtk-common-y` combines `mtk-afe-platform-driver.o`, `mtk-afe-fe-dai.o`, `mtk-dsp-sof-common.o`, `mtk-soundcard-driver.o`, and `mtk-dai-adda-common.o`. `mtk-btcvsd.o` is built for `CONFIG_SND_SOC_MTK_BTCVSD`.

## Control Flow, State, And Persistence
No runtime state. This file controls which shared helpers are linked into the common module.

## Dependencies And Integration Points
Integrates with `CONFIG_SND_SOC_MEDIATEK` and `CONFIG_SND_SOC_MTK_BTCVSD`.

## Risks And Test Signals
Risks include common helper exports being unavailable if a SoC driver selects the wrong symbol. Test signals are build/link coverage for all MediaTek ASoC users.
