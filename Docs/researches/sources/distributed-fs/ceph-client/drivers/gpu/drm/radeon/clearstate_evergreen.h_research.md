# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/clearstate_evergreen.h

## Purpose
`clearstate_evergreen.h` defines static default register-state tables for Evergreen-generation GPUs. Its shape closely matches the Cayman variant: context extents, clear-mask extents, control-constant extents, and a top-level section descriptor list.

## Important APIs, types, and data
- `SECT_CONTEXT_def_1` through `SECT_CONTEXT_def_7` contain context defaults for depth/stencil, scissor, shader constants/resources, viewport, blend/rasterizer, vertex/geometry, streamout, and AA state.
- `SECT_CONTEXT_defs` maps extents at `0x0000a000`, `0x0000a1f5`, `0x0000a200`, `0x0000a23a`, `0x0000a29e`, `0x0000a2a5`, and `0x0000a2de`. The fourth extent count is 98, slightly different from Cayman's corresponding count.
- `SECT_CLEAR_def_1` maps clear masks for sampler/resource/loop-bool clear registers at `0x0000ffc0`.
- `SECT_CTRLCONST_def_1` maps vertex base/start-instance defaults at `0x0000f3fc`.
- `evergreen_cs_data` is the top-level `struct cs_section_def` list ending in `SECT_NONE`.

## Control flow and integration points
There are no functions. Clear-state emission code includes this data and iterates the section and extent descriptors to produce command-stream writes for Evergreen hardware. The descriptor contract is defined by `clearstate_defs.h`, though this header itself does not include it and depends on the including compilation context.

## State and persistence behavior
The static arrays do not change. When emitted, they program persistent Evergreen GPU context, clear, and control-constant registers until later rendering setup or reset changes them.

## Dependencies and constraints
The file depends on `u32` and the clearstate descriptor types being visible to the including source. The register index/count pairs are tightly coupled to Evergreen register layout. `HOLE` zeroes are counted placeholders and must remain aligned with the target register ranges.

## Risks and test signals
Incorrect extents or defaults can break Evergreen rendering, blits, and post-reset context initialization. Test signals include Evergreen clear-state command generation, draw/blit smoke tests, GPU hang absence after preambles, and command-stream/register trace comparison with known-good defaults.
