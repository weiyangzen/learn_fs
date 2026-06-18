# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_crt.h

## Purpose
Declares the CRT/VGA encoder interface and provides no-op stubs when the i915-specific build path is disabled.

## APIs and integration
Under `I915`, it exposes `intel_crt_port_enabled()`, `intel_crt_init()`, and `intel_crt_reset()`. Without `I915`, inline stubs return disconnected/no-op behavior. Consumers use these helpers for CRT setup, hardware-state queries, and encoder reset callbacks.

## State, risks, and tests
The header owns no state but controls whether CRT support is compiled in. Risks are mismatched stub behavior in non-i915 builds or missing include dependencies for `i915_reg_t`. Build matrix coverage and basic CRT init/reset tests are the main signals.
