# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_edram.h

## Purpose
This header declares the eDRAM detection helper used during i915 hardware probe.

## Important APIs, Types, and Functions
The only API is `void i915_edram_detect(struct drm_i915_private *i915)`.

## Control Flow
There is no internal flow. Callers invoke the function before later feature predicates and cache policy code depend on `i915->edram_size_mb`.

## State and Persistence Behavior
The header stores no state; the implementation updates `drm_i915_private`.

## Dependencies and Integration Points
It forward-declares `struct drm_i915_private` and is included by `i915_driver.c` and other code that needs explicit eDRAM probing.

## Risks
The include guard says `__I915_DRAM_H__`, which is harmless but easy to confuse with DRAM-related display code. Signature changes must match the implementation.

## Test Signals
Build coverage and successful hardware probe with eDRAM detection are sufficient signals.
