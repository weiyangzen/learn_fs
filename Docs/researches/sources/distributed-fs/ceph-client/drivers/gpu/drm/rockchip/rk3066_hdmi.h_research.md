# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/rk3066_hdmi.h

## Purpose
Defines RK3066 HDMI register offsets, DDC/audio constants, infoframe buffer constants, and bit-field values used by the native RK3066 HDMI driver.

## Important APIs, Types, And Functions
Contains macros for GRF video selection, DDC addresses/rates, audio N values, HDMI system/audio/video/DDC/interrupt/HDCP/status registers, and an enum of field masks/values for power modes, audio input, sample frequency, video format/depth, external timing, AV mute, infoframe selectors, interrupts, HDMI/DVI mode, and HPD/MSENS status.

## Control Flow
No executable control flow. Values are consumed by `rk3066_hdmi.c` MMIO helpers and bridge callbacks.

## State And Persistence
No software state. Constants describe persistent hardware register layout.

## Dependencies And Integration Points
Requires common bit macros from includers. It is tightly coupled to `rk3066_hdmi.c` and the RK3066 HDMI hardware block.

## Risks
The header includes many byte-sized register fields even though MMIO helpers use 32-bit relaxed reads/writes and cast to `u8`. Incorrect masks can silently affect adjacent hardware fields. Some undocumented PHY offsets are intentionally not named here and remain in the C file.

## Test Signals
Successful compile, DDC register programming, interrupt status/mask handling, power mode transitions, and video timing register writes on RK3066 hardware.
