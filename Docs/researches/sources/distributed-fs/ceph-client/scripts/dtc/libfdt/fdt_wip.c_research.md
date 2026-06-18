# sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt_wip.c

Purpose: work-in-place helpers that modify existing structure bytes without resizing the blob, primarily replacing property values or NOP-ing properties/nodes.

Important APIs/functions: `fdt_setprop_inplace_namelen_partial()` writes a byte range inside an existing property after bounds checking. `fdt_setprop_inplace()` replaces an entire property only when the length is identical. `fdt_nop_region_()` fills a byte range with `FDT_NOP` tags. `fdt_nop_property()` finds a property and NOPs its record. `fdt_node_end_offset_()` computes a subtree end offset via depth traversal. `fdt_nop_node()` NOPs an entire node subtree.

Control flow/state: no block sizes or offsets are changed. NOP operations preserve byte layout while making tags ignored by traversal. In-place set APIs return `-FDT_ERR_NOSPACE` for length mismatches because resizing is outside this module.

Dependencies/integration: uses read-only property lookup, writable pointer helpers, `fdt_next_node`, and endian tag writes. Overlay code uses partial in-place writes for phandle fixups where property sizes are fixed.

Risks: `fdt_nop_property()` uses property value length plus header size without tag alignment padding, so behavior relies on existing layout and traversal tolerance. These APIs are unsuitable for size-changing updates.

Test signals: exact-length replacements, partial unaligned phandle writes, out-of-bounds partial writes, node/property NOP traversal skip behavior, and subtree end calculation on malformed trees.
