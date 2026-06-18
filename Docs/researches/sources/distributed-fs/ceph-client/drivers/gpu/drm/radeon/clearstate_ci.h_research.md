# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/clearstate_ci.h

## Purpose
`clearstate_ci.h` defines CIK/CI default clear-state context register tables. Unlike the Evergreen/Cayman variants, this header provides only a context section, reflecting the CIK register layout and defaults used to initialize or restore graphics state.

## Important APIs, types, and data
- Includes `clearstate_defs.h`.
- `ci_SECT_CONTEXT_def_1` through `ci_SECT_CONTEXT_def_7` hold CIK context defaults, including depth/stencil, scissor, BC base, shader resource, viewport, color-buffer, blend, rasterizer, geometry, streamout, and anti-aliasing related registers.
- `ci_SECT_CONTEXT_defs` maps the arrays to extents at `0x0000a000`, `0x0000a0d6`, `0x0000a1f5`, `0x0000a200`, `0x0000a2a0`, `0x0000a2a3`, and `0x0000a2a5`.
- `ci_cs_data` is the top-level sentinel-terminated section list with `SECT_CONTEXT` followed by `SECT_NONE`.

## Control flow and integration points
The file has no executable control flow. Clear-state consumers iterate `ci_cs_data` and emit each context extent as packetized context-register writes for CIK hardware. The descriptor format is shared with other clearstate headers through `clearstate_defs.h`.

## State and persistence behavior
The arrays are static immutable CPU-side data. Emission writes persistent CIK context-register state. The state remains active until the next context restore, clear-state command, draw setup, or GPU reset changes it.

## Dependencies and constraints
The content depends on CIK-specific register index layout and field semantics. The use of `unsigned int` rather than `u32` still assumes 32-bit entries. Consumers must respect sentinel termination and must not interpret `HOLE` zeroes as omitted registers; they are part of counted ranges.

## Risks and test signals
Bad counts or defaults can corrupt CIK graphics state, particularly color/depth targets, scissor/viewport, shader resources, and AA state. Test signals include CIK clear-state emission, draw/blit correctness after reset or preamble, command submission without CP faults, and register trace comparison against expected CIK defaults.
