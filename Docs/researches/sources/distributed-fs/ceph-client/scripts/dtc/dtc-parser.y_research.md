# sources/distributed-fs/ceph-client/scripts/dtc/dtc-parser.y

## Purpose
`dtc-parser.y` is the Bison grammar for DTS files. It builds live tree structures, memory reservations, property data blobs, labels, references, overlays, delete markers, omit markers, included binary data, and integer expressions.

## Important APIs, Types, and Functions
The grammar uses a `%union` carrying property/node names, label refs, bytes, `struct data`, array metadata, properties, nodes, reserve entries, integers, and DTS flags. It calls live-tree builders such as `build_dt_info()`, `build_reserve_entry()`, `build_property()`, `build_node()`, `merge_nodes()`, `add_orphan_node()`, `delete_node()`, and data helpers. `is_ref_relative()` rejects label-relative plugin references.

## Control Flow and State
The root production builds `parser_output` from headers, reserves, and the device tree. Device-tree productions support root definitions, repeated root merges, label/path overlays, orphan plugin fragments, node deletion, and omit-if-no-ref. Property productions build empty, scalar, array, bytestring, path-reference, and incbin data. Integer expressions implement C-like precedence with divide-by-zero errors. Errors set `treesource_error`.

## Dependencies and Integration
It depends on Bison, lexer tokens, `srcpos`, `srcfile_relative_open()`, live-tree APIs, and data buffer APIs.

## Risks and Test Signals
The grammar uses `$<flags>-1` to inspect earlier header/plugin state, which is powerful but fragile. Incbin reads external files relative to source. Test plugin orphan handling, label/path references, relative reference rejection, delete nodes/properties, array bit widths, truncation warnings, expression precedence, incbin offsets/lengths, and property-before-subnode enforcement.
