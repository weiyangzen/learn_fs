# sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-afe-platform-driver.c

## Purpose
Provides the shared MediaTek AFE PCM platform component, including DAI aggregation, DAPM/control aggregation, PCM pointer calculation, and buffer preallocation.

## Important APIs, Types, And Functions
`mtk_afe_combine_sub_dai()` flattens registered sub-DAI driver arrays into `afe->dai_drivers`. `mtk_afe_add_sub_dai_control()` adds controls, widgets, and routes from each sub-DAI. `mtk_afe_pcm_pointer()` reads memif current/base registers and returns the PCM hardware pointer. `mtk_afe_pcm_new()` sets managed buffers. `mtk_afe_pcm_platform` is the exported component driver.

## Control Flow, State, And Persistence
Component probe initializes the regmap on the component and adds sub-DAI controls if the list is initialized. Pointer reads hardware registers per call and falls back to zero on read errors or zero addresses. Buffer sizing comes from `afe->mtk_afe_hardware` and `afe->preallocate_buffers`.

## Dependencies And Integration Points
Depends on `struct mtk_base_afe`, regmap, ASoC component/DAPM APIs, and SoC-specific setup of the `sub_dais` list and memif data.

## Risks And Test Signals
Risks include pointer underflow if current address is below base, no wrap adjustment, uninitialized `sub_dais` checks by raw list pointers, and DAPM route failures not checked. Test signals include pointer accuracy during playback/capture, sub-DAI controls/routes appearing once, and buffer preallocation size validation.
