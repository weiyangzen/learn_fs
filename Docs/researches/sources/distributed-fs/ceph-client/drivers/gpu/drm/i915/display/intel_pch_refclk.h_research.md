# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_pch_refclk.h

Purpose: declares PCH reference clock control APIs and provides no-op stubs for non-I915 builds.

Important APIs: LPT iCLKIP program/disable/get/compute, global PCH refclk init, and LPT CLKOUT_DP disable.

Control flow/state: no state. Stub implementations return `0` or no-op, allowing shared code to compile when i915-specific PCH refclk logic is unavailable.

Dependencies/integration: used by PCH display enable/disable and display initialization.

Risks/test signals: header-level risks are conditional compilation and call-site assumptions about nonzero clock returns. Build both I915 and stub configurations.
