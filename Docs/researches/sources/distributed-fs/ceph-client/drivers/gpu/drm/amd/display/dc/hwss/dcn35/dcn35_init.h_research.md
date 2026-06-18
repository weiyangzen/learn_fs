# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn35/dcn35_init.h

## Purpose
`dcn35_init.h` exposes the DCN35 hw sequencer constructor.

## Important APIs, types, and functions
The only API is `dcn35_hw_sequencer_construct(struct dc *dc)`, with `struct dc` forward-declared.

## Control flow
There is no runtime control flow in the header. It supplies the construction prototype for generation selection code.

## State and persistence behavior
No state is stored here. The declared constructor persists callback assignments in the `dc` object.

## Dependencies and integration points
The header is included wherever DCN35 resource construction needs to install the DCN35 hwseq callbacks.

## Risks and edge cases
The main risk is selecting the wrong constructor or invoking DC paths before construction. The concise interface otherwise has little local complexity.

## Test signals
Build coverage and successful DCN35 display initialization validate this header's role.
