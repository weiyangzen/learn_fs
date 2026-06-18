# sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_hdmi_regs.h

## Purpose
Defines register offsets, bit masks, and secure monitor call ID for the original MediaTek HDMI transmitter IP used by `mtk_hdmi.c`.

## Important APIs, types, and functions
The header covers GRL interrupt, control, status, infoframe, audio, channel status, N/CTS, ABIST, video config, and HDMI system configuration registers. Key masks include audio packet controls, DVI mode, AV mute/unmute, channel swap, I2S format, MCLK ratios, deep color, HDMI output FIFO, analog/HDMI enable, reset, and `MTK_SIP_SET_AUTHORIZED_SECURE_REG`.

## Control flow
This file is declarative. Callers combine these constants with regmap/syscon updates in the v1 HDMI driver.

## State and persistence
No C state is stored. The definitions describe persistent hardware register bits that control video, audio, infoframes, system power, and secure output authorization.

## Dependencies and integration points
Requires `BIT()` and related kernel bit macros from includers. It is tightly coupled to `mtk_hdmi.c` and indirectly to SoC syscon layout through `HDMI_SYS_CFG1C/20`.

## Risks
Incorrect bit definitions can directly break HDMI bring-up, audio routing, AV mute, or secure register access. The header contains a repeated `GRL_INT_MASK` definition with the same value; harmless for preprocessing, but it signals that edits should be checked carefully. Several fields are plain shifted masks rather than `GENMASK()`, so callers must pass already-aligned values or use update masks correctly.

## Test signals
Compile-time use catches missing symbols. Runtime signals are v1 HDMI modeset success, audio packet delivery, DVI mode selection, infoframe enablement, syscon power/reset behavior, and SMC/syscon authorization on TrustZone-enabled and `tz_disabled` SoCs.
