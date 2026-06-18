# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exstoren.c

## Purpose
`exstoren.c` supports storing into namespace objects by resolving source references and copying or converting object values into existing destination objects.

## Important APIs, Types, and Functions
Exports are `acpi_ex_resolve_object()` and `acpi_ex_store_object_to_object()`. Dependencies include `acpi_ex_resolve_to_value()`, `acpi_ex_convert_to_target_type()`, `acpi_ut_copy_iobject_to_iobject()`, `acpi_ex_truncate_for32bit_table()`, `acpi_ex_store_string_to_string()`, and `acpi_ex_store_buffer_to_buffer()`.

## Control Flow, State, and Persistence
`acpi_ex_resolve_object()` resolves local reference sources when the target is a field or simple integer/string/buffer, skips extra validation for `CopyObject`, and otherwise enforces that field/simple stores receive integer, string, buffer, or DDB handle-like table references. It also rejects unresolved aliases. `acpi_ex_store_object_to_object()` copies directly when the destination is uninitialized, performs implicit conversion to the destination type when source and destination differ, then updates the destination value in place for integers, strings, buffers, or packages. Integer stores are truncated in 32-bit table mode. Temporary converted source objects are released before return.

## Dependencies and Integration Points
This module is used by `exstore.c` for named object stores and by conversion-aware target storage. It depends on separate buffer/string copy helpers and on the global integer execution width.

## Risks and Test Signals
Risks include validating the pre-resolution source instead of the updated source pointer, conversion returning the original object as a new descriptor, package copy semantics, 32-bit truncation, and temporary object cleanup. Tests should cover uninitialized destinations, integer/string/buffer cross-conversions, field-target resolution, `CopyObject` no-conversion paths, alias rejection, DDB handles, package stores, and 32-bit table truncation.
