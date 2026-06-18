# sources/distributed-fs/ceph-client/fs/hpfs/alloc.c

Purpose: this file manages HPFS free-space allocation, directory-band allocation, object initialization for dnodes/fnodes/anodes, and block discard trimming.

Important APIs and functions: `hpfs_alloc_sector()`, `hpfs_alloc_if_possible()`, and `hpfs_free_sectors()` manipulate main free-space bitmaps. `hpfs_alloc_dnode()`, `hpfs_alloc_fnode()`, and `hpfs_alloc_anode()` allocate and initialize core metadata objects. `hpfs_check_free_dnodes()` reserves safety for dnode splits/deletes. `hpfs_trim_fs()` scans free runs and issues discard. Internal `hpfs_claim_*` helpers maintain cached free counts unless corruption is detected.

Control flow: allocation searches near the requested sector, then outward across bitmap bands, using `alloc_in_bmp()` to find aligned free bit runs and clear bits. It adapts forward preallocation with `sb_max_fwd_alloc`. Dnodes prefer the directory band when enough free dnodes remain, otherwise they fall back to general sectors. Freeing sets bitmap bits back to free, crossing bitmap boundaries as needed. Trim separately scans the directory-band bitmap and main bitmaps, under `hpfs_lock()`, and calls `sb_issue_discard()` for free runs meeting limits.

State and persistence: bitmap bits are persistent metadata; dirtying quad buffers commits allocation/free state. Superblock cached counts `sb_n_free`, `sb_n_free_dnodes`, `sb_c_bitmap`, and `sb_max_fwd_alloc` are updated in memory. Newly allocated metadata sectors are zeroed and initialized with magic values and default headers.

Dependencies and integration: it depends on `map.c` bitmap mappers, `buffer.c` quad-buffer dirtying, `hpfs_error()`, and structure definitions from `hpfs.h`. File growth, directory mutation, EA growth, and object creation all call into this allocator.

Risks: HPFS uses inverted bitmap semantics where `1` means free and `0` means allocated. Corruption checks are optional through `sb_chk`; without them, invalid bitmap state can propagate. Dnode operations rely on `hpfs_check_free_dnodes()` to avoid mid-split ENOSPC corruption. Preallocation failure after main allocation logs an error and may leave earlier sectors allocated.

Test signals: allocate/free single sectors and four-sector dnodes, stress bitmap-boundary crossing, directory-band exhaustion, ENOSPC during dnode split, free-count underflow/overflow detection, trim ranges overlapping the directory band, readonly trim rejection, and fatal signal interruption during discard.
