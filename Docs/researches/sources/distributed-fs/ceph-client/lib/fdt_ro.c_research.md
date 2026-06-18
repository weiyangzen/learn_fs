# sources/distributed-fs/ceph-client/lib/fdt_ro.c

## Purpose
Kernel wrapper for shared libfdt read-only query and traversal routines. It includes `linux/libfdt_env.h` and compiles `../scripts/dtc/libfdt/fdt_ro.c`.

## Important APIs, Types, and Functions
The included implementation provides read-only APIs for memory reservations, node/path lookup, property iteration and lookup, phandle discovery/generation, path construction, parent/depth queries, string-list helpers, and compatible matching. Examples include `fdt_get_mem_rsv()`, `fdt_num_mem_rsv()`, `fdt_subnode_offset()`, `fdt_path_offset()`, `fdt_first_property_offset()`, `fdt_next_property_offset()`, `fdt_get_phandle()`, `fdt_get_path()`, `fdt_parent_offset()`, `fdt_node_offset_by_prop_value()`, `fdt_node_offset_by_phandle()`, `fdt_stringlist_count()`, `fdt_stringlist_search()`, and `fdt_node_offset_by_compatible()`.

## Control Flow
The routines validate offsets through core libfdt helpers, walk the structure block, compare node names and properties, decode string lists, and return negative `FDT_ERR_*` values for invalid input or missing data. Search routines usually iterate from a supplied offset so callers can continue scanning.

## State and Persistence
No wrapper-owned state exists. All operations read caller-provided immutable FDT memory. Some functions write outputs to caller buffers or output pointers.

## Dependencies and Integration Points
Depends on libfdt core parsing and kernel environment definitions. It is a major integration point for early boot, platform discovery, driver matching, reserved-memory parsing, and other firmware data consumers.

## Risks
Read-only does not mean low-risk: malformed firmware blobs must be rejected without overread. Path and string-list handling can fail with truncation or malformed NUL termination. Phandle generation must avoid reserved/overflow values. Shared-source updates affect all kernel FDT readers.

## Test Signals
Use valid and malformed FDT blobs to test node/path/property lookup, memory reservation counts, compatible matching, string-list edge cases, phandle searches, parent/depth relationships, and output-buffer truncation.
