# sources/distributed-fs/ceph-client/drivers/media/mc/mc-dev-allocator.c

Purpose: shared USB media-device allocator that gives multiple USB interface drivers for the same `usb_device` a single refcounted `struct media_device` instance.

Important APIs/types/functions: `struct media_device_instance` embeds `struct media_device`, owner module, list node, and `kref`. Public exports are `media_device_usb_allocate()` and `media_device_delete()`. Internal `__media_device_get()` searches or creates instances under `media_device_lock`; `media_device_instance_release()` unregisters, cleans up, removes from the global list, and frees.

Control flow: allocation locks the global list, finds an existing instance by `udev->dev` or creates one, takes a kref, manages owner module references when the requester differs, initializes the media device for USB if not already initialized, then returns it. Delete drops the module reference if needed and decrements the kref; last put unregisters and frees.

State/persistence: global in-memory list and krefs persist while drivers hold references. There is no durable persistence.

Dependencies/integration: depends on USB core, media-device helpers, module refcounting, and callers that pair `media_device_usb_allocate()` with `media_device_delete()`.

Risks/test signals: module reference acquisition failure is logged but the media device is still returned, which can surprise lifetime assumptions. Tests should cover multiple interfaces sharing one USB media device, owner mismatch refcounting, last-delete cleanup, allocation failure, initialization-on-first-use, and hot-unplug races.
