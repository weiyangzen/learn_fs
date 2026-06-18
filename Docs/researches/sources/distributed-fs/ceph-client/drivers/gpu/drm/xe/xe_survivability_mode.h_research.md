<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_survivability_mode.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_survivability_mode.h

## Purpose

`xe_survivability_mode.h` declares the public survivability-mode control and query functions.

## Important APIs, Types, and Functions

The header exposes boot enable, runtime enable, boot-enabled query, and requested query functions.

## Control Flow

Probe code calls the requested/boot-enable path when normal initialization detects incomplete pcode or a manual configfs request. Runtime error handling calls runtime enable when firmware recovery requires a flash.

## State and Persistence Behavior

These functions read and mutate `xe->survivability` state and sysfs presence; the header owns no state.

## Dependencies and Integration Points

It depends on Linux types and forward-declares `struct xe_device`. It integrates with probe, wedging, and firmware recovery code.

## Risks and Test Signals

Callers must respect platform support and the reduced boot-mode lifecycle. Tests should verify unsupported platforms return false or `-EINVAL` as appropriate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_survivability_mode.h -->
