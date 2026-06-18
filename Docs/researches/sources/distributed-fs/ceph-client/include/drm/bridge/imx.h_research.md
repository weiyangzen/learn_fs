# sources/distributed-fs/ceph-client/include/drm/bridge/imx.h

Purpose: small compatibility helper interface for creating devm-managed legacy i.MX DRM bridges from device tree nodes.

Important APIs/types/functions: `devm_imx_drm_legacy_bridge(struct device *dev, struct device_node *np, int type)` plus forward declarations for `struct device`, `struct device_node`, and `struct drm_bridge`.

Control flow: callers pass a device, OF node, and bridge type; the implementation creates/registers a managed bridge whose lifetime follows the parent device.

State and persistence: no header state. Bridge runtime state is allocated by the implementation and released by devres.

Dependencies and integration points: device tree, devres, i.MX legacy display pipelines, and DRM bridge chains.

Risks and test signals: wrong type values, stale OF assumptions, and returned bridge lifetime misuse are the main risks. Test invalid nodes, probe deferral, device removal, and legacy i.MX attach order.
