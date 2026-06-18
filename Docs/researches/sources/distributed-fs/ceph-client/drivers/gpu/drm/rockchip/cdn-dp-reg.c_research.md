# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/cdn-dp-reg.c

## Purpose
Implements low-level Cadence DP firmware, mailbox, DPCD, link-training, video, and audio register operations used by `cdn-dp-core.c`.

## Important APIs, Types, And Functions
Public functions include `cdn_dp_set_fw_clk()`, `cdn_dp_clock_reset()`, `cdn_dp_load_firmware()`, `cdn_dp_set_firmware_active()`, `cdn_dp_set_host_cap()`, `cdn_dp_event_config()`, `cdn_dp_get_event()`, `cdn_dp_get_hpd_status()`, DPCD read/write, EDID block read, `cdn_dp_train_link()`, `cdn_dp_config_video()`, and audio config/stop/mute helpers. Internal mailbox helpers serialize commands to the firmware.

## Control Flow
Clock reset enables source, PHY, AUX, packet, audio, cipher, and crypto clocks. Firmware load writes IRAM/DRAM, releases reset, polls keep-alive, and records firmware version. Mailbox commands write headers and payload bytes, validate reply headers, and drain mismatched replies. Link training starts firmware training, polls training events, then reads negotiated link status. Video config computes TU/valid-symbol parameters and writes MSA/framer registers. Audio config programs I2S or SPDIF paths and enables audio packets.

## State And Persistence
Updates `dp->fw_version`, `dp->max_rate`, `dp->max_lanes`, and audio/video hardware registers. Most operations persist in the DP controller/firmware until disabled or reset.

## Dependencies And Integration Points
Depends on `cdn-dp-reg.h` register constants, firmware command IDs, DRM DP helpers, MMIO polling, and `struct cdn_dp_device` from `cdn-dp-core.h`.

## Risks
Mailbox timeouts are long and synchronous. The mailbox validation drains unexpected replies, so interleaved callers would be unsafe without the core lock. Audio sample rates/widths assume supported cases; unsupported values can leave `val` paths under-specified. TU calculation rejects modes only after iterative register math.

## Test Signals
Firmware keep-alive, mailbox timeout/reply mismatch, DPCD address validation, EDID block retries, link training event bits, high-bandwidth mode TU calculation, and I2S/SPDIF audio output at all advertised sample rates.
