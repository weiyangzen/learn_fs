# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn32/dcn32_init.h

## Purpose
`dcn32_init.h` exposes the DCN32 hw sequencer construction entry point.

## Important APIs, types, and functions
The only API is `dcn32_hw_sequencer_init_functions(struct dc *dc)`. The file forward-declares `struct dc` and uses a normal include guard.

## Control flow
The header has no runtime control flow. It allows resource construction code to call the DCN32 vtable initializer.

## State and persistence behavior
No state is owned here. The declared function persists callback assignments into the `dc` object when called.

## Dependencies and integration points
This header is included by DCN32 resource construction or generation selection code that needs to install the DCN32 hwseq table.

## Risks and edge cases
The interface is small, so the main risk is selecting the wrong generation constructor for an ASIC or failing to call it before DC paths invoke `dc->hwss`.

## Test signals
Build coverage and successful DCN32 probe/init are the relevant signals.
