# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_connector.h

## Purpose
Declares connector-generic i915 helpers for lifecycle, encoder association, EDID/mode handling, common properties, and modeset retry work.

## APIs and integration
It exposes allocation/free/destroy/register/unregister helpers, `intel_connector_attach_encoder()`, hardware-state and pipe queries, EDID update/DDC mode helpers, property attachers, and retry work queue/cancel routines. Connector implementations such as CRT, HDMI, DP, LVDS, and eDP use this shared interface.

## State, risks, and tests
The header owns no state, but declared functions manipulate DRM connector state, i915 connector fields, shared properties, and workqueue references. Risks are incorrect callback wiring or missing cancellation before teardown. Compile coverage plus connector hotplug/mode enumeration tests exercise the contract.
