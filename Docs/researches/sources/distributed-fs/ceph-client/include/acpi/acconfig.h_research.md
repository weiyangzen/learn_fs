<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acconfig.h -->
# sources/distributed-fs/ceph-client/include/acpi/acconfig.h

## Purpose
`acconfig.h` centralizes ACPICA global configuration constants, cache sizing defaults, specification limits, RSDP search windows, serial-operation-region buffer sizes, UUID formatting constants, and AML debugger buffer limits. It is the compile-time policy header that keeps common ACPICA constants consistent across the interpreter, namespace, table manager, resource manager, and tools.

## Important APIs, types, and functions
This header exports no functions. Important constants include `ACPI_OS_NAME`, cache depths such as `ACPI_MAX_STATE_CACHE_DEPTH`, checksum and reduced-hardware switches (`ACPI_CHECKSUM_ABORT`, `ACPI_REDUCED_HARDWARE`), interpreter limits such as `ACPI_MAX_SEMAPHORE_COUNT`, `ACPI_MAX_REFERENCE_COUNT`, `ACPI_MAX_SLEEP`, `ACPI_MAX_LOOP_TIMEOUT`, method argument/local counts, RSDP scan locations, operation-region space limits, SMBus/IPMI/GSBus/PRM/FFH buffer sizes, UUID string offsets, and debugger sizes/prompts.

## Control flow
There is no runtime flow here, but these definitions steer runtime behavior elsewhere. For example, table-discovery code scans the EBDA and high BIOS areas using the RSDP constants; the AML interpreter enforces method local/argument counts and loop timeouts; serial bus operation regions size status/length/data buffers from these macros.

## State and persistence behavior
The header does not store state. Its constants influence in-memory ACPICA caches and guardrails. Changing them can alter object lifetime, memory pressure, interpreter failure modes, and firmware compatibility, but no state persists across boots from this file alone.

## Dependencies and integration points
`acpixf.h` includes `acconfig.h` before public globals and interfaces. The constants integrate with ACPICA core implementation files, the Linux ACPICA build, ACPICA user-space tools, and platform headers that may override switches before inclusion. `ACPI_OS_NAME` is a particularly sensitive integration point because firmware often branches on `_OS`/`_OSI` compatibility strings.

## Risks and test signals
Risks include breaking AML compatibility by changing `_OS`, hiding firmware checksum defects if `ACPI_CHECKSUM_ABORT` stays false, increasing cache depths enough to affect memory usage, setting reduced-hardware mode incorrectly, and altering spec constants that external AML assumes. Test signals include ACPICA boot on legacy and reduced-hardware systems, RSDP discovery tests, malformed checksum behavior, interpreter loop-timeout tests, serial bus buffer bounds, and debugger command-buffer coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acconfig.h -->
