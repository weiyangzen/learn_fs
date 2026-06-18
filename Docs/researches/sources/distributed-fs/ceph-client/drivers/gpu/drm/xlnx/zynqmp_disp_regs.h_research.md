# sources/distributed-fs/ceph-client/drivers/gpu/drm/xlnx/zynqmp_disp_regs.h

## Purpose

`zynqmp_disp_regs.h` names register offsets and bit fields for the ZynqMP display controller's blender, AV buffer manager, and audio mixer.

## Important APIs, Types, And Functions

It defines blender background/global-alpha/output-format/layer-control/CSC registers, AV buffer format/channel/STC/output/clock/reset/scaling/live-config/palette registers, and audio mixer volume/channel-status/data/reset registers.

## Control Flow

No runtime control flow. These macros are consumed by direct MMIO reads/writes in `zynqmp_disp.c`, `zynqmp_dp_audio.c`, and related paths.

## State And Persistence Behavior

The macros describe persistent hardware register state for layer routing, format selection, CSC matrices, buffer channel enable/flush, clock source selection, and audio mixer/control state.

## Dependencies And Integration Points

It depends on `linux/bits.h` for bit helpers and integrates tightly with the display and audio source files. Values must match the ZynqMP DP subsystem hardware specification.

## Risks And Test Signals

Risks include incorrect offsets/masks silently corrupting adjacent hardware state, especially shared AV buffer output fields and audio reset/volume registers. Test through register readback where available, format/output changes, alpha/CSC behavior, audio playback, and underflow/overflow interrupt observation.
