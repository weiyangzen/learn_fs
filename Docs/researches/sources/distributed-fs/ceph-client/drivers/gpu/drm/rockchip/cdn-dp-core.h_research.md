# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/cdn-dp-core.h

## Purpose
Defines shared Cadence DP core data structures used by the Rockchip Cadence DP bridge and mailbox/register implementation.

## Important APIs, Types, And Functions
Declares `MAX_PHY`, `enum audio_format`, `struct audio_info`, video pixel encoding enum, `struct video_info`, `struct cdn_firmware_header`, `struct cdn_dp_port`, and `struct cdn_dp_device`.

## Control Flow
No executable control flow. It shapes how `cdn-dp-core.c` and `cdn-dp-reg.c` share device, firmware, audio, video, DPCD, and port state.

## State And Persistence
`struct cdn_dp_device` is the main persistent runtime state object, holding DRM objects, work item, mutex, connection flags, firmware pointer/version, MMIO/regmap/clock/reset handles, audio/video state, port list, negotiated link parameters, active port, and DPCD buffer.

## Dependencies And Integration Points
Includes DRM DP, bridge, panel/probe helpers, HDMI codec, and Rockchip DRM driver types. The header is the contract between DP policy code and low-level mailbox programming.

## Risks
The maximum port count is fixed at two. Shared mutable fields such as `max_lanes`, `max_rate`, and `active_port` require external locking discipline; the header itself cannot enforce it.

## Test Signals
Compile coverage of both Cadence DP source files and runtime tests that exercise all fields: multi-port extcon, firmware load, link training, audio, and DPCD reads.
