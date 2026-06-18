# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_dsb_buffer.h

## Purpose
This header exposes the i915 implementation of the display DSB buffer interface to display parent-interface wiring.

## Important APIs, Types, and Functions
It declares `extern const struct intel_display_dsb_interface i915_display_dsb_interface`.

## Control Flow
There is no control flow. Display code receives this interface through `i915_driver_parent_interface()` and calls the function pointers implemented in `i915_dsb_buffer.c`.

## State and Persistence Behavior
The header stores no state. The exported interface object is static storage in the implementation file.

## Dependencies and Integration Points
The header intentionally avoids including the display interface definition and relies on external declarations. It integrates i915 GEM-backed DSB buffers with split display code.

## Risks
Signature drift in `intel_display_dsb_interface` will surface at build time in `i915_dsb_buffer.c`. The header is minimal; adding includes can expand dependencies.

## Test Signals
Build i915 display code and run display DSB modeset/update paths that consume the interface.
