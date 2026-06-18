# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_virtual.h

## Purpose

`link_hwss_virtual.h` declares the no-op virtual link HWSS interface.

## Important APIs, Types, And Functions

It declares `virtual_setup_stream_encoder()`, `virtual_setup_stream_attribute()`, `virtual_reset_stream_encoder()`, and `get_virtual_link_hwss()`.

## Control Flow

There is no runtime flow in the header. The declarations are used by the virtual implementation and by HPO FRL code, which reuses virtual stream encoder setup/reset while supplying HDMI FRL stream attributes.

## State And Persistence Behavior

The header stores no state; the implementation intentionally does not mutate hardware.

## Dependencies And Integration Points

It includes `core_types.h` for `struct pipe_ctx` and `struct link_hwss`. It is integrated into HWSS selection for virtual links and as shared no-op scaffolding for HPO FRL.

## Risks And Edge Cases

The interface is intentionally sparse. Callers must not expect link output enable, audio, payload, or DP extension callbacks from the virtual HWSS.

## Test Signals

Build coverage validates prototypes. Runtime tests should verify virtual streams and FRL users of these no-op helpers do not accidentally attempt physical DIO/HPO operations.
