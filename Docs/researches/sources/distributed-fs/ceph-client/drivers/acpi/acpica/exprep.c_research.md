# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exprep.c

## Purpose
`exprep.c` prepares AML field descriptors for region fields, bank fields, and index fields. It decodes AML field flags, computes access granularity and offsets, attaches constructed field objects to namespace nodes, and preserves enough metadata for later field reads/writes.

## Important APIs, Types, and Functions
Exported functions are `acpi_ex_prep_common_field_object()` and `acpi_ex_prep_field_value()`. Internal helpers include `acpi_ex_decode_field_access()` and, under `ACPI_UNDER_DEVELOPMENT`, `acpi_ex_generate_access()`. Important inputs are `struct acpi_create_field_info`, `union acpi_operand_object`, `ACPI_COMMON_FIELD_INFO`, AML field flags, region/register namespace nodes, and optional connection/resource buffer metadata.

## Control Flow, State, and Persistence
Common preparation stores field flags, attributes, bit length, access byte width, base byte offset, and starting bit offset. Access types map to byte/word/dword/qword or byte-oriented `AnyAcc`, with buffer fields forced to one-byte alignment. `acpi_ex_prep_field_value()` validates region-backed fields, allocates the field object, initializes common state, then fills type-specific references: region fields point at the region object and optional serial/GPIO connection resource; bank fields keep region and bank register objects plus AML source locations; index fields keep index/data register objects and compute the index value from byte offset. The new object is attached to the field namespace node and the local reference is dropped.

## Dependencies and Integration Points
This file depends on namespace object attachment, dispatcher lazy argument evaluation for connection buffers, AML parse object metadata for bank fields, and later field access code that consumes `common_field`, `field`, `bank_field`, or `index_field` members. EC regions receive a special wider access width for multi-byte reads when possible.

## Risks and Test Signals
Risks include incorrect bit/byte offset math, access width mismatches, stale resource buffer pointers, missing reference increments for bank/index backing objects, invalid region-node acceptance, and EC access-width compatibility. Tests should create byte/word/dword/qword/buffer fields at unaligned bit offsets, region/bank/index fields, serial-bus/GPIO connection fields, EC multi-byte fields, invalid region targets, and teardown/reference-count scenarios.
