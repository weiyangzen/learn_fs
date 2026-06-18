# sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-data-defs.h

## Purpose
`ccs-data-defs.h` defines the packed on-wire/on-firmware binary format for CCS static data files consumed by `ccs-data.c`. It is not a runtime parser; it documents block IDs, length encodings, register encodings, frame-format descriptors, rule records, PDAF descriptors, and the end block layout.

## Important APIs, Types, and Functions
Important definitions include `CCS_STATIC_DATA_VERSION`, the variable-width length specifier structs, `struct __ccs_data_block`, `enum __ccs_data_block_id`, packed register block variants, frame-format descriptor pixelcode enums, rule IDs, PDAF readout orders, PDAF pixel-location record structs, and `struct __ccs_data_block_end`. All structs are `__packed` because parser offsets must match the binary blob exactly.

## Control Flow
There is no executable control flow. `ccs_data_parse()` uses the first block's high ID bits as the static-data format version, decodes length specifiers, dispatches block IDs, then interprets payloads according to the packed structs and enums here.

## State and Persistence Behavior
The header stores no state. It defines firmware block formats that are parsed into `struct ccs_data_container`; those parsed containers can override or supplement live sensor/module registers and manufacturer-specific registers.

## Dependencies and Integration Points
It includes `ccs-data.h` for in-memory type relationships and is tightly coupled to `ccs-data.c`. Parsed data is later used by `ccs-reg-access.c` for read-only register lookup and by `ccs-core.c` for manufacturer-specific register writes.

## Risks and Edge Cases
Any layout drift breaks binary compatibility with CCS static-data firmware. Length specifier interpretation, big-endian multi-byte fields, and variable register address deltas are especially sensitive. The duplicate numeric value for vendor/original-order PDAF pixelcode is intentional-looking but can confuse consumers that expect unique symbolic values.

## Test Signals
Build coverage should catch missing symbols. Runtime tests need valid and malformed static-data firmware with every block family: version, sensor/module read-only registers, manufacturer registers, rules, FFD, PDAF readout/location, license, dummy, and end blocks.
