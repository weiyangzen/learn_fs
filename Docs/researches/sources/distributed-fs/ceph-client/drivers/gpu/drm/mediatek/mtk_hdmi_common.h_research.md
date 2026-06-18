# sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_hdmi_common.h

## Purpose
Defines the shared MediaTek HDMI data model, audio enums, SoC/version configuration, and common function declarations used by HDMI v1/v2 implementations and their HDMI codec integration.

## Important APIs, types, and functions
- Audio enums describe input type, I2S format, MCLK ratio, many CEA channel layouts, and channel swap modes.
- `struct hdmi_audio_param` wraps HDMI codec parameters plus normalized MediaTek audio choices.
- `struct mtk_hdmi_ver_conf` describes per-IP bridge functions, codec ops, clock names/count, and interlace support.
- `struct mtk_hdmi_conf` describes per-SoC quirks such as TrustZone disablement, CEA-only modes, max clock, and v2 TX config register.
- `struct mtk_hdmi` is the shared runtime object used by all HDMI files.

## Control flow
The header only contains the `hdmi_ctx_from_bridge()` container helper. All other behavior is implemented in common or version-specific C files.

## State and persistence
The central persistent state definition is `struct mtk_hdmi`: bridge, current connector, device/config pointers, PHY, CEC/DDC resources, clocks, current mode, DVI flag, register maps, audio codec platform device, audio params, powered/enabled flags, IRQ/HPD state, plugged callback, and callback mutex.

## Dependencies and integration points
Includes DRM atomic/bridge/CRTC/EDID/print headers, Linux clock/device/HDMI/I2C/regmap/mutex/PHY/platform headers, and `sound/hdmi-codec.h`. It is the common contract between `mtk_hdmi_common.c`, `mtk_hdmi.c`, `mtk_hdmi_v2.c`, and DDC/codec users.

## Risks
This header is broad and exposes many audio channel enum values; semantic mismatch between shared enums and hardware-specific channel maps can cause audio layout bugs. The include guard and function declarations are compile-time critical for both HDMI modules.

## Test signals
Build coverage across v1 and v2 is the primary signal. Runtime coverage is shown by shared audio params, bridge callbacks, HPD callback storage, and the same `struct mtk_hdmi` supporting both HDMI IP versions.
