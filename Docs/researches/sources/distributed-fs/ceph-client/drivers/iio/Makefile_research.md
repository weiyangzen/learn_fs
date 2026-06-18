# sources/distributed-fs/ceph-client/drivers/iio/Makefile

Purpose: Kbuild entry point for the Industrial I/O subsystem. It builds the core `industrialio` object and descends into every IIO device-class subdirectory.

Important entries: `obj-$(CONFIG_IIO) += industrialio.o`; `industrialio-y` contains `industrialio-core.o`, `industrialio-event.o`, and `inkern.o`; conditional components include `industrialio-buffer.o`, `industrialio-trigger.o`, and `industrialio-acpi.o`. Other feature modules include configfs, GTS helper, software device/trigger, triggered events, and backend objects.

Control flow: Kconfig symbols decide which object files participate in the build. `obj-y += accel/` and the other class directories force Kbuild to visit subdirectories so their own `obj-$(CONFIG_...)` entries can be evaluated.

State and persistence: no runtime state. The file persists build composition only.

Dependencies and integration: pairs with `drivers/iio/Kconfig` and the Linux Kbuild system. It integrates the core IIO object with optional buffer, trigger, ACPI, configfs, and backend implementation files and the full set of IIO driver families.

Risks: missing conditional object entries can produce unresolved symbols for selected Kconfig features. Removing a subdirectory from `obj-y` silently prevents all drivers below it from building even when symbols are enabled.

Test signals: compile with `CONFIG_IIO=y/m`, `CONFIG_IIO_BUFFER`, `CONFIG_IIO_TRIGGER`, `CONFIG_ACPI`, and allmodconfig; check that modules and built-in objects include the expected `industrialio-*` components.
