# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_jiffies.h

## Purpose
Provides a timeout conversion helper that avoids zero-jiffy timeouts for positive millisecond values.

## Important APIs, types, and functions
Defines `msecs_to_jiffies_timeout(unsigned int m)`, which calls `msecs_to_jiffies(m)` and returns `min(MAX_JIFFY_OFFSET, j + 1)`.

## Control flow
Inline conversion only. Adding one jiffy gives callers a full timeout interval rather than immediate expiry after rounding.

## State and persistence
No state.

## Dependencies and integration points
Depends on Linux jiffies helpers and is usable by i915 wait/poll code needing conservative timeouts.

## Risks
For very large inputs, saturation at `MAX_JIFFY_OFFSET` avoids overflow. For zero input, the helper still returns one jiffy, so callers needing immediate/no wait should not use it.

## Test signals
Unit or compile-time checks for zero, small positive, and near-maximum millisecond values.
