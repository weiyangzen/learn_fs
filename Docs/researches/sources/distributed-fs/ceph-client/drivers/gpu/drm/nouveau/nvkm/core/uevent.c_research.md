## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/core/uevent.c

### Purpose
`uevent.c` implements client-visible NVIF event objects. It wraps an `nvkm_event_ntfy` subscription in an NVKM object and exposes allow/block methods so userspace can control event delivery.

### Important APIs, types, and functions
The file defines private `struct nvkm_uevent` with base object, parent object, optional callback, wait flag, event notification, and atomic `allowed` state. Public functions are `nvkm_uevent_new()` and `nvkm_uevent_add()`. Object methods include `NVIF_EVENT_V0_ALLOW` and `NVIF_EVENT_V0_BLOCK`.

### Control flow
Creation validates versioned `nvif_event_args`, constructs the object, stores the parent and wait mode, then delegates to the parent object's `uevent` callback to bind a concrete event source. `nvkm_uevent_add()` adds the notifier to an event, stores an optional delivery callback, and rejects reuse. Allow/block methods update the notifier and mirror the state in `allowed`. Fini blocks delivery; init re-allows delivery only if `allowed` was set before fini.

### State and persistence behavior
The event object's allowed state persists across object init/fini cycles through an atomic flag. The notifier remains attached until destructor calls `nvkm_event_ntfy_del()`. Delivery either calls the per-event `nvkm_uevent_func` or falls back to `client->event()` with the event object's handle.

### Dependencies
It depends on `core/event.h`, `core/client.h`, NVIF event ABI headers `if000e.h`, and the base object system.

### Integration points
Any NVKM object with a `uevent` callback can create a user event object. This bridges kernel event sources to the NVIF client event callback path and participates in object lifecycle ordering.

### Risks
`nvkm_uevent_add()` warns and returns `-EBUSY` if called twice on one object. Version/size mismatches return `-ENOSYS`. Allow/block must stay synchronized with suspend/fini to avoid delivering events when the object is inactive. Parent `uevent` callbacks must fully initialize the notifier or creation returns an error with a partially allocated object handled by caller cleanup.

### Test signals
Test event object creation with bad versions, allow/block method calls, suspend/resume preserving allow state, notifier deletion on object destroy, and parent event callbacks that use both direct function delivery and client fallback delivery.
