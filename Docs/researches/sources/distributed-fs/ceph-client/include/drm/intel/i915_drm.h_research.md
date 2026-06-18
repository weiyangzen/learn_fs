# sources/distributed-fs/ceph-client/include/drm/intel/i915_drm.h

Purpose: exposes legacy i915 kernel-facing declarations and PCI config register constants related to integrated graphics stolen memory, GTT aperture sizing, VGA disable, TSEG sizing, and old IPS/GPU turbo hooks.

Important APIs/types/functions: declares `i915_read_mch_val()`, `i915_gpu_raise()`, `i915_gpu_lower()`, `i915_gpu_busy()`, and `i915_gpu_turbo_disable()`. Exports `intel_graphics_stolen_res`. Defines GMCH control offsets and masks for Sandy Bridge/Broadwell style `SNB_GMCH_CTRL`, older `I830_GMCH_CTRL`, DRB/TOUD/ESMRAMC/TSEG registers, `INTEL_BSM`, Gen11 BSM dwords, and `INTEL_BSM_MASK`.

Control flow: consuming platform/quirk/GTT code reads PCI config registers, extracts bitfields, maps stolen memory and aperture ranges, and coordinates IPS/turbo policy through the declared helper functions.

State and persistence: no local state. Hardware config registers and `intel_graphics_stolen_res` represent boot-discovered memory reservations that persist for the device lifetime.

Dependencies and integration: depends on Linux fixed-width types and `struct resource` from included kernel headers. Used by i915, intel-gtt, early quirks, and platform power management paths.

Risks and test signals: bitfield errors can mis-size stolen memory or corrupt reserved ranges. Test signals include boot logs for stolen memory detection across old and new chipsets, PCI config decoding, VGA disable handling, and no overlap with system RAM resources.
