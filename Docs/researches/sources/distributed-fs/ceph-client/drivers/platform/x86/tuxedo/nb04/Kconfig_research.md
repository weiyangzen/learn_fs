# sources/distributed-fs/ceph-client/drivers/platform/x86/tuxedo/nb04/Kconfig

Purpose: defines the selectable NB04 WMI AB platform driver option. `TUXEDO_NB04_WMI_AB` is a tristate driver for TUXEDO notebooks with NB04 board vendor firmware, exposing keyboard backlight control through a virtual HID LampArray device.

Important APIs and control flow: no runtime code. The option depends on `ACPI_WMI` and `HID`, and its help text documents the module name `tuxedo_nb04_wmi_ab`.

State and dependencies: the Kconfig state controls whether the WMI/HID source files are built-in, modular, or omitted. Runtime dependencies are declared here so the driver has WMI registration and HID virtual device APIs available.

Risks and test signals: missing `HID` or `ACPI_WMI` dependencies would cause build failures. Configuration tests should cover `n`, `m`, and `y`, and module builds should verify the resulting module name matches the help text.
