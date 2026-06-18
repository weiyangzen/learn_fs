# sources/distributed-fs/ceph-client/drivers/acpi/acpica/utexcep.c

Purpose: `utexcep.c` validates and formats `acpi_status` exception codes into stable symbolic strings.

Important APIs/types/functions: `acpi_format_exception()` is the exported formatter. `acpi_ut_validate_exception()` selects an entry from exception tables defined by `ACPI_DEFINE_EXCEPTION_TABLE` for environmental, programmer, table, AML, and control status classes.

Control flow: Formatting delegates to validation; unknown codes emit an ACPICA error and return `"UNKNOWN_STATUS_CODE"`. Validation masks the status class with `AE_CODE_MASK`, checks the sub-status against the class maximum, and returns NULL if no named entry exists.

State and persistence behavior: It uses compile-time exception tables and stores no mutable state.

Dependencies and integration points: It is used by debug, error, method evaluation, table loading, and nearly every path that logs `acpi_status`. It depends on status-code layout and generated exception-name globals.

Risks and test signals: Risks include enum/table drift, incorrect masking of new status classes, and logging recursion if unknown exceptions happen inside error paths. Tests should cover representative statuses from every class, boundary max values, invalid high-bit patterns, and exported symbol availability.
