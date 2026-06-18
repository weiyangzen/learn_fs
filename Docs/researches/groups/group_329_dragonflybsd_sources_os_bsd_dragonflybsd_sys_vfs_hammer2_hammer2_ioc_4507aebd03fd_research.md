# Group Research: group_329_dragonflybsd_sources_os_bsd_dragonflybsd_sys_vfs_hammer2_hammer2_ioc_4507aebd03fd

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/dragonflybsd` is included. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_ioctl.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_ioctl.h

## Purpose
Defines the HAMMER2 user/kernel ioctl ABI for administrative operations: version query, remote copy configuration, socket association, PFS management, inode metadata access, bulkfree, destructive deletion, emergency mode, growfs, and volume listing.

## Public ABI
The file exports fixed C structs used directly with `_IOWR('h', ...)` ioctl numbers:
- `hammer2_ioc_version`: returns filesystem ioctl version.
- `hammer2_ioc_recluster`: passes an fd for recluster operations.
- `hammer2_ioc_remote`: manages `volume->copyinfo[]` entries and socket descriptors. Carries `copyid`, iteration `nextid`, fd, and two `hammer2_volconf_t` copies for replace/rename-like operations.
- `hammer2_ioc_pfs`: describes PFS entries under the super-root, including name hash cursor fields, PFS type/subtype/flags, fsid, clid, and label.
- `hammer2_ioc_inode`: gets/sets inode data and optional quota/copy/check/compression flags.
- `hammer2_ioc_bulkfree`: parameters and counters for bulkfree scans.
- `hammer2_ioc_destroy`: unconditional delete by path or inode number.
- `hammer2_ioc_growfs`: grow filesystem target size and modified flag.
- `hammer2_ioc_volume` / `hammer2_ioc_volume_list`: expose multi-volume path/id/offset/size information.

## Constants And Commands
Important flags include `HAMMER2_PFSFLAGS_NOSYNC` and inode ioctl flags for inode quota, data quota, copies, check algorithm, and compression algorithm. Ioctl command numbers currently span version/recluster at 64-65, remotes at 68-71, sockets at 76-77, PFS operations at 80-84, inode get/set at 86-87, debug/bulkfree/destroy/emergency/growfs/volume-list at 91-97. Numbers 88-90 are explicitly reserved for old compression ioctls.

## Dependencies
Includes `sys/param.h`, `sys/syslimits.h`, `sys/ioccom.h`, `hammer2_disk.h`, and `hammer2_mount.h`, so this header binds the ioctl ABI to on-disk structures and mount flags.

## Integration Notes
The structures are ABI-sensitive: several include reserved padding or fixed arrays, and userland HAMMER2 tools must match them exactly. Any changes require compatibility review. `HAMMER2IOC_DESTROY` is explicitly dangerous because it deletes unconditionally.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_lz4.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_lz4.c

## Purpose
Kernel-adapted reduced LZ4 implementation used by HAMMER2 for file-data compression and decompression. It provides the public functions declared in `hammer2_lz4.h`: `LZ4_compress_limitedOutput()` and `LZ4_decompress_safe()`.

## Implementation Shape
The file is an older Yann Collet LZ4 source adapted for HAMMER2:
- Uses `MEMORY_USAGE 14`, producing a 16 KiB hash table.
- Uses `HEAPMODE 1`; HAMMER2 allocates the hash table with `kmalloc()` instead of stack allocation.
- Defines little-endian, unaligned-access-oriented read/write helpers and 32/64-bit architecture macros.
- Includes `hammer2_lz4_encoder.h` to instantiate compressor routines.

## Compression Flow
`LZ4_create()` allocates the hash table from a HAMMER2-specific malloc type `C_HASHTABLE`; `LZ4_free()` releases it. `LZ4_compress_limitedOutput()` allocates a context, selects `LZ4_compress64k_heap_limitedOutput()` for inputs below `LZ4_64KLIMIT`, otherwise uses `LZ4_compress_heap_limitedOutput()`, frees the context, and returns compressed size or zero on failure.

## Decompression Flow
`LZ4_decompress_generic()` implements token parsing, literal copying, offset decoding, match-length decoding, overlap copying, and strict input/output bounds checks. `LZ4_decompress_safe()` instantiates it with `endOnInputSize`, no 64 KiB prefix, full decoding, and max output size. Malformed streams return a negative value.

## Dependencies
Includes `hammer2.h`, `hammer2_lz4.h`, and `sys/malloc.h`. It relies on kernel memory allocation and HAMMER2 build context, not a generic userspace runtime.

## Risk Notes
This is low-level pointer arithmetic code. Correctness depends on LZ4 format invariants, endian assumptions, unaligned loads, and the caller supplying valid buffer sizes. HAMMER2 write code prefixes compressed LZ4 data with an `int` compressed size because LZ4 does not carry the original size itself.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_lz4.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_lz4.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_lz4.h

## Purpose
Public header for the HAMMER2-local LZ4 implementation. It exposes only the small safe decompression and limited-output compression API used by the filesystem.

## Interfaces
Exports:
- `int LZ4_decompress_safe(char *source, char *dest, int inputSize, int maxOutputSize);`
- `int LZ4_compress_limitedOutput(char *source, char *dest, int inputSize, int maxOutputSize);`

The header documents that safe decompression never writes past the destination buffer or reads past the input buffer, returning a negative result for malformed or oversized source streams. Limited-output compression returns compressed bytes written or zero if it cannot fit within `maxOutputSize`.

## Integration Notes
The API is C-compatible under C++ via `extern "C"`. HAMMER2 strategy code uses the compressor on writes and safe decompressor on reads for blocks whose blockref method encodes `HAMMER2_COMP_LZ4`.

## Risk Notes
The signatures use mutable `char *` for source even though callers often treat input as read-only, causing `__DECONST` use in kernel callers. This mirrors older LZ4 APIs but is not const-correct.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_lz4.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_lz4_encoder.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_lz4_encoder.h

## Purpose
Header-included implementation body for the LZ4 compressor. It is designed to be included by `hammer2_lz4.c` after architecture constants and helper macros are defined.

## Interfaces
Declares allocator helpers:
- `LZ4_create()`
- `LZ4_free()`

Declares and implements:
- `LZ4_compress_heap_limitedOutput()`
- `LZ4_compress64k_heap_limitedOutput()`

Both functions take an external hash-table context, source, destination, input size, and max output size.

## Compression Algorithm
The compressor:
- Initializes a hash table sized from `MEMORY_USAGE`.
- Uses 4-byte hash values from `A32(p)` and multiplicative hashing.
- Skips forward adaptively on incompressible data using `SKIPSTRENGTH`.
- Emits LZ4 tokens where high bits encode literal run length and low bits encode match length.
- Writes match offsets as little-endian 16-bit distances.
- Encodes extended literal/match lengths in 255-byte continuation bytes.
- Enforces output bounds before each token/literal/match-length emission; returns zero on overflow.
- Finishes by emitting last literals.

The 64K variant uses `U16` table entries and `CURRENTBASE(base) BYTE* base = ip`; the general variant uses architecture-dependent `HTYPE`.

## Dependencies
Requires macros and types from the including C file: `BYTE`, `U16`, `U32`, `A32`, `LZ4_HASH`, `RUN_MASK`, `ML_MASK`, `LZ4_WRITE_LITTLEENDIAN_16`, `LZ4_BLINDCOPY`, `LZ4_NbCommonBytes`, `MAX_DISTANCE`, `MFLIMIT`, and related constants.

## Risk Notes
This file is not standalone despite its `.h` extension. It intentionally relies on include-time macro context and undefines local macros at the end. Maintenance risk is high if included elsewhere or if macro names collide.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_lz4_encoder.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_mount.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_mount.h

## Purpose
Defines the userland-to-kernel mount argument structure and mount flags for HAMMER2.

## Public Interface
`struct hammer2_mount_info` contains:
- `const char *volume`: user pointer to a device/label string formatted like `/dev/ad0s1a@LABEL`.
- `int hflags`: extended HAMMER2 mount flags.
- `int cluster_fd`: socket/pipe fd for cluster management.
- reserved padding.

Flags:
- `HMNT2_LOCAL`: force local mode, disassociating PFSs from their clusters, mainly for debugging.
- `HMNT2_EMERG`: emergency mode.
- `HMNT2_UNUSED01`: reserved/unused.
- `HMNT2_USERFLAGS` and `HMNT2_DEVFLAGS` currently allow only `HMNT2_LOCAL`.

## Integration Notes
`hammer2_vfs_mount()` copies this struct from userland for non-root mounts, parses `volume`, applies PFS/device flags, and optionally holds `cluster_fd` for cluster reconnect. The header is also included by the ioctl ABI header.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_mount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_msgops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_msgops.c

## Purpose
Contains minimal HAMMER2 debug/message operation handlers for kdmsg cluster messaging.

## Functions
`hammer2_msg_adhoc_input(kdmsg_msg_t *msg)` logs an ad-hoc input message command and returns success. It does not dispatch or mutate message state.

`hammer2_msg_dbg_rcvmsg(kdmsg_msg_t *msg)` handles debug-message commands:
- `DMSG_DBG_SHELL`: shell execution is not supported; replies `DMSG_ERR_NOSUPP`.
- `DMSG_DBG_SHELL | DMSGF_REPLY`: prints auxiliary reply text if present, forcing NUL termination at `aux_size - 1`.
- default: replies unsupported for unknown messages.

## Dependencies
Includes kernel headers and `hammer2.h`; depends on kdmsg command flags and `kdmsg_msg_reply()`.

## Integration Notes
This is defensive/stub-like support for debug kdmsg traffic. Shell command execution is intentionally unsupported. The reply path assumes `aux_data` is writable and `aux_size` is nonzero when present; callers should not pass malformed aux buffers.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_msgops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_ondisk.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_ondisk.c

## Purpose
Handles HAMMER2 block-device vnode lookup/open/close, device list initialization/cleanup, volume-header reading, volume validation, and logical offset to volume lookup.

## Device Lifecycle
`hammer2_lookup_device()` resolves a device path. Root mounts use `kgetdiskbyname()` and `bdevvp()`, while normal mounts use `nlookup()` and `cache_vref()`. It validates the vnode is a block device with `vn_isdisk()`.

`hammer2_init_devvp()` parses colon-separated block-device strings, prepends `/dev/` for relative paths, looks up each device vnode, and appends `hammer2_devvp_t` entries. `hammer2_cleanup_devvp()` clears `si_mountpoint`, releases vnodes, frees path strings, and frees list entries.

`hammer2_open_devvp()` refuses already-referenced devices via `vcount()`, invalidates buffers, then opens each vnode read-only or read-write. `hammer2_close_devvp()` invalidates/saves buffers and closes open device vnodes.

## Volume Validation
`hammer2_read_volume_header()` scans the four HAMMER2 volume-header zones, reads each candidate header, checks magic, rejects reverse-endian filesystems, verifies all header CRC sections, and returns the valid header with the highest `mirror_tid`.

`hammer2_init_volumes()` initializes the `volumes[]` table, reads each supplied device’s volume header, checks version/nvolume/fsid/fstype consistency, records id/offset/size, captures root volume data and zone, and sets `si_mountpoint`.

`hammer2_verify_volumes_common()` validates root volume id, HAMMER2 UUID, initialized volume fields, device media sizes, and nonzero sizes. `hammer2_verify_volumes_1()` enforces legacy single-volume layout fields. `hammer2_verify_volumes_2()` enforces multi-volume count, total size, ordered ids, contiguous offsets, and required alignment.

## Offset Mapping
`hammer2_get_volume()` masks off radix bits, scans mounted volumes for the offset range, and panics if no volume owns the offset. Current code comments say locking is unnecessary until volume-add support exists.

## Risk Notes
Mount correctness depends on strict header CRC and layout checks. Multi-volume support assumes volumes are ordered and contiguous. Reverse-endian media is detected but unsupported.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_ondisk.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_strategy.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_strategy.c

## Purpose
Implements HAMMER2 logical file buffer strategy I/O. This layer backs the logical buffer cache and handles asynchronous reads/writes, decompression, compression, zero-block conversion, check-code generation, and live dedup heuristics.

## Read Path
`hammer2_vop_strategy()` dispatches `BUF_CMD_READ` to `hammer2_strategy_read()` and writes to `hammer2_strategy_write()`. Reads allocate an XOP, record the logical base offset and bio, and start `hammer2_strategy_read_desc`.

`hammer2_xop_strategy_read()` runs per cluster node. It resolves the inode chain, looks up the data chain at `lbase`, feeds the XOP cluster, then races to complete the frontend once quorum/focus can be collected. Missing data (`ENOENT`) is treated as a sparse zero block. Successful data calls `hammer2_strategy_read_completion()`.

`hammer2_strategy_read_completion()` handles embedded inode data and external data. For external data it records live dedup information if possible, marks the chain releasable, then copies or decompresses based on `bref.methods`: LZ4, ZLIB, or none. LZ4 data is prefixed with an `int` compressed size.

## Write Path
`hammer2_strategy_write()` marks the inode dirty, increments logical-write-in-progress hysteresis, starts a buffer-cache transaction, creates a modifying strategy XOP, and waits if the write pipe exceeds `hammer2_flush_pipe`.

`hammer2_xop_strategy_write()` copies the logical buffer to per-thread scratch before releasing the frontend bio lock, resolves the parent chain, calls `hammer2_write_file_core()`, feeds the XOP result, and completes the bio when collection reaches completion/quorum.

`hammer2_write_file_core()` selects among:
- no compression: assign physical storage, write direct/embedded/dedup data;
- `AUTOZERO`: convert all-zero blocks into holes when checks are enabled;
- LZ4/ZLIB/default: zero-check first, then attempt compression.

`hammer2_compress_and_write()` attempts compression when the inode heuristic allows it or `hammer2_always_compress` is set. It requires compression to fit in half the physical block, rounds compressed allocation to 1K-32K, zero-fills the remainder for dedup comparability, assigns physical storage, sets methods/checks, writes data, and records dedup candidates.

`zero_write()` deletes an existing data chain for all-zero writes, or zeroes embedded direct data. `hammer2_write_bp()` writes uncompressed data into a device buffer and sets check codes before issuing sync/async/delayed write.

## Dedup
`hammer2_dedup_record()` stores recent data offsets keyed by XXH64/check-derived CRC into a four-way heuristic table and marks DIO dedup-valid bits after data population. `hammer2_dedup_lookup()` validates candidate offsets by radix, DIO allocation/valid masks, and full `bcmp()` before returning a reused physical offset and setting `*datap = NULL`. `hammer2_dedup_clear()` clears heuristic offsets.

## Risk Notes
The code is heavily asynchronous: frontend bio ownership is protected by `xop->lock` and `xop->finished`. Dedup is explicitly heuristic and allows SMP collisions but validates before reuse. Check-code disabled data cannot be deduped because in-place overwrite would make reused storage unsafe.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_strategy.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_subr.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_subr.c

## Purpose
Shared HAMMER2 utility routines for type conversion, timestamp conversion, GUID/UUID mapping, directory hashing, block-size calculations, I/O counters, signal checks, and diagnostic strings.

## Type And Time Conversion
`hammer2_get_dtype()`, `hammer2_get_vtype()`, and `hammer2_get_obj_type()` convert between HAMMER2 object types, directory entry types, and vnode types.

`hammer2_time_to_timespec()`, `hammer2_timespec_to_time()`, and `hammer2_update_time()` convert HAMMER2 microsecond timestamps to/from `timespec` and current VFS timestamps.

`hammer2_to_unix_xid()` and `hammer2_guid_to_uuid()` map Unix uid/gid values into/out of a UUID node field.

## Directory Hashing
`hammer2_dirhash()` adapts HAMMER1 directory hashing. It hashes filename segments split by `.`, `-`, `_`, and `~`, sets bit 63, adds a full-name CRC component, and sets bit 15 so readdir cookies can remain positive while preserving low artificial cookie values.

## Block Sizing
`hammer2_getradix()` converts byte sizes to allocation radix, optimized for common HAMMER2 buffer sizes and clamped to minimum allocation where appropriate. `hammer2_calc_logical()` currently always returns `HAMMER2_PBUFSIZE` logical blocks and can return logical base/eof. `hammer2_calc_physical()` returns a smaller physical block size for the file EOF block or zero beyond EOF.

## Counters And Errors
`hammer2_adjreadcounter()` and `hammer2_adjwritecounter()` increment global read/write byte counters by blockref type. `hammer2_signal_check()` periodically yields and detects pending user-thread signals for long operations. `hammer2_error_str()` maps HAMMER2 error bits to human-readable strings. `hammer2_bref_type_str()` maps blockref types to names.

## Integration Notes
These helpers are used throughout HAMMER2 VFS, strategy, directory, inode, and recovery code. The directory hash shape is part of on-disk lookup semantics and must remain stable.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_synchro.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_synchro.c

## Purpose
Implements HAMMER2 cluster synchronization threads. Each relevant PFS cluster node can have a management thread responsible for synchronizing that node from authoritative peer data.

## Thread Loop
`hammer2_primary_sync_thread()` handles stop, freeze, unfreeze, and remaster flags, then repeatedly runs synchronization from `pmp->iroot`. It wraps scans in a transaction, uses a deferred inode list for recursion, retries on `HAMMER2_ERROR_EAGAIN`, and sleeps for events or a five-second poll interval.

Single-node masters generally do not need these threads; multi-node masters, soft masters, slaves, copies, and other clustered PFS types do.

## Synchronization Scan
`hammer2_sync_slaves()` first collects authoritative cluster focus excluding the local index. If the local chain modify TID already matches the focus, it returns. Otherwise it scans authoritative children and local children in key order, comparing with `hammer2_chain_cmp()`:
- local extra item: `hammer2_sync_destroy()`
- same key but stale modify TID: `hammer2_sync_replace()`
- missing local item: `hammer2_sync_insert()`
- exact match: advance both scans

Inode children are deferred instead of recursed immediately because the XOP scan is still active across node threads. The function later updates the inode metadata/modify TID only after child synchronization succeeds.

## Insert/Delete/Replace
`hammer2_sync_insert()` upgrades parent locking, reissues lookup for insertion position, creates a chain matching the focus blockref, copies body data where needed, sets checks, and returns to shared locks.

`hammer2_sync_destroy()` upgrades parent and child locks, permanently deletes the local chain, then resumes iteration from the next key.

`hammer2_sync_replace()` locks the local chain exclusively, resizes if needed, modifies it, copies focus metadata and data, recalculates checks, and handles PFSROOT inode replacement specially so local distinguishing fields are preserved while common metadata is updated.

## Risk Notes
The file is dominated by careful lock ordering. Insert/delete/replace intentionally unlock and relock parent/child chains to avoid deadlocks. Synchronization is possible only when peer data can be collected authoritatively; mismatch/no-quorum conditions surface as HAMMER2 errors and may require retry or manual repair.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_synchro.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_vfsops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_vfsops.c

## Purpose
Main HAMMER2 VFS operations implementation for DragonFlyBSD. It defines filesystem module init/uninit, mount/remount/unmount, PFS allocation/freeing, root/vget/stat/export operations, mount-time recovery, sync/flushing, write-pressure throttling, volume-data modification, and ENOSPC heuristics.

## Globals And Init
The file owns global mount/PFS lists, mount lock, sysctls, counters, malloc types, and VFS operation table. `hammer2_vfs_init()` sizes XOP worker groups from `ncpus`, sets DIO cache limits, verifies on-disk structure sizes, creates object caches for compression/decompression buffers and XOPs, initializes global lists/locks, and derives dirty-chain/dirty-inode limits. `hammer2_vfs_uninit()` destroys caches.

## PFS Lifecycle
`hammer2_pfsalloc()` finds or creates a PFS by cluster id or forced-local name, initializes transaction management, inode allocator, locks, queues, hashes, root inode, cluster slots, PFS type/name/hmp arrays, visible master counts, sync threads, and XOP helpers. `hammer2_pfsdealloc()` removes one cluster element and deletes associated sync/XOP threads. `hammer2_pfsfree()` tears down a PFS when no cluster chains remain. `hammer2_pfsfree_scan()` removes all references to an unmounted device from PFS/SPMP lists, freezing management threads while it edits embedded clusters.

## Mount Flow
`hammer2_vfs_mount()` handles root mounts, new mounts, secondary label-only mounts, and remount updates. It copies `hammer2_mount_info`, parses `device@label`, defaults labels from partition suffix, initializes device vnodes, matches existing mounted devices, opens new devices, initializes volume metadata, constructs the `hammer2_dev_t`, embedded volume chain and freemap chain, creates the super-root PFS, locates the super-root inode, runs recovery/fixup on writable mounts, initializes cluster I/O and bulkfree, optionally reconnects a cluster fd, then finds and attaches the requested PFS to `mp`.

`hammer2_remount()` supports read-only to read-write transition by reopening volumes writable, running recovery/fixup on the root volume, then updating `hmp`/PFS read-only state.

## Unmount Flow
`hammer2_vfs_unmount()` flushes vnodes and runs three syncs for clean teardown, cleans XOP helpers, and calls `hammer2_unmount_helper()`. The helper either detaches a PFS mount and decrements device mount counts, or fully decommissions a device: shuts down network and bulkfree, removes PFS references, flushes freemap and volume chains, closes/cleans device vnodes, clears modified flags, dumps chains for diagnostics, drops embedded chains, cleans DIO hashes, removes the mount list entry, and frees device allocators.

## Lookup, Root, Stat, Export
`hammer2_vfs_vget()` resolves inode numbers from cache or by XOP lookup under iroot. `hammer2_vfs_root()` initializes PFS inode/modify transaction counters from the root cluster if needed and returns the root vnode. `hammer2_vfs_statfs()` and `hammer2_vfs_statvfs()` report blocks/free space/files from the mounted PFS’s backing device and reserve 5% from non-root availability. `hammer2_vfs_vptofh()` and `hammer2_vfs_fhtovp()` implement simple file-handle conversion by inode number. `hammer2_vfs_checkexp()` uses `vfs_export_lookup()` for NFS export checks.

## Recovery And Fixups
`hammer2_recovery()` compares `freemap_tid` with `mirror_tid` and scans committed topology to mark newly referenced blocks allocated after a crash. `hammer2_recovery_scan()` recursively scans volume/inode/indirect topology with a depth-defer list and adjusts freemap state for blockrefs newer than the freemap sync tid. `hammer2_fixup_pfses()` corrects older media where PFSROOT blockref flags were lost after moving PFS inodes into indirect blocks.

## Sync And Throttling
`hammer2_vfs_sync_pmp()` moves dependency/side queues to syncq, carefully avoids vnode/inode deadlocks with `vget(... LK_NOWAIT)`, flushes dirty buffers and inode chains, restarts for PASS2/dependency cases, then flushes the PFS root last with `HAMMER2_XOP_VOLHDR` so volume headers and root blocksets update correctly. It waits for strategy BIO completion before ending the flush transaction.

`hammer2_lwinprog_ref/drop/wait()` throttle outstanding logical writes. `hammer2_vfs_modifying()` rejects writes on read-only mounts and calls `hammer2_pfs_memory_wait()`. Dirty memory helpers trigger async syncer work and sleep/wake with hysteresis based on dirty-chain and dirty-inode limits.

## Volume And Space Helpers
`hammer2_voldata_lock/unlock()` wrap the volume lock. `hammer2_voldata_modify()` marks the embedded volume chain modified and advances its mirror TID. `hammer2_vfs_enospace()` caches free-space values per tick across master/soft-master cluster members and returns warning/severe states based on root versus non-root reserve thresholds.

## Risk Notes
This file coordinates nearly all high-level HAMMER2 lifetimes. The riskiest areas are mount failure unwinding, PFS/device reference accounting, sync queue restart logic, and lock ordering around vnode/inode flushes. The code intentionally uses repeated syncs and recovery scans to handle delayed freemap consistency.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/hammer2/hammer2_vfsops.c -->