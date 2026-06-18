# subset-b-005774 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/misc.c -->
# sources/distributed-fs/ceph-client/fs/udf/misc.c

## Purpose
`misc.c` provides shared UDF descriptor utilities: extended-attribute insertion and lookup, tagged descriptor reads with checksum/version/CRC validation, and tag creation/update helpers. It is a low-level correctness layer used by mount-time descriptor parsing, inode metadata updates, allocation descriptors, and sparing-table repair.

## Important APIs, types, and functions
The public functions are `udf_add_extendedattr`, `udf_get_extendedattr`, `udf_read_tagged`, `udf_read_ptagged`, `udf_update_tag`, `udf_new_tag`, and `udf_tag_checksum`. The code works directly with ECMA/UDF structures such as `struct tag`, `struct genericFormat`, and `struct extendedAttrHeaderDesc`, plus in-core `struct udf_inode_info`.

## Control flow
Extended-attribute insertion checks available in-ICB room, creates the EA header when absent, shifts allocation descriptors or later EA classes as needed, updates application/implementation attribute offsets, then recomputes the EA header CRC and tag checksum. Lookup validates the EA header and walks variable-length generic attributes with overflow and undersize guards. Tagged reads reject invalid sentinel blocks, read a block, verify tag location, checksum, descriptor version, and descriptor CRC length before returning the buffer.

## State and persistence
The file mutates in-memory inode `i_data`, `i_lenEAttr`, and allocation descriptor placement; those changes persist only when inode writeback later writes the file entry. Descriptor tag helpers persist CRC/checksum fields into on-disk-format buffers.

## Dependencies and integration points
It depends on buffer-head I/O, little-endian UDF structures, `crc_itu_t`, `UDF_I`, and `UDF_SB`. `super.c`, `partition.c`, `truncate.c`, directory code, and inode code rely on the tagged descriptor and tag-update helpers.

## Risks and test signals
Risks include malformed EA lengths, memmove overlap mistakes when inserting attributes, accepting bogus descriptor CRC lengths, and using stale tag locations after moving metadata. Test signals include corrupted tag checksums, wrong descriptor versions, overlarge CRC lengths, EA insertion with existing allocation descriptors, and EA lookup across system/implementation/application attribute regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/namei.c -->
# sources/distributed-fs/ceph-client/fs/udf/namei.c

## Purpose
`namei.c` implements UDF VFS namespace operations for directories: lookup, create, tmpfile, mknod, mkdir, rmdir, unlink, symlink, hard link, rename, and NFS export file-handle conversion. It owns file identifier descriptor creation/deletion and keeps Logical Volume Integrity Descriptor file/dir counters in sync.

## Important APIs, types, and functions
The exported operation tables are `udf_dir_inode_operations` and `udf_export_ops`. Core helpers include `udf_fiiter_find_entry`, `udf_fiiter_add_entry`, `udf_fiiter_delete_entry`, `udf_expand_dir_adinicb`, `udf_add_nondir`, `empty_dir`, `udf_get_parent`, `udf_nfs_get_inode`, and `udf_encode_fh`. It relies on `struct udf_fileident_iter`, `struct fileIdentDesc`, and `struct allocDescImpUse`.

## Control flow
Lookup scans a directory iterator, filters deleted/hidden entries unless mount flags expose them, converts CS0 names to the host charset, and instantiates `udf_iget` results. Creation allocates an inode, sets file ops/address ops, appends or reuses a FID, stores the target ICB and unique-id imp-use value, updates parent times, and instantiates the dentry. Directories get an internal parent FID first, then the parent directory receives the child FID. Symlink creation encodes UDF `pathComponent` records either inline or into a new data block.

Rename validates source identity, directory emptiness and link counts, optionally locates the child `..` FID, creates/reuses the destination entry, copies the source FID payload, deletes the old entry, adjusts counters/link counts, and rewrites `..` when moving directories across parents. NFS export encodes UDF logical block, partition reference, and generation fields.

## State and persistence
Persistent state includes directory FID records, inode link counts, inode times, directory sizes and allocation extents, LVID file/dir counters, symlink encoded path components, and exported file-handle identity. It also converts inline AD-in-ICB directories to block-backed extents when an entry no longer fits inline.

## Dependencies and integration points
It integrates with `directory.c` iterators, `unicode.c` filename conversion, `inode.c` inode allocation and extent insertion, `balloc.c` block allocation, `truncate.c` tail truncation, VFS dcache/inode APIs, and Linux exportfs.

## Risks and test signals
Risks include FID tag-location mistakes after expanding inline directories, link-count/counter drift on failure paths, stale iterators after destination allocation during rename, mishandled hidden/deleted entries, symlink size limits, and the parent generation field in `udf_encode_fh` using the child generation. Test signals include create/unlink/rmdir/rename across directories, AD-in-ICB directory expansion, hidden and undelete mount flags, long or non-UTF8 names, absolute and relative symlinks, NFS export/restore, and corrupted `..` entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/namei.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/osta_udf.h -->
# sources/distributed-fs/ceph-client/fs/udf/osta_udf.h

## Purpose
`osta_udf.h` is the Linux copy of OSTA UDF 2.60 identifiers, suffixes, partition-map structures, allocation-descriptor implementation-use structures, and OS identifier constants. It binds Linux UDF code to the normative on-disk layout beyond base ECMA-167.

## Important APIs, types, and functions
There are no functions. Important definitions include UDF entity identifier strings such as `UDF_ID_COMPLIANT`, `UDF_ID_VIRTUAL`, `UDF_ID_SPARABLE`, and `UDF_ID_METADATA`; suffix types `domainIdentSuffix`, `UDFIdentSuffix`, `impIdentSuffix`, and `appIdentSuffix`; LVID implementation-use data; partition-map types for virtual, sparable, and metadata partitions; VAT 2.0; sparing tables; metadata-file ICB file types; and OS class/id values.

## Control flow
The header participates through structure casts and string comparisons in `super.c`, `partition.c`, `namei.c`, and inode metadata paths. Mount-time parsing uses it to classify partition maps and domain identifiers; LVID open/close writes Linux OS identifiers into `impIdent.identSuffix`.

## State and persistence
All structures are packed on-disk contracts. Incorrect changes alter media compatibility and persisted metadata interpretation. Constants identify write-protected domains, append-only VAT media, sparable media, metadata partitions, and allocation descriptor erase state.

## Dependencies and integration points
It includes `ecma_167.h` and is included through `udfdecl.h`. It is a cross-file schema contract for UDF mount, allocation, namespace, symlink, and statfs code.

## Risks and test signals
Risks are ABI/layout drift, string identifier mismatches, endian misuse by callers, and unsupported feature constants being interpreted as writable. Test signals are mounting media with UDF 1.50 virtual maps, sparable maps, UDF 2.50 metadata partitions, write-protected domain flags, and LVID implementation-use records created by Linux and non-Linux systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/osta_udf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/partition.c -->
# sources/distributed-fs/ceph-client/fs/udf/partition.c

## Purpose
`partition.c` resolves UDF logical partition block addresses to physical block numbers. It supports plain type-1 mappings, VAT virtual mappings, sparable packet remapping, metadata partitions with mirror fallback, and writable sparing-table relocation.

## Important APIs, types, and functions
Public entry points are `udf_get_pblock`, `udf_get_pblock_virt15`, `udf_get_pblock_virt20`, `udf_get_pblock_spar15`, `udf_get_pblock_meta25`, and `udf_relocate_blocks`. Internal `udf_try_read_meta` uses `inode_bmap` to translate metadata-file logical blocks.

## Control flow
`udf_get_pblock` validates the partition index and dispatches through `s_partition_func` when a special map is installed by `super.c`; otherwise it returns partition root plus logical block and offset. VAT lookup reads entries from the VAT inode, handling inline and block-backed VAT storage, then recursively translates through the VAT inode's physical partition while rejecting direct recursion. Sparable lookup aligns to packet boundaries and searches the first available sparing table for remapped packets. Metadata partition lookup maps through the metadata file, and on failure lazily loads and tries the mirror file.

`udf_relocate_blocks` finds the partition containing an old physical block, computes its packet, searches sparing entries, inserts or reuses a remap entry, updates all loaded sparing tables, recomputes descriptor tags, and returns the replacement physical block.

## State and persistence
The file reads and mutates `udf_part_map` type-specific state, VAT inode contents, sparing table buffers, metadata-file inodes, and `MF_MIRROR_FE_LOADED`. Sparing relocation persists by marking sparing-table buffers dirty.

## Dependencies and integration points
It depends on partition maps populated in `super.c`, `inode_bmap` and `udf_bread` from inode code, `udf_update_tag` from `misc.c`, and `s_alloc_mutex` for sparing relocation serialization.

## Risks and test signals
Risks include off-by-one VAT bounds (`block > s_num_entries`), recursion through virtual partitions, invalid sparing table ordering, missing mirror metadata, and dirtying only partially loaded sparing tables. Test signals include VAT 1.50/2.00 media, packet-remapped sparable images, failed metadata primary reads with mirror fallback, invalid partition references, and simulated block relocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/partition.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/super.c -->
# sources/distributed-fs/ceph-client/fs/udf/super.c

## Purpose
`super.c` implements UDF filesystem registration, mount/remount option parsing, superblock initialization and teardown, volume descriptor discovery, partition map loading, Logical Volume Integrity Descriptor management, statfs, and module lifecycle.

## Important APIs, types, and functions
Key external functions are `udf_sb_lvidiu`, `udf_compute_nr_groups`, `udf_find_metadata_inode_efe`, `lvid_get_unique_id`, `_udf_err`, and `_udf_warn`. Major internal flows are `udf_fill_super`, `udf_load_vrs`, `udf_scan_anchors`, `udf_process_sequence`, `udf_load_logicalvol`, `udf_load_partdesc`, `udf_load_vat`, `udf_load_metadata_files`, `udf_load_logicalvolint`, `udf_open_lvid`, `udf_close_lvid`, `udf_sync_fs`, and `udf_count_free`.

## Control flow
Module init creates the inode cache and registers the `udf` filesystem. Mount allocates `udf_sb_info`, copies parsed options, determines the session, probes block sizes unless fixed, validates the Volume Structure Descriptor area, scans standard and fallback anchor locations, processes main then reserve descriptor sequences, loads the prevailing PVD/LVD/PD records, builds partition maps, loads LVID chains with nesting limits, checks supported UDF revisions, locates the file set, opens the LVID on writable mounts, and installs the root dentry.

Partition-map loading classifies type-1, virtual, sparable, and metadata maps, validates domain identifiers and write compatibility, loads allocation bitmap/table metadata, VAT inodes, sparing tables, and metadata/mirror/bitmap files. Remount applies mutable credential/mode flags and transitions LVID open/close state for read-only changes.

## State and persistence
Persistent effects include opening/closing the LVID integrity state, updating LVID timestamps, unique IDs, file/dir counters via callers, and dirtying LVID buffers on sync. Runtime state includes partition maps, bitmaps/tables, metadata inodes, VAT inode, NLS map, mount flags, root partition, volume id, last block/session/anchor, and inode cache objects.

## Dependencies and integration points
It integrates with Linux `fs_context`, block-device mounts, buffer-head I/O, NLS, exportfs, UDF inode/name/allocation modules, low-level CD session probing, and UDF/ECMA on-disk schemas. `partition.c`, `namei.c`, and allocation code consume the state initialized here.

## Risks and test signals
Risks include accepting malformed descriptor sequence loops, reserve/main sequence fallback errors, blocksize probing cleanup gaps, incorrect read-write rejection for unsupported media, LVID corruption or missing unique IDs, anchor heuristics on open/drive-misreported media, and free-space count overflow. Test signals include multi-session optical media, `novrs`, explicit `bs/session/lastblock/anchor`, writable versus read-only mounts on VAT/sparable/metadata partitions, corrupted LVID chains, unsupported UDF revisions, remount ro/rw, and `statfs` free-space paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/super.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/symlink.c -->
# sources/distributed-fs/ceph-client/fs/udf/symlink.c

## Purpose
`symlink.c` decodes UDF symbolic-link path component records into normal path strings for VFS readlink and attributes. It provides symlink address-space and inode operations.

## Important APIs, types, and functions
The exported tables are `udf_symlink_aops` and `udf_symlink_inode_operations`. Internal helpers are `udf_pc_to_char`, `udf_symlink_filler`, and `udf_symlink_getattr`. It consumes `struct pathComponent` streams and `udf_get_filename`.

## Control flow
Readlink goes through `page_get_link`, which triggers `udf_symlink_filler`. The filler rejects encoded symlinks longer than one block, chooses inline `i_data + i_lenEAttr` or reads block zero via `udf_bread`, decodes components into the folio, and completes the folio read. Component decoding maps root/absolute markers, parent, current directory, and named components, appending `/` separators and converting CS0 names through `udf_get_filename`. `getattr` reads the decoded first folio and reports decoded string length as `st_size`, not the encoded byte count.

## State and persistence
The file does not mutate disk. It interprets persisted symlink payloads stored either in the file entry or external data blocks and exposes decoded runtime folio contents.

## Dependencies and integration points
It depends on UDF inode allocation type, `udf_bread`, filename conversion, pagecache folio helpers, VFS symlink helpers, and `inode_nohighmem` setup from creation/read paths.

## Risks and test signals
Risks include malformed component lengths overrunning the encoded payload, decoded path truncation, root component semantics, pagecache errors affecting `getattr`, and mismatch between encoded `i_size` and decoded size. Test signals include inline and block-backed symlinks, absolute paths, repeated slashes, `.` and `..`, long component names, malformed component lengths, and `lstat` size consistency with `readlink`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/symlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/truncate.c -->
# sources/distributed-fs/ceph-client/fs/udf/truncate.c

## Purpose
`truncate.c` shortens UDF extent lists, discards preallocation, trims the last extent to `i_size`, and frees no-longer-referenced data or indirect allocation extents.

## Important APIs, types, and functions
Public functions are `udf_truncate_tail_extent`, `udf_discard_prealloc`, and `udf_truncate_extents`. Internal helpers are `extent_trunc` and `udf_update_alloc_ext_desc`.

## Control flow
`extent_trunc` rewrites one allocation descriptor to a shorter length, converts preallocated but not recorded space to unallocated form when needed, and frees blocks beyond the new extent end. Tail truncation walks extents until logical bytes exceed `i_size`, rewinds to the containing descriptor, trims it, and warns if extents remain past EOF. Preallocation discard finds a trailing `EXT_NOT_RECORDED_ALLOCATED` extent, deletes it, and frees its blocks. Full truncation maps the first block after the new EOF, trims that extent to the byte offset, then iterates remaining descriptors; indirect extent descriptors switch traversal to the external allocation extent and are freed when emptied.

## State and persistence
The file mutates allocation descriptors in the inode entry or allocation extent blocks, `i_lenAlloc`, `i_lenExtents`, and dirty state. It frees blocks through UDF allocation code and updates allocation extent descriptor tags and dirty metadata buffers.

## Dependencies and integration points
It depends on `inode_bmap`, `udf_next_aext`, `udf_current_aext`, `udf_write_aext`, `udf_delete_aext`, `udf_free_blocks`, `udf_update_tag`, `mmb_mark_buffer_dirty`, and inode locking performed by callers in `inode.c`.

## Risks and test signals
Risks include freeing the wrong block range for partial extents, mishandling `EXT_NEXT_EXTENT_ALLOCDESCS`, stale `lenalloc`, leaked preallocation, and inconsistent `i_lenExtents` after iterator errors. Test signals include shrinking direct and indirect extent files, preallocated tail discard, AD short versus AD long, exact block-boundary truncates, inline AD-in-ICB bypass, and corrupted extent chains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/truncate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/udf_i.h -->
# sources/distributed-fs/ceph-client/fs/udf/udf_i.h

## Purpose
`udf_i.h` defines UDF in-core inode-private state and extent-position helper structures. It is the central contract for all UDF inode, allocation, directory, symlink, and truncation code.

## Important APIs, types, and functions
It defines `struct extent_position`, `struct udf_ext_cache`, and `struct udf_inode_info`, plus `UDF_I()` to recover the private inode from `struct inode`. Important fields include physical inode location, unique ID, extended attribute and allocation descriptor lengths, logical extent length, allocation goals, checkpoint/extra permissions, allocation type, extended-file-entry flags, stream directory fields, inline data pointer, metadata buffer tracking, extent cache, and extent-cache lock.

## Control flow
The header has no standalone control flow. Its comments define locking rules: regular file and symlink allocation information is protected by `i_data_sem` and inode mutex; extent mutations require write ownership and inode serialization. Directory protection is through inode mutex.

## State and persistence
Most fields mirror or cache persistent file-entry data: location, unique ID, allocation descriptors, inline data, timestamps, and extent lengths. Other fields are runtime-only allocation hints, caches, locks, and metadata buffer accounting.

## Dependencies and integration points
It is included by nearly every UDF C file. `super.c` initializes the structure in the slab constructor/allocator, `inode.c` populates it from disk, and `namei.c`, `partition.c`, `truncate.c`, and `symlink.c` rely on the layout and locking rules.

## Risks and test signals
Risks include violating allocation locking rules, stale cached extents after mutation, inconsistent `i_lenAlloc`/`i_lenExtents`, and inline data lifetime issues. Test signals include concurrent buffered writes/truncates, inline-to-block expansion, symlink reads during eviction, and metadata buffer dirty tracking under writeback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/udf_i.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/udf_sb.h -->
# sources/distributed-fs/ceph-client/fs/udf/udf_sb.h

## Purpose
`udf_sb.h` defines UDF superblock-private state, mount/compatibility flags, partition-map state, and helpers for querying and mutating filesystem flags.

## Important APIs, types, and functions
Key types are `struct udf_meta_data`, `struct udf_sparing_data`, `struct udf_virtual_data`, `struct udf_bitmap`, `struct udf_part_map`, and `struct udf_sb_info`. It defines read/write revision limits, mount flags such as `UDF_FLAG_USE_AD_IN_ICB`, `UDF_FLAG_STRICT`, `UDF_FLAG_RW_INCOMPAT`, partition flags, map type constants, metadata flags, `UDF_SB()`, `UDF_QUERY_FLAG`, `UDF_SET_FLAG`, and `UDF_CLEAR_FLAG`.

## Control flow
There is no independent control flow. `super.c` allocates, fills, and frees this state at mount/unmount; `partition.c` dispatches through `s_partition_func`; allocation and namespace paths use `s_alloc_mutex`, LVID state, and mount flags to decide behavior.

## State and persistence
`udf_sb_info` holds runtime representation of persistent media state: partition maps, volume identifier, session/anchor/last block, LVID buffer, root partition, serial number, UDF revision, VAT inode, and NLS map. Permission defaults, mount flags, allocation mutex, and dirty-LVID marker are runtime mount state.

## Dependencies and integration points
It depends on Linux bitops, mutexes, magic values, NLS, buffer heads, and inodes. It is the shared state surface between `super.c`, `partition.c`, `namei.c`, allocation, inode writeback, and `statfs`.

## Risks and test signals
Risks include wrong map type dispatch, stale LVID dirty state, mutable permission defaults racing without `s_cred_lock`, and treating `RW_INCOMPAT` as writable. Test signals include all partition map variants, remount option changes, LVID updates under allocation and namespace mutations, and read-only fallback when unsupported write features appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/udf_sb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/udfdecl.h -->
# sources/distributed-fs/ceph-client/fs/udf/udfdecl.h

## Purpose
`udfdecl.h` is the main internal UDF declaration hub. It includes UDF schemas/private headers, defines logging macros, common constants, inline layout helpers, iterator and descriptor scan structures, and cross-file function declarations.

## Important APIs, types, and functions
Important definitions include `UDF_DEFAULT_PREALLOC_BLOCKS`, `UDF_EXTENT_LENGTH_MASK`, `UDF_NAME_LEN`, `udf_file_entry_alloc_offset`, `udf_ext0_offset`, `struct udf_fileident_iter`, `struct udf_vds_record`, `struct generic_desc`, `udf_updated_lvid`, `udf_iget`, `udf_iget_special`, `udf_dir_entry_len`, and declarations for super, inode, misc, lowlevel, partition, unicode, ialloc, truncate, balloc, and directory modules.

## Control flow
The header's inline helpers influence many call paths. File-entry allocation offsets depend on whether the inode is an unallocated-space entry, extended file entry, or normal file entry and include extended attribute length. `udf_updated_lvid` asserts an open LVID, sets `s_lvid_dirty`, and is called by namespace/allocation code to defer LVID CRC rewrite to sync.

## State and persistence
The header itself has no storage, but its helpers control where persistent allocation descriptors live, how directory FID record sizes are computed, and when the LVID is marked dirty after persistent counter/unique-id updates.

## Dependencies and integration points
It includes `ecma_167.h`, `osta_udf.h`, `udf_sb.h`, `udfend.h`, and `udf_i.h`. Nearly every UDF source file includes it, so signature or helper changes affect the whole filesystem.

## Risks and test signals
Risks include mismatched prototypes, incorrect file-entry offsets when EAs are present, misuse of `udf_updated_lvid` without a valid open LVID, and directory entry length mismatches. Test signals include builds across UDF modules, EA-bearing files, unallocated-space entries, extended file entries, LVID dirty/sync behavior, and directory entries with implementation-use bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/udfdecl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/udfend.h -->
# sources/distributed-fs/ceph-client/fs/udf/udfend.h

## Purpose
`udfend.h` provides small endian-conversion helpers for UDF logical block addresses and allocation descriptors, converting between on-disk little-endian structures and kernel-native helper structures.

## Important APIs, types, and functions
It defines `lelb_to_cpu`, `cpu_to_lelb`, `lesa_to_cpu`, `cpu_to_lesa`, `lela_to_cpu`, `cpu_to_lela`, and `leea_to_cpu`. The converted structures include `lb_addr`, `short_ad`, `long_ad`, `kernel_long_ad`, and `kernel_extent_ad`.

## Control flow
There is no branching beyond field-by-field conversion. Callers use these helpers when reading FIDs, file set descriptors, logical volume contents, extent descriptors, and when writing FID ICB locations or allocation descriptors.

## State and persistence
The helpers do not own state. They are persistence-critical because they determine the byte order of block numbers, partition references, extent lengths, and descriptor locations written to disk.

## Dependencies and integration points
It depends on Linux byteorder helpers and is included by `udfdecl.h`. `namei.c`, `super.c`, `partition.c`, inode extent code, and truncation paths all use these conversions.

## Risks and test signals
Risks include double conversion, missing conversion on mixed-endian fields, and confusing native `kernel_*` structures with disk structures. Test signals include mounting and mutating media on big-endian and little-endian systems, FID location checks, allocation descriptor round trips, and metadata partition extent traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/udfend.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/udftime.c -->
# sources/distributed-fs/ceph-client/fs/udf/udftime.c

## Purpose
`udftime.c` converts between UDF disk timestamps and Linux `timespec64`, including UDF timezone encoding and sub-second fields.

## Important APIs, types, and functions
The public functions are `udf_disk_stamp_to_time` and `udf_time_to_disk_stamp`. They operate on ECMA/UDF `struct timestamp` and Linux `struct timespec64`.

## Control flow
Disk-to-Linux conversion checks timestamp type 1 for signed timezone offset in minutes, treats the unspecified `-2047` offset as UTC/no offset, converts calendar fields with `mktime64`, subtracts the offset, and sanitizes sub-second fields by accepting only centiseconds, hundreds-of-microseconds, and microseconds below 100. Linux-to-disk conversion uses `sys_tz.tz_minuteswest`, writes type 1 plus 12-bit offset, converts adjusted seconds through `time64_to_tm`, and splits nanoseconds into UDF sub-second components.

## State and persistence
The file has no private state. It affects persistent recording, inode, and LVID timestamps and the runtime interpretation of media timestamps.

## Dependencies and integration points
It depends on kernel time conversion helpers and is declared through `udfdecl.h`. `super.c` uses it for PVD recording time and LVID open/close timestamps; inode code uses it for file timestamps.

## Risks and test signals
Risks include invalid calendar fields, timezone sign errors, unspecified offset interpretation, no leap-second handling, and lossy nanosecond conversion. Test signals include timestamps with explicit positive/negative offsets, unspecified offsets, bogus sub-second fields, pre-1970 or far-future years supported by `time64`, and LVID close timestamp updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/udftime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/unicode.c -->
# sources/distributed-fs/ceph-client/fs/udf/unicode.c

## Purpose
`unicode.c` converts between UDF OSTA Compressed Unicode CS0 and Linux filenames, with UTF-8/NLS support, surrogate handling, illegal-character replacement, and CRC-based name mangling for uniqueness after truncation or translation.

## Important APIs, types, and functions
Public APIs are `udf_dstrCS0toChar`, `udf_get_filename`, and `udf_put_filename`. Internal helpers include `get_utf16_char`, `udf_name_conv_char`, `udf_name_from_CS0`, and `udf_name_to_CS0`. It uses constants for Unicode planes, surrogate masks, illegal mark `_`, extension mark `.`, CRC mark `#`, and five-character CRC suffixes.

## Control flow
CS0-to-host conversion validates compression id 8 or 16, decodes one- or two-byte UTF-16 units including surrogate pairs, optionally translates `/` and invalid characters to `_`, tracks whether CRC mangling is needed, preserves a short extension when possible, and appends `#XXXX` from `crc_itu_t` when names are truncated, illegal, or become `.`/`..`. Host-to-CS0 conversion uses the configured NLS `char2uni` or UTF-8 decoder, starts in 8-bit compression, retries with 16-bit compression when needed, and emits surrogate pairs for codepoints above BMP.

## State and persistence
No private state exists. The file translates persistent FID and volume dstring names into VFS names and writes newly created names back into FIDs.

## Dependencies and integration points
It depends on `UDF_SB(sb)->s_nls_map`, kernel UTF-8 helpers, NLS callbacks, CRC helpers, and name length constants from `udfdecl.h`. `namei.c`, `symlink.c`, and `super.c` are primary consumers.

## Risks and test signals
Risks include name collisions after mangling, truncation around multibyte output, malformed surrogate pairs, NLS conversion failures, and incorrect dstring length handling. Test signals include ASCII, BMP, non-BMP, invalid UTF-8, invalid CS0 compression ids, odd CS0 byte lengths, names containing `/`, names mapping to `.` or `..`, long extensions, and non-UTF8 `iocharset`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/udf/unicode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ufs/Kconfig -->
# sources/distributed-fs/ceph-client/fs/ufs/Kconfig

## Purpose
`Kconfig` exposes Linux UFS filesystem build options: core UFS support, experimental write support, and debug logging.

## Important APIs, types, and functions
It defines `CONFIG_UFS_FS` as a tristate depending on `BLOCK` and selecting `BUFFER_HEAD`, `CONFIG_UFS_FS_WRITE` as a dangerous write-support boolean depending on UFS, and `CONFIG_UFS_DEBUG` as a debug-message boolean.

## Control flow
The file participates in kernel configuration rather than runtime code. Selecting UFS builds the module or builtin object; write support enables mutation paths elsewhere in the filesystem; debug support feeds the Makefile's `-DDEBUG`.

## State and persistence
No runtime state exists. The choices determine whether UFS code can be loaded and whether write paths that mutate inode, directory, cylinder group, and bitmap metadata are compiled or reachable.

## Dependencies and integration points
It integrates with kbuild, `fs/ufs/Makefile`, buffer-head infrastructure, and admin documentation for UFS mount behavior.

## Risks and test signals
Risks are user misunderstanding of read-only versus write-capable UFS, especially because UFS2 is documented as read-only supported while write support is marked dangerous. Test signals include build coverage for `n`, `m`, and `y`, builds with write support disabled/enabled, and debug builds verifying `UFSD` logging compiles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ufs/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ufs/Makefile -->
# sources/distributed-fs/ceph-client/fs/ufs/Makefile

## Purpose
`Makefile` defines the UFS filesystem kbuild object composition and debug compiler flag.

## Important APIs, types, and functions
It builds `ufs.o` when `CONFIG_UFS_FS` is enabled and composes it from `balloc.o`, `cylinder.o`, `dir.o`, `file.o`, `ialloc.o`, `inode.o`, `namei.o`, `super.o`, and `util.o`. It adds `-DDEBUG` when `CONFIG_UFS_DEBUG` is enabled.

## Control flow
There is no runtime control flow. Kbuild links all listed objects into one filesystem module/builtin, so symbols declared in `ufs.h` and `util.h` resolve across these compilation units.

## State and persistence
No filesystem state is held here. The object list determines which code participates in UFS mount, directory, inode, allocation, and utility behavior.

## Dependencies and integration points
It is driven by `Kconfig` and integrates UFS with the kernel's filesystem build. Missing an object would break symbol resolution or silently drop functionality.

## Risks and test signals
Risks include object-list drift when new UFS files are added, and debug macro behavior changing only under `CONFIG_UFS_DEBUG`. Test signals are allmodconfig/build-only checks, module link verification, and debug/non-debug compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ufs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ufs/balloc.c -->
# sources/distributed-fs/ceph-client/fs/ufs/balloc.c

## Purpose
`balloc.c` implements UFS fragment and block allocation/freeing, including cylinder-group bitmap updates, fragment accounting, cluster accounting, partial-fragment growth, page-cache block-number migration, and free-space search heuristics.

## Important APIs, types, and functions
Public functions are `ufs_free_fragments`, `ufs_free_blocks`, and `ufs_new_fragments`. Key internals are `adjust_free_blocks`, `ufs_change_blocknr`, `ufs_clear_frags`, `try_add_frags`, `ufs_add_fragments`, `ufs_alloc_fragments`, `ufs_alloccg_block`, `ubh_scanc`, `ufs_bitmap_search`, `ufs_clusteracct`, and fragment search tables.

## Control flow
Free paths lock `s_lock`, locate the cylinder group, validate magic and bit state, set free bits, update fragment/block summaries, mark super/cylinder buffers dirty, and optionally sync. Allocation first enforces root-reserved space, chooses a preferred cylinder group from goal or parent inode, tries direct allocation in that group, then quadratic and linear fallback. Partial tail growth first tries adjacent fragments; if unavailable, it allocates a new block/fragment run, moves dirty page-cache buffer mappings from old blocks to new blocks, frees old fragments, and updates inode block pointers under `meta_lock`.

## State and persistence
Persistent state includes UFS free bitmaps, cylinder group summaries, superblock summary totals, inode `i_blocks`, inode block pointers, allocation rotors, cluster summaries, and dirty superblock state. Runtime state includes page-cache buffer mappings and allocation goals.

## Dependencies and integration points
It depends on `ufs_load_cylinder`, `util.h` bitmap/endian helpers, `UFS_I(inode)->meta_lock`, buffer-head I/O, capabilities for reserved blocks, and inode mapping operations in `inode.c`.

## Risks and test signals
Risks include bitmap/summary counter divergence, incorrect fragment reassembly, 32-bit `i_blocks` overflow guarded by `try_add_frags`, page-cache aliasing during block moves, and weak coverage because write support is experimental. Test signals include allocating direct and indirect blocks, growing short tails, ENOSPC with/without `CAP_SYS_RESOURCE`, freeing whole blocks across cylinder group boundaries, synchronous mounts, and fsck comparison after write workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ufs/balloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ufs/cylinder.c -->
# sources/distributed-fs/ceph-client/fs/ufs/cylinder.c

## Purpose
`cylinder.c` caches and loads UFS cylinder group metadata. It provides an LRU-like cache of cylinder group private info and buffer-head arrays used by allocation and inode code.

## Important APIs, types, and functions
Public functions are `ufs_put_cylinder` and `ufs_load_cylinder`; `ufs_read_cylinder` is internal. State lives in `struct ufs_sb_info` arrays `s_ucg`, `s_ucpi`, `s_cgno`, and `s_cg_loaded`, and in `struct ufs_cg_private_info`.

## Control flow
Reading a cylinder group fills an already allocated `ufs_cg_private_info`, attaches the first preloaded cylinder-group buffer plus any additional fragments, caches offsets such as inode bitmap, free bitmap, cluster summary, and rotors, then records the cache slot's cylinder number. Loading first checks slot 0, then direct-index mode when total groups fit in cache, otherwise searches loaded slots, promotes hits to slot 0, or evicts the least-recent slot with `ufs_put_cylinder` before reading the requested group.

## State and persistence
Runtime cache state stores buffer heads and decoded offsets/rotors. `ufs_put_cylinder` writes rotor fields back into the cylinder group buffer and marks it dirty, so allocation search position can persist.

## Dependencies and integration points
It depends on UFS superblock-private geometry, `ubh` buffer abstractions, cylinder group magic validation by callers, and block I/O. `balloc.c` and `ialloc.c` are primary consumers.

## Risks and test signals
Risks include stale buffer-head pointers after eviction, wrong cache promotion with many cylinder groups, failure cleanup leaking buffer references, and rotor updates being persisted unexpectedly late. Test signals include filesystems with fewer and more than `UFS_MAX_GROUP_LOADED` groups, repeated allocation across many groups, forced read failures of later cylinder group fragments, and unmount dirty-buffer checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ufs/cylinder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ufs/dir.c -->
# sources/distributed-fs/ceph-client/fs/ufs/dir.c

## Purpose
`dir.c` implements UFS directory pagecache handling, validation, lookup, add/delete/set-link operations, `.`/`..` initialization, emptiness checks, readdir, and directory file operations.

## Important APIs, types, and functions
Public functions include `ufs_inode_by_name`, `ufs_set_link`, `ufs_dotdot`, `ufs_find_entry`, `ufs_add_link`, `ufs_delete_entry`, `ufs_make_empty`, and `ufs_empty_dir`. Exported `ufs_dir_operations` supplies open/release/read/iterate/fsync/llseek/setlease. Important internals are `ufs_match`, `ufs_commit_chunk`, `ufs_handle_dirsync`, `ufs_check_folio`, `ufs_get_folio`, `ufs_last_byte`, `ufs_next_entry`, `ufs_validate_entry`, and `ufs_readdir`.

## Control flow
Directory reads map folios through `ufs_get_folio`, validate record lengths, alignment, chunk boundaries, names, and inode ranges once per folio, then iterate records. Lookup begins at a cached page index and wraps around. Adding a link scans existing and one-past-end folios, splits reusable records when needed, prepares block-backed chunks, writes the new dirent, commits size/version changes, updates times, and syncs if required. Deletion merges with the previous record when possible and clears the inode number. Readdir revalidates offsets after directory version changes.

## State and persistence
Persistent state includes directory entry records, `d_ino`, record lengths, name length/type fields, directory size, ctime/mtime, and block contents. Runtime state includes folio checked bits, per-open i_version cookie, and `i_dir_start_lookup`.

## Dependencies and integration points
It depends on `ufs_prepare_chunk` from `inode.c`, endian/name helpers in `util.h`, VFS folio and dir_context APIs, and namei operations in `ufs/namei.c`.

## Risks and test signals
Risks include accepting corrupt directories, record splitting/merging bugs, offset revalidation errors after mutation, missing kmap release on error paths, and old versus 4.4BSD dirent format differences. Test signals include fsck-corrupted dirents, create/delete/rename loops, readdir during mutation, directory sync mounts, max-length names, old UFS dir format and 44BSD d_type format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ufs/dir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ufs/file.c -->
# sources/distributed-fs/ceph-client/fs/ufs/file.c

## Purpose
`file.c` provides the regular-file `file_operations` table for UFS, delegating actual I/O and mapping behavior to generic VFS helpers and UFS address-space operations.

## Important APIs, types, and functions
The only exported object is `ufs_file_operations`. It wires `generic_file_llseek`, `generic_file_read_iter`, `generic_file_write_iter`, `generic_file_mmap_prepare`, `generic_file_open`, `simple_fsync`, `filemap_splice_read`, `iter_file_splice_write`, and `generic_setlease`.

## Control flow
There is no custom file-level control flow. VFS calls on regular files flow through generic helpers; block mapping, write_begin/write_end, truncation, and persistence semantics are handled by `inode.c` through `ufs_aops` and inode operations.

## State and persistence
The file stores no state. Reads and writes mutate pagecache and on-disk blocks through generic helpers and UFS address-space callbacks.

## Dependencies and integration points
It depends on the VFS generic file API and is selected by `ufs_set_inode_ops` for regular files. Correct behavior depends on `ufs_aops`, `ufs_setattr`, and superblock mount flags.

## Risks and test signals
Risks are mostly integration risks: generic write paths may reach experimental UFS allocation code when write support is enabled, and `simple_fsync` relies on lower layers marking buffers/inodes correctly. Test signals include buffered read/write, mmap prepare, splice read/write, fsync, file leases, and behavior on read-only mounts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ufs/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ufs/ialloc.c -->
# sources/distributed-fs/ceph-client/fs/ufs/ialloc.c

## Purpose
`ialloc.c` implements UFS inode allocation and freeing, including inode bitmap updates, cylinder group/free summary counters, UFS2 lazy inode chunk initialization, and new in-core inode initialization.

## Important APIs, types, and functions
Public functions are `ufs_free_inode` and `ufs_new_inode`; internal `ufs2_init_inodes_chunk` zeroes newly initialized UFS2 inode blocks and advances `cg_initediblk`.

## Control flow
Freeing locks `s_lock`, validates inode range, loads the containing cylinder group, verifies bitmap state, clears the inode-used bit, updates free inode and directory counters, writes rotors/summaries dirty, and optionally syncs. Allocation rejects deleted parent directories, allocates a VFS inode, then searches the parent cylinder group, quadratic fallback groups, and linear fallback groups for free inodes. It sets the bitmap bit, initializes UFS2 inode disk chunks when the chosen bit is beyond initialized inode blocks, updates counters, assigns inode number, owner, timestamps, flags, and UFS private fields, inserts the inode into the hash, marks it dirty, and for UFS2 writes birthtime directly to disk.

## State and persistence
Persistent state includes inode-used bitmaps, cylinder group counters, superblock summary totals, UFS2 initialized inode block marker, birthtime fields, and new inode records on writeback. Runtime state includes newly allocated `struct inode` and `ufs_inode_info`.

## Dependencies and integration points
It depends on `ufs_load_cylinder`, bitmap helpers, endian helpers, `insert_inode_locked`, `inode_init_owner`, and `ufs_mark_sb_dirty`. `namei.c` calls `ufs_new_inode`; `ufs_evict_inode` calls `ufs_free_inode`.

## Risks and test signals
Risks include alias races if free ordering changes, counter drift on failure after bitmap set, UFS2 chunk zeroing errors, directory counter mismatches, and inode range boundary mistakes. Test signals include create/unlink stress, directory creation/removal, allocation after deleted parent, UFS2 new inode birthtime, ENOSPC on inode exhaustion, and fsck validation of inode bitmaps/counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ufs/ialloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ufs/inode.c -->
# sources/distributed-fs/ceph-client/fs/ufs/inode.c

## Purpose
`inode.c` implements UFS block mapping, address-space operations, inode read/writeback for UFS1 and UFS2, eviction, truncation, and setattr. It is the bridge between VFS pagecache I/O and UFS direct/indirect fragment allocation.

## Important APIs, types, and functions
Exported objects/functions are `ufs_aops`, `ufs_prepare_chunk`, `ufs_iget`, `ufs_write_inode`, `ufs_sync_inode`, `ufs_evict_inode`, `ufs_setattr`, and `ufs_file_inode_operations`. Key internals include `ufs_block_to_path`, `ufs_frag_map`, `ufs_extend_tail`, `ufs_inode_getfrag`, `ufs_inode_getblock`, `ufs_getfrag_block`, `ufs_set_inode_ops`, `ufs1_read_inode`, `ufs2_read_inode`, `ufs1_update_inode`, `ufs2_update_inode`, `ufs_update_inode`, `ufs_trunc_direct`, `free_full_branch`, `free_branch_tail`, `ufs_alloc_lastblock`, `ufs_truncate_blocks`, and `ufs_truncate`.

## Control flow
Read mapping computes a direct/single/double/triple-indirect path, follows pointers under `meta_lock` sequence protection, and maps physical fragments. Write mapping serializes creation with `truncate_mutex`, extends short direct tails when needed, allocates direct or indirect fragment runs via `ufs_new_fragments`, marks new buffers, and updates inode dirty state. Address-space operations call these paths for read folio, writepages, write begin/end, and bmap.

Inode read validates inode number, reads the inode block, decodes UFS1 or UFS2 fields, copies block pointers or fast symlink data, initializes last-fragment and ops. Writeback encodes inode fields back, clearing deleted inodes. Eviction truncates data for unlinked files, writes the cleared inode, then frees the inode bitmap. Truncation allocates the final partial block if needed, truncates pagecache, frees direct and indirect branches beyond EOF, updates `i_lastfrag`, times, and dirty state.

## State and persistence
Persistent state includes inode mode/link/uid/gid/size/times/blocks/generation/flags, direct and indirect block pointers, fast symlink bytes, device numbers, allocated fragments, and freed branch blocks. Runtime state includes `i_lastfrag`, `i_dir_start_lookup`, `meta_lock`, `truncate_mutex`, pagecache buffers, and mapping ops.

## Dependencies and integration points
It depends on `balloc.c` for block allocation/freeing, `util.h` for pointer/endian/device helpers, `dir.c` for directory chunk preparation, `file.c` operations, namei operation tables, buffer-head/pagecache APIs, and UFS superblock geometry/format flags.

## Risks and test signals
Risks include direct/indirect path arithmetic overflow, stale reads during concurrent pointer updates, tail-fragment growth and relocation bugs, missing `s_sbbase` in read/write asymmetry, truncation leaks or double frees, UFS1/UFS2 field mismatch, and fast-symlink versus block-backed symlink confusion. Test signals include sparse reads, direct/single/double/triple indirect writes, truncate up/down at fragment and block boundaries, fast and long symlinks, UFS1/UFS2 inode round trips, eviction of unlinked open files, and fsck after write/truncate workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ufs/inode.c -->
