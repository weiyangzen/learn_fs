# sources/distributed-fs/ceph-client/drivers/platform/x86/uniwill/Makefile

Purpose: Kbuild recipe for the Uniwill laptop platform driver. It creates the composite object `uniwill-laptop.o` from `uniwill-acpi.o` and `uniwill-wmi.o`.

Important APIs and control flow: `obj-$(CONFIG_UNIWILL_LAPTOP)` gates the composite object. The object list ensures the ACPI EC platform driver and the WMI event bridge are linked into one module or built-in unit.

State and dependencies: no runtime state. It depends on Kbuild composite-object semantics and the matching Kconfig symbol.

Risks and test signals: object order matters because the ACPI file calls `uniwill_wmi_register_driver()` from module init. Build tests should verify no unresolved notifier/WMI symbols and that the module name is `uniwill-laptop`.
