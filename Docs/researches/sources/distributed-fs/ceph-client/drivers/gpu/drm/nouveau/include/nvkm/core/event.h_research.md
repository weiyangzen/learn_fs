# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvkm/core/event.h

## Purpose
Declares NVKM server-side event and notification infrastructure, including user-event bridging to NVIF objects.

## Important APIs, Types, And Functions
Defines `struct nvkm_event`, `nvkm_event_func`, `nvkm_event_init/fini`, `NVKM_EVENT_KEEP/DROP`, `struct nvkm_event_ntfy`, notification add/delete/allow/block APIs, `nvkm_event_ntfy`, validation, `nvkm_uevent_func`, `nvkm_uevent_new`, and `nvkm_uevent_add`.

## Control Flow
Event initialization sets unique lock classes and reference tracking. Notifications are added to event lists, allowed/blocked atomically, dispatched by id/bits, and callbacks decide keep/drop. Uevents adapt NVKM notifications to NVIF client callbacks.

## State And Persistence
Event state stores function table, subdevice, type/index counts, reference counters, locks, and notification list. Each notification stores id, bits, wait flag, callback, allowed state, running flag, and list node.

## Dependencies And Integration Points
Depends on core OS locking/list primitives, NVKM objects/classes, subdevices, and NVIF event wrappers.

## Risks
Concurrency is the main risk: allow/block/delete versus dispatch, wait semantics, lock ordering, and callback lifetime must be correct to avoid missed events or use-after-free.

## Test Signals
Hotplug/vblank/fault/software event tests, concurrent teardown, lockdep, and event reference-count traces validate behavior.
