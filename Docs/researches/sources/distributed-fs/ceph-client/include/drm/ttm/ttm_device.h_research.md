# sources/distributed-fs/ceph-client/include/drm/ttm/ttm_device.h

Purpose: declares the TTM per-device object, global state, driver callback table, initialization/finalization, manager access, hibernation, swapout, and DMA mapping cleanup.

Important APIs/types/functions: `ttm_glob` contains dummy read page, device list, and global BO count. `struct ttm_device_funcs` lets drivers create/populate/unpopulate/destroy TT, judge eviction value, choose evict placement, move BOs, receive delete/swap/release notifications, reserve/free IO memory, compute IO PFNs, and perform ptrace-style memory access. `struct ttm_device` stores device list, allocation flags, funcs, system manager, per-memory-type managers, VMA manager, page pool, LRU lock, unevictable list, dev mapping, and delayed-delete workqueue.

Control flow: a driver initializes `ttm_device`, installs memory managers, creates BOs, and TTM calls driver callbacks during validation, eviction, swapout, mapping, and release. `ttm_manager_type()` and `ttm_set_driver_manager()` access manager slots with constant-bound checks.

State and persistence: per-device managers, pool, LRU lists, unevictable BOs, and workqueue are persistent for the DRM device lifetime. Global state tracks all TTM devices and BO count.

Dependencies and integration: depends on TTM allocation/resource/pool headers, DRM VMA offset management, workqueues, address_space, and driver memory callbacks.

Risks and test signals: callback misimplementation, manager slot misuse, pool cleanup, LRU locking, and hibernation/swapout are critical. Test device init/fini leaks, manager registration bounds, BO create/destroy counts, global/device swapout, hibernation preparation, and DMA mapping cleanup.
