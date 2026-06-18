# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/i915_gem_phys.c

## Purpose
Tests conversion of a shmem GEM object to physically contiguous backing through the i915 physical-object API.

## APIs And Control Flow
Defines `mock_phys_object()` and registers it through `i915_gem_phys_mock_selftests()`. The test creates a one-page shmem object, verifies it starts with struct pages, attaches physical backing via `i915_gem_object_attach_phys()`, checks that normal struct-page backing is gone, verifies the physical pages are pinned, and marks the object dirty through the GTT domain so release must copy data back.

## State, Dependencies, Integration, Risks, And Tests
State is the mock device and object page/pin metadata. Dependencies include object locking, physical attach logic, page pin-count tracking, and GTT domain transition. Risks include mixed physical/struct-page state, leaked pins, or skipped dirty copyback. Signals are failed attach, unexpected struct-page backing, missing pins, and dirtying failures.
