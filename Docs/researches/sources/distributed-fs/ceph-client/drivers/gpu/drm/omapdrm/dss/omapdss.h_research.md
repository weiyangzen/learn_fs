# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/omapdss.h

Purpose: Public internal DSS interface header shared between OMAP DRM and DSS output drivers. It defines display types, channels, plane/output IDs, overlay/manager/writeback data contracts, DSS device descriptors, IRQ bits, and manager/output API prototypes.

Important APIs/types: `enum omap_display_type`, `omap_plane_id`, `omap_channel`, `omap_dss_output_id`, and related enums describe hardware display routing and features. `struct omap_overlay_info`, `omap_overlay_manager_info`, and `omap_dss_writeback_info` carry plane, manager, and writeback programming data. `struct omap_dss_device` is the central output/sink object with device, bridge, panel, list node, type/name, DSI ops, bus flags, DISPC channel, output ID, and OF port. Prototypes cover device registration/connect/disconnect, output initialization/cleanup, DISPC ISR registration, CRTC manager operations, manager timing/config/enable/update/framedone APIs, component readiness, DSS init/exit, and DISPC lookup.

Control flow: Output drivers create and register `omap_dss_device` objects. The DRM driver connects them into pipelines and manager helpers call back into `omap_crtc_dss_*()` to program DISPC/CRTC state. DSI manual update and framedone paths use the function pointer contracts here.

State and persistence: The header defines in-memory device and programming state only. Lifetime is controlled by platform probes, component bind/unbind, and DRM modeset objects.

Dependencies/integration: Includes DRM color/mode types, Linux device/list/IRQ types, OMAP platform data, and videomode. It is the integration point between DSS hardware drivers and DRM KMS.

Risks and test signals: Because many modules share these structs, enum/channel/output ID mismatches can break pipeline routing. Fixed array users assume channel and output IDs fit local limits. Validate multi-output probe, bridge/panel graph handling, DSI manual update, writeback users, and IRQ mapping for each SoC.
