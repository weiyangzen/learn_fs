# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/i915_gem_migrate.c

## Purpose
Tests GEM object migration between system memory and local memory, including content preservation, failure fallback, asynchronous unbind behavior, and reset behavior under injected GPU/memcpy/allocation failures.

## APIs And Control Flow
Important routines are `igt_fill_check_buffer()`, `igt_create_migrate()`, `lmem_pages_migrate_one()`, `__igt_lmem_pages_migrate()`, `igt_lmem_pages_failsafe_migrate()`, `igt_async_migrate()`, and `igt_lmem_async_migrate()`. Tests fill predictable dword patterns, migrate objects across regions, pin pages, wait for moving fences, verify contents, toggle TTM failure modes, and use spinner dependencies to prove migration unbinds can be scheduled asynchronously.

## State, Dependencies, Integration, Risks, And Tests
State is transient in GEM objects, LMEM/SMEM placement, moving fences, VMAs, dependency sets, spinners, and GT wedge/reset flags. Dependencies include `intel_migrate_clear()`, `i915_gem_object_migrate()`, TTM move failure injection, reset helpers, and spinner infrastructure. Risks are intended GT wedging during failure injection, deadlocks if async unbind becomes synchronous, and wrong coherent map type for validation. Signals include region/data mismatches, unexpected failure/success, wrong wedge state, spinner hangcheck termination, and stale moving fences.
