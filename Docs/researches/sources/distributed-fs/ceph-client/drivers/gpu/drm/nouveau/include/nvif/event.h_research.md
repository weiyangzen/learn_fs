# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/event.h

## Purpose
Declares NVIF event objects and callback plumbing for receiving asynchronous notifications.

## Important APIs, Types, And Functions
Defines `NVIF_EVENT_KEEP/DROP`, `nvif_event_func`, `struct nvif_event`, `nvif_event_constructed`, `nvif_event_ctor_`, wrapper `nvif_event_ctor`, destructor, allow, and block.

## Control Flow
Construction registers an event object with a callback and optional wait behavior. `allow` enables delivery and `block` disables it; callbacks return keep/drop.

## State And Persistence
Event state includes the embedded object and callback pointer and persists until destructor.

## Dependencies And Integration Points
Depends on `nvif/object.h` and `nvif/if000e.h`; used by connector, head/vblank, fault-buffer, and software event paths.

## Risks
Callbacks can run asynchronously relative to teardown. Blocking/allowing incorrectly can miss notifications or deliver after owner destruction.

## Test Signals
Hotplug, vblank, fault, and software event delivery plus teardown race tests validate behavior.
