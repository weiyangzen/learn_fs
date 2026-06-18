# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/pxp/intel_pxp_debugfs.h

Purpose: Declares optional debugfs registration for PXP.

Important APIs/types: `intel_pxp_debugfs_register()` with a stub when `CONFIG_DRM_I915_PXP` is disabled.

Control flow: Header-only conditional compilation.

State/persistence: None.

Dependencies/integration: Used by i915 debugfs setup code.

Risks: Disabled-config stub means callers need not add extra ifdefs, but no debugfs diagnostics exist without PXP config.

Test signals: Build coverage in PXP/non-PXP configs and presence of debugfs files.
