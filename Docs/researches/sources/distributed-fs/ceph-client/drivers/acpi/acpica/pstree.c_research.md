# sources/distributed-fs/ceph-client/drivers/acpi/acpica/pstree.c

## Purpose
`pstree.c` provides parse-tree argument access, append, and depth-first traversal helpers for ACPICA parser op trees.

## Important APIs, types, and functions
`acpi_ps_get_arg()` returns the nth linked argument op. `acpi_ps_append_arg()` appends one or more linked argument ops to an op and sets parent pointers. `acpi_ps_get_depth_next()` returns the next parse op in depth-first order from an origin. An obsolete `acpi_ps_get_child()` helper remains under `ACPI_OBSOLETE_FUNCTIONS`.

## Control flow
Argument lookup first gets opcode metadata and returns null for unknown opcodes or opcodes without `AML_HAS_ARGS`. It then walks `common.value.arg` and `common.next` until the requested index. Append validates that the parent opcode can have arguments, appends at the tail or initializes the list, then walks every linked argument being appended to set `common.parent` and increment the parent's argument-list length. Depth-first traversal first tries the current op's first argument, then its next sibling, then climbs parent links looking for a parent's sibling; it stops when it reaches the origin boundary.

## State and persistence behavior
`acpi_ps_append_arg()` mutates parse tree topology, parent pointers, sibling links, and the parent argument-list length. The lookup and traversal helpers are read-only except for ASL comment/filename labeling macros in compiler builds.

## Dependencies and integration points
These helpers depend on opcode metadata from `acpi_ps_get_opcode_info()`, parse object layout, AML flags, and ASL compiler comment macros. Parser construction in `psargs.c` and `psobject.c`, parse-tree deletion in `pswalk.c`, and disassembler/debug walkers rely on this file.

## Risks and edge cases
Appending a linked chain increments the parent length for every node in the chain, so callers must not pass an unintended sibling list. Unknown opcodes are ignored rather than asserted. Depth traversal must respect the origin boundary or it can walk outside a requested subtree. Parent pointers must be set before deletion and traversal paths depend on them.

## Test signals
Tests should cover appending first and subsequent args, appending chained args, retrieving existing and missing arg indexes, opcodes without arguments, unknown opcode behavior, depth-first traversal through child and sibling paths, stopping at origin, and tree integrity after parser construction and deletion.
