# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pch_display.h

Purpose: declares PCH transcoder/display sequencing APIs and provides inert stubs when `I915` is not defined.

Important APIs: PCH transcoder availability/mapping; ILK pre-enable/enable/disable/post-disable/get-config; LPT enable/disable/get-config; PCH transcoder M/N getters; `intel_pch_sanitize()`.

Control flow/state: no state. The stubs make non-i915 builds compile while returning false/zero or no-op.

Dependencies/integration: consumed by encoder/CRTC enable and readout paths for PCH-backed outputs.

Risks/test signals: prototype or stub return type mismatch can break alternate builds. Hardware sequencing coverage belongs to the `.c` implementation.
