# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/cik_blit_shaders.h

## Purpose
`cik_blit_shaders.h` provides a static CIK default GPU context-state command stream used by the Radeon blit path. The `cik_default_state` array is encoded as PM4-style register write packets, primarily `PACKET3_SET_CONTEXT_REG`-class headers (`0xc0xx6900`) followed by register offsets and default values for depth, rasterizer, viewport, vertex, blend, shader, and anti-aliasing state.

## Important APIs, types, and data
- `static const u32 cik_default_state[]`: a contiguous command buffer that programs default render state such as `DB_RENDER_CONTROL`, `PA_SC_CLIPRECT_*`, `PA_SC_VPORT_SCISSOR_*`, `VGT_*`, `CB_BLEND*`, `DB_DEPTH_CONTROL`, `CB_COLOR_CONTROL`, `PA_CL_*`, `PA_SU_*`, `PA_SC_*`, and `DB_ALPHA_TO_MASK`.
- `static const u32 cik_default_size = ARRAY_SIZE(cik_default_state)`: compile-time size used by consumers when copying/emitting the state.
- Depends on `u32`, `ARRAY_SIZE`, and packet/register definitions supplied by the including Radeon translation unit.

## Control flow and integration points
The file contains no functions. Consumers include it and emit/copy the static dword stream into a ring, IB, or driver-owned state buffer before CIK blit operations so a known graphics context exists. The encoded sequence walks register ranges in contiguous extents, reducing per-register command overhead.

## State and persistence behavior
The header itself is immutable static data. When emitted to hardware, it overwrites GPU context registers with deterministic defaults. That state persists in the GPU context until later command streams change it or a hardware context reset occurs.

## Dependencies and constraints
The array depends on exact CIK register ordering and packet encoding. The values assume expected CIK context-register offsets and field semantics from `cikd.h` and related Radeon packet helpers. Alignment and count values in the packet headers must match the number of following dwords.

## Risks and test signals
Risks include silent GPU hangs or rendering/copy corruption if any packet count, register offset, or default value is wrong. Test signals include blit/copy correctness, GPU ring progress after default-state emission, absence of command-processor faults, and suspend/resume or reset paths that rebuild default state.
