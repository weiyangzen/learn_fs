# sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-data.c

## Purpose
`ccs-data.c` parses CCS static-data firmware blobs into `struct ccs_data_container`. These blobs can contain version metadata, sensor/module read-only register snapshots, manufacturer-specific register writes, conditional rule blocks, frame-format descriptors, PDAF metadata, licenses, and end markers.

## Important APIs, Types, and Functions
The exported API is `ccs_data_parse()`. Internally, `struct bin_container` implements a two-pass arena allocator: first pass reserves aligned sizes, second pass allocates one `kvzalloc()` backing store and fills pointers. Key parsers are `ccs_data_parse_length_specifier()`, `ccs_data_block_parse_header()`, `ccs_data_parse_regs()`, `ccs_data_parse_rules()`, `ccs_data_parse_ffd()`, `ccs_data_parse_pdaf_readout()`, `ccs_data_parse_pdaf()`, `ccs_data_parse_license()`, and `ccs_data_parse_end()`.

## Control Flow
`ccs_data_parse()` calls `__ccs_data_parse()` once with no backing store to validate structure and compute allocation size. It then allocates the backing arena and calls the same parser again to populate the in-memory container. The parser validates the static-data version, walks blocks until the blob end, decodes each header's payload length, and dispatches by block ID. Rule-based blocks require an IF rule to start a rule group; subsequent rule entries attach read-only registers, manufacturer registers, frame format, or PDAF readout to the current rule.

## State and Persistence Behavior
The parser creates one self-contained backing allocation stored in `ccsdata->backing`; all nested pointers reference that allocation. On parse failure it frees the backing and zeroes the container. No disk state is written. The resulting parsed register arrays persist in memory until probe cleanup or device remove and are consulted before live sensor reads or during manufacturer-register programming.

## Dependencies and Integration Points
The parser depends on packed binary definitions from `ccs-data-defs.h`, kernel allocation/string helpers, and a `struct device` for diagnostics. `ccs-core.c` loads firmware with `request_firmware()` and calls this parser for sensor and module blobs. `ccs-reg-access.c` uses parsed read-only registers to satisfy some CCS register reads without touching hardware.

## Risks and Edge Cases
The code is bounds-check heavy, but pointer arithmetic on `void *` is a GNU C extension. Rule parsing assumes non-IF entries follow an IF entry; malformed ordering fails. PDAF block parsing derives `max_block_type_id` from block descriptors and then expects matching pixel descriptor groups; malformed block type IDs or truncated groups return errors. `ccs_data_parse_pdaf()` checks `__bdesc->block_type_id >= num_block_descs`, which compares a block type ID to the current group's descriptor count rather than the eventual number of pixel descriptor groups; this may be overly strict for some legal encodings. License data is copied without appending a NUL terminator, so consumers must use `license_length`.

## Test Signals
Use parser tests or firmware fixtures covering one-, two-, and three-byte length specifiers; register encodings with address deltas and absolute addresses; empty and multi-entry register lists; rule ordering errors; FFD row/column descriptors; PDAF location/readout data; license payloads; unknown block IDs; short headers; and backing-size mismatch detection.
