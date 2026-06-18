# sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-soc-card.h

## Purpose
Defines shared MediaTek machine-card private data used by common sound-card and SOF helper code.

## Important APIs, Types, And Functions
`struct mtk_soc_card_data` stores optional SOF private data, a list of saved SOF DAI-link fixups, platform card data, optional accessory-detect component, and machine-private data.

## Control Flow, State, And Persistence
No control flow. Instances are allocated during machine-driver probe and attached to `snd_soc_card` drvdata.

## Dependencies And Integration Points
Forward-declares `mtk_platform_card_data` and `mtk_sof_priv`. Used by `mtk-soundcard-driver.c` and `mtk-dsp-sof-common.c`.

## Risks And Test Signals
Risks are uninitialized list fields when SOF helpers are skipped and lifetime coupling between card drvdata and devm allocations. Test signals are probe paths with and without SOF and accessory detection.
