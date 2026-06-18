# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga3d_cmd.h

## Purpose

`svga3d_cmd.h` defines the VMware SVGA3D FIFO command ABI. It enumerates 3D command IDs and declares packed command payload structures for legacy fixed-function 3D, guest-backed resources, MOB/object-table operations, screen targets, logic operations, and command-era bridges into the DX command range.

## Important APIs, Types, and Functions

- `enum SVGAFifo3dCmdId`: command ID map from `SVGA_3D_CMD_BASE` through legacy commands, GB commands, DX commands, logicops, staging, and reserved/future ranges.
- `SVGA3dCmdHeader`: packed `{ id, size }` header used before command-specific payload bytes.
- Surface/context/shader commands: define/destroy/set/copy/present/clear payloads for `SVGA3dCmdDefineSurface`, `SVGA3dCmdDefineSurface_v2`, `SVGA3dCmdDefineGBSurface*`, `SVGA3dCmdDefineGBContext`, `SVGA3dCmdDefineGBShader`, and related bind/readback/invalidate commands.
- Draw-state commands: render state, render target, texture state, transform, viewport, scissor, clip plane, material, light, shader constants, vertex declarations/streams/divisors, and primitive draw payloads.
- MOB/object-table commands: `SVGAOTable*Entry`, `SVGA3dCmdSetOTableBase*`, `SVGA3dCmdGrowOTable`, `SVGA3dCmdDefineGBMob*`, and mapping/update commands.
- Screen and copy commands: GB screen target define/bind/update, GB screen DMA, screen copy status, zero-surface update/write, and logicops blit/fill/blend structures.

## Control Flow

The header has no executable code. Runtime control flow is implicit in FIFO submission: driver code writes `SVGA3dCmdHeader`, appends the matching packed structure and any variable-length tail data, and the virtual device interprets fields by command ID. Command families evolve from legacy host surfaces to guest-backed MOB/object-table resources and then to DX commands whose payload structures live in `svga3d_dx.h`.

## State and Persistence Behavior

The command structures describe state transitions in the virtual GPU: object creation/destruction, binding, readback/invalidation, draw state changes, query lifecycle, screen target updates, and synchronization/fence reporting. State itself persists in host/device resources, MOBs, object tables, and guest-visible buffers, not in this header.

## Dependencies and Integration Points

- Includes `svga3d_types.h`, `svga3d_limits.h`, and `svga_reg.h`.
- Used by vmwgfx command construction, execbuf validation, resource tracking, surface/context/shader/MOB managers, and virtual-device capability handling.
- Shares command IDs with the host hypervisor ABI; numeric values and packed layout are externally constrained.

## Risks and Edge Cases

- Packed structure sizes and command IDs are ABI. Any padding, type-width, or enum-number drift can break host parsing.
- Many commands use implicit variable-length payloads following a fixed header, so validators must compute sizes from command header length and count fields.
- Several names are reserved or dead; reusing them without host support can create compatibility failures.
- Surface flag versions split 32-bit and 64-bit flags. Validation must apply the right disallowed masks for command version and hardware capability.
- MOB offsets, pitches, array sizes, mip levels, and boxes are guest-controlled command data and require overflow and bounds checks before submission.

## Test Signals

- Compile-time `sizeof`/offset checks against known ABI sizes are valuable for packed command structs.
- Execbuf validation tests should cover command ID dispatch, payload length mismatch, variable-tail commands, invalid IDs, reserved/dead commands, and capability-gated commands.
- Integration tests should exercise surface/context/shader/MOB lifecycles, readback/invalidate ordering, screen target updates, and logicops commands under supported virtual hardware versions.
