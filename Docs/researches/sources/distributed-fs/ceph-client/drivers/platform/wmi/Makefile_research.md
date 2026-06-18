# sources/distributed-fs/ceph-client/drivers/platform/wmi/Makefile

Purpose: Builds the ACPI-WMI core module and descends into the WMI KUnit test directory.

Important APIs and types: `wmi-y := core.o marshalling.o string.o` composes the module from the bus core, ACPI-object marshalling, and WMI string helpers. `obj-$(CONFIG_ACPI_WMI) += wmi.o` gates the module. `obj-y += tests/` lets test Makefiles decide what to build.

Control flow: Kbuild links the listed objects into `wmi.o` when ACPI-WMI is enabled, then evaluates the tests subdirectory independently.

State and persistence: No runtime state. The file defines build composition and object ordering.

Dependencies and integration points: Tied to `drivers/platform/wmi/Kconfig`, `tests/Makefile`, and public symbols used by WMI client drivers.

Risks: Omitting `marshalling.o` or `string.o` would break newer WMI buffer/string APIs. The tests subdirectory comment says `drivers/platform/x86/wmi/tests`, which is stale relative to this path.

Test signals: `make drivers/platform/wmi/` builds `core.o`, `marshalling.o`, `string.o`, and optional KUnit modules; `modinfo wmi` shows the core module metadata from `core.c`.
