# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/Makefile

Purpose: defines the i915 build graph, compiler flags, conditional object lists, display/GT/GEM/PXP/GVT/selftest components, and header/kernel-doc test hooks.

Important APIs/types: object aggregations include `i915-y`, `gt-y`, `gem-y`, conditional `i915-$(CONFIG_...)`, `obj-$(CONFIG_DRM_I915)`, and `obj-$(CONFIG_DRM_I915_GVT_KVMGT)`. Flags add format-truncation warnings, optional Werror, `-DI915`, optional `-DNOTRACE`, and include path.

Control flow: kbuild expands sorted object lists into the i915 module. Conditional sections add compat ioctls, debugfs, PMU, fbdev, ACPI, DP tunnel, GVT, PXP commands/debug, selftests, and header tests.

State and persistence: build-time only.

Dependencies and integration points: integrates nearly all i915 subsystems: core driver, GT, GEM/TTM, display, encoders, DP/HDMI/DSI/LVDS/DVO, GuC/HuC/GSC, PXP, error capture, selftests, GVT, and generated render state.

Risks: file list ordering and conditional objects are critical for link correctness. The DVO source files in this subset are always part of modesetting output/encoder code. Header tests intentionally exclude broken headers. PREEMPT_RT disables tracing wholesale through `NOTRACE`.

Test signals: full i915 build across config matrices, Werror/kernel-doc builds, module symbol/link checks, selftest builds, and display-only source reuse with `-DI915`.
