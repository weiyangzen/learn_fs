# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_acpi.h

## Purpose

`intel_acpi.h` declares the i915 display ACPI integration hooks and supplies no-op stubs when ACPI support is disabled. It is the boundary between generic display bring-up code and ACPI-specific connector, DSM, and backlight behavior.

## Important APIs, Types, And Functions

The header forward declares `struct intel_display`. With `CONFIG_ACPI`, it declares `intel_register_dsm_handler()`, `intel_unregister_dsm_handler()`, `intel_dsm_get_bios_data_funcs_supported()`, `intel_acpi_device_id_update()`, `intel_acpi_assign_connector_fwnodes()`, and `intel_acpi_video_register()`. Without `CONFIG_ACPI`, inline stubs return immediately.

## Control Flow

There is no standalone control flow. Display initialization and cleanup can call these functions unconditionally; the preprocessor selects real ACPI behavior or no-op stubs.

## State And Persistence Behavior

The header stores no state. Real implementations update connector ACPI IDs, connector fwnode references, and ACPI video/backlight registration. Stub builds intentionally leave those states untouched.

## Dependencies And Integration Points

The header avoids including ACPI headers directly and depends only on the forward declaration of `intel_display`. It integrates ACPI support with the rest of i915 while keeping non-ACPI builds simple.

## Risks And Edge Cases

Callers must tolerate no-op behavior in non-ACPI builds. Any future function that needs a return value should define a meaningful stub result rather than silently hiding an error. Since connector fwnodes and ACPI IDs are absent in stub builds, user-space or tests expecting firmware-node metadata must account for `CONFIG_ACPI`.

## Test Signals

Build tests with `CONFIG_ACPI=y` and `CONFIG_ACPI=n`, boot tests verifying connector metadata on ACPI systems, and static checks for unconditional call sites are the main signals.
