# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exstorob.c

## Purpose
`exstorob.c` implements low-level value copying for buffer-to-buffer and string-to-string AML stores.

## Important APIs, Types, and Functions
Exports are `acpi_ex_store_buffer_to_buffer()` and `acpi_ex_store_string_to_string()`. They manipulate `union acpi_operand_object` buffer/string fields, `AOPOBJ_STATIC_POINTER`, allocation/free helpers, and buffer flags.

## Control Flow, State, and Persistence
Buffer stores return immediately for self-assignment. If the target buffer has length zero or points at static table storage, a new buffer is allocated at the source length. If the source fits, the target is zeroed then overwritten; if not, the source is truncated to the existing target length. Source buffer flags are copied and the static-pointer flag is cleared. String stores either reuse an existing non-static buffer when the new string is shorter than the old length, or free non-static storage and allocate a new NUL-terminated buffer. The target string length is updated to the source length.

## Dependencies and Integration Points
These helpers are called by `acpi_ex_store_object_to_object()` after any required implicit conversion has produced matching source and destination types. They preserve ACPICA ownership rules for pointers into AML tables.

## Risks and Test Signals
Risks include leaks when replacing static and dynamic buffers, truncation surprises for fixed-size buffers, stale bytes after string reuse, allocation failures leaving partial target state, and buffer flag propagation. Tests should cover self-assignment, zero-length targets, static-pointer targets, source shorter/equal/longer than target, zero-length strings, allocation failures, and post-store flags/lengths.
