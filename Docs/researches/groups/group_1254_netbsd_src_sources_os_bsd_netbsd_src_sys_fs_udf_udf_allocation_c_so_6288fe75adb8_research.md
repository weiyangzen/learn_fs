# Group Research: group_1254_netbsd_src_sources_os_bsd_netbsd_src_sys_fs_udf_udf_allocation_c_so_6288fe75adb8

Scope checked against `Docs/research_subset_a.md`: `sources/os/bsd/netbsd-src` is included in subset A. All 11 listed source files were read completely; no file was sampled.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/udf_allocation.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/udf_allocation.c

Read completely: 3211 lines.

Implements UDF logical allocation, extent translation, free-space accounting, node growth/shrink, and allocation descriptor maintenance. It is the central allocator for UDF vnode data, directory FIDs, node descriptors, VAT-backed writes, space bitmap allocation, sequential media allocation, and metadata partition bookkeeping.

Core translation paths include `udf_translate_vtop()`, which maps UDF virtual partition addresses to physical logical block numbers for raw, physical, VAT virtual, sparable, and metadata partitions, and `udf_translate_file_extent()`, which maps file-relative logical blocks through allocation descriptors, returning zero-fill markers for free/unallocated extents and physical sectors for allocated extents. Metadata partition translation recursively walks the metadata file’s allocation descriptors before re-entering virtual-to-physical translation.

Free-space and reservation management is handled by `udf_calc_freespace()`, `udf_calc_vpart_freespace()`, `udf_reserve_space()`, `udf_do_reserve_space()`, `udf_do_unreserve_space()`, and `udf_cleanup_reservation()`. These combine logical volume integrity table counts, sequential track free counts, uncommitted block reservations, and a `UDF_DISC_SLACK` safety margin. If space is low, the code tries syncs and, for metadata partitions, attempts redistribution through metadata partition truncation hooks.

Allocation backends include VAT slot search/update, sequential track advancement, ordinary partition space bitmap allocation, and metadata bitmap allocation. `udf_allocate_space()` selects the backing mechanism using `ump->vtop_alloc[]`; `udf_free_allocated_space()` returns blocks to freed/unallocated bitmaps, VAT entries, or the metadata bitmap and updates logical volume integrity free counts. Several allocation types are explicitly not implemented, including metadata sequential and relaxed sequential allocation.

Allocation descriptor maintenance is extensive. `udf_get_adslot()` and `udf_append_adslot()` read and write short or long allocation descriptors across the FE/EFE and allocation extent descriptors, adding redirect descriptors and allocating AED blocks when needed. `udf_wipe_adslots()`, `udf_count_alloc_exts()`, and `udf_ads_merge()` rebuild, merge, and trim descriptor lists while keeping `l_ad`, descriptor CRC lengths, and `logblks_rec` synchronized.

`udf_late_allocate_buf()` allocates physical/logical space for delayed-write buffers and calls `udf_record_allocation_in_node()` for userdata, FIDs, and metadata space bitmap buffers. `udf_record_allocation_in_node()` rewrites the node’s descriptor stream around the newly allocated mappings: it copies descriptors before the overlap, inserts allocated runs, frees replaced allocations, preserves the tail, wipes descriptors, merges adjacent compatible extents, and appends the rebuilt list.

`udf_grow_node()` and `udf_shrink_node()` update file information length/object size and descriptor allocation state. Growth may keep internal allocation if it still fits, convert internal allocation to short/long allocation, append free extents, and evacuate existing inline data through vnode I/O. Shrink frees allocated extents past the new size, truncates the last kept extent, and can convert zero-length files back to internal allocation.

Risk areas are high because the file mutates on-disc allocation state, in-memory reservation counters, and descriptor CRC-covered structures. There are panics for impossible allocation-accounting states, unimplemented metadata partition grow/sparsify paths, and several comments calling out incomplete recovery behavior. Descriptor rewriting depends on exact locking and offset arithmetic across short/long descriptors, redirects, partial blocks, VAT entries, and metadata partition special cases.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/udf_allocation.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/udf_bswap.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/udf_bswap.h

Read completely: 76 lines.

Defines endian access helpers for UDF on-disc little-endian fields. On big-endian machines, `udf_rw16()`, `udf_rw32()`, and `udf_rw64()` inline to byte-swap operations. On little-endian machines, the same names are casts/no-ops.

The header is intentionally small but pervasive: UDF code uses these helpers both when reading on-disc fields and when writing values back into descriptor structures.

Risk is mostly misuse risk. Because the helpers are named as bidirectional read/write converters, callers must apply them consistently exactly once at every on-disc boundary.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/udf_bswap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/udf_mount.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/udf_mount.h

Read completely: 63 lines.

Defines the user/kernel mount argument ABI for NetBSD UDF. `struct udf_args` carries the version, device specifier, session selector, mount flags, GMT offset, uid/gid mapping parameters for anonymous and nobody ownership, an explicit sector size for dump/file mounts, and reserved space for future extension.

The only mount flag defined here is `UDFMNT_CLOSESESSION`, exposed with `UDFMNT_BITS` for flag decoding. `UDFMNT_VERSION` is currently `1`.

Risk is ABI compatibility: this structure is passed across the mount interface, so field ordering, sizes, and reserved space matter for old userland/new kernel interactions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/udf_mount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/udf_osta.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/udf_osta.c

Read completely: 520 lines.

Provides OSTA-derived support routines for UDF Unicode compression, checksums, and portable filename translation. The file is shared-style code: it can be built in kernel contexts and in tool contexts with `nbtool_config.h`.

`udf_UncompressUnicode()` decodes OSTA CS0 compressed Unicode names with compression IDs 8 or 16, treating deleted-entry IDs 254 and 255 as 8-bit and 16-bit encodings. `udf_CompressUnicode()` performs the reverse compression into CS0 byte streams.

The file embeds a CRC-CCITT-style 256-entry table and exposes `udf_cksum()` for byte streams, `udf_unicode_cksum()` for Unicode strings in big-endian byte order, and `udf_ea_cksum()` for the 48-byte extended-attribute checksum region.

Filename translation is handled by `UDFTransName()`. It walks a Unicode input name, replaces illegal or nonprintable characters with `_`, tracks short extensions, truncates to `MAXLEN`, and appends `#` plus a four-hex-digit Unicode CRC when the name needed modification or truncation. With the default `UNIX` path, only NUL and slash are illegal; OS/2, Windows, and Mac variants are still present behind preprocessor branches.

Risk areas include caller-managed buffer sizing, limited validation of compressed Unicode streams, and the use of OSTA reference-era translation rules. The kernel fallback `isprint()` is ASCII-like, and the name transformation intentionally changes names while preserving uniqueness through CRC suffixes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/udf_osta.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/udf_osta.h -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/udf_osta.h

Read completely: 44 lines.

Declares the OSTA helper interface used by UDF code. It defines `unicode_t` as `uint16_t`, `byte` as `uint8_t`, sets default platform macros to `UNIX`, and sets default `MAXLEN` to 255.

Exported functions cover CS0 Unicode compression/decompression, byte and Unicode CRCs, extended-attribute checksums, OSTA filename translation, and null-terminated Unicode string length.

The header is simple but globally affects `udf_osta.c` behavior through the `UNIX` and `MAXLEN` defaults, so build environments that define alternate platform macros change filename legality and truncation rules.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/udf_osta.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/udf_readwrite.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/udf_readwrite.c

Read completely: 736 lines.

Implements generic UDF physical-sector I/O, descriptor I/O, descriptor fixups, and strategy dispatch wrappers. It is the common read/write helper layer below UDF metadata code and above the selected disc strategy backend.

Descriptor fixups include `udf_fixup_fid_block()`, which resynchronizes to FID descriptors inside a block, updates each FID tag location, and recalculates tag checksums; `udf_fixup_internal_extattr()`, which fixes embedded extended-attribute header tag locations and CRCs; and `udf_fixup_node_internals()`, which fixes internal FIDs, internal metadata bitmap descriptors, allocation extent CRC length quirks for older UDF versions, and final node descriptor tag/CRC sums.

Physical I/O helpers build top-level buffers and split transfers into nested `MAXPHYS`-sized buffers submitted through `udf_discstrat_queuebuf()`. `udf_read_phys_sectors()` synchronously reads one or more physical sectors. `udf_write_phys_sectors()` and the internal `udf_write_phys_buf()` synchronously write physical sectors while preserving vnode output accounting.

Descriptor readers/writers build on sector I/O. `udf_read_phys_dscr()` reads a descriptor, validates tag and payload checksums, handles empty blocks as “no descriptor”, and expands multi-sector descriptors when `udf_tagsize()` exceeds one sector. `udf_write_phys_dscr_sync()` and `udf_write_phys_dscr_async()` set tag locations, validate tag/CRC sums, and write descriptors either synchronously or with an iodone callback.

The bottom of the file is the strategy vtable facade: create/free/read/write logical-volume descriptors, queue buffers, synchronize caches, initialize a strategy, and finish a strategy by dispatching through `ump->strategy`.

Risk areas include nested buffer lifecycle/accounting, descriptor checksum correctness, and assumptions that logical-space descriptors are at most one sector except where explicitly handled. Some paths panic on unexpected tag types, so corrupted or misclassified buffers must be filtered before these helpers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/udf_readwrite.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/udf_rename.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/udf_rename.c

Read completely: 683 lines.

Implements UDF rename using NetBSD’s `genfs_sane_rename` framework. `udf_rename()` adapts the legacy VOP rename API through `genfs_insane_rename()`, while `udf_sane_rename()` provides the saner internal call into the UDF-specific `genfs_rename_ops` table.

The callback table supplies directory-empty checks, permission checks, actual rename/remove operations, lookup, genealogy analysis, and directory locking. Empty-directory checks populate/use UDF dirhash state. Permission checks map UDF ownership/access modes into the generic UFS-like rename/remove permission helpers.

`udf_gro_rename()` performs the core operation: gather source attributes, detach an existing target if present, attach the source node under the target name, detach the old source entry, update the moved directory’s `..` entry when reparenting a directory, and purge name-cache state. Rollback attempts reattach/detach if later steps fail. `udf_gro_remove()` handles the same-object rename-over-self case by detaching the original link and reporting the remaining link count.

`udf_gro_lookup()` performs directory lookup by name and returns the vnode found by ICB location. `udf_gro_genealogy()` walks `..` entries from the target directory toward root to detect whether the source directory is an ancestor, preventing directory cycles. `udf_gro_lock_directory()` locks a directory and fails if it has already been removed.

Risk centers on non-journaled rename ordering. The attach/detach/update-`..` sequence has rollback attempts but cannot provide full crash atomicity. Genealogy relies on valid on-disc `..` entries, and dirhash population failures conservatively report directories as non-empty.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/udf_rename.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/udf_strat_bootstrap.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/udf_strat_bootstrap.c

Read completely: 153 lines.

Defines the temporary bootstrap disc strategy used before the full UDF strategy is selected. It only supports queueing read buffers directly to the device vnode strategy.

All logical-volume descriptor create/free/read/write operations panic because bootstrap mode is not supposed to perform node descriptor I/O or writing. Cache sync and init/finish hooks are no-ops.

The strategy table `udf_strat_bootstrap` is therefore a minimal read-only pass-through for early mount-time probing. Risk is misuse: any write or descriptor operation while this strategy is active is treated as a kernel programming error and panics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/udf_strat_bootstrap.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/udf_strat_direct.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/udf_strat_direct.c

Read completely: 457 lines.

Implements the direct UDF strategy for media where fixed-position reads and writes can be submitted directly, while still supporting delayed allocation for sequential-style data buffers. It maintains a pool of logical-block-sized node descriptor buffers in `struct strat_private`.

Node descriptor operations allocate/free descriptors from the pool, read descriptors by translating their ICB through `udf_translate_vtop()` and `udf_read_phys_dscr()`, and write descriptors to translated sectors either synchronously or asynchronously. The async node descriptor callback marks nodes modified on write error, decrements `outstanding_nodedscr`, unlocks the node when the last descriptor write completes, and releases the iobuf.

`udf_queue_buf_direct()` classifies buffers into read, fixed write, or sequential write handling. Reads and fixed writes go straight to `VOP_STRATEGY()` after descriptor/node fixups for write buffers. Sequential writes are late-allocated with `udf_late_allocate_buf()`, FID blocks and metadata bitmap tags are fixed up, node internals are fixed, logical mappings are translated to physical mappings, adjacent physical sectors are coalesced into nested buffers, and those nested writes are submitted to the device.

Initialization creates the descriptor pool; finish destroys it and frees strategy private state. `udf_sync_caches_direct()` delegates to MMC cache synchronization.

Risk areas include late allocation during queueing, fixed-vs-sequential write classification by `b_udf_c_type`, and async descriptor unlocking. The direct strategy assumes the device/media combination can tolerate direct fixed writes except where it explicitly routes delayed sequential writes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/udf_strat_direct.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/udf_strat_rmw.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/udf_strat_rmw.c

Read completely: 1520 lines.

Implements the packet read-modify-write UDF strategy for media that require packet/ECC-line granularity. It keeps packet-sized `udf_eccline` cache entries with bitmaps for present sectors, pending read-in sectors, dirty sectors, and error sectors, plus per-sector nested-buffer callbacks for callers waiting on subranges.

The private state includes a scheduler thread, condition variable, strategy mutex, sequential-write mutex, queues for waiting/read/write/sequential-write/idle/free ECC lines, line pools, blob pools, and a hash table by packet start sector. ECC line helpers lock/unlock lines, push/pop/unqueue lines from queues, allocate or recycle lines, and decide the next queue based on refcounts, wanted locks, read-in bits, dirty bits, wait timers, full-packet availability, and sequential-write flags.

Descriptor operations are packet-cache aware. Creating a descriptor obtains the containing ECC line, marks the sector present, clears it, and returns an in-line pointer into the packet blob. Reading a descriptor schedules packet reads if needed, waits for the target sector to become present or errored, validates tag and payload checksums, and holds an ECC-line reference for the descriptor. Writing a descriptor validates checksums, fixes node internals, marks the sector dirty, and releases the node descriptor outstanding lock state.

`udf_queuebuf_rmw()` handles ordinary reads, fixed writes, and sequential writes. Reads copy immediately from present sectors or attach caller buffers to pending sector callbacks. Fixed writes copy caller data into ECC lines, mark sectors present/dirty, and complete caller nested buffers. Sequential writes allocate logical space late, fix FIDs/metadata bitmap tags/node internals, translate logical mappings to physical packet sectors, copy data into ECC lines, mark them sequential, and complete caller buffers.

The scheduler thread promotes waiting dirty lines after a timeout, reads missing sectors before partial-packet writes, writes only full present packets, prefers current queue activity for a short interval, trims excess free lines, and tears down all lines on finish. Read callbacks populate missing sectors and satisfy waiting buffers. Write callbacks clear dirty bits or mark sector errors. The blob pool uses wired kernel memory sized to the packet blob.

Risk areas are concurrency and packet correctness. The code depends on careful mutex/condition-variable discipline, line refcounts, queue membership invariants, and full-packet write guarantees. Write-error handling is mostly TODO/panic/assertion oriented; comments mention future sparable remapping. The strategy also has pressure limits for sequential-write busy lines and can block waiting for line availability.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/udf_strat_rmw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/udf_strat_sequential.c -->
# File Research: sources/os/bsd/netbsd-src/sys/fs/udf/udf_strat_sequential.c

Read completely: 737 lines.

Implements the sequential-media UDF strategy for recordable optical media, with separate queues for reading, fixed writes, and sequential writes. It owns a descriptor pool, a scheduler thread, condition variable/mutex, queue state, a sync request flag, and saved device disk-strategy settings.

Descriptor operations are similar to the direct strategy for allocation and reads, but writes account for VAT-style virtual partitions. `udf_write_logvol_dscr_seq()` writes descriptors at translated fixed positions for non-VAT partitions, while VAT-backed node writes can be issued as sequential writes whose final physical mapping is recorded later.

`udf_queuebuf_seq()` classifies buffers and enqueues them for the scheduler. Reads go to the reading queue; absolute writes go to the fixed write queue; other writes go to the sequential write queue. `udf_sync_caches_seq()` asks the scheduler thread to drain and synchronize caches, then waits for completion.

The sequential write path is in `udf_issue_buf()`. It late-allocates logical space with `udf_late_allocate_buf()`, relies on linear sequential-media mapping to derive the physical block number, fixes floating descriptor tag locations, updates VAT mappings for node writes through `udf_VAT_mapping_update()`, fixes node internals, fixes FID block tag locations, and submits the buffer to the device.

`udf_doshedule()` issues one buffer from the current queue synchronously, calls the original iodone callback after completion, and switches queues only after short idle windows to avoid expensive optical read/write mode changes. When switching from reading to sequential writing, it refreshes track information. When switching back to reading, it synchronizes MMC caches. Initialization installs a `discsort` device strategy, allocates queues and descriptor pools, and starts the scheduler thread; finish stops the thread, restores the old device strategy, and frees resources.

Risk areas include synchronous scheduler behavior, unhandled write-error recovery (`panic` on write errors), VAT update correctness, and the assumption that sequential media mappings are linear. Queue switching deliberately trades latency for optical-media efficiency.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/fs/udf/udf_strat_sequential.c -->