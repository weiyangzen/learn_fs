# sources/distributed-fs/ceph-client/fs/hpfs/anode.c

Purpose: this file implements HPFS allocation B+ trees stored in fnodes and anodes. These trees map file-relative sectors or EA-relative sectors to disk sectors and support extension, truncation, and removal.

Important APIs and functions: `hpfs_bplus_lookup()` maps a logical sector through internal and leaf nodes. `hpfs_add_sector_to_btree()` extends an allocation tree and splits full nodes. `hpfs_remove_btree()` frees every data extent and anode in a tree. `hpfs_ea_read()`, `hpfs_ea_write()`, and `hpfs_ea_remove()` reuse the same mapping logic for external EA storage. `hpfs_truncate_btree()` releases sectors beyond a new length. `hpfs_remove_fnode()` removes file/directory content, EAs, and the fnode itself.

Control flow: lookup descends internal nodes by comparing `file_secno`, then scans leaf extents for the requested sector, optionally caching the found run in `hpfs_inode_info`. Adding first tries to extend the last physical extent contiguously; otherwise it allocates a sector, inserts a new leaf entry, and recursively splits/promotes anodes if no free entries remain. Removal and truncation are iterative to avoid stack overflow and use up pointers to walk back up the tree.

State and persistence: this code mutates B+ tree headers, extent arrays, anode parent pointers, fnode root trees, and bitmap allocation state. Buffers are marked dirty after structural changes. Removing fnodes also frees directory dtrees or file data trees and indirect EAs.

Dependencies and integration: it depends on `alloc.c` for sectors/anodes, `map.c` for fnodes/anodes, `buffer.c`, and corruption-cycle detection through `hpfs_stop_cycles()`. `file.c`, `ea.c`, `inode.c`, and `namei.c` call these helpers for data and metadata lifecycle.

Risks: tree splitting is intricate and must keep `first_free`, used/free counts, `BP_internal`, `BP_fnode_parent`, and `up` pointers consistent. Several failure exits after partial allocation rely on freeing temporary sectors/anodes correctly. Truncation intentionally does not join anodes, which can leave sparse tree shape but should remain valid.

Test signals: grow files through contiguous and fragmented extents, force fnode-to-anode and anode-to-root splits, lookup after splits, truncate to zero and middle of extents, remove fragmented files, remove directories through `hpfs_remove_fnode()`, test EA reads/writes through direct and anode-backed storage, and run with strict checks to catch cycle/up-pointer errors.
