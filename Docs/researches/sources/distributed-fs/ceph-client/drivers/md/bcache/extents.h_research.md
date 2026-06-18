# sources/distributed-fs/ceph-client/drivers/md/bcache/extents.h

Purpose: declares the extent and B-tree-pointer operation tables and public validation/formatting helpers implemented by `extents.c`.

Important APIs: `bch_btree_keys_ops` configures `btree_keys` for interior-node child pointers. `bch_extent_keys_ops` configures leaf nodes for data extents. `bch_extent_to_text()` formats keys for diagnostics. `__bch_btree_ptr_invalid()` and `__bch_extent_invalid()` validate keys against a cache set when a full `btree_keys` wrapper is not available.

Control flow: this header is included by B-tree, journal, debug, and request-adjacent code so they can initialize key containers or perform direct validation before marking/replaying keys.

State and persistence: no local state. The declared ops determine how on-disk bsets are canonicalized after reads and before writes, so changing them changes persistent B-tree semantics.

Dependencies/integration: forward-declares `struct bkey` and `struct cache_set`; relies on `struct btree_keys_ops` being visible to includers through the bcache headers.

Risks/test signals: because the header exports only a small set of contracts, ABI drift is mostly semantic: callers must choose the correct ops table for node level. Tests should assert leaf nodes use extent ops and interior nodes use pointer ops, and that journal replay rejects invalid extents through `__bch_extent_invalid()`.
