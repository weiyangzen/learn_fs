# sources/distributed-fs/ceph-client/scripts/dtc/dtc.h

## Purpose
`dtc.h` is the central public header for the DTC implementation. It declares command-line globals, endian helpers, data buffers, marker types, live tree structures, reserve and root tree metadata, and cross-module APIs.

## Important APIs, Types, and Functions
Core types are `cell_t`, `enum markertype`, `struct marker`, `struct data`, `struct label`, `struct property`, `struct node`, `struct reserve_info`, and `struct dt_info`. It defines traversal macros for labels, properties, children, and markers, helpers like `phandle_is_valid()`, `dtb_ld16/32/64()`, `strends()`, and `ALIGN()`, and declarations for data, live-tree, check, flattree, source, YAML, and filesystem operations.

## Control Flow and State
The header itself has no control flow. It exposes the shared state model: live tree nodes contain parent/child/sibling links, properties, labels, bus classification, phandles, address/size cell metadata, source positions, delete/omit/reference flags, and full paths populated after parsing.

## Dependencies and Integration
It depends on standard C headers, `libfdt_env.h`, `fdt.h`, and `util.h`. Almost every DTC C file includes it, making it the integration contract between parser, checks, tree manipulation, and output writers.

## Risks and Test Signals
Changes to struct layout or marker semantics affect the full compiler. Deleted nodes/properties remain in lists and are filtered by traversal macros, so callers must use the right iterator. Test by compiling all DTC objects, exercising parser/check/output round trips, and verifying phandle, marker, deletion, and source-position behavior.
