<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix-anx6345.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix-anx6345.c

## Purpose

`analogix-anx6345.c` implements an I2C DRM bridge driver for the Analogix ANX6345 LVTTL RGB to eDP/DisplayPort transmitter. It manages dual I2C register maps, power sequencing, AUX/DDC access, DP link training, connector creation, EDID retrieval, panel integration, and bridge enable/disable.

## Important APIs, Types, And Functions

- `struct anx6345`: stores DP AUX, bridge, main I2C client, EDID cache, connector, optional panel, regulators, reset GPIO, EDID mutex, two I2C clients/regmaps, chip ID, DPCD cache, and power flag.
- Register-map helpers `anx6345_set_bits()` and `anx6345_clear_bits()`.
- `anx6345_aux_transfer()`: delegates DP AUX transactions to `anx_dp_aux_transfer()`.
- `anx6345_dp_link_training()`: powers link logic, reads DPCD/link bandwidth, configures downspread/enhanced framing/lane count/link rate, writes sink DPCD, starts source training, and polls training completion.
- `anx6345_tx_initialization()`: programs video input depth, PLL/debug/power, forced HPD, lane training controls, and resets AUX.
- `anx6345_poweron()` / `_poweroff()`: sequence reset GPIO, `dvdd12`/`dvdd25` regulators, module power bits, panel prepare/unprepare, and the power flag.
- Bridge/connector funcs: attach/detach, mode_valid, enable/disable, connector get_modes/destroy/atomic funcs.
- Probe/remove: allocate bridge, find panel, get supplies/reset GPIO, create dummy I2C clients and regmaps, power on, validate chip ID, add bridge, and cleanup.

## Control Flow

Probe builds both register maps for DPTX and TX common address windows, powers the chip, reads chip ID/version, and registers the bridge on success. Bridge attach registers DP AUX, initializes and registers an eDP connector, and attaches it to the encoder. Mode enumeration powers the chip temporarily if needed, checks sink count, reads EDID over DP AUX DDC, updates connector EDID, and falls back to panel modes if EDID yields none. Bridge enable enables the panel, starts the transmitter, runs link training, then unmutes/enables DP output. Disable powers down video/link/audio/HDCP modules, disables panel, and powers off regulators.

## State And Persistence Behavior

Software state includes EDID cache protected by `lock`, DPCD cache, chip ID, power flag, registered AUX/connector, panel pointer, regulators/GPIO, and dummy I2C clients. Hardware state persists in ANX6345 power, PLL, video, link-training, lane, downspread, AUX, and DP stream-control registers, plus sink DPCD settings.

## Dependencies And Integration Points

It depends on DRM bridge/connector/EDID/DP helpers, Analogix I2C DPTX/TX common register headers, I2C, regmap, regulators, GPIO, optional panel, OF graph, and DP AUX/DDC infrastructure. It presents a DRM bridge with its own connector; it rejects `DRM_BRIDGE_ATTACH_NO_CONNECTOR`.

## Risks And Edge Cases

The power-on path returns void and logs regulator failures, so callers may continue after partial power failure. `anx6345_start()` overwrites the first `clear_bits()` return by immediately calling TX initialization, losing that specific error. The driver currently hardcodes 6 bpc and rejects clocks above 154 MHz/interlace. It forces HPD/stream validity and only supports DPCD link rates 1.62 and 2.7 Gbps. EDID is cached until remove and may become stale after downstream changes.

## Test Signals

Probe with both possible I2C base addresses, regulator/reset sequencing, chip ID detection, AUX registration, EDID read and panel fallback, DP link training at 1.62/2.7 Gbps, mode rejection for interlace/high clock, enable/disable cycles, hotplug/panel tests, and cleanup of dummy I2C clients/EDID cache are important validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix-anx6345.c -->
