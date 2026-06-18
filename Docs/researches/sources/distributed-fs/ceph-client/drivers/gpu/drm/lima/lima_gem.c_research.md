<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_gem.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_gem.c

## Purpose
Implements Lima GEM buffer creation, heap-buffer growth, VM attachment, mmap/vmap/pin restrictions, submission dependency handling, scheduler queuing, reservation fences, and GEM wait.

## Important APIs, types, and functions
Public APIs are `lima_heap_alloc()`, `lima_gem_create_handle()`, `lima_gem_create_object()`, `lima_gem_get_info()`, `lima_gem_submit()`, and `lima_gem_wait()`. GEM object hooks include free/open/close/pin/vmap/mmap. Dependency helpers are `lima_gem_sync_bo()` and `lima_gem_add_deps()`.

## Control flow
Create allocates a shmem GEM object, forces DMA32 pages, optionally initializes a growable heap BO, otherwise pins/maps pages through shmem, creates a handle, and drops the allocation reference. Object open adds the BO to the file VM, close removes it. Heap allocation doubles committed size up to BO size, faults shmem pages, maps SG tables for DMA, maps newly added pages into the VM, and updates `heap_size`. Submit resolves optional output syncobj, looks up each BO, pins VM mappings by incrementing BO-VA references, locks reservations, initializes a scheduler task, adds explicit or implicit dependencies, queues the task, attaches the returned fence to BO reservations with read/write usage, unlocks, drops refs, and updates output syncobj.

## State and persistence
`struct lima_bo` stores shmem object, lock, VA list, and heap size. BO-to-VM mappings persist while open handles or executing tasks hold references. DMA reservation fences persist for synchronization. Heap BO committed size can grow across recoverable GP out-of-memory interrupts.

## Dependencies and integration points
Depends on DRM GEM shmem, DMA mapping, syncobj, DRM scheduler, Lima VM, scheduler task API, IOCTL submit parsing, and module parameter `lima_heap_init_nr_pages`.

## Risks
Heap BOs cannot be pinned, vmapped, or mmaped; callers must respect that. Error unwind must drop BO VM refs and object refs exactly once. Explicit sync bypasses implicit dependencies, so userspace must supply correct fences. SG table replacement during heap growth must keep DMA mappings and VM mappings consistent.

## Test signals
Test GEM create/info/mmap, heap BO growth during GP recovery, submit with read/write BO flags, explicit and implicit fences, output syncobj replacement, invalid handles, reservation-lock failure injection, and GEM wait timeout conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_gem.c -->
