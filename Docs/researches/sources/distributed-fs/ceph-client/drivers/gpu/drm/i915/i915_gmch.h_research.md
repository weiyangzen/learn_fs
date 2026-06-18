# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_gmch.h

## Purpose
This header declares GMCH bridge and MCHBAR setup/teardown helpers.

## Important APIs, Types, and Functions
It declares `i915_gmch_bridge_setup()`, `i915_gmch_bar_setup()`, and `i915_gmch_bar_teardown()`.

## Control Flow
There is no control flow. `i915_driver.c` calls setup during MMIO probe and teardown during MMIO release/failure unwind.

## State and Persistence Behavior
The header stores no state; implementation updates `i915->gmch`.

## Dependencies and Integration Points
It forward-declares `struct drm_i915_private` and links driver probe code to legacy GMCH support.

## Risks
The setup/teardown pairing is ordering-sensitive around runtime info and uncore register access.

## Test Signals
Build coverage and legacy platform probe/unload testing.
