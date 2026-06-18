# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_wopcm.h

## Purpose

`xe_wopcm.h` exposes the WOPCM initialization and sizing API to Xe GT/uC setup code.

## Important APIs, Types, And Functions

It includes `xe_wopcm_types.h`, forward declares `struct xe_device`, and declares `xe_wopcm_init()` and `xe_wopcm_size()`.

## Control Flow

There is no runtime control flow; this is a declaration boundary between WOPCM consumers and the implementation.

## State And Persistence Behavior

No state is owned by the header. It centralizes access to `struct xe_wopcm` through the included type header.

## Dependencies And Integration Points

The header integrates GT/uC initialization with the WOPCM implementation while avoiding full Xe device type inclusion.

## Risks And Test Signals

Risk is declaration/type mismatch. Build coverage in users of `xe_wopcm_init()` and `xe_wopcm_size()` is the relevant signal.
