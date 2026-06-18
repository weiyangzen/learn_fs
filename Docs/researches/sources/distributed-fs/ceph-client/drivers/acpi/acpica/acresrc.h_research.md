# sources/distributed-fs/ceph-client/drivers/acpi/acpica/acresrc.h

## Purpose
Declares ACPICA Resource Manager internals. It defines conversion-table row formats, dump-table row formats, conversion opcodes, dispatch tables, and prototypes that convert between raw AML resource templates and `struct acpi_resource` lists.

## Important APIs, Types, And Functions
`struct acpi_rsconvert_info` is the byte-sized conversion instruction used by resource conversion tables; `enum ACPI_RSCONVERT_OPCODES` includes initialization, flag extraction, bitmask encode/decode, count calculation, source-string handling, fixed-width moves, GPIO/serial variable field moves, and exit predicates. `struct acpi_rsdump_info` plus `enum ACPI_RSDUMP_OPCODES` describe debugger/disassembler resource dumps. Public internal prototypes cover list creation (`acpi_rs_create_resource_list`, `acpi_rs_create_aml_resources`, `acpi_rs_create_pci_routing_table`), method wrappers (`acpi_rs_get_crs_method_data`, `acpi_rs_set_srs_method_data`, `_PRT`, `_PRS`, `_AEI`), length calculation, AML/resource conversion, address common-field helpers, data movement, bitmask helpers, resource-source handling, and descriptor header writes.

## Control Flow, State, And Persistence
The Resource Manager is table-driven. Dispatch arrays map internal resource type or AML descriptor type to a `struct acpi_rsconvert_info` program, and conversion routines execute that program to copy, synthesize, count, or validate fields. Dump dispatch arrays perform the same indirection for debug output. No persistent data is owned here except global static table declarations defined in resource modules.

## Dependencies And Integration Points
Includes `amlresrc.h` for packed AML descriptor overlays and relies on ACPICA namespace, operand object, buffer, resource, and status types. It is used by ACPI external resource APIs, namespace method evaluation for `_CRS`/`_PRS`/`_SRS`/`_AEI`/`_PRT`, debugger resource commands, and disassembler/compiler resource template support. Packing pragmas are important because conversion tables store byte offsets into packed raw descriptors.

## Risks And Test Signals
Offset and packing errors are the primary risk, especially on architectures that cannot tolerate misaligned access. GPIO, pin, serial-bus, and vendor-data descriptors carry variable sections whose lengths and offsets must be consistent. Test signals include AML-to-resource-to-AML round trips, debugger `Resources`/`Template` output, `acpi_walk_resources`, `_SRS` application tests, compiler/disassembler resource template tests, and boots on devices with modern GPIO/I2C/SPI/UART/CSI2 descriptors.
