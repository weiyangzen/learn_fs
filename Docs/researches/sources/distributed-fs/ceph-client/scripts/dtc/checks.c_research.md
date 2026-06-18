# sources/distributed-fs/ceph-client/scripts/dtc/checks.c

## Purpose
`checks.c` is the validation and fixup engine for DTC live trees. It reports structural, semantic, style, bus, phandle, interrupt, GPIO, and graph binding issues and performs reference fixups before output.

## Important APIs, Types, and Functions
`struct check` describes a named check, callback, data pointer, warning/error enablement, status, and prerequisites. Macros `WARNING`, `ERROR`, and `CHECK` declare checks. `check_msg()`, `FAIL`, and `FAIL_PROP` format diagnostics. `run_check()` enforces prerequisites and walks the tree through `check_nodes_props()`. Public APIs are `parse_checks_option()` and `process_checks()`.

## Control Flow and State
`process_checks()` iterates `check_table`, running enabled checks. Each check caches status as `UNCHECKED`, `PREREQ`, `PASSED`, or `FAILED`, and `inprogress` guards recursion. Some checks mutate the tree: `name_properties` removes redundant `name`, phandle and path reference checks patch property data, `omit_unused_nodes` deletes nodes, and bus checks set `node->bus`. Warning/error state is mutable through `-W` and `-E` options.

## Dependencies and Integration
It depends on DTC live-tree helpers from `livetree.c`, data/marker APIs, source positions, libfdt endian helpers, and global CLI flags such as `quiet` and `generate_symbols`.

## Risks and Test Signals
Checks have ordering dependencies and some mutate state used by later checks. Overlay/plugin behavior intentionally suppresses or defers some reference failures. Test duplicate names/labels, explicit and generated phandles, plugin unresolved references, bus-specific reg formats, interrupt maps, GPIO cell checks, graph endpoints, `-Wno-*`, `-E*`, `-f`, and quiet levels.
