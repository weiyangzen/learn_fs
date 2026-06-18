<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fault/user.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fault/user.c

## Purpose
Exposes an NVKM user object for a replayable fault buffer so userspace can query buffer metadata, map the buffer through BAR2, and subscribe to pending-buffer events.

## Important APIs, Types, And Functions
`nvkm_ufault_new()` handles class construction and `nvif_clb069_v0` argument unpacking. `nvkm_ufault_map()` returns `NVKM_OBJECT_MAP_IO`, BAR2 instance address plus buffer offset, and allocation size. `nvkm_ufault_uevent()` subscribes to `NVKM_FAULT_BUFFER_EVENT_PENDING`. Object callbacks also include `nvkm_ufault_init()`, `nvkm_ufault_fini()`, and a no-op destructor.

## Control Flow
Creation selects `device->fault->buffer[fault->func->user.rp]`, unpacks ABI version 0 arguments, returns entries/get/put metadata to the caller, and constructs the object around the existing buffer object storage. Init/fini simply call generation-specific buffer programming callbacks. Event registration validates argument size before binding the user event to the fault event source.

## State And Persistence
No new memory is owned by the user object; it wraps the pre-existing `struct nvkm_fault_buffer`. Mapping exposes the persistent hardware-managed queue memory. Init/fini mutate hardware buffer enablement through the selected function table.

## Dependencies And Integration Points
Depends on NVIF class `clb069`, NVKM object/event helpers, BAR2 resource addressing, fault-buffer memory, and the generation fault function table. It is the user ABI bridge for draining replayable faults.

## Risks
The object does not validate that `device->fault`, `buffer`, or `buffer->mem` are non-NULL, relying on core construction ordering. ABI size mismatch returns `-ENOSYS`. BAR2 address calculation and `user.rp` must match the hardware buffer intended for userspace.

## Test Signals
Useful checks are successful CLB069 object creation, correct returned entry/get/put values, mmap size matching buffer memory, pending-event delivery, and init/fini toggling hardware without leaking events after close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/fault/user.c -->
