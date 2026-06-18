# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_gem.c

## Purpose

`radeon_gem.c` implements Radeon GEM object creation, lifetime hooks, mmap/fault handling, userptr support, domain and tiling IOCTLs, buffer busy/wait queries, GPU virtual-address mapping, dumb-buffer creation, and GEM debugfs reporting. It bridges DRM GEM APIs to Radeon BO/TTM memory management and per-file GPUVM state.

## Important APIs, Types, and Functions

- `radeon_gem_object_create()` validates size/alignment, applies the unpinned-GTT maximum, creates a Radeon BO, records the creating PID, and tracks it in `rdev->gem.objects`.
- `radeon_gem_object_funcs` wires free/open/close/export/pin/unpin/sg-table/vmap/mmap/vm-ops into DRM GEM.
- `radeon_gem_fault()` handles CPU faults under `pm.mclk_lock`, reserves the TTM BO, applies Radeon fault notification, and delegates to TTM fault handling.
- IOCTLs include GEM info/create/userptr/set-domain/mmap/busy/wait-idle/set-tiling/get-tiling/VA/op and dumb create/map.
- `radeon_gem_object_open()` and `radeon_gem_object_close()` maintain per-file VM BO references for Cayman+ acceleration.
- `radeon_gem_va_update_vm()` locks VM-related BOs with `drm_exec`, clears freed VM entries, and updates page tables opportunistically.

## Control Flow

Creation IOCTLs take `exclusive_lock`, round sizes, create BOs, export handles, and translate `-EDEADLK` through `radeon_gem_handle_lockup()` to reset/retry behavior. Userptr creation validates page alignment and flags, rejects unsafe writable non-anonymous or unregistered mappings, creates a CPU-domain BO, installs the user pointer and optional MMU notifier, optionally validates into GTT under `mmap_read_lock()`, and returns a GEM handle. VA IOCTL validates VM availability, reserved address ranges, flags, and operation, finds the per-file `bo_va`, maps or unmaps it, and updates VM page tables if possible.

## State and Persistence Behavior

GEM state persists in Radeon BOs, DRM handles, TTM reservation objects, per-file `radeon_vm` BO-VA records, userptr/MMU notifier registration, tiling flags, initial domain, and the debug list `rdev->gem.objects`. CPU fault handling temporarily holds `pm.mclk_lock` to coordinate memory-clock changes with CPU access. Many IOCTLs read current TTM placement from `robj->tbo.resource`.

## Dependencies and Integration Points

The file depends on DRM GEM/TTM helpers, dma-buf PRIME hooks from `radeon_prime.c`, Radeon BO and placement APIs, MMU notifier/userptr support, GPUVM code, `drm_exec`, reservation objects, fence/reset behavior, debugfs, and mode/fbdev paths that use dumb buffers and mmap offsets.

## Risks and Edge Cases

- Userptr writable mappings require anonymous memory plus MMU notifier registration; relaxing this risks stale DMA mappings.
- Imported/shared BOs cannot be migrated to VRAM in some paths, and userptr BOs are blocked from mmap/op operations.
- `radeon_gem_va_update_vm()` treats update errors as non-fatal, so failures may surface later at command submission.
- Object close can leak BO-VA state if reservation fails.
- Size limits depend on unpinned GTT size; large VRAM-only expectations can fail or fall back to GTT during creation.

## Test Signals

Test GEM create limits and VRAM-to-GTT fallback, PRIME import/export restrictions, CPU mmap faults, busy/wait-idle with HDP flush, userptr flag validation/MMU notifier invalidation, tiling set/get, VM map/unmap reserved-range rejection, close/open VM refcounts, reset-on-`-EDEADLK`, dumb buffer pitch/size, and debugfs object reporting.
