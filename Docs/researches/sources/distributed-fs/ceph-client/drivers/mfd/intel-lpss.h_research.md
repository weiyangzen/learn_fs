# sources/distributed-fs/ceph-client/drivers/mfd/intel-lpss.h

Purpose: private interface shared by the Intel LPSS ACPI, PCI, and core source files. It defines platform data, quirk bits, and exported core entry points.

Important APIs/types/functions: `struct intel_lpss_platform_info`, `QUIRK_IGNORE_RESOURCE_CONFLICTS`, `QUIRK_CLOCK_DIVIDER_UNITY`, `intel_lpss_probe()`, `intel_lpss_remove()`, and `intel_lpss_pm_ops`.

Control flow: no executable flow. Bus-specific wrappers populate `intel_lpss_platform_info` with resources, IRQ, quirks, clock data, and software-node properties before calling the core.

State and persistence: the structure points to per-device MEM/IRQ resources and immutable board/platform properties. Runtime state is created by the implementation in `intel-lpss.c`.

Dependencies and integration: depends on `linux/pm.h`, `linux/bits.h`, and forward declarations for `struct device`, `struct resource`, and `struct software_node`. Namespaced exports are imported by ACPI/PCI modules.

Risks: this header is the contract between wrappers and core. Adding fields requires all platform-info initializers to be reviewed. Quirk semantics must stay narrow because they alter resource conflict and clock-divider behavior globally for a matched device.

Test signals: build coverage with both `CONFIG_MFD_INTEL_LPSS_ACPI` and `CONFIG_MFD_INTEL_LPSS_PCI`, module namespace import checks, and runtime validation that all platform-info fields are filled before core probe.
