<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hugetlbfs/inode.c -->
# sources/distributed-fs/ceph-client/fs/hugetlbfs/inode.c

## Purpose

`sources/distributed-fs/ceph-client/fs/hugetlbfs/inode.c` implements the hugetlbfs pseudo-filesystem: a VFS filesystem whose regular-file data is backed by hugetlb folios and hugetlb reservation accounting rather than normal page-cache writeback. It provides mount parsing, superblock construction, inode allocation with optional inode limits, file creation, mmap preparation, read support, fallocate and hole punching, truncate/eviction, internal mounts for SysV/shared hugepage files, and filesystem registration.

## Important APIs, Types, and Functions

Important private state includes `struct hugetlbfs_fs_context` for parsed mount options, `struct hugetlbfs_sb_info` from hugetlb headers for superblock limits and subpool state, and `struct hugetlbfs_inode_info` for per-inode reservation maps and seals. Mount options include `uid=`, `gid=`, `mode=`, `size=`, `min_size=`, `nr_inodes=`, and `pagesize=`.

Core VFS objects are `hugetlbfs_fs_type`, `hugetlbfs_ops`, `hugetlbfs_file_operations`, `hugetlbfs_dir_inode_operations`, `hugetlbfs_inode_operations`, and `hugetlbfs_aops`. Key functions include `hugetlbfs_init_fs_context()`, `hugetlbfs_parse_param()`, `hugetlbfs_validate()`, `hugetlbfs_fill_super()`, `hugetlbfs_get_tree()`, `hugetlbfs_get_inode()`, `hugetlbfs_read_iter()`, `hugetlbfs_file_mmap_prepare()`, `hugetlb_get_unmapped_area()`, `hugetlbfs_fallocate()`, `hugetlbfs_punch_hole()`, `hugetlb_vmtruncate()`, `remove_inode_hugepages()`, `hugetlbfs_evict_inode()`, `hugetlb_file_setup()`, `mount_one_hugetlbfs()`, and `init_hugetlbfs_fs()`.

## Control Flow

Mounting starts by allocating `struct hugetlbfs_fs_context` with defaults for current fsuid/fsgid, mode `0755`, unlimited size/inodes, default hstate, and no minimum pool size. Parse callbacks convert size strings or percentages to pending options and map `pagesize=` to an hstate. `hugetlbfs_get_tree()` validates min/max hugepage counts and calls `get_tree_nodev()`. `hugetlbfs_fill_super()` allocates `sbinfo`, initializes inode counters and optional `hugepage_subpool`, fills VFS superblock fields, sets `DCACHE_DONTCACHE`, creates a root directory inode, and installs it as the root dentry.

File and directory creation flow through `hugetlbfs_get_inode()`, which allocates a reserve map for regular files and symlinks, initializes owner/mode through idmapped mount helpers, assigns address-space operations, sets initial seals, and selects file, directory, symlink, or special inode operations. Directory operations are mostly simplefs operations with hugetlbfs-specific create, mkdir, mknod, symlink, tmpfile, and setattr hooks.

`hugetlbfs_file_mmap_prepare()` validates hugepage-aligned offsets and overflow, reserves pages over the requested hstate range, grows `i_size` for writable mappings, installs hugetlb VM operations, and arranges delayed VMA-lock allocation so rmap cannot observe the VMA before its hugetlb lock exists. `hugetlb_get_unmapped_area()` aligns non-fixed address hints and rejects unaligned length or fixed address.

Read support walks hugepage indexes from `ki_pos`, returns zeroes for holes, copies present huge folios to the iterator, and treats raw-hwpoison subpages as short readable ranges or `-EIO`. There is no normal buffered write path; `write_begin` rejects and `write_end` is a BUG fallback.

Truncate, hole punch, and eviction remove huge folios from page cache and reservations. `hugetlb_vmtruncate()` shrinks `i_size`, unmaps VMAs, and removes pages after the new EOF. `hugetlbfs_punch_hole()` zeroes partial hugepages at the edges, unmaps and removes fully covered hugepages, and checks write seals. `hugetlbfs_fallocate()` either delegates to punch-hole or preallocates huge folios one hstate index at a time through a pseudo VMA, reservation-aware allocation, zeroing, and page-cache insertion.

Boot-time initialization creates the inode slab, registers hugetlbfs, mounts an internal hugetlbfs instance for the default hstate, and best-effort mounts internal instances for other hstates. `hugetlb_file_setup()` uses those internal mounts to create pseudo regular files for shared hugetlb mappings after checking hstate availability and SHM_HUGETLB privilege.

## State and Persistence Behavior

hugetlbfs has no disk persistence. File contents and metadata exist in memory, backed by hugetlb folios and reservation/subpool accounting. Superblock state records hstate, uid/gid/mode, inode counters, and optional subpool with maximum/minimum hugepage limits. Inode state records reserve maps, file seals, `i_size`, ownership, mode, timestamps, and mapping state.

Persistent-looking operations are runtime accounting updates: reserving pages during mmap or `hugetlb_file_setup()`, consuming reservations during fallocate, removing page-cache folios, unreserving pages during truncate/hole punch/eviction, and adjusting subpool/free-inode counters. Eviction releases the reserve map for regular and symlink inodes and clears the inode.

The file also stores global state: `sysctl_hugetlb_shm_group`, the hugetlbfs inode kmem cache, and `hugetlbfs_vfsmount[]` for each hstate internal mount.

## Dependencies and Integration Points

This file is tightly integrated with the hugetlb MM subsystem: hstates, reservation maps, hugepage subpools, hugetlb fault mutexes, VMA locks, huge PTE walking, hugepage allocation, migration, and hugetlb tracepoints. It uses VFS fs-context, nodev mounts, idmapped mounts, simple directory operations, page symlink support, inode attributes, `statfs`, Linux security/capability helpers, `user_shm_lock()`, and internal long-term kernel mounts.

The mmap path integrates with `vm_area_desc`, `hugetlb_vm_ops`, rmap visibility, and per-VMA hugetlb locks. Internal shared memory users enter through exported `hugetlb_file_setup()`.

## Risks and Edge Cases

Reservation accounting is the highest-risk area. Truncation and hole punching must coordinate page-cache deletion, VMA unmapping, hugetlb fault mutexes, reserve-map updates, and subpool/global counts; the code explicitly handles races with faults by rechecking mapped folios and using hugetlb fault locks. OOM during unreserve can require reserve-count repair.

Alignment and overflow checks are critical because offsets are translated between base-page units, hugepage units, and byte offsets. `PGOFF_LOFFT_MAX`, hugepage-mask tests, and `len < vma_len` checks prevent signed `loff_t` overflow. Fallocate loops can be interrupted and must release fault mutexes and folio references on every exit.

Seals are enforced for shrink, grow, write, and future-write cases in setattr and punch-hole paths. The code deliberately sets high stack depth because hugetlbfs is unsuitable as a stacking filesystem. Internal hstate mounts are required for `hugetlb_file_setup()`; missing non-default hstates return `-ENOENT`.

## Test Signals

Coverage should include mounting with byte and percentage `size=`/`min_size=`, invalid `pagesize=`, min greater than max, inode-limit exhaustion, idmapped create ownership, root mode/uid/gid display in `/proc/mounts`, statfs subpool accounting, read holes returning zeroes, hwpoison read failures, aligned and unaligned mmap offsets, MAP_FIXED alignment rejection, writable mmap size growth, truncate alignment rejection, seals blocking grow/shrink/punch, fallocate preallocation and interrupt behavior, hole punching edge partial-zeroing, eviction unreserving all pages, and SysV SHM_HUGETLB privilege checks.

Useful runtime signals include hugetlbfs tracepoints for allocation, free, eviction, fallocate, and setattr, plus global/subpool hugepage counters before and after mmap, fallocate, truncate, and unmount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/hugetlbfs/inode.c -->
