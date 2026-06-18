# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/clearstate_ci.h

Purpose: contains the CIK/CI clear-state context-register payload used to initialize or reset graphics pipeline context state. It is data-only: arrays of register default values grouped into extents, plus a section table exported as `ci_cs_data`.

Important APIs and data: defines seven `ci_SECT_CONTEXT_def_*` arrays of unsigned register values. `ci_SECT_CONTEXT_defs[]` maps those arrays to context register start indexes and register counts, for example start `0x0000a000` count 212 and later context-register ranges. `ci_cs_data[]` maps the context extent list to `SECT_CONTEXT` using structures from `clearstate_defs.h`.

Control flow: no executable code. Consumers iterate `ci_cs_data`, then each `cs_extent_def`, and write or packetize the values into the corresponding context register ranges. Holes in the arrays are represented as zero-valued entries with comments naming them as holes.

State and persistence: static const data only. When consumed, it affects GPU graphics context state such as DB/PA/CB/VGT/SPI/SX registers, scissor defaults, viewport z ranges, shader masks, coherency bases, and other context registers.

Dependencies and integration points: depends on `struct cs_extent_def`, `struct cs_section_def`, and `enum section_id` from `clearstate_defs.h`. It integrates with the GFX clear-state or command preamble path for CIK-class GPUs.

Risks: the data must exactly match CIK context-register layout. A wrong register count, start offset, or default value can cause rendering corruption or GPU hangs. Because the arrays contain many holes and magic defaults, manual edits are high risk. Comments are descriptive but not enforced; consumers rely on extent counts.

Test signals: compile consumers that include this header, command submission using clear-state preambles, graphics rendering correctness, GPU reset/recovery, and comparison against known-good upstream clear-state tables.
