<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_encoder.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_encoder.h

## Purpose
This header declares generic i915 encoder helper APIs shared by output-specific encoder implementations.

## Important APIs, Types, and Functions
It forward declares `struct intel_digital_port`, `struct intel_display`, and `struct intel_encoder`. Declarations cover link-check work management, suspend/shutdown fan-out, HPD block/unblock fan-out, and digital port allocation.

## Control Flow
There is no implementation flow. The header defines the call surface for encoder lifecycle and workqueue helpers.

## State and Persistence Behavior
No state is stored here; the functions operate on persistent encoder and digital-port structures.

## Dependencies and Integration Points
It is included by DP/HDMI, hotplug, suspend, and display probe code that needs generic encoder helpers without pulling in implementation details.

## Risks
Callers must flush delayed work before freeing encoders. Allocation callers must complete port-specific initialization after `intel_dig_port_alloc()` sets only generic defaults.

## Test Signals
Compile coverage and lifecycle tests that exercise helper declarations from multiple encoder implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_encoder.h -->
