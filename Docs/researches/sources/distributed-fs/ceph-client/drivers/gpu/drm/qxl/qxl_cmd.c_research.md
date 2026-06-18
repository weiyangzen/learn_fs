# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_cmd.c

Purpose: This file implements QXL guest/host command-ring handling, I/O-port commands, release-ring garbage collection, surface ID allocation/reaping, and host surface create/destroy operations.

Important APIs, types, and functions: `qxl_ring_create/free/push()`, `qxl_check_idle()`, `qxl_push_command_ring_release()`, `qxl_push_cursor_ring_release()`, `qxl_queue_garbage_collect()`, and `qxl_garbage_collect()` manage ring communication and completed releases. I/O helpers include `qxl_io_update_area()`, `qxl_io_create_primary()`, `qxl_io_destroy_primary()`, `qxl_io_memslot_add()`, `qxl_io_reset()`, and `qxl_io_monitors_config()`. Surface helpers include `qxl_surface_id_alloc/dealloc()`, `qxl_hw_surface_alloc/dealloc()`, and `qxl_surface_evict()`.

Control flow: Ring push waits or busy-spins when the producer has filled the host-visible ring, copies a command into the current slot, advances `prod`, and notifies the host when requested. Async I/O commands serialize through `async_io_mutex`, track `irq_received_io_cmd`, issue `outb()`, and wait up to five seconds for an IRQ. Garbage collection pops release IDs from the host release ring, follows `next` chains through mapped release info, frees releases, and wakes release waiters. Surface allocation gets an ID from `surf_id_idr`, creates a `QXL_SURFACE_CMD_CREATE` release, fences involved BOs, pushes it, and later mirrors destroy through `QXL_SURFACE_CMD_DESTROY`.

State and persistence: Runtime state includes ring headers in guest VRAM RAM header, `release_idr`, `surf_id_idr`, `last_alloced_surf_id`, `primary_bo`, wait queues, atomic IRQ counters, and per-BO `surface_id`/`hw_surf_alloc`. Host-visible state persists in QXL device memory and is reset or rebuilt during device initialization and resume.

Dependencies and integration points: Depends on QXL protocol structs in `qxl_dev.h`, BO helpers in `qxl_object.c`, release helpers in `qxl_release.c`, IRQ wait queues from `qxl_irq.c`, and TTM reservation/fence behavior. Command pushes are used by display, draw, cursor, ioctl, and surface management paths.

Risks: Ring fullness, memory barriers, and IRQ wait sequencing are concurrency-sensitive. `qxl_bo_physical_address()` assumes stable BO resource placement while mapping commands. Surface reaping can stall on fences and must avoid races with IDR lookups and eviction. Async I/O timeout treats missing host response as device disappearance.

Test signals: Stress command-ring and cursor-ring saturation; trigger host release-ring chains; allocate more surfaces than `rom->n_surfaces` to exercise reaping; test update-area bounds; suspend/resume to rebuild memslots; run under QEMU with IRQ loss or delayed host processing.
