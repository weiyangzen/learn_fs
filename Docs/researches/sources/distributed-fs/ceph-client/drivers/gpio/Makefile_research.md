# sources/distributed-fs/ceph-client/drivers/gpio/Makefile

## Purpose
This Makefile is the kernel build manifest for the GPIO subsystem under `drivers/gpio`. It selects core gpiolib objects, optional userspace and firmware integration layers, and a long alphabetized list of concrete GPIO controller and expander drivers.

## Important APIs, types, and functions
The file is Kbuild data rather than C code. Important build variables are `ccflags-$(CONFIG_DEBUG_GPIO) += -DDEBUG`, `obj-$(CONFIG_GPIOLIB)`, `obj-$(CONFIG_GPIO_CDEV)`, `obj-$(CONFIG_GPIO_REGMAP)`, `obj-$(CONFIG_GPIO_GENERIC)`, and per-driver `obj-$(CONFIG_GPIO_*) += gpio-*.o` entries. `gpiolib-acpi-y` composes the ACPI support object from core and quirks files, while `gpio-generic-$(CONFIG_GPIO_GENERIC) += gpio-mmio.o` folds `gpio-mmio.o` into the generic GPIO object.

## Control flow
Kbuild evaluates the `CONFIG_*` symbols chosen by Kconfig and appends matching objects into the directory build. Core gpiolib objects are listed first, followed by helper frameworks and individual device drivers sorted mostly alphabetically. There is no runtime control flow in this file.

## State and persistence behavior
The Makefile persists no runtime state. Its state effect is build-time: changing an `obj-*` line changes which modules or built-in objects exist in the produced kernel tree. `CONFIG_DEBUG_GPIO` also changes compilation by defining `DEBUG`.

## Dependencies and integration points
The file integrates all drivers in this directory with the kernel Kbuild system and with Kconfig symbols defined elsewhere. It also encodes helper relationships, notably `gpio-generic` including `gpio-mmio.o` and `gpiolib-acpi` including both ACPI core and quirk objects.

## Risks and edge cases
The main risks are omitted object mappings for new Kconfig symbols, typoed object names, and ordering/duplication mistakes that make a driver unavailable despite a visible Kconfig option. Since many entries build platform-specific code, accidental broad enablement can expose compile errors on unrelated architectures.

## Test signals
Useful signals are successful `make drivers/gpio/` or allmodconfig builds, module presence for enabled `CONFIG_GPIO_*` symbols, and no unresolved symbols from split helper objects such as `gpio-mmio.o`, `gpiolib-acpi-core.o`, or imported helper namespaces.
