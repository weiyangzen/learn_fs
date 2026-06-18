# File Research: sources/cow-pools/bcachefs-tools/fs/btree/node_scan.h

Read completeness: full file read, 18 lines.

Purpose: public declarations for btree node scanning and scanned-node recovery queries.

Declared API:
- `bch2_found_btree_node_to_text()` formats one scanned node.
- `bch2_scan_for_btree_nodes()` performs the scan and normalizes discovered nodes.
- `bch2_btree_node_is_stale()` tests a loaded node against scan results.
- `bch2_btree_has_scanned_nodes()` and `bch2_get_scanned_nodes()` expose recovery queries over scanned nodes.
- `bch2_find_btree_nodes_init()` and `bch2_find_btree_nodes_exit()` manage `struct find_btree_nodes` lifetime.

Dependencies and integration:
- Expects `struct printbuf`, `struct bch_fs`, `struct found_btree_node`, `struct btree`, and `struct find_btree_nodes` from surrounding bcachefs headers.
- Implemented by `node_scan.c`; state types are in `node_scan_types.h`.

Risks and validation notes:
- This header does not include `node_scan_types.h` directly, so users must include appropriate type definitions before using the full signatures.
