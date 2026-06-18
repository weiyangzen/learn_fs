# sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt_empty_tree.c

Purpose: convenience constructor for an empty but fully open read-write FDT containing only the root node.

Important APIs/functions: `fdt_create_empty_tree()` chains `fdt_create()`, `fdt_finish_reservemap()`, `fdt_begin_node("")`, `fdt_end_node()`, `fdt_finish()`, and finally `fdt_open_into(buf, buf, bufsize)` to convert the compact sequential-write result into a version-17 mutable blob with remaining buffer space.

Control flow/state: strict sequential-write state transitions: create, reserve-map completion, structure emission, finalization, then read-write reopening. Any error aborts and returns the libfdt negative error code.

Dependencies/integration: depends on `fdt_sw.c` creation APIs and `fdt_rw.c` `fdt_open_into`. Used by callers needing a blank tree before adding nodes/properties.

Risks: in-place `fdt_open_into` must preserve the just-created blob while expanding totalsize to the caller buffer. The function assumes the caller supplied enough aligned memory and handles no allocation itself.

Test signals: tiny buffer `-FDT_ERR_NOSPACE`, valid root-only tree layout, ability to add properties after creation, and preservation of total buffer size for later mutations.
