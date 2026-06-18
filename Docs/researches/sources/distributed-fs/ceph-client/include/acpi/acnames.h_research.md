<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acnames.h -->
# sources/distributed-fs/ceph-client/include/acpi/acnames.h

## Purpose
`acnames.h` collects canonical ACPI namespace method names and root path strings used across ACPICA and Linux ACPI code. It avoids duplicated string literals for common predefined methods and root namespace identifiers.

## Important APIs, types, and functions
The header exports string macros for common namespace methods such as `METHOD_NAME__ADR`, `_HID`, `_CID`, `_CRS`, `_DSD`, `_PLD`, `_PRW`, `_STA`, `_UID`, and power methods `_PS0` through `_PS3`. Root-only pathname macros include `METHOD_PATHNAME__PTS`, `METHOD_PATHNAME__SST`, and `METHOD_PATHNAME__WAK`. It also defines encoded name constants `ACPI_UNKNOWN_NAME`, `ACPI_PREFIX_MIXED`, `ACPI_PREFIX_LOWER`, `ACPI_ROOT_NAME`, and string forms such as `ACPI_ROOT_PATHNAME`, `ACPI_NAMESPACE_ROOT`, and `ACPI_NS_ROOT_PATH`.

## Control flow
There is no direct control flow. Namespace lookup, object evaluation, table loading, suspend/resume, and device enumeration code pass these names to ACPICA functions like `acpi_get_handle()` and `acpi_evaluate_object()`.

## State and persistence behavior
No state is stored. These are compile-time constants representing AML namespace names that firmware persists in DSDT/SSDT tables.

## Dependencies and integration points
`acpi.h` includes this early so later type and interface headers can refer to canonical names. Linux ACPI bus helpers and drivers use the strings to evaluate device identity, resource, power, and wake methods. The integer constants depend on ACPICA name-segment conventions and host byte ordering assumptions already handled by ACPICA.

## Risks and test signals
Risks are typographical or encoding errors that silently break namespace lookup, inconsistent root path handling, and overuse of names in contexts where methods are optional. Test signals include namespace traversal on devices with `_HID`, `_CID`, `_UID`, `_CRS`, `_DSD`, `_PLD`, suspend/resume calls to `\_PTS` and `\_WAK`, and root-name formatting tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/acpi/acnames.h -->
