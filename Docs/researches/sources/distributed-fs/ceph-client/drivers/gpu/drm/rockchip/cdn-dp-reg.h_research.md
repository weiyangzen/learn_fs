# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/cdn-dp-reg.h

## Purpose
Defines Cadence DP register addresses, firmware mailbox protocol constants, bit fields, enums, and function prototypes for the Cadence DP register library.

## Important APIs, Types, And Functions
The header covers APB, mailbox, source, PHY, HPD, framer, AUX, HDCP, audio, and stream registers. It defines mailbox module/opcode IDs, firmware states, event bits, link-training bits, video/audio constants, DP lane mapping, link-rate limit, and enums for voltage swing, pre-emphasis, pattern set, color depth, and BT type. Public prototypes match `cdn-dp-reg.c`.

## Control Flow
No runtime control flow. The macros parameterize mailbox commands and MMIO writes in `cdn-dp-reg.c`.

## State And Persistence
No software state is stored. Constants describe persistent hardware/firmware state fields and command payload encodings.

## Dependencies And Integration Points
Includes Linux bitops and references `struct cdn_dp_device`, `struct audio_info`, and video data defined in `cdn-dp-core.h`. It is the shared ABI between the core driver and low-level DP firmware interface.

## Risks
Typos or stale constants can break firmware communication silently. `CDN_DP_MAX_LINK_RATE` caps the source at HBR2 despite possible sink capabilities. Protocol constants are not self-validating and rely on matching the firmware binary.

## Test Signals
Compile coverage and hardware smoke tests for firmware activation, DPCD/EDID reads, link training, video enable, and audio packet programming.
