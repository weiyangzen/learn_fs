<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel_ips.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel_ips.h

Purpose: tiny public companion header for the IPS/i915 integration point.

Important API: declares `void ips_link_to_i915_driver(void);`, exported by `intel_ips.c` and intended for i915 to notify the IPS driver that i915 has loaded and its turbo symbols may now be available.

Control flow: no code. Inclusion lets a GPU driver or related code call the notifier without depending on IPS internals.

State/persistence: no state in the header. The called implementation sets a static `late_i915_load` flag in `intel_ips.c`.

Dependencies/integration: part of the platform/x86 IPS and DRM i915 cooperation path. The symbol is exported GPL-only in the implementation.

Risks: because the API has no instance parameter, the IPS implementation cannot directly address multiple IPS devices and instead uses a global late-load flag.

Test signals: code including this header should compile against the IPS implementation; calling the function should allow `ips_gpu_turbo_enabled()` to retry `symbol_get()` for i915 hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel_ips.h -->
