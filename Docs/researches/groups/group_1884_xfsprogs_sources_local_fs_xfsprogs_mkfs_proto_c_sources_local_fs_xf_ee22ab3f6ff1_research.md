# Group Research: group_1884_xfsprogs_sources_local_fs_xfsprogs_mkfs_proto_c_sources_local_fs_xf_ee22ab3f6ff1

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/local-fs/xfsprogs`, which is included in subset A.

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/mkfs/proto.c -->
# File Research: sources/local-fs/xfsprogs/mkfs/proto.c

## Purpose
Implements `mkfs.xfs` filesystem population from either a legacy protofile or a source directory tree. It creates the root inode, optional metadata directory, realtime metadata inodes, regular files, directories, symlinks, special files, xattrs, parent pointers, and inherited root fsxattr settings.

## Key Elements
`setup_proto` classifies no input as a default root-directory protofile, regular input as an in-memory protofile, and directory input as `PROTO_SRC_DIR`. `parse_proto` dispatches to proto parsing or directory traversal and applies `slashes_are_spaces` and `preserve_atime`.

Protofile parsing uses `getstr`, `getnum`, `parseproto`, and type format strings for regular, reserved/preallocated, block, char, directory, symlink, and FIFO entries. It creates inodes through `creatproto`, links them with `newdirent`, and writes file data and xattrs after committing the initial inode/link transaction.

Directory population uses `populate_from_dir`, `walk_dir`, `handle_direntry`, `create_directory_inode`, and `create_nondir_inode`. It preserves uid/gid, mode, mtime, optional atime, file contents, xattrs, fsxattr-derived inode flags, and hardlinks via a growable source-inode to destination-inode tracker.

Realtime initialization is split across non-rtgroup and rtgroup paths. It creates rt bitmap/summary or rtgroup metadata inodes and frees realtime extents into the allocator, with special handling for realtime superblock and zoned filesystems.

## Dependencies
Depends heavily on libxfs transaction, inode, directory, symlink, xattr, realtime, parent-pointer, and allocation APIs. Also uses POSIX directory/stat/open/read/lseek/xattr/resource APIs and Linux xattr constants.

## Behavior/Risks
File data copying preserves sparse holes with `SEEK_DATA`/`SEEK_HOLE` and rounds data ranges to filesystem block boundaries to avoid partial-block corruption. Realtime regular-file creation from protofile content is rejected.

Directory-tree mode supports sockets as XFS directory entries but does not copy socket payloads. Hardlink tracking is keyed by source inode number only, so unusual traversals across multiple source devices with colliding inode numbers could misidentify hardlinks. Protofile names are tokenized by whitespace unless `slashes_are_spaces` rewrites slash characters in entry names.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/mkfs/proto.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/mkfs/proto.h -->
# File Research: sources/local-fs/xfsprogs/mkfs/proto.h

## Purpose
Declares the mkfs protofile/directory population interface used by `xfs_mkfs.c`.

## Key Elements
Defines `enum proto_source_type` with `PROTO_SRC_NONE`, `PROTO_SRC_PROTOFILE`, and `PROTO_SRC_DIR`, plus `struct proto_source` carrying source type and associated string data.

Exports `setup_proto`, `parse_proto`, and `res_failed`.

## Dependencies
Uses `struct xfs_mount` and `struct fsxattr` from the surrounding xfsprogs/libxfs headers included by callers.

## Behavior/Risks
The API abstracts protofile and directory inputs behind a single `proto_source`, letting the mkfs main path defer root population until after devices, AG headers, and free-space metadata are initialized.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/mkfs/proto.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/mkfs/xfs_mkfs.c -->
# File Research: sources/local-fs/xfsprogs/mkfs/xfs_mkfs.c

## Purpose
Main implementation of `mkfs.xfs`. It parses CLI and config-file options, validates feature and geometry combinations, initializes devices and on-disk metadata, populates the root filesystem, and marks the new XFS filesystem complete.

## Key Elements
The file uses table-driven option definitions for block, config, data, inode, log, naming, proto, realtime, sector, and metadata options. Each option table records suboption names, INI section names, conflicts, range checks, unit conversion behavior, power-of-two requirements, and defaults.

Parsing flows through `parse_subopts`, option-family parser functions, and optional INI parsing via `ini_parse`. `cli_params` stores user input and delayed string conversions; `mkfs_params` stores validated/calculated filesystem geometry; `mkfs_default_params` stores build-time defaults.

Validation covers device type and overwrite checks, block/sector/log sector sizes, zoned topology, feature dependencies, directory and inode sizes, realtime extent size, data/log/realtime device sizes, stripe factors, allocation group geometry, realtime group or zone geometry, max inode percentage, atomic-write limits, log sizing/alignment, extent-size hints, and support policy.

Feature policy enforces CRC-v5 requirements for modern features, emits deprecation warnings for V4 and ascii-ci formats, auto-enables or disables features for autofsck, realtime, metadir, parent pointers, exchange-range, persistent quota flags, reflink, zoned mode, and atomic writes.

The creation path discards or resets devices when requested, initializes libxfs buffer targets, clears stale filesystem signatures and old XFS secondary superblocks, writes the bootstrap superblock and cleared log, mounts through libxfs, initializes AG headers and AGFL free space, creates realtime superblock if needed, calls `setup_proto`/`parse_proto`, checks root inode placement, verifies realtime metadata preallocation, rewrites selected secondary superblocks with root/metadir inode numbers, sets autofsck fs property, clears `sb_inprogress`, unmounts, and destroys libxfs state.

## Dependencies
Depends on libxfs, libxcmd, libfrog geometry/conversion/properties/zones/hash self-tests, Linux block/zoned ioctls, INI parser support, and `mkfs/proto.h`.

## Behavior/Risks
The file is the policy center for mkfs; small changes can affect on-disk format defaults, kernel compatibility, repair assumptions, and performance geometry. `check_root_ino` intentionally fails formatting if root inode placement diverges from xfs_repair expectations. Dry-run mode prints geometry before writing. CRC32C and dir/attr hash self-tests gate actual filesystem creation.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/mkfs/xfs_mkfs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/mkfs/xfs_protofile.py.in -->
# File Research: sources/local-fs/xfsprogs/mkfs/xfs_protofile.py.in

## Purpose
Generates a mkfs.xfs protofile from one or more source directory trees.

## Key Elements
Emits the legacy protofile header `/` and `0 0`, then either emits a minimal empty root directory or walks supplied directories recursively. `stat_to_str` converts file type, suid/sgid bits, mode, uid, and gid into protofile format. `stat_to_extra` emits regular-file source path, device major/minor, or symlink target.

`walk_tree` separates files and directories, skips sockets, rejects names containing spaces, aligns file-name columns, emits files before directories, recursively descends subdirectories, and emits `$` directory terminators.

## Dependencies
Uses Python `os`, `argparse`, `sys`, `stat`, gettext substitution via `@INIT_GETTEXT@`, and build-time `@pkg_version@`.

## Behavior/Risks
Generated protofiles cannot represent filenames containing spaces because mkfs protofile parsing is whitespace-tokenized. Socket files are ignored. There is a likely error path bug: when the first supplied path is not a directory, `raise NotADirectoryError(path)` references `path` before the loop assigns it.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/mkfs/xfs_protofile.py.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/Makefile -->
# File Research: sources/local-fs/xfsprogs/repair/Makefile

## Purpose
Builds and installs the `xfs_repair` command and enumerates repair subsystem sources and headers.

## Key Elements
Sets `TOPDIR`, includes build definitions/rules, defines `LTCOMMAND = xfs_repair`, lists repair headers and C files, links against libxfs, libxlog, libxcmd, libfrog, uuid, rt, blkid, urcu, and pthread, and uses `-static-libtool-libs`.

Defines `default: depend $(LTCOMMAND)`, a `globals.o` header dependency, install target for `$(PKG_SBIN_DIR)`, and commented tracing flag names for inode, directory, duplicate extent, btree build, parent pointer, and prefetch debugging.

## Dependencies
Depends on xfsprogs top-level build system variables and `$(BUILDRULES)`.

## Behavior/Risks
The source list makes repair composition explicit; adding repair modules requires updating this file so they are compiled and linked into `xfs_repair`.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/agbtree.c -->
# File Research: sources/local-fs/xfsprogs/repair/agbtree.c

## Purpose
Rebuilds per-allocation-group btrees during xfs_repair phase work using libxfs bulk-loading infrastructure.

## Key Elements
`bt_rebuild` contexts are initialized by `init_rebuild`, which sets up fake-root bulkload state and geometry slack. `reserve_agblocks` consumes smallest free extents from repair’s in-memory bno/bcnt trees, reserves them for rebuilt btrees, adds rmap records for the reservations, and updates free-space trees.

Free-space btree rebuild initializes bnobt and cntbt cursors, iteratively computes geometry because reservations change free-space records, leaves enough extra blocks for AGFL setup, and bulk-loads records from in-memory extent trees.

Inode btree rebuild computes inode/free-inode totals, handles sparse inode holemask conversion, builds inobt and optionally finobt, and tracks first agino/count/freecount in rebuild state.

Rmap and refcount rebuilds are feature-gated by `xfs_has_rmapbt` and `xfs_has_reflink`, respectively. They feed records from repair rmap cursors or refcount slab cursors into libxfs bulk loaders.

`finish_rebuild` marks unused reserved blocks as lost blocks before committing reservations. `estimate_agbtree_blocks` estimates allocbt, inobt/finobt, rmapbt, and refcountbt block needs.

## Dependencies
Depends on libxfs btree/bulkload APIs, repair in-core extent/inode/rmap/refcount structures, `bulkload.h`, `incore.h`, `rmap.h`, `slab.h`, and libfrog bitmap utilities.

## Behavior/Risks
This code mutates repair’s in-memory free-space records while reserving blocks for new metadata, so ordering matters. It intentionally does not commit btree cursors when AGF/AGI headers have not yet been written. Reservation shortfalls are fatal because repaired metadata cannot be safely written without space for the rebuilt trees and AGFL.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/agbtree.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/agbtree.h -->
# File Research: sources/local-fs/xfsprogs/repair/agbtree.h

## Purpose
Declares shared repair structures and functions for rebuilding per-AG btrees.

## Key Elements
Defines `struct bt_rebuild`, containing a `bulkload` fake-root/reservation context, `xfs_btree_bload` geometry, staged cursor, and a union of tree-specific cursors/state for free-space, inode, rmap, and refcount rebuilds.

Declares initialization and build functions for free-space btrees, inode btrees, rmapbt, and refcountbt, plus `finish_rebuild` and `estimate_agbtree_blocks`.

## Dependencies
Requires repair bulkload structures, xfs btree cursor types, slab cursors, in-core extent and inode tree nodes, and libfrog bitmap.

## Behavior/Risks
The union makes the rebuild context compact but tree-specific fields must only be used by the matching init/build path. Callers are responsible for sequencing init, bulk-load build, header update, and finish/cleanup correctly.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/agbtree.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/agheader.c -->
# File Research: sources/local-fs/xfsprogs/repair/agheader.c

## Purpose
Verifies and repairs allocation group headers: AG superblocks, AGF, and AGI.

## Key Elements
`verify_set_agf` checks AGF magic, version, sequence number, length, freelist indexes, and v5 UUID, repairing fields unless `no_modify` is set. `verify_set_agi` does analogous checks for AGI magic, version, sequence, length, and UUID.

`compare_sb` compares geometry from a candidate superblock to the mounted primary superblock, ignoring transient/counter fields. `check_v5_feature_mismatch` synchronizes secondary v5 feature fields with the primary, with special handling for `NEEDSREPAIR` and log-incompat feature semantics.

`secondary_sb_whack` determines the valid on-disk superblock field extent for the feature set, zeros garbage beyond it, clears invalid flags, handles quota or metadir-era inode fields, normalizes alignment/stripe/sector fields when feature bits do not justify them, and clears secondary `needsrepair`.

`verify_set_agheader` runs superblock verification/comparison, resets a bad superblock from the primary geometry when repair is allowed, sanitizes secondary-super fields, then verifies AGF and AGI.

## Dependencies
Depends on libxfs superblock/AG structures and feature helpers, repair globals such as `no_modify` and `features_changed`, warning/error helpers, and `agheader.h` geometry structures.

## Behavior/Risks
The code is intentionally conservative around primary-vs-secondary differences because older mkfs and growfs behavior can leave valid historical variations. Return bits identify which AG structures were changed so callers can decide what to write and report.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/agheader.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/repair/agheader.h -->
# File Research: sources/local-fs/xfsprogs/repair/agheader.h

## Purpose
Defines repair-side filesystem geometry comparison structures and AG header modification flags.

## Key Elements
`fs_geometry_t` mirrors key superblock geometry and feature fields used to compare candidate superblocks. It separates fields that must match automatically from fields requiring manual checks or historical tolerance.

`fs_geo_list_t` tracks geometry variants and reference counts. Defines `XR_SB_COUNTERS`, `XR_SB_INOALIGN`, and `XR_SB_SALIGN` for last-nonzero superblock field tracking, plus `XR_AG_SB`, `XR_AG_AGF`, `XR_AG_AGI`, and `XR_AG_SB_SEC` modification bits.

Provides a local inline `xfs_sb_version_hasmetadir` helper for v5 metadir feature detection from an `xfs_sb`.

## Dependencies
Uses XFS scalar types and `struct xfs_sb` feature constants from libxfs headers.

## Behavior/Risks
The geometry layout is used with `memcmp` up to `sb_shared_vn`, so field ordering is part of the comparison contract. Adding or reclassifying superblock fields requires care to preserve repair’s primary/secondary comparison semantics.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/repair/agheader.h -->