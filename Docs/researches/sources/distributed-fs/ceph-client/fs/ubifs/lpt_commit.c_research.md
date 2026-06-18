<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/lpt_commit.c -->
# sources/distributed-fs/ceph-client/fs/ubifs/lpt_commit.c

## Purpose
`lpt_commit.c` implements commit-time persistence and garbage collection for the LPT. It freezes dirty LPT cnodes, lays them out in free LPT space, writes packed nodes plus `ltab`/`lsave`, frees obsolete COW copies, and keeps enough LPT free space available through trivial GC and big-LPT node relocation.

## Important APIs, Types, and Functions
The public entry points are `ubifs_lpt_start_commit()`, `ubifs_lpt_end_commit()`, `ubifs_lpt_post_commit()`, `ubifs_lpt_free()`, `dbg_check_ltab()`, `dbg_chk_lpt_free_spc()`, `dbg_chk_lpt_sz()`, and `ubifs_dump_lpt_lebs()`. Core private functions include `get_cnodes_to_commit()`, `layout_cnodes()`, `write_cnodes()`, `make_tree_dirty()`, `need_write_all()`, `lpt_tgc_start()`, `lpt_tgc_end()`, `populate_lsave()`, `lpt_gc()`, and `lpt_gc_lnum()`.

## Control Flow
Commit begins in `ubifs_lpt_start_commit()`. Under `lp_mutex`, it runs debug checks, optionally performs big-LPT GC until there is enough future free space, marks trivial-GC LEBs, makes the whole tree dirty for small LPTs when free space is low, populates `lsave`, builds a circular `cnext` list of currently dirty cnodes, and calls `layout_cnodes()` to assign new flash addresses. It then computes the LPT hash into the master node and snapshots `c->ltab` into `c->ltab_cmt`.

`ubifs_lpt_end_commit()` writes the frozen cnode list with `write_cnodes()`. This function repeats the same LEB allocation decisions using `realloc_lpt_leb()`, packs each nnode/pnode, writes aligned chunks, and clears `DIRTY_CNODE`/`COW_CNODE` with memory barriers so readers/writers see a coherent post-commit state. `ubifs_lpt_post_commit()` unmaps trivially collected LPT LEBs and, for big LPTs, runs relocation GC until `need_write_all()` is false.

## State and Persistence
The commit path maintains `c->lpt_cnext`, `dirty_nn_cnt`, `dirty_pn_cnt`, `lpt_drty_flgs`, `ltab[].free/dirty/tgc/cmt`, `ltab_cmt`, `lsave`, `nhead_lnum/off`, and root/ltab/lsave locations. Start commit is a planning/freeze phase; end commit is the physical write phase. Nodes obsolete because of COW are kept until after successful writing, then `free_obsolete_cnodes()` releases them.

## Dependencies and Integration Points
The file depends on packing functions from `lpt.c`, lazy node lookup helpers, UBI write/unmap operations, lprops locking, category state, cryptographic LPT hashing, and UBIFS commit orchestration in `commit.c`. `recovery.c` cleans the LPT head after failed commits, and `master.c` persists the new LPT root/head/table locations and hash.

## Risks and Test Signals
The main risks are divergence between `layout_cnodes()` and `write_cnodes()`, wrong `ltab` accounting, failure to clear COW after writes, LPT out-of-space loops, and GC mistaking current nodes for obsolete nodes. Useful tests include power-cut injection across start/end/post commit, forced small-LPT whole-tree rewrite, big-LPT GC with fragmented LPT area, random `lsave` debug population, corrupted LPT padding/CRC during debug scans, and memory-failure paths in obsolete-node cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ubifs/lpt_commit.c -->
