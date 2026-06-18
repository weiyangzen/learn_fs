# sources/distributed-fs/ceph-client/drivers/platform/wmi/Kconfig

Purpose: Defines the ACPI-WMI core Kconfig menu and test inclusion point. It gates the shared WMI bus/mapper used by vendor platform drivers.

Important APIs and types: `menuconfig ACPI_WMI` is a tristate depending on `ACPI && X86` and selecting `NLS`. `ACPI_WMI_LEGACY_DEVICE_NAMES` preserves old WMI device naming behavior. The file sources `drivers/platform/wmi/tests/Kconfig` under the `ACPI_WMI` menu.

Control flow: Kconfig selection controls whether `wmi.o` is built and whether WMI client drivers can depend on the core. The legacy naming option influences runtime device names through `wmi_dev_set_name()` in `core.c`.

State and persistence: No runtime state is present. The selected configuration persists in the kernel build and affects module availability, symbol exports, and WMI bus naming.

Dependencies and integration points: Integrates with platform/x86 vendor Kconfig entries that depend on `ACPI_WMI`. Selecting `NLS` supports WMI string conversion helpers.

Risks: The help text contains a typo, "Acer, Dell an HP". The legacy naming option can keep userspace compatibility but may cause duplicate-GUID registration conflicts in corner cases. Test Kconfig is only visible when the core is enabled.

Test signals: `CONFIG_ACPI_WMI=m/y` builds `drivers/platform/wmi/wmi.o`; disabling ACPI or X86 hides it; enabling legacy naming changes WMI device names; KUnit test options appear under the menu.
