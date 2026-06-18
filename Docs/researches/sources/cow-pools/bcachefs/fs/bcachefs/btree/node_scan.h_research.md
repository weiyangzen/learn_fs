# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/node_scan.h

This header exposes the B-tree node scan recovery interface.

Public functions:
- `bch2_found_btree_node_to_text()` renders a scanned node and its replica pointers.
- `bch2_scan_for_btree_nodes()` performs the full device scan and normalizes the result list.
- `bch2_btree_node_is_stale()` checks whether a loaded node is older than a scanned overlapping node.
- `bch2_btree_has_scanned_nodes()` checks if scanned recovery data exists for a btree.
- `bch2_get_scanned_nodes()` emits scanned nodes into recovery output and the journal overlay.
- Init/exit helpers manage `struct find_btree_nodes`.

This is a narrow recovery API consumed by topology repair and node-read paths.
