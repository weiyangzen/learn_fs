# Group Research: group_351_e2fsprogs_sources_local_fs_e2fsprogs_misc_create_inode_libarchive_c__90e4c1722bf1

This grouped report covers the listed `sources/local-fs/e2fsprogs/misc` files from subset A. Each file was read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/create_inode_libarchive.c -->
# File Research: sources/local-fs/e2fsprogs/misc/create_inode_libarchive.c

## Purpose
Implements the libarchive-backed tarball population path for e2fsprogs filesystem creation helpers. Its exported entry point is `__populate_fs_from_tar`, which reads an archive and creates corresponding ext2/3/4 inodes under a target root.

## Main Behaviors
- Supports three build modes:
  - Disabled libarchive: provides a stub `__populate_fs_from_tar` returning `ENOTSUP`.
  - `CONFIG_DLOPEN_LIBARCHIVE`: loads `libarchive.so.13` or platform equivalent at runtime and resolves required symbols manually.
  - Direct libarchive linkage: assigns libarchive functions to local function pointers.
- Walks archive entries with `archive_read_next_header`.
- Resolves parent directories using `__find_path`, which iteratively looks up slash-separated components from a root inode.
- Handles repeated archive entries by unlinking and freeing the existing non-directory inode before recreating it.
- Creates archive entry types:
  - Regular files through `do_write_internal_tar`.
  - Directories through `do_mkdir_internal`.
  - Symlinks through `do_symlink_internal`.
  - Character/block/FIFO/socket nodes through `do_mknod_internal`.
  - Hardlinks by resolving the archive hardlink target and calling `add_link`.
- Applies inode metadata with `set_inode_extra`.
- Copies selected xattrs unless `POPULATE_FS_NO_COPY_XATTRS` is set.

## Important Functions
- `libarchive_available`: validates/initializes libarchive function pointers.
- `__find_path`: translates a path relative to an ext2 root inode into an inode number.
- `remove_inode`: decrements link count and frees blocks/xattrs when link count reaches zero.
- `copy_file_chunk_tar`: streams archive file data into an `ext2_file_t`, skipping zero blocks for sparse-friendly writes.
- `copy_file_tar`: opens the ext2 file, allocates a 16 MiB copy buffer and zero buffer, then copies file contents.
- `do_write_internal_tar`: allocates a new inode, links it, initializes mode/timestamps/size/extents/inline-data, then writes contents.
- `set_inode_xattr_tar`: copies only `security.capability` and `gnu.translator` xattrs into ext2 xattr storage.
- `handle_entry`: dispatches archive entries by file type.
- `__populate_fs_from_tar`: top-level archive open/read/create/metadata loop.

## Dependencies
- Local e2fsprogs helpers from `create_inode.h`, including inode creation, symlink, mknod, link, and metadata helpers.
- `ext2fs` inode, xattr, file, bitmap, and block-punch APIs.
- Optional libarchive headers or runtime-loaded libarchive symbols.
- Global `link_append_flag`.

## Notes and Edge Cases
- The file can compile without `archive.h` by using opaque libarchive declarations.
- Sparse file support is implemented by avoiding writes of all-zero filesystem blocks.
- Existing directories in duplicate tar entries are preserved; existing non-directories are removed and recreated.
- Error handling commonly returns `1` for archive/libarchive failures rather than a specific libext2fs error code.
- The cleanup path unconditionally calls archive close/free after `a` creation path; failures before reader creation are guarded by flow but the function assumes `a` exists once past allocation.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/create_inode_libarchive.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/create_inode_libarchive.h -->
# File Research: sources/local-fs/e2fsprogs/misc/create_inode_libarchive.h

## Purpose
Declares the tarball population entry point implemented in `create_inode_libarchive.c`.

## API
- `__populate_fs_from_tar(ext2_filsys fs, ext2_ino_t root_ino, const char *source_tar, ext2_ino_t root, struct hdlinks_s *hdlinks, struct file_info *target, int flags, struct fs_ops_callbacks *fs_callbacks)`

## Dependencies
- Relies on types from surrounding `create_inode` and ext2fs headers included before or alongside this header.
- Exposes a low-level internal helper rather than a public installed API.

## Notes
- The declaration includes `hdlinks`, `target`, flags, and callback hooks to match the non-archive population interface, though the archive implementation ignores `hdlinks`.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/create_inode_libarchive.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/dumpe2fs.8.in -->
# File Research: sources/local-fs/e2fsprogs/misc/dumpe2fs.8.in

## Purpose
Manual page template for `dumpe2fs`, the ext2/ext3/ext4 superblock and block group information dumper.

## Documented Interface
- Synopsis: `dumpe2fs [-bfghixV] [-o superblock=num] [-o blocksize=num] device`
- Device can be a path, `LABEL=...`, or `UUID=...`.
- Options:
  - `-b`: print reserved bad blocks.
  - `-o superblock=...`: use an alternate superblock.
  - `-o blocksize=...`: force a block size.
  - `-f`: force display despite unknown features.
  - `-g`: machine-readable group descriptor format.
  - `-h`: superblock only.
  - `-i`: read an `e2image` image file.
  - `-m`: MMP safety/status checking.
  - `-x`: hexadecimal block numbers.
  - `-V`: version output.

## Important Notes
- Warns that output from mounted filesystems may be stale or inconsistent.
- Documents exit codes as nonzero for errors, checksum problems, invalid superblocks, or unsafe MMP state.
- References `e2mmpstatus`, `e2fsck`, `mke2fs`, `tune2fs`, and `ext4`.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/dumpe2fs.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/dumpe2fs.c -->
# File Research: sources/local-fs/e2fsprogs/misc/dumpe2fs.c

## Purpose
Implements `dumpe2fs`, which opens an ext2/3/4 filesystem or image and prints superblock, journal, MMP, bad block, bitmap, and block group descriptor information. It also implements `e2mmpstatus` behavior when invoked under that name.

## Main Behaviors
- Parses options `-bfg himxV` and extended `-o superblock=...`, `-o blocksize=...`.
- Resolves device names using `get_devname`.
- Opens filesystems with 64-bit and threaded ext2fs flags.
- Retries open/read operations with `EXT2_FLAG_IGNORE_CSUM_ERRORS`, then reports checksum errors and advises `e2fsck`.
- Can open e2image metadata files with `EXT2_FLAG_IMAGE_FILE`.
- Prints:
  - Superblock via `list_super`.
  - Journal information for external or inline journals.
  - MMP block details.
  - Bad block list.
  - Per-group descriptor locations, bitmap/table locations, free blocks/inodes, checksums, and group flags.
- Machine-readable `-g` output prints colon-separated group metadata.

## Important Functions
- `print_number` / `print_range`: decimal or hex formatting, with 64-bit width handling.
- `print_free`: compresses free bitmap runs into ranges.
- `print_bg_opts`: prints group descriptor flags such as `INODE_UNINIT`, `BLOCK_UNINIT`, and `ITABLE_ZEROED`.
- `list_desc`: core group descriptor reporting routine.
- `list_bad_blocks`: reads bad block inode and prints either dump or summary format.
- `print_inline_journal_information`: opens the journal inode and lists the JBD2 superblock.
- `print_journal_information`: reads external journal superblock.
- `check_mmp`: uses `ext2fs_mmp_start` in read-only mode to determine whether mount is safe.
- `print_mmp_block`: reads and displays MMP metadata fields.
- `parse_extended_opts`: parses `superblock`, `sb`, `blocksize`, and `bs`.

## Dependencies
- `ext2fs`, `e2p`, JBD kernel structures, UUID support.
- `support/devname.h` and `support/plausible.h`.
- Version metadata from `../version.h`.

## Notes and Edge Cases
- `e2mmpstatus` is not a separate implementation here; `main` checks `argv[0]` for `"mmpstatus"` and switches into MMP-check/header-only behavior.
- Group reporting honors bigalloc by switching terminology from blocks to clusters.
- `DUMPE2FS_IGNORE_80COL` changes formatting around bitmap output.
- If checksums fail but forced/ignored paths succeed, the tool still reports the original checksum problem.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/dumpe2fs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/e2freefrag.8.in -->
# File Research: sources/local-fs/e2fsprogs/misc/e2freefrag.8.in

## Purpose
Manual page template for `e2freefrag`, which reports free-space fragmentation on ext2/3/4 filesystems.

## Documented Interface
- Synopsis: `e2freefrag [-c chunk_kb] [-h] filesys`
- `-c chunk_kb`: report aligned free chunks of a given power-of-two size in KB.
- `-h`: usage.

## Output Described
- Device and block size.
- Total and free block counts.
- Optional total/free chunk counts.
- Minimum, maximum, average free extent size.
- Histogram of free extent sizes.

## Notes
- Explains that the report helps estimate free-space fragmentation.
- See also: `debugfs`, `dumpe2fs`, `e2fsck`.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/e2freefrag.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/e2freefrag.c -->
# File Research: sources/local-fs/e2fsprogs/misc/e2freefrag.c

## Purpose
Implements `e2freefrag`, a free-space fragmentation reporter for ext2/3/4 filesystems. It can also be compiled into `debugfs` as `do_freefrag`.

## Main Behaviors
- Parses `-c` chunk size in KB and validates power-of-two and block-size constraints.
- Opens the filesystem read-only through ext2fs unless compiled for `debugfs`.
- Collects free extent statistics via:
  - Online FSMAP ioctl scanning when available and the filesystem is mounted.
  - Offline ext2 block bitmap scanning as fallback.
- Reports totals, chunk stats, min/max/average free extent size, number of free extents, and a histogram.

## Important Functions
- `init_chunk_info`: initializes chunk size, block counts, histogram state, and min/max/avg fields.
- `update_chunk_stats`: updates histogram and aggregate free extent metrics.
- `scan_block_bitmap`: offline bitmap scan over blocks/clusters to identify contiguous free runs and aligned chunks.
- `scan_online`: optional live scan using `FS_IOC_GETFSMAP` and `FMR_OWN_FREE`.
- `scan_offline`: reads block bitmap and calls `scan_block_bitmap`.
- `dump_chunk_info`: formats all output.
- `collect_info`: coordinates scanning and output.
- `open_device` / `close_device`: standalone open/close wrappers.
- `do_freefrag` / `main`: shared command entry depending on `DEBUGFS`.

## Dependencies
- `ext2fs` block bitmap and filesystem APIs.
- Optional Linux FSMAP ioctl support through `fsmap.h`.
- `e2freefrag.h` for `struct chunk_info`, histogram constants, and default chunk size.

## Notes and Edge Cases
- The online scan only runs for mounted filesystems and returns false on mount/open/ioctl failure, causing offline fallback where possible.
- Free blocks from online mode are accumulated from free extents rather than the superblock.
- Bigalloc is handled indirectly through ext2fs bitmap behavior; the scanner tests the block map using cluster ratio bits.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/e2freefrag.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/e2freefrag.h -->
# File Research: sources/local-fs/e2fsprogs/misc/e2freefrag.h

## Purpose
Defines shared constants and data structures for `e2freefrag`.

## Contents
- `DEFAULT_CHUNKSIZE`: 1 MiB.
- `MAX_HIST`: 32 histogram buckets.
- `struct free_chunk_histogram`: arrays for free extent counts and block counts per bucket.
- `struct chunk_info`: configured chunk size, derived chunk/block bit counts, free chunk totals, min/max/avg metrics, and histogram.

## Notes
- `chunkbytes == 0` means the default chunk size is used by `init_chunk_info`.
- Histogram units are block counts internally, converted to KB at output time.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/e2freefrag.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/e2fuzz.c -->
# File Research: sources/local-fs/e2fsprogs/misc/e2fuzz.c

## Purpose
Implements `e2fuzz`, a test utility that corrupts bytes in ext filesystems or filesystem images to exercise fsck and kernel robustness.

## Main Behaviors
- Defaults to corrupting metadata only.
- Options:
  - `-b N` or `-b P%`: corrupt exact byte count or percentage of corruptible bytes.
  - `-d`: include data blocks.
  - `-n`: dry run.
  - `-v`: verbose corruption log.
- Forces dry-run mode if the filesystem is mounted read-write.
- Opens filesystem via ext2fs and refuses filesystems with error state.
- If filesystem is unclean but not in error state, switches to dry run.
- Builds a bitmap of corruptible blocks:
  - All used blocks in data mode.
  - Metadata blocks, inode tables, bitmaps, xattrs, directories, metadata-bearing file blocks, and indirect/extent metadata in metadata-only mode.
- Randomly chooses byte offsets within marked blocks and writes random bytes, skipping the first 4096 bytes to avoid the primary superblock area.

## Important Functions
- `getseed`: reads random seed from `/dev/urandom`.
- `find_block_helper`: marks blocks to corrupt based on inode type and metadata/data mode.
- `find_metadata_blocks`: marks filesystem structural metadata and scans all allocated inodes.
- `rand_num`: generates a random integer in a range using `random()`.
- `process_fs`: full safety check, bitmap creation, corruption loop, and cleanup.
- `print_help` / `main`: CLI handling.

## Dependencies
- ext2fs open, mount-state, bitmap, inode scan, and block iteration APIs.
- POSIX file I/O, with fallback `my_pwrite` if `pwrite`/`pwrite64` are unavailable.

## Notes and Edge Cases
- Metadata-only mode still includes directory data blocks because corrupting directories tests metadata repair paths.
- When using data mode, `corrupt_map` aliases `fs->block_map`; cleanup avoids freeing it twice.
- The program writes bytes directly to the backing file/device, bypassing ext2fs write helpers.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/e2fuzz.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/e2fuzz.sh -->
# File Research: sources/local-fs/e2fsprogs/misc/e2fuzz.sh

## Purpose
Shell harness for repeatedly creating, corrupting, mounting, mutating, and repairing ext filesystem images with `e2fuzz` and `e2fsck`.

## Main Behaviors
- Creates a temporary mke2fs config under `/tmp/mke2fs.conf`.
- Builds a base image with configurable features, block size, inode size, image size, extended mke2fs options, and source data directory.
- Populates the image by mounting it and copying repeated copies of `SRCDIR`.
- For each pass:
  - Copies the base image.
  - Relabels it with `tune2fs`.
  - Corrupts it with `e2fuzz`.
  - Attempts a kernel loop mount or optional `fuse2fs` mount.
  - Runs filesystem operations: recursive listing, file reads, xattr listing, append writes, renames, copy/remove tree.
  - Runs `e2fsck -fy` up to `MAX_FSCK` times, detecting lack of progress by comparing logs.
  - Verifies the repaired image with `e2fsck -fn`.
  - Mounts the repaired image again and repeats read/write/remove checks.
  - Removes per-pass images/logs on success.

## Options
- `-b`: filesystem block size.
- `-B`: corruption bytes passed to `e2fuzz`.
- `-d`: working directory.
- `-E`: mke2fs extended options.
- `-F`: e2fsck extended options.
- `-f`: skip fsck after each pass.
- `-I`: inode size.
- `-n`: number of passes.
- `-O`: additional filesystem features.
- `-p`: use system tools instead of prepending local build dirs to `PATH`.
- `-s`: image size.
- `-S`: source directory.
- `-x`: maximum fsck passes.
- `-u`: use `fuse2fs` when available.

## Dependencies
- `mke2fs`, `e2fsck`, `tune2fs`, `e2fuzz`, `dumpe2fs`.
- Mount/umount, loop module, `truncate`, `cp`, `find`, `xargs`, `attr`, `dd`, `sync`, `stat`, `du`, `awk`, `diff`.
- Optional local `fuse2fs`.

## Notes and Edge Cases
- Defaults exercise many ext4 features including journal, extents, 64bit, metadata checksums, bigalloc, sparse_super2, and inline_data.
- The script treats out-of-memory and no-free-block fsck failures as environmental limits rather than fuzz failures.
- Uses shell pipelines with subshells in some loops; `break`/`exit` behavior is controlled by the pipeline/subshell context.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/e2fuzz.sh -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/e2image.8.in -->
# File Research: sources/local-fs/e2fsprogs/misc/e2image.8.in

## Purpose
Manual page template for `e2image`, which saves critical ext2/ext3/ext4 metadata to image files and can restore classic metadata images.

## Documented Interface
- Standard metadata image:
  - `e2image [options] device image-file`
- Install/restore:
  - `e2image -I device image-file`
- Raw/QCOW2:
  - `e2image [-r|-Q] [-a] [-f] [-b superblock] [-B blocksize] [-c] [-n] [-p] [-s] [-o src_offset] [-O dest_offset] device image-file`

## Major Options
- `-a`: include all file data for raw/QCOW2.
- `-b`, `-B`: alternate superblock/block size.
- `-c`: compare target blocks and skip identical writes in raw mode.
- `-f`: allow imaging read-write mounted filesystems.
- `-I`: install metadata image back to a device.
- `-n`: no writes; print blocks that would be written.
- `-o`, `-O`: source/destination offsets.
- `-p`: progress.
- `-Q`: QCOW2 image.
- `-r`: raw sparse image.
- `-s`: scramble directory entries.

## Important Notes
- Raw images preserve metadata at original filesystem-relative offsets and are sparse.
- QCOW2 images are compact but not sparse and can be processed by QCOW2-aware tools.
- `-I` is documented as a desperation recovery measure because stale metadata restore can lose data.
- Output to stdout is only supported for raw image creation.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/e2image.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/e2image.c -->
# File Research: sources/local-fs/e2fsprogs/misc/e2image.c

## Purpose
Implements `e2image`, which creates classic ext2 image files, raw sparse metadata/data images, QCOW2 images, QCOW2-to-raw conversion, and classic metadata image installation.

## Main Image Modes
- Classic metadata image:
  - Writes an `ext2_image_hdr`, superblock, inode tables, block bitmap, and inode bitmap using ext2fs image helpers.
- Raw image:
  - Writes selected filesystem blocks at their filesystem-relative offsets, usually sparse.
  - Includes metadata, directory blocks, indirect/extent metadata, journal/quota/orphan-file blocks, and optionally all data blocks.
- QCOW2 image:
  - Writes metadata/data blocks into a generated QCOW2 structure with L1/L2/refcount metadata.
- Install mode:
  - Restores inode table metadata from a classic image to a target device.
- QCOW2 input conversion:
  - Detects QCOW2 input when raw output is requested and converts it with `qcow2_write_raw_image`.

## Important Functions
- `align_offset`, `get_bits_from_size`: block/cluster alignment helpers.
- `generic_write`: central write/no-op write helper.
- `write_header`: writes zero-padded headers at file start.
- `write_image_file`: classic image writer.
- `use_inode_shortcuts`, `meta_get_blocks`, `meta_check_directory`, `meta_read_inode`: short-circuit ext2fs callbacks during inode scanning.
- `mark_table_blocks`: marks superblock, descriptors, MMP, inode tables, block bitmaps, and inode bitmaps as metadata.
- `scramble_dir_block`: anonymizes directory entry names and zeros unused directory entry slack.
- `output_meta_data_blocks`: raw sparse output loop with optional progress, zero-block skipping, compare-before-write, and in-place move handling.
- `initialize_qcow2_image`, `init_l1_table`, `init_l2_cache`, `init_refcount`: QCOW2 setup.
- `add_l2_item`, `update_refcount`, `sync_refcount`, `flush_l2_cache`: QCOW2 metadata maintenance.
- `output_qcow2_meta_data_blocks`: QCOW2 data and metadata writer.
- `write_raw_image_file`: scans inodes, builds block maps, and dispatches raw/QCOW2 output.
- `install_image`: restores a classic image to a device.
- `check_qcow2_image`: identifies QCOW2 input.
- `main`: option validation, mount safety checks, open paths, and mode dispatch.

## Dependencies
- ext2fs core, private ext2fs structures, e2image helpers, QCOW2 helpers.
- quota inode helpers.
- `support/plausible.h`.
- POSIX large-file I/O, signals, and filesystem stat APIs.

## Notes and Edge Cases
- `-a` and `-b` are only valid with raw or QCOW2 images.
- Offsets and in-place move mode are raw-only; move mode also requires all-data mode.
- Raw imaging normally refuses read-write mounted filesystems unless `-f` is supplied.
- Directory scrambling preserves `.` and `..`, replaces other names with deterministic `A...` variants, and repairs malformed directory record lengths enough to continue.
- In-place rightward moves copy in reverse chunks to avoid overwriting source data before it is copied.
- `-c` compare-before-write is raw-only and not supported with stdout.
- `-p` progress is raw-only.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/e2image.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/e2initrd_helper.c -->
# File Research: sources/local-fs/e2fsprogs/misc/e2initrd_helper.c

## Purpose
Implements `e2initrd_helper`, a small utility for reading `/etc/fstab` from an ext filesystem image/device and reporting the root filesystem type for initrd generation workflows.

## Main Behaviors
- Parses `-r` to request root type output and `-v` for version.
- Resolves the device name through `get_devname`.
- Opens the filesystem with ext2fs.
- Reads `/etc/fstab` from inside the filesystem using ext2fs file APIs.
- Parses fstab lines, resolves devices through blkid, and prints the `type` field for the `/` mount entry.

## Important Functions
- `get_file`: looks up a path, reads a small regular file into memory, and rejects files larger than 64 KiB.
- `get_line`: returns the next line from the in-memory file.
- `parse_escape`: decodes fstab-style backslash escapes including `\t`, `\n`, and octal escapes.
- `parse_fstab_line`: splits fields, ignores comments, resolves device names, and fills `struct fs_info`.
- `PRS`: command-line parsing and localization setup.
- `get_root_type`: reads and scans `/etc/fstab`.

## Dependencies
- ext2fs path lookup, inode read, and file read APIs.
- blkid cache/device resolution.
- `support/devname.h`.
- Version metadata.

## Notes and Edge Cases
- `open_flag` is global but not set by options in this file, so opens use default flags unless modified externally at compile/link context.
- `free_fstab_line` clears pointers without freeing allocated field strings, which is a short-lived process leak.
- The parser ignores fstab entries with comma-containing type fields.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/e2initrd_helper.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/e2label.8.in -->
# File Research: sources/local-fs/e2fsprogs/misc/e2label.8.in

## Purpose
Manual page template for `e2label`, which displays or changes ext2/ext3/ext4 volume labels.

## Documented Interface
- `e2label device`
- `e2label device volume-label`

## Behavior Described
- Without `volume-label`, prints the current label.
- With `volume-label`, sets the filesystem label.
- Ext labels are at most 16 characters; longer labels are truncated with a warning.
- Mentions that mounted filesystems with online label support may also work and may not use the same truncation path.

## See Also
- `mke2fs`
- `tune2fs`
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/e2label.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/e2label.c -->
# File Research: sources/local-fs/e2fsprogs/misc/e2label.c

## Purpose
Implements a minimal volume label reader/writer for ext2-style superblocks.

## Main Behaviors
- Opens the device directly with POSIX `open`.
- Seeks to byte offset 1024 and reads a local partial `struct ext2_super_block`.
- Validates magic `0xEF53`.
- With one argument, prints `s_volume_name`.
- With two arguments, writes a zero-padded/truncated 16-byte label and rewrites the same partial superblock area.

## Important Functions
- `open_e2fs`: open, seek, read, and magic validation.
- `print_label`: formats the fixed-size volume name safely.
- `change_label`: updates `s_volume_name`, warns on truncation, and writes the superblock structure back.
- `main`: two-argument print or three-argument change dispatch.

## Dependencies
- Direct POSIX I/O only; this implementation does not use ext2fs open helpers.
- `support/nls-enable.h` for translated messages.

## Notes and Edge Cases
- The file defines a local partial superblock layout containing only fields needed around magic and volume name.
- Writes back the whole local partial struct, not only the volume-name field.
- Label length limit is `VOLNAMSZ` 16.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/e2label.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/e2mmpstatus.8.in -->
# File Research: sources/local-fs/e2fsprogs/misc/e2mmpstatus.8.in

## Purpose
Manual page template for `e2mmpstatus`, the Multiple-Mount Protection status checker for ext4 filesystems.

## Documented Interface
- `e2mmpstatus [-i] file system`
- `-i`: print MMP information instead of checking safety.

## Behavior Described
- Checks whether an MMP-enabled ext4 filesystem is safe to mount.
- Accepts device paths, `UUID=...`, or `LABEL=...`.
- Unsafe conditions include:
  - `e2fsck` running.
  - Filesystem in use by another node.
  - MMP block corrupted or unreadable.
- May wait to observe whether another node is updating the MMP block.

## Exit Codes
- `0`: safe to mount.
- `1`: in use by another node, not safe.
- `2`: other failure preventing reliable status detection.

## Implementation Link
- The implementation is in `dumpe2fs.c`, which switches behavior when invoked as `e2mmpstatus`.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/e2mmpstatus.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/e2undo.8.in -->
# File Research: sources/local-fs/e2fsprogs/misc/e2undo.8.in

## Purpose
Manual page template for `e2undo`, which replays an undo log onto an ext2/ext3/ext4 filesystem.

## Documented Interface
- `e2undo [-f] [-h] [-n] [-o offset] [-v] [-z undo_file] undo_log device`

## Options
- `-f`: skip safety check that filesystem superblock matches the undo log.
- `-h`: display usage/header information.
- `-n`: dry run.
- `-o offset`: filesystem byte offset in the target.
- `-v`: print block replay information.
- `-z undo_file`: create a new undo file while replaying, so replay itself can be undone.

## Notes
- Warns that undo files do not recover from power or system crashes.
- References `mke2fs` and `tune2fs`.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/e2undo.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/e2undo.c -->
# File Research: sources/local-fs/e2fsprogs/misc/e2undo.c

## Purpose
Implements `e2undo`, which validates and replays e2fsprogs undo logs back onto an ext2/3/4 filesystem or image.

## Undo Format
- Header block begins with magic `E2UNDO02`.
- Header records number of keys, superblock copy offset, key block offset, undo block size, filesystem block size, superblock CRC, state, feature flags, and optional filesystem offset.
- Key blocks begin with `KEYBLOCK_MAGIC` and contain `undo_key` entries mapping filesystem block numbers to data blocks in the undo file.
- Each data block/extent has a CRC.

## Main Behaviors
- Parses `-f`, `-h`, `-n`, `-o`, `-v`, and `-z`.
- Refuses to use the replayed undo file as the new backup undo file.
- Opens and validates the undo file header, feature flags, block sizes, and CRCs unless forced.
- Refuses mounted target filesystems.
- Optionally wraps target writes with undo I/O manager for a new undo file.
- Applies filesystem offset from command line or undo file feature.
- Compares target superblock with undo file’s saved superblock unless forced.
- Reads all key blocks, verifies key block CRCs and individual block CRCs.
- Sorts replay keys by target filesystem block.
- Replays data to target unless dry-run.
- If corruption/I/O/incomplete undo state is detected, marks the target filesystem invalid and possibly errored to force fsck.

## Important Functions
- `dump_header`: prints undo header metadata.
- `print_undo_mismatch`: explains superblock mismatches.
- `check_filesystem`: verifies the undo file matches current target filesystem state and saved superblock CRC.
- `key_compare`: orders replay by filesystem block.
- `e2undo_setup_tdb`: configures undo I/O manager and selects backup undo file path.

## Dependencies
- ext2fs I/O managers, undo I/O manager, CRC32C, filesystem open/close.
- POSIX path and environment helpers.
- `E2FSPROGS_UNDO_DIR`, defaulting to `/var/lib/e2fsprogs`.

## Notes and Edge Cases
- `-h` in code dumps the undo header and exits with status `1`, while the manpage calls it a usage message.
- `-f` allows operation through checksum and feature problems but tracks corruption/I/O warnings.
- Maximum replay extent size is capped at `512 * undo block size`.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/e2undo.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/e4crypt.8.in -->
# File Research: sources/local-fs/e2fsprogs/misc/e4crypt.8.in

## Purpose
Manual page template for `e4crypt`, an ext4 encryption management utility.

## Documented Commands
- `e4crypt add_key [-vq] [-S salt] [-k keyring] [-p pad] [path ...]`
- `e4crypt get_policy path ...`
- `e4crypt new_session`
- `e4crypt set_policy [-p pad] policy path ...`

## Behavior Described
- `add_key` prompts for a passphrase, derives encryption keys from salts, inserts them into a keyring, and optionally applies policy to directories.
- Salt can be a text salt (`s:`), hex salt (`0x`), filename (`f:` or absolute path), or UUID.
- `pad` controls filename padding and must be one of the supported values.
- `get_policy` prints directory policy key descriptors.
- `new_session` creates a new session keyring.
- `set_policy` applies an existing 16-hex-character key descriptor to directories.

## See Also
- `keyctl`
- `mke2fs`
- `mount`
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/e4crypt.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/e4crypt.c -->
# File Research: sources/local-fs/e2fsprogs/misc/e4crypt.c

## Purpose
Implements `e4crypt`, an ext4 encryption policy and key management utility using kernel keyrings and legacy ext4 encryption ioctls.

## Main Behaviors
- Provides subcommands:
  - `add_key`
  - `get_policy`
  - `new_session`
  - `set_policy`
  - hidden `help`
- Supports direct libc `keyctl`/`add_key` or syscall fallbacks.
- Reads salts from command-line strings, files/directories via `EXT4_IOC_GET_ENCRYPTION_PWSALT`, UUIDs, or mounted ext4 filesystems.
- Prompts for passphrase with terminal echo disabled.
- Derives raw encryption key with the file’s PBKDF2-like SHA512 routine.
- Computes key descriptor as SHA512(SHA512(key)) truncated to ext4 descriptor size.
- Inserts keys as `logon` keys with description prefix `ext4:`.
- Sets and gets encryption policy via `EXT4_IOC_SET_ENCRYPTION_POLICY` and `EXT4_IOC_GET_ENCRYPTION_POLICY`.
- Can create a new session keyring and push it to parent process with keyctl commands.

## Important Functions
- `validate_paths`: ensures path arguments are writable directories.
- `hex2byte`: parses lowercase hex descriptors.
- `parse_salt`: accepts text, hex, UUID, file, and directory salt forms.
- `clear_secrets`, `sigcatcher_setup`: clear passphrase/key material on normal/error signal paths.
- `set_policy`: builds `ext4_encryption_policy` and applies it to directories.
- `pbkdf2_sha512`: derives ext4 key material from passphrase and salt.
- `get_passphrase`: terminal echo-disabled passphrase read.
- `get_keyring_id`: maps `@us`, `@u`, `@s`, `@g`, `@p`, `@t`, or numeric keyring IDs.
- `generate_key_ref_str`: computes printable key descriptor.
- `insert_key_into_keyring`: searches then inserts a logon key.
- `get_default_salts`: scans `/etc/mtab` ext4 mounts and queries salts.
- `do_add_key`, `do_set_policy`, `do_get_policy`, `do_new_session`, `do_help`: command implementations.

## Dependencies
- Linux keyring syscalls.
- ext4 encryption ioctl structures/constants from ext2fs/ext4 headers.
- UUID parsing.
- `/etc/mtab` mount table.
- Terminal control APIs.

## Notes and Edge Cases
- Only lowercase hex descriptors are accepted by `set_policy`.
- The command uses older ext4 encryption APIs and policy version `0`.
- `add_key` with no explicit salt queries mounted ext4 filesystems for default salts.
- Signal handlers attempt to clear in-memory secrets before exit.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/e4crypt.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/e4defrag.8.in -->
# File Research: sources/local-fs/e2fsprogs/misc/e4defrag.8.in

## Purpose
Manual page for `e4defrag`, an online defragmenter for extent-based ext4 files.

## Documented Interface
- `e4defrag [-c] [-v] target ...`

## Behavior Described
- Targets can be regular files, directories, or mounted ext4 block devices.
- Directory targets recursively defragment files inside.
- Device targets resolve the mount point and defragment files on that filesystem.
- Only extent-based ext4 files are supported.

## Options
- `-c`: report current and ideal fragmentation counts and a fragmentation score; does not defragment.
- `-v`: verbose per-file errors and before/after extent counts.

## Notes
- Does not support swap files, files in `lost+found`, or files using indirect blocks.
- Avoids crossing into other mounted filesystems.
- Can run on active files, but may cause page cache and I/O contention.
- Non-root users can defragment their own files, but score details are limited.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/e4defrag.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/e4defrag.c -->
# File Research: sources/local-fs/e2fsprogs/misc/e4defrag.c

## Purpose
Implements `e4defrag`, an online ext4 defragmentation and fragmentation-statistics utility using FIEMAP and `EXT4_IOC_MOVE_EXT`.

## Main Modes
- Default defrag mode:
  - Walks files, creates donor files, preallocates contiguous-ish donor extents, and swaps extents into the target via ioctl.
- Statistic mode `-c`:
  - Computes current extent count, ideal/best extent count, average size per extent, top fragmented files, and score.
- Verbose mode `-v`:
  - Prints per-file progress, extent details, and errors.

## Main Data Structures
- `fiemap_extent_data`: logical, physical, and length in filesystem blocks.
- `fiemap_extent_list`: circular doubly linked list of extents.
- `fiemap_extent_group`: contiguous logical extent group used for donor allocation.
- `move_extent`: ioctl payload for `EXT4_IOC_MOVE_EXT`.
- `frag_statistic_ino`: top-fragmented-file ranking entry.

## Important Functions
- `get_mount_point`: maps a block device to its ext4 mount point using `/etc/mtab` and device numbers.
- `is_ext4`: validates a file/directory is on ext4 and records mount device and `lost+found` path.
- `calc_entry_counts`: counts total and regular files before a tree walk.
- `page_in_core`: uses `mmap` and `mincore` to remember cached pages before moving extents.
- `defrag_fadvise`: syncs and releases pages that were cached by this process.
- `check_free_size`: verifies enough free blocks for donor allocation, accounting for root vs non-root availability.
- `file_frag_count`: asks FIEMAP for mapped extent count.
- `file_check`: validates free space, ownership, and advisory lock status.
- `insert_extent_by_logical` / `insert_extent_by_physical`: sorted insertion with overlap checks.
- `join_extents`: groups logically contiguous extents.
- `get_file_extents`: retrieves FIEMAP extents in batches of 512.
- `change_physical_to_logical`: reorders the extent list from physical to logical order.
- `get_best_count`: estimates ideal extent count based on block groups and flex_bg.
- `file_statistic`: computes per-file fragmentation metrics and top-fragmented rankings.
- `call_defrag`: loops over donor logical extents and invokes `EXT4_IOC_MOVE_EXT`.
- `file_defrag`: validates a file, builds original/donor extent lists, creates/unlinks donor file, fallocates donor regions, compares improvement, and performs defrag.
- `main`: parses args, classifies target type, validates ext4, opens superblock details as root, walks directories/devices, and prints summaries.

## Dependencies
- Linux FIEMAP ioctl.
- ext4 `EXT4_IOC_MOVE_EXT`.
- `nftw64`, mount table parsing, `statfs64`, `fallocate`, `mmap`, `mincore`, `sync_file_range`, `posix_fadvise`.
- ext2fs open for block group/flex_bg metadata used in scoring.

## Notes and Edge Cases
- Skips `lost+found`, non-regular files, empty files, and one-block files.
- Non-root users can only process their own files and get limited statistics.
- Directory walks use `FTW_PHYS | FTW_MOUNT` to avoid symlinks and crossing mount points.
- If donor physical extent count is not better than original, the file is reported OK without moving extents.
- Donor files are created as `file.defrag`, immediately unlinked after open, and used only as temporary extent donors.
- The tool exits nonzero if no target had any successful processing.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/e4defrag.c -->