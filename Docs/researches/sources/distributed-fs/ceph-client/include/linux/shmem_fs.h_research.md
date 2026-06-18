# sources/distributed-fs/ceph-client/include/linux/shmem_fs.h

## Purpose

`shmem_fs.h` defines tmpfs/shmem internal inode and superblock data, mount quota limits, flags, helper accessors, and the exported API used by mm, VFS, userfaultfd, hugepage, swap, and file setup code.

## Important APIs, Types, And Functions

Important types are `struct shmem_inode_info`, `struct shmem_quota_limits`, `struct shmem_sb_info`, and `enum sgp_type`. `shmem_inode_info` embeds VFS inode state plus shmem-specific locks, seals, flags, allocated and swapped counters, directory offset context or shrink/swap lists, creation time, NUMA policy, xattrs, fallocate end, fs flags, stop-eviction counter, optional quotas, and the embedded `vfs_inode`. `shmem_sb_info` tracks max and used blocks, inode limits, free inode space, mount mode/uid/gid, hugepage policy, swap policy, inode allocation batches, memory policy, shrinklist, and quota defaults.

APIs include `SHMEM_I()`, `shmem_init()`, `shmem_init_fs_context()`, `shmem_file_setup()`, `shmem_kernel_file_setup()`, `shmem_file_setup_with_mnt()`, `shmem_zero_setup()`, `shmem_zero_setup_desc()`, `shmem_get_unmapped_area()`, `shmem_lock()`, `shmem_mapping()`, `shmem_unlock_mapping()`, `shmem_read_mapping_page_gfp()`, `shmem_writeout()`, `shmem_truncate_range()`, `shmem_unuse()`, `shmem_allowable_huge_orders()`, `shmem_hpage_pmd_enabled()`, `shmem_swap_usage()`, `shmem_uncharge()`, `shmem_partial_swap_usage()`, `shmem_get_folio()`, `shmem_read_folio_gfp()`, `shmem_read_folio()`, `shmem_read_mapping_page()`, `shmem_file()`, `shmem_freeze()`, `shmem_fallocend()`, and `shmem_charge()`.

## Control Flow

File setup APIs create anonymous or mounted shmem files. Page lookup/allocation flows through `shmem_get_folio()` with `SGP_READ`, `SGP_NOALLOC`, `SGP_CACHE`, `SGP_WRITE`, or `SGP_FALLOC`, controlling whether holes may allocate pages or exceed size. Swap and reclaim paths call writeout, unuse, swap usage, uncharge, and shrinklist helpers. Truncation and fallocate paths use `shmem_truncate_range()` and `shmem_fallocend()` to preserve required reservations. `shmem_freeze()` toggles a mapping-frozen flag under exclusive inode lock.

## State And Persistence

Persistent in-memory filesystem state is per-inode allocation, swap, seal, policy, xattr, quota, and shrink/swap list membership plus per-superblock accounting counters and policies. `SHMEM_F_NORESERVE`, `SHMEM_F_LOCKED`, and `SHMEM_F_MAPPING_FROZEN` modify allocation, swap, and mapping mutability behavior. Quota limits use signed 64-bit safe maxima despite byte counters being unsigned.

## Dependencies And Integration Points

Dependencies include VFS files and inodes, swap, NUMA mempolicy, pagemap, percpu counters, xattrs, fs parser, userfaultfd, bits, tmpfs quota, transparent hugepage, and shmem config. Integration points include anonymous shared mappings, tmpfs mounts, memfd-like file setup, userfaultfd, THP, swapoff, reclaim, quotas, xattrs, and FS_IOC flags.

## Risks And Test Signals

Risks are accounting mismatches between `alloced`, `swapped`, quotas, and `used_blocks`; freeze flag changes without the inode lock; hugepage truncation around fallocate reservations; wrong behavior under `CONFIG_SHMEM` or `CONFIG_TRANSPARENT_HUGEPAGE` stubs; and quota overflow. Test signals include tmpfs xfstests, memfd and shared anonymous mmap, swapoff/shmem_unuse, THP tmpfs tests, userfaultfd minor faults, quota enforcement, fallocate hole punch/keep-size, and lockdep around inode freeze.
