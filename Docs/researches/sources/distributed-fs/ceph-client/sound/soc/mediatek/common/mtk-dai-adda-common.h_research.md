# sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-dai-adda-common.h

## Purpose
Declares MediaTek ADDA rate-code enums and conversion helpers.

## Important APIs, Types, And Functions
Defines `enum adda_input_mode_rate`, `enum adda_voice_mode_rate`, and `enum adda_rxif_delay_data`, plus prototypes for `mtk_adda_dl_rate_transform()` and `mtk_adda_ul_rate_transform()`.

## Control Flow, State, And Persistence
No control flow or state. The enum constants are shared ABI between common helpers and SoC-specific register programming.

## Dependencies And Integration Points
Forward-declares `struct mtk_base_afe` and is included by ADDA DAI implementations.

## Risks And Test Signals
Risks are enum value drift relative to hardware manuals and duplicate delay enum values that must be intentional for SoC compatibility. Test signals are compile coverage and register-value validation for ADDA paths.
