# sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt_ro.c

Purpose: read-only libfdt API implementation for string lookup, node/property navigation, phandles, paths, aliases, symbols, compatible/string-list helpers, and reserve-map access.

Important APIs/functions: `fdt_get_string`/`fdt_string`; phandle helpers `fdt_find_max_phandle`, `fdt_generate_phandle`, `fdt_get_phandle`, `fdt_node_offset_by_phandle`; reserve helpers `fdt_get_mem_rsv`, `fdt_num_mem_rsv`; path and node functions `fdt_subnode_offset*`, `fdt_path_offset*`, `fdt_get_name`, `fdt_get_path`, `fdt_parent_offset`; property functions `fdt_first_property_offset`, `fdt_get_property*`, `fdt_getprop*`; alias/symbol helpers; string-list and compatible search APIs.

Control flow/state: stateless traversal over the structure block using `fdt_next_node` and property iterators. Many APIs return pointers into the original blob and communicate errors through negative return values or `lenp`.

Dependencies/integration: built on `fdt.c` probing and tag traversal plus raw endian helpers. It is the read side consumed by overlay, read-write mutation, CLI tools, and external users.

Risks: old FDT versions before 16 require special property realignment and limit some property-structure APIs. Path lookup supports aliases only for non-absolute first components. Several scans are O(tree size) and comments call out suboptimal repeated property scans.

Test signals: string bounds/truncation, alias paths, omitted unit addresses, old-version realignment, parent/path reconstruction, malformed string lists, compatible matching, reserve terminators, and invalid phandle values.
