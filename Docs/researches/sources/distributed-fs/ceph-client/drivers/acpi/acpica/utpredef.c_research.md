## sources/distributed-fs/ceph-client/drivers/acpi/acpica/utpredef.c

Purpose: `utpredef.c` provides support routines for ACPICA predefined method/name metadata. Runtime code uses it to match names and format expected return types; compiler/help builds also expose display helpers for argument and resource metadata.

Important APIs and functions: `acpi_ut_get_next_predefined_method` advances through `acpi_gbl_predefined_methods`, skipping package-info entries that follow package-returning names. `acpi_ut_match_predefined_method` quickly rejects non-underscore names and searches predefined metadata. `acpi_ut_get_expected_return_types` formats the expected return bitmask into names such as `Integer/String/Buffer`. Tool-only functions include `acpi_ut_match_resource_name`, `acpi_ut_display_predefined_method`, static `acpi_ut_get_argument_types`, and `acpi_ut_get_resource_bit_width`.

Control flow: table matching is linear and uses ACPICA name-segment comparisons. Formatting iterates bitfields in stable table order and uses separators embedded in static string tables. Tool display logic decodes packed argument counts/types and validates maximum counts/types before printing.

State and dependencies: no mutable persistent state. The file depends on predefined metadata tables from `acpredef.h`, global tables such as `acpi_gbl_predefined_methods` and `acpi_gbl_resource_names`, and compiler/help build flags.

Integration points: namespace validation, predefined return-object repair, diagnostics, iASL, and `acpi_help` use these helpers to turn compact metadata into decisions or user-facing messages.

Risks: static string arrays must stay aligned with `ACPI_RTYPE_*`, `ACPI_TYPE_*`, and resource-width bit definitions. Metadata corruption can lead to invalid display or matching results, so tool-only validation messages are important.

Test signals: names with and without underscore, package-returning predefined entries, `ACPI_RTYPE_ALL`, empty expected bitmasks, invalid packed argument counts/types in tool builds, and resource-width bit combinations are useful.
