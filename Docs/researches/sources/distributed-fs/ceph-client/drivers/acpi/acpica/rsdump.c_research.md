# sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsdump.c

Purpose: provides debugger-only formatting and dumping of ACPICA resource lists and PCI IRQ routing tables. It turns `struct acpi_rsdump_info` tables from `rsdumpinfo.c` into human-readable diagnostic output.

Important APIs, types, and functions: under `ACPI_DEBUGGER`, `acpi_rs_dump_resource_list()` dumps each resource until `END_TAG`, and `acpi_rs_dump_irq_list()` dumps `_PRT` entries until a zero-length terminator. The core local interpreter is `acpi_rs_dump_descriptor()`, with helpers for optional resource sources/labels, address common flags, scalar formatting, and byte/word/dword lists.

Control flow: dump entrypoints first check debug level enablement. Resource-list dumping validates type and nonzero length, dispatches serial bus subtypes through `acpi_gbl_dump_serial_bus_dispatch`, all other resources through `acpi_gbl_dump_resource_dispatch`, then advances with `ACPI_NEXT_RESOURCE()`. The descriptor dumper uses the first table entry as a count and switches on opcodes such as title, literal, string, integer, bit flags, short/long lists, address common fields, source, label, and source-label. List opcodes depend on the previous table target as the length source.

State and persistence: no durable state; emits through `acpi_os_printf()` and reads debug configuration. It never changes resource objects.

Dependencies and integration points: compiled for debugger/disassembler/debug-output configurations and depends on dump tables from `rsdumpinfo.c`, decode string arrays, and public resource structures. It is a diagnostic companion to conversion logic, useful when inspecting `_CRS`, `_PRS`, `_AEI`, and `_PRT` results.

Risks and test signals: diagnostic paths still need guardrails against malformed in-memory resources because zero lengths or invalid types could otherwise loop or index dispatch tables incorrectly. Table opcode/count mismatches in `rsdumpinfo.c` can print wrong fields or dereference invalid offsets. Test signals include debugger builds that dump representative resources for every dispatch entry, serial bus subtypes, empty strings, optional source absence, and invalid/zero-length resource handling.
