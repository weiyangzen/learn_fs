# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_memcpy.h

## Purpose
Declares accelerated WC memcpy helpers and convenience probes for capability/alignment.

## Important APIs, types, and functions
Exports `i915_memcpy_init_early()`, `i915_memcpy_from_wc()`, `i915_unaligned_memcpy_from_wc()`, and macros `i915_can_memcpy_from_wc()` and `i915_has_memcpy_from_wc()`.

## Control flow
The macros call `i915_memcpy_from_wc()` with synthetic low-bit arguments or NULL/zero arguments to test alignment and static-key availability without copying.

## State and persistence
No state in the header. Runtime capability lives in the implementation static key.

## Dependencies and integration points
Included by GEM/display readback code needing WC copy acceleration.

## Risks
The capability macros rely on implementation behavior that returns false for low-bit alignment failures and true for zero-length supported fast path. Changing that contract can break callers.

## Test signals
Build and runtime checks for macro results on SSE4.1 bare metal, hypervisors, and misaligned offsets.
