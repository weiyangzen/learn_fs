# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/Kconfig

Purpose: declares i915 DRM driver configuration and related optional features for Intel integrated graphics.

Important APIs/types: `DRM_I915` is a tristate depending on DRM, X86, PCI, and not PREEMPT_RT, selecting many display, memory, ACPI, sync, TTM, and helper dependencies. Additional symbols include force-probe string, error capture/compression, userptr, GVT KVMGT, PXP, DP tunnel support, and hidden `DRM_I915_GVT`.

Control flow: selected symbols control build inclusion in `drivers/gpu/drm/i915/Makefile`, optional debug/profile submenus, and feature-specific source lists.

State and persistence: build-time configuration and default module parameter values only.

Dependencies and integration points: integrates i915 with DRM helpers, display helpers, KMS, ACPI video, Intel GTT, audio, CEC, TTM, auxiliary bus, selftests, virtualization, protected content, and DP tunnel support.

Risks: large dependency surface; force-probe can enable unsupported hardware and taint the kernel. `!PREEMPT_RT` excludes realtime kernels because tracepoints are disabled globally through Makefile flags. Optional features require matching firmware/subsystems.

Test signals: allmodconfig, i915 module build, selected feature builds, force_probe parameter behavior, and boot/probe on supported and blocked PCI IDs.
