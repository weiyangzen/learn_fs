# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_overlay.h

Purpose: declares the legacy overlay lifecycle and ioctl entry points.

Important APIs: setup/availability/cleanup/reset, `intel_overlay_switch_off()`, `intel_overlay_put_image_ioctl()`, and `intel_overlay_attrs_ioctl()`.

Control flow/state: no state in the header. It exposes `struct intel_overlay` opaquely so callers can switch off without seeing internal register/attribute fields.

Dependencies/integration: used by display init/cleanup, parent wrappers, and DRM ioctl dispatch. Includes Linux types and forward declarations for DRM device/file and Intel display structs.

Risks/test signals: header risk is ABI mismatch with ioctl dispatch or missing CONFIG coverage. Build and ioctl smoke tests cover it.
