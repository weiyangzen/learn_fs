# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-streams.h

## Purpose
This header declares the ivtv stream lifecycle API for setup, registration, cleanup, capture/decode control, and passthrough mode.

## Important APIs, Types, and Functions
It declares `ivtv_streams_setup`, `ivtv_streams_register`, `ivtv_streams_cleanup`, encoder and decoder start/stop functions, `ivtv_stop_all_captures`, and `ivtv_passthrough_mode`.

## Control Flow
There is no executable flow. Driver probe and remove paths use setup/register/cleanup, while fileops and ioctl paths use the start/stop and passthrough declarations.

## State and Persistence Behavior
The header stores no state. Implementations allocate stream buffers, register V4L2 devices, mutate stream flags and atomics, issue firmware commands, and update IRQ masks.

## Dependencies and Integration Points
It depends on `struct ivtv_stream`, `struct ivtv`, V4L2 stream semantics, and the broader ivtv fileops/ioctl code.

## Risks
Callers must pass stream types appropriate to encode/decode helpers and must hold expected serialization locks where required by implementation paths.

## Test Signals
Build coverage plus stream setup/register/unregister and V4L2 capture/decode/passthrough tests cover the header contract.
