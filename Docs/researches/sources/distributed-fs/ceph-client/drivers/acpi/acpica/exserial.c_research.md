# sources/distributed-fs/ceph-client/drivers/acpi/acpica/exserial.c

## Purpose
`exserial.c` implements field-unit read/write support for GPIO, SMBus, IPMI, GenericSerialBus, Platform Runtime Mechanism, and Fixed Function Hardware address spaces.

## Important APIs, Types, and Functions
Exports are `acpi_ex_read_gpio()`, `acpi_ex_write_gpio()`, `acpi_ex_read_serial_bus()`, and `acpi_ex_write_serial_bus()`. They operate on field descriptors, serial address-space IDs, field attributes/protocol IDs, and ACPICA buffer objects. Dependencies include `acpi_ex_access_region()`, `acpi_ex_get_protocol_buffer_length()`, `acpi_ut_create_buffer_object()`, `acpi_ex_acquire_global_lock()`, and `acpi_ex_release_global_lock()`.

## Control Flow, State, and Persistence
GPIO reads and writes bypass normal bitfield packing and pass the pin index and bit length directly to the region handler while holding the ACPI global lock when the field requests it. GPIO writes require an integer source. Serial-bus reads select a transfer buffer length and function code from the region space and accessor type, reject direct reads for bidirectional raw process bytes, allocate a return buffer, and call the region handler. Serial-bus writes require a source buffer, allocate a fixed/protocol-sized bidirectional buffer, copy as much input as fits, call the region handler, and return the same buffer to the caller.

## Dependencies and Integration Points
These helpers are called by field read/write code for special address spaces. They integrate field metadata prepared in `exprep.c`, operation-region handlers, global-lock semantics, and protocol-specific ACPICA constants for SMBus/IPMI/GSBus/PRM/FFH buffers.

## Risks and Test Signals
Risks include incorrect protocol buffer sizing, accepting invalid accessor types, global-lock leaks on error paths, source buffer truncation, GPIO integer-only enforcement, and handler expectations for bidirectional buffers. Tests should cover GPIO read/write pin metadata, SMBus/IPMI/GSBus read/write protocols, raw-process read rejection, invalid space IDs, invalid GSBus protocol IDs, short and long source buffers, PRM/FFH buffer sizes, and lock acquire/release pairing.
