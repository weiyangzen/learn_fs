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
