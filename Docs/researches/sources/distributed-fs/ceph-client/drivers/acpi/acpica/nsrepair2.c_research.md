# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsrepair2.c

## Purpose
`nsrepair2.c` implements complex repair logic for selected ACPI predefined method return values after normal predefined-object validation has found a mismatch or suspicious shape. It is a compatibility layer for common firmware defects: malformed `_HID`/`_CID` strings, undersized `_FDE`/`_GTM` buffers, reversed `_PRT` fields, invalid `_CST` entries, and unsorted power/thermal/light-response packages.

## Important APIs, types, and functions
The public entry is `acpi_ns_complex_repairs()`, which receives `struct acpi_evaluate_info`, the target namespace node, the prior validation status, and an in/out operand-object pointer. `struct acpi_repair_info` maps four-character ACPI names to `acpi_repair_function` handlers. Repair handlers cover `_ALR`, `_CID`, `_CST`, `_FDE`/`_GTM`, `_HID`, `_PRT`, `_PSS`, and `_TSS`. Shared helpers include `acpi_ns_match_complex_repair()`, `acpi_ns_check_sorted_list()`, `acpi_ns_sort_list()`, and `acpi_ns_remove_element()`.

## Control flow
`acpi_ns_complex_repairs()` first matches `node->name.ascii` against `acpi_ns_repairable_names`; non-matches return the original validation status. Matched names dispatch to a repair function. String repairs create replacement string objects, remove invalid leading `*`, uppercase characters, replace the object pointer, and drop the old reference. `_CID` applies the `_HID` string repair to either the returned string or every package element while preserving package element reference counts. `_FDE` and `_GTM` accept a valid 5-DWORD buffer or expand the known 5-byte firmware bug into a 20-byte DWORD buffer. Package sorting repairs validate outer package and subpackage shape, compare integer sort keys, and bubble-sort only when a disorder is detected. `_CST` also removes zero-count or type-zero C-state entries and rewrites the top-level count. `_TSS` suppresses sorting when a sibling `_PSS` exists because firmware may leave `_TSS` power fields meaningless in that case.

## State and persistence behavior
The file mutates transient ACPICA operand objects returned by method evaluation, not persistent firmware tables. State changes are reference-counted: replacement objects take over `*return_object_ptr`, original objects are released, removed package entries are dereferenced, and `info->return_flags` is marked with `ACPI_OBJECT_REPAIRED` when a visible repair occurs. The repaired object then flows to predefined validation and caller-facing object conversion.

## Dependencies and integration points
This code depends on namespace identity (`struct acpi_namespace_node`), operand object constructors in `acpi_ut_create_*`, reference management in `acpi_ut_remove_reference`, namespace lookup through `acpi_ns_get_node()`, and predefined warning/debug macros. It is called from ACPICA namespace evaluation validation, so its behavior directly affects public `acpi_evaluate_object*()` results and Linux driver enumeration.

## Risks and edge cases
The repairs intentionally accept firmware that violates the ACPI spec, so overly broad repair can mask real BIOS defects. Package repair assumes earlier validation has removed null elements before sorting. `_CST` indexes subpackage element 1 after only checking package count is nonzero, relying on prior type/length validation. `_PRT` has a warning call with a duplicated format string in the arguments, making that path worth compiler-format scrutiny. Reference-count mistakes here would leak or prematurely free returned operand objects.

## Test signals
Useful signals include ACPICA tests or firmware tables that return lower-case or starred IDs, 5-byte `_FDE`/`_GTM` buffers, reversed `_PRT` source fields, unsorted `_PSS`/`_TSS`/`_ALR`/`_CST` packages, zero-type C-state entries, and valid cases that should remain untouched. Memory-debug builds should show no leaks or double releases when repairs replace or remove objects.
