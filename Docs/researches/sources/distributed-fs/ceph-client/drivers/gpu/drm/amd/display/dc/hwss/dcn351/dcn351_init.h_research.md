# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dcn351/dcn351_init.h

## Purpose
`dcn351_init.h` exposes the DCN351 hw sequencer constructor.

## Important APIs, types, and functions
The only API is `dcn351_hw_sequencer_construct(struct dc *dc)`, with `struct dc` forward-declared.

## Control flow
There is no runtime control flow. The header supplies the prototype for generation construction code.

## State and persistence behavior
No state is owned. The declared function installs persistent public/private hwseq callback tables into `dc`.

## Dependencies and integration points
This header is included by code that selects the DCN351 hw sequencer during resource construction.

## Risks and edge cases
As with the other init headers, the main risk is failing to call the constructor or calling it for the wrong ASIC generation.

## Test signals
Successful DCN351 build, probe, and display init are the practical validation signals.
