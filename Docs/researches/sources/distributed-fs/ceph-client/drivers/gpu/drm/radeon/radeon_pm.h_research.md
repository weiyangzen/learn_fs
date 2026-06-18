# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_pm.h

## Purpose

`radeon_pm.h` is a very small private Radeon PM header. In this tree it exposes only `radeon_pm_acpi_event_handler()` to other Radeon compilation units, keeping most PM implementation details in `radeon_pm.c` or in broader internal headers such as `radeon.h`.

## Important APIs, Types, And Functions

- Header guard: `__RADEON_PM_H__`.
- Prototype: `void radeon_pm_acpi_event_handler(struct radeon_device *rdev);`
- The declaration relies on `struct radeon_device` being visible or forward-declared by the includer; the header does not include `radeon.h` itself.

## Control Flow

There is no runtime control flow in the header. Its only role is compile-time linkage: users such as `radeon_acpi.c` include it so ACPI power-source or platform events can be forwarded into the PM implementation in `radeon_pm.c`.

## State And Persistence Behavior

The header owns no state and persists nothing. It gives callers access to a function that mutates runtime PM state inside `struct radeon_device`, but the state lives outside this file.

## Dependencies And Integration Points

The key integration is between ACPI/platform notification code and Radeon PM. Because the header is intentionally narrow, other PM entry points are declared elsewhere or kept local, reducing the amount of PM surface exposed through this private include.

## Risks And Edge Cases

- The header depends on include order for `struct radeon_device`; adding standalone prototypes using other types would require forward declarations or includes.
- The narrow API is good for encapsulation, but it can be confusing because `radeon_pm.c` exports additional non-static symbols, such as `radeon_pm_get_type_index()`, through other headers.
- Any signature change must be synchronized with `radeon_acpi.c` and the implementation.

## Test Signals

Compile coverage is the main signal. A missing declaration or include-order regression would surface as build failures in ACPI-enabled Radeon objects. Runtime validation belongs to the `radeon_pm_acpi_event_handler()` path: AC/battery events should update DPM/profile policy without touching powered-off PX hardware.
