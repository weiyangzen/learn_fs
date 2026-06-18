# sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_hdmi_common.c

## Purpose
Provides shared infrastructure for MediaTek HDMI v1 and v2 drivers: ACR N/CTS calculation, audio parameter validation/storage, ELD and plugged-callback helpers, bridge mode storage, DT parsing, CEC/DDC discovery, audio codec registration, bridge initialization, and common probe allocation.

## Important APIs, types, and functions
- `mtk_hdmi_get_ncts()` computes HDMI recommended N and expected CTS.
- `mtk_hdmi_audio_params()` validates codec DAI params and stores normalized `struct hdmi_audio_param`.
- `mtk_hdmi_audio_get_eld()` and `mtk_hdmi_audio_set_plugged_cb()` serve HDMI codec callbacks.
- `mtk_hdmi_bridge_mode_fixup()` and `mtk_hdmi_bridge_mode_set()` are shared bridge callbacks.
- `mtk_hdmi_common_probe()` is the exported common probe entry for both hardware versions.

## Control flow
N/CTS calculation first selects HDMI-spec recommended N for common TMDS clocks and sample families, then computes CTS from exact 1000/1001-adjusted pixel-clock values where needed. Audio params accept only 2/4/6/8 channels, common sample rates, and I2S or SPDIF, then populate the shared audio state used by hardware-specific code. DT parsing obtains all version-specific clocks, IRQ, register regmap, optional next bridge, DDC adapter from the connector's `ddc-i2c-bus`, optional CEC device/syscon, and device-managed put actions. Common probe allocates a bridge-backed `struct mtk_hdmi`, stores config, parses DT, gets the PHY, initializes the plugged-callback mutex, registers an `hdmi-codec` platform device, fills bridge operations and HDMI infoframe capabilities, and adds the bridge.

## State and persistence
Shared persistent state is `struct mtk_hdmi`, including mode, audio params, callback pointers, DDC/CEC references, clocks, PHY, register maps, current connector, and bridge metadata. Audio codec platform device lifetime is tied to devm cleanup. The function stores bridge mode and audio params for later hardware-specific programming.

## Dependencies and integration points
Depends on DRM HDMI/EDID/bridge helpers, Linux HDMI codec framework, OF graph and phandle parsing, I2C adapter lookup, regmap/syscon, PHY, platform devices, and version-specific `mtk_hdmi_conf` supplied as OF match data. It is the shared ABI used by `mtk_hdmi.c` and `mtk_hdmi_v2.c`.

## Risks
The DDC adapter and external bridge are probe-order sensitive. CEC lookup is optional in common code but mandatory for v1. The registered codec data advertises `max_i2s_channels = 2` even though shared audio params accept up to 8 channels, so hardware-specific expectations need care. `mtk_hdmi_audio_get_eld()` depends on `curr_conn` being valid when `enabled`.

## Test signals
Signals include successful bridge registration, audio codec platform device creation, DDC adapter discovery, optional CEC unavailable log, mode storage logs, accepted/rejected audio params, and correct N/CTS values for 25.175/74.176/148.352/296.703 MHz and common sample rates.
