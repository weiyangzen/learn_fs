# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exresolv.c

## Purpose
`exresolv.c` resolves operand-stack entries and nested reference objects into concrete AML values or base object/type information.

## Important APIs, Types, and Functions
Exports are `acpi_ex_resolve_to_value()` and `acpi_ex_resolve_multiple()`. The local resolver is `acpi_ex_resolve_object_to_value()`. Important data includes operand descriptors, namespace nodes, local reference classes (`LOCAL`, `ARG`, `INDEX`, `REFOF`, `NAME`, `DEBUG`, `TABLE`), and walk-state opcode context.

## Control Flow, State, and Persistence
`acpi_ex_resolve_to_value()` validates the stack entry, resolves operand descriptors first, then namespace nodes. The object resolver turns local/arg references into method data values, dereferences package indexes except for method calls and `CopyObject`, leaves buffer-field indexes as references, resolves name references to attached objects or device/thermal nodes, evaluates buffers/packages lazily, and reads fields into value objects. It removes references to replaced stack objects. `acpi_ex_resolve_multiple()` traverses reference chains for `ObjectType` and `SizeOf`, follows namespace nodes and package index references, detects circular references, maps internal field types to external `FieldUnit`, maps scope to `Any`, and can optionally return the final descriptor.

## Dependencies and Integration Points
This file is central to operand resolution before opcode execution and to type introspection opcodes. It integrates method local/arg storage, namespace lookup, lazy buffer/package evaluation, field reads, and ACPI reference classes produced by `RefOf`, `Index`, `Load`, and namepath parsing.

## Risks and Test Signals
Risks include dereferencing when an opcode requires a reference, uninitialized package element errors, circular reference handling, stale pointer/reference ownership after stack replacement, and incorrect external type mapping. Tests should cover every reference class, package index behavior for method call versus normal use, buffer-field index preservation, name references to device/thermal and ordinary objects, nested `RefOf` chains, circular references, lazy buffer/package evaluation, and field reads.
