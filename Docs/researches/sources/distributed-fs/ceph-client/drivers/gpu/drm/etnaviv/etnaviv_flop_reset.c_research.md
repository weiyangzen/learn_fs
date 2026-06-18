# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_flop_reset.c

## Purpose
Implements a PPU flop-reset workaround for selected Vivante GPU identities by preparing a small compute payload and emitting command stream state to run it.

## Important APIs, Types, and Functions
Exports `etnaviv_flop_reset_ppu_require`, `etnaviv_flop_reset_ppu_init`, and `etnaviv_flop_reset_ppu_run`. Internal helpers fill input image data, copy a fixed shader instruction sequence, and emit OpenCL/PPU state through command macros. Module parameter `force_flop_reset` can force the workaround when 3D pipe support exists.

## Control Flow
Requirement checking matches chip model/revision against a small database or the force parameter. Init allocates a cmdbuf from the shared suballocator, fills input data and shader bytes, and keeps it for driver lifetime. Run computes the GPU VA of the payload in the active MMU context and emits state that loads uniforms, shader ranges, workgroup configuration, kicker, and shader cache flushes into the GPU ring.

## State and Persistence
Persistent state is `priv->flop_reset_data_ppu`, a suballocated cmdbuf containing input/output image regions and shader code. It is freed on driver unbind.

## Dependencies and Integration Points
Called from GPU initialization/ring setup when chip identity requires it. Depends on command emission helpers, cmdbuf suballocation, active MMU context mapping, generated state headers, and chip feature flags.

## Risks
Hard-coded shader/state values are highly hardware-specific. Running on a chip without required 3D/PPU support can hang; force mode guards only the 3D feature. Init failure or missing payload causes run to skip with an error.

## Test Signals
Boot/init logs on affected model `0x8000` revision `0x6205`, forced-workaround tests, GPU initialization success, ring dumps showing emitted reset commands, and absence of early hangs on affected hardware.
