# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce80/dce80_timing_generator.h

## Purpose
Declares the DCE8 timing-generator constructor and documents that the implementation inherits from the DCE11 timing-generator structure and behavior.

## Important APIs, Types, And Functions
Exports `dce80_timing_generator_construct(struct dce110_timing_generator *tg, struct dc_context *ctx, uint32_t instance, const struct dce110_timing_generator_offsets *offsets)`. The header includes `timing_generator.h` and `grph_object_id.h`, relying on the DCE110 type being visible through surrounding include chains.

## Control Flow
The header has no executable control flow. Its constructor declaration is the entry point resource builders use to initialize a DCE8 timing-generator instance.

## State And Persistence
No state is defined here. The constructor populates caller-owned state in the `.c` implementation.

## Dependencies And Integration Points
Used by DCE8 resource code and included by `dce80_timing_generator.c`. It binds DCE8 code to the common timing-generator API and the DCE110-compatible implementation structure.

## Risks
The header accepts a DCE110 concrete object for DCE8 behavior, so changes to DCE110 structure layout or offset contracts can affect DCE8. Missing direct include of `dce110_timing_generator.h` would be fragile if include order changes.

## Test Signals
Compile coverage is the main signal: resource files must be able to include this header and construct timing generators without incomplete-type errors.
