# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/Makefile

Purpose: Defines the xe Kbuild graph: flags, generated workaround files, core/optional object lists, shared i915 display compilation, debug/test objects, header tests, and final module linkage.

Important APIs/types: `xe-y`, conditional `xe-$(CONFIG_...)`, generated `xe_wa_oob` and `xe_device_wa_oob` rules, `subdir-ccflags-*`, i915 display object rule, `hdrtest`, and `obj-$(CONFIG_DRM_XE) += xe.o`.

Control flow: Kbuild builds the workaround generator, emits generated workaround C/H files, compiles sorted object lists, conditionally adds I2C/SVM/hwmon/PMU/configfs/SR-IOV/display/debugfs/fbdev/tunnel/test objects, and links `xe.o`.

State/persistence: Generated sources live under `$(obj)/generated`. Header tests become always-built only under `CONFIG_DRM_XE_WERROR`.

Dependencies/integration: Kbuild, i915 display sources, xe Kconfig symbols, KUnit, debugfs, PCI IOV, VFIO, and generated workaround rules.

Risks/test signals: Generated-header dependencies, object-list ordering, shared i915 API drift, header self-containment/kernel-doc failures, clean/incremental builds, display enabled/disabled builds, and WERROR hdrtests.
