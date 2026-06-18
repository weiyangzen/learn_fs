# sources/distributed-fs/ceph-client/drivers/acpi/numa/Makefile

The Makefile maps local ACPI NUMA configuration symbols to object files: `srat.o` is built for `CONFIG_ACPI_NUMA`, and `hmat.o` is built for `CONFIG_ACPI_HMAT`.

It has no runtime APIs, control flow, or persistent state. Its dependencies are the Kconfig rules that ensure `srat.c` and `hmat.c` compile only under supported feature combinations.

The main risk is build skew if Kconfig and object inclusion diverge. Test signals are object-inclusion checks and kernel builds for `CONFIG_ACPI_NUMA` and `CONFIG_ACPI_HMAT` combinations.
