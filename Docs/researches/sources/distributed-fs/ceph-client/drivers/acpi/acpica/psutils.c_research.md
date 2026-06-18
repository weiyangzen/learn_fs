# sources/distributed-fs/ceph-client/drivers/acpi/acpica/psutils.c

## Purpose
`psutils.c` contains parser-only utility functions for parse-op allocation, initialization, freeing, and simple parse-op name helpers.

## Important APIs, types, and functions
Functions include `acpi_ps_create_scope_op()`, `acpi_ps_init_op()`, `acpi_ps_alloc_op()`, `acpi_ps_free_op()`, `acpi_ps_is_leading_char()`, `acpi_ps_get_name()`, and `acpi_ps_set_name()`. The file uses parser object caches `acpi_gbl_ps_node_cache` and `acpi_gbl_ps_node_ext_cache`, opcode metadata, parse-op flags, and ASL comment capture globals.

## Control flow
`acpi_ps_create_scope_op()` allocates a `AML_SCOPE_OP` and names it as the root. `acpi_ps_init_op()` sets descriptor type and AML opcode, and in disassembler builds copies the opcode name into the op. `acpi_ps_alloc_op()` chooses a generic parse op by default, an extended op for deferred or named opcodes, or a bytelist op for `AML_INT_BYTELIST_OP`; it acquires from the corresponding object cache, initializes the op, records the AML pointer and parse-op flags, updates current scope for scope ops, and transfers captured comments when enabled. `acpi_ps_free_op()` clears comment metadata and releases to the same cache family based on flags.

## State and persistence behavior
The file manages transient parse-op cache objects and writes global parser/comment state such as `acpi_gbl_current_scope` in scope-op allocation. It does not create namespace objects or operand objects, but bad allocation/free behavior affects every parse.

## Dependencies and integration points
It depends on opcode metadata from `psopinfo.c`, ACPICA object cache functions, parse object layout, AML constants, and ASL compiler/disassembler comment macros. All parser construction and deletion paths call these helpers either directly or through `psargs.c`, `psobject.c`, and `pswalk.c`.

## Risks and edge cases
The cache selected for allocation must match the flag used for free. Flags are derived from opcode metadata, so metadata bugs can cause size mismatches. Generic ops cannot hold named fields; `acpi_ps_get_name()` and `acpi_ps_set_name()` intentionally no-op for generic ops. Comment capture paths are build-configuration dependent and can leak metadata if not cleared.

## Test signals
Signals include allocation/free for generic, named, deferred, and bytelist ops, cache leak checking, scope-op root name initialization, disassembler opcode-name population, leading-character classification, get/set name behavior for generic versus extended ops, and comment capture/clear behavior in ASL compiler builds.
