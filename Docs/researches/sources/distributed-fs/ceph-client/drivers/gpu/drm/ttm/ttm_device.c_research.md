# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_device.c

Purpose: global and per-device TTM initialization, teardown, swapout orchestration, hibernation preparation, and DMA mapping clearing.

Important APIs and functions: exports `ttm_glob`, `ttm_device_prepare_hibernation()`, `ttm_global_swapout()`, `ttm_device_swapout()`, `ttm_device_init()`, `ttm_device_fini()`, and `ttm_device_clear_dma_mappings()`. Internal `ttm_global_init()` and `ttm_global_release()` reference-count global state.

Control flow: global init creates the `ttm` debugfs root, sizes pool and TT managers to about half system memory with a DMA32 cap, initializes pool/TT managers, allocates a zeroed dummy read page, initializes the global device list and BO count, and creates debugfs stats. Device init rejects missing VMA manager, initializes global state, allocates a high-priority reclaim workqueue, stores driver funcs and allocation flags, initializes the system manager and pool, sets LRU locks/lists/mapping, and links the device into the global list. Teardown removes from the global list, drains/destroys the workqueue, disables/unregisters the system manager, finalizes the pool, and releases globals. Swapout walks devices or managers with `use_tt`, invoking `ttm_bo_swapout()`.

State and dependencies: state includes `ttm_glob_use_count`, `ttm_glob`, `ttm_debugfs_root`, per-device workqueue, managers, pool, `unevictable`, global `device_list`, and `dummy_read_page`. It depends on debugfs, sysinfo, TTM pool/TT managers, TTM BO swapout, and resource managers.

Risks and test signals: global refcounting and device-list locking are central. A visible bug-like risk is teardown debug logging checking `man->lru[0]` inside a loop over priorities. KUnit device tests cover initialization, pool flags, missing VMA manager, and basic teardown.
