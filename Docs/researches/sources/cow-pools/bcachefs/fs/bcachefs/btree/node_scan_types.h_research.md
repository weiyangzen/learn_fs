# File Research: sources/cow-pools/bcachefs/fs/bcachefs/btree/node_scan_types.h

This header defines the data model for scanned B-tree nodes.

Key types:
- `found_btree_node`: compact record for a discovered node, including range, btree id, level, sequence, journal sequence, cookie, written sectors, range-update flag, and up to `BCH_REPLICAS_MAX` extent pointers.
- `darray_found_btree_node`: dynamic array of discovered nodes.
- `find_btree_nodes`: scan state containing a return code, mutex, and node array.

The scan state is embedded in `struct bch_fs_btree` and shared between scan workers and recovery consumers. The mutex protects concurrent worker appends to the discovered node array.
