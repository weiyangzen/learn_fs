# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_rpm.c

## Purpose
This file is a thin display-side adapter for runtime power management. It forwards display RPM get/put/assert operations through the parent display interface so common display code can be shared between i915 and Xe parent implementations.

## Important APIs, Types, and Functions
The exported wrappers are `intel_display_rpm_get_raw()`, `intel_display_rpm_put_raw()`, `intel_display_rpm_get()`, `intel_display_rpm_get_if_in_use()`, `intel_display_rpm_get_noresume()`, `intel_display_rpm_put()`, `intel_display_rpm_put_unchecked()`, `intel_display_rpm_suspended()`, `assert_display_rpm_held()`, and `intel_display_rpm_assert_block()/unblock()`. All use `display->parent->rpm` callbacks and pass `display->drm`.

## Control Flow
There is no local branching other than the parent callback call chain. Each function delegates to the matching parent RPM operation, so all wake reference creation, ref tracking, noresume behavior, and assertion semantics are owned by the parent implementation.

## State and Persistence Behavior
This file does not own RPM state. It moves `struct ref_tracker *` wake references between caller and parent runtime PM code. Correct pairing of `get` and `put` calls controls whether display MMIO/power domains can autosuspend.

## Dependencies and Integration Points
It includes `drm/intel/display_parent_interface.h`, `intel_display_core.h`, and its public header. It integrates with display code that needs a runtime PM wakeref before MMIO access, power-domain logic, and parent driver implementations for i915/Xe.

## Risks
Because the wrappers are direct callbacks, a missing or mismatched parent `rpm` method will crash or corrupt wakeref accounting. `put_unchecked()` and raw/noresume variants are special-case APIs and can hide unbalanced references if used casually. Callers must hold a wakeref around MMIO paths that may run while runtime suspended.

## Test Signals
Signals include runtime PM selftests, suspend/autosuspend cycles, ref-tracker leak reports, `assert_display_rpm_held()` coverage around MMIO, and display operation success under aggressive runtime PM.
