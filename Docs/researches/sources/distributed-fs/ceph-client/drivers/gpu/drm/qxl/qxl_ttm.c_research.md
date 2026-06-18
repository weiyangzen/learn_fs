# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_ttm.c

Purpose: This file implements QXL's TTM memory manager integration for system memory, VRAM, and surface RAM.

Important APIs, types, and functions: `qxl_ttm_init()`, `qxl_ttm_fini()`, `qxl_ttm_io_mem_reserve()`, `qxl_ttm_debugfs_init()`, and TTM device callbacks including `qxl_evict_flags()`, `qxl_ttm_tt_create()`, `qxl_bo_move_notify()`, `qxl_bo_move()`, and delete-memory notification.

Control flow: TTM init creates a `ttm_device`, initializes a VRAM range manager sized by `rom->ram_header_offset / PAGE_SIZE`, initializes a private surface-memory range manager sized by surface BAR pages, and logs memory sizes. Move notification evicts host surfaces before BOs leave `TTM_PL_PRIV`; move handles null/system transitions and otherwise uses memcpy moves after waiting. I/O memory reserve maps VRAM and surface resources to write-combined bus offsets.

State and persistence: Persistent memory-manager state lives in `qdev->mman.bdev` and its VRAM/PRIV range managers. BO moves can clear host surface allocation state through eviction.

Dependencies and integration points: Called from QXL low-level init/fini and object init/fini. Depends on TTM range managers, QXL BO type checks, surface eviction command path, PCI BAR base addresses, and DRM anon inode/vma offset manager.

Risks: Surface eviction during TTM moves must happen before memory disappears from host visibility. VRAM manager size excludes RAM header and uses surface0 memory assumptions. Failed second manager init does not unwind the first manager/device in this function, which cleanup paths should audit.

Test signals: BO moves between VRAM/PRIV/SYSTEM, eviction under memory pressure, debugfs range managers, mmap bus offsets, initialization failure injection, and surface BO migration while commands are pending.
