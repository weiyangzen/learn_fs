# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/ttm_object.h

## Purpose
Declares the public object-management contract implemented by `ttm_object.c`. It defines the base object layout embedded by vmwgfx user-visible resources, the PRIME-aware wrapper object, and the APIs used by file open/release, resource creation/destruction, handle lookup, and dma-buf conversion.

## Important APIs, Types, And Functions
- `enum ttm_object_type` reserves generic TTM object kinds and driver-private ranges.
- `struct ttm_base_object` contains RCU head, owner `ttm_object_file`, kref, release callback, numeric handle, object type, and shareability flag.
- `struct ttm_prime_object` embeds `ttm_base_object`, adds a mutex, exported size, real underlying type, cached dma-buf pointer, and underlying release callback.
- API declarations cover base initialization, lookup, unref, per-file reference add/drop, object-file/device init/release, and PRIME fd/handle conversion.
- Helper macros `ttm_base_object_kfree()` and `ttm_prime_object_kfree()` encode the expected RCU-free pattern.
- `ttm_base_object_type()` hides the internal `ttm_prime_type` wrapper and returns the real resource type.

## Control Flow
Callers allocate an embedding object, initialize resource-specific fields, then call `ttm_base_object_init()` or `ttm_prime_object_init()`. The release callback is called only after the object is removed from the device namespace and all file/dma-buf references are gone. Consumers must lookup with the correct file or device object and drop acquired refs with `ttm_base_object_unref()`.

## State, Persistence, Dependencies, And Integration
This header only describes in-memory state. It depends on `linux/dma-buf.h`, `kref`, `list`, `rcupdate`, and TTM buffer-object types. The comments document an RCU lifetime model: object release removes global visibility first, then embedding objects must be freed after an RCU grace period. It is included by vmwgfx context, surface, and file-private code that needs handle-backed user resources.

## Risks And Test Signals
The main risks are misuse of release callbacks, freeing without RCU, type confusion when `ttm_prime_type` wraps the real type, and incorrect shareability flags. Test signals should verify type reporting through `ttm_base_object_type()`, correct NULLing behavior of unref APIs, and resource-specific release callbacks under close, explicit destroy ioctl, and dma-buf export lifetimes.
