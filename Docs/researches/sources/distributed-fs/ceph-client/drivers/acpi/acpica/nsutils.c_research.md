# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nsutils.c

## Purpose
`nsutils.c` provides common namespace utilities: path printing, type/scope property lookup, conversion between external ASL names and internal AML namestrings, ACPI handle validation, namespace teardown, and locked/unlocked node lookup.

## Important APIs, types, and functions
Important functions include `acpi_ns_print_node_pathname()`, `acpi_ns_get_type()`, `acpi_ns_local()`, `acpi_ns_get_internal_name_length()`, `acpi_ns_build_internal_name()`, `acpi_ns_internalize_name()`, `acpi_ns_externalize_name()`, `acpi_ns_validate_handle()`, `acpi_ns_terminate()`, `acpi_ns_opens_scope()`, `acpi_ns_get_node_unlocked()`, and `acpi_ns_get_node()`. Core data structures are `struct acpi_namestring_info`, `struct acpi_namespace_node`, `union acpi_generic_state`, and `struct acpi_buffer`.

## Control flow
Internalization first scans an external path for root prefixes, parent prefixes, path separators, and segment count, then allocates a zeroed internal string and writes root/parent/dual/multi-name prefixes plus padded four-byte name segments. Externalization parses internal prefixes, determines segment count, validates the encoded length, allocates the printable name, copies prefixes, repairs name segments for printable output, and inserts dots between segments. `acpi_ns_get_node_unlocked()` handles null path and root-only fast paths, internalizes the path, builds a scope wrapper, calls `acpi_ns_lookup()` in execute mode with `ACPI_NS_DONT_OPEN_SCOPE`, frees the internal path, and returns the node. `acpi_ns_get_node()` wraps the same logic in `ACPI_MTX_NAMESPACE`.

## State and persistence behavior
Most routines are conversion or query helpers. Allocated name buffers are returned to callers, who must free them. `acpi_ns_terminate()` is destructive: it deletes the namespace subtree rooted at `acpi_gbl_root_node`, locks the namespace, deletes the root node's attached object, and releases the lock.

## Dependencies and integration points
This file integrates with name parsing constants from `amlcode.h`, namespace property table `acpi_gbl_ns_properties`, global root node `acpi_gbl_root_node`, namespace lookup, mutex helpers, and pathname conversion helpers such as `acpi_ns_handle_to_pathname()`. Public namespace APIs in `nsxfname.c`, `nsxfobj.c`, and `nsxfeval.c` use these helpers to validate handles and resolve paths.

## Risks and edge cases
Name conversion must handle redundant root prefixes, parent-prefix-only strings, zero segments, dual and multi-name encodings, short segments padded with underscores, and malformed separators. `acpi_ns_validate_handle()` can only check the ACPICA descriptor type, so stale driver handles after table unload remain a broader lifecycle risk. `acpi_ns_externalize_name()` uses length checks that are necessary but must remain aligned with AML namestring encoding.

## Test signals
Strong tests include round-tripping names such as `\\_SB.PCI0`, `^^DEV0`, single segments, multi-segment names, redundant roots, bad separators, root-only lookup, null pathname lookup, locked and unlocked lookup parity, invalid handles, scope property checks for local and opens-scope types, and teardown under memory-debug instrumentation.
