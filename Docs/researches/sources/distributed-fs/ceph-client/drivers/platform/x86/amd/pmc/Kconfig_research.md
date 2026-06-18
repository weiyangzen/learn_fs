# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/pmc/Kconfig

Purpose: this Kconfig file defines AMD Power Management Controller support and the optional MP2 Smart Trace Buffer helper.

Important APIs, types, and functions: `AMD_PMC` is a tristate depending on ACPI, PCI, RTC_CLASS, AMD_NODE, SUSPEND, and selecting SERIO. `AMD_MP2_STB` is a bool depending on `AMD_PMC`, defaulting to it.

Control flow: enabling `AMD_PMC` builds the PMC module; enabling `AMD_MP2_STB` includes MP2 STB support in the composite object.

State and persistence: configuration persists in `.config`.

Dependencies and integration points: dependencies mirror runtime integration with ACPI LPS0, root PCI/SMN access, RTC wake-alarm workarounds, AMD node access, suspend callbacks, and serio wakeup manipulation.

Risks: defaulting MP2 STB on broadens debugfs and PCI probing behavior. Missing dependencies would fail compile or produce runtime stubs for suspend/RTC paths.

Test signals: config visibility on AMD x86 builds, successful module build as `amd-pmc`, and inclusion/exclusion of `mp2_stb.o` as expected.
