# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/i915_gem_tiling.h

## Purpose
This header declares the core tiling helpers shared outside the tiling ioctl implementation.

## Important APIs, Types, and Functions
It declares `i915_gem_object_needs_bit17_swizzle`, `i915_gem_fence_size`, and `i915_gem_fence_alignment`, with forward declarations for GEM object and i915 private types.

## Control Flow
No executable logic is present. The declarations expose generation-specific fence sizing/alignment and bit17 swizzle detection implemented in `i915_gem_tiling.c`.

## State and Persistence Behavior
The header has no state. The declared functions inspect object tiling and platform GGTT swizzle state or compute fence geometry.

## Dependencies and Integration Points
Users include shmem page setup/release, physical object conversion checks, and code that needs GTT fence constraints for tiled objects.

## Risks
Consumers must pass valid tiling/stride combinations; implementation uses `GEM_BUG_ON` for invalid internal inputs. Misusing bit17 swizzle detection can cause data corruption after page migration or swap.

## Test Signals
Build coverage plus tiling, shmem swizzle, and phys-conversion tests validate this small interface.
