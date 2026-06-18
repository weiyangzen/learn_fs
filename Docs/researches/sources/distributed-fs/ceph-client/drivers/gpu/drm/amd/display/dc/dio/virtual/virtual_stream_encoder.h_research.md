# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/virtual/virtual_stream_encoder.h

## Purpose
Declares creation and construction APIs for the virtual stream encoder. This is the public interface used by resource code to obtain a stream encoder for virtual display outputs.

## Important APIs, Types, And Functions
`virtual_stream_encoder_create(struct dc_context *ctx, struct dc_bios *bp)` allocates and returns a virtual `stream_encoder`. `virtual_stream_encoder_construct(struct stream_encoder *enc, struct dc_context *ctx, struct dc_bios *bp)` initializes a caller-provided object.

## Control Flow
The header itself has no runtime behavior. The implementation validates inputs, installs a no-op function table, and sets virtual identity fields.

## State And Persistence
No state is stored here. Constructed stream encoder objects hold function pointers and context/BIOS/engine identity.

## Dependencies And Integration Points
Includes `stream_encoder.h`. DC resource code includes this header when building virtual stream encoders.

## Risks
The API exposes both allocation and caller-owned construction paths, so callers must pair ownership with the appropriate cleanup path. The required BIOS pointer can be surprising for virtual-only tests.

## Test Signals
Compile-time inclusion should be clean wherever virtual resource creation is enabled. Runtime virtual display tests should verify create/construct success and harmless no-op stream operations.
