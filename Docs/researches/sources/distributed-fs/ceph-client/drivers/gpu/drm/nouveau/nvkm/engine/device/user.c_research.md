<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/user.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/user.c

Purpose: exposes the root user-visible NVIF `NV_DEVICE` object that clients use to query device information, map BAR0, get timer values, and enumerate child classes for engines/subdevices.

Important APIs and functions: `nvkm_udevice_sclass` registers the `NV_DEVICE` class. `nvkm_udevice_new()` allocates `struct nvkm_udevice` and binds it to `nvkm_device_find(client->device)`. `nvkm_udevice_info()` handles v0 legacy info and v1 batched `NV_DEVICE_INFO_*` requests. `nvkm_udevice_time()` returns `nvkm_timer_read()`. `nvkm_udevice_init()` and `nvkm_udevice_fini()` refcount calls to `nvkm_device_init()`/`nvkm_device_fini()`. `nvkm_udevice_child_get()` enumerates DMAOBJ, FIFO, DISP, control, MMU, fault, and VFN children.

Control flow: user methods are dispatched by `nvkm_udevice_mthd()`. Info v1 validates that the remaining payload equals `count * sizeof(data[0])` and translates supported unit queries to subdev info, currently only `NV_DEVICE_HOST(0)` to FIFO. Info v0 reports platform, family, chipset, revision, RAM size/user RAM, chip name, and device name.

State and persistence: persistent object state is just the `nvkm_object` and a device pointer. Device power/lifecycle state is managed through the shared `device->refcount` under `device->mutex`; failed init/fini paths restore the count.

Dependencies and integration points: depends on NVIF class headers, `nvif_unpack`, client lookup, timer, framebuffer/instmem RAM accounting, and engine class enumeration. It is the root bridge from DRM/user clients into NVKM engine objects.

Risks: ABI compatibility is critical because NVIF structs are user-visible. Family/platform mappings must stay aligned with new `card_type` values. Child enumeration order affects userspace class discovery. RAM accounting subtracts reserved instmem only when both FB RAM and instmem are present.

Test signals: create/destroy NVIF device objects, query both v0 and v1 info with valid and invalid payload sizes, map BAR0, read time, enumerate child classes, and exercise multiple simultaneous clients to verify refcounted init/fini.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/device/user.c -->
