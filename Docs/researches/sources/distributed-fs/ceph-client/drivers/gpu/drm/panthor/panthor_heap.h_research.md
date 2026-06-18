# sources/distributed-fs/ceph-client/drivers/gpu/drm/panthor/panthor_heap.h

`panthor_heap.h` declares the tiler heap API used by ioctl, VM, scheduler, and firmware-resource paths.

It forward-declares `struct panthor_device`, `struct panthor_heap_pool`, and `struct panthor_vm`. The API includes `panthor_heap_create()`, `panthor_heap_destroy()`, `panthor_heap_pool_create()`, `panthor_heap_pool_destroy()`, `panthor_heap_pool_get()`, `panthor_heap_pool_put()`, `panthor_heap_pool_size()`, `panthor_heap_grow()`, and `panthor_heap_return_chunk()`.

No runtime flow lives here. Ioctl handlers call create/destroy, VM lifetime code owns pool creation/destruction, scheduler or firmware event handling calls grow and return chunk, and fdinfo/memory reporting reads pool size.

The opaque pool hides persistent xarray, refcount, VM binding, GPU context BO, and size accounting. Dependencies are minimal Linux types and Panthor forward declarations. Risks are caller lifetime mistakes: pool destruction clears VM association, so users need valid pool refs and must handle `-EINVAL` from stale handles. Ioctl code also combines VM ID and heap ID into one handle, so all users must split that consistently. Tests should compile all users and exercise create/grow/return/destroy through real firmware resource events.
