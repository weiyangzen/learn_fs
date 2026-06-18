# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga3d_limits.h

## Purpose

`svga3d_limits.h` centralizes compile-time SVGA3D hardware and protocol limits for contexts, surfaces, render targets, UAVs, shaders, texture units, lights, surface sizes, arrays, samples, and sandbox data sizes.

## Important APIs, Types, and Functions

- Context/surface limits: `SVGA3D_HB_MAX_CONTEXT_IDS`, `SVGA3D_HB_MAX_SURFACE_IDS`, and `SVGA3D_HB_MAX_SURFACE_SIZE`.
- DX render/UAV limits: `SVGA3D_DX_MAX_RENDER_TARGETS`, DX11/DX11.1 UAV limits, and simultaneous RT/UAV aliases.
- Shader limits: maximum shader IDs, simultaneous shaders, shader memory bytes/words, and compute thread groups.
- Fixed-function/texture limits: texture units, lights, clip planes, texture coordinates, surface faces, vertex arrays, primitive ranges, and samples.
- Surface array limits: SM4 and SM5 array sizes with `SVGA3D_MAX_SURFACE_ARRAYSIZE`.
- Sandbox data-size constants for SBX/DVM paths.

## Control Flow

There is no runtime flow. Other headers and driver validators use these macros for array sizing, command validation, and capability clamping.

## State and Persistence Behavior

No state is owned here. The macros influence structure sizes and accepted resource dimensions throughout the driver.

## Dependencies and Integration Points

- Uses byte conversion macros from `vm_basic_types.h` indirectly in includers.
- Included by `svga3d_cmd.h`, `svga3d_dx.h`, and the aggregate `svga3d_reg.h`.
- Tightly coupled to fixed array lengths in command/context structures.

## Risks and Edge Cases

- Changing a limit can change packed ABI structure sizes when used in arrays, especially DX context MOB layouts.
- Some limits are aliases of the latest supported generation. Validators may need to use lower capability-specific limits on older virtual hardware.
- Large constants must be checked for overflow when multiplied by element sizes or page counts.

## Test Signals

- Compile-time checks should verify ABI structure sizes after any limit change.
- Runtime validation tests should cover boundary values at max, max plus one, and older-capability limits.
