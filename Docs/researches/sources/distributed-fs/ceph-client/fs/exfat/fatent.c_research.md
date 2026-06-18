# sources/distributed-fs/ceph-client/fs/exfat/fatent.c

## Purpose
`fatent.c` implements FAT entry I/O, FAT mirroring, FAT-chain construction, cluster allocation/freeing, cluster-chain counting, cluster zeroing, and block readahead helpers. Together with `balloc.c`, it maintains exFAT's persistent allocation state: bitmap bits identify allocated clusters, and FAT entries link clusters when a file is not represented as a contiguous no-FAT chain.

## Important APIs, types, and functions
FAT entry primitives are `exfat_ent_get()`, `exfat_ent_set()`, internal `__exfat_ent_get()`, `__exfat_ent_set()`, `exfat_end_bh()`, and `exfat_mirror_bh()`. Readahead and chain helpers include `exfat_blk_readahead()`, `exfat_chain_cont_cluster()`, `exfat_find_last_cluster()`, and `exfat_count_num_clusters()`.

Cluster lifecycle APIs are `exfat_alloc_cluster()`, `exfat_free_cluster()`, internal `__exfat_free_cluster()`, `exfat_zeroed_cluster()`, and `exfat_discard_cluster()`. They call bitmap helpers and, when needed, FAT setters.

## Control flow
`exfat_ent_get()` validates the requested cluster, reads or reuses the proper FAT sector buffer, remaps reserved values above bad-cluster to EOF, rejects free/bad/out-of-range content, and leaves the buffer cached for the caller to release. `exfat_ent_set()` writes one FAT entry and mirrors the containing sector to FAT2 when present.

`exfat_alloc_cluster()` runs under `bitmap_lock`. It verifies free-space accounting, chooses a hint cluster from the caller or `sbi->clu_srch_ptr`, finds free bitmap bits, sets bitmap bits, initializes FAT entries when the chain uses FAT, links from the prior cluster, and increments `p_chain->size`. If contiguous allocation breaks while the caller wanted `ALLOC_NO_FAT_CHAIN`, it materializes the previous contiguous run with `exfat_chain_cont_cluster()` and switches to `ALLOC_FAT_CHAIN`. On failure it frees the partially allocated chain.

`__exfat_free_cluster()` clears bitmap bits for either a no-FAT contiguous range or a FAT-linked chain, optionally issues discard for contiguous physical runs, detects possible chain loops by bounding traversal, and decrements `used_clusters`. Truncate and rmdir paths call it through `exfat_free_cluster()`. `exfat_zeroed_cluster()` obtains each buffer in a cluster, zeroes it, marks it dirty, and synchronizes a blockdev range for synchronous directories.

## State and persistence behavior
Persistent state modified here includes FAT1/FAT2 sectors and allocation bitmap bits; discard informs lower storage but does not change exFAT metadata. Runtime state updated includes `sbi->used_clusters`, `sbi->clu_srch_ptr`, chain descriptors passed by callers, and the `discard` mount option when the device reports unsupported discard. FAT writes are buffer-head dirty writes, optionally synchronous through `exfat_update_bh()`.

## Dependencies and integration points
This file depends on bitmap operations, buffer-head block I/O, block discard, cluster geometry macros, mount options, and sync helpers. It is called by inode block mapping, file expansion/truncate, directory growth, mkdir/rmdir, rename replacement cleanup, and directory allocation.

## Risks and test signals
Risks include bitmap/FAT ordering inconsistency, failure rollback leaks, FAT2 mirroring errors, looped chain traversal, incorrect conversion from contiguous to FAT chains, stale `used_clusters`, discard of allocated clusters, and synchronous write failures. Tests should cover fragmented and contiguous allocation, ENOSPC rollback, FAT2 images, discard-supported and unsupported devices, cluster zeroing for directories, corrupt FAT loops, truncate after allocation failure, full-volume wraparound allocation, and power-fail ordering with fsck validation.
