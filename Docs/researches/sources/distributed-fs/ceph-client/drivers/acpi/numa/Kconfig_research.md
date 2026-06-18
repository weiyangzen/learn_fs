# sources/distributed-fs/ceph-client/drivers/acpi/numa/Kconfig

This Kconfig file defines ACPI NUMA build controls. `ACPI_NUMA` defaults to enabled for `NUMA && !X86`, while `ACPI_HMAT` is a user-visible boolean for Heterogeneous Memory Attribute Table parsing and reporting.

`ACPI_HMAT` depends on `ACPI_NUMA` and selects `HMEM_REPORTING` and `MEMREGION`, matching the runtime needs of `hmat.c`. There is no runtime control flow or persistence; it controls whether the corresponding objects are compiled.

Integration is with Kbuild, generic NUMA, hmem reporting, and memory-region infrastructure. Risks are dependency skew that builds HMAT without PXM/node mapping support or omits required reporting APIs. Test signals are configuration matrix builds for NUMA on/off, x86/non-x86, and ACPI_HMAT enabled/disabled.
