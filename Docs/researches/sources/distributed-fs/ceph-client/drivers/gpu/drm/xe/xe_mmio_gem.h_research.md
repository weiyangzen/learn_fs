
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_mmio_gem.h

## Purpose

`xe_mmio_gem.h` declares the small MMIO-to-GEM wrapper API used by Xe code that needs to hand a safe MMIO mmap offset to userspace.

## Important APIs, Types, and Functions

It forward declares `struct xe_mmio_gem` and exposes `xe_mmio_gem_create()`, `xe_mmio_gem_mmap_offset()`, and `xe_mmio_gem_destroy()`.

## Control Flow

Callers create an object for a page-aligned physical range, retrieve the fake mmap offset, communicate it through a driver-specific interface, and destroy the object when the exposure is no longer needed.

## State and Persistence Behavior

State lives in the opaque implementation object. The header makes ownership explicit enough that callers are responsible for balancing create/destroy.

## Dependencies and Integration Points

It depends only on Linux types and forward declarations for DRM file and Xe device types.

## Risks and Edge Cases

The header does not encode the security policy for which registers may be exposed; all policy remains with callers.

## Test Signals

Compile tests should catch API drift. Integration tests should verify callers balance create/destroy and do not leak mmap offsets after teardown.
