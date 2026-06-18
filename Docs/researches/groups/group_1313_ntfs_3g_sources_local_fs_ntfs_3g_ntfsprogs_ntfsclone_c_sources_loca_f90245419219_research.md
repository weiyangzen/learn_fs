# Group Research: ntfs-3g ntfsprogs utilities

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/local-fs/ntfs-3g`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsclone.c -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsclone.c

## Role

Implements `ntfsclone`, a user-space NTFS cloning, imaging, restore, rescue, and metadata-only sanitization utility. It can clone used clusters to sparse files/devices/stdout, save/restore a compact special image format, rescue unreadable sectors, generate new volume serial numbers, adjust boot-sector sector-size fields, and create metadata-only images with optional timestamp/data wiping.

## Main Areas

- Option parsing validates mutually exclusive clone/restore/save-image/metadata/no-action/stdout combinations.
- Special image format handling defines the `\0ntfsclone-image` header, version 10.1, endian-safe fields, and command stream opcodes `CMD_GAP` and `CMD_NEXT`.
- I/O wrappers `io_all()`, `copy_cluster()`, `read_rescue()`, and `rescue_sector()` abstract device/file/stdin/stdout/image I/O and bad-sector rescue.
- Cluster discovery walks all in-use MFT records and attributes, decompresses mapping pairs, builds an internal LCN bitmap, and compares it with `$Bitmap`.
- Clone/restore paths use the bitmap or image command stream to copy allocated clusters and preserve gaps.
- Metadata mode identifies critical metadata clusters, handles `$LogFile` specially, includes the alternate boot sector, and can copy only selected metadata.
- Wiping mode clears resident user data, deleted/unused MFT record data, file-name/standard-information timestamps, directory index timestamps, and quota timestamps unless preservation is requested.
- Output setup handles sparse-file sizing, block-device size validation, free-space checks, sync, Windows-specific device output, and optional post-clone sector-size adjustment.

## Dependencies

Uses libntfs-3g volume, inode, attribute, bitmap, runlist, MST, boot sector, directory/index, timestamp, device, and utility APIs. It depends heavily on `ntfs_mount()`, `ntfs_inode_open()`, `ntfs_attrs_walk()`, `ntfs_mapping_pairs_decompress()`, `$Bitmap` reads, `ntfs_attr_pread()`, `ntfs_rl_pwrite()`, and MST fixup helpers.

## Important Behavior

The core correctness check is `compare_bitmaps()`: clusters discovered by walking metadata are compared against `$Bitmap`, and mismatches abort unless `--ignore-fs-check` is allowed for rescue/metadata situations. Bad clusters from `$BadClus` can be removed from the copy set.

The metadata-image path has two passes: first it computes metadata cluster usage, then it sets `wipe = 1` and emits wiped metadata records/clusters. MFT and `$I30` index allocations get record-level wiping so logical records spanning clusters are handled coherently.

The code intentionally preserves update sequence numbers when writing modified MFT records via `ntfs_mft_usn_dec()` before write/pre-write fixup. Restore validates image opcodes and bounds, and rejects metadata images to stdout when negative/invalid gaps imply non-linear placement.

## Research Notes

This is one of the highest-risk utilities in the group because it mixes filesystem metadata walking, raw cluster copying, image serialization, rescue reads, and direct metadata sanitization. The source also contains an endianness FIXME and special compatibility handling for pre-10.0 images.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsclone.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfscluster.8.in -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfscluster.8.in

## Role

Manual page for `ntfscluster`, describing it as a tool for identifying files occupying a specified sector or cluster range on an NTFS volume.

## Documented Interface

Documents `--cluster`, `--sector`, `--inode`, `--filename`, `--force`, `--quiet`, `--verbose`, `--version`, and `--help`. It explains range-based cluster/sector lookup and file/inode inspection.

## Important Behavior

The manpage says `info` mode is not implemented, but the current `ntfscluster.c` does implement `info()` and prints volume, MFT, free-space, user-data, and metadata statistics.

## Research Notes

The page is useful for command-line semantics but slightly stale relative to implementation.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfscluster.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfscluster.c -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfscluster.c

## Role

Implements `ntfscluster`, a read-only inspection utility that finds the owner of a cluster/sector range or dumps runlists for a file/inode.

## Main Functions

- `parse_options()` selects exactly one action: info, cluster range, sector range, inode, filename, or last.
- `info()` walks MFT records and non-resident attributes to compute metadata, user-data, and free-space statistics.
- `dump_file()` prints all attributes of an inode and runlists for non-resident attributes.
- `print_match()` is the `cluster_find()` callback that prints inode and attribute names for range matches.
- `find_last()` is a callback for locating the file with the highest referenced LCN.
- `main()` mounts the volume read-only, dispatches the selected action, and unmounts.

## Dependencies

Uses `ntfscluster.h`, libntfs-3g volume, directory/pathname, attribute, cluster, runlist, MFT search, and logging helpers.

## Important Behavior

Sector ranges are converted to cluster ranges by shifting with `cluster_size_bits - sector_size_bits`. `--force` maps to `NTFS_MNT_RECOVER`; otherwise the volume is mounted read-only without recovery. File lookup uses `ntfs_pathname_to_inode()` and Windows builds translate paths first.

## Research Notes

The tool is a thin front end over libntfs-3g’s MFT and cluster scanning helpers. Its output is diagnostic and it does not modify the filesystem.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfscluster.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfscluster.h -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfscluster.h

## Role

Shared declarations for `ntfscluster.c`.

## Main Definitions

- `enum action` names supported command actions: info, cluster, sector, inode, file, last, and error.
- `struct options` stores parsed CLI state, target device, range, filename, inode, and verbosity/force flags.
- `struct match` stores inode, LCN, attribute type/name, and name length for cluster-match tracking.

## Dependencies

Includes NTFS basic types and layout definitions.

## Research Notes

The header is local to the `ntfscluster` utility and has no cross-tool API surface.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfscluster.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfscmp.8.in -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfscmp.8.in

## Role

Manual page for `ntfscmp`, a utility for comparing two NTFS filesystems or image files.

## Documented Interface

Documents `--no-progress-bar`, `--verbose`, and `--help`, plus exit status. It positions the utility primarily as a development/verification tool for identifying metadata differences.

## Important Behavior

The page recommends comparing metadata images produced by `ntfsclone --metadata` when ordinary timestamp churn is not interesting.

## Research Notes

The manpage matches the implementation’s terse difference reporting and progress-bar behavior.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfscmp.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfscmp.c -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfscmp.c

## Role

Implements `ntfscmp`, a read-only NTFS volume comparator that walks MFT records and compares inode open status, attribute presence, attribute headers, and attribute contents.

## Main Functions

- `parse_options()` requires two volumes and configures progress/verbose/debug output.
- `mount_volume()` checks mount state and mounts each volume read-only.
- `cmp_inodes()` iterates MFT record numbers and compares inode open results.
- `cmp_attributes()` walks attributes in type/name order and reports presence, walk errno, or content differences.
- `cmp_attribute()` compares attribute headers, opens matching attributes, checks sizes, and compares data.
- `cmp_attribute_data()` reads both attributes in `NTFS_BUF_SIZE` chunks.
- `cmp_index_allocation()` compares `$INDEX_ALLOCATION` attributes using their associated bitmap and MST-deprotected active index blocks.

## Dependencies

Uses libntfs-3g inode, attribute, MST, utility, and mount helpers via included project headers such as `mst.h`, `support.h`, `utils.h`, and `misc.h`.

## Important Behavior

The output strings are intentionally stable because external tools grep for them. Extension records are skipped as independent inode comparisons and handled through base-inode attribute walking. `$BadClus:$Bad` content comparison is skipped after header differences because mapping pairs already encode differences.

Index allocation comparison is bitmap-aware: inactive index blocks are not compared as live content. Attribute header comparison for non-resident attributes compares the full attribute record length, including padding, which the file comments call out as a FIXME relative to `ntfsinfo`.

## Research Notes

This utility is optimized for exact metadata-difference localization, not human-friendly diff output. It exits on serious read/pathological traversal errors but otherwise prints all detected differences.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfscmp.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfscp.8.in -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfscp.8.in

## Role

Manual page for `ntfscp`, which copies a host file into an NTFS volume.

## Documented Interface

Documents destination by path or inode, optional attribute type/name, `--min-fragments`, `--no-action`, `--force`, `--timestamp`, quiet/verbose, and version/help options. It also explains NTFS named data streams.

## Important Behavior

The manpage notes the unusual case of writing an unnamed data attribute to a directory when the destination is specified by inode number.

## Research Notes

The documentation aligns with the implementation’s file creation, overwrite, named stream, inode-target, and minimal-fragmentation features.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfscp.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfscp.c -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfscp.c

## Role

Implements `ntfscp`, a write utility that copies a local file into an NTFS file or attribute, creating the destination when needed and optionally minimizing fragmentation.

## Main Areas

- `parse_options()` handles device/source/destination, attribute type/name, inode mode, timestamp copy, no-action, force, and verbosity.
- Signal handling records SIGINT/SIGTERM so the copy loop can abort cleanly.
- Minimal-fragmentation allocation scans `$Bitmap`, selects large free runs, sorts them by LCN, assigns a custom runlist, updates mapping pairs, and marks clusters allocated.
- `ntfs_new_file()` wraps Unicode conversion and `ntfs_create()` for regular file creation.
- `main()` mounts the volume, resolves or creates the destination, opens/adds the target attribute, resizes it, writes data with `ntfs_attr_pwrite()`, closes compressed attributes with `ntfs_attr_pclose()`, optionally updates timestamps, and syncs by closing the inode.

## Dependencies

Uses libntfs-3g volume, directory/pathname, inode creation, attribute truncate/write, bitmap, runlist, timestamp, logging, and utility APIs.

## Important Behavior

`--min-fragments` is disabled for compressed attributes. Existing attributes are truncated to zero before minimal-fragmentation preallocation. No-action mounts read-only and skips actual runlist assignment/writes where relevant.

If the destination path resolves to a directory and destination is not inode mode, the source basename is copied into that directory, overwriting an existing same-name file when found. Inode mode treats the destination argument as an MFT reference and can write directly to that inode’s selected attribute.

## Research Notes

The custom preallocator is the highest-risk part: it mutates `$Bitmap`, runlists, mapping pairs, and attribute/inode size fields directly. The normal copy path relies more on libntfs-3g truncate/write helpers.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfscp.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsdecrypt.8.in -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsdecrypt.8.in

## Role

Manual page for `ntfsdecrypt`, a tool for decrypting or updating NTFS EFS-encrypted files from an unmounted NTFS volume.

## Documented Interface

Documents keyfile selection with `--keyfile`, inode or path target selection, `--encrypt` update mode, force, quiet/verbose, version, and help.

## Important Behavior

Explains the two-level EFS scheme: file data is encrypted by a symmetric FEK, and the FEK is encrypted for authorized users/recovery agents in `$LOGGED_UTILITY_STREAM` / `$EFS`. It documents supported symmetric modes as DESX, 3DES, and AES-256.

## Research Notes

The page highlights that encrypted-file backups must include `$LOGGED_UTILITY_STREAM`; otherwise decryption is impossible even with a recovery key.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsdecrypt.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsdecrypt.c -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsdecrypt.c

## Role

Implements `ntfsdecrypt`, which decrypts EFS-encrypted NTFS file contents to stdout or encrypts replacement stdin data back into an already encrypted file while preserving the existing EFS key material.

## Main Areas

- CLI parsing selects keyfile, target file/inode, update/encrypt mode, force, and logging.
- Crypto initialization wires libgcrypt and GnuTLS.
- PKCS#12 loading reads a `.pfx/.p12` file, prompts for its passphrase, verifies MAC, extracts RSA private key parameters, detects EFS certificate purpose OID, and returns the certificate SHA-1 thumbprint.
- RSA FEK decryption reverses raw FEK bytes, converts to libgcrypt MPI/S-expression, decrypts with the private key, removes PKCS#1 padding, and imports the symmetric FEK.
- FEK import supports DESX, 3DES, and AES-256, with DES/unknown algorithms rejected.
- DESX support expands the Windows EFS DESX key using MD5 salts and implements sector encryption/decryption block-by-block.
- `ntfs_inode_fek_get()` reads `$LOGGED_UTILITY_STREAM:$EFS`, chooses DDF or DRF arrays based on certificate purpose, matches thumbprint credentials, and decrypts the matching FEK.
- `ntfs_cat_decrypt()` temporarily clears the encrypted flag and extends readable size to raw allocation so it can read encrypted sectors, decrypt 512-byte sectors, and emit only logical data size.
- `ntfs_feed_encrypt()` truncates the encrypted data stream, reads stdin in 512-byte sectors, pads the last sector with pseudo-random bytes, encrypts each sector, writes raw encrypted data, truncates to logical size, and updates timestamps.

## Dependencies

Uses libgcrypt, GnuTLS PKCS#12/X.509 APIs, and libntfs-3g volume, inode, attribute, directory/pathname, layout/EFS structure, logging, and utility APIs.

## Important Behavior

Decryption mode mounts read-only; encrypt/update mode mounts read-write unless force recovery is requested. Sector IVs are manually XORed because libgcrypt IV handling does not match the AES-256 EFS sector format used here.

The password buffer returned by `getpass()` is zeroed after key extraction. The FEK is decrypted in place within the `$EFS` buffer copy, not on disk.

## Research Notes

This file is crypto-sensitive and format-sensitive. It depends on exact EFS structure offsets, certificate thumbprint matching, RSA parameter conversion between GnuTLS and libgcrypt, and per-sector EFS IV constants.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsdecrypt.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsdump_logfile.c -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsdump_logfile.c

## Role

Implements `ntfsdump_logfile`, a diagnostic utility that reads NTFS `$LogFile` either from a mounted-by-tool volume or from a standalone file copy and dumps interpreted restart/log-record structures.

## Main Functions

- `logfile_open()` opens either an NTFS volume read-only and `$LogFile/$DATA`, or a raw file with `-f`.
- `logfile_pread()` abstracts positioned reads from the NTFS attribute or raw file.
- `restart_header_sanity()` validates restart-page magic, page sizes, version 1.1, update sequence array placement, and restart-area alignment.
- `dump_restart_areas_header()` and `dump_restart_areas_area()` print restart page and client-record fields.
- `dump_restart_areas()` MST-deprotects the two restart pages, skips the second if it matches the first, and aborts on CHKD/BAAD cases.
- `dump_log_record()` prints decoded fields from a single log record.
- `dump_log_records()` walks record pages after the restart pages and prints page and record fields using fixed offsets.
- `main()` caps input to 64 MiB, reads it into memory, validates initial magic, dumps restart pages, then dumps log pages.

## Dependencies

Uses libntfs-3g volume, inode, attribute, logfile layout structures, MST fixups, endian helpers, utilities, and logging.

## Important Behavior

The tool is read-only but aborts on many unsupported/corrupt log states. It treats all-`0xff` data as an uninitialized `$LogFile`. It warns when only the first 64 MiB is analyzed.

Several sanity checks are explicitly TODO: restart-area checking, log-client array checking, richer command-line parsing, and more complete log record handling.

## Research Notes

This is an inspection aid rather than a repair or replay implementation. The parser has hard-coded assumptions such as version 1.1 and a `0x40` log-record start offset.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsdump_logfile.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsfallocate.8.in -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsfallocate.8.in

## Role

Manual page for `ntfsfallocate`, a tool for preallocating space for a file or arbitrary NTFS attribute.

## Documented Interface

Documents mandatory `--length`, optional `--offset`, `--no-size-change`, `--no-action`, `--force`, quiet/verbose/version/help, and advanced attribute type/name parameters.

## Important Behavior

Warns that preallocated unwritten clusters can produce NTFS layouts unsupported by Windows, possibly causing Windows crashes when later writing those clusters. It also documents SI/decimal and IEC/binary suffix parsing for sizes.

## Research Notes

The manpage’s warning matches the source-level warning and the implementation’s direct cluster allocation behavior.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsfallocate.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsfallocate.c -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsfallocate.c

## Role

Implements `ntfsfallocate`, a direct NTFS attribute preallocation tool that fills holes in a requested byte range, optionally extending apparent file size.

## Main Functions

- `parse_options()` parses length/offset with suffixes, device, file, attribute type, attribute name, and mode flags.
- `ntfs_save_rl()` copies the original runlist for rollback.
- `ntfs_restore_rl()` frees newly allocated clusters that overlap holes in the original runlist and restores mapping pairs after errors.
- `ntfs_inner_zero()` zeroes newly allocated clusters that are before initialized size.
- `ntfs_merge_allocation()` merges newly allocated runs into the attribute runlist, updates sparse/compressed-size accounting, and writes mapping pairs.
- `ntfs_inner_allocation()` finds holes overlapping the requested VCN range and allocates clusters with `ntfs_cluster_alloc()`.
- `ntfs_full_allocation()` handles extension versus hole-filling, restores initialized size, computes apparent size according to `--no-size-change`, and updates the attribute record and inode size fields.
- `ntfs_fallocate()` opens/maps the target attribute, rejects compressed files, saves sizes/runlist, performs allocation, rolls back on error, and marks filename/inode dirty.
- `main()` checks mount state, mounts with read-only/no-action or recovery/force flags, resolves the path, runs allocation, closes inode, unmounts, and frees attribute name storage.

## Dependencies

Uses libntfs-3g attribute, inode, layout, volume, runlist, directory/pathname, bitmap, cluster allocation (`lcnalloc.h`), utilities, and logging.

## Important Behavior

Compressed attributes are rejected. Sparse attributes are accounted by increasing `compressed_size`; once compressed size reaches allocated size the sparse flag is cleared. Allocated clusters that become visible before initialized size are zeroed to avoid exposing stale disk data.

On allocation failure, the code attempts to restore original inode sizes, free newly allocated clusters, restore the saved runlist, and preserve `errno`.

## Research Notes

This utility mutates low-level allocation state directly. The option parser has a suspicious extra `optind++` after accepting an attribute name, which can consume an additional argument before the final arity check.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsfallocate.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsfix.8.in -->
# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsfix.8.in

## Role

Manual page for `ntfsfix`, a utility that fixes limited common NTFS problems and schedules Windows `chkdsk`.

## Documented Interface

Documents `--clear-bad-sectors`, `--clear-dirty`, `--no-action`, `--help`, and `--version`.

## Important Behavior

Clearly states that `ntfsfix` is not a Linux replacement for Windows `chkdsk`; it repairs only fundamental inconsistencies, resets the NTFS journal, and requests a Windows consistency check on next boot.

## Research Notes

This file is documentation only; the implementation is not in this requested group.
<!-- END FILE RESEARCH: sources/local-fs/ntfs-3g/ntfsprogs/ntfsfix.8.in -->