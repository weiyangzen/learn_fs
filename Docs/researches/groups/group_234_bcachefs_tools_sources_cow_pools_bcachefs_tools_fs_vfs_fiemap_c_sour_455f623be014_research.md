# Group Research: bcachefs-tools VFS and Linux Shim Sources

Scope: `Docs/research_subset_a.md` subset A, source tree `sources/cow-pools/bcachefs-tools`.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/vfs/fiemap.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/vfs/fiemap.c

Purpose: implements bcachefs `fiemap` support, translating extent btree records plus dirty pagecache state into `FIEMAP_EXTENT_*` records for userspace.

Key behavior:
- `bch2_fill_extent()` emits fiemap extents for direct data, inline data, reservations, reflinks, unwritten extents, compressed data, and unaligned mappings.
- `bch2_next_fiemap_pagecache_extent()` scans pagecache over btree holes and synthesizes delayed-allocation extents for dirty cached data.
- `bch2_next_fiemap_extent()` merges pagecache-delalloc state with extent btree mappings, resolves `KEY_TYPE_reflink_p` through indirect extent lookup, and trims keys to the requested range.
- `bch2_fiemap()` prepares the request, walks sector ranges, delays emission by one extent so the final record can be marked `FIEMAP_EXTENT_LAST`, and normalizes errors through `bch2_err_class()`.

Important interactions:
- Depends on `vfs/pagecache.c` seek helpers to detect dirty cached data in holes.
- Uses btree transactions and restarts; blocking pagecache scans are done through `drop_locks_do()` to avoid sleeping on folio locks while holding btree locks.
- The code explicitly notes fiemap mappings are not stable because bcachefs can relocate data in the background.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/vfs/fiemap.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/vfs/fs.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/vfs/fs.c

Purpose: main bcachefs VFS integration layer. It wires bcachefs inode, directory, file, superblock, export, mount, and lifecycle operations into Linux VFS interfaces.

Key behavior:
- Maintains bcachefs VFS inode cache using `rhashtable` keyed by `subvol_inum` plus a secondary `rhltable` keyed by inode number for open-inode/snapshot checks.
- Synchronizes btree inode state into VFS inodes via `bch2_inode_update_after_write()`.
- Treats VFS atime as the source of truth and folds it into transactional inode updates with `bch2_inode_fold_atime()`.
- Implements create, lookup, link, unlink, symlink, mkdir, rename, tmpfile, getattr, setattr, file attributes, mmap setup, open, readdir, and inode eviction.
- Defines file, directory, symlink, special inode, address-space, export, and superblock operation tables.
- Handles NFS export file handles with bcachefs-specific fid structs containing inode, subvolume, and generation.
- Implements mount flow through `fs_context`: parse options, open/start devices, create or reuse superblock, initialize root inode/dentry, and handle reconfigure read-only/read-write transitions.
- Initializes and tears down VFS resources: inode cache, biosets, writepage buffer pool, writeback workqueue, inode hash tables, and fast inode list.

Important interactions:
- Calls lower bcachefs transactional helpers for inode/dirent/subvolume/quota mutations.
- Delegates buffered and direct I/O operations to `vfs/io.*`, pagecache methods to `vfs/pagecache.*`, xattrs/ACLs to `fs/xattr.*` and `fs/acl.*`, and ioctl handling to `vfs/ioctl.*`.
- Uses per-inode `ei_update_lock` for inode metadata updates and `ei_pagecache_lock` guards for pagecache add/block coordination.
- Contains Linux-version compatibility branches for inode state APIs, mmap setup, fileattr naming, and Unicode dentry behavior.
- Snapshot subvolumes are marked on inodes and excluded from quota accounting.

Notable constraints:
- `bch2_alloc_inode()` is a `BUG()` because inodes are allocated through bcachefs-specific paths.
- Eviction removes or retains hash entries carefully depending on whether the inode is being deleted, so fsck/open-inode checks can see unlinked open inodes.
- Casefold dentry ops are installed selectively to avoid generic casefold overhead on non-casefolded directories.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/vfs/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/vfs/fs.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/vfs/fs.h

Purpose: declares the bcachefs VFS inode wrapper and public VFS-layer helpers.

Key contents:
- `struct bch_inode_info` embeds `struct inode` and adds bcachefs state: subvolume inode identity, hash links, cached reserved extent range, update/pagecache/quota locks, quota state, nocow flush device mask, btree inode copy, and delayed writeback work.
- Defines pagecache add/block locking helpers using `two_state_lock_t`.
- Defines inode flag bits: `EI_INODE_ERROR`, `EI_INODE_SNAPSHOT`, and `EI_INODE_HASHED`.
- Provides ordered multi-inode lock/unlock macros that sort inode pointers before acquiring pagecache-block and/or update locks.
- Declares VFS inode lookup/create/write/update helpers, quota transfer, setattr/unlink, fiemap, VFS init/exit, and dirty-inode scheduling.

Important interactions:
- Included by most VFS files as the shared inode contract.
- The cached reserved range comment documents a critical staleness contract: allocation can become more allocated without notification, but deallocation must clear cached state under pagecache blocking.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/vfs/fs.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/vfs/io.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/vfs/io.c

Purpose: implements higher-level file I/O operations around fsync, truncate, fallocate, remap/dedupe, nocow flushes, i_size updates, quota accounting, and `llseek` data/hole behavior.

Key behavior:
- Issues asynchronous prefush bios for devices touched by nocow writes, then integrates that into fsync.
- `bch2_fsync()` waits dirty file data, syncs inode metadata, flushes journal sequence, flushes nocow writes, checks writeback errors, and emits trace data.
- `bchfs_truncate()` coordinates DIO waits, pagecache blocking, partial-folio zeroing, pagecache truncation, btree truncation, i_blocks accounting, reserved-range invalidation, and final inode metadata update.
- Fallocate supports regular allocation, zero range, punch hole, insert range, and collapse range.
- Remap/dedupe validates flags/alignment/overlap, blocks pagecache, invalidates destination pages, reserves quota, remaps btree extents, adjusts i_size, and optionally flushes sync destinations.
- `bch2_llseek()` supports normal seeks plus `SEEK_DATA`/`SEEK_HOLE`, combining extent btree state with dirty pagecache scans.

Important interactions:
- Relies on pagecache helpers for folio truncation, reservation marking, pagecache hole/data scanning, and write-invalidate loops.
- Uses `bch2_i_sectors_acct()` to keep VFS `i_blocks`, quota reservation, and quota accounting aligned.
- Uses per-inode cached reservation ranges from `fs.h`; operations that mutate extent layout clear the cache.
- Most mutating paths check read-only state or acquire internal write refs.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/vfs/io.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/vfs/io.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/vfs/io.h

Purpose: public declarations and small helpers for the VFS I/O layer.

Key contents:
- `struct nocow_flush` embeds a bio used for block-device preflushes after nocow writes.
- `struct folio_vec` plus `bio_for_each_folio()` adapters iterate bios at folio granularity.
- `struct quota_res` tracks reserved sectors for quota preallocation.
- Inline quota reservation add/put helpers update `inode->ei_quota_reserved` under quota locking when quota is enabled; stubbed to no-ops otherwise.
- Declares fsync, truncate, fallocate, remap, llseek, nocow flush, i_size update, and fault-disabled mapping helpers.

Important interactions:
- Included by `io.c`, `pagecache.c`, and other VFS I/O implementation files.
- Bridges disk reservation, quota reservation, folio state, and inode accounting.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/vfs/io.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/vfs/ioctl.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/vfs/ioctl.c

Purpose: implements file-level bcachefs ioctls and compatibility ioctl dispatch.

Key behavior:
- Provides compatibility wrappers for path create/remove helper APIs before Linux 6.18.
- Supports reinheriting inode attributes from a parent directory.
- Implements get/set generation, filesystem label get/set, and `FS_IOC_GOINGDOWN`.
- Implements subvolume create/destroy, including snapshot creation, permission/security checks, idmap checks, VFS path locking, create-lock synchronization, and fsnotify events.
- Implements subvolume listing and subvolume-to-path queries with permission-aware traversal.
- Implements snapshot tree query, including snapshot accounting readout.
- Supports reflink option propagation and setting `REFLINK_P_MAY_UPDATE_OPTIONS`.
- Implements raw direct pread with optional poison-check bypass and structured error reporting.
- Implements unpoisoning extents, including reflink target extents.
- Dispatches known commands in `bch2_fs_file_ioctl()`, forwarding unknowns to generic `bch2_fs_ioctl()`.

Important interactions:
- Calls into `fs.c` create/unlink/VFS inode lookup helpers, snapshot/subvolume modules, btree transaction iteration, direct I/O read path, and reflink format helpers.
- Security-sensitive paths use capability checks, owner checks, VFS permissions, LSM hooks, mount write references, and idmapped mount helpers.
- `CONFIG_COMPAT` maps 32-bit flag/version ioctls to native commands where possible.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/vfs/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/vfs/ioctl.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/vfs/ioctl.h

Purpose: small header declaring the VFS file ioctl entry points.

Key contents:
- `bch2_fs_file_ioctl(struct file *, unsigned, unsigned long)`
- `bch2_compat_fs_ioctl(struct file *, unsigned, unsigned long)`

Important interactions:
- Included by `fs.c` to attach ioctl handlers to file and directory `file_operations`.
- Included by `ioctl.c` as its implementation contract.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/vfs/ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/vfs/pagecache.c -->
# File Research: sources/cow-pools/bcachefs-tools/fs/vfs/pagecache.c

Purpose: implements bcachefs per-folio sector state, reservation handling, dirtying/undirtying, mmap fault support, invalidation/release hooks, and pagecache data/hole scanning.

Key behavior:
- `bch2_filemap_get_contig_folios_d()` gets contiguous folios, limiting creation after a 1 MiB window.
- `bch2_write_invalidate_inode_pages_range()` repeatedly writes and invalidates pagecache ranges until pages are gone or an error occurs.
- `bch2_folio_set()` initializes per-sector folio state from extent btree records and publishes cached sequential reservation state into `bch_inode_info`.
- Tracks sector states: unallocated, reserved, dirty, dirty_reserved, allocated.
- Manages disk and quota reservations before dirtying folios, including partial reservation support.
- `bch2_set_folio_dirty()` consumes reservations, updates per-sector state and `i_blocks`, and dirties the folio.
- `bch2_vfs_dirty_folio()` handles generic VFS dirty callbacks by obtaining nofail reservations.
- `bch2_page_fault()` coordinates page faults with pagecache blocking and fault-disabled mappings.
- `bch2_page_mkwrite()` reserves space, updates file time, marks folio dirty, waits for stable writes, and schedules delayed inode writeback.
- Invalidate/release hooks clear per-folio bcachefs state and return reservations.
- Seek helpers scan pagecache for dirty data or holes and are used by fiemap, fallocate, and `SEEK_DATA`/`SEEK_HOLE`.

Important interactions:
- This file is the in-memory contract between VFS pagecache and bcachefs COW allocation semantics.
- Callers must respect lock ordering: btree locks cannot be held while blocking on folio locks unless locks are dropped and reacquired.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/vfs/pagecache.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/vfs/pagecache.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/vfs/pagecache.h

Purpose: declares per-folio bcachefs pagecache structures, state helpers, reservation APIs, and pagecache scanning interfaces.

Key contents:
- `folios` dynamic array typedef for `struct folio *`.
- Safe `folio_end_pos()`, `folio_sectors()`, `folio_sector()`, and `folio_end_sector()` helpers using `u64` where needed to avoid overflow near maximum file offsets.
- Sector state enum generated from `BCH_FOLIO_SECTOR_STATE()`.
- `struct bch_folio_sector` stores fully allocated replica count, reserved replica count, and sector state.
- `struct bch_folio` stores a lock, write count, state-uptodate flag, and flexible sector-state array.
- `BCH_WRITEPAGE_BUF_BYTES` computes worst-case per-folio state snapshot size for writepage buffer pool sizing.
- Declares folio initialization, pagecache mark/unmark, reservation get/put, dirty/undirty, fault, invalidate/release, and seek helpers.

Important interactions:
- Included by `pagecache.c`, `fiemap.c`, `io.c`, and address-space operations.
- The `inode_nr_replicas()` helper derives required replicas from inode options or filesystem default.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/vfs/pagecache.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/vfs/types.h -->
# File Research: sources/cow-pools/bcachefs-tools/fs/vfs/types.h

Purpose: defines filesystem-wide VFS state embedded in `struct bch_fs`.

Key contents:
- `struct bch_fs_vfs` contains:
  - active inode fast list,
  - inode hash tables,
  - biosets for writepage, direct write, direct read, and nocow flush,
  - writepage buffer mempool,
  - delayed writeback workqueue.

Important interactions:
- Initialized and destroyed by `bch2_fs_vfs_init()`, `bch2_fs_vfs_init_rw()`, and `bch2_fs_vfs_exit()` in `fs.c`.
- Used by VFS inode tracking, direct I/O, writeback, and nocow flush paths.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/fs/vfs/types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/asm/page.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/asm/page.h

Purpose: empty compatibility placeholder.

Key contents:
- File is zero bytes and defines no declarations or macros.

Important interactions:
- Exists so code including kernel-style `<asm/page.h>` can resolve the path in the bcachefs-tools userspace build environment.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/asm/page.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/asm/unaligned.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/asm/unaligned.h

Purpose: selects endian-correct unaligned access helpers for the userspace kernel-shim environment.

Key contents:
- On little endian, includes little-endian struct helpers and big-endian byteshift helpers, then maps `get_unaligned`/`put_unaligned` to little-endian variants.
- On big endian, does the inverse.
- Fails compilation if endianess is not known.

Important interactions:
- Used by crypto and on-disk format code that expects kernel unaligned helpers.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/asm/unaligned.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/crypto/chacha.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/crypto/chacha.h

Purpose: kernel-style ChaCha20 constants and helper wrappers backed by libsodium.

Key contents:
- Defines ChaCha IV/key/block/state sizes and state word counts.
- Defines ChaCha constant words and `struct chacha_state`.
- `chacha_init_consts()` and `chacha_init()` initialize state from key and IV.
- `chacha20_crypt()` calls `crypto_stream_chacha20_xor_ic()` from libsodium.
- `chacha_zeroize_state()` clears state with `memzero_explicit()`.

Important interactions:
- Provides the kernel crypto API shape expected by bcachefs code while using libsodium in tools builds.
- Assumes libsodium call succeeds, enforced with `BUG_ON(ret)`.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/crypto/chacha.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/crypto/poly1305.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/crypto/poly1305.h

Purpose: kernel-style Poly1305 wrapper backed by libsodium.

Key contents:
- Maps key and digest sizes to libsodium constants.
- Defines `struct poly1305_desc_ctx` containing libsodium state.
- Provides inline `poly1305_init()`, `poly1305_update()`, and `poly1305_final()` wrappers.

Important interactions:
- Used by crypto code that expects Linux Poly1305 helper names.
- Uses `BUG_ON(ret)` for libsodium failures.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/crypto/poly1305.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/crypto/sha2.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/crypto/sha2.h

Purpose: kernel-style SHA constants, state structs, and SHA helper declarations for tools builds.

Key contents:
- Defines digest and block sizes for SHA1, SHA224, SHA256, SHA384, and SHA512.
- Defines initial hash constants for SHA1/SHA224/SHA256/SHA384/SHA512.
- Declares zero-message hash arrays.
- Defines SHA1/SHA256/SHA512 state structures.
- Declares update/finup functions for SHA1/SHA256/SHA512.
- Provides inline `sha256()` backed by libsodium `crypto_hash_sha256()`.

Important interactions:
- Lets bcachefs code compile against kernel-like SHA names while delegating SHA256 one-shot hashing to libsodium.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/crypto/sha2.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/keys/user-type.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/keys/user-type.h

Purpose: minimal key subsystem compatibility header.

Key contents:
- Include guard.
- Includes `<linux/key.h>`.
- No additional declarations.

Important interactions:
- Satisfies kernel-style includes for code that references user key types.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/keys/user-type.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/atomic.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/atomic.h

Purpose: userspace implementation of Linux atomic types and operations using compiler `__atomic` builtins.

Key contents:
- Defines `atomic_t`, `atomic_long_t`, and `atomic64_t`.
- Provides low-level atomic read/set/add/sub/and/or/exchange/cmpxchg macros.
- Provides memory barrier macros and acquire/release helpers.
- `DEF_ATOMIC_OPS()` generates the standard Linux atomic API for `atomic` and `atomic_long`, and usually `atomic64`.
- Includes fallback declarations for `ATOMIC64_SPINLOCK` platforms.

Important interactions:
- Core shim for code that expects Linux atomic APIs.
- Memory ordering is conservative in places: several SMP barriers map to sequentially consistent fences.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/atomic.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/backing-dev-defs.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/backing-dev-defs.h

Purpose: empty compatibility placeholder.

Key contents:
- File is zero bytes and defines no declarations or macros.

Important interactions:
- Present to satisfy Linux include paths where `<linux/backing-dev-defs.h>` is expected.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/backing-dev-defs.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/backing-dev.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/backing-dev.h

Purpose: minimal backing-device-info shim for userspace builds.

Key contents:
- Defines `congested_fn`, `enum wb_congested_state`, and `struct backing_dev_info`.
- Defines BDI capability flags.
- Stubs `bdi_congested()` to always return uncongested.
- Stubs setup/register/destroy operations.
- Defines `VM_MAX_READAHEAD`.

Important interactions:
- Used by block-device, superblock, and readahead-related shims.
- Provides enough BDI surface for bcachefs-tools without real kernel writeback congestion.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/backing-dev.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/bio.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/bio.h

Purpose: userspace shim for Linux bio helper APIs and bio list handling.

Key contents:
- Defines bio priority helpers, iterator accessors, segment iteration macros, sector/byte helpers, and data/no-advance checks.
- Implements `bio_advance_iter()`, `bio_segments()`, reference helpers, flag helpers, split wrappers, and bio list operations.
- Defines `struct bio_set` and bioset creation/init/exit declarations.
- Declares bio allocation, cloning, put/endio/reset/chain/copy/advance helpers.
- Provides virtual memory bvec mapping stubs.
- `bio_init()` initializes a bio over a caller-provided vec table.

Important interactions:
- Depends on `blkdev.h`, `blk_types.h`, `bvec.h`, atomics, and mempools.
- Used by bcachefs data and VFS I/O paths that are shared with kernel code.
- Dataless operations such as discard/write-zeroes are treated specially for iterator advancement and segment counts.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/bio.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/bit_spinlock.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/bit_spinlock.h

Purpose: userspace bit spinlock implementation using atomic bit operations plus futex wait/wake.

Key contents:
- `do_futex()` maps a bit number within an `unsigned long` bitmap to the correct 32-bit futex word, handling 64-bit endian layout.
- `bit_spin_lock()` atomically sets the target bit with acquire semantics and waits with futex while contended.
- `bit_spin_unlock()` clears the bit with release semantics and wakes waiters.
- `bit_spin_wake()` wakes waiters without unlocking.

Important interactions:
- Provides blocking bit-lock semantics for userspace code ported from Linux.
- Depends on futex headers and userspace RCU futex support.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/bit_spinlock.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/bitmap.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/bitmap.h

Purpose: userspace bitmap helper implementation compatible with common Linux bitmap APIs.

Key contents:
- Defines `DECLARE_BITMAP`, first/last word masks, and small-constant optimization helper.
- Implements bitmap weight, and, andnot, complement, zero, or, equality, empty tests, and allocation.
- Implements next-bit and next-zero-bit scanning, plus `find_next_andnot_bit()`.
- Defines `find_first_bit()` and `find_first_zero_bit()` aliases.

Important interactions:
- Depends on `bits.h`, `bitops.h`, `kernel.h`, and libc allocation/string routines.
- Used throughout bcachefs code for masks, device sets, flags, and allocation maps.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/bitmap.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/bitops.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/bitops.h

Purpose: userspace implementation of Linux bit operations and bit arithmetic helpers.

Key contents:
- Defines bit sizing macros, `BIT_MASK`, `BIT_WORD`, and `BITS_TO_*`.
- Implements atomic and non-atomic set/clear/test/test-and-set/test-and-clear operations.
- Provides acquire/release variants used for lock-style bit operations.
- Defines set-bit iteration macros.
- Implements hweight/popcount helpers, rotate helpers, find-last/find-first-set helpers, `ffz()`, and `rounddown_pow_of_two()`.

Important interactions:
- Included by bitmap and many kernel-shim headers.
- Uses compiler builtins and `__atomic` operations for userspace atomicity.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/bitops.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/bits.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/bits.h

Purpose: bit-mask construction macros compatible with Linux headers.

Key contents:
- Defines bit word and bit-per-type helpers.
- Defines `__GENMASK`, typed `GENMASK_TYPE()`, and `GENMASK*` variants for unsigned long, unsigned long long, and fixed-width integer types.
- Performs compile-time input checks for invalid mask ranges where possible.
- Provides assembly-compatible fallbacks without build-bug checks.

Important interactions:
- Used by bitmap/bitops and code that manipulates packed on-disk fields.
- Relies on compiler/overflow helpers for type maximums and build-time checks.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/bits.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/blk_types.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/blk_types.h

Purpose: defines block-layer data structures, request operations, request flags, bio structure, and status values for tools builds.

Key contents:
- Defines block open mode flags.
- Provides lightweight `struct inode`, `request_queue`, `gendisk`, `hd_struct`, and `block_device` shims.
- Defines `blk_status_t` values and `BIO_INLINE_VECS`.
- Defines `struct bio` layout including bdev, status, operation flags, iterator, refcounts, callbacks, vector table, and pool.
- Defines bio flag bits and bvec pool indexing.
- Defines request operation enum and request flag bits/macros.
- Provides `bio_op()` and `bio_set_op_attrs()`.
- Defines common read/write operation aliases.

Important interactions:
- Foundation for `bio.h` and `blkdev.h`.
- Used by bcachefs I/O code that expects Linux block-layer types while running in userspace tools context.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/blk_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/blkdev.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/blkdev.h

Purpose: userspace block-device shim exposing common Linux block-device and filesystem helper APIs.

Key contents:
- Defines file size, bio vector limits, major/minor device helpers, sector constants, page-sector helpers, and discard/nonrot stubs.
- Defines minimal `struct file`, `struct super_block`, `struct dir_context`, and `struct file_operations`.
- Declares block I/O submission, discard, zeroout, block-device open/lookup, capacity, logical block size, status conversion, and init helpers.
- Provides stubs for plugs, inode eviction, filesystem sync, char device registration, invalidate bdev, and `capable()`.
- Implements `file_inode()`, `file_bdev()`, `bdevname()`, `op_is_write()`, `bio_data_dir()`, `dir_emit()`, and `dir_emit_dots()`.

Important interactions:
- Provides much of the block/VFS compatibility base for bcachefs-tools.
- Some kernel security/scheduling concepts are deliberately simplified, e.g. `capable(cap)` always returns true in this shim.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/blkdev.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/bsearch.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/bsearch.h

Purpose: inline binary search helper compatible with Linux `bsearch`-style usage.

Key contents:
- Defines `__inline_bsearch()` taking key, base pointer, element count, element size, and comparison callback.
- Iteratively probes the middle element, narrows the search, and returns the matching element pointer or `NULL`.

Important interactions:
- Depends on `cmp_func_t` from Linux types shims.
- Used by code wanting header-only bsearch without libc API mismatch.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/bsearch.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/bug.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/bug.h

Purpose: userspace equivalents for Linux build-time assertions, BUG, and WARN macros.

Key contents:
- Defines build-bug macros such as `BUILD_BUG_ON`, `BUILD_BUG_ON_ZERO`, and power-of-two checks.
- `BUG()` flushes stdout, asserts false, and marks unreachable.
- `BUG_ON()` maps to `assert(!(cond))`.
- `WARN`, `WARN_ON`, `WARN_ONCE`, and `WARN_ON_ONCE` print warning locations to stderr and return condition status.
- Optional Valgrind memory debugging hook under `CONFIG_VALGRIND`.

Important interactions:
- Used pervasively by shim and bcachefs code.
- In userspace, `BUG_ON` behavior depends on assertions, unlike kernel panic semantics.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/bug.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/bvec.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/bvec.h

Purpose: block vector and iterator shim.

Key contents:
- Defines `struct bio_vec` with virtual address and length.
- Defines `struct bvec_iter` with sector, residual size, index, and completed bytes.
- Defines `struct bvec_iter_all`.
- Provides bvec virtual address, current address/length, current bvec construction, and iterator advancement helpers.
- Defines `for_each_bvec()` iterator macro.

Important interactions:
- Used by `bio.h` and I/O paths to walk memory vectors.
- This userspace version stores virtual addresses directly rather than kernel pages.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/bvec.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/byteorder.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/byteorder.h

Purpose: maps Linux byte-order helper names onto asm byte-order shim names and adds small helpers.

Key contents:
- Defines `swab*`, `cpu_to_*`, `*_to_cpu`, pointer, and in-place conversion aliases.
- Provides `le16_add_cpu()`, `le32_add_cpu()`, and `le64_add_cpu()`.
- Provides `le32_to_cpu_array()` for in-place array conversion.

Important interactions:
- Used by on-disk format parsing and serialization code.
- Depends on `<asm/byteorder.h>` and kernel-style type definitions.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/byteorder.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/cache.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/cache.h

Purpose: cacheline-size and cache-alignment shim.

Key contents:
- Defines L1 cache shift/bytes and SMP cache bytes as 64 bytes.
- Defines `L1_CACHE_ALIGN()`.
- Defines `__read_mostly` and `__ro_after_init` as empty.
- Defines cacheline alignment attributes.

Important interactions:
- Used by code that expects Linux cacheline annotation macros.
- In tools builds, most placement annotations are no-ops except explicit alignment attributes.

<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/cache.h -->