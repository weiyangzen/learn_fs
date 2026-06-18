# sources/distributed-fs/ceph-client/drivers/acpi/apei/einj-core.c

## Purpose
Implements ACPI APEI Error Injection (EINJ) support. It discovers the EINJ table, builds an APEI instruction interpreter for EINJ actions, exposes debugfs controls under the APEI debugfs tree, and exports injection helpers used by other subsystems such as CXL.

## Important APIs, Types, And Functions
Key exported entry points are `einj_get_available_error_type()`, `einj_error_inject()`, `einj_cxl_rch_error_inject()`, `einj_is_cxl_error_type()`, and `einj_validate_error_type()`. Internal data structures model ACPI 5 address parameters (`struct set_error_type_with_address`), ACPI 6.5 EINJv2 component syndrome arrays, vendor extensions, and legacy unpublished v4 parameters. `einj_ins_type[]` maps ACPI EINJ opcodes to the common APEI executor.

## Control Flow
`einj_init()` creates a faux device whose probe reads and validates the ACPI EINJ table, queries supported error types, collects and reserves register resources, pre-maps GARs, maps the parameter block, and creates debugfs files. A debugfs write to `error_type` validates one error bit, and writing `error_inject` calls `einj_error_inject()`. Injection executes optional begin, sets the error type or address parameter block, runs firmware execute, polls busy/status with timeout, obtains the trigger table, executes trigger actions unless `notrigger` is set, and runs optional end.

## State And Persistence
Global state includes the table pointer, resource set, mapped parameter block, supported type masks, EINJv2 syndrome data, debugfs values, and vendor blobs. `einj_mutex` serializes firmware interpreter use. There is no disk persistence, but debugfs values persist in memory until module removal.

## Dependencies And Integration Points
Depends on ACPI table access, APEI executor/resource helpers, debugfs, faux devices, memory resource ownership, fixups for ACPI 5 and EINJv2, and architecture helpers such as `arch_is_platform_page()`. CXL uses exported symbols for CXL protocol and RCH injection paths.

## Risks
Primary risks are malformed firmware tables, unsafe target address masks, resource conflicts with RAM/MMIO, vendor extension size errors, firmware timeouts, and debugfs-triggered injection misuse. CXL RCH injection deliberately bypasses normal memory-MMIO rejection after separate validation.

## Test Signals
Useful signals include EINJ table validation logs, `available_error_type` output, debugfs parameter file behavior, rejected invalid type/flag combinations, timeout paths, successful trigger-table resource collection, CXL injection callers, and cleanup/unmap behavior on module remove.
