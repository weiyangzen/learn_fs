# Group Research: group_353_e2fsprogs_sources_local_fs_e2fsprogs_misc_lsattr_c_sources_local_fs__d346cdee01a1

Scope: `Docs/research_subset_a.md`, source tree `sources/local-fs/e2fsprogs`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/lsattr.c -->
# File Research: sources/local-fs/e2fsprogs/misc/lsattr.c

`lsattr.c` implements the `lsattr` command for listing ext-family inode attributes on files and directories.

Core behavior:
- Parses `-R`, `-V`, `-a`, `-d`, `-l`, `-v`, and `-p`.
- Uses `lstat`/`lstat64` so symbolic links are inspected without following directory loops.
- Calls `fgetflags()` and `print_flags()` from e2p support code to retrieve and display inode flags.
- Optional `-v` prints inode generation/version via `fgetversion()`.
- Optional `-p` prints project ID via `fgetproject()`.
- Optional `-l` switches to long formatting with name before flags.
- If no files are supplied, operates on `.`.

Directory traversal:
- `lsattr_args()` decides whether to list a path directly or iterate a directory.
- `lsattr_dir_proc()` builds child paths, skips dot entries unless `-a` is set, and recursively descends when `-R` is active.
- Recursion explicitly avoids descending into `.` and `..`.
- Path allocation guards against extremely large directory/name lengths before `malloc`.

Important dependencies:
- `e2p/e2p.h`: file flag/project/version helpers and flag formatting.
- `et/com_err.h`: consistent error reporting.
- `support/nls-enable.h`: translated messages.
- `../version.h`: version banner.

Research notes:
- The utility works through host filesystem ioctls/helpers rather than opening an ext filesystem image through libext2fs.
- Errors are reported per path and converted into a nonzero process exit if any top-level argument fails.
- The file is self-contained CLI glue around e2p attribute helpers and directory iteration.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/lsattr.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/mk_hugefiles.c -->
# File Research: sources/local-fs/e2fsprogs/misc/mk_hugefiles.c

`mk_hugefiles.c` implements optional creation of large preallocated regular files during `mke2fs` formatting. It is invoked by `mke2fs.c` via `mk_hugefiles()` when profile option `make_hugefiles` is enabled.

Core behavior:
- Reads hugefile settings from the active `mke2fs.conf` fs type stack:
  - `make_hugefiles`
  - `hugefiles_uid`
  - `hugefiles_gid`
  - `hugefiles_umask`
  - `num_hugefiles`
  - `hugefiles_slack`
  - `hugefiles_size`
  - `hugefiles_align`
  - `hugefiles_align_disk`
  - `hugefiles_dir`
  - `hugefiles_name`
  - `hugefiles_digits`
  - `zero_hugefiles`
- Requires extents; returns `EXT2_ET_EXTENT_NOT_SUPPORTED` if the target filesystem lacks the extents feature.
- Creates the configured directory path inside the new filesystem.
- Allocates contiguous free ranges directly from the block bitmap and inserts initialized extents manually.
- Optionally zeroes allocated physical blocks to avoid exposing stale data.
- Calculates extent tree overhead and directory-entry slack before choosing the starting block.
- Sets `large_file` if created file size requires it.

Key functions:
- `get_partition_start()` reads `/sys/dev/block/<major>:<minor>/start` on Linux for disk-relative alignment.
- `create_directory()` creates each missing path component and applies configured uid/gid.
- `mk_hugefile()` creates one regular inode, allocates extents, updates block/inode accounting, sets size, and links it into the target directory.
- `calc_overhead()` estimates extent index block overhead for large extent counts.
- `get_start_block()` skips configured free-space slack before allocation.
- `round_up_align()` aligns blocks, optionally relative to partition offset.
- `mk_hugefiles()` orchestrates profile parsing, sizing, alignment, and file loop.

Important dependencies:
- `mke2fs.h`: imports `program_name`, `quiet`, `verbose`, `zero_hugefile`, `fs_types`, and profile helper functions from `mke2fs.c`.
- libext2fs extent, inode, bitmap, and zeroing APIs.
- blkid/sysfs only for device-offset alignment support.

Research notes:
- The implementation intentionally avoids `ext2fs_fallocate()` because the goal is a contiguous physical layout with extent tree blocks near the start of the filesystem.
- If discard/prezero handling in `mke2fs.c` proves blocks are zeroed, it can set global `zero_hugefile = 0`, and this file respects that.
- `num_blocks == 0` means use available space rather than a fixed per-file size; the code derives file count/size depending on which profile values are present.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/mk_hugefiles.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/mke2fs-hurd.conf -->
# File Research: sources/local-fs/e2fsprogs/misc/mke2fs-hurd.conf

`mke2fs-hurd.conf` is a compact default configuration for creating ext filesystems for GNU Hurd compatibility.

Contents:
- `[defaults]` enables conservative ext features:
  - `sparse_super`
  - `filetype`
  - `resize_inode`
  - `dir_index`
  - `ext_attr`
- Default mount options are `acl,user_xattr`.
- Periodic fsck is disabled.
- Default block size is 4096.
- Default inode size is 128, matching Hurd limitations.
- Default inode ratio is 16384.

Filesystem type stanzas:
- `ext3` adds `has_journal`.
- `ext4` adds journal, extents, huge file support, flex_bg, uninitialized groups, dir_nlink, and extra inode size, with `auto_64-bit_support = 1` and inode size 256.
- Usage profiles tune inode density:
  - `small`, `floppy`, `news`: denser inode ratios.
  - `big`, `huge`, `largefile`, `largefile4`: sparser inode ratios.
- `hurd` forces block size 4096 and inode size 128.

Research notes:
- Compared with the general `mke2fs.conf.in`, this configuration omits newer default ext4 features such as metadata checksums, checksum seed, 64bit, and orphan_file.
- The `hurd` stanza is designed to be appended by `mke2fs.c` when the creator OS is Hurd.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/mke2fs-hurd.conf -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/mke2fs.8.in -->
# File Research: sources/local-fs/e2fsprogs/misc/mke2fs.8.in

`mke2fs.8.in` is the generated-source manual page template for `mke2fs`, `mkfs.ext2`, `mkfs.ext3`, and `mkfs.ext4`.

Documented purpose:
- Create ext2, ext3, or ext4 filesystems on a block device or image file.
- Infer fs type from invocation name such as `mkfs.ext4` unless overridden with `-t`.
- Use `/etc/mke2fs.conf` defaults unless command-line options override them.

Major option coverage:
- Geometry and sizing: `-b`, `-C`, `-g`, `-G`, `fs-size`.
- Inode layout: `-i`, `-I`, `-N`.
- Journaling: `-j`, `-J size=`, `-J device=`, `-J location=`, `-J fast_commit_size=`.
- Features: `-O`, including enable/disable syntax and reference to `ext4(5)`.
- Extended options: `-E`, including discard, lazy initialization, casefold encoding, hash seed, packed metadata, offset, resize reservation, quotas, root ownership/perms/SELinux label, orphan file size, RAID stride/stripe, test_fs.
- Safety/operation: `-c`, `-l`, `-D`, `-F`, `-n`, `-S`, `-q`, `-v`, `-V`, `-z`.
- Metadata strings: `-L`, `-M`, `-U`, `-o`.
- Usage profiles: `-T`.

Environment variables:
- `MKE2FS_SYNC`
- `MKE2FS_CONFIG`
- `MKE2FS_FIRST_META_BG`
- `MKE2FS_DEVICE_SECTSIZE`
- `MKE2FS_DEVICE_PHYS_SECTSIZE`
- `MKE2FS_SKIP_CHECK_MSG`

Research notes:
- The page closely matches behavior implemented in `mke2fs.c`, especially extended options parsed by `parse_extended_opts()`.
- It explicitly warns that `-S` is a last-resort recovery mode requiring exact recreation of original layout parameters.
- It documents undo-file limitations: undo cannot recover from power or system crash.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/mke2fs.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/mke2fs.c -->
# File Research: sources/local-fs/e2fsprogs/misc/mke2fs.c

`mke2fs.c` is the main implementation of the `mke2fs`/`mkfs.ext*` formatter. It parses command-line and profile configuration, derives filesystem parameters, validates feature combinations and device constraints, then constructs ext2/ext3/ext4 filesystem metadata through libext2fs.

Global role:
- Owns process-wide formatting state used by helper modules, including `program_name`, `quiet`, `verbose`, `fs_types`, and `zero_hugefile`.
- Exports profile lookup helpers declared in `mke2fs.h` and used by `mk_hugefiles.c`.
- Integrates device probing, bad-block handling, undo files, discard, journaling, quota inodes, orphan file creation, root population, and final filesystem close/writeout.

Primary phases:

1. Early setup and option parsing via `PRS()`
- Initializes profile config from `MKE2FS_CONFIG`, system config, or built-in default profile.
- Sets locale, error tables, PATH, page size, and initial superblock revision.
- Parses CLI options for block/cluster size, bad blocks, source population, direct I/O, extended options, journal options, labels, UUIDs, features, filesystem type, usage type, undo file, force/noaction modes, and recovery-only superblock mode.
- Determines device size, creates a regular file if needed and size was explicit, and checks mount/plausibility unless forced.
- Resolves fs type stack from invocation name, `-t`, `-T`, per-device profile, defaults, and size-derived usage class.

2. Profile and feature resolution
- `parse_fs_type()` builds ordered fs type/usage list, with size classes `floppy`, `small`, `default`, `big`, and `huge`.
- For Hurd targets, it forces or appends Hurd-compatible behavior.
- `get_string_from_profile()`, `get_int_from_profile()`, `get_uint_from_profile()`, `get_double_from_profile()`, and `get_bool_from_profile()` merge `[defaults]` and `[fs_types]` values.
- Base features, cumulative `features`, default mount options, and `default_features` are applied through e2p editing helpers.
- Hurd-incompatible features such as filetype, huge_file, metadata_csum, ea_inode, and casefold are cleared or rejected depending on user intent.

3. Extended option parsing
- `parse_extended_opts()` handles comma-separated `-E` and profile `options` settings.
- Supported options include descriptor size, hash seed, offset, MMP interval, no_copy_xattrs, sparse_super2 backup count, packed metadata, RAID stride/stripe, online resize reservation, revision, test_fs, lazy inode/journal initialization, prezeroed storage assumption, root owner/perms/SELinux label, discard/nodiscard, quota types, Android sparse output, casefold encoding/flags, and orphan file size.
- It validates arguments immediately and exits with a detailed valid-option list on malformed input.
- It enforces encoding flag use only when encoding/casefold is active.

4. Device and layout derivation
- Reads logical and physical sector sizes, with environment overrides.
- Uses blkid topology when available to derive minimum/optimal I/O, alignment offset, DAX capability, and RAID stride/stripe defaults.
- Applies blocksize, cluster size, inode ratio, inode size, flex_bg size, reserved blocks, sparse_super2 backups, 64-bit constraints, and feature dependency checks.
- Rejects incompatible combinations such as 64bit without extents, verity without extents, bigalloc without extents, resize_inode with meta_bg, resize_inode without sparse_super, and project quota with too-small inodes.
- Warns for deprecated 128-byte inode date limits when configured to do so.

5. Filesystem creation in `main()`
- Calls `PRS()`, selects the I/O manager, and optionally wraps it with undo I/O via `mke2fs_setup_tdb()`.
- Initializes the filesystem with `ext2fs_initialize()`, or sparse Android output via `sparse_io_manager`.
- Applies error behavior from profile/CLI.
- Computes journal sizing through `figure_journal_size()` when needed.
- Applies I/O channel options including undo data size and filesystem offset.
- Handles `assume_storage_prezeroed` and discard. Successful discard that guarantees zero reads lets mke2fs skip inode table wiping and hugefile zeroing.
- Zaps old superblock/boot/terminal metadata sectors where appropriate.
- Generates or parses filesystem UUID, initializes checksum seed, directory hash seed, check intervals, creator OS, volume label, last-mounted path, encryption algorithms, and checksum type.
- Shows summary stats and supports `-n` noaction exit.

6. Metadata construction
- Reads or generates bad block lists and marks them used.
- Allocates group tables either normally or with `packed_allocate_tables()` for packed flex_bg metadata.
- Converts bitmaps for subcluster accounting and calculates overhead.
- In normal mode:
  - zeros end-of-device metadata area,
  - writes inode tables,
  - creates root directory,
  - creates `/lost+found`,
  - reserves special inodes,
  - creates bad block inode,
  - creates resize inode if enabled.
- In `-S` super-only mode:
  - warns and marks filesystem erroneous,
  - avoids dirtying bitmaps,
  - preserves inode usage assumptions for later e2fsck recovery.

7. Optional feature materialization
- Creates external journal devices with `create_journal_dev()` or attaches external journals.
- Creates internal journal inode with `ext2fs_add_journal_inode3()`.
- Initializes MMP if enabled.
- Fixes bigalloc group free counts.
- Creates quota inodes when quota feature is enabled.
- Creates orphan file when orphan_file feature is enabled and journaling is present.
- Calls `mk_hugefiles()` for configured preallocated huge files.
- Copies a source directory/tarball/stdin tree into the filesystem via `populate_fs3()` when `-d` is used.
- Closes and writes superblocks/accounting through `ext2fs_close_free()`.

Important helper functions:
- Bad block handling: `read_bb_file()`, `test_disk()`, `handle_bad_blocks()`, `create_bad_block_inode()`.
- Metadata zeroing/layout: `write_inode_tables()`, `packed_allocate_tables()`, `zap_sector()`.
- Directory/bootstrap: `create_root_dir()`, `create_lost_and_found()`, `reserve_inodes()`.
- Journal device support: `create_journal_dev()`.
- Display: `show_stats()`.
- OS handling: `for_hurd()`, `set_os()`.
- Undo/discard: `should_do_undo()`, `mke2fs_setup_tdb()`, `mke2fs_discard_device()`.
- Accounting: `fix_cluster_bg_counts()`, `create_quota_inodes()`, `set_error_behavior()`.

Important dependencies:
- libext2fs for all on-disk ext metadata creation.
- e2p for feature/mount option parsing, UUID/encoding display helpers, and hashing constants.
- support profile library for `mke2fs.conf`.
- blkid for topology probing.
- quota support for internal quota inode creation.
- create_inode support for `-d` population.
- `mk_hugefiles.c` through `mke2fs.h`.

Research notes:
- The formatter is deliberately profile-driven: command line values override profile defaults, but many defaults are derived late after fs type and device size are known.
- Many safety checks happen before `ext2fs_initialize()`, but some dependency checks happen after the initialized filesystem exists because they depend on finalized superblock values.
- The file treats discard as irreversible with respect to undo, so discard is skipped when using undo I/O.
- `mke2fs.c` is the coordination center for config templates and man-page behavior in this group.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/mke2fs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/mke2fs.conf.5.in -->
# File Research: sources/local-fs/e2fsprogs/misc/mke2fs.conf.5.in

`mke2fs.conf.5.in` is the manual page template for the `mke2fs.conf` configuration file.

Documented format:
- INI-style syntax with top-level stanzas in brackets.
- Relations assign tags to scalar values or nested subsections.
- Duplicate tags are permitted.
- Comments begin with `;` or `#`.
- Values with spaces require double quotes.
- Standard backslash escapes are documented.
- Boolean parsing is liberal, accepting common true/false spellings.

Documented stanzas:
- `[options]`: controls formatter behavior.
- `[defaults]`: global defaults.
- `[fs_types]`: defaults for filesystem and usage profiles selected by `-t`, `-T`, device settings, or size.
- `[devices]`: per-device defaults.

Important documented options:
- `[options]`: `proceed_delay`, `sync_kludge`.
- `[defaults]`: `creator_os`, `fs_type`, `undo_dir`, plus filesystem tags also valid in fs type subsections.
- `[fs_types]`: feature sets, periodic fsck, error behavior, force_undo, auto 64-bit support, mount options, blocksize, lazy init, journal location, sparse_super2 backups, packed metadata, inode ratio/size, reserved ratio, hash algorithm, flex_bg size, default extended options, discard, RAID stride/stripe policy, cluster size, hugefile options, Y2038 warning, casefold encoding settings.
- `[devices]`: `fs_type`, `usage_types`.

Hugefile documentation:
- Explains `make_hugefiles`, target directory, uid/gid/umask, count, slack, size, alignment, disk-relative alignment, basename, digits, and zeroing behavior.
- Notes that hugefiles are intended to place extent tree blocks early and data contiguously.

Research notes:
- This man page describes the configuration model consumed directly by `mke2fs.c` and `mk_hugefiles.c`.
- It documents the fs type precedence rule: later entries in the constructed fs type list override earlier scalar settings, while `features` entries are cumulative.
- It includes newer feature defaults such as casefold encoding and orphan file sizing.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/mke2fs.conf.5.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/mke2fs.conf.in -->
# File Research: sources/local-fs/e2fsprogs/misc/mke2fs.conf.in

`mke2fs.conf.in` is the default `mke2fs` configuration template.

Defaults:
- `base_features = sparse_super,large_file,filetype,resize_inode,dir_index,ext_attr`
- `default_mntopts = acl,user_xattr`
- `enable_periodic_fsck = 0`
- `blocksize = 4096`
- `inode_size = 256`
- `inode_ratio = 16384`

Filesystem type stanzas:
- `ext3` adds `has_journal`.
- `ext4` enables modern ext4 defaults:
  - `has_journal`
  - `extent`
  - `huge_file`
  - `flex_bg`
  - `metadata_csum`
  - `metadata_csum_seed`
  - `64bit`
  - `dir_nlink`
  - `extra_isize`
  - `orphan_file`
- `small` and `floppy` force 1024-byte block size and denser inode ratios.
- `big`, `huge`, `news`, `largefile`, and `largefile4` tune inode density.
- `largefile` and `largefile4` use `blocksize = -1`, allowing `mke2fs.c` to choose a heuristic/page-size block size subject to a minimum.
- `hurd` forces 4096-byte blocks, 128-byte inodes, and disables Y2038 warning.

Research notes:
- This template is used both for installation and, through `profile-to-c.awk`, as the source of an embedded default profile.
- The ext4 stanza reflects current defaults expected by `mke2fs.c`, including metadata checksumming and orphan file support.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/mke2fs.conf.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/mke2fs.h -->
# File Research: sources/local-fs/e2fsprogs/misc/mke2fs.h

`mke2fs.h` is the shared local header between `mke2fs.c` and helper code such as `mk_hugefiles.c`.

Exports from `mke2fs.c`:
- `program_name`
- `quiet`
- `verbose`
- `zero_hugefile`
- `fs_types`
- `get_string_from_profile()`
- `get_int_from_profile()`
- `get_bool_from_profile()`

Exports from `mk_hugefiles.c`:
- `mk_hugefiles(ext2_filsys fs, const char *device_name)`

Research notes:
- The header intentionally exposes only the profile lookup and status globals needed by helper modules.
- `zero_hugefile` is shared so `mke2fs.c` can disable hugefile zeroing after discard/prezero detection.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/mke2fs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/mklost+found.8.in -->
# File Research: sources/local-fs/e2fsprogs/misc/mklost+found.8.in

`mklost+found.8.in` is the manual page template for the `mklost+found` utility.

Documented purpose:
- Create a `lost+found` directory in the current working directory on a mounted ext2/ext3/ext4 filesystem.
- Preallocate directory blocks so `e2fsck` can reconnect many unlinked files without needing to allocate new data blocks during recovery.

Options:
- None.

Research notes:
- The manual describes the user-space mounted-filesystem companion to `mke2fs.c`'s internal `create_lost_and_found()` bootstrap function.
- The operational goal is recovery robustness: make room in the directory before a damaged filesystem needs fsck repair.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/mklost+found.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/mklost+found.c -->
# File Research: sources/local-fs/e2fsprogs/misc/mklost+found.c

`mklost+found.c` implements the standalone `mklost+found` utility for mounted ext filesystems.

Core behavior:
- Requires no arguments.
- Creates a `lost+found` directory with mode `0700`.
- Repeatedly creates long temporary files inside it until the directory size exceeds `(EXT2_NDIR_BLOCKS - 1) * st_blksize`.
- Deletes all temporary files after expansion.
- Exits nonzero on mkdir/create/stat/unlink errors.

Implementation details:
- Temporary names are 246 `x` characters plus an 8-digit number, staying within ext directory name limits.
- Uses normal POSIX filesystem operations (`mkdir`, `creat`, `stat`, `unlink`) rather than libext2fs.
- Prints version banner from `../version.h`.
- Uses NLS support for translated usage text.

Research notes:
- The file relies on the mounted filesystem allocating directory blocks as a side effect of creating many entries.
- It is intentionally simple and assumes it is run in the target filesystem directory where `lost+found` should be created.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/mklost+found.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/partinfo.c -->
# File Research: sources/local-fs/e2fsprogs/misc/partinfo.c

`partinfo.c` is a small Linux-oriented utility that prints block device geometry and partition extent information.

Core behavior:
- Requires one or more device paths.
- For each device:
  - opens it read-only,
  - calls `HDIO_GETGEO` to fetch heads, sectors, cylinders, and start,
  - calls `BLKGETSIZE` to fetch size in sectors,
  - prints geometry plus start, size, and end sector.
- Continues to the next device after open/ioctl failures.

Important dependencies:
- Linux `hdreg.h` geometry API.
- `BLKGETSIZE`, locally defined if missing but `_IO` exists.
- NLS and `com_err` setup, though direct `fprintf`/`strerror` is used for errors.

Research notes:
- This is legacy diagnostic tooling around kernel block-device ioctls.
- It is not portable outside Linux-style block device APIs.
- It does not modify devices.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/partinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/profile-to-c.awk -->
# File Research: sources/local-fs/e2fsprogs/misc/profile-to-c.awk

`profile-to-c.awk` converts a profile/config file into a C string constant.

Behavior:
- Emits `const char *mke2fs_default_profile =`.
- For each input line:
  - escapes double quotes,
  - prints the line as a quoted C string with trailing `\n`.
- Emits the final semicolon.

Research notes:
- This script is used to embed the default `mke2fs.conf` profile into the binary, allowing `mke2fs.c` to fall back to `mke2fs_default_profile` when no config file exists.
- It performs only minimal escaping for quotes; backslashes are passed through as-is.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/profile-to-c.awk -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/e2fsprogs/misc/tune2fs.8.in -->
# File Research: sources/local-fs/e2fsprogs/misc/tune2fs.8.in

`tune2fs.8.in` is the manual page template for `tune2fs`, the ext2/ext3/ext4 filesystem tuning utility.

Documented purpose:
- Adjust tunable filesystem parameters on an existing ext filesystem.
- Display current superblock settings with `-l`.
- Accept device paths and `LABEL=`/`UUID=` specifiers.

Major option coverage:
- Check scheduling: `-c`, `-C`, `-i`, `-T`.
- Error behavior: `-e`.
- Force behavior: `-f`, including warnings for external journal removal and unreplayed journals.
- Ownership/reservation: `-g`, `-u`, `-m`, `-r`.
- Inode size conversion: `-I`, with warnings about required fsck and interruption risk.
- Journaling: `-j`, `-J device=`, `-J size=`, `-J location=`, `-J fast_commit_size=`.
- Labels and mount metadata: `-L`, `-M`, `-o`, `-E mount_opts=`.
- Feature toggling: `-O`.
- Quotas: `-Q usrquota`, `grpquota`, `prjquota` and negated forms.
- UUID changes: `-U clear|random|time|uuid`.
- Undo support: `-z`.

Extended options documented:
- `clear_mmp`
- `encoding`
- `encoding_flags`
- `force_fsck`
- `hash_alg`
- `mmp_update_interval`
- `mount_opts`
- `orphan_file_size`
- `stride`
- `stripe_width`
- `test_fs`
- `^test_fs`

Feature documentation:
- Lists tunable features such as `64bit`, `casefold`, `dir_index`, `dir_nlink`, `ea_inode`, `encrypt`, `extent`, `extra_isize`, `filetype`, `flex_bg`, `has_journal`, `fast_commit`, `large_dir`, `huge_file`, `large_file`, `metadata_csum`, `metadata_csum_seed`, `mmp`, `orphan_file`, `project`, `quota`, `read-only`, `resize_inode`, `sparse_super`, `stable_inodes`, `uninit_bg`, and `verity`.
- Notes that some features are only settable or only clearable by `tune2fs`.
- Advises follow-up `e2fsck` for some feature changes.

Research notes:
- This file is documentation only, but it overlaps conceptually with `mke2fs.c` options for journals, features, quotas, encoding, MMP, orphan files, and undo.
- It documents post-creation mutation paths for many fields initially established by `mke2fs`.
<!-- END FILE RESEARCH: sources/local-fs/e2fsprogs/misc/tune2fs.8.in -->