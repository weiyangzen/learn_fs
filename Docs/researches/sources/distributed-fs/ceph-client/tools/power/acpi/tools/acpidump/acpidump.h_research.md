<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/tools/acpidump/acpidump.h -->
# sources/distributed-fs/ceph-client/tools/power/acpi/tools/acpidump/acpidump.h

## Purpose
Shared declarations and globals for the `acpidump` utility. It defines option-controlled globals, dump action records, action constants, maximum action/table limits, FADT offset thresholds, and prototypes for dump/file helper functions.

## Important APIs, Types, And Functions
The header uses `_DECLARE_GLOBALS` to either define or extern globals such as `gbl_summary_mode`, `gbl_binary_mode`, `gbl_dump_customized_tables`, `gbl_output_file`, and `gbl_rsdp_base`. State ownership is therefore centralized in `apmain.c` and shared with all dump modules. Dependencies are ACPICA `acpi.h`, `accommon.h`, `actables.h`, and `acapps.h`. Risks include global mutable state, `AP_MAX_ACTIONS`/`AP_MAX_ACPI_FILES` hard limits, and ABI dependence on ACPICA FADT struct layout. Test signals are compile-time one-definition behavior, mixed action parsing, and table dumps involving DSDT/FACS address fields.

## Control Flow
The header uses `_DECLARE_GLOBALS` to either define or extern globals such as `gbl_summary_mode`, `gbl_binary_mode`, `gbl_dump_customized_tables`, `gbl_output_file`, and `gbl_rsdp_base`. State ownership is therefore centralized in `apmain.c` and shared with all dump modules. Dependencies are ACPICA `acpi.h`, `accommon.h`, `actables.h`, and `acapps.h`. Risks include global mutable state, `AP_MAX_ACTIONS`/`AP_MAX_ACPI_FILES` hard limits, and ABI dependence on ACPICA FADT struct layout. Test signals are compile-time one-definition behavior, mixed action parsing, and table dumps involving DSDT/FACS address fields.

## State And Persistence
The header uses `_DECLARE_GLOBALS` to either define or extern globals such as `gbl_summary_mode`, `gbl_binary_mode`, `gbl_dump_customized_tables`, `gbl_output_file`, and `gbl_rsdp_base`. State ownership is therefore centralized in `apmain.c` and shared with all dump modules. Dependencies are ACPICA `acpi.h`, `accommon.h`, `actables.h`, and `acapps.h`. Risks include global mutable state, `AP_MAX_ACTIONS`/`AP_MAX_ACPI_FILES` hard limits, and ABI dependence on ACPICA FADT struct layout. Test signals are compile-time one-definition behavior, mixed action parsing, and table dumps involving DSDT/FACS address fields.

## Dependencies And Integration Points
The header uses `_DECLARE_GLOBALS` to either define or extern globals such as `gbl_summary_mode`, `gbl_binary_mode`, `gbl_dump_customized_tables`, `gbl_output_file`, and `gbl_rsdp_base`. State ownership is therefore centralized in `apmain.c` and shared with all dump modules. Dependencies are ACPICA `acpi.h`, `accommon.h`, `actables.h`, and `acapps.h`. Risks include global mutable state, `AP_MAX_ACTIONS`/`AP_MAX_ACPI_FILES` hard limits, and ABI dependence on ACPICA FADT struct layout. Test signals are compile-time one-definition behavior, mixed action parsing, and table dumps involving DSDT/FACS address fields.

## Risks And Edge Cases
The header uses `_DECLARE_GLOBALS` to either define or extern globals such as `gbl_summary_mode`, `gbl_binary_mode`, `gbl_dump_customized_tables`, `gbl_output_file`, and `gbl_rsdp_base`. State ownership is therefore centralized in `apmain.c` and shared with all dump modules. Dependencies are ACPICA `acpi.h`, `accommon.h`, `actables.h`, and `acapps.h`. Risks include global mutable state, `AP_MAX_ACTIONS`/`AP_MAX_ACPI_FILES` hard limits, and ABI dependence on ACPICA FADT struct layout. Test signals are compile-time one-definition behavior, mixed action parsing, and table dumps involving DSDT/FACS address fields.

## Test Signals
The header uses `_DECLARE_GLOBALS` to either define or extern globals such as `gbl_summary_mode`, `gbl_binary_mode`, `gbl_dump_customized_tables`, `gbl_output_file`, and `gbl_rsdp_base`. State ownership is therefore centralized in `apmain.c` and shared with all dump modules. Dependencies are ACPICA `acpi.h`, `accommon.h`, `actables.h`, and `acapps.h`. Risks include global mutable state, `AP_MAX_ACTIONS`/`AP_MAX_ACPI_FILES` hard limits, and ABI dependence on ACPICA FADT struct layout. Test signals are compile-time one-definition behavior, mixed action parsing, and table dumps involving DSDT/FACS address fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/acpi/tools/acpidump/acpidump.h -->
