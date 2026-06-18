# sources/distributed-fs/ceph-client/drivers/mcb/mcb-parse.c

## Purpose
`mcb-parse.c` parses MEN Chameleon FPGA descriptor tables and instantiates MCB devices from general device descriptors.

## Important APIs, Types, and Functions
Main routines are `get_next_dtype()`, `chameleon_parse_gdd()`, `chameleon_parse_bar()`, `chameleon_get_bar()`, and exported `chameleon_parse_cells()`. `chameleon_parse_bdd()` is present but currently a stub.

## Control Flow, State, and Persistence
Parsing copies the header from IO memory, validates Chameleon v2 magic, stores revision/model/minor/name into the MCB bus, obtains BAR descriptors either from the table or from the carrier map base, then iterates descriptor cells until `CHAMELEON_DTYPE_END`. General descriptors allocate `mcb_device`, decode ID/revision/variant/BAR/group/instance, skip unsupported/missing/IO-mapped BARs without failing the whole parse, fill IRQ and memory resources, and register devices. The return value is the parsed table size so carriers can remap the exact descriptor window. Persistent state is hardware descriptor memory; runtime state is allocated devices and resource ranges.

## Dependencies and Integration Points
It uses IO accessors, kernel allocation helpers, resource flags, exported MCB registration APIs, and `mcb-internal.h` layouts. PCI and LPC carriers both call `chameleon_parse_cells()`.

## Risks and Test Signals
Risks include unimplemented bridge descriptors, invalid descriptor loops without bounds beyond hardware data, endian handling, BAR count validation, leaking an allocated device if `mcb_device_register()` fails after initialization, and unsupported IO BARs. Tests should feed valid/invalid descriptor tables, zero-cell tables, bad magic, missing BARs, max BAR descriptors, and bridge descriptors.
