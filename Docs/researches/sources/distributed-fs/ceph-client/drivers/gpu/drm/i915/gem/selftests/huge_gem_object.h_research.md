# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gem/selftests/huge_gem_object.h

## Purpose
This header declares the huge GEM selftest object constructor and inline accessors for the synthetic object's physical and DMA sizes.

## Important APIs, Types, and Functions
It declares `huge_gem_object(struct drm_i915_private *i915, phys_addr_t phys_size, dma_addr_t dma_size)`. Inline helpers `huge_gem_object_phys_size` and `huge_gem_object_dma_size` return `obj->scratch` and `obj->base.size`.

## Control Flow
There is no executable control flow beyond the inline accessors. The constructor implementation in `huge_gem_object.c` validates sizes and creates the synthetic object.

## State and Persistence Behavior
The header documents that `obj->scratch` is used as the real physical backing size while `obj->base.size` is the larger DMA-visible GEM size. It stores no state itself.

## Dependencies and Integration Points
It includes Linux types and GEM object type definitions, forward-declares `drm_i915_private`, and is consumed by i915 selftests needing large object fixtures.

## Risks
The accessors depend on the selftest object's convention of storing physical size in `scratch`; using them on other GEM objects would be invalid.

## Test Signals
Build coverage and selftests that compare accessor values against constructor arguments validate this header.
