# sources/distributed-fs/ceph-client/include/drm/bridge/dw_dp.h

Purpose: declares the platform interface for DesignWare DisplayPort bridge binding.

Important APIs, types, and flow: an anonymous enum defines single-, dual-, and quad-pixel modes. `struct dw_dp_plat_data` passes maximum link rate and pixel mode. `dw_dp_bind()` binds a DesignWare DP controller to a device and DRM encoder using the platform data, returning an opaque `dw_dp` handle.

State and persistence: DP controller state is owned by the returned `struct dw_dp` implementation object. No persistence exists.

Dependencies and integration: depends on Linux devices, DRM encoders, and platform-specific DesignWare DP driver code.

Risks and test signals: risks include unsupported pixel-mode values, link-rate negotiation mismatch, and encoder lifetime coupling. Signals include bridge bind tests, mode-setting at each pixel mode, link training at configured maximum rate, invalid platform data handling, and DRM component teardown.
