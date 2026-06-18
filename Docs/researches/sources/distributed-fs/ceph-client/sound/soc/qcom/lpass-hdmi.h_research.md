# sources/distributed-fs/ceph-client/sound/soc/qcom/lpass-hdmi.h

## Purpose
`lpass-hdmi.h` defines the HDMI/DisplayPort-specific register constants, register address helpers, and regmap-field holder types used by the Qualcomm LPASS CPU/platform drivers. It is a hardware interface header, not an executable driver: its job is to centralize HDMI TX control, stream control, metadata, parity, vbit, channel status, and HDMI DMA field descriptions so SoC variant files can describe the register layout and common code can program it.

## Important APIs, types, and constants
The file exposes bit values such as `LPASS_HDMITX_LEGACY_ENABLE`, `LPASS_DP_AUDIO_BITWIDTH16`, `LPASS_DP_AUDIO_BITWIDTH24`, `LPASS_SSTREAM_ENABLE`, `LPASS_MUTE_ENABLE`, `HW_MODE`, `SW_MODE`, and masks for data format, word length, and frequency. Address helpers such as `LPASS_HDMI_TX_CTL_ADDR(v)`, `LPASS_HDMI_TX_CH_LSB_ADDR(v, port)`, and `LPASS_HDMI_TX_DMA_ADDR(v, port)` read offsets and strides from `struct lpass_variant`.

The key holder structs are `struct lpass_sstream_ctl`, `struct lpass_dp_metadata_ctl`, `struct lpass_hdmi_tx_ctl`, `struct lpass_hdmitx_dmactl`, and `struct lpass_vbit_ctrl`; each stores `struct regmap_field *` members allocated elsewhere. The header also declares `asoc_qcom_lpass_hdmi_dai_ops`, which integrates with SoC DAI driver tables in `lpass-sc7180.c` and `lpass-sc7280.c`.

## Control flow and integration
This header has no direct runtime control flow. Its definitions are consumed by LPASS HDMI DAI operations and by SoC variant tables that populate `struct lpass_variant` HDMI fields. `lpass-platform.c` indirectly depends on these definitions through `lpass.h` when it selects DP/HDMI DMA register maps, enables HDMI DMA fields, and handles HDMI-specific IRQ bits such as metadata done, preload request, and deep-audio disable.

## State and persistence behavior
No state is persisted in the header. The structs describe in-memory regmap-field handles stored in `struct lpass_data`; actual state lives in LPASS registers and in the regmap cache used by the platform driver during suspend/resume.

## Dependencies and integration points
The header depends on Linux `regmap` and on `struct lpass_variant` fields defined in `lpass.h`. It is part of the ASoC LPASS register programming path and integrates with HDMI/DP DAI ops, SC7180/SC7280 variant data, and LPASS platform interrupt/DMA handling.

## Risks and test signals
The main risk is register layout drift: wrong offsets, masks, or field ranges will silently program the wrong HDMI TX block fields. Useful tests include HDMI/DP playback on supported SoCs, suspend/resume playback, channel status validation for 16/24-bit audio, and IRQ traces confirming preload/metadone/deep-audio events are cleared correctly.
