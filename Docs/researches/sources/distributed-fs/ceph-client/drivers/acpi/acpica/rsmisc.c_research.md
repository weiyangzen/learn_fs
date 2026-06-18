# sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsmisc.c

Purpose: implements the generic interpreter for `struct acpi_rsconvert_info` conversion tables. It is the core engine that transforms individual AML resource descriptors into internal resources and internal resources back into AML.

Important APIs, types, and functions: `acpi_rs_convert_aml_to_resource()` interprets get-side opcodes. `acpi_rs_convert_resource_to_aml()` interprets set-side opcodes. Supported operations include initialization, flag extraction/insertion, count/length adjustments, fixed-width moves, GPIO/pin/serial variable-data moves, resource source handling, address-common conversion, bitmask encoding/decoding, and conditional exits.

Control flow: get-side conversion starts by reading AML descriptor length, then iterates the table count from the first entry. `INITGET` zeros and initializes the internal resource; count opcodes expand `resource->length`; move opcodes copy scalar or variable data; `SOURCE`/`SOURCEX` delegate optional source parsing; bitmask opcodes decode lists; conditional exits stop early for compact descriptors. Unless in flag-subtable mode, final internal length is rounded to native word alignment. Set-side conversion starts with `INITSET`, zeroes AML, sets the descriptor header, adjusts AML length as count operations add variable data, writes offsets before moving GPIO/serial data, delegates source/address handling, and honors `EXIT_LE`, `EXIT_NE`, and `EXIT_EQ` optimizations.

State and persistence: no persistent state. It writes into caller-provided resource and AML buffers and depends on precomputed sizes being large enough.

Dependencies and integration points: consumes all conversion tables defined in `rsaddr.c`, `rsio.c`, `rsirq.c`, `rsmemory.c`, and `rsserial.c`; calls helpers from `rsutils.c`; and is invoked by `rslist.c`.

Risks and test signals: this file is highly pointer- and offset-sensitive. The interpreter trusts table opcode sequencing, counts, offsets, and prior sizing; a mismatch can corrupt memory. Variable-length GPIO/serial/resource-source paths are the riskiest. Tests should fuzz malformed AML resource lengths and offsets, round-trip every descriptor type, verify native alignment, exercise conditional compact encodings, and assert invalid conversion opcodes return `AE_BAD_PARAMETER`.
