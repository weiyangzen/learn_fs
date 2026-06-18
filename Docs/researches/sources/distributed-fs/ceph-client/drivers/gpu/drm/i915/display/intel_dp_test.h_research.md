# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_test.h

## Purpose
Declares the DisplayPort compliance test interface for i915 DP core, link configuration, PHY testing, short-pulse handling, and debugfs registration.

## Important APIs, types, and functions
- Forward declares `struct intel_dp`, `struct intel_display`, `struct intel_crtc_state`, and `struct link_config_limits`.
- Declares reset, request dispatch, config adjustment, PHY execution, short-pulse handling, and debugfs registration functions.

## Control flow
The header has no runtime control flow. It exposes the compliance-test lifecycle to DP hotplug and modeset code while keeping request parsing and debugfs implementation private.

## State and persistence
No state is defined here. The functions operate on `intel_dp->compliance` state and display debugfs roots in the implementation.

## Dependencies and integration points
Included by DP core, MST code for PHY master-transcoder handling, and the implementation file. It includes `linux/types.h` for `bool`.

## Risks
The API lets callers affect modeset limits and PHY programming based on compliance state. Calls should remain limited to DP compliance paths to avoid leaking test behavior into normal operation.

## Test signals
Compile coverage catches signature mismatch. Runtime signals are debugfs file presence and compliance behavior implemented in `intel_dp_test.c`.
