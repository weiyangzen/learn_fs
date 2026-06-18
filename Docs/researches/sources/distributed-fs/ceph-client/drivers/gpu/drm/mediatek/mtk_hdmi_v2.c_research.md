# sources/distributed-fs/ceph-client/drivers/gpu/drm/mediatek/mtk_hdmi_v2.c

## Purpose
Implements MediaTek HDMI v2 transmitter support for MT8188/MT8195-class hardware. It provides DRM bridge and HDMI helper callbacks, HPD/PORD IRQ handling, runtime PM and clock sequencing, SCDC scrambling, color downsampling, infoframe programming, audio codec support, PHY configuration, and debugfs ABIST control.

## Important APIs, types, and functions
- `mtk_v2_hdmi_bridge_funcs` includes attach/detach, HPD enable/disable, EDID, detect, HDMI infoframe write/clear callbacks, TMDS-rate validation, atomic enable/disable sequencing, and debugfs init.
- `mtk_hdmi_v2_enable()` / `mtk_hdmi_v2_disable()` wrap runtime PM and four clocks.
- `mtk_hdmi_v2_change_video_resolution()` programs reset, HPD override, HDCP-related HPD state, packing, deep color, HDMI mode, mute, scrambling, and output format downsampling.
- Audio helpers configure I2S, SPDIF, HBR, DSD, channel maps, N/CTS, channel status, infoframes, mute, reset, and packet drop.
- `mtk_hdmi_v2_isr()` and threaded handler debounce HPD/PORD changes.

## Control flow
Probe populates subdevices, calls common HDMI probe, initializes HPD state, disables and clears all interrupts, requests a threaded IRQ with `IRQ_NOAUTOEN`, and enables runtime PM. Bridge attach chains any downstream bridge, powers the controller, enables HPD/PORD debounce, enables the IRQ, performs an immediate non-debounced status check via the ISR thread helper, then powers down again.

Atomic pre-enable powers the controller/clocks, retrieves connector and connector state, configures HDMI controller and PHY before DPI output starts, powers the PHY, and marks powered. Atomic enable updates DRM HDMI infoframes, unmutes video, notifies the audio codec as plugged, and marks enabled. Disable sends GCP AV mute, mutes video/audio with delays, and post-disable powers the PHY off, notifies codec disconnect, and releases clocks/runtime PM.

HPD IRQ top half disables HPD/PORD interrupts, clears status, and wakes the thread. The thread debounces 30 ms, reads HPD/PORD pins, updates `hdmi->hpd`, notifies DRM hotplug if changed, and reenables interrupts. HPD enable/disable bridge ops power the controller solely to manage IRQs.

## State and persistence
Shared `struct mtk_hdmi` stores current mode, current connector, HPD enum, powered/enabled flags, audio params, callback state, clocks, PHY, IRQ, and regmap. Hardware state includes TOP/AIP/infoframe/HDCP/DDC/TX config registers, SCDC sink state for scrambling, PHY link rate, and debugfs ABIST enablement.

## Dependencies and integration points
Depends on `mtk_hdmi_common`, HDMI v2 register definitions, DRM HDMI state/helper APIs, SCDC helpers, DRM EDID, runtime PM, Linux PHY, debugfs, clocks, threaded IRQs, and parent DDC subdevice population. It is the modern MediaTek HDMI bridge and HDMI codec implementation.

## Risks
The enable path is order-sensitive because HDMI must be configured before DPI output. Scrambling toggles both local registers and SCDC sink state and depends on `curr_conn`. HPD/PORD handling deliberately disables interrupts during debounce to avoid storms. Audio channel mapping is complex for PCM, DSD, HBR over I2S/SPDIF, and multichannel layouts. The debugfs write checks an unsigned value for `< 0`, which is ineffective though bounded by `> 1`.

## Test signals
Signals include HPD/PORD interrupt logs and hotplug events, EDID reads through v2 DDC, modes at 27-594 MHz, 340 MHz scrambling threshold and SCDC state, RGB/YUV444/YUV422/YUV420 output, DRM HDMI infoframe updates, audio codec plugged notifications, multichannel/HBR/DSD playback, runtime suspend/resume, and `hdmi_abist` debugfs behavior.
