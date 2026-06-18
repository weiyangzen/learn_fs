<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acpi_io.h -->
# sources/distributed-fs/ceph-client/include/acpi/acpi_io.h

## Purpose
`acpi_io.h` declares Linux ACPI memory-mapping helpers used by the ACPICA OS services layer and ACPI table/register access paths. It provides a default `acpi_os_ioremap()` wrapper and APIs for mapping physical addresses and ACPI Generic Address Structures.

## Important APIs, types, and functions
The default inline `acpi_os_ioremap()` maps an ACPI physical address with `ioremap_cache()` unless an architecture supplies its own implementation. Public declarations include `acpi_permanent_mmap`, `acpi_os_map_iomem()`, `acpi_os_unmap_iomem()`, `acpi_os_get_iomem()`, `acpi_os_map_generic_address()`, and `acpi_os_unmap_generic_address()`.

## Control flow
Callers request mappings for physical ACPI memory ranges or `struct acpi_generic_address` registers. The implementation decides whether to create a transient mapping, reuse a permanent mapping, or return an existing early/late mapping. Generic-address helpers interpret GAS space IDs and map only applicable memory-backed registers.

## State and persistence behavior
The header exposes `acpi_permanent_mmap`, a runtime policy flag controlling mapping lifetime behavior. Mapping state is maintained in implementation code and the kernel ioremap subsystem; no persistent state exists.

## Dependencies and integration points
It depends on Linux `io.h`, architecture ACPI hooks from `asm/acpi.h`, ACPICA physical address types, and ACPI table/register consumers such as FADT register access, WDAT/GAS users, and `acpiosxf.h` memory I/O functions.

## Risks and test signals
Risks include cacheability mismatches, leaking permanent mappings, unmapping shared mappings incorrectly, handling zero/invalid GAS addresses, and architecture overrides diverging from generic expectations. Test signals include mapping FADT GAS registers, early table mapping and late unmapping, repeated map/unmap of the same physical range, memory versus I/O GAS handling, and architecture builds with custom `acpi_os_ioremap`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acpi_io.h -->
