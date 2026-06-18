# sources/distributed-fs/ceph-client/scripts/dtc/livetree.c

Purpose: core DTC in-memory device-tree construction, merging, lookup, sorting, phandle allocation, and generation/consumption of overlay metadata nodes.

Important APIs/functions: builders for labels, properties, nodes, reserve entries, and `dt_info`; merge/delete helpers; append helpers for unique strings/u32s; accessors by property, label, marker, path, phandle, and reference; `get_node_phandle()` allocates phandles and adds legacy/ePAPR properties according to global format; `sort_tree()` canonicalizes order. Overlay metadata functions generate `__symbols__`, `__fixups__`, `__local_fixups__`, reconstruct labels/fixup markers, and update local phandle markers.

Control flow/state: tree nodes/properties are linked lists with soft-delete flags and label delete flags. Merging overlays new content onto old nodes, replacing property values on name collision and recursively merging child collisions. Phandle allocation uses a static local counter and consults existing tree phandles.

Dependencies/integration: depends on `dtc.h` data/marker/tree types, global options (`phandle_format`, `generate_fixups`, `quiet`), and `srcpos`. It feeds serializers in `flattree.c` and receives parsed DTS/DTB/FS trees.

Risks: soft-deleted elements remain in lists and must be filtered by iteration macros. Static phandle counter is process-global. Fixup string parsing temporarily mutates property data. Existing malformed metadata produces warnings and partial recovery.

Test signals: duplicate label resurrection, property/node delete overlays, merge collision behavior, path/label/phandle references, sorting determinism, phandle formats, symbol/fixup/local-fixup generation, and malformed metadata warnings.
