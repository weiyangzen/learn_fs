# sources/distributed-fs/ceph-client/drivers/acpi/acpica/amlresrc.h

## Purpose
Defines raw AML resource descriptor tags and packed wire-format structures used to overlay ACPI resource template byte streams. It also declares mapfile/compiler helper interfaces for GPIO, serial-bus, HID, and connection metadata.

## Important APIs, Types, And Structures
`ACPI_RESTAG_*` constants map ASL descriptor field names such as `_ADR`, `_LEN`, `_INT`, `_SHR`, `_VEN`, `_FQN`, and `_FQD`. Default small-descriptor sizes support ASL resource generation. `struct asl_resource_node` and `struct asl_resource_info` support compiler resource-template construction. Packed structs model small descriptors (`irq`, `dma`, `io`, `fixed_io`, `fixed_dma`, `end_tag`) and large descriptors (`memory24/32`, fixed memory, address16/32/64, extended address64, extended IRQ, generic register, GPIO, CSI2/I2C/SPI/UART serial bus, pin function/config/group/group function/group config, and clock input). `union aml_resource` overlays all descriptor variants and scalar utility views.

## Control Flow, State, And Persistence
The header has no executable control flow, but conversion and validation code casts raw AML bytes to these packed structs and uses embedded lengths/offsets to locate variable trailing data such as pin lists, resource-source strings, labels, and vendor bytes. Compiler/disassembler map helpers persist relationship metadata outside these raw descriptors as needed.

## Dependencies And Integration Points
Used by `acresrc.h` conversion tables, resource manager code, AML resource walkers, iASL resource generation, disassembler mapfile support, and debugger resource dumps. `#pragma pack(1)` is essential because these structs are ABI overlays on AML bytes, not native in-memory layouts.

## Risks And Test Signals
Risks include descriptor layout drift from the ACPI spec, incorrect variable-section offsets, missing revision/minimum-data-length updates, and unaligned-access problems if code performs unsafe native loads on strict architectures. Test signals include resource-template compile/disassemble round trips, AML-to-resource conversion for each descriptor kind, GPIO/pin/serial bus device enumeration, `_CRS`/`_PRS`/`_AEI` debugger dumps, and firmware samples using ACPI 6.2+ pin and ACPI 6.5 clock descriptors.
