# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_hdcp.h

## Purpose
Declares the DisplayPort HDCP initialization API for i915 digital ports and connectors.

## Important APIs, types, and functions
- Forward declares `struct intel_connector` and `struct intel_digital_port`.
- Exports `int intel_dp_hdcp_init(struct intel_digital_port *dig_port, struct intel_connector *intel_connector);`.

## Control flow
No runtime control flow exists in the header. It exposes the implementation file's shim installation function to DP and MST connector setup code.

## State and persistence
No state is stored here. Calling the declared function initializes connector HDCP state through the generic `intel_hdcp_init()` path when the platform and connector type support it.

## Dependencies and integration points
Integrated by `intel_dp.c` for SST DP connectors and by `intel_dp_mst.c` for dynamically created MST connectors. The header intentionally hides all HDCP 1.x/2.2 transport helper details.

## Risks
The include guard name has a triple underscore suffix but is internally consistent. API expansion should remain cautious because the transport shim is meant to stay private.

## Test signals
Build coverage catches signature drift. Runtime validation belongs to `intel_dp_hdcp.c` through successful HDCP initialization and authentication.
