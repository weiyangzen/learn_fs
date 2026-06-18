# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/clearstate_cayman.h

## Purpose
`clearstate_cayman.h` defines static default register-state tables for Cayman-generation GPUs. The tables describe context, clear, and control-constant sections consumed by Radeon clear-state emission code to reset graphics context registers to known defaults.

## Important APIs, types, and data
- Includes `clearstate_defs.h` for `struct cs_extent_def`, `struct cs_section_def`, and `enum section_id`.
- `SECT_CONTEXT_def_1` through `SECT_CONTEXT_def_7` contain context-register default values with explicit `HOLE` placeholders where register ranges skip unsupported or reserved addresses.
- `SECT_CONTEXT_defs` maps those arrays to register indices and counts, including extents beginning at `0x0000a000`, `0x0000a1f5`, `0x0000a200`, `0x0000a23a`, `0x0000a29e`, `0x0000a2a5`, and `0x0000a2de`.
- `SECT_CLEAR_def_1` and `SECT_CLEAR_defs` define clear masks for `SQ_TEX_SAMPLER_CLEAR`, `SQ_TEX_RESOURCE_CLEAR`, and `SQ_LOOP_BOOL_CLEAR` at `0x0000ffc0`.
- `SECT_CTRLCONST_def_1` and `SECT_CTRLCONST_defs` define `SQ_VTX_BASE_VTX_LOC` and `SQ_VTX_START_INST_LOC` at `0x0000f3fc`.
- `cayman_cs_data` is the top-level sentinel-terminated section list.

## Control flow and integration points
There are no functions. Consumers iterate `cayman_cs_data`, then each section's extent list, emitting register writes for each array/count pair. The top-level sentinel `{ NULL, SECT_NONE }` and extent sentinels `{ NULL, 0, 0 }` terminate iteration.

## State and persistence behavior
The header data is immutable. When emitted, it resets persistent GPU context registers, shader-resource clear masks, and control constants. The values persist in hardware until later command streams or context switches update them.

## Risks and test signals
Risks are off-by-one register counts, wrong extent base indices, missing holes, or incorrect default values causing render corruption or command-processor faults. Test signals include clear-state packet emission tests, Cayman blit/draw smoke tests, context reset behavior, and comparison of generated command streams to known-good register traces.
