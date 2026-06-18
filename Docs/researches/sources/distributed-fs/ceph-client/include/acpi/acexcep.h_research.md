<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acexcep.h -->
# sources/distributed-fs/ceph-client/include/acpi/acexcep.h

## Purpose
`acexcep.h` defines the complete `acpi_status` exception namespace for ACPICA. It classifies return codes into environmental, programmer, table, AML execution, and internal control classes, provides success/failure and class-test macros, and optionally defines the string tables used by `acpi_format_exception()` and ACPICA help/compiler tools.

## Important APIs, types, and functions
Important macros are class tags `AE_CODE_ENVIRONMENTAL`, `AE_CODE_PROGRAMMER`, `AE_CODE_ACPI_TABLES`, `AE_CODE_AML`, `AE_CODE_CONTROL`, constructors `EXCEP_ENV`/`EXCEP_PGM`/`EXCEP_TBL`/`EXCEP_AML`/`EXCEP_CTL`, `ACPI_SUCCESS`, `ACPI_FAILURE`, `AE_OK`, and class predicates such as `ACPI_AML_EXCEPTION`. The exception catalog covers common runtime failures (`AE_NO_MEMORY`, `AE_NOT_FOUND`, `AE_TIME`), API misuse (`AE_BAD_PARAMETER`), table defects (`AE_BAD_SIGNATURE`, `AE_BAD_CHECKSUM`), AML faults (`AE_AML_OPERAND_TYPE`, `AE_AML_LOOP_TIMEOUT`), and interpreter control statuses (`AE_CTRL_BREAK`, `AE_CTRL_CONTINUE`). `struct acpi_exception_info` carries names and optional descriptions.

## Control flow
There is no direct executable flow unless `ACPI_DEFINE_EXCEPTION_TABLE` is defined in one translation unit. In that build mode, the header emits static exception-name arrays by class; `acpi_format_exception()` indexes those arrays after masking the class and code. ACPICA code uses nonzero status values as error/control returns and `AE_OK` as success.

## State and persistence behavior
The header has no mutable state. With `ACPI_DEFINE_EXCEPTION_TABLE`, it contributes read-only static tables. Status values are transient function-return contracts and are not persisted.

## Dependencies and integration points
All ACPICA public and OSL interfaces use `acpi_status`, making this header a central ABI contract. `acpixf.h` exposes `acpi_format_exception()`, diagnostic macros in `acoutput.h` consume status codes, and Linux ACPI callers translate many ACPICA errors into kernel error codes or boot logs.

## Risks and test signals
Risks include changing numeric values and breaking binary/source compatibility, misclassifying control statuses as hard failures, omitting string-table entries for new codes, or treating `AE_CTRL_*` as user-visible errors. Test signals include formatting every exception, asserting class predicates, compile coverage with and without `ACPI_DEFINE_EXCEPTION_TABLE`, AML interpreter paths for loop timeout and resource errors, and callers that distinguish `AE_NOT_FOUND` from `AE_SUPPORT`/`AE_NOT_CONFIGURED`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acexcep.h -->
