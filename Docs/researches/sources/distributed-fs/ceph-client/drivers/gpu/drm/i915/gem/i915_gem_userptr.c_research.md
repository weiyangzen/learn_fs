# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_userptr.c

## Purpose
This file implements the i915 userptr GEM object type, which wraps page-aligned user virtual memory as a restricted proxy GEM object with MMU interval notifier validation and pinned user pages at submission time.

## Important APIs, Types, and Functions
Primary APIs are `i915_gem_object_userptr_submit_init`, `i915_gem_object_userptr_submit_done`, `i915_gem_object_userptr_validate`, and `i915_gem_userptr_ioctl`. Backend ops include `i915_gem_userptr_get_pages`, `i915_gem_userptr_put_pages`, release, and rejected dmabuf/pread/pwrite hooks. `probe_range` validates that a range maps normal struct-page VMAs.

## Control Flow
The ioctl checks platform snooping/LLC support, flags, size, page alignment, access_ok, synchronized mode, read-only hardware support, and optional VMA probing. With MMU notifier support it allocates a proxy object, sets CPU domains/cache coherency, stores the user pointer, marks read-only if requested, inserts an MMU interval notifier for current mm, creates a GEM handle, and drops the allocation ref.

Submission init verifies the object belongs to current mm, reads the notifier sequence, locks and unbinds old pages if needed, pins all user pages with `pin_user_pages_fast` and optional `FOLL_WRITE`, relocks, retries if the notifier invalidated the range, installs the page vector, and calls the backend get_pages. Submit done checks for notifier collision and returns `-EAGAIN` to force retry.

## State and Persistence Behavior
Object state includes `userptr.ptr`, `userptr.notifier`, `notifier_seq`, `pvec`, and `page_ref`. Pages are pinned only while active, converted into an SG table, marked accessed/dirty on release, and unpinned when the final page ref drops. The object is shrinkable, non-mappable by i915 CPU mmap, and marked proxy.

## Dependencies and Integration Points
It integrates with Linux MMU interval notifiers, GUP pinning, VMA iteration, GEM unbind/page helpers, shmem release semantics, GTT DMA mapping, reservation/submission retry paths, and UAPI `DRM_IOCTL_I915_GEM_USERPTR`.

## Risks
User memory lifetime is inherently racy; notifier sequence handling must force retries. Dirtying pages uses `trylock_page` to avoid migrate-folio deadlock, so dirty marking can be missed. Userptr export and CPU access ioctls are intentionally rejected. Unsynchronized userptr is disabled. Platforms without coherent snooping are rejected.

## Test Signals
Userptr ioctl validation, MMU invalidation retry tests, munmap/free while GPU active, read-only GPU mapping checks, GUP pin/unpin leak tests, dirty/accessed page accounting, probe rejection of PFNMAP/MIXEDMAP, and no-dmabuf/pread/pwrite ABI tests are important.
