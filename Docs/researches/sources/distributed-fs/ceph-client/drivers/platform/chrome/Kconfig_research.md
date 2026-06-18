# sources/distributed-fs/ceph-client/drivers/platform/chrome/Kconfig

Purpose: Kconfig menu for ChromeOS/Chromebook platform support and Chrome EC child/transport drivers.

Important APIs, types, and functions: parent `CHROME_PLATFORMS` gates the submenu for X86, ARM, ARM64, or compile-test builds. Major symbols include `CHROMEOS_ACPI`, `CHROMEOS_LAPTOP`, `CHROMEOS_PSTORE`, `CHROMEOS_TBMC`, `CHROMEOS_OF_HW_PROBER`, `CROS_EC`, bus transports (`I2C`, `RPMSG`, `ISHTP`, `SPI`, `UART`, `LPC`), EC child interfaces (`CHARDEV`, `LIGHTBAR`, `VBC`, `DEBUGFS`, `SENSORHUB`, `SYSFS`, `TYPEC`, `USBPD_NOTIFY`, etc.), privacy screen, Type-C switch, Wilco EC, and KUnit protocol tests.

Control flow: `CROS_EC` selects `CROS_EC_PROTO`; transport symbols depend on the core plus their bus subsystems. MFD child drivers generally depend on `MFD_CROS_EC_DEV` and often default to that symbol. Privacy screen selects DRM privacy-screen support. The KUnit test symbol selects protocol helpers.

State and persistence: build-configuration only; selected symbols determine object graph and module availability.

Dependencies and integration points: tied to `drivers/platform/chrome/Makefile`, MFD Chrome EC devices, ACPI/OF firmware descriptions, USB Type-C, IIO sensorhub, debugfs, sysfs, and Wilco EC subdirectory.

Risks and edge cases: the LPC help text says the module is `cros_ec_lpcs`, matching the composite object, but user expectations may look for `cros_ec_lpc`. Defaults tied to `MFD_CROS_EC_DEV` pull in user interfaces automatically when the MFD core is enabled. Dependency mistakes can cause either missing child drivers or excessive build surface on non-ChromeOS machines.

Test signals: all enabled Chrome symbols should compile in representative x86/ARM/ARM64 and `COMPILE_TEST` configs. KUnit protocol tests exercise `CROS_EC_PROTO`, while transport and ACPI/OF drivers require integration hardware or emulation.
