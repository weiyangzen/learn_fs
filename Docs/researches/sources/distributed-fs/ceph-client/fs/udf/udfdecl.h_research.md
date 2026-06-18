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
