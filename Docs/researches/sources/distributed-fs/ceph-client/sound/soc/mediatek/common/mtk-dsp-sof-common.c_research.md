# sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-dsp-sof-common.c

## Purpose
Provides MediaTek common helpers for integrating ASoC machine drivers with SOF topology back-end links, fixup callbacks, DAPM route insertion, and devicetree-selected DAI link lists.

## Important APIs, Types, And Functions
Exports `mtk_sof_dai_link_fixup()`, `mtk_sof_card_probe()`, `mtk_sof_card_late_probe()`, and `mtk_sof_dailink_parse_of()`. Private helpers find topology BEs through DPCM relationships and choose the correct stored or SOF-provided `be_hw_params_fixup`.

## Control Flow, State, And Persistence
Card probe initializes a list and gives unnamed BE streams names. Late probe finds the SOF component, backs up existing BE fixups into `soc_card_data->sof_dai_link_list`, replaces BE fixups with a wrapper, adds DAPM routes between normal widgets and SOF DMA widgets, and installs the SOF component fixup on SOF BE links. The parse helper copies requested predeclared DAI links into a device-managed array based on `mediatek,dai-link`.

## Dependencies And Integration Points
Depends on `mtk_soc_card_data`, `mtk_sof_priv`, ASoC DPCM traversal, SOF component name `sof-audio-component`, card prelinks/rtds, and DT properties for DAI-link selection.

## Risks And Test Signals
Risks include name-based link matching, route insertion without duplicate handling, dynamic DAI link arrays copied by value, fallback behavior when no SOF component is present, and fixup wrapping order. Test signals include cards with and without ADSP nodes, playback/capture through SOF DMA, BE hw_params fixup propagation, DAPM route graph inspection, and invalid `mediatek,dai-link` lists.
