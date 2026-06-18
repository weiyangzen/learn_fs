# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_freq.h

## Purpose
This header declares legacy i915 frequency decode helpers.

## Important APIs, Types, and Functions
It declares `i9xx_fsb_freq()`, `ilk_fsb_freq()`, and `ilk_mem_freq()`, all taking `struct drm_i915_private *` and returning unsigned integer frequencies.

## Control Flow
There is no control flow. Callers include the header when they need legacy strap/PLL decode helpers.

## State and Persistence Behavior
The header stores no state and only forward-declares the i915 private type.

## Dependencies and Integration Points
It is a lightweight interface between legacy display/bandwidth code and the implementation in `i915_freq.c`.

## Risks
Return units are implicit in implementation conventions and should be preserved by callers. Adding includes can create unnecessary coupling.

## Test Signals
Build coverage and runtime frequency decode on legacy hardware are the primary signals.
