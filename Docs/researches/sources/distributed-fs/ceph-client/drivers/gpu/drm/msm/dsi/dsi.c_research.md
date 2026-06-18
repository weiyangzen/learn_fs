# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/dsi.c

Purpose: This is the MSM DSI platform driver and component glue. It creates the DSI host, finds the associated DSI PHY, registers with the global DSI manager, binds into MSM KMS, and exposes modeset/snapshot helpers.

Important APIs and functions: Public helpers include `msm_dsi_is_cmd_mode()`, `msm_dsi_get_dsc_config()`, `msm_dsi_wide_bus_enabled()`, `msm_dsi_register()`, `msm_dsi_unregister()`, `msm_dsi_modeset_init()`, and `msm_dsi_snapshot()`. Probe uses `dsi_init()`, which allocates `struct msm_dsi`, initializes the host, resolves the PHY from the `phys` phandle, and registers with `dsi_manager`. Component bind gets the external bridge for standalone or bonded-master DSI and stores the DSI pointer in `priv->kms->dsi[id]`.

Control flow: Driver registration also registers DSI PHY platform drivers. Probe tolerates `-ENODEV` as an absent port but otherwise propagates defers/errors. Attach/detach are component add/del wrappers called from host attach/detach. Modeset init initializes host modeset resources and skips connector creation for bonded slave links. Unbind frees TX buffers and removes KMS references. Destroy unregisters manager/host and releases the PHY device reference.

State and dependencies: `struct msm_dsi` persists device, host, PHY, optional TE source, next bridge, PHY device reference, PHY-enabled flag, and id. It depends on OF platform, DRM bridge lookup, MSM KMS, DSI host/manager/PHY APIs, and runtime PM ops implemented in `dsi_host.c`.

Risks and test signals: Risks include PHY probe deferral, reference leaks around `of_find_device_by_node`, missing next bridge on master links, bonded slave connector suppression, and cleanup ordering when host init partially fails. Test signals include standalone and bonded DSI probe, absent-panel probe, component bind/unbind, mode init for master/slave, command-mode detection, DSC/wide-bus accessors, and snapshots.
