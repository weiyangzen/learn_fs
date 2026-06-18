# sources/distributed-fs/ceph-client/sound/soc/mediatek/common/mtk-dai-adda-common.c

## Purpose
Provides common MediaTek ADDA downlink and uplink sample-rate-to-register-code conversion helpers.

## Important APIs, Types, And Functions
Exports `mtk_adda_dl_rate_transform()` and `mtk_adda_ul_rate_transform()`. The downlink helper maps 8 kHz through 192 kHz including 11.025/22.05/44.1 kHz rates. The uplink helper maps 8/16/32/48/96/192 kHz. Unknown rates log and fall back to 48 kHz codes.

## Control Flow, State, And Persistence
Both functions are stateless switch statements. They use `afe->dev` only for logging invalid rates.

## Dependencies And Integration Points
Depends on `mtk-base-afe.h` for the device pointer and `mtk-dai-adda-common.h` enums. SoC ADDA DAI drivers call these when programming codec/AFE rate fields.

## Risks And Test Signals
Risks include silent 48 kHz fallback after an invalid-rate log and mismatched enum values against SoC register definitions. Test signals are rate-programming tests for every supported rate and negative tests for unsupported rates.
