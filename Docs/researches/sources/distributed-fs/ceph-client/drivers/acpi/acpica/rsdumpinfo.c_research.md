# sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsdumpinfo.c

Purpose: defines the data tables used by `rsdump.c` to print ACPICA resource descriptors. It has no conversion behavior itself; it maps resource structure offsets to labels, scalar/list opcodes, and decode tables.

Important APIs, types, and functions: exported table symbols include `acpi_rs_dump_irq`, `acpi_rs_dump_dma`, `acpi_rs_dump_*` address/memory/I/O/vendor/GPIO/pin/serial/fixed-DMA tables, common address flag tables, and `acpi_rs_dump_prt`. Macros `ACPI_RSD_OFFSET`, `ACPI_PRT_OFFSET`, and `ACPI_RSD_TABLE_SIZE` keep entries compact and countable.

Control flow: when compiled with `ACPI_DEBUG_OUTPUT`, `ACPI_DISASSEMBLER`, or `ACPI_DEBUGGER`, each table begins with a title or literal entry whose offset field stores table length. `rsdump.c` later iterates exactly that count and interprets the remaining entries. Common serial bus fields are shared through `ACPI_RS_DUMP_COMMON_SERIAL_BUS`; common address decoding is split into general, memory-specific, and I/O-specific tables.

State and persistence: static metadata only. It contains no mutable state and no runtime allocation.

Dependencies and integration points: must stay aligned with `union acpi_resource_data`, `struct acpi_pci_routing_table`, decode arrays such as `acpi_gbl_he_decode`, and dispatch arrays in `rsinfo.c`. The tables cover resources produced by `rsserial.c`, `rsirq.c`, `rsio.c`, `rsmemory.c`, and `rsaddr.c`.

Risks and test signals: stale offsets or wrong opcode types cause misleading debugger output and can hide conversion bugs. Because list opcodes rely on previous entries for lengths, entry ordering is part of the contract. Debugger/disassembler tests should dump every resource type, especially variable-length GPIO/pin/serial/vendor fields and `_PRT`, and compare output against known field values after AML round-trips.
