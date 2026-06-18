# sources/distributed-fs/ceph-client/sound/soc/mediatek/mt8186/mt8186-afe-gpio.h

## Purpose

This header exposes the MT8186 audio GPIO/pinctrl initialization and request API to DAI implementation files.

## Important APIs, Types, and Data

It forward-declares `struct mtk_base_afe` and declares `mt8186_afe_gpio_init(struct device *dev)` plus `mt8186_afe_gpio_request(struct device *dev, bool enable, int dai, int uplink)`. The `dai` argument uses `MT8186_DAI_*` IDs, and `uplink` distinguishes ADDA capture from playback pin groups.

## Control Flow and State

The header has no state. Its functions are implemented in `mt8186-afe-gpio.c`, where global pinctrl state and a mutex are maintained.

## Dependencies and Integration Points

Consumers need Linux `struct device` and boolean definitions through their includes. ADDA, I2S, PCM, and TDM code call the request function in DAPM events or DAI lifecycle hooks.

## Risks

The API accepts raw integer DAI IDs, so invalid IDs are only detected at runtime. The misleading file comment names mt6833 while the include guard and symbols are MT8186-specific.

## Test Signals

Compile coverage verifies function declarations. Runtime validation is board-specific pinctrl activation through the implementation file.
