# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/opregion.h

## Purpose
This header provides the OpRegion function declarations and no-op fallbacks when ACPI support is disabled.

## Important APIs, Types, and Functions
When `CONFIG_ACPI` is enabled it declares `psb_intel_opregion_asle_intr()`, `psb_intel_opregion_init()`, `psb_intel_opregion_fini()`, `psb_intel_opregion_setup()`, and `psb_intel_opregion_enable_asle()`. Without ACPI it supplies inline stubs; setup returns `0` and all other functions do nothing.

## Control Flow
There is no runtime flow in the enabled-declaration case. In non-ACPI builds, callers execute local stubs so driver load/unload paths can remain unconditional.

## State and Persistence Behavior
The header has no state. In ACPI builds the implementation stores mapped OpRegion pointers in `drm_psb_private`; in non-ACPI builds no OpRegion state is created.

## Dependencies and Integration Points
The header lets `psb_drv.c`, `psb_device.c`, and `oaktrail_device.c` call OpRegion setup/init/fini/ASLE helpers without preprocessor branches.

## Risks
The non-ACPI `psb_intel_opregion_setup()` returning success can hide absence of OpRegion functionality from callers. The inline stubs are declared `extern inline`, which can be sensitive to compiler inline semantics.

## Test Signals
Build both ACPI and non-ACPI configurations. ACPI builds should link to `opregion.c`; non-ACPI builds should load without unresolved symbols and simply skip OpRegion behavior.
