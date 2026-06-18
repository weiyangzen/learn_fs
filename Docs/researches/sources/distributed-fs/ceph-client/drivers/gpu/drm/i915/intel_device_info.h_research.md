# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_device_info.h

Purpose: defines the core static and runtime hardware capability model for i915.

Important APIs/types: declares `enum intel_platform`, subplatform bit assignments, `enum intel_ppgtt_type`, `DEV_INFO_FOR_EACH_FLAG`, `struct intel_ip_version`, `struct intel_runtime_info`, `struct intel_device_info`, and `struct intel_driver_caps`, plus initialization and print functions.

Control flow: static PCI match tables populate `struct intel_device_info`; driver creation copies `__runtime`; early and normal runtime init mutate fields that require PCI ID or MMIO knowledge. Other i915 code reads the resulting flags and version fields through macros.

State and persistence: structures persist inside `drm_i915_private` for the driver lifetime. They model platform, engines, memory regions, PAT mapping, feature flags, page sizes, ppgtt capability, IP versions, and scheduler caps.

Dependencies and integration: includes i915 UAPI memory classes, stepping, engine/context/SSEU types, and GEM object cache constants. It is foundational for feature gates across display, GT, memory, and virtualization paths.

Risks: flag additions must update the print macro list and initialization data. Subplatform bits share namespaces per parent platform, so callers must combine them with platform checks. Wrong capabilities can misprogram hardware or expose unsupported UAPI behavior.

Test signals: compile-time coverage across the driver, device-info debug output, PCI ID table tests, platform-specific CI, and feature/workaround branch coverage.
