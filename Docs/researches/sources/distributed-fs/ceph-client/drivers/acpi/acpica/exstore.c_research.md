# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exstore.c

## Purpose
`exstore.c` is the main AML store engine. It stores values into namespace nodes, reference targets, indexed buffers/packages, locals/args, Debug, and fields.

## Important APIs, Types, and Functions
Exports are `acpi_ex_store()` and `acpi_ex_store_object_to_node()`. Local helpers are `acpi_ex_store_object_to_index()` and `acpi_ex_store_direct_to_node()`. Important types include local reference descriptors, namespace nodes, `ACPI_TYPE_LOCAL_REGION_FIELD`, `ACPI_TYPE_LOCAL_BANK_FIELD`, `ACPI_TYPE_LOCAL_INDEX_FIELD`, and `ACPI_TYPE_BUFFER_FIELD`.

## Control Flow, State, and Persistence
`acpi_ex_store()` validates source and destination, routes namespace-node destinations to `acpi_ex_store_object_to_node()`, treats AML constants as no-op store destinations, and dispatches reference classes: `RefOf` stores to the referenced node, `Index` stores to a buffer/string byte or package element, locals/args update method data, and Debug prints the object. Package index stores copy normal objects or retain DDB handles, adjust references according to the parent package reference count, and replace the element. Buffer/string index stores the low byte of an integer or first byte of a buffer/string. Named-object stores reject immutable target types for normal `Store`, resolve references, convert for integer/string/buffer targets when allowed, preserve field object type by writing field data, and use direct copy/attach for `CopyObject` or other allowed targets.

## Dependencies and Integration Points
This file integrates with namespace attachment, method local/arg storage, field write code, object copying, implicit conversion in `exstoren.c`, object printing for Debug, and opcode-specific semantics for `Store` versus `CopyObject`.

## Risks and Test Signals
Risks include reference-count imbalance in package replacement, incorrect package parent reference-count adjustment, accidental type changes for field nodes, wrong implicit conversion on `ArgX` stores, store-to-constant behavior, and buffer/string index source validation. Tests should cover stores to names, locals, args, constants, Debug, fields, package indexes with existing/null elements, DDB handles, buffer/string indexes, immutable targets, `CopyObject` type changes, and conversion failures.
