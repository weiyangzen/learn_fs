# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_connector.c

## Purpose
Provides connector-generic allocation, cleanup, registration, encoder attachment, mode retrieval, retry work, and common DRM connector property helpers for the i915 display driver.

## Important APIs and functions
Lifecycle functions include `intel_connector_alloc()`, `intel_connector_free()`, `intel_connector_destroy()`, `intel_connector_register()`, and `intel_connector_unregister()`. Runtime helpers include `intel_connector_attach_encoder()`, `intel_connector_get_hw_state()`, `intel_connector_get_pipe()`, `intel_connector_update_modes()`, `intel_ddc_get_modes()`, and modeset retry work queue/cancel helpers. Property attachers create or attach force-audio, Broadcast RGB, aspect ratio, HDMI/DP colorspace, and scaling mode properties.

## Control flow
Allocation zeroes the connector, allocates an oversized digital connector state, resets DRM atomic state, initializes panel allocation, and sets retry work. Retry work takes a connector ref, marks link status BAD under the mode config mutex, sends a hotplug event, then drops the ref. Destroy frees EDID, HDCP, panel, DRM connector state, MST port refs, and the connector object. Mode helpers read EDID over DDC, update connector EDID state, and add modes.

## State and integration
State includes connector DRM state, panel data, `detect_edid`, HDCP state, MST port reference, attached encoder pointer, polled mode, and display-wide cached property objects. Dependencies include DRM EDID/probe helpers, i2c, panel, HDCP, debugfs, and connector state types.

## Risks and test signals
Risks include refcount imbalance around retry work, connector state size assumptions, missed work cancellation during destroy, stale shared property objects, and mode_config locking mistakes. Test signals include hotplug retry tests, connector registration/unregistration, EDID mode enumeration, MST teardown, and KASAN/refcount checks.
