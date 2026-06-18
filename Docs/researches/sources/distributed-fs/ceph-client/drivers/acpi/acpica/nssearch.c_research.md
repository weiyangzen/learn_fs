# sources/distributed-fs/ceph-client/drivers/acpi/acpica/nssearch.c

## Purpose
`nssearch.c` performs low-level ACPI namespace name lookup and optional insertion for a single name segment. It is the search primitive used by namespace loading, namespace reference resolution, and execution-time lookup.

## Important APIs, types, and functions
`acpi_ns_search_one_scope()` scans the child list of a namespace node for a 4-byte target name. `acpi_ns_search_parent_tree()` implements ACPI upward search rules for non-local object types. `acpi_ns_search_and_enter()` combines validation, one-scope search, parent search, override handling, error-if-found behavior, temporary/external flags, node creation, and installation.

## Control flow
Single-scope search walks `parent_node->child` through peer links and compares `node->name.integer` with `target_name`. When it finds a local method alias, it resolves the alias to the actual method node before returning it. Parent-tree search exits early at root or for object types marked local by `acpi_ns_local()`, otherwise it repeatedly searches enclosing parents with `ACPI_TYPE_ANY`.

`acpi_ns_search_and_enter()` repairs non-printable name bytes, searches the current scope, and if found applies special flags. `ACPI_NS_OVERRIDE_IF_FOUND` deletes children and either clears the attached object for runtime override or removes the node. `ACPI_NS_ERROR_IF_FOUND` converts a found node to `AE_ALREADY_EXISTS`. If not found and not in load pass 1, the parent tree is searched when `ACPI_NS_SEARCH_PARENT` is set. Execute mode never creates nodes. Load modes allocate a new namespace node, mark ASL compiler external or temporary flags as needed, then install it under the parent.

## State and persistence behavior
The file mutates the in-memory namespace tree only through `acpi_ns_search_and_enter()` in load modes or override mode. New nodes are attached to parent child/peer lists and inherit owner information via `acpi_ns_install_node()`. Override mode can delete subtree children, clear attached objects, change owner IDs, or remove the node entirely.

## Dependencies and integration points
Search depends on namespace node layout, `acpi_ns_create_node()`, `acpi_ns_install_node()`, `acpi_ns_remove_node()`, `acpi_ns_delete_children()`, `acpi_ut_repair_name()`, and global runtime namespace override policy. It is invoked by `acpi_ns_lookup()` and parser callbacks in `psobject.c`/dispatcher code when AML names are loaded or resolved.

## Risks and edge cases
Lookups are linear within a scope; this is intentional but can still affect pathological firmware tables with huge sibling lists. Parent search must not run during load pass 1 or it can resolve forward references incorrectly. Override behavior has high blast radius because it deletes children and attached objects. Method aliases require safe casting from `node->object` back to a namespace node.

## Test signals
Tests should cover local-only types, parent upsearch, execute-mode misses that do not create nodes, load-pass insertion, duplicate detection, runtime override with and without `acpi_gbl_runtime_namespace_override`, method aliases, invalid name repair warnings, and temporary/external flag propagation.
