# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_display_rpm.h

## Purpose
This header exposes display runtime PM helpers and a scoped helper macro for holding a display RPM wakeref. It keeps display code independent of parent-driver runtime PM details.

## Important APIs, Types, and Functions
Public functions mirror the implementation wrappers: normal `get/put`, raw `get_raw/put_raw`, `get_if_in_use`, `get_noresume`, `put_unchecked`, `intel_display_rpm_suspended()`, and assertion block/unblock helpers. `with_intel_display_rpm(display)` expands to a `for` loop that gets a wakeref, runs a scoped block, and puts the wakeref exactly once.

## Control Flow
The header only defines declarations and macros. The scoped macro uses `__UNIQUE_ID(wakeref)` to avoid local variable collisions and uses the loop increment expression to release the wakeref.

## State and Persistence Behavior
No state lives here. The API exposes `struct ref_tracker *` ownership to callers and creates a scope-based lifetime for wakerefs.

## Dependencies and Integration Points
It forward-declares `struct intel_display` and `struct ref_tracker`, and includes Linux types. It is consumed throughout display code before MMIO or parent operations that require runtime resume.

## Risks
The scoped macro is only safe when used as a block-like construct; control flow that exits abnormally must still respect C cleanup behavior. Raw, noresume, and unchecked helpers should remain restricted to display power implementation or carefully audited paths.

## Test Signals
Build coverage confirms prototypes. Runtime PM leak detection, lockdep, and suspend/resume tests are the meaningful validation signals.
