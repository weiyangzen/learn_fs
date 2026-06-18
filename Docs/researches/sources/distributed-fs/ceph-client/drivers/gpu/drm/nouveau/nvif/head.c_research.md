# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/head.c

## Purpose
This file wraps NVIF display head objects and vblank event creation.

## Important APIs, Types, and Functions
Public functions are `nvif_head_ctor`, `nvif_head_dtor`, and `nvif_head_vblank_event_ctor`.

## Control Flow
Head construction creates an `NVIF_CLASS_HEAD` object for a display head ID. Vblank event construction creates an event object for that head ID with caller-selected wait behavior. Destructor destroys the head object.

## State and Persistence Behavior
State is the head NVIF object and any event object managed by callers.

## Dependencies and Integration Points
It depends on NVIF display/object/event APIs and the display head class ABI. DRM/KMS vblank handling uses the event wrapper.

## Risks
Invalid head IDs fail at object construction. Event wait semantics must match the caller's interrupt handling.

## Test Signals
Signals include head enumeration, vblank event delivery/block/allow, and teardown during display disable.
