<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_object.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_object.h

## Purpose

`radeon_object.h` is the private public-facing header for Radeon BO and suballocation helpers. It defines inline domain/reservation/address helpers, declares the BO lifecycle/pinning/tiling/fencing APIs implemented in `radeon_object.c`, and declares suballocator manager functions used by IB and scratch allocation code.

## Important APIs, Types, and Functions

- `radeon_mem_type_to_domain(u32 mem_type)`: maps TTM memory placement types to Radeon GEM domains.
- `radeon_bo_reserve()` / `radeon_bo_unreserve()`: wrappers around TTM reservation with Radeon logging and signal behavior controlled by `no_intr`.
- `radeon_bo_gpu_offset()`: computes GPU address from TTM resource start plus VRAM or GTT aperture base.
- `radeon_bo_size()`, `radeon_bo_ngpu_pages()`, `radeon_bo_gpu_page_alignment()`, and `radeon_bo_mmap_offset()`: inline BO size/page/mmap queries.
- Extern BO APIs: create, kmap/kunmap, ref/unref, pin/unpin, evict/fini/init, list validation, tiling get/set/check, move/fault notifications, surface register acquisition, and fence insertion.
- Suballocation helpers `to_radeon_sa_manager()`, `radeon_sa_bo_gpu_addr()`, and `radeon_sa_bo_cpu_addr()`: convert DRM suballoc manager/objects into Radeon manager and CPU/GPU addresses.
- Extern suballocation APIs: manager init/start/suspend/fini, allocate/free, and debugfs dump.

## Control Flow

The inline helpers are called throughout command submission, modesetting, VM, and memory management. Reservation wrappers are typically the first step before mutating BO placement, pinning, or tiling state. GPU offset helpers are used after validation/pinning to populate relocations, scanout registers, and IB addresses. Suballocation address helpers convert an allocated offset inside a manager BO into CPU/GPU pointers for IB emission.

## State and Persistence Behavior

The header stores no state, but all helpers operate on persistent `struct radeon_bo`, `struct ttm_buffer_object`, `struct radeon_device`, and `struct radeon_sa_manager` state. `radeon_bo_reserve()` changes reservation ownership, `radeon_bo_gpu_offset()` reflects current placement, and suballocation helpers depend on manager base CPU/GPU addresses remaining valid.

## Dependencies and Integration Points

It includes Radeon core definitions and DRM UAPI domain constants, and it depends on TTM placement/resource fields, DRM VMA node helpers, DRM suballocator APIs, and Radeon memory-controller aperture bases. Consumers include GEM ioctl paths, KMS scanout, IB allocation, command submission validation, VM updates, TTM callbacks, and debugfs.

## Risks and Edge Cases

- `radeon_bo_gpu_offset()` assumes the BO has a valid TTM resource and is reserved or pinned enough to keep placement stable.
- `radeon_bo_reserve()` uses inverted interruptibility (`!no_intr`) for TTM and returns `-ERESTARTSYS` when interruptible waits are signaled; callers must unwind all reservations.
- GPU page alignment divides by Radeon GPU page size after converting TTM page alignment; mismatched page-size assumptions can affect VM mappings.
- Suballocation address helpers assume the suballoc belongs to a `radeon_sa_manager`; passing another manager type would corrupt container lookup.

## Test Signals

Build coverage across BO users catches signature drift. Runtime signals include reservation/unreservation under contention and signal interruption, correct GPU offsets in VRAM and GTT, mmap offsets for GEM handles, VM page-count/alignment calculations, IB suballocation CPU/GPU addresses, and debugfs suballocator dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_object.h -->
