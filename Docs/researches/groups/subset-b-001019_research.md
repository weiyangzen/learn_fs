# subset-b-001019 Research

Grouped research report for ACPICA resource-manager and table-data source files. Each file section preserves the original source path in its title and is bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsaddr.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsaddr.c

Purpose: implements the conversion metadata and common helpers for ACPI address resource descriptors: `Address16`, `Address32`, `Address64`, and `ExtendedAddress64`. It is part of the ACPICA resource manager's table-driven AML-to-internal-resource and internal-resource-to-AML conversion path.

Important APIs, types, and functions: the exported data symbols are `acpi_rs_convert_address16`, `acpi_rs_convert_address32`, `acpi_rs_convert_address64`, and `acpi_rs_convert_ext_address64`, each a `struct acpi_rsconvert_info` conversion table. The local flag tables `acpi_rs_convert_general_flags`, `acpi_rs_convert_mem_flags`, and `acpi_rs_convert_io_flags` describe bit extraction/insertion for common, memory-specific, and I/O-specific address flags. `acpi_rs_get_address_common()` validates the AML resource type and imports common/type-specific flags; `acpi_rs_set_address_common()` writes the same fields back to AML.

Control flow: descriptor-specific conversion begins with `ACPI_RSC_INITGET`/`ACPI_RSC_INITSET`, invokes `ACPI_RSC_ADDRESS` for common flags, moves contiguous granularity/min/max/translation/length fields at the correct integer width, and optionally handles `resource_source`. The common getter rejects resource types greater than `2` unless they are vendor-defined `>= 0xC0` or the known value `0x0A`; memory and I/O ranges are decoded through specific flag tables, while bus/generic ranges preserve the raw `type_specific` byte.

State and persistence: this file holds static conversion tables only and mutates caller-provided AML/resource buffers during conversion. There is no independent persistent state.

Dependencies and integration points: depends on `acresrc.h` conversion opcodes, `union aml_resource`, `struct acpi_resource`, and dispatch from `rsinfo.c`. `rsmisc.c` interprets these tables, while `rsxface.c`, `rscreate.c`, and `rsutils.c` expose/use the converted resources for `_CRS`, `_PRS`, `_SRS`, and address normalization.

Risks and test signals: correctness depends on structure offsets matching ACPICA ABI layouts and AML descriptor definitions. Bad flag bit positions or width moves can corrupt PCI/root-bus windows, memory apertures, or I/O decode semantics. Boundary tests should round-trip address descriptors with memory, I/O, bus, vendor-defined, optional `resource_source`, and extended address type-specific attributes, plus reject invalid AML resource type values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsaddr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/rscalc.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/rscalc.c

Purpose: calculates buffer sizes for ACPICA resource conversions before allocation. It determines internal `struct acpi_resource` list size from an AML resource byte stream, AML stream size from an internal resource list, and `struct acpi_pci_routing_table` size from a `_PRT` package.

Important APIs, types, and functions: `acpi_rs_get_aml_length()` walks an internal resource list and returns required AML bytes. `acpi_rs_get_list_length()` walks AML descriptors and returns required internal resource bytes. `acpi_rs_get_pci_routing_table_length()` sizes a flattened PCI routing table. Helpers include `acpi_rs_count_set_bits()`, `acpi_rs_struct_option_length()`, and `acpi_rs_stream_option_length()`.

Control flow: `acpi_rs_get_aml_length()` validates resource type and nonzero length, starts from `acpi_gbl_aml_resource_sizes`, then adjusts for optional flags, vendor data, resource sources, interrupt counts, GPIO/pin tables, serial bus subtype sizes, labels, and vendor payloads. It returns normally only when an `END_TAG` is found. `acpi_rs_get_list_length()` validates each AML descriptor with `acpi_ut_validate_resource()`, computes extra bytes for variable fields such as IRQ/DMA bitmasks, vendor payloads, optional source strings, extended IRQ arrays, GPIO/pin offsets, and serial bus subtype payloads, rounds each internal descriptor to native-word alignment, and stops at `END_TAG`. `_PRT` sizing validates each top-level element is a package, scans for source string/reference/null, rounds each entry to 64-bit alignment, and adds a zero-length terminator entry.

State and persistence: no global state is owned here. The functions read global size tables from `rsinfo.c` and write only output size values. Allocation happens later in `rscreate.c` and `rsutils.c`.

Dependencies and integration points: heavily coupled to `rsinfo.c` size arrays, `acpi_ut_get_resource_*` descriptor helpers, namespace path sizing for `_PRT` references, and conversion allocation in `rscreate.c`. Its sizing results must match `rsmisc.c` conversion behavior exactly.

Risks and test signals: this is a primary memory-safety boundary. Underestimates cause conversion-time overwrites; overestimates waste memory but are safer. Risks include unsigned underflow when counts are malformed, offset arithmetic for GPIO/pin descriptors, missing `END_TAG`, zero-length internal descriptors, and serial bus subtype index validity. Tests should include malformed AML lengths, absent end tags, empty and multi-entry IRQ/DMA masks, large vendor data, all GPIO/pin/serial variable sections, and `_PRT` packages with strings, references, integers, nulls, and wrong element counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/rscalc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/rscreate.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/rscreate.c

Purpose: creates caller-visible ACPICA resource objects from AML buffers or namespace method results, and creates AML resource byte streams from internal resource lists for `_SRS`.

Important APIs, types, and functions: `acpi_buffer_to_resource()` is exported and converts a raw AML buffer into an allocated `struct acpi_resource` list. `acpi_rs_create_resource_list()` converts an evaluated `_CRS`, `_PRS`, `_AEI`, or similar buffer object into a caller-supplied `struct acpi_buffer`. `acpi_rs_create_pci_routing_table()` flattens `_PRT` packages into `struct acpi_pci_routing_table` entries. `acpi_rs_create_aml_resources()` converts an internal resource list to AML.

Control flow: raw AML conversion first calls `acpi_rs_get_list_length()`, allocates or initializes a buffer, then walks AML with `acpi_ut_walk_aml_resources()` and `acpi_rs_convert_aml_to_resources()`. `acpi_buffer_to_resource()` specifically tolerates `AE_AML_NO_RESOURCE_END_TAG`, while method-based list creation expects the normal resource-template end tag. `_PRT` creation sizes the output, iterates subpackages of exactly four elements, validates address/pin/source/source-index types, copies strings or resolves namespace references to pathnames, aligns each entry length, and leaves a final zeroed terminator. AML creation uses `acpi_rs_get_aml_length()`, initializes the caller buffer, then calls `acpi_rs_convert_resources_to_aml()`.

State and persistence: allocates transient buffers via ACPICA allocation helpers and fills caller buffers. It does not own persistent state but does transfer allocated memory ownership to callers on success.

Dependencies and integration points: sits between method evaluation helpers in `rsutils.c`, public APIs in `rsxface.c`, length calculation in `rscalc.c`, conversion walking in `rslist.c`, and namespace path helpers for `_PRT`.

Risks and test signals: error-path cleanup is important because conversion failures after allocation must not leak. `_PRT` parsing is type-sensitive and must preserve alignment for consumer iteration. Tests should cover buffer-overflow sizing behavior, local-buffer allocation, no-end-tag raw buffer tolerance, conversion failures, `_PRT` malformed packages, reference-to-path conversion, integer null sources, and AML round-trips for `_SRS` inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/rscreate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsdump.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsdump.c

Purpose: provides debugger-only formatting and dumping of ACPICA resource lists and PCI IRQ routing tables. It turns `struct acpi_rsdump_info` tables from `rsdumpinfo.c` into human-readable diagnostic output.

Important APIs, types, and functions: under `ACPI_DEBUGGER`, `acpi_rs_dump_resource_list()` dumps each resource until `END_TAG`, and `acpi_rs_dump_irq_list()` dumps `_PRT` entries until a zero-length terminator. The core local interpreter is `acpi_rs_dump_descriptor()`, with helpers for optional resource sources/labels, address common flags, scalar formatting, and byte/word/dword lists.

Control flow: dump entrypoints first check debug level enablement. Resource-list dumping validates type and nonzero length, dispatches serial bus subtypes through `acpi_gbl_dump_serial_bus_dispatch`, all other resources through `acpi_gbl_dump_resource_dispatch`, then advances with `ACPI_NEXT_RESOURCE()`. The descriptor dumper uses the first table entry as a count and switches on opcodes such as title, literal, string, integer, bit flags, short/long lists, address common fields, source, label, and source-label. List opcodes depend on the previous table target as the length source.

State and persistence: no durable state; emits through `acpi_os_printf()` and reads debug configuration. It never changes resource objects.

Dependencies and integration points: compiled for debugger/disassembler/debug-output configurations and depends on dump tables from `rsdumpinfo.c`, decode string arrays, and public resource structures. It is a diagnostic companion to conversion logic, useful when inspecting `_CRS`, `_PRS`, `_AEI`, and `_PRT` results.

Risks and test signals: diagnostic paths still need guardrails against malformed in-memory resources because zero lengths or invalid types could otherwise loop or index dispatch tables incorrectly. Table opcode/count mismatches in `rsdumpinfo.c` can print wrong fields or dereference invalid offsets. Test signals include debugger builds that dump representative resources for every dispatch entry, serial bus subtypes, empty strings, optional source absence, and invalid/zero-length resource handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsdump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsdumpinfo.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsdumpinfo.c

Purpose: defines the data tables used by `rsdump.c` to print ACPICA resource descriptors. It has no conversion behavior itself; it maps resource structure offsets to labels, scalar/list opcodes, and decode tables.

Important APIs, types, and functions: exported table symbols include `acpi_rs_dump_irq`, `acpi_rs_dump_dma`, `acpi_rs_dump_*` address/memory/I/O/vendor/GPIO/pin/serial/fixed-DMA tables, common address flag tables, and `acpi_rs_dump_prt`. Macros `ACPI_RSD_OFFSET`, `ACPI_PRT_OFFSET`, and `ACPI_RSD_TABLE_SIZE` keep entries compact and countable.

Control flow: when compiled with `ACPI_DEBUG_OUTPUT`, `ACPI_DISASSEMBLER`, or `ACPI_DEBUGGER`, each table begins with a title or literal entry whose offset field stores table length. `rsdump.c` later iterates exactly that count and interprets the remaining entries. Common serial bus fields are shared through `ACPI_RS_DUMP_COMMON_SERIAL_BUS`; common address decoding is split into general, memory-specific, and I/O-specific tables.

State and persistence: static metadata only. It contains no mutable state and no runtime allocation.

Dependencies and integration points: must stay aligned with `union acpi_resource_data`, `struct acpi_pci_routing_table`, decode arrays such as `acpi_gbl_he_decode`, and dispatch arrays in `rsinfo.c`. The tables cover resources produced by `rsserial.c`, `rsirq.c`, `rsio.c`, `rsmemory.c`, and `rsaddr.c`.

Risks and test signals: stale offsets or wrong opcode types cause misleading debugger output and can hide conversion bugs. Because list opcodes rely on previous entries for lengths, entry ordering is part of the contract. Debugger/disassembler tests should dump every resource type, especially variable-length GPIO/pin/serial/vendor fields and `_PRT`, and compare output against known field values after AML round-trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsdumpinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsinfo.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsinfo.c

Purpose: centralizes ACPICA resource dispatch and size tables. It maps internal resource types, AML descriptor names, and serial bus subtypes to conversion tables, dump tables, and base structure sizes.

Important APIs, types, and functions: global arrays include `acpi_gbl_set_resource_dispatch`, `acpi_gbl_get_resource_dispatch`, `acpi_gbl_convert_resource_serial_bus_dispatch`, debug-only `acpi_gbl_dump_resource_dispatch`, debug-only `acpi_gbl_dump_serial_bus_dispatch`, `acpi_gbl_aml_resource_sizes`, `acpi_gbl_resource_struct_sizes`, `acpi_gbl_aml_resource_serial_bus_sizes`, and `acpi_gbl_resource_struct_serial_bus_sizes`.

Control flow: there are no functions. Runtime control flow occurs in consumers: `rslist.c` indexes get/set dispatch by AML resource index or internal type, handles serial bus through the subtype table, `rscalc.c` indexes size arrays for allocation planning, and `rsdump.c` indexes dump tables for diagnostics.

State and persistence: process-global read-only metadata. It does not allocate or mutate state.

Dependencies and integration points: integrates all resource descriptor implementation files. Adding a new resource type requires coordinated updates here, the relevant conversion table file, size calculations in `rscalc.c` when variable length is involved, dump tables in `rsdumpinfo.c`, and public type definitions.

Risks and test signals: array index order is the core risk. A misplaced entry can route an AML descriptor to the wrong conversion table or size, producing memory corruption or invalid resources. Serial bus entries start with a null slot and must remain bounded by `AML_RESOURCE_MAX_SERIALBUSTYPE`. Tests should validate dispatch coverage for every resource type and descriptor name, all size-table entries against `sizeof`/`ACPI_RS_SIZE`, and failure behavior for reserved or unsupported descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsio.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsio.c

Purpose: defines conversion tables for small I/O, fixed I/O, generic register, start/end dependent functions, and end tag resource descriptors.

Important APIs, types, and functions: table symbols include `acpi_rs_convert_io`, `acpi_rs_convert_fixed_io`, `acpi_rs_convert_generic_reg`, `acpi_rs_convert_end_dpf`, `acpi_rs_convert_end_tag`, `acpi_rs_get_start_dpf`, and `acpi_rs_set_start_dpf`.

Control flow: the I/O and fixed I/O tables move decode flags, base/min/max/alignment/length fields, and generic register address-space metadata using fixed-width conversion opcodes. End-dependent and end-tag descriptors are minimal `INITGET`/`INITSET` tables. `StartDependentFn` has asymmetric get/set logic: get initializes default acceptable priorities, reads descriptor length from the small descriptor type byte, exits early if no flags byte is present, and otherwise decodes two 2-bit priority fields. Set starts with the one-byte form, can force or optimize to zero-length priority data, and only omits the flags byte when both priority values are `ACPI_ACCEPTABLE_CONFIGURATION`.

State and persistence: static conversion metadata only; conversion mutates caller buffers through `rsmisc.c`.

Dependencies and integration points: dispatch comes from `rsinfo.c`; table execution is in `rsmisc.c`; length planning is in `rscalc.c`. End tags are especially important because list walkers in `rscalc.c`, `rslist.c`, `rsdump.c`, and `rsxface.c` stop on them.

Risks and test signals: end-tag and zero-length dependent-function behavior affects resource-template termination and list walking. Start-dependent optimization has explicit TODO comments about validating incompatible flags for zero-byte descriptors. Tests should round-trip fixed and variable `StartDependentFn` descriptors, generic registers with 64-bit addresses, end tags, and missing end-tag error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsirq.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsirq.c

Purpose: defines conversion tables for IRQ, extended IRQ, DMA, and fixed DMA resource descriptors.

Important APIs, types, and functions: table symbols are `acpi_rs_get_irq`, `acpi_rs_set_irq`, `acpi_rs_convert_ext_irq`, `acpi_rs_convert_dma`, and `acpi_rs_convert_fixed_dma`.

Control flow: short IRQ get decodes a 16-bit IRQ mask to an interrupt list, sets default edge-sensitive triggering, reads whether the optional flags byte exists, and exits early when absent. IRQ set encodes the list back to a bitmask, writes flags, and can optimize from a 3-byte descriptor to a 2-byte no-flags descriptor when triggering, polarity, and sharing match ACPI defaults. Extended IRQ moves producer/consumer, triggering, polarity, sharing, wake, interrupt count, a variable dword interrupt array, and optional resource source. DMA converts transfer/bus-master/type flags and an 8-bit channel mask. Fixed DMA moves request lines, channels, and width.

State and persistence: static conversion tables only.

Dependencies and integration points: relies on bitmask helpers in `rsutils.c`, the generic conversion interpreter in `rsmisc.c`, size logic in `rscalc.c`, and dispatch from `rsinfo.c`.

Risks and test signals: malformed interrupt counts and bitmasks are sensitive because they affect variable internal length. IRQ no-flags optimization has the same compatibility caveat as start-dependent functions. Extended IRQ must enforce at least one interrupt through validation elsewhere. Tests should cover empty/full IRQ masks, multiple extended interrupts, optional resource source, wake/share flags, DMA masks, fixed DMA widths, and conversion of default flags to compact AML descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsirq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/rslist.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/rslist.c

Purpose: performs list-level conversion between AML resource byte streams and native `struct acpi_resource` lists by dispatching each descriptor to the table-driven converter.

Important APIs, types, and functions: `acpi_rs_convert_aml_to_resources()` is an `acpi_ut_walk_aml_resources()` callback that converts one AML descriptor and advances the output pointer. `acpi_rs_convert_resources_to_aml()` walks an internal resource list and writes AML descriptors to an output buffer.

Control flow: AML-to-resource conversion checks output alignment, chooses the correct conversion table from the normal get dispatch table or serial bus subtype table, errors on unsupported descriptors, calls `acpi_rs_convert_aml_to_resource()`, warns on zero output length, then advances with `ACPI_NEXT_RESOURCE()`. Resource-to-AML conversion loops until the planned AML buffer end, validates internal type and nonzero length, selects the set conversion table or serial bus subtype conversion table, calls `acpi_rs_convert_resource_to_aml()`, validates the newly emitted AML descriptor with `acpi_ut_validate_resource()`, returns success on `END_TAG`, and otherwise advances both AML and internal-resource pointers.

State and persistence: no owned state. It mutates caller-supplied output buffers and pointer context.

Dependencies and integration points: connects `rscreate.c` allocation/sizing to the conversion interpreter in `rsmisc.c`, dispatch metadata in `rsinfo.c`, AML validation helpers, and public walkers in `rsxface.c`.

Risks and test signals: this is a loop-safety boundary. Unsupported serial bus subtypes, invalid resource types, zero lengths, missing `END_TAG`, or a converter that emits invalid AML all stop the operation. Tests should assert no infinite loops on zero length, rejection of out-of-range types/subtypes, validation failures after conversion, and exact end-tag termination behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/rslist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsmemory.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsmemory.c

Purpose: defines conversion tables for memory range descriptors and vendor-defined resource descriptors.

Important APIs, types, and functions: table symbols include `acpi_rs_convert_memory24`, `acpi_rs_convert_memory32`, `acpi_rs_convert_fixed_memory32`, `acpi_rs_get_vendor_small`, `acpi_rs_get_vendor_large`, and `acpi_rs_set_vendor`.

Control flow: memory tables initialize the correct internal/external descriptor type, convert read/write protection, and move contiguous address fields at 16-bit or 32-bit width. Fixed memory moves base address and length. Vendor get tables use small or large AML header offsets, count vendor bytes from descriptor length, and copy byte data. Vendor set starts as a small vendor descriptor, copies byte data, exits when byte length is at most seven, and otherwise reinitializes as a large vendor descriptor and repeats length/data setup.

State and persistence: static conversion metadata only.

Dependencies and integration points: dispatched by `rsinfo.c`, executed by `rsmisc.c`, and sized by `rscalc.c`. Vendor resources are also searched by `acpi_get_vendor_resource()` in `rsxface.c`.

Risks and test signals: vendor small/large switching is a compatibility boundary because AML small descriptors can hold only seven data bytes. Incorrect counts can shift the variable data payload or misrepresent typed vendor UUID resources. Tests should round-trip memory24, memory32, fixed-memory32, zero-length vendor data, 1-7 byte small vendor data, 8+ byte large vendor data, and vendor UUID matching through `rsxface.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsmemory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsmisc.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsmisc.c

Purpose: implements the generic interpreter for `struct acpi_rsconvert_info` conversion tables. It is the core engine that transforms individual AML resource descriptors into internal resources and internal resources back into AML.

Important APIs, types, and functions: `acpi_rs_convert_aml_to_resource()` interprets get-side opcodes. `acpi_rs_convert_resource_to_aml()` interprets set-side opcodes. Supported operations include initialization, flag extraction/insertion, count/length adjustments, fixed-width moves, GPIO/pin/serial variable-data moves, resource source handling, address-common conversion, bitmask encoding/decoding, and conditional exits.

Control flow: get-side conversion starts by reading AML descriptor length, then iterates the table count from the first entry. `INITGET` zeros and initializes the internal resource; count opcodes expand `resource->length`; move opcodes copy scalar or variable data; `SOURCE`/`SOURCEX` delegate optional source parsing; bitmask opcodes decode lists; conditional exits stop early for compact descriptors. Unless in flag-subtable mode, final internal length is rounded to native word alignment. Set-side conversion starts with `INITSET`, zeroes AML, sets the descriptor header, adjusts AML length as count operations add variable data, writes offsets before moving GPIO/serial data, delegates source/address handling, and honors `EXIT_LE`, `EXIT_NE`, and `EXIT_EQ` optimizations.

State and persistence: no persistent state. It writes into caller-provided resource and AML buffers and depends on precomputed sizes being large enough.

Dependencies and integration points: consumes all conversion tables defined in `rsaddr.c`, `rsio.c`, `rsirq.c`, `rsmemory.c`, and `rsserial.c`; calls helpers from `rsutils.c`; and is invoked by `rslist.c`.

Risks and test signals: this file is highly pointer- and offset-sensitive. The interpreter trusts table opcode sequencing, counts, offsets, and prior sizing; a mismatch can corrupt memory. Variable-length GPIO/serial/resource-source paths are the riskiest. Tests should fuzz malformed AML resource lengths and offsets, round-trip every descriptor type, verify native alignment, exercise conditional compact encodings, and assert invalid conversion opcodes return `AE_BAD_PARAMETER`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsmisc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsserial.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsserial.c

Purpose: defines conversion tables for GPIO, pin, clock input, and serial bus resource descriptors, including I2C, SPI, UART, and CSI2 subtypes.

Important APIs, types, and functions: table symbols include `acpi_rs_convert_gpio`, `acpi_rs_convert_clock_input`, `acpi_rs_convert_pin_function`, `acpi_rs_convert_csi2_serial_bus`, `acpi_rs_convert_i2c_serial_bus`, `acpi_rs_convert_spi_serial_bus`, `acpi_rs_convert_uart_serial_bus`, `acpi_rs_convert_pin_config`, `acpi_rs_convert_pin_group`, `acpi_rs_convert_pin_group_function`, and `acpi_rs_convert_pin_group_config`.

Control flow: each table declares fixed header fields, flag bitfields, then variable sections. GPIO and pin descriptors use generic GPIO count/move opcodes for pin tables, resource source or labels, and vendor data. Clock input uses fixed scalar moves plus optional `resource_source`. Serial bus common descriptors move revision/type/slave/producer/sharing/type-data metadata, compute vendor length from subtype-specific minimum data lengths, copy vendor data, compute resource source string length from type data length, and then append subtype-specific fields such as I2C access mode/speed/address, SPI wire mode/polarity/selection/speed, UART flow/stop/data/parity/FIFO/baud, and CSI2 PHY/local port fields.

State and persistence: static conversion metadata only, with variable pointers set into caller-allocated internal resource storage during conversion.

Dependencies and integration points: dispatched through `rsinfo.c` normal and serial subtype tables, interpreted by `rsmisc.c`, sized in `rscalc.c`, and dumped through `rsdumpinfo.c`. This file covers many ACPI 5+/6+ descriptors used by GPIO controllers, pin controllers, camera links, and serial-attached peripherals.

Risks and test signals: variable offsets are dense and descriptor-specific. Incorrect offset/count handling can swap resource source, pin table, labels, or vendor data. Serial subtype sizes must remain consistent with `acpi_gbl_aml_resource_serial_bus_sizes` and `AML_RESOURCE_*_MIN_DATA_LEN`. Tests should round-trip each descriptor with empty and non-empty pin/vendor/source sections, all serial subtypes, boundary string lengths, and invalid subtype dispatch from `rslist.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsserial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsutils.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsutils.c

Purpose: provides helper functions for ACPICA resource conversion and namespace method execution. It handles bitmasks, endian/alignment-safe data movement, AML resource headers, optional resource sources, method evaluation for resource-producing methods, and `_SRS` invocation.

Important APIs, types, and functions: `acpi_rs_decode_bitmask()`, `acpi_rs_encode_bitmask()`, `acpi_rs_move_data()`, `acpi_rs_set_resource_length()`, `acpi_rs_set_resource_header()`, `acpi_rs_get_resource_source()`, `acpi_rs_set_resource_source()`, `acpi_rs_get_prt_method_data()`, `acpi_rs_get_crs_method_data()`, `acpi_rs_get_prs_method_data()`, `acpi_rs_get_aei_method_data()`, `acpi_rs_get_method_data()`, and `acpi_rs_set_srs_method_data()`.

Control flow: bitmask helpers convert IRQ/DMA masks to lists and back. `acpi_rs_move_data()` uses raw `memcpy` for byte moves and ACPICA move macros for 16/32/64-bit transfers to handle alignment/endian constraints. Header helpers write small-vs-large descriptor lengths. Resource-source get detects optional source data by comparing total length with the minimum descriptor length, copies index and null-terminated string, and rounds storage to native-word alignment; set appends index/string only when string length is nonzero. Method helpers evaluate `_PRT`, `_CRS`, `_PRS`, `_AEI`, or a named resource method, convert returned objects, release operand references, and for `_SRS` convert the input resource list to an AML buffer object before calling `acpi_ns_evaluate()`.

State and persistence: no durable state; it allocates temporary evaluation info and buffers, attaches buffers to operand objects, and releases references after method execution.

Dependencies and integration points: bridges resource conversion with ACPICA namespace/evaluator internals (`acpi_ut_evaluate_object`, `acpi_ns_evaluate`, operand objects, namespace nodes). Public APIs in `rsxface.c` delegate most method work here.

Risks and test signals: resource-source length math and `_SRS` buffer ownership are key risks. `acpi_rs_encode_bitmask()` assumes list values fit the target mask width. Tests should cover resource source absent/present strings, native alignment, endian-safe moves, all method helpers' object-type validation, reference cleanup on failures, and `_SRS` failure paths after AML buffer allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsutils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsxface.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsxface.c

Purpose: exposes ACPICA public resource-manager interfaces used by OS code and drivers to get, set, convert, search, and walk ACPI resources.

Important APIs, types, and functions: exported APIs include `acpi_get_irq_routing_table()`, `acpi_get_current_resources()`, `acpi_get_possible_resources()`, `acpi_set_current_resources()`, `acpi_get_event_resources()`, `acpi_resource_to_address64()`, `acpi_get_vendor_resource()`, `acpi_walk_resource_buffer()`, and `acpi_walk_resources()`. Internal helpers are `acpi_rs_validate_parameters()` and `acpi_rs_match_vendor_resource()`.

Control flow: common validation requires a non-null handle, a namespace node of type `ACPI_TYPE_DEVICE`, and a valid `struct acpi_buffer`. Getters then call `rsutils.c` helpers for `_PRT`, `_CRS`, `_PRS`, or `_AEI`; setter rejects empty input and calls `_SRS`. `acpi_resource_to_address64()` copies 16/32/64-bit address resource fields into a uniform 64-bit output. Vendor resource lookup walks a named resource method and copies the first vendor descriptor whose subtype and 16-byte UUID match. Resource walkers validate buffer/user callback, iterate until buffer end or `END_TAG`, reject invalid/zero-length descriptors, and treat `AE_CTRL_TERMINATE` from callbacks as successful early termination.

State and persistence: no global state is owned. APIs allocate local buffers through downstream helpers and free them after walking. `acpi_set_current_resources()` can persist device configuration by invoking firmware `_SRS`.

Dependencies and integration points: this is the external interface layer over `rsutils.c`, `rscreate.c`, and `rslist.c`. It is exported to the kernel/ACPICA integration through `ACPI_EXPORT_SYMBOL`.

Risks and test signals: public API validation must prevent non-device handles and bad buffers from reaching namespace execution. Walkers must not loop on zero-length resources. Vendor resource matching assumes typed vendor data layout. Tests should cover each exported API's parameter validation, buffer sizing semantics, `_CRS`/`_PRS`/`_AEI` walking, callback early termination, address conversion for all supported widths, and `_SRS` invocation with invalid and valid lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/rsxface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/tbdata.c -->
## sources/distributed-fs/ceph-client/drivers/acpi/acpica/tbdata.c

Purpose: manages ACPICA table descriptors and table lifecycle state: acquisition, validation, duplication checks, root table list growth, owner IDs, namespace load/unload, and table event notification.

Important APIs, types, and functions: descriptor/table helpers include `acpi_tb_init_table_descriptor()`, `acpi_tb_acquire_table()`, `acpi_tb_release_table()`, `acpi_tb_acquire_temp_table()`, `acpi_tb_release_temp_table()`, `acpi_tb_validate_table()`, `acpi_tb_invalidate_table()`, `acpi_tb_validate_temp_table()`, and `acpi_tb_verify_temp_table()`. Root-list and lifecycle APIs include `acpi_tb_resize_root_table_list()`, `acpi_tb_get_next_table_descriptor()`, `acpi_tb_terminate()`, `acpi_tb_delete_namespace_by_owner()`, owner-ID helpers, loaded-flag helpers, `acpi_tb_load_table()`, exported `acpi_tb_install_and_load_table()`, exported `acpi_tb_unload_table()`, and `acpi_tb_notify_table()`. Static helpers compare full table contents and check duplicates.

Control flow: acquisition maps physical-origin tables or returns virtual pointers based on origin flags; release unmaps only internal physical mappings. Temporary acquisition maps just the header when needed to learn length. Verification validates, optionally checks expected signature, verifies checksum when validation is enabled, checks full-content duplication against verified installed tables, and marks the descriptor verified. Root list resizing allocates a larger array, compacts descriptors with addresses, frees the prior owned array, and updates counts/flags. Loading gets the table by index, loads namespace objects, updates GPEs for the table owner, and notifies handlers. Unloading verifies loaded state, notifies before deletion, deletes namespace objects by owner under namespace write lock, releases owner ID, and clears the loaded flag.

State and persistence: mutates `acpi_gbl_root_table_list`, per-table descriptor flags/pointers/owner IDs, namespace objects, GPE registrations, and global table-handler callbacks. Mutex `ACPI_MTX_TABLES` protects root table metadata; namespace deletion uses `acpi_gbl_namespace_rw_lock`.

Dependencies and integration points: integrates table installation, OS memory mapping, checksum utilities, namespace loading/deletion, owner-ID allocation, event/GPE update, and external dynamic table load/unload callers.

Risks and test signals: lifecycle bugs can leak mappings, leave stale namespace nodes, double-load duplicate tables, or notify handlers with invalid pointers. `acpi_tb_install_and_load_table()` writes `*table_index = i` even after install failure, so callers rely on status before using it. Tests should cover all table origins, validation disabled vs enabled, checksum/signature failures, duplicate loaded vs unloaded tables, root-list resizing/compaction, concurrent load/unload locking, owner-ID lifecycle, GPE update after load, and handler notification order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/acpi/acpica/tbdata.c -->
