# sources/distributed-fs/ceph-client/scripts/dtc/flattree.c

Purpose: converts DTC's in-memory `dt_info`/`node` tree to flattened device-tree binary or assembly output, and parses DTB input back into the live tree representation.

Important APIs/functions: version metadata in `version_table` controls FDT versions 1, 2, 3, 16, and 17. `struct emitter` abstracts binary vs assembly emission. `flatten_tree()` emits node tags, names, properties, synthetic legacy `name` properties, string-table entries, alignment, and children. `flatten_reserve_list()` serializes reserve entries plus requested expansion slots. `make_fdt_header()` lays out header offsets and size fields. Public emitters are `dt_to_blob()` and `dt_to_asm()`. Read-side helpers `struct inbuf`, `flat_read_*`, `flat_read_property()`, `flat_read_mem_reserve()`, and `unflatten_tree()` feed public `dt_from_blob()`.

Control flow/state: output is staged in `struct data` buffers for reserve map, structure block, strings, and final blob. Global DTC options `reservenum`, `minsize`, `padsize`, `alignsize`, and `quiet` affect layout and diagnostics. Input parsing reads the full `totalsize`, validates section offsets, chooses legacy flags by version, then recursively rebuilds nodes.

Dependencies/integration: depends on `dtc.h` tree/data APIs, `srcpos`, `fdt.h` structs/constants, endian helpers, and source-file open helpers. It is the main bridge between DTC parsing and libfdt-compatible DTB bytes.

Risks: string-table insertion is O(n). Old-version alignment and full-path semantics are subtle. `dt_from_blob()` validates bounds manually but exits via `die()` rather than returning errors. Malformed ordering of properties after subnodes is tolerated with a warning during unflattening.

Test signals: round trips for all supported FDT versions, reserve maps, legacy full-path/name-property blobs, NOP tags, padding/alignment/minsize options, assembly labels, malformed offset bounds, and plugin marker detection through `__fixups__`/`__local_fixups__`.
