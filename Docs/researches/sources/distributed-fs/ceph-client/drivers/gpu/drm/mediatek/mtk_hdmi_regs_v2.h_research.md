# sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_hdmi_regs_v2.h

## Purpose
Defines register offsets, bit fields, and DDC command enum for the newer MediaTek HDMI v2 transmitter used by `mtk_hdmi_v2.c` and `mtk_hdmi_ddc_v2.c`.

## Important APIs, types, and functions
The header covers HDMI top config, infoframe packet registers, audio mapping and AIP registers, video mute, downsampling, interrupts, HDCP/HPD/DDC/SCDC registers, SoC-specific TX config offsets, and `enum mtk_hdmi_ddc_v2_cmds`.

## Control flow
No runtime control flow exists in the header. The DDC command enum documents command values used by the DDC engine; all other definitions are consumed by regmap field programming in HDMI v2 and DDC v2 code.

## State and persistence
No C state is stored. The constants describe persistent HDMI controller state: scrambling, HDMI/DVI mode, TMDS packing, ABIST, infoframe enable/repeat bits, audio reset/mute/input format, downsampling, HPD/PORD status, DDC command/status, HDCP overrides, and TX reset/HPD/YUV420 mode.

## Dependencies and integration points
Uses `BIT()`, `GENMASK()`, and `FIELD_PREP/FIELD_GET` conventions from includers. It is shared by the v2 bridge driver and v2 DDC adapter, so it is the key integration contract between display, audio, HPD, DDC, SCDC, and HDCP-adjacent hardware setup.

## Risks
Register definitions are platform-specific and include MT8188 versus MT8195 TX config offsets; a wrong `reg_hdmi_tx_cfg` value can break reset, HPD override, or YUV420 mode. Audio bitfield polarity and packet layout flags are easy to misprogram. DDC command values control bus transactions directly and can hang or abort EDID/SCDC access if wrong.

## Test signals
Runtime signals include HDMI v2 hotplug interrupts, SCDC scrambling toggles, RGB/YUV444/YUV422/YUV420 output, infoframe updates through DRM HDMI helpers, DDC EDID reads, audio startup/mute/reset, ABIST debugfs behavior, and MT8188/MT8195-specific bring-up.
