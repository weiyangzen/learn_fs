# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exfield.c

## Purpose
`exfield.c` is the high-level read/write layer for AML named fields. It chooses return object types, handles special address spaces, and delegates bit-level field extraction/insertion to `exfldio.c`.

## Important APIs, Types, And Functions
APIs are `acpi_ex_get_protocol_buffer_length`, `acpi_ex_read_data_from_field`, and `acpi_ex_write_data_to_field`. It defines serial bus protocol length mapping and PCC command-offset macros. Important field types include buffer fields, region fields, GPIO, SMBus/GSBus/IPMI/platform runtime/fixed hardware serial regions, Platform Communication Channel regions, and normal operation regions.

## Control Flow
Protocol lookup validates AccessAs protocol IDs and returns fixed, variable, or invalid lengths. Field reads first evaluate lazy buffer-field arguments, route serial bus regions to serial bus helpers, allocate either a buffer or integer depending on field bit length and CreateField semantics, route GPIO reads to GPIO helpers, read PCC fields from the internal PCC buffer, or acquire the global lock and call `acpi_ex_extract_from_field`. Field writes similarly evaluate lazy buffer fields, route GPIO and serial bus writes to helpers, handle PCC by copying to the internal PCC buffer and invoking the region handler only when the command field is written, or convert integer/buffer/string source data into a byte pointer and call `acpi_ex_insert_into_field` under the global lock.

## State And Persistence
Normal fields update backing buffers or operation regions. PCC writes update `internal_pcc_buffer` and may trigger a handler. Lazy buffer field evaluation sets object data-valid state. Global lock acquisition is transient around locked field transactions.

## Dependencies And Integration Points
This layer depends on dispatcher argument evaluation, serial bus/GPIO helpers, PCC region state, global lock helpers, and the lower-level field I/O functions in `exfldio.c`.

## Risks
Special address-space routing means incorrect space IDs can bypass normal locking or validation. PCC command detection uses offsets rather than names for robustness, so region layout must match spec. Field return type compatibility preserves CreateField-as-buffer behavior even for small fields.

## Test Signals
Tests should cover protocol ID validation, integer-versus-buffer read result selection, CreateField buffer preservation, lazy buffer-field evaluation, GPIO/serial/PCC routing, command-field PCC handler invocation, global lock use for locked fields, and source type rejection on writes.
