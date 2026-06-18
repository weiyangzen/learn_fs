# sources/distributed-fs/ceph-client/drivers/misc/mei/gsc_proxy/Kconfig

## Purpose
This Kconfig file defines `CONFIG_INTEL_MEI_GSC_PROXY`, the MEI client driver for Intel GSC proxy services.

## Important APIs, Types, and Functions
The symbol is tristate, depends on `INTEL_MEI_ME`, and requires `DRM_I915`, `DRM_XE`, or `COMPILE_TEST` availability.

## Control Flow
When selected, the build includes the GSC proxy MEI bus client that lets Intel graphics proxy messages between GSC service and CSE/ME firmware.

## State and Persistence
No runtime state is defined here.

## Dependencies and Integration Points
Integrates GSC proxy support with MEI ME hardware and Intel graphics drivers.

## Risks
The dependency must keep proxy code aligned with graphics component interfaces; enabling without a compatible graphics stack is limited to compile testing.

## Test Signals
Signals are correct menu visibility, module build when selected, and dependency behavior for i915, xe, and compile-test configurations.
