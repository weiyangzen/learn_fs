# sources/distributed-fs/ceph-client/drivers/staging/vme_user/vme.c

## Purpose
Implements the staging VME bridge framework: a Linux bus type named `vme`, bridge registration, software enumeration of VME devices per bridge, and exported resource APIs for VME master windows, slave windows, DMA engines, interrupts, location monitors, bus errors, and bridge-local coherent allocation.

## Important APIs, Types, and Functions
Important exported APIs include `vme_register_bridge()`, `vme_unregister_bridge()`, `vme_register_driver()`, `vme_unregister_driver()`, `vme_slave_request/set/get/free()`, `vme_master_request/set/get/read/write/rmw/mmap_prepare/free()`, `vme_dma_request()`, `vme_new_dma_list()`, `vme_dma_*_attribute()`, `vme_dma_list_add/exec/free()`, `vme_irq_request/free/generate()`, `vme_lm_request/set/get/attach/detach/free()`, `vme_alloc_consistent()`, `vme_free_consistent()`, `vme_check_window()`, `vme_slot_num()`, and `vme_bus_num()`. The file also exports the `vme_bus_type` bus object.

## Control Flow
Bridge drivers call `vme_init_bridge()` and `vme_register_bridge()` after filling resource lists and callback function pointers. VME client drivers call `vme_register_driver()`, which registers the generic driver and creates up to `ndevs` synthetic `struct vme_dev` instances for every registered bridge. Matching requires the device `platform_data` to point to the same `struct vme_driver` and optionally pass the driver's `match()` callback. Resource requests scan the bridge's resource lists, lock the first compatible unlocked resource, and return a small `struct vme_resource` wrapper. Later operations validate the resource type and delegate to bridge-specific callbacks.

## State and Persistence Behavior
Global framework state is `vme_bus_numbers`, `vme_bus_list`, and `vme_buses_lock`. Per-resource locked state persists in bridge-owned resource structs until the corresponding free call. IRQ callback state persists in `bridge->irq[level - 1].callback[statid]` and `count`. Bus error handlers are bridge-local list entries with first-error and count accumulation. No state is persisted outside kernel memory or device registers.

## Dependencies and Integration Points
Depends on the Linux driver core, list/mutex/spinlock primitives, DMA mapping types, mmap helpers, and bridge contracts from `vme_bridge.h`. Provider implementations in `vme_fake.c` and `vme_tsi148.c` fill callbacks; `vme_user.c` consumes master/slave/IRQ APIs.

## Risks and Test Signals
Several APIs call `find_bridge(resource)` before fully validating `resource`, so callers must not pass null or stale resources. `vme_irq_request()` indexes `statid` without checking `0..255`; bad callers can corrupt callback state. DMA resource request logs that route attributes are not fully tested. `vme_bus_error_handler()` walks handler lists without an explicit lock. Test signals are clean bridge probe/remove, driver registration across multiple bridges, resource double-free warnings, master mmap bounds rejection, IRQ request/free refcounting per level, DMA busy/free rejection, and bus-error routing with `err_chk`.
