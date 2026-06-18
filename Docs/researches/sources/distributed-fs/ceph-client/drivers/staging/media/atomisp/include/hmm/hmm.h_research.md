# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/include/hmm/hmm.h

## Purpose
This header declares the high-level Host Memory Manager interface used by AtomISP/CSS code to allocate, map, copy, flush, and free ISP-addressable memory. It abstracts `hmm_bo` buffer-object management and exposes allocations as `ia_css_ptr` ISP virtual addresses.

## Important APIs, Types, And Functions
- `hmm_init()` and `hmm_cleanup()` initialize and tear down the global HMM buffer-object device.
- `hmm_alloc()` allocates private ISP-addressable memory, while `hmm_create_from_vmalloc_buf()` wraps an existing vmalloc buffer.
- `hmm_free()`, `hmm_load()`, `hmm_store()`, `hmm_set()`, and `hmm_flush()` provide allocation lifetime and CPU-side data movement/cache operations by ISP virtual address.
- `hmm_virt_to_phys()` resolves an ISP virtual address to a physical address for lower-level hardware programming.
- `hmm_vmap()`, `hmm_vunmap()`, and `hmm_flush_vmap()` expose BO pages as contiguous kernel virtual memory.
- `hmm_mmap()` maps an HMM allocation into a user VMA for video node mmap paths.
- `bo_device` is declared as the global `struct hmm_bo_device` backing this API.

## Control Flow
Typical use is initialize HMM at device startup, allocate an `ia_css_ptr`, transfer or map data with load/store/set/vmap/mmap, flush caches/TLB-relevant mappings where needed, and free the pointer at teardown. The comments require `hmm_vmap()`, `hmm_vunmap()`, and `hmm_mmap()` callers to pass the allocation start address returned by `hmm_alloc()`, not arbitrary interior addresses.

## State And Persistence
State is centralized in the global `bo_device`, whose internals are declared in `hmm_bo.h`. Allocations persist as ISP virtual address ranges plus backing pages until `hmm_free()`. There is no file persistence.

## Dependencies And Integration Points
The API depends on Linux memory management types, `hmm_common.h`, `hmm_bo.h`, and CSS `ia_css_types.h`. It integrates with AtomISP PCI/CSS memory paths, MMU mapping, vmap-based kernel access, cache maintenance, and V4L2 mmap handling.

## Risks
- The API exposes raw ISP virtual addresses; wrong or stale `ia_css_ptr` values can address the wrong BO unless implementations validate range ownership.
- Start-address-only requirements for vmap/vunmap/mmap are easy to violate from callers that hold interior offsets.
- Cache coherency depends on correct `hmm_flush()`/`hmm_flush_vmap()` use around CPU/ISP sharing.
- The global `bo_device` implies device-global state, so init/cleanup ordering and multi-device assumptions are important.

## Test Signals
Useful tests include alloc/free leak checks, load/store/set round trips, vmalloc-backed buffer import, vmap/vunmap reference behavior, mmap size validation, virt-to-phys mapping consistency, cache flush behavior under CPU/ISP sharing, and negative tests for null, freed, and interior ISP addresses.
