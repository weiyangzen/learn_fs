<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/lib/acpi_cppc.h -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/lib/acpi_cppc.h

## Purpose
Public libcpupower header for ACPI CPPC values. It defines `enum acpi_cppc_value` entries such as highest/lowest/nominal performance, lowest/nominal frequency, reference performance, wraparound time, and declares `acpi_cppc_get_data()`.

## Important APIs, Types, And Functions
There is no runtime control flow; callers pass an enum and CPU number to retrieve sysfs data. Dependencies are the implementation in `acpi_cppc.c` and C consumers including this header. Risks include enum/file-order ABI coupling and the closing comment naming `_ACPI_CPPC_H` while the guard is `__ACPI_CPPC_H__`. Test signals are compile of C/C++ consumers and successful retrieval of each enum on CPPC systems.

## Control Flow
There is no runtime control flow; callers pass an enum and CPU number to retrieve sysfs data. Dependencies are the implementation in `acpi_cppc.c` and C consumers including this header. Risks include enum/file-order ABI coupling and the closing comment naming `_ACPI_CPPC_H` while the guard is `__ACPI_CPPC_H__`. Test signals are compile of C/C++ consumers and successful retrieval of each enum on CPPC systems.

## State And Persistence
There is no runtime control flow; callers pass an enum and CPU number to retrieve sysfs data. Dependencies are the implementation in `acpi_cppc.c` and C consumers including this header. Risks include enum/file-order ABI coupling and the closing comment naming `_ACPI_CPPC_H` while the guard is `__ACPI_CPPC_H__`. Test signals are compile of C/C++ consumers and successful retrieval of each enum on CPPC systems.

## Dependencies And Integration Points
There is no runtime control flow; callers pass an enum and CPU number to retrieve sysfs data. Dependencies are the implementation in `acpi_cppc.c` and C consumers including this header. Risks include enum/file-order ABI coupling and the closing comment naming `_ACPI_CPPC_H` while the guard is `__ACPI_CPPC_H__`. Test signals are compile of C/C++ consumers and successful retrieval of each enum on CPPC systems.

## Risks And Edge Cases
There is no runtime control flow; callers pass an enum and CPU number to retrieve sysfs data. Dependencies are the implementation in `acpi_cppc.c` and C consumers including this header. Risks include enum/file-order ABI coupling and the closing comment naming `_ACPI_CPPC_H` while the guard is `__ACPI_CPPC_H__`. Test signals are compile of C/C++ consumers and successful retrieval of each enum on CPPC systems.

## Test Signals
There is no runtime control flow; callers pass an enum and CPU number to retrieve sysfs data. Dependencies are the implementation in `acpi_cppc.c` and C consumers including this header. Risks include enum/file-order ABI coupling and the closing comment naming `_ACPI_CPPC_H` while the guard is `__ACPI_CPPC_H__`. Test signals are compile of C/C++ consumers and successful retrieval of each enum on CPPC systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/lib/acpi_cppc.h -->
