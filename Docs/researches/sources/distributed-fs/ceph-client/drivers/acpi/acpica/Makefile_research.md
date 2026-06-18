# sources/distributed-fs/ceph-client/drivers/acpi/acpica/Makefile

Purpose: defines how Linux Kbuild compiles ACPICA core interpreter sources into the ACPI composite object `acpi.o`.

Important build contracts: `ccflags-y` defines `_LINUX` and `BUILDING_ACPICA`; `CONFIG_ACPI_DEBUG` adds `ACPI_DEBUG_OUTPUT`; `CFLAGS_tbfind.o` suppresses one truncation warning; `obj-y += acpi.o` keeps these objects in the ACPI module-parameter namespace; `acpi-y` lists dispatcher, event, executor, hardware, namespace, parser, resource, table, utility, debugger, and future-use objects.

Control flow: Kbuild expands unconditional object lists and conditional blocks. Core `ds*`, `ev*`, `ex*`, `hw*`, `ns*`, `ps*`, `rs*`, `tb*`, and `ut*` files are always linked. `hwpci.o` depends on `CONFIG_PCI`, debugger objects depend on `CONFIG_ACPI_DEBUGGER`, and some upstream utility/debug objects depend on `ACPI_FUTURE_USAGE`.

State and persistence: no runtime state; the persistent effect is build composition. Object inclusion decides which declarations from ACPICA headers are actually implemented in a given kernel build.

Dependencies and integration: integrates upstream ACPICA source layout into Linux's ACPI core build. It gates debugger, PCI config, and future utility support by config symbols.

Risks: missing objects produce link failures or disabled runtime paths. New references to future-use/debug-only functions must match config gates. Warning suppression should remain local.

Test signals: ACPI builds with and without `CONFIG_PCI`, `CONFIG_ACPI_DEBUG`, and `CONFIG_ACPI_DEBUGGER`; `W=1` builds; link checks after ACPICA updates; boot smoke tests for table load, namespace init, GPE handling, and AML execution.
