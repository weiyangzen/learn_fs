# sources/distributed-fs/ceph-client/drivers/gpu/drm/sti/sti_drv.h

Purpose: Declares shared top-level STI DRM private state and platform-driver exports.

Important types/APIs: `struct sti_private` stores the compositor pointer, an unused/legacy plane z-order property pointer, and the DRM device pointer. The header exports `sti_tvout_driver`, `sti_hqvdp_driver`, `sti_hdmi_driver`, `sti_hda_driver`, `sti_dvo_driver`, `sti_vtg_driver`, and `sti_compositor_driver` for the module driver array.

Control/state: The private object is allocated by `sti_init()` and receives the compositor pointer during compositor bind. Driver declarations let `sti_drv.c` register all display subdrivers as one module unit.

Dependencies/integration: Includes Linux platform device definitions and forward declares DRM/property/compositor types. It is included by most subdrivers that need `sti_private` or platform-driver declarations.

Risks/test signals: Adding/removing a subdriver requires keeping this export list and the registration array in sync. Build coverage and platform-driver probe logs are the main signals.
