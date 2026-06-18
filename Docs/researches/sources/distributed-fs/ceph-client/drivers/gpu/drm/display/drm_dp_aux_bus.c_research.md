# sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_dp_aux_bus.c

Purpose: implements the DisplayPort AUX endpoint bus, primarily for eDP panels described under an `aux-bus` child node of a DP AUX provider, so panel drivers can perform transactions over the AUX channel.

Important APIs/types/functions: `struct dp_aux_ep_device_with_data` extends `dp_aux_ep_device` with a `done_probing` callback. `dp_aux_bus_type` matches endpoint drivers by OF compatible, calls endpoint probe/remove/shutdown, and attaches/detaches PM domains. `of_dp_aux_populate_bus()` finds the `aux-bus` node, gets the first available child, marks it populated, allocates the endpoint device, assigns parent/bus/type/fwnode/name, and registers it. `of_dp_aux_depopulate_bus()` walks AUX device children and unregisters populated DP AUX endpoint devices. `devm_of_dp_aux_populate_bus()` wraps populate with a devm cleanup action. `__dp_aux_dp_driver_register()` and `dp_aux_dp_driver_unregister()` register endpoint drivers on this bus.

Control flow: endpoint probe attaches the PM domain powered on, calls driver probe, then calls `done_probing(aux)` if provided. If `done_probing()` returns `-EPROBE_DEFER`, the bus converts it to `-EINVAL` because deferring the already-probed panel would be wrong. Error paths invoke endpoint remove if needed and detach the PM domain.

State and persistence: OF child nodes are marked `OF_POPULATED` while the endpoint device exists, and node references are held by the device fwnode. Device memory is freed by the device release callback. PM domains remain attached for the endpoint lifetime.

Dependencies and integration points: depends on OF device matching, Linux device/bus model, PM domains, DRM DP AUX helper definitions, and panel/endpoint drivers using `dp_aux_ep_driver`. Used by bridge drivers such as SN65DSI86 to make AUX-connected panels probe beneath the AUX adapter.

Risks: only the first available child is populated, matching the assumption that one endpoint exists. Populated flag handling must stay balanced to avoid duplicate device creation or leaked OF refs. `done_probing()` contract is subtle and forbids deferral. Parent AUX must have been initialized (`aux->ddc.algo` warning).

Test signals: no-child `-ENODEV`, duplicate population `-EINVAL`, endpoint probe deferral behavior, done-probing success/failure, devm depopulation, PM domain attach/detach, and module/bus register/unregister.
