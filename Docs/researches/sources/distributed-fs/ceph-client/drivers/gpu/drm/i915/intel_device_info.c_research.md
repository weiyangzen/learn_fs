# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/intel_device_info.c

Purpose: initializes, refines, and prints static and runtime Intel GPU device information.

Important APIs/functions: exports `intel_platform_name`, `intel_device_info_print`, `intel_device_info_runtime_init_early`, `intel_device_info_runtime_init`, `intel_device_info_driver_create`, and `intel_driver_caps_print`. Internal helpers map PCI IDs to subplatform bits, read GMD IP version registers before normal MMIO setup, and validate reported IP versions.

Control flow: driver creation stores matched static info and copies initial runtime info. Early runtime init reads GMD graphics/media IP versions through PCI BAR mapping when available and marks platform/subplatform masks from PCI IDs. Later runtime init adjusts fields requiring MMIO/PCH state, currently disabling ppGTT on gen6 with VT-d.

State and persistence: updates `i915->__info` and `RUNTIME_INFO(i915)` in memory, including device ID, platform mask, IP versions, ppgtt type/size, page sizes, and stepping. The data persists for the driver lifetime.

Dependencies and integration: depends on PCI IDs, GMD registers, i915 platform macros, VT-d detection, DRM printers, and runtime info consumed throughout the driver.

Risks: incorrect subplatform classification changes feature/workaround selection globally. GMD direct BAR reads happen before regular MMIO and must use always-on registers. Static platform name array size is enforced but missing names return `<unknown>`.

Test signals: boot logs, debugfs/info dumps, force-probe/device matching tests, GMD platforms, VT-d gen6 systems, and compile-time `BUILD_BUG_ON` checks.
