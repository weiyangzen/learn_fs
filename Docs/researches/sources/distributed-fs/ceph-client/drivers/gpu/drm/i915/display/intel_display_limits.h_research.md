# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_limits.h

## Purpose
`intel_display_limits.h` defines stable display topology enumerations and maximum counts used across i915 display code. It fixes IDs for pipes, transcoders, planes, ports, HPD pins, AUX channels, and internal color blocks.

## Important APIs, Types, And Functions
Key enums are `enum pipe`, `enum transcoder`, `enum i9xx_plane_id`, `enum plane_id`, `enum port`, `enum hpd_pin`, `enum aux_ch`, and `enum intel_color_block`. Constants such as `I915_MAX_PIPES`, `I915_MAX_TRANSCODERS`, `I915_MAX_PLANES`, `I915_MAX_PORTS`, `HPD_NUM_PINS`, and `INTEL_CB_MAX` size arrays and masks throughout the display subsystem.

## Control Flow And State
There is no runtime flow. The persistent contract is enum numbering. Pipe values start at `PIPE_A = 0` and remain consecutive. `TRANSCODER_A..D` intentionally match corresponding pipe values for 1:1 mappings. Plane IDs are arranged for register macro compatibility, with cursor after numbered universal planes and legacy aliases (`PLANE_PRIMARY`, `PLANE_SPRITE0`, `PLANE_SPRITE1`) mapped onto universal IDs. Port and AUX aliases model Type-C and Xe_LPD repositioned offsets.

## Dependencies And Integration Points
This header is included by most display headers and implementations, especially iterator macros, runtime masks, IRQ arrays, register offset tables, HPD/AUX routing, and color management. Its values are consumed by hardware register macros and bitmask operations, so changing them has broad impact.

## Risks And Test Signals
The main risk is accidental enum renumbering or max-count mismatch, which can corrupt register selection, bit masks, array indexing, and users of pipe/transcoder 1:1 assumptions. Tests include build-time array size coverage, KMS boot on platforms with fused pipes, Type-C/AUX/HPD hotplug tests, plane enumeration checks, and platform bring-up whenever new ports, pipes, transcoders, or color blocks are added.
