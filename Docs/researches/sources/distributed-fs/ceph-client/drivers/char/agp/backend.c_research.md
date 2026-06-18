# sources/distributed-fs/ceph-client/drivers/char/agp/backend.c

## Purpose
This file implements AGPGART backend bridge registration and initialization. It manages bridge lifetime, backend acquisition/release, global bridge lists, boot options, scratch pages, GATT setup, key-list allocation, and generic cleanup.

## Important APIs, Types, and Functions
Exported APIs are `agp_backend_acquire()`, `agp_backend_release()`, `agp_alloc_bridge()`, `agp_put_bridge()`, `agp_add_bridge()`, and `agp_remove_bridge()`. Important internals are `agp_find_max()`, `agp_backend_initialize()`, and `agp_backend_cleanup()`. Globals include `agp_find_bridge`, `agp_bridge`, `agp_bridges`, `agp_off`, and `agp_try_unsupported_boot`.

## Control Flow
Chipset drivers allocate and fill a bridge, then call `agp_add_bridge()`. The backend rejects registration if `agp_off` is set or no PCI device exists, pins the chipset module, initializes the bridge by allocating scratch page, fetching aperture size, creating GATT table, allocating key list, running chipset `configure()`, and initializing mapped-memory tracking. On success it logs the first aperture and adds the bridge to `agp_bridges`. Removal cleans chipset state, frees GATT/key/scratch resources, removes the list entry, and drops the module reference.

## State and Persistence Behavior
The backend persists global bridge pointers/lists, per-bridge memory accounting, scratch page DMA/masked address, key list, current/previous aperture state, and mapped memory list. Boot parameter `agp=off` disables registration; `agp=try_unsupported` sets a global flag used by drivers such as AMD64.

## Dependencies and Integration Points
It depends on PCI, miscdevice AGP interfaces, generic AGP memory helpers, vmalloc, module references, and chipset callback tables from `agp.h`. User-space `/dev/agpgart` paths acquire/release bridges through this backend.

## Risks
Initialization error unwinding must destroy scratch page in both unmap and free phases and free partial GATT/key allocations. `agp_put_bridge()` sets global `agp_bridge` to NULL only when the list is empty, so singleton assumptions remain fragile. `agp_backend_acquire()` uses an atomic in-use flag but no compare-and-swap, so concurrent acquire attempts can race. The key list allocation comment notes vmalloc memory is not guaranteed contiguous, though it is used as a key bitmap/list.

## Test Signals
Test chipset registration failure at each initialization stage, multiple bridge registration/removal, backend acquire/release concurrency, boot `agp=off`, boot `agp=try_unsupported`, scratch-page allocation cleanup, and no leaks after module unload.
