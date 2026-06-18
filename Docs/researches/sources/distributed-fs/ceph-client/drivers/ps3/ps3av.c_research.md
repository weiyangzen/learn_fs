# sources/distributed-fs/ceph-client/drivers/ps3/ps3av.c Research

## Purpose
`ps3av.c` is the PS3 AV settings backend driver. It binds to the PS3 virtual UART AV settings device, initializes the AV backend, discovers hardware ports, chooses an initial video mode, and exports helper APIs used by PS3 framebuffer/audio code to set video mode, audio mode, mute state, and query mode geometry.

## Important APIs, Types, And Functions
The central private state is `struct ps3av`, a singleton containing the VUART device, mutex, asynchronous mode-setting work item, completion, detected region, hardware configuration, AV/optical/head port arrays, active mode, previous mode, and a 512-byte receive buffer. Public exports include `ps3av_do_pkt()`, `ps3av_set_video_mode()`, `ps3av_get_auto_mode()`, `ps3av_get_mode()`, `ps3av_video_mode2res()`, `ps3av_video_mute()`, `ps3av_audio_mute_analog()`, `ps3av_audio_mute()`, and `ps3av_set_audio_mode()`. The `video_mode_table` maps PS3 mode ids to command-level video IDs, color spaces, formats, aspect ratios, and resolution.

## Control Flow
Module init verifies PS3 LV1 firmware and registers `ps3av_driver` as a VUART port driver. Probe enforces a single device, allocates state, initializes work/completion/mutexes, derives region from OS area settings, calls `ps3av_cmd_init()`, fetches hardware config, honors `video=safe`, auto-selects a mode from monitor info, and stores it. Packet I/O runs through `ps3av_do_pkt()`, which validates the command table, serializes with `ps3av->mutex`, sets headers, sends through `ps3av_send_cmd_pkt()`, skips asynchronous event packets, validates the reply CID, and copies reply data back into the caller packet. Video mode changes wait for any previous work completion, update `ps3av_mode`, mute video, schedule `ps3avd`, then the worker disables signals, handles VESA and HDCP options, sends AVB parameter packets, waits for display settling, unmutes, and completes.

## State And Persistence
State is in memory only and is global to the singleton device. Persistent hardware-facing state is the AV backend's programmed mode, mute state, audio parameters, and port routing. `ps3av_mode_old` is used for HDCP mode transitions; completion `done` prevents overlapping asynchronous mode changes. The `safe_mode` module/global flag only affects auto-selection during probe.

## Dependencies And Integration Points
The driver depends on PS3 LV1 firmware, the PS3 VUART layer, `asm/ps3av.h` command layouts, PS3 OS area region values, `video_get_options()`, and `ps3_gpu_mutex` through the command helper path. It integrates with PS3 framebuffer/video users via exported symbols and with PS3 VUART bus matching through `PS3_MATCH_ID_AV_SETTINGS`.

## Risks
Packet reads trust reply `size` enough to read into the fixed receive buffer; correctness depends on firmware obeying `PS3AV_BUF_SIZE` protocol limits. Many helper loops return `-1` instead of preserving specific command errors. Probe logs init failure but continues into hardware config discovery. Mode changes are asynchronous, so callers get success before the display programming finishes. Monitor quirks and preferred-mode ordering can choose conservative or unexpected modes on unusual EDID data.

## Test Signals
Useful validation includes booting on PS3 LV1 firmware with HDMI, DVI, and AVMULTI outputs; exercising `video=safe`; switching all mode ids including VESA and HDCP-off flags; checking that concurrent mode requests serialize; verifying audio mute and mode programming on HDMI, AVMULTI, and SPDIF; and fault-injecting VUART timeouts, event packets, and malformed reply CIDs.
