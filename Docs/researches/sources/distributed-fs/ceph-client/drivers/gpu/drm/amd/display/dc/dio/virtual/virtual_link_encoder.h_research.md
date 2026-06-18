# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/virtual/virtual_link_encoder.h

## Purpose
Declares the constructor for the virtual link encoder implementation. It is the public header used by core DC code when creating virtual links.

## Important APIs, Types, And Functions
The sole API is `virtual_link_encoder_construct(struct link_encoder *enc, const struct encoder_init_data *init_data)`, which fills a caller-owned `link_encoder` object with virtual function pointers and identity fields.

## Control Flow
The header has no control flow. The implementation installs no-op hardware callbacks and virtual identity state.

## State And Persistence
No state is stored here. The constructed object persists state in the caller-provided `struct link_encoder`.

## Dependencies And Integration Points
Includes `link_encoder.h` for the base type and `encoder_init_data`. Core DC virtual link initialization includes this header and calls the constructor.

## Risks
The narrow API makes ownership expectations important: the constructor does not allocate the object, while the implementation's destroy callback frees it. Callers must keep allocation and destruction conventions aligned.

## Test Signals
Compile-time coverage verifies the link encoder type is visible. Runtime virtual connector tests should confirm construction succeeds and physical link operations remain no-ops.
