<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsarguments.c -->
# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsarguments.c

## Purpose
Validates argument declarations and caller-supplied arguments for ACPI predefined methods and ordinary control methods. It emits firmware/caller diagnostics without usually blocking execution.

## Important APIs, Types, And Functions
Provides `acpi_ns_check_argument_types`, `acpi_ns_check_acpi_compliance`, and `acpi_ns_check_argument_count`. It uses `struct acpi_evaluate_info`, `union acpi_predefined_info`, method argument-list bitfields, node flags such as `ANOBJ_EVALUATED`, and method parameter counts from attached method objects.

## Control Flow
Type checking only applies to predefined names that have not already been evaluated; it walks the expected type list and compares actual operand object types. ACPI compliance checks predefined method declarations: non-method objects are flagged when the spec requires a method, and method AML parameter counts are compared with required or minimum counts. Caller argument-count checking handles non-predefined methods by comparing caller count with AML declaration, and predefined names by comparing caller count with the ACPI spec.

## State And Persistence
No objects are modified except `ANOBJ_EVALUATED`, which suppresses repeated warning noise for a node after a mismatch. Diagnostics persist only in logs.

## Dependencies And Integration Points
Called from `acpi_ns_evaluate` before method execution or object resolution. Depends on predefined-name tables and ACPICA warning macros.

## Risks And Edge Cases
The code intentionally warns rather than fails for many mismatches, so invalid firmware may continue until AML actually references missing arguments. `ANOBJ_EVALUATED` suppresses future type warnings, trading log clarity for reduced repetition. Minimum-argument predefined methods require special handling.

## Test Signals
Evaluate predefined and non-predefined methods with too few, exact, and excess arguments; wrong argument object types; non-method predefined objects; `_SCP`-style minimum counts; and repeated evaluation to verify warning suppression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsarguments.c -->
