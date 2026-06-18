<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/os_specific/service_layers/osunixmap.c -->
# sources/distributed-fs/ceph-client/tools/power/acpi/os_specific/service_layers/osunixmap.c

## Purpose
Implements native Unix physical memory mapping for ACPICA tools. `acpi_os_map_memory()` opens `/dev/mem`, aligns the requested physical address to a page boundary, mmaps the covering range read-only, and returns an adjusted pointer; `acpi_os_unmap_memory()` reverses the offset adjustment.

## Important APIs, Types, And Functions
State is only the transient mapping; the `/dev/mem` fd is closed immediately after `mmap()`. Dependencies are `/dev/mem`, page size discovery, `mmap/munmap`, and ACPICA pointer/integer macros. Risks include privilege and kernel lockdown failures, page-size arithmetic overflow, callers needing to pass the same length used for mapping, and returning an interior pointer that must not be directly munmapped except through this helper. Test signals are successful acpidump table mapping as root, graceful failure without `/dev/mem`, unaligned physical addresses, and ASAN/valgrind checks around unmap lengths.

## Control Flow
State is only the transient mapping; the `/dev/mem` fd is closed immediately after `mmap()`. Dependencies are `/dev/mem`, page size discovery, `mmap/munmap`, and ACPICA pointer/integer macros. Risks include privilege and kernel lockdown failures, page-size arithmetic overflow, callers needing to pass the same length used for mapping, and returning an interior pointer that must not be directly munmapped except through this helper. Test signals are successful acpidump table mapping as root, graceful failure without `/dev/mem`, unaligned physical addresses, and ASAN/valgrind checks around unmap lengths.

## State And Persistence
State is only the transient mapping; the `/dev/mem` fd is closed immediately after `mmap()`. Dependencies are `/dev/mem`, page size discovery, `mmap/munmap`, and ACPICA pointer/integer macros. Risks include privilege and kernel lockdown failures, page-size arithmetic overflow, callers needing to pass the same length used for mapping, and returning an interior pointer that must not be directly munmapped except through this helper. Test signals are successful acpidump table mapping as root, graceful failure without `/dev/mem`, unaligned physical addresses, and ASAN/valgrind checks around unmap lengths.

## Dependencies And Integration Points
State is only the transient mapping; the `/dev/mem` fd is closed immediately after `mmap()`. Dependencies are `/dev/mem`, page size discovery, `mmap/munmap`, and ACPICA pointer/integer macros. Risks include privilege and kernel lockdown failures, page-size arithmetic overflow, callers needing to pass the same length used for mapping, and returning an interior pointer that must not be directly munmapped except through this helper. Test signals are successful acpidump table mapping as root, graceful failure without `/dev/mem`, unaligned physical addresses, and ASAN/valgrind checks around unmap lengths.

## Risks And Edge Cases
State is only the transient mapping; the `/dev/mem` fd is closed immediately after `mmap()`. Dependencies are `/dev/mem`, page size discovery, `mmap/munmap`, and ACPICA pointer/integer macros. Risks include privilege and kernel lockdown failures, page-size arithmetic overflow, callers needing to pass the same length used for mapping, and returning an interior pointer that must not be directly munmapped except through this helper. Test signals are successful acpidump table mapping as root, graceful failure without `/dev/mem`, unaligned physical addresses, and ASAN/valgrind checks around unmap lengths.

## Test Signals
State is only the transient mapping; the `/dev/mem` fd is closed immediately after `mmap()`. Dependencies are `/dev/mem`, page size discovery, `mmap/munmap`, and ACPICA pointer/integer macros. Risks include privilege and kernel lockdown failures, page-size arithmetic overflow, callers needing to pass the same length used for mapping, and returning an interior pointer that must not be directly munmapped except through this helper. Test signals are successful acpidump table mapping as root, graceful failure without `/dev/mem`, unaligned physical addresses, and ASAN/valgrind checks around unmap lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/os_specific/service_layers/osunixmap.c -->
