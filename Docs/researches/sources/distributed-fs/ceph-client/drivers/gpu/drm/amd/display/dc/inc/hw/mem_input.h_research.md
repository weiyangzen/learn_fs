# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/mem_input.h

## Purpose

`mem_input.h` defines the older memory-input hardware abstraction used to feed display pipes from memory. It covers tiling, page flip, watermark, stutter, blanking, compression, and surface-address programming for DCE-era front-end memory blocks.

## Important APIs, Types, And Functions

The file defines request modes, stutter modes, tiling settings, DCP GRPH surfaces, MI register update callbacks, and `struct mem_input` with context, instance, and vtable. The function table includes allocation/destruction style hooks plus register programming for addresses, tiling, surface configuration, memory requests, page flips, watermarks, stutter, blanking, and compression behavior.

## Control Flow

Plane programming code configures tiling and surface parameters, programs base/flip addresses, updates memory request parameters, and may enable stutter or compression after the pipe is ready. Page-flip paths use the flip-specific hooks and depend on interrupt service paths to signal completion.

## State And Persistence Behavior

The software object is stable in the resource pool, while programmed surface addresses and memory-controller settings persist in hardware until the next page flip or modeset. Watermark and stutter settings persist across frames and interact with power-management decisions.

## Dependencies And Integration Points

The header depends on DC hardware types and is a predecessor to HUBP-style memory input in DCN. It integrates with resource mapping, plane state, IRQ page-flip sources, and power-management watermarks.

## Risks And Test Signals

Risks include stale surface addresses, tiling mismatches, incorrect blanking before address changes, and power-saving watermarks that cause underflow. Test signals include page-flip completion, tiled/compressed framebuffer scanout, stutter enablement, underflow logs, and multi-plane modesets on ASICs that still use this interface.
