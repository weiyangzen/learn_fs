# sources/distributed-fs/ceph-client/include/drm/bridge/dw_mipi_dsi.h

Purpose: glue-driver interface for the Synopsys DesignWare MIPI DSI host/bridge core, abstracting DPHY timing, lane-rate calculation, escape clock discovery, host attach hooks, and DRM bridge format negotiation.

Important APIs/types/functions: `struct dw_mipi_dsi_dphy_timing`, `struct dw_mipi_dsi_phy_ops`, `struct dw_mipi_dsi_host_ops`, `struct dw_mipi_dsi_plat_data`, `dw_mipi_dsi_probe`, `dw_mipi_dsi_remove`, `dw_mipi_dsi_bind`, `dw_mipi_dsi_unbind`, `dw_mipi_dsi_set_slave`, and `dw_mipi_dsi_get_bridge`.

Control flow: platform code supplies MMIO base, lane limit, validation/fixup callbacks, input bus format callback, PHY ops, host ops, and private data; the common driver probes, binds to a DRM encoder, services MIPI DSI attach/detach, and sequences PHY power/timing during enable/disable.

State and persistence: no header state; opaque `struct dw_mipi_dsi` owns runtime controller, bridge, host, and dual-DSI state. Hardware register and PHY state are runtime only.

Dependencies and integration points: Linux I/O memory, DRM bridge/atomic/connector/modes, MIPI DSI devices, platform devices, display panels, and SoC PHY glue.

Risks and test signals: lane Mbps/timing errors, bus-format mismatches, attach cleanup failures, and dual-DSI ordering are key risks. Test panel attach/detach, bridge atomic format negotiation, mode fixup, lane limits, escape clock failures, and master/slave enable.
