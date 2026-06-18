# sources/distributed-fs/ceph-client/include/drm/clients/drm_client_setup.h

Purpose: helper declarations for setting up standard DRM clients, optionally with a preferred format, fourcc, or color mode, with no-op stubs when disabled.

Important APIs/types/functions: `drm_client_setup`, `drm_client_setup_with_fourcc`, `drm_client_setup_with_color_mode`, and disabled-build inline stubs; forward declarations for `struct drm_device` and `struct drm_format_info`.

Control flow: display drivers call a setup helper after device/mode configuration is ready. Enabled builds create/configure clients; disabled builds compile calls into no-ops.

State and persistence: no header state. Client state belongs to DRM client infrastructure and the DRM device runtime.

Dependencies and integration points: Kconfig, Linux types, DRM devices, format metadata, and drivers wanting generic fbdev/client setup.

Risks and test signals: disabled-build assumptions, invalid fourcc/color modes, and too-early setup are risks. Test enabled/disabled builds, default setup, preferred fourcc/color mode, and unregister cleanup.
