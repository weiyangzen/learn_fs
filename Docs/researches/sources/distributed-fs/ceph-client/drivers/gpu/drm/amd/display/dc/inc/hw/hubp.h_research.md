# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/inc/hw/hubp.h

## Purpose

`hubp.h` defines the per-pipe HUBP abstraction, the DCHUB front-end block that fetches plane memory, handles tiling/DCC/VM, cursor fetch, viewport programming, flip/address updates, DML RQ/DLG/TTU registers, MALL/SubVP, and 3D LUT fetch logic.

## Important APIs, Types, And Functions

Important enums include cursor pitch, cursor lines per chunk, HUBP independent block size, and 3D LUT fetch modes/formats/addressing/width/crossbar. `struct hubp` stores vtable, context, request address, instance, runtime OPP/MPCC IDs, cursor state/cache, offload flag, power-gated state, and MALL cursor flag. `surface_flip_registers` mirrors flip/address registers. `hubp_funcs` covers setup/setup2, interdependent setup, DCC control, reset, viewport, flip/address, PTE/VM, aperture/context0, surface config, flip pending, blanking, cursor attributes/position, disconnect, clock/VTG, state/reg readback, underflow, disable/init, DM data, triple buffering, GSL flip control, DML output validation, unbounded requesting, soft reset, interrupts, p-state disallow, MALL/SubVP, surface update lock, extended blank, pipe-read-start wait, mcache, 3D LUT fetch, tiling clear, current read line, and DET config error.

## Control Flow

Plane enable programs surface config, VM/PTE, viewport, RQ/DLG/TTU/DML registers, VTG selection, cursor state, and surface addresses. Flip paths call `hubp_program_surface_flip_and_addr` and then poll pending status or use interrupts. Updates may lock surface registers, adjust MALL/SubVP, reprogram mcache, or validate DML outputs. Disable paths blank, disconnect, reset, or power gate HUBP.

## State And Persistence Behavior

`hubp` persists per hardware pipe and caches request address, runtime routing IDs, cursor attributes/position, cursor register mirrors, cursor rectangle, MALL cursor selection, and power-gated state. Hardware persists memory-fetch, VM, DCC, cursor, flip, blank, and DLG/TTU registers until changed.

## Dependencies And Integration Points

It includes `mem_input.h`, cursor cache, and DML2 DCHUB register/types. It integrates with `pipe_ctx`, HUBBUB, DPP, MPC/OPP, timing generator, DML/DML2 bandwidth output, VM setup, cursor handling, MALL/SubVP, DM data/infoframes, and HWSS block sequences.

## Risks And Edge Cases

Flip/address programming is synchronization-sensitive and must handle immediate vs vblank flips, stereo, TMZ, VMID, meta surfaces, and chroma planes. VM aperture/context and DCC settings must match surface tiling. DML register validation is important because invalid RQ/DLG/TTU values cause underflow. Cursor state is split with DPP. Power-gated state and cached registers must be refreshed after reset.

## Test Signals

Tests should cover surface flips, DCC on/off, VM/PTE, rotations/tiling, viewport changes, cursor movement/offload, triple buffering, GSL flip control, unbounded requesting, SubVP/MALL, mcache, 3D LUT fetch, underflow clear/status, blank/disconnect/reset, and DET config errors. Signals include flip-pending timeouts, underflows, VM faults, current read line, and visual corruption.
