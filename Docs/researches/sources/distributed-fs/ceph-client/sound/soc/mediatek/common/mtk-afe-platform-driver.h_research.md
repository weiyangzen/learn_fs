# sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-afe-platform-driver.h

## Purpose
Declares the shared MediaTek AFE PCM platform component and helper APIs.

## Important APIs, Types, And Functions
Defines `AFE_PCM_NAME` as `"mtk-afe-pcm"`, declares `mtk_afe_pcm_platform`, and exposes `mtk_afe_pcm_pointer()`, `mtk_afe_pcm_new()`, `mtk_afe_combine_sub_dai()`, and `mtk_afe_add_sub_dai_control()`.

## Control Flow, State, And Persistence
No control flow or state. It is the contract used by SoC-specific platform drivers and FE DAI helpers.

## Dependencies And Integration Points
Uses forward declarations for ASoC and MediaTek base structures. `AFE_PCM_NAME` is also used for runtime component lookup by FE helpers.

## Risks And Test Signals
Risks are string-name mismatch with component registration and prototype drift. Test signals are SoC driver compile/link coverage and successful `snd_soc_rtdcom_lookup()` for `AFE_PCM_NAME`.
