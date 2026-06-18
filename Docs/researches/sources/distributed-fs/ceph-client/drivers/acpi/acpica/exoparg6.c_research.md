# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exoparg6.c

## Purpose
`exoparg6.c` implements AML six-argument operators: package `Match` and `LoadTable`.

## Important APIs, Types, and Functions
The main entry point is `acpi_ex_opcode_6A_0T_1R()`. The local helper `acpi_ex_do_match()` evaluates `MTR`, `MEQ`, `MLE`, `MLT`, `MGE`, and `MGT` terms. Dependencies include `acpi_ex_do_logical_op()` for type-aware comparisons, `acpi_ut_create_integer_object()`, and `acpi_ex_load_table_op()`.

## Control Flow, State, and Persistence
`Match` validates both match operator IDs, validates `start_index` against the package count, creates an integer result initialized to all ones, then scans package elements from the start index. NULL package elements are non-matches. Both match terms must pass before the result is changed to the matching index. `LoadTable` delegates table loading and returns the descriptor produced by the loader.

## Dependencies and Integration Points
`Match` relies on the common logical comparison engine so package elements can be implicitly converted to the match object type. `LoadTable` integrates with ACPICA table loading and returns a DDB handle-style object through the normal result path.

## Risks and Test Signals
Risks include reversed comparison semantics in `acpi_ex_do_match()`, invalid operator acceptance, package boundary errors, NULL package element handling, and table loader reference ownership. Tests should include every match operator, mixed integer/string/buffer package elements, no-match all-ones return, start index at and beyond package length, NULL elements, and `LoadTable` success/failure with DDB handle lifetime checks.
