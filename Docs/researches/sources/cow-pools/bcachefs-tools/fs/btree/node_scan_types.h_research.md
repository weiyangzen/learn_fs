# File Research: sources/cow-pools/bcachefs-tools/fs/btree/node_scan_types.h

Read completeness: full file read, 31 lines.

Purpose: type definitions for scanned btree-node recovery state.

Key definitions:
- `found_btree_node` stores the logical identity and physical replicas of one discovered node: btree id, level, sectors written, node sequence, journal sequence, cookie, min/max key range, replica count, and extent pointers.
- `range_updated` records that recovery trimmed the node's logical range because another discovered node overwrote part of it.
- `DEFINE_DARRAY(found_btree_node)` creates the dynamic array type used by the scanner.
- `struct find_btree_nodes` owns scan status, a mutex, and the discovered-node array.

Dependencies and integration:
- Includes `util/darray.h`; relies on `struct bpos` and `struct bch_extent_ptr` definitions from broader bcachefs type includes.
- Embedded in `struct bch_fs_btree` as `node_scan` via `types.h`.

Risks and validation notes:
- `ptrs` is capped at `BCH_REPLICAS_MAX`; scanner code treats overflow as a recovery error.
- `ret` is shared by worker threads and updated under broader scanner conventions; node insertion itself is protected by `lock`.
