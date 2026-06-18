# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_hdcp_gsc.h

## Purpose
This header exposes the i915 implementation of the display HDCP GSC interface.

## Important APIs, Types, and Functions
It declares `extern const struct intel_display_hdcp_interface i915_display_hdcp_interface`.

## Control Flow
There is no control flow. Display HDCP code obtains this interface through the display parent interface and invokes callbacks implemented in `i915_hdcp_gsc.c`.

## State and Persistence Behavior
The header stores no state. The implementation owns per-transaction/per-context state.

## Dependencies and Integration Points
It is a lightweight bridge between i915 core and split display HDCP/GSC code.

## Risks
Signature drift in `intel_display_hdcp_interface` must be reflected in the implementation. The header should remain dependency-light.

## Test Signals
Build coverage and HDCP GSC runtime tests on supported platforms.
