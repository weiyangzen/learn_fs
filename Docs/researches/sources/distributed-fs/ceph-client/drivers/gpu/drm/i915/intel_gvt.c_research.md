# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_gvt.c

Purpose: provides i915 host-side integration with Intel GVT-g graphics virtualization when `CONFIG_DRM_I915_GVT` is enabled.

Important APIs/functions: exports `intel_gvt_init`, `intel_gvt_driver_remove`, `intel_gvt_resume`, `intel_gvt_set_ops`, and `intel_gvt_clear_ops`, plus many i915 symbols under namespace `I915_GVT` for the external GVT module. Internal helpers test supported platforms, snapshot initial PCI/MMIO state, and initialize/clean devices.

Control flow: i915 devices register on a global list. When GVT ops are registered, existing devices are initialized if module parameters, guest status, platform support, and GuC submission restrictions allow it. Initial state capture saves PCI config space and MMIO ranges from `intel_gvt_iterate_mmio_table()`. Clear/remove paths call backend cleanup and free snapshots under a global mutex.

State and persistence: global state includes `intel_gvt_devices`, `intel_gvt_ops`, and `intel_gvt_mutex`. Per-device state lives in `dev_priv->vgpu.initial_cfg_space`, `initial_mmio`, list entry, and `dev_priv->gvt`. State is volatile and rebuilt on driver/module load.

Dependencies and integration: depends on GEM, context, ring, runtime PM, uncore forcewake, GVT MMIO table iteration, vGPU detection, kernel module symbol namespaces, and hypervisor-facing GVT backend ops.

Risks: GVT must not initialize on guests, unsupported devices, or GuC submission. Snapshot allocation failures disable GVT without failing i915. Exported symbols expand coupling to GEM internals, so API changes can break the GVT module.

Test signals: GVT module load/unload, device probe/remove, suspend/resume with `pm_resume`, supported BDW/SKL/KBL/BXT/CFL/CML hosts, and failure logs for unsupported or GuC-enabled configurations.
