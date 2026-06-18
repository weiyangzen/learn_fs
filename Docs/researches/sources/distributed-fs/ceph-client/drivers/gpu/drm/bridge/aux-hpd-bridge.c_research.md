# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/aux-hpd-bridge.c

Purpose: Auxiliary-bus helper for a terminal DisplayPort HPD DRM bridge that can notify hotplug events for bridge chains without a full downstream bridge driver.

Important APIs/types/functions: Exported APIs are `devm_drm_dp_hpd_bridge_alloc`, `devm_drm_dp_hpd_bridge_add`, `drm_dp_hpd_bridge_register`, and `drm_aux_hpd_bridge_notify`. Internal state is `struct drm_aux_hpd_bridge_data`. Probe creates a bridge with `DRM_BRIDGE_OP_HPD` and connector type from auxiliary ID driver data.

Control flow: Allocation creates an auxiliary device named `dp_hpd_bridge`, stores an OF node in platform data, inherits parent OF node, initializes the auxiliary device, and ties uninit to devm cleanup. Add registers the auxiliary device and ties delete to devm cleanup. Probe allocates bridge data, sets bridge OF node, HPD ops, connector type, passthrough allowances, stores driver data, and devm-adds the bridge. Notify converts the device to its auxiliary driver data and calls `drm_bridge_hpd_notify`.

State and persistence: IDA IDs and OF references live for auxiliary-device lifetime. Bridge driver data is devm-managed. No persistent storage exists.

Dependencies and integration: Depends on auxiliary bus, OF, DRM bridge HPD notification, and aux-bridge public helpers. Parent drivers use the returned device to report HPD status from their own detection logic.

Risks: `drm_aux_hpd_bridge_notify` is a no-op before probe driver data exists, so early notifications may be dropped. Only NO_CONNECTOR attach is allowed. Correct OF-node ownership is split between `dev.of_node` and `platform_data`.

Test signals: Allocation/add cleanup paths, HPD notification before/after probe, attach flag validation, connector type propagation, and OF refcount checks.
