# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/vpg.h

## Purpose

`vpg.h` defines the Video Packet Generator abstraction. VPG hardware emits secondary data packets such as DP/HDMI infoframes or stream metadata from the display pipeline.

## Important APIs, Types, And Functions

The header defines `struct vpg` with context, instance, and a `vpg_funcs` table. The vtable provides packet generation controls, update hooks, and destruction or state management depending on the ASIC implementation.

## Control Flow

Stream encoder and link sequencing code prepares packet contents, then calls VPG operations to enable, update, or stop packet emission. Dynamic metadata paths update packet data while a stream is active.

## State And Persistence Behavior

Packet contents and enable bits persist in VPG/register packet RAM until overwritten or disabled. The software object only persists identity and function dispatch.

## Dependencies And Integration Points

VPG integrates with stream encoders, DP/HDMI info packet paths, HDR metadata, audio/video packet scheduling, and link hardware sequencing.

## Risks And Test Signals

Risks include stale metadata, packet timing issues, NULL implementations on ASICs without VPG separation, and packet RAM corruption. Test signals include HDMI/DP infoframe validation, HDR metadata changes, audio/video packet tests, and blank/unblank transitions.
