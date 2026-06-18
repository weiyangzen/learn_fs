# sources/distributed-fs/ceph-client/scripts/dtc/fdtget.c

## Purpose
`fdtget.c` implements the `fdtget` host utility for reading property values, listing properties, or listing subnodes from a flattened device tree blob.

## Important APIs, Types, and Functions
`enum display_mode` selects value, properties, or subnodes. `struct display_info` stores type, cell size, mode, and default value. `show_data()` formats string lists or integer data using selected or guessed size. `list_properties()` and `list_subnodes()` enumerate libfdt structures. `show_data_for_item()` dispatches by mode. `do_fdtget()` reads the blob and processes node/property argument groups.

## Control Flow and State
`main()` parses `-t`, `-p`, `-l`, `-d`, and `-h`, validates filename and argument grouping, then calls `do_fdtget()`. The blob is loaded with `utilfdt_read()`. For each node path, missing nodes or properties either print the default value or produce libfdt diagnostics. State is local to the loaded blob and display options.

## Dependencies and Integration
It depends on libfdt, `util.h` helpers including `utilfdt_read()`, `utilfdt_decode_type()`, `util_is_printable_string()`, and `USAGE_TYPE_MSG`. It is built as part of DTC host tools.

## Risks and Test Signals
`show_data()` casts unaligned byte pointers to `uint32_t *` for 4-byte reads, which can matter on strict-alignment hosts. Listing subnodes manually walks tags with a fixed `MAX_LEVEL` of 32. Test string, byte, 16-bit, 32-bit, signed/unsigned/hex formatting, defaults, missing paths, property and subnode list modes, deep trees, and malformed blobs.
