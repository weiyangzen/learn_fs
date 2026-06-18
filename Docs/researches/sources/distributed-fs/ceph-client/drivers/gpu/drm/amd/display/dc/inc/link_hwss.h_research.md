# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/link_hwss.h

## Purpose

`link_hwss.h` defines the link hardware sequencing interface used by DC to abstract signal-specific link programming. It separates mandatory stream/audio/link operations from optional DP-specific extension hooks.

## Important APIs, Types, And Functions

`link_hwss_ext` contains optional hooks for hblank minimum symbol width, throttled VCP size, DP link output enable, DP test patterns, DP lane settings, and MST allocation-table updates. `link_hwss` embeds those extensions and requires core hooks for stream encoder setup/reset, stream attributes, link output disable, audio output setup, audio packet enable, and audio packet disable.

## Control Flow

Higher-level link code selects a `link_hwss` implementation based on link/signal/resource characteristics, then invokes mandatory hooks for stream setup and DPMS. DP paths call extension hooks when present for training, test patterns, MST, and bandwidth throttling.

## State And Persistence Behavior

This header defines no state. The selected vtable acts as persistent dispatch for the link operation and programs stream encoder, link encoder, audio, and MST state in hardware.

## Dependencies And Integration Points

It depends on basic DP, signal, graphics object, and fixed-point types and forward-declares DC core objects. It integrates with link service, stream encoder, link encoder, MST allocation, audio, and DP test paths.

## Risks And Test Signals

Risks include missing mandatory hooks, optional hooks used without NULL checks, and selecting a HWSS variant that does not match the link resource. Test signals include DP/HDMI enable/disable, audio packet control, MST allocation changes, DP test patterns, and DP2/HPO versus DIO link sequencing.
