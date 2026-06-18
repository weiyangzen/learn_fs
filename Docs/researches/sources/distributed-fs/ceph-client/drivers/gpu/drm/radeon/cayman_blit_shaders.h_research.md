# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/cayman_blit_shaders.h

## Purpose
This header provides a statically generated Cayman/Evergreen 3D engine default state stream used by the Radeon DRM driver for blit operations. It avoids embedding the full Mesa/3D state generator in the kernel by supplying precomputed packet/register data for the CP clear-context preamble.

## Important APIs, Types, and Functions
The key objects are `static const u32 cayman_default_state[]` and `static const u32 cayman_default_size = ARRAY_SIZE(cayman_default_state)`. The array contains packetized register writes for depth buffer state, scissor and viewport state, shader input/output state, color blend and shader masks, primitive assembly state, streamout state, antialiasing defaults, and other 3D pipeline defaults needed before kernel blits.

## Control Flow
The header has no functions. `ni.c` includes it and, during Cayman CP initialization, locks the ring, emits `PACKET3_PREAMBLE_BEGIN_CLEAR_STATE`, writes every dword in `cayman_default_state`, emits `PACKET3_PREAMBLE_END_CLEAR_STATE`, then issues `PACKET3_CLEAR_STATE`. Subsequent blit setup can assume this known baseline 3D state.

## State and Persistence Behavior
The C array is immutable static data in the compiled driver. When emitted to the command processor, it establishes persistent GPU context clear-state until replaced by later ring commands or reset. `cayman_default_size` tracks the number of dwords so the ring lock reservation and emission loop stay synchronized with the table.

## Dependencies and Integration Points
The file depends on `u32` and `ARRAY_SIZE` definitions from the including Radeon kernel context. It is included by `ni.c`, which provides packet macros, ring locking, and command submission. It integrates with the Radeon blit path and Cayman command processor initialization rather than DPM.

## Risks
The table is hand generated, so register ordering, packet counts, and data values must match Cayman hardware expectations exactly. A wrong dword can corrupt the clear-state preamble, break accelerated blits, hang the CP, or produce rendering/copy corruption. Because the table is opaque packet data, normal compiler checks cannot validate register semantics; review depends on comments, hardware documentation, and runtime testing.

## Test Signals
Build coverage confirms the array and `ARRAY_SIZE` use compile. Runtime signals include Cayman/NI CP initialization, ring tests, GPU reset recovery, framebuffer console and modeset operations, accelerated BO moves and clears, blit correctness tests, and absence of CP hangs after `PACKET3_CLEAR_STATE` on Cayman-class hardware.
