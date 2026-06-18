# sources/distributed-fs/ceph-client/scripts/dtc/libfdt/fdt_rw.c

Purpose: read-write libfdt API for mutating complete, version-17-compatible DTBs in caller-provided buffers.

Important APIs/functions: `fdt_rw_probe_()` verifies read-write suitability and block order. Splice helpers move bytes in memory and update offsets/sizes for reserve, structure, and string blocks. Public APIs add/delete reserve entries, set node names, set/append/delete properties, add/delete subnodes, open/repack blobs, and normalize layout with `fdt_open_into()`/`fdt_pack()`. `fdt_find_add_string_()` deduplicates or appends property names with rollback support.

Control flow/state: all mutation is in-place and may shift structure offsets, invalidating cached offsets after insertion/deletion. `fdt_open_into()` can convert supported older layout/version into ordered version 17 and expand totalsize to the target buffer. `fdt_pack()` compacts data and shrinks totalsize to actual used bytes.

Dependencies/integration: depends on read-only lookup APIs, `fdt_next_tag`, internal reserve/offset helpers, and assumption masks. CLI tools and overlay application use these mutators.

Risks: caller must provide enough slack or handle `-FDT_ERR_NOSPACE`. Misordered blocks require `fdt_open_into()` before other writes. Rollback of newly added strings can be disabled by `ASSUME_NO_ROLLBACK`, leaving harmless but persistent string-table growth after failed mutations.

Test signals: property resize grow/shrink, append, delete, subnode insertion ordering after properties, node deletion, reserve-map splicing, opening misordered/old blobs, overlapping output buffers, packing, and offset invalidation behavior.
