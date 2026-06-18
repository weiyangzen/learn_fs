<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/lib/acpi_cppc.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/lib/acpi_cppc.c

## Purpose
libcpupower helper for reading ACPI CPPC performance data from per-CPU sysfs. It maps enum values to files under `/sys/devices/system/cpu/cpuX/acpi_cppc/` and returns parsed unsigned values.

## Important APIs, Types, And Functions
`acpi_cppc_get_data()` validates the enum index, reads the file through `cpupower_read_sysfs()`, parses with `strtoull()`, and returns zero on failure. State is read-only sysfs access. Dependencies are `cpupower_intern.h`, `acpi_cppc.h`, kernel ACPI CPPC sysfs support, and libc parsing. Risks include zero being both a valid value and an error sentinel, not clearing `errno` before `strtoull()`, and returning `unsigned long` after parsing `unsigned long long`. Test signals are reads of each CPPC file on supported hardware, missing-file returns, malformed content, and 32-bit build truncation checks.

## Control Flow
`acpi_cppc_get_data()` validates the enum index, reads the file through `cpupower_read_sysfs()`, parses with `strtoull()`, and returns zero on failure. State is read-only sysfs access. Dependencies are `cpupower_intern.h`, `acpi_cppc.h`, kernel ACPI CPPC sysfs support, and libc parsing. Risks include zero being both a valid value and an error sentinel, not clearing `errno` before `strtoull()`, and returning `unsigned long` after parsing `unsigned long long`. Test signals are reads of each CPPC file on supported hardware, missing-file returns, malformed content, and 32-bit build truncation checks.

## State And Persistence
`acpi_cppc_get_data()` validates the enum index, reads the file through `cpupower_read_sysfs()`, parses with `strtoull()`, and returns zero on failure. State is read-only sysfs access. Dependencies are `cpupower_intern.h`, `acpi_cppc.h`, kernel ACPI CPPC sysfs support, and libc parsing. Risks include zero being both a valid value and an error sentinel, not clearing `errno` before `strtoull()`, and returning `unsigned long` after parsing `unsigned long long`. Test signals are reads of each CPPC file on supported hardware, missing-file returns, malformed content, and 32-bit build truncation checks.

## Dependencies And Integration Points
`acpi_cppc_get_data()` validates the enum index, reads the file through `cpupower_read_sysfs()`, parses with `strtoull()`, and returns zero on failure. State is read-only sysfs access. Dependencies are `cpupower_intern.h`, `acpi_cppc.h`, kernel ACPI CPPC sysfs support, and libc parsing. Risks include zero being both a valid value and an error sentinel, not clearing `errno` before `strtoull()`, and returning `unsigned long` after parsing `unsigned long long`. Test signals are reads of each CPPC file on supported hardware, missing-file returns, malformed content, and 32-bit build truncation checks.

## Risks And Edge Cases
`acpi_cppc_get_data()` validates the enum index, reads the file through `cpupower_read_sysfs()`, parses with `strtoull()`, and returns zero on failure. State is read-only sysfs access. Dependencies are `cpupower_intern.h`, `acpi_cppc.h`, kernel ACPI CPPC sysfs support, and libc parsing. Risks include zero being both a valid value and an error sentinel, not clearing `errno` before `strtoull()`, and returning `unsigned long` after parsing `unsigned long long`. Test signals are reads of each CPPC file on supported hardware, missing-file returns, malformed content, and 32-bit build truncation checks.

## Test Signals
`acpi_cppc_get_data()` validates the enum index, reads the file through `cpupower_read_sysfs()`, parses with `strtoull()`, and returns zero on failure. State is read-only sysfs access. Dependencies are `cpupower_intern.h`, `acpi_cppc.h`, kernel ACPI CPPC sysfs support, and libc parsing. Risks include zero being both a valid value and an error sentinel, not clearing `errno` before `strtoull()`, and returning `unsigned long` after parsing `unsigned long long`. Test signals are reads of each CPPC file on supported hardware, missing-file returns, malformed content, and 32-bit build truncation checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/lib/acpi_cppc.c -->
