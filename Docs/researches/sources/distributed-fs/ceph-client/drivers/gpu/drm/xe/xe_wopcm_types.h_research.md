# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_wopcm_types.h

## Purpose

`xe_wopcm_types.h` defines the small persistent data model for Xe WOPCM layout information.

## Important APIs, Types, And Functions

The sole type is `struct xe_wopcm`, containing the overall WOPCM `size` and a nested `guc` region with `base` and `size`.

## Control Flow

The file has no control flow. It supplies a shared structure definition to implementation and consumers.

## State And Persistence Behavior

Instances persist as part of GT uC state and reflect the software copy of the hardware WOPCM partition.

## Dependencies And Integration Points

It depends only on Linux integer types. It is included by `xe_wopcm.h` and any code needing the struct layout.

## Risks And Test Signals

Risks are field semantic drift from the hardware register interpretation. Compile coverage plus runtime WOPCM debug logs validate that populated fields are nonzero and aligned.
