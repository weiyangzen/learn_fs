# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/event.c

## Purpose
This file wraps NVIF event object creation, block/allow control, and destruction.

## Important APIs, Types, and Functions
Public functions are `nvif_event_ctor_`, `nvif_event_block`, `nvif_event_allow`, and `nvif_event_dtor`.

## Control Flow
Constructor fills default event args when none are supplied, sets version and wait mode, creates an `NVIF_CLASS_EVENT` object, and stores the callback function. Block and allow issue event methods only if the event is constructed. Destructor destroys the event object.

## State and Persistence Behavior
State lives in the event object and callback pointer. Backend state controls whether notifications are blocked or allowed.

## Dependencies and Integration Points
It depends on NVIF object method APIs, event class ABI, and object construction. Connector/head/SVM code builds on this wrapper.

## Risks
Callbacks are stored but invoked by backend event routing elsewhere; stale event objects can call stale callbacks if not blocked/destroyed. Wait-mode behavior affects list insertion on the NVKM side.

## Test Signals
Signals include event construction with custom/default args, block/allow transitions, destruction while blocked/allowed, and HPD/vblank/SVM event delivery.
