# sources/distributed-fs/ceph-client/drivers/platform/x86/x86-android-tablets/Kconfig

Purpose: configuration for the x86 Android tablet DSDT-fixup driver. It targets tablets whose factory Android kernels hardcoded devices, GPIOs, and addresses that firmware failed to describe reliably.

Important APIs and control flow: `X86_ANDROID_TABLETS` is tristate and depends on I2C, SPI, serial device bus, GPIO, PMIC opregion, ACPI, EFI, and PCI. It selects LED and power-supply support used by instantiated board devices.

State and dependencies: the Kconfig symbol controls both the main fixup driver and the Vexia EC battery driver in the Makefile.

Risks and test signals: this driver is broad and DMI-gated at runtime, so generic distro configs are expected to build it as a module. Configuration tests should verify all selected subsystems are available and the module builds in x86 allmodconfig-like environments.
