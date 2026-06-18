<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/lpt.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/lpt.c

## Purpose
`lpt.c` implements the read-side, formatting, packing, validation, lookup, hashing, and scan mechanics for UBIFS's LEB Properties Tree (LPT). The LPT is a flash-resident wandering tree that stores per-main-LEB free/dirty/index-category metadata in pnodes, internal nnode branches, an LPT-area lprops table (`ltab`), and, for big LPTs, an `lsave` table of useful main-area LEBs to pre-load at mount.

## Important APIs, Types, and Functions
Key exported functions are `ubifs_calc_lpt_geom()`, `ubifs_create_dflt_lpt()`, `ubifs_pack_pnode()`, `ubifs_pack_nnode()`, `ubifs_pack_ltab()`, `ubifs_pack_lsave()`, `ubifs_unpack_bits()`, `ubifs_unpack_nnode()`, `ubifs_read_nnode()`, `ubifs_get_nnode()`, `ubifs_get_pnode()`, `ubifs_pnode_lookup()`, `ubifs_lpt_lookup()`, `ubifs_lpt_lookup_dirty()`, `ubifs_lpt_calc_hash()`, `ubifs_lpt_init()`, `ubifs_lpt_scan_nolock()`, and debug validator `dbg_check_lpt_nodes()`. The major in-memory objects are `struct ubifs_nnode`, `struct ubifs_pnode`, `struct ubifs_lprops`, `struct ubifs_lpt_lprops`, and `struct lpt_scan_node`.

## Control Flow
Geometry setup starts with `do_calc_lpt_geom()`, which derives tree height, pnode/nnode counts, packed bit widths, and total LPT size. `ubifs_calc_lpt_geom()` validates an existing superblock geometry, while `calc_dflt_lpt_geom()` iteratively chooses default small or big LPT sizing for formatting. `ubifs_create_dflt_lpt()` then writes initial pnodes, builds parent nnodes bottom-up, records root/ltab/lsave/head locations, computes the LPT hash, and initializes the first root/index/inode LEB properties.

Runtime reads are lazy. `ubifs_pnode_lookup()` descends from `c->nroot`, using `ubifs_read_nnode()` and `read_pnode()` only when an nnode or pnode is absent from memory. A zero flash branch is treated as an unwritten all-empty subtree. Dirty lookups use `ubifs_lpt_lookup_dirty()`, which performs copy-on-write through `dirty_cow_nnode()` and `dirty_cow_pnode()` when commit has marked existing cnodes with `COW_CNODE`.

## State and Persistence
Packed LPT nodes do not use normal UBIFS common headers. Bitfields are compacted by `pack_bits()` and `ubifs_unpack_bits()`, with crc16 stored at the front. Pnodes persist per-main-LEB `free`, `dirty`, and `LPROPS_INDEX`; category flags are reconstructed in memory by `ubifs_categorize_lprops()`. Nnodes persist branch `(lnum, offs)` pairs. `ltab` persists free/dirty accounting for the LPT area itself. `lsave` persists a small cache of main LEB numbers. `ubifs_lpt_calc_hash()` hashes packed pnodes for authenticated mounts and is checked by `lpt_check_hash()` against the master node.

## Dependencies and Integration Points
The file depends on UBI IO helpers (`ubifs_leb_read()`, `ubifs_leb_change()`, `ubifs_leb_unmap()`), LEB-property category helpers (`ubifs_add_to_cat()`, `ubifs_replace_cat()`, `ubifs_ensure_cat()`), cryptographic hash helpers, CRC16, allocation wrappers, and master-node fields (`c->mst_node->hash_lpt`). `find.c`, `lprops.c`, replay, GC, and budgeting consume `ubifs_lpt_lookup*()` and `ubifs_lpt_scan_nolock()`.

## Risks and Test Signals
High-risk areas are bit-width math, CRC/type validation, big-vs-small numbering, automatic resize handling in `read_lsave()`, COW parent replacement during commit, and category-list replacement after pnode copy. Tests should stress format/mount on small and large volumes, authenticated mount hash mismatch, corrupt LPT CRC/type/branch offsets, resize with stale lsave values, concurrent lprops updates during commit, and full LPT scans that request `LPT_SCAN_ADD` while validating category lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/lpt.c -->
