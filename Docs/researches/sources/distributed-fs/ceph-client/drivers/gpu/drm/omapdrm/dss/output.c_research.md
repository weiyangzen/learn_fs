# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/output.c

Purpose: Provides common OMAP DSS output setup and manager wrapper functions used by DSS output drivers to connect local bridges/panels to DRM and to call back into OMAP DRM CRTC manager operations.

Important APIs/functions: `omapdss_device_init_output()` finds the remote OF graph sink, resolves a DRM bridge or panel, wraps panels with `drm_panel_bridge_add()`, chains an optional local bridge ahead of the next bridge, and defers probe when no sink bridge is ready. `omapdss_device_cleanup_output()` removes any panel bridge. `dss_mgr_set_timings()`, `dss_mgr_set_lcd_config()`, `dss_mgr_enable()`, `dss_mgr_disable()`, `dss_mgr_start_update()`, and framedone register/unregister wrappers dispatch through `dss->mgr_ops_priv` into `omap_crtc_dss_*()`.

Control flow: Output probe initializes an `omap_dss_device` and calls `omapdss_device_init_output()` before registering it. DRM modeset later attaches bridges, creates connectors, and uses the manager wrappers during bridge enable/disable or mode setting.

State and persistence: Updates fields in caller-owned `struct omap_dss_device`: `bridge`, `next_bridge`, and `panel`. No persistent storage exists.

Dependencies/integration: Depends on OF graph, DRM bridge/panel helpers, `dss.h`, `omapdss.h`, and the OMAP DRM CRTC manager API.

Risks and test signals: Missing remote nodes are tolerated as no sink, while missing resolved bridges with local bridges defer probe. Cleanup only removes panel bridges when both bridge and panel are present. Test panel and bridge sinks, chained local bridge outputs like HDMI/SDI/VENC, deferred probe ordering, and manager callback availability before bridge enable.
