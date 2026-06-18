# Group Research: group_1257_netbsd_src_sources_os_bsd_netbsd_src_sys_fs_v7fs_v7fs_datablock_c_s_ec36b866ef53

Scope: `Docs/research_subset_a.md`, NetBSD source tree files under `sources/os/bsd/netbsd-src`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_datablock.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_datablock.c

## Purpose
Implements V7FS data block allocation, deallocation, file block tree growth/shrink, logical-to-physical block lookup, and iteration over file payload blocks.

## Main Interfaces
- `datablock_number_sanity()` validates data-sector numbers against the mounted superblock.
- `v7fs_datablock_allocate()` pops from the superblock free-block cache, refreshes chained free-block lists with `v7fs_freeblock_update()`, zeroes the selected block, and returns `ENOSPC`/`EIO` on failure.
- `v7fs_datablock_foreach()` walks direct, single, double, and triple indirect block references and calls a callback with each block and payload size.
- `v7fs_datablock_last()` maps a file offset to the backing block using `v7fs_datablock_addr()` and indirect-link readers.
- `v7fs_datablock_expand()`, `v7fs_datablock_contract()`, and `v7fs_datablock_size_change()` maintain inode size and block/index allocation.

## Implementation Notes
The file models classic V7 addressing: direct entries plus single/double/triple indirect blocks. Indirect block contents are sector addresses converted with `V7FS_VAL32()`. Freeing an indirect level unlinks child entries before returning data/index blocks to the free list. Metadata changes are written immediately through `v7fs_inode_writeback()` and `fs->io.write()`.

## Dependencies
Uses `v7fs_superblock` free-block state, scratch buffers from `v7fs_io.c`, endian helpers, inode writeback, and the block I/O callback table in `struct v7fs_self`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_datablock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_datablock.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_datablock.h

## Purpose
Declares the V7FS data-block allocator, iterator, size-changing helpers, and logical block-address map type.

## Main Interfaces
- `v7fs_datablock_allocate()`, `v7fs_datablock_expand()`, `v7fs_datablock_contract()`, and `v7fs_datablock_size_change()` are the mutation API used by file and vnode operations.
- `v7fs_datablock_foreach()` provides a callback iterator for directory scans and file operations.
- `v7fs_datablock_last()` and `v7fs_datablock_addr()` expose block mapping.
- `struct v7fs_daddr_map` stores indirect level and up to three indexes.

## Dependencies
Consumers must provide `struct v7fs_self`, `struct v7fs_inode`, and V7FS address/offset typedefs from the core headers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_datablock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_dirent.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_dirent.c

## Purpose
Provides directory-entry endian conversion and filename normalization for V7FS directory records.

## Main Interfaces
- `v7fs_dirent_endian_convert()` converts `inode_number` fields in an array of `struct v7fs_dirent` from on-disk order and checks inode-number sanity.
- `v7fs_dirent_filename()` truncates and NUL-pads names to `V7FS_NAME_MAX + 1` for stable comparisons.

## Implementation Notes
Directory names are fixed-width V7 names; lookups compare the normalized buffer with `strncmp(..., V7FS_NAME_MAX)`. The conversion function returns `false` if it sees invalid inode numbers, while still writing converted inode numbers into the records.

## Dependencies
Depends on superblock inode bounds via `v7fs_inode_number_sanity()` and endian macros from `v7fs_endian.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_dirent.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_dirent.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_dirent.h

## Purpose
Declares directory-entry utilities used by lookup, readdir, rename, and directory mutation code.

## Main Interfaces
- `v7fs_dirent_endian_convert()` for batch conversion and validation of directory entries.
- `v7fs_dirent_filename()` for fixed-length V7 filename normalization.

## Dependencies
Requires V7FS directory-entry definitions and `struct v7fs_self` from the surrounding V7FS headers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_dirent.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_endian.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_endian.c

## Purpose
Implements V7FS endian conversion, including the 24-bit disk block address packing used by V7 inodes.

## Main Interfaces
- `v7fs_endian_init()` installs per-mount conversion callbacks when `V7FS_EI` is enabled.
- `val24_normal_order_read()` and `val24_normal_order_write()` always provide native-order 24-bit address packing/unpacking.

## Implementation Notes
The optional endian-independent path supports little, big, and PDP endian modes. PDP conversion is handled specially for 32-bit values and 24-bit addresses. Without `V7FS_EI`, the macros in the header are pass-through except for normal 24-bit helpers.

## Dependencies
Uses `<sys/endian.h>`, mount-level `fs->endian`, and callback storage in `struct endian_conversion_ops`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_endian.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_endian.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_endian.h

## Purpose
Defines the V7FS value-conversion macros used by superblock, inode, directory, and free-list code.

## Main Interfaces
- `V7FS_VAL32`, `V7FS_VAL16`, `V7FS_VAL24_READ`, and `V7FS_VAL24_WRITE` abstract disk/native conversion.
- `v7fs_endian_init()` is declared only for `V7FS_EI` builds.
- `val24_normal_order_read()` and `val24_normal_order_write()` are available in all builds.

## Dependencies
The `V7FS_EI` mode requires conversion callbacks in `struct v7fs_self`; the default mode assumes native on-disk order.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_endian.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_extern.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_extern.c

## Purpose
Registers V7FS with NetBSD as a VFS module and defines vnode operation vectors for regular, special, and FIFO nodes.

## Main Interfaces
- `v7fs_vnodeop_entries`, `v7fs_specop_entries`, and `v7fs_fifoop_entries` map VOP descriptors to V7FS, genfs, specfs, and fifofs handlers.
- `v7fs_vfsops` exposes mount, unmount, sync, vnode loading, statvfs, and root-mount entry points.
- `v7fs_genfsops` integrates the file system with genfs page-cache operations.
- `v7fs_modcmd()` attaches/detaches the file system module.

## Implementation Notes
Most unsupported operations use genfs error/default helpers. Device and FIFO vnodes share V7FS metadata operations but use spec/fifo read/write behavior.

## Dependencies
Depends on vnode/VFS declarations in `v7fs_extern.h`, genfs, specfs, fifofs, module infrastructure, and V7FS vnode/VFS operation implementations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_extern.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_extern.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_extern.h

## Purpose
Defines the NetBSD-facing V7FS mount/node wrappers and declares VFS/VOP entry points.

## Main Interfaces
- `struct v7fs_mount` connects a NetBSD mount and device vnode to the core `struct v7fs_self`.
- `struct v7fs_node` embeds `genfs_node`, stores the V7FS inode, vnode back-pointer, advisory-lock state, and deferred timestamp flags.
- `VFSTOV7FS()` casts `mnt_data`.
- Declares vnode operations, VFS prototypes, operation vector pointers, genfs hooks, and `v7fs_update()`.

## Dependencies
Includes V7FS on-disk/core headers plus genfs and specfs declarations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_extern.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_file.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_file.c

## Purpose
Implements core file and directory entry operations: lookup by name, inode creation, unlink/deallocation, directory-entry append, and directory-entry removal.

## Main Interfaces
- `v7fs_file_lookup_by_name()` scans a parent directory with `v7fs_datablock_foreach()`.
- `v7fs_file_allocate()` allocates an inode, initializes attributes/type-specific state, creates `.` and `..` for directories, writes the inode, and links it into the parent directory.
- `v7fs_file_deallocate()` removes a name, decrements/removes inode links, enforces empty-directory rules, and shrinks directory data.
- `v7fs_directory_add_entry()` expands a directory and writes the new fixed-size dirent at the end.
- `v7fs_directory_remove_entry()` replaces the removed entry with the last dirent, then contracts the directory.

## Implementation Notes
Directory deletion requires exactly `.` and `..` to remain. Special device files store the device number in `inode.device` and `addr[0]`. Directory entry mutation uses disk-endian inode values where appropriate.

## Dependencies
Uses inode allocation/load/writeback, datablock expansion/contraction, dirent normalization/conversion, scratch buffers, and the mount I/O callbacks.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_file.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_file.h

## Purpose
Declares core and utility-level V7FS file/directory operations.

## Main Interfaces
- `struct v7fs_lookup_arg` is the shared callback context for name lookup, inode-number lookup, replacement, and removal.
- Declares allocation/deallocation, directory add/remove, rename, replacement, link, lookup-by-number, and symlink helpers.

## Dependencies
Requires `struct v7fs_self`, `struct v7fs_inode`, `struct v7fs_fileattr`, and V7FS inode/address typedefs from core headers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_file.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_file_util.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_file_util.c

## Purpose
Provides higher-level file utilities for hard links, symbolic links, rename, directory-entry replacement, lookup by inode number, and directory-move validation.

## Main Interfaces
- `v7fs_file_link()` adds a directory entry and increments the target inode link count.
- `v7fs_file_symlink()` stores the symlink target in a single allocated data block.
- `v7fs_file_rename()` handles replacement of existing targets, adds the destination entry, removes the source entry, and updates `..` when moving directories between parents.
- `v7fs_directory_replace_entry()` changes an existing dirent inode number.
- `v7fs_file_lookup_by_number()` finds a name for an inode in a parent directory.

## Implementation Notes
`can_dirmove()` walks destination parents via `..` to prevent moving a directory into its own descendant. Symlink targets are limited to the V7/2BSD maximum and include a trailing NUL.

## Dependencies
Uses `v7fs_datablock_foreach()`, dirent conversion, core directory add/remove, inode load/writeback, and scratch I/O.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_file_util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_impl.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_impl.h

## Purpose
Defines V7FS implementation-private runtime structures, I/O callbacks, locking hooks, scratch buffers, mount-device inputs, stats, and iterator sentinel codes.

## Main Interfaces
- `struct block_io_ops` abstracts read/write of one or more disk sectors.
- `struct v7fs_self` is the core per-mount state: scratch buffers, I/O ops, optional endian ops, optional locks, superblock, stats, and endian selection.
- `struct v7fs_fileattr` carries create-time uid/gid/mode/device/timestamps.
- `SUPERB_LOCK`, `ILIST_LOCK`, and `MEM_LOCK` map to lock callbacks in kernel builds and no-ops otherwise.
- Declares `v7fs_io_init()`, `v7fs_io_fini()`, `scratch_read()`, `scratch_free()`, and `scratch_remain()`.

## Dependencies
Bridges kernel and userland builds with conditional locking, assertions, and scratch-buffer allocation policy.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_inode.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_inode.c

## Purpose
Implements V7FS inode allocation/freeing, inode disk-location calculation, and conversion between memory and on-disk inode images.

## Main Interfaces
- `v7fs_inode_number_sanity()` validates inode numbers against the superblock-derived inode count.
- `v7fs_inode_allocate()` draws from the superblock free-inode cache, refreshing it with `v7fs_freeinode_update()` as needed.
- `v7fs_inode_deallocate()` zeroes the inode on disk and returns its number to the free-inode accounting/cache.
- `v7fs_inode_load()` and `v7fs_inode_writeback()` read/write a single inode through the ilist sector area.
- `v7fs_inode_setup_memory_image()` expands disk fields, including 24-bit addresses, into `struct v7fs_inode`.

## Implementation Notes
Inode numbers start at 1. Disk location is computed from `(ino - 1) * sizeof(struct v7fs_inode_diskimage)` relative to `V7FS_ILIST_SECTOR`. Character/block device inodes copy `addr[0]` into `device`.

## Dependencies
Uses superblock free-inode state, endian macros, scratch buffers, ilist locks, and V7FS on-disk inode layout.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_inode.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_inode.h

## Purpose
Defines the in-memory V7FS inode and declares inode allocation, disk I/O, validation, utility, and ilist iteration functions.

## Main Interfaces
- `struct v7fs_inode` stores inode number, mode/link/owner/time attributes, append flag, special-device number, file size, and V7 address array.
- Macros classify V7 original, 2BSD extension, and NetBSD FIFO inode types.
- Declares allocate/deallocate, load/writeback, disk-to-memory conversion, `v7fs_inode_chmod()`, `v7fs_inode_dump()`, and `v7fs_ilist_foreach()`.

## Dependencies
Requires V7FS mode constants, address counts, and on-disk inode structures from `v7fs.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_inode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_inode_util.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_inode_util.c

## Purpose
Provides inode utility routines for chmod, diagnostic dumping, and walking every inode in the ilist.

## Main Interfaces
- `v7fs_inode_chmod()` replaces only permission bits while preserving file type bits.
- `v7fs_inode_dump()` prints inode metadata and special-device major/minor information.
- `v7fs_ilist_foreach()` reads every ilist sector, converts each disk inode to memory form, and invokes a callback.

## Dependencies
Uses scratch I/O, `v7fs_inode_setup_memory_image()`, superblock ilist bounds, and optional userland time formatting.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_inode_util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_io.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_io.c

## Purpose
Implements scratch-buffer read/free support shared by kernel and userland V7FS core code.

## Main Interfaces
- `scratch_read()` reads a block into either one of the static per-mount scratch buffers in kernel builds or a newly allocated userland buffer.
- `scratch_free()` releases the selected scratch slot or frees the userland buffer.
- `scratch_remain()` reports remaining static scratch buffers in kernel builds.

## Implementation Notes
Kernel builds use `STATIC_BUFFER` and `MEM_LOCK()` to manage three fixed scratch blocks. Userland builds allocate one `V7FS_BSIZE` buffer per read. Scratch exhaustion asserts in kernel mode.

## Dependencies
Depends on `struct v7fs_self`, the block I/O `read` callback, and lock macros from `v7fs_impl.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_io_kern.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_io_kern.c

## Purpose
Provides the kernel implementation of V7FS block I/O initialization, teardown, sector read/write, and mutex-backed lock callbacks.

## Main Interfaces
- `v7fs_io_init()` allocates `struct v7fs_self`, initializes endian conversion, I/O callbacks, local vnode/credential state, scratch state, and lock callbacks.
- `v7fs_io_fini()` frees local I/O state and destroys allocated mutexes.
- `v7fs_os_read()`/`v7fs_os_write()` use `bread()`, `getblk()`, and `bwrite()` for device-vnode sector I/O.
- `v7fs_os_read_n()`/`v7fs_os_write_n()` loop one sector at a time.

## Dependencies
Uses NetBSD vnode/buf/kmem/mutex APIs, `struct v7fs_mount_device`, and optional endian initialization.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_io_kern.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_io_user.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_io_user.c

## Purpose
Provides the userland V7FS block I/O implementation for tools/tests using file descriptors.

## Main Interfaces
- `v7fs_io_init()` allocates `struct v7fs_self`, stores fd/block-size/size state, initializes endian conversion, and chooses mmap or lseek/read/write callbacks.
- `v7fs_io_fini()` unmaps, fsyncs, and frees the V7FS runtime.
- `read_sector()`/`write_sector()` perform positioned fd I/O.
- `read_mmap()`/`write_mmap()` copy to/from the mapped device image.

## Implementation Notes
The attempted mmap uses `MAP_SHARED` and falls back to sector I/O on failure. A single static `local` I/O state is used.

## Dependencies
Uses POSIX file, mmap, fsync, and warning APIs plus V7FS endian/core headers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_io_user.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_superblock.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_superblock.c

## Purpose
Implements V7FS superblock load/writeback, free-block cache refill, free-inode cache scan, and superblock/free-list endian conversion.

## Main Interfaces
- `v7fs_superblock_load()` reads sector `V7FS_SUPERBLOCK_SECTOR`, converts it, and validates core invariants.
- `v7fs_superblock_writeback()` writes modified in-memory superblock state back to disk.
- `v7fs_freeblock_update()` reads a chained free-block table and installs it into the in-memory superblock cache.
- `v7fs_freeblock_endian_convert()` converts and validates free-block table counts.
- `v7fs_freeinode_update()` scans the ilist for unallocated inodes and fills the free-inode cache.

## Implementation Notes
Sanity checks reject too-small volumes, invalid data starts, oversized free caches, impossible free counts, and unreadable final sectors. Free-inode scanning uses the on-disk inode `mode` field as the allocation test.

## Dependencies
Uses scratch I/O, endian helpers, inode helpers, datablock sanity, and `struct v7fs_superblock`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_superblock.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_superblock.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_superblock.h

## Purpose
Declares V7FS superblock core and utility routines.

## Main Interfaces
- Core declarations cover load, writeback, free-block update/conversion, and free-inode cache refill.
- Utility declarations cover status computation and debug dumping.

## Dependencies
Requires `struct v7fs_self`, `struct v7fs_freeblock`, and V7FS on-disk constants from core headers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_superblock.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_superblock_util.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_superblock_util.c

## Purpose
Provides status/statistics calculation and diagnostic superblock dumping.

## Main Interfaces
- `v7fs_superblock_status()` populates `fs->stat` with total/free block and inode counts plus total file count.
- `v7fs_superblock_dump()` prints key superblock fields and, in userland, the update time as text.

## Dependencies
Uses `V7FS_MAX_INODE()`, `struct v7fs_superblock`, `struct v7fs_stat`, and debug printing macros.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_superblock_util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_vfsops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_vfsops.c

## Purpose
Implements NetBSD VFS operations for mounting, unmounting, syncing, statvfs, vnode loading, root lookup, module lifecycle, and root-file-system mounting.

## Main Interfaces
- `v7fs_mount()` validates mount arguments/device vnode, authorizes access, opens the block device, and calls `v7fs_mountfs()`.
- `v7fs_mountfs()` allocates `struct v7fs_mount`, initializes core I/O, loads the superblock, and fills mount metadata.
- `v7fs_unmount()` flushes vnodes, closes the device, tears down V7FS core state, and clears mount data.
- `v7fs_sync()` writes the superblock and fsyncs allocated live vnodes selected by `v7fs_sync_selector()`.
- `v7fs_loadvnode()` loads a V7 inode into a pooled `struct v7fs_node`, initializes genfs state, sets vnode type/op vector, and handles special/FIFO nodes.
- `v7fs_vget()`, `v7fs_root()`, `v7fs_statvfs()`, `v7fs_init()`, `v7fs_done()`, and `v7fs_mountroot()` provide standard VFS integration.

## Implementation Notes
`v7fs_mode_to_vtype()` maps V7 mode bits to vnode types. File handles are not implemented (`EOPNOTSUPP`). Root mounting verifies the disk wedge type is `DKW_PTYPE_V7`.

## Dependencies
Uses NetBSD mount, vnode cache, genfs, specfs, pools, authorization, disk wedge, and V7FS core I/O/superblock/inode code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_vfsops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_vnops.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_vnops.c

## Purpose
Implements NetBSD vnode operations for V7FS files, directories, symlinks, special nodes, metadata changes, page-cache I/O, directory reads, block mapping, locking, and reclamation.

## Main Interfaces
- Name operations: `v7fs_lookup()`, `v7fs_create()`, `v7fs_mknod()`, `v7fs_remove()`, `v7fs_link()`, `v7fs_rename()`, `v7fs_mkdir()`, and `v7fs_rmdir()`.
- Data operations: `v7fs_read()`, `v7fs_write()`, `v7fs_fsync()`, `v7fs_bmap()`, and `v7fs_strategy()`.
- Metadata operations: `v7fs_access()`, `v7fs_getattr()`, `v7fs_setattr()`, `v7fs_update()`, `v7fs_pathconf()`, and `v7fs_advlock()`.
- Directory/symlink operations: `v7fs_readdir()`, `v7fs_symlink()`, and `v7fs_readlink()`.
- Lifecycle operations: `v7fs_open()`, `v7fs_close()`, `v7fs_inactive()`, `v7fs_reclaim()`, and `v7fs_print()`.

## Implementation Notes
The vnode layer uses the core file helpers for namespace mutations and `uvm_vnp_setsize()` to keep vnode size synchronized with inode size. Reads/writes use `ubc_uiomove()` through the unified buffer cache. `v7fs_reclaim()` frees blocks and deallocates the inode when link count reaches zero. `v7fs_readdir()` synthesizes NetBSD `struct dirent` records from fixed V7 dirents and inode type lookup.

## Dependencies
Uses NetBSD VOP argument structures, genfs/UBC/buf/lockf/kauth APIs, and nearly all V7FS core helpers: file, dirent, inode, datablock, and mount structures.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/v7fs/v7fs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/Make.tags.inc -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/Make.tags.inc

## Purpose
Provides common make logic for generating kernel source tags across architecture builds.

## Main Interfaces
- Under `.ifmake tags`, defines `SYSDIR`, `FINDCOMM`, and `COMM`.
- `FINDCOMM` finds common `*.[ch]` files while pruning architecture and selected generated/vendor/problematic directories/files.

## Implementation Notes
The comment explains common files are placed near the end so function tags win over struct tags with the same name.

## Dependencies
Included by architecture-specific kernel tag makefiles and relies on BSD make conditionals and shell `find`/`sort`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/Make.tags.inc -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/Makefile -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/Makefile

## Purpose
Top-level makefile for generated kernel files and tags-link maintenance under `sys/kern`.

## Main Interfaces
- Generates syscall outputs from `makesyscalls.sh`, `syscalls.conf`, and `syscalls.master`.
- Generates vnode interface files from `vnode_if.sh` and `vnode_if.src`.
- Builds a diagnostic `subr_vmem` helper target.
- `tags` recurses into selected architectures; `links` creates symlinks to the machine tags file.

## Implementation Notes
The default `all` target intentionally fails with guidance to invoke only supported maintenance targets.

## Dependencies
Uses BSD make, `${HOST_SH}`, tool variables, and `<bsd.files.mk>`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/bufq_disksort.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/bufq_disksort.c

## Purpose
Implements the traditional disk seek-sort buffer queue strategy as a loadable `MODULE_CLASS_BUFQ` module.

## Main Interfaces
- `BUFQ_DEFINE(disksort, 20, bufq_disksort_init)` registers strategy metadata.
- `bufq_disksort_put()` inserts buffers into a two-list ascending scan order using `buf_inorder()`.
- `bufq_disksort_get()` returns/removes the head request.
- `bufq_disksort_cancel()` removes a specific queued buffer.
- `bufq_disksort_init()`/`fini()` allocate and free private queue state.
- Module command registers/unregisters `bufq_strat_disksort`.

## Implementation Notes
The queue models a one-way scan: requests after the active position form the first sorted list, while requests already passed form the second sorted list.

## Dependencies
Uses `TAILQ`, `struct buf`, bufq framework hooks, kmem allocation, and module infrastructure.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/bufq_disksort.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/bufq_fcfs.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/bufq_fcfs.c

## Purpose
Implements a first-come, first-served buffer queue strategy.

## Main Interfaces
- `BUFQ_DEFINE(fcfs, 10, bufq_fcfs_init)` defines the strategy.
- `bufq_fcfs_put()` appends buffers to the tail with no reordering.
- `bufq_fcfs_get()` returns/removes the head.
- `bufq_fcfs_cancel()` removes a matching queued buffer.
- Init/fini set bufq callbacks and allocate/free private TAILQ state.

## Dependencies
Uses the NetBSD bufq framework, `struct buf`, `TAILQ`, kmem, and module registration.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/bufq_fcfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/bufq_priocscan.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/bufq_priocscan.c

## Purpose
Implements a priority-aware cyclical scan buffer queue strategy using red-black trees.

## Main Interfaces
- `BUFQ_DEFINE(priocscan, 40, bufq_priocscan_init)` registers the strategy.
- `cscan_put()` and `cscan_get()` maintain per-priority CSCAN ordered queues.
- `bufq_priocscan_selectqueue()` maps `BIO_GETPRIO()` classes to three priority queues.
- `bufq_priocscan_get()` chooses which priority queue to serve, enforcing burst limits when multiple queues are non-empty.
- `bufq_priocscan_cancel()` searches all priority queues and removes a matching buffer.

## Implementation Notes
Each priority queue has a CSCAN last-position key unless global-position mode is enabled. Burst defaults are 64, 16, and 4 requests for high, medium, and low priority, trading throughput and latency.

## Dependencies
Uses bufq, `struct buf`, `BIO_GETPRIO()`, `rb_tree`, kmem, and module registration.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/bufq_priocscan.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/bufq_readprio.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/bufq_readprio.c

## Purpose
Implements a read-priority buffer queue strategy with FCFS reads and sorted writes.

## Main Interfaces
- `BUFQ_DEFINE(readprio, 30, bufq_readprio_init)` registers the strategy.
- `bufq_prio_put()` appends reads to the read queue and inserts writes into a sorted write queue.
- `bufq_prio_get()` selects reads first, then serves a burst of writes after `PRIO_READ_BURST` reads when writes are pending.
- `bufq_prio_cancel()` removes a buffer from read or write queues and resets current selection.

## Implementation Notes
Reads are prioritized up to 48 consecutive requests; then 16 write requests may be served. `bq_write_next` tracks the rotating write position.

## Dependencies
Uses bufq infrastructure, `TAILQ`, buffer flags such as `B_READ`, `buf_inorder()`, kmem, and module registration.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/bufq_readprio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/cnmagic.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/cnmagic.c

## Purpose
Implements console magic-key sequence encoding/decoding as a compact state machine.

## Main Interfaces
- `cn_init_magic()` initializes a `cnm_state_t` to use the global magic table.
- `cn_destroy_magic()` clears the state.
- `cn_set_magic()` parses an escaped magic string into `cn_magic[]`.
- `cn_get_magic()` reconstructs the escaped magic string from the state table.

## Implementation Notes
State entries pack the expected character and next state with `ENCODE_STATE()`. The escape byte `0x27` represents literal escape, BREAK, and NUL encodings.

## Dependencies
Uses console magic constants/macros such as `CNS_LEN`, `CNC_BREAK`, `CNS_TERM`, `CNS_MAGIC_NEXT`, and `CNS_MAGIC_VAL` from kernel headers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/cnmagic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/compat_stub.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/compat_stub.c

## Purpose
Defines compatibility hook storage and default vectors used by optional or modular compatibility code throughout the kernel.

## Main Interfaces
- NTP vectors point to real NTP functions when `NTP` is built in, otherwise `NULL`.
- SCTP address hooks default to `NULL` and are later patched by network initialization.
- Many global hook structs are defined for USB, ccd, clockctl, crypto, raidframe, puffs, wscons, sysmon, bio, vnd, networking, tty, socket, modstat, proc32, coredump, and other compatibility paths.
- `kern_sig_43_pgid_mask` provides shared state for older signal compatibility.

## Implementation Notes
This file intentionally centralizes hook definitions to avoid link-time circular dependencies between base kernel and optional compat modules/rump components.

## Dependencies
Depends on `sys/compat_stub.h` hook type declarations and optional NTP headers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/compat_stub.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/core_elf32.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/core_elf32.c

## Purpose
Implements ELF32 core dump generation; also serves as the template included by `core_elf64.c` when `ELFSIZE` is 64.

## Main Interfaces
- `ELFNAMEEND(real_coredump)()` builds ELF headers, program headers, PT_NOTE contents, and writes process memory segments.
- `ELFNAMEEND(coredump_getseghdrs)()` converts UVM dump segments into `PT_LOAD` program headers and trims trailing zero pages where possible.
- `ELFNAMEEND(coredump_notes)()` gathers process, auxv, and per-LWP notes.
- `ELFNAMEEND(coredump_note)()` saves LWP status, integer registers, optional FP registers, and machine-dependent notes.
- `ELFNAMEEND(coredump_savenote)()` serializes aligned ELF notes into linked buffers.

## Implementation Notes
The dump takes three map passes conceptually: count segments, build headers, then write segment data. It uses module hooks for UVM map walking/counting and coredump I/O, allowing the generic core code to call implementation-specific writers.

## Dependencies
Uses ELF exec definitions, process/register/ptrace APIs, UVM coredump hooks, coredump module hooks, kauth credentials, and optional netbsd32 support.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/core_elf32.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/core_elf64.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/core_elf64.c

## Purpose
Instantiates the ELF core dump implementation for 64-bit ELF.

## Main Interfaces
- Defines `ELFSIZE 64`.
- Includes `core_elf32.c`, causing the shared ELF core implementation to compile with 64-bit ELF types and symbol names.

## Implementation Notes
This is a template-inclusion wrapper rather than an independent implementation.

## Dependencies
Depends entirely on `core_elf32.c` and ELF macro indirection in the NetBSD exec headers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/core_elf64.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/core_netbsd.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/core_netbsd.c

## Purpose
Implements the historic NetBSD native core file format.

## Main Interfaces
- `CORENAME(real_coredump_netbsd)()` fills the core header, invokes CPU-specific core dumping, writes the header, writes CPU state, and walks UVM mappings to write segments.
- `CORENAME(coredump_writesegs_netbsd)()` writes a `coreseg` header and corresponding user memory for each dump segment.

## Implementation Notes
The file is macro-parameterized with `CORENAME` and optional `COREINC`, allowing format variants. Segment flags distinguish stack from data with `CORE_STACK`/`CORE_DATA`.

## Dependencies
Uses `sys/core.h`, CPU coredump hooks, UVM coredump walk/count hooks, coredump write hooks, and process VM sizing fields.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/core_netbsd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/exec_aout.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/exec_aout.c

## Purpose
Implements NetBSD a.out executable format recognition and VM command setup.

## Main Interfaces
- `exec_aout_execsw` registers the executable switch entry for a.out binaries.
- `exec_aout_makecmds()` validates header size, checks native magic values, dispatches to ZMAGIC/NMAGIC/OMAGIC preparation, or calls a CPU hook.
- `exec_aout_prep_zmagic()` maps text/data from the vnode with demand paging and marks text busy.
- `exec_aout_prep_nmagic()` maps text/data with readvn commands and page-aligns data.
- `exec_aout_prep_omagic()` maps combined text/data writable/executable and adjusts data size for `obreak(2)` expectations.
- Module command adds/removes the exec switch entry.

## Dependencies
Uses exec package/vmcmd infrastructure, a.out headers, vnode text marking, UVM VM command helpers, stack setup, and NetBSD native coredump support.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/exec_aout.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/exec_ecoff.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/exec_ecoff.c

## Purpose
Implements ECOFF executable format recognition and VM command setup.

## Main Interfaces
- `exec_ecoff_execsw` registers the ECOFF executable switch with CPU probe and setregs hooks.
- `exec_ecoff_makecmds()` validates header size/magic, calls the CPU ECOFF probe, dispatches by OMAGIC/NMAGIC/ZMAGIC, and sets up the stack.
- `exec_ecoff_prep_omagic()` maps combined text/data and zeroes BSS.
- `exec_ecoff_prep_nmagic()` maps text and data separately from ECOFF offsets.
- `exec_ecoff_prep_zmagic()` marks text busy and maps text/data demand-paged.
- Module command adds/removes the exec switch entry.

## Dependencies
Uses ECOFF header macros, exec/vmcmd infrastructure, CPU ECOFF hooks, vnode text marking, and NetBSD native coredump support.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/exec_ecoff.c -->