# sources/distributed-fs/ceph-client/include/drm/display/drm_dp_aux_bus.h

Purpose: Linux bus abstraction for devices reachable over a DisplayPort AUX channel, commonly eDP panels exposed as device tree children.

Important APIs/types/functions: `struct dp_aux_ep_device`, `struct dp_aux_ep_driver`, `to_dp_aux_ep_dev`, `to_dp_aux_ep_drv`, `of_dp_aux_populate_bus`, `of_dp_aux_depopulate_bus`, `devm_of_dp_aux_populate_bus`, deprecated endpoint wrappers, `dp_aux_dp_driver_register`, `__dp_aux_dp_driver_register`, and `dp_aux_dp_driver_unregister`.

Control flow: an AUX provider populates endpoint devices, optionally runs a `done_probing` callback, and endpoint drivers receive probe/remove/shutdown callbacks. Deprecated wrappers translate no-child `-ENODEV` into success.

State and persistence: endpoint runtime state is an embedded `struct device` plus AUX pointer; lifetime follows the device model or devm cleanup.

Dependencies and integration points: Linux device model, OF matching, modules, `struct drm_dp_aux`, eDP panels, AUX controllers, and managed cleanup.

Risks and test signals: endpoint lifetime after AUX unregister, legacy no-child behavior, owner refs, and shutdown ordering are risks. Test OF population, no-child case, devm cleanup, endpoint probe/remove/shutdown, and AUX unregister with endpoints.
