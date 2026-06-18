# sources/distributed-fs/ceph-client/scripts/dtc/treesource.c

Purpose: Converts DTS source text into `dt_info` by invoking the dtc parser, and serializes a device tree back to DTS source form.

Important APIs/functions: `dt_from_source()` initializes parser globals, pushes the source file, assigns `yyin` and `yylloc.file`, runs `yyparse()`, and returns `parser_output`. `dt_to_source()` emits `/dts-v1/`, optional `/plugin/`, reserve entries, and recursively writes the node tree. `property_add_marker()` and `add_phandle_marker()` enrich property values with type, label, and phandle markers used for formatting.

Control flow: Serialization calls `write_tree_source_node()` recursively. Properties go through `write_propval()`, which ensures type markers exist with `guess_type_markers()`, then emits strings, byte arrays, integer cells, phandle references, labels, delimiters, and optional source annotations. Marker insertion preserves ordering invariants so formatting can walk a single marker list.

State/persistence: Uses global `parser_output` and `treesource_error` for parser communication. It reads global `annotate` and `quiet` settings. It mutates property marker lists when guessing types and adding phandle markers.

Dependencies/integration: Depends on dtc core tree structures, marker macros, libfdt byte-load helpers, source-position formatting, parser globals, and node lookup by phandle. It is one output backend selected by dtc front-end code.

Risks: Guessing value types can change property marker state and may not preserve an exact original textual representation. `add_phandle_marker()` only handles 4-byte cells and warns for missing referenced nodes. Formatting assumes marker invariants and valid type marker lengths. Parser globals are not reentrant.

Test signals: Round-trip DTS to source for strings, string lists, bytes, 16/32/64-bit cells, labels, memreserve labels, plugin flag, phandle labels and absolute paths, annotations, and malformed phandle offsets.
