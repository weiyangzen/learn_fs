# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_late_bind_fw.h

## Purpose
`xe_late_bind_fw.h` exposes the minimal late-bind firmware lifecycle API to the rest of the Xe driver.

## Important APIs, Types, And Functions
- Forward-declares `struct xe_late_bind`.
- Declares initialization, load/reload, and worker-flush helpers.

## Control Flow
Callers initialize late-bind support through `xe_late_bind_init()`, may request payload load with `xe_late_bind_fw_load()`, and can synchronize pending work with `xe_late_bind_wait_for_worker_completion()`.

## State And Persistence
The header owns no state; it operates on `struct xe_late_bind` defined in the types header.

## Dependencies And Integration Points
It depends only on Linux types and is included by Xe device/PM paths that coordinate late-bind firmware.

## Risks
Callers need to understand that `xe_late_bind_fw_load()` can queue async work and success does not mean the firmware has already reached MEI. The flush helper must be used before component teardown or other operations that invalidate payload/component state.

## Test Signals
Build coverage and PM/component teardown tests that call the flush path before removing the component.
