# sources/distributed-fs/ceph-client/drivers/acpi/acpica/psargs.c

## Purpose
`psargs.c` decodes AML opcode arguments into parse objects. It handles package lengths, AML namestrings and namespace-assisted namepaths, simple constants, strings, field lists, byte lists, targets, supernames, and variable argument lists.

## Important APIs, types, and functions
Exports and shared parser helpers include `acpi_ps_get_next_package_end()`, `acpi_ps_get_next_namestring()`, `acpi_ps_get_next_namepath()`, `acpi_ps_get_next_simple_arg()`, and `acpi_ps_get_next_arg()`. Local helpers are `acpi_ps_get_next_package_length()`, `acpi_ps_get_next_field()`, and `acpi_ps_free_field_list()`. The file uses `struct acpi_parse_state`, `struct acpi_walk_state`, `union acpi_parse_object`, namespace nodes, method operand objects, and argument type constants such as `ARGP_TERMARG`, `ARGP_FIELDLIST`, and `ARGP_SUPERNAME`.

## Control flow
Package-length decoding reads the low two count bits from byte 0, consumes up to four bytes, and reconstructs the 28-bit length. Namestring decoding skips root/parent prefixes, handles null, dual-name, multi-name, and single-segment forms, and advances the AML pointer. Namepath decoding initializes an internal namepath op, looks up the path in the namespace in execute mode with parent search, detects control-method invocations when allowed, rewinds AML for target/supername ambiguity, creates a method-call op with a child namepath op, and sets `walk_state->arg_count` from the method's parameter count. Not-found statuses are tolerated in load passes, `CondRefOf`, and package construction contexts.

Simple arguments copy fixed-width integer data, strings, or raw namestrings. Field-list parsing repeatedly decodes named fields, reserved fields, access fields, extended access fields, and connection fields until package end. `acpi_ps_get_next_arg()` dispatches by expected argument type: some types immediately allocate and fill parse ops, package length updates `pkg_end`, complex term arguments set `walk_state->arg_count`, and variable lists set `ACPI_VAR_ARGS`.

## State and persistence behavior
The file mutates parser state by advancing `parser_state->aml`, setting `pkg_end`, and appending allocated parse objects. It may set `walk_state->arg_count` and rewrite `walk_state->parser_state.aml` when a namepath is actually a method call. Allocated field-list nodes are freed on partial allocation failure.

## Dependencies and integration points
It integrates parser utilities (`acpi_ps_alloc_op`, `acpi_ps_append_arg`, `acpi_ps_init_op`), namespace lookup (`acpi_ns_lookup`, `acpi_ns_get_attached_object`), dispatcher method error conversion, AML opcode helpers, ASL compiler comment capture hooks, and field/connection AML grammar. `psloop.c` calls it to populate each operation's operands.

## Risks and edge cases
AML pointer arithmetic must stay within package boundaries. Method-call detection is grammar-sensitive because a bare name can be a namepath, target, supername, or method invocation depending on expected argument type. Not-found tolerance in package construction can hide errors until later phases. Connection-field parsing has several nested length and opcode interpretations that must agree with AML resource descriptors. Allocation failures in partially built field lists need complete cleanup.

## Test signals
Useful tests include package length encodings with 1 to 4 bytes, null/root/parent/dual/multi namestrings, method-call arity detection, forward references in load passes, `CondRefOf` missing names, missing names in packages with and without slack behavior, all simple integer sizes, strings, field/access/extended/connection entries, byte lists, targets that are method calls, and malformed field-list allocation cleanup.
