# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_drv.h

Purpose: This is the central private header for the QXL DRM driver. It defines driver constants, core runtime structures, conversion macros, and cross-file function prototypes.

Important APIs, types, and functions: Key structs include `qxl_bo`, `qxl_gem`, `qxl_crtc`, `qxl_output`, `qxl_mman`, `qxl_memslot`, `qxl_release`, `qxl_drm_image`, `qxl_debugfs`, and `qxl_device`. It declares command, display, GEM, dumb, TTM, image, release, draw, debugfs, PRIME, IRQ, surface, and ioctl APIs. `qxl_bo_physical_address()` computes QXL physical addresses from BO placement and memslot high bits.

Control flow: The header itself has no runtime control flow, but it defines the shared control contract between probe, KMS, object management, command submission, and ioctls. Inline address computation chooses main vs surface memslot based on TTM memory type.

State and persistence: `struct qxl_device` aggregates nearly all persistent driver state: PCI resource bases, ROM/RAM mappings, rings, BO managers, memslots, IDRs, release counters, wait queues, IRQ counters, work structs, primary/dumb-shadow state, monitor config, and debugfs registry. `qxl_bo` persists per-buffer surface and mapping state.

Dependencies and integration points: Includes DRM core, GEM, TTM, DRM exec, DMA fences, QXL UAPI, and `qxl_dev.h`. It is included by nearly every QXL translation unit, so it is the coupling point for subsystem boundaries.

Risks: `qxl_bo_physical_address()` has a TODO about locking while reading BO resource placement. Struct fields have mixed locking rules; comments identify `gem.mutex`, `tbo.reserved`, spinlocks, and mutexes, but callers must obey them. Any struct layout changes can affect many files.

Test signals: Full QXL build after prototype or struct changes; lockdep under modeset/draw/ioctl stress; surface memory vs VRAM address validation; sparse/static analysis for missing declarations and locking misuse.
