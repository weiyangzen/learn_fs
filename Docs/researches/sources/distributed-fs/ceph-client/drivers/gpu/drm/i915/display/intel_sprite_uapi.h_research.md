# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_sprite_uapi.h

Purpose: declares the legacy sprite colorkey ioctl handler. It keeps UAPI-facing implementation details out of broader display headers while forward-declaring only `drm_device` and `drm_file`.

Important API: `intel_sprite_set_colorkey_ioctl(struct drm_device *dev, void *data, struct drm_file *file_priv)` is the single exported entry point. It is intended to be registered in the i915 ioctl table and implemented by `intel_sprite_uapi.c`.

Control flow and integration: userspace reaches this function through DRM ioctl dispatch. The implementation parses `data` as `struct drm_intel_sprite_colorkey`, performs DRM plane lookup using `file_priv`, and commits an internal atomic update. The header deliberately does not expose plane-state internals.

State and persistence: no direct state. Its contract preserves the legacy ioctl ABI and ties the UAPI handler to DRM core types.

Risks and tests: prototype drift would break ioctl table registration. Build tests should include this header in ioctl code without requiring unrelated display internals. Behavioral testing belongs to `intel_sprite_uapi.c`, especially invalid input and atomic color-key placement.
