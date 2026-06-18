# Group Research: group_1354_ocfs2_tools_sources_local_fs_ocfs2_tools_ocfs2console_ocfs2interfac_2637fb15a0f4

Scope verified against `Docs/research_subset_a.md`: all files are under `sources/local-fs/ocfs2-tools`, which is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/toolbar.py -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/toolbar.py

## Purpose
Defines the GTK toolbar used by `ocfs2console`, with mount, unmount, refresh, and partition-name filter controls.

## Main Behavior
- `toolbar_data` declares three toolbar buttons: `Mount`, `Unmount`, and `Refresh`.
- `Toolbar.get_widgets()` builds a `gtk.Toolbar`, wires callbacks through `guiutil.make_callback()`, stores returned toolbar items by callback name, and appends a filter box.
- `Toolbar.get_filter_box()` creates a horizontal `Filter:` label plus `gtk.Entry`.
- `main()` is a small standalone GTK smoke/demo harness that creates dummy callbacks and displays the toolbar.

## Dependencies
- GTK 2 Python bindings via `import gtk`.
- `guiutil.make_callback`, expected to adapt `window.<callback>` plus optional sub-callback names into GTK callbacks.
- The parent window object is expected to expose `mount`, `unmount`, and `refresh` methods.

## Notes
The file is UI glue only; it performs no OCFS2 operations directly. It returns `(toolbar, items, entry)` so callers can later enable/disable toolbar items and inspect/filter text.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/toolbar.py -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/tune.py -->
# File Research: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/tune.py

## Purpose
Provides OCFS2 console dialogs for changing a volume label and node slot count by invoking `tunefs.ocfs2`.

## Main Behavior
- `TuneVolumeLabel` subclasses `VolumeLabel`, opens `ocfs2.Filesystem(device)`, and preloads `fs.fs_super.s_label` when readable.
- `TuneNumSlots` subclasses `NumSlots`, reads the filesystem, and sets the allowed range from the current `s_max_slots` through `ocfs2.MAX_SLOTS`.
- `tune_action()` constructs a GTK dialog, validates empty values depending on `empty_ok`, builds `tunefs.ocfs2` command arguments from `widget.get_arg()`, runs the command with `Process`, and reports failures through `error_box`.
- `tune_label()` and `tune_slots()` are thin wrappers.
- `main()` runs both tuners for a command-line device.

## Dependencies
- Python GTK.
- Python `ocfs2` bindings for reading current superblock values.
- `guiutil.Dialog`, `set_props`, `error_box`, `format_bytes`.
- `process.Process` for launching `tunefs.ocfs2`.
- `fswidgets.NumSlots` and `VolumeLabel`, which provide `.label`, `.get_text()`, and `.get_arg()`.

## Notes
The module only shells out for mutations; it does not write OCFS2 metadata itself. The empty-invalid branch calls `widget_type.lower().ucfirst()`, which is unusual for a class object and appears to rely on surrounding project conventions or may be a latent error path.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/ocfs2console/ocfs2interface/tune.py -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/sizetest/Makefile -->
# File Research: sources/local-fs/ocfs2-tools/sizetest/Makefile

## Purpose
Builds the uninstalled `sizetest.ocfs2` utility.

## Main Behavior
- Includes common project build rules from `../Preamble.make` and `../Postamble.make`.
- Defines `UNINST_PROGRAMS = sizetest.ocfs2`.
- Adds `-I$(TOPDIR)/include` and `-DVERSION="$(VERSION)"`.
- Compiles `sizetest.c` into `sizetest.o`.
- Links `sizetest.ocfs2` with `$(LIBOCFS2_DEPS)` through the shared `$(LINK)` rule.
- Marks `sizetest.c` as the distribution file.

## Dependencies
- Top-level OCFS2 tools make infrastructure.
- `libocfs2.a`.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/sizetest/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/sizetest/sizetest.c -->
# File Research: sources/local-fs/ocfs2-tools/sizetest/sizetest.c

## Purpose
Prints offsets and sizes of important OCFS2 on-disk C structures, mainly to verify ABI/layout consistency across ports.

## Main Behavior
- Defines local `offsetof`, `ssizeof`, `START_TYPE`, `SHOW_OFFSET`, and `END_TYPE` helpers for tabular output.
- Prints field offsets and total sizes for:
  - `ocfs2_extent_rec`
  - `ocfs2_chain_rec`
  - `ocfs2_extent_list`
  - `ocfs2_chain_list`
  - `ocfs2_extent_block`
  - `ocfs2_super_block`
  - `ocfs2_local_alloc`
  - `ocfs2_dinode`
  - `ocfs2_dir_entry`
  - `ocfs2_group_desc`
- `main()` calls every printer and exits success.

## Dependencies
- `ocfs2/ocfs2.h` structure definitions.
- Standard output only; no device I/O.

## Notes
This is a diagnostic layout utility. It intentionally computes offsets from null pointer member expressions and prints raw hexadecimal offsets/sizes.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/sizetest/sizetest.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tests/fsck-test.sh -->
# File Research: sources/local-fs/ocfs2-tools/tests/fsck-test.sh

## Purpose
Destructive test driver for `fsck.ocfs2`, using `fswreck` to corrupt a block device and verifying whether `fsck.ocfs2 -fy` repairs it.

## Main Behavior
- Locates tools through `PATH`, `/sbin`, `which`, and wraps commands in `sudo -u root`.
- Creates a timestamped log directory.
- Iterates fswreck corruption codes from `STARTCODE` to `ENDCODE`, defaulting to `0..500`.
- For each valid code:
  - Uses `fswreck -C <code> -M` to obtain mkfs corruption options.
  - Runs `mkfs.ocfs2 -x <opts> -L fswreck <device>`.
  - Runs `fswreck -C <code> <device>`.
  - Runs `fsck.ocfs2 -fy <device>` if corruption succeeded.
  - Logs pass/fail and per-code output.
- Stops when `fswreck -L <code>` fails, treating that as no more valid corruption codes.

## Dependencies
- Root privileges via `sudo`.
- A real block device supplied with `-d`; script refuses non-block devices.
- `mkfs.ocfs2`, `fsck.ocfs2`, `fswreck`, `chown`, `date`, `mkdir`, `seq`.

## Safety Notes
This script formats and corrupts the specified block device. It is not safe for mounted or valuable data devices.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tests/fsck-test.sh -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tests/mkfs-test.sh -->
# File Research: sources/local-fs/ocfs2-tools/tests/mkfs-test.sh

## Purpose
Destructive mkfs regression test driver for `mkfs.ocfs2`, followed by fsck and metadata verification.

## Main Behavior
- Creates timestamped logs and counts pass/fail tests.
- Tests combinations of block size and cluster size:
  - block sizes: `512 1024 2048 4096`
  - cluster sizes: `4096` through `1048576`
  - formats with `mkfs.ocfs2 -x -M local -L mkfstest -b ... -C ...`
  - verifies with `fsck.ocfs2 -fy` and `tunefs.ocfs2 -Q "B=%B;C=%T;"`
- Tests journal sizes `4M`, `64M`, `128M`, `256M`, verifying journal inode size with `debugfs.ocfs2`.
- Tests node slot counts `2 8 16 32 64 128 255`, verifying with `tunefs.ocfs2 -Q "N=%N;"`.
- Tests fstype profiles `mail`, `datafiles`, and `vmstore`.
- Tests short and maximum-length volume labels, verifying with `tunefs.ocfs2 -Q "V=%V;"`.
- Tests UUID input in compact and hyphenated forms.

## Dependencies
- Root privileges via `sudo`.
- A real block device supplied with `-d`; script refuses non-block devices.
- `mkfs.ocfs2`, `fsck.ocfs2`, `tunefs.ocfs2`, `debugfs.ocfs2`, `awk`, shell utilities.

## Safety Notes
This script repeatedly formats the target block device. It is destructive by design.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tests/mkfs-test.sh -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/Makefile -->
# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/Makefile

## Purpose
Builds the `tunefs.ocfs2` implementation, its internal helper library `libocfs2ne.a`, the `o2cluster` utility, man pages, and optional debug executables.

## Main Behavior
- Defines internal libraries:
  - `libtools-internal`
  - `libocfs2`
  - `libo2dlm`
  - `libo2cb`
- Adds conditional `-ldlm_lt` and `-lcmap` based on build support.
- Builds `libocfs2ne.a` from `libocfs2ne.c` and generated `o2ne_err.o`.
- Lists all `OCFS2NE_FEATURES`, including backup super, sparse files, xattr, quota, clusterinfo, append dio, etc.
- Lists `OCFS2NE_OPERATIONS`, such as query, resize, label, journal size, slot count, cluster stack update, and quota sync interval.
- Builds `ocfs2ne`, then hard-links `tunefs.ocfs2` to it.
- Builds `o2cluster` separately.
- Generates `o2ne_err.c` and `o2ne_err.h` from `o2ne_err.et`.
- Supports optional `DEBUG_EXE` binaries for selected operation/feature source files.

## Dependencies
- Project top-level make infrastructure.
- `compile_et` for com_err table generation.
- OCFS2, O2CB, O2DLM, UUID, AIO, com_err, and internal tools libraries.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_append_dio.c -->
# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_append_dio.c

## Purpose
Implements `tunefs.ocfs2` enable/disable support for the append direct I/O incompat feature.

## Main Behavior
- `enable_append_dio()`:
  - No-ops if `ocfs2_supports_append_dio()` is already true.
  - Prompts via `tools_interact()`.
  - Sets `OCFS2_FEATURE_INCOMPAT_APPEND_DIO`.
  - Writes the superblock with signals blocked.
- `disable_append_dio()`:
  - No-ops if feature is absent.
  - Prompts.
  - Clears the incompat bit and writes the superblock.
- Defines `append_dio_feature` with `TUNEFS_FLAG_RW | TUNEFS_FLAG_ONLINE`.

## Dependencies
- `ocfs2/ocfs2.h` feature helpers.
- `libocfs2ne.h` tunefs framework, progress, signal-block wrappers, and feature macros.

## Notes
This feature is a pure superblock flag toggle; it performs no inode or allocator migration.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_append_dio.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_backup_super.c -->
# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_backup_super.c

## Purpose
Implements enabling and disabling backup superblock support.

## Main Behavior
- `empty_backup_supers()` clears known backup superblock locations.
- `fill_backup_supers()` writes backup superblocks to known offsets.
- `disable_backup_super()`:
  - No-ops if `OCFS2_FEATURE_COMPAT_BACKUP_SB` is absent.
  - Prompts, clears backup superblock locations, clears compat bit, writes superblock.
- `check_backup_offsets()`:
  - Gets backup super offsets.
  - Loads the global bitmap.
  - Verifies backup locations are not already allocated.
  - Refuses enable when the volume is too small or locations are in use.
- `enable_backup_super()`:
  - No-ops if already enabled.
  - Prompts, checks offsets, writes backup supers, sets compat bit, writes superblock.
- Defines `backup_super_feature` as compat feature with `TUNEFS_FLAG_RW | TUNEFS_FLAG_ALLOCATION`.

## Dependencies
- OCFS2 backup superblock APIs.
- Global bitmap system inode and chain allocator loading.
- Tunefs progress and signal-blocking helpers.

## Notes
Enable does real allocation-safety checking before writing backup blocks. Disable frees/clears backup locations before clearing the feature flag.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_backup_super.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_clusterinfo.c -->
# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_clusterinfo.c

## Purpose
Toggles the clusterinfo incompat feature and synchronizes cluster descriptor metadata.

## Main Behavior
- `enable_clusterinfo()`:
  - No-ops if feature is already set.
  - Prompts.
  - Sets `OCFS2_FEATURE_INCOMPAT_CLUSTERINFO`.
  - Clears `OCFS2_FEATURE_INCOMPAT_USERSPACE_STACK` because clusterinfo supersedes it.
  - Reads the running cluster descriptor and writes it to disk via `ocfs2_set_cluster_desc()`.
- `disable_clusterinfo()`:
  - No-ops if feature is absent.
  - Prompts.
  - If the superblock still indicates a userspace stack, re-sets `USERSPACE_STACK`.
  - Clears `CLUSTERINFO` and writes the superblock.
- Defines `clusterinfo_feature` with `TUNEFS_FLAG_RW`.

## Dependencies
- O2CB cluster descriptor APIs.
- OCFS2 cluster stack feature helpers.
- Tunefs progress and signal wrappers.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_clusterinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_discontig_bg.c -->
# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_discontig_bg.c

## Purpose
Enables or disables discontiguous block group support.

## Main Behavior
- `enable_discontig_bg()` is a superblock incompat flag set after prompt.
- Disable path is more restrictive:
  - Scans every inode allocator and extent allocator chain for every slot.
  - `check_discontig_bg()` reads each group descriptor.
  - If any descriptor is actually discontiguous, disable aborts.
  - If a non-discontiguous descriptor uses the newer `bg_size`, records it for later conversion.
  - `change_bg_size()` rewrites recorded group descriptors back to old-style bitmap size.
  - Clears `OCFS2_FEATURE_INCOMPAT_DISCONTIG_BG` and writes the superblock.
- Defines `discontig_bg_feature` with `TUNEFS_FLAG_RW | TUNEFS_FLAG_ALLOCATION | TUNEFS_FLAG_LARGECACHE`.

## Dependencies
- OCFS2 chain iteration, group descriptor read/write, and bitmap-size helpers.
- Tunefs allocator checks and large cache support.

## Notes
Disabling is only possible when no actual discontiguous block groups exist. The code can normalize compatible group descriptors but will not migrate truly discontiguous allocation groups.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_discontig_bg.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_extended_slotmap.c -->
# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_extended_slotmap.c

## Purpose
Toggles the extended slot map incompat feature.

## Main Behavior
- `enable_extended_slotmap()`:
  - No-ops if extended slot map is already in use.
  - Sets `OCFS2_FEATURE_INCOMPAT_EXTENDED_SLOT_MAP`.
  - Calls `ocfs2_format_slot_map()` to rewrite the slot map in the new format.
  - Writes the superblock.
- `disable_extended_slotmap()`:
  - No-ops if old-style slot map is already in use.
  - Clears the feature bit.
  - Calls `ocfs2_format_slot_map()` to rewrite old-style slot map data.
  - Writes the superblock.
- Defines `extended_slotmap_feature` with `TUNEFS_FLAG_RW | TUNEFS_FLAG_ALLOCATION`.

## Dependencies
- OCFS2 slot map formatting and feature helpers.
- Tunefs signal and progress helpers.

## Notes
The feature bit is changed before formatting so `ocfs2_format_slot_map()` sees the target layout.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_extended_slotmap.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_indexed_dirs.c -->
# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_indexed_dirs.c

## Purpose
Enables or disables directory indexing.

## Main Behavior
- Enable:
  - Seeds `s_uuid_hash` if xattr is not enabled.
  - Generates three random `s_dx_seed` values.
  - Sets `OCFS2_FEATURE_INCOMPAT_INDEXED_DIRS`.
  - Writes the superblock.
  - Scans all valid inodes.
  - For each directory, truncates any stale indexed tree, installs directory trailers, then builds a dx/index tree.
- Disable:
  - Scans all directories with `OCFS2_INDEXED_DIR_FL` into a list.
  - Truncates each indexed tree with `ocfs2_dx_dir_truncate()`.
  - Clears the indexed dirs feature.
  - Clears `s_uuid_hash` only if xattr is not using it.
  - Clears `s_dx_seed[]`.
  - Writes the superblock.
- Defines `indexed_dirs_feature` with `TUNEFS_FLAG_RW | TUNEFS_FLAG_ALLOCATION`.

## Dependencies
- `tunefs_foreach_inode()`.
- Directory trailer helpers from `libocfs2ne.c`.
- OCFS2 dx directory APIs.
- Kernel list helpers.

## Notes
Disable intentionally clears the feature even if truncation encountered work already done; comments state `fsck.ocfs2` handles orphan indexed trees after touched filesystem state.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_indexed_dirs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_inline_data.c -->
# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_inline_data.c

## Purpose
Enables or disables inline data support.

## Main Behavior
- Enable:
  - No-ops if already supported.
  - Prompts, sets `OCFS2_FEATURE_INCOMPAT_INLINE_DATA`, writes superblock.
- Disable:
  - Scans regular files and directories with `OCFS2_INLINE_DATA_FL`.
  - Counts one additional cluster per inline-data inode and verifies free space.
  - Converts each inline-data inode to extent-backed storage with `ocfs2_convert_inline_data_to_extents()`.
  - Loads quota info and applies quota usage changes for non-system files and the root inode.
  - Clears the inline-data incompat bit and writes the superblock.

## Dependencies
- `tunefs_foreach_inode()` and `tunefs_get_free_clusters()`.
- OCFS2 cached inode, inline conversion, quota change APIs.
- Kernel list helpers.

## Notes
Disable is a data migration. It requires enough free clusters to expand all inline data and updates quota accounting for cluster changes.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_inline_data.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_local.c -->
# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_local.c

## Purpose
Switches an OCFS2 filesystem between local single-node mode and cluster-aware mode.

## Main Behavior
- `enable_local()`:
  - No-ops if already local.
  - Prompts.
  - Sets `OCFS2_FEATURE_INCOMPAT_LOCAL_MOUNT`.
  - Clears `OCFS2_FEATURE_INCOMPAT_USERSPACE_STACK`.
  - Writes superblock.
- `disable_local()`:
  - No-ops if already cluster-aware.
  - Prompts.
  - Initializes O2CB because local filesystems are not connected during `tunefs_open()`.
  - Reads the running cluster descriptor.
  - Clears local mount bit.
  - Writes the cluster descriptor to disk with `ocfs2_set_cluster_desc()`.

## Dependencies
- O2CB running cluster discovery.
- OCFS2 local mount and cluster descriptor helpers.
- Tunefs progress and signal wrappers.

## Notes
`disable_local()` contains two consecutive `tunefs_block_signals()` calls around `ocfs2_set_cluster_desc()` where the second likely intended to unblock. That affects signal-block nesting but later process cleanup may still finish normally.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_local.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_metaecc.c -->
# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_metaecc.c

## Purpose
Enables or disables metadata ECC support.

## Main Behavior
- Enable:
  - Scans all inodes and metadata into an rb-tree of `block_to_ecc` records.
  - Stores write callbacks per block type: dinode, extent block, group descriptor, directory block.
  - Defers chain allocator scanning until after directory trailer installation because trailer work may allocate.
  - For directories without trailers, prepares trailer contexts and estimates extra blocks/clusters needed.
  - Verifies sufficient free clusters.
  - Sets `OCFS2_TUNEFS_INPROG_DIR_TRAILER` while installing trailers.
  - Installs directory trailers using `tunefs_install_dir_trailer()`.
  - Clears the in-progress bit.
  - Scans chain allocator group descriptors.
  - Sets `OCFS2_FEATURE_INCOMPAT_META_ECC` in memory.
  - Rewrites collected metadata blocks so checksums/ECC match the new feature state.
  - Writes the superblock.
- Disable:
  - Clears `OCFS2_FEATURE_INCOMPAT_META_ECC` and writes the superblock.
  - Does not remove directory trailers or rewrite all metadata.

## Dependencies
- OCFS2 rb-tree and kernel-list helpers.
- `tunefs_prepare_dir_trailer()` and `tunefs_install_dir_trailer()`.
- OCFS2 inode, extent, chain, group descriptor, directory block APIs.
- Tunefs in-progress flag helpers.

## Notes
The enable path is one of the most complex migrations in this group. It deliberately caches metadata before writing and uses an in-progress bit for directory trailer installation so fsck can reason about interruption.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_metaecc.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_quota.c -->
# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_quota.c

## Purpose
Enables and disables user and group quota features.

## Main Behavior
- `create_system_file()` creates missing quota system inodes and links them in the system directory.
- `create_quota_files()`:
  - Creates the global quota file and per-slot local quota files.
  - Initializes global and local quota files.
  - Computes current quota usage by scanning the filesystem.
  - Writes quota usage to disk.
- `remove_quota_files()` iterates the system directory and deletes matching `aquota.user`, `aquota.group`, and per-slot suffixed files.
- `enable_usrquota()` / `enable_grpquota()` create quota files and set the matching RO-compatible feature bit.
- `disable_usrquota()` / `disable_grpquota()` delete quota files and clear the matching feature bit.
- Defines two features:
  - `usrquota_feature`
  - `grpquota_feature`

## Dependencies
- OCFS2 quota APIs, system inode creation/linking, directory iteration, inode truncation/delete.
- Tunefs progress, signal blocking, and allocator checks.

## Notes
Quota enable is not just a superblock flag: it materializes quota system files and computes initial usage. Disable removes quota files from the system directory.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_quota.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_refcount.c -->
# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_refcount.c

## Purpose
Enables or disables refcount tree support.

## Main Behavior
- Enable:
  - No-ops if already enabled.
  - Prompts, sets `OCFS2_FEATURE_INCOMPAT_REFCOUNT_TREE`, writes superblock.
- Disable:
  - Scans regular non-system inodes with `OCFS2_HAS_REFCOUNT_FL`.
  - Groups files by `i_refcount_loc` in an rb-tree of refcount blocks.
  - Counts refcounted data and xattr clusters, estimating space needed to COW shared clusters and extra extent blocks.
  - Verifies enough free space.
  - For each file, calls `ocfs2_refcount_cow()` for data and COWs refcounted xattr value clusters.
  - Clears per-inode refcount dynamic feature and `i_refcount_loc`.
  - Verifies/refuses unexpected non-empty refcount tree state through assertions, then deletes empty refcount blocks.
  - Clears the incompat feature and writes the superblock.

## Dependencies
- OCFS2 rb-tree/list helpers.
- OCFS2 refcount, xattr iterate, cached inode, and extent APIs.
- Tunefs free-space and progress helpers.

## Notes
Disable is a full copy-on-write materialization pass. It needs enough free space to break sharing before the global feature bit can be cleared.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_refcount.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_sparse_files.c -->
# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_sparse_files.c

## Purpose
Enables or disables sparse file support.

## Main Behavior
- Enable:
  - Scans regular non-system, non-inline files and truncates allocations beyond `i_size`.
  - Sets `OCFS2_FEATURE_INCOMPAT_SPARSE_ALLOC`.
  - Writes the superblock.
- Disable:
  - Refuses to proceed if unwritten extents are enabled.
  - Scans regular non-system, non-inline files.
  - Records holes inside `i_size`, files requiring truncate-to-size, hole counts, needed data clusters, and estimated extent-block clusters.
  - Verifies free space can fill all holes and metadata needs.
  - Allocates clusters for each hole, zeroes them, inserts extents, and optionally truncates tail allocation.
  - Applies quota changes when cluster counts change.
  - Clears the sparse allocation feature and writes the superblock.

## Dependencies
- OCFS2 extent lookup/insertion, allocation, truncate, quota, and cached inode APIs.
- Tunefs inode scanning, free-space checks, and zero-fill helper.
- Kernel list helpers.

## Notes
Disable converts sparse holes into real zero-filled extents. It explicitly rejects sparse disable while unwritten extents remain enabled.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_sparse_files.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_unwritten_extents.c -->
# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_unwritten_extents.c

## Purpose
Enables or disables unwritten extent support.

## Main Behavior
- Enable:
  - No-ops if already enabled.
  - Requires sparse files to be enabled; otherwise returns `TUNEFS_ET_SPARSE_MISSING`.
  - Sets `OCFS2_FEATURE_RO_COMPAT_UNWRITTEN` and writes the superblock.
- Disable:
  - Scans regular, non-system, non-inline files.
  - For each extent marked `OCFS2_EXT_UNWRITTEN`, verifies/zero-checks the physical clusters through `tunefs_empty_clusters()`, then marks the extent written with `ocfs2_mark_extent_written()`.
  - Clears the RO-compatible feature and writes the superblock.

## Dependencies
- OCFS2 extent lookup and mark-written APIs.
- Tunefs inode scanning and zero-fill helper.

## Notes
Disable turns every unwritten extent into a written extent before clearing feature support.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_unwritten_extents.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_xattr.c -->
# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_xattr.c

## Purpose
Enables or disables extended attribute support.

## Main Behavior
- Enable:
  - No-ops if already enabled.
  - Sets `s_uuid_hash` if indexed dirs are not using it.
  - Sets `s_xattr_inline_size` to `OCFS2_MIN_XATTR_INLINE_SIZE`.
  - Sets `OCFS2_FEATURE_INCOMPAT_XATTR`.
  - Writes superblock.
- Disable:
  - Scans regular files, directories, and symlinks with `OCFS2_HAS_XATTR_FL`.
  - Removes inline xattr values, external xattr blocks, indexed xattr buckets, and xattr value trees.
  - Deletes external xattr blocks.
  - Adjusts inline-data capacity or extent-list count after inline xattr removal.
  - Clears per-inode xattr dynamic flags and `i_xattr_loc`.
  - Clears global xattr metadata fields and feature bit.
  - Writes superblock.

## Dependencies
- OCFS2 xattr block, bucket, tree, and value truncation APIs.
- Tunefs inode scanning and progress helpers.
- Kernel list helpers.

## Notes
Disable deletes all xattrs. It preserves `s_uuid_hash` if indexed directories still need it.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/feature_xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/libocfs2ne.c -->
# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/libocfs2ne.c

## Purpose
Shared implementation library for `tunefs.ocfs2` operations and debug feature executables. It handles filesystem opening, locking, signal safety, journal checks, allocator validation, online operation detection, feature/operation dispatch, and directory trailer migration support.

## Main Components
- `tunefs_filesystem_state` tracks the master filesystem, local exclusive fd, online mount fd, cluster lock status, allocator use, resized cluster count, max journal size, and journal feature bits.
- `tunefs_private` attaches per-open flags and shared state to each `ocfs2_filesys`.
- Global `fs_list` tracks all open filesystems for signal cleanup.
- Signal blocking uses a nesting counter around sensitive metadata writes.

## Operation Helpers
- `tunefs_get_number()` parses numeric strings with `K/M/G/T/P/B` suffixes.
- `tunefs_set_in_progress()` and `tunefs_clear_in_progress()` update resize/tunefs in-progress superblock bits.
- `tunefs_set_journal_size()` resizes every journal and optionally changes journal feature bits.
- `tunefs_empty_clusters()` writes zero blocks over a cluster range, falling back to smaller buffers on memory pressure.
- `tunefs_get_free_clusters()` reads global bitmap accounting.
- `tunefs_foreach_inode()` scans valid inodes and calls a supplied callback.

## Directory Trailer Support
- `tunefs_prepare_dir_trailer()` scans directory blocks, computes dirents that must move to make trailer space, and records affected blocks.
- `tunefs_install_dir_trailer()` optionally expands the directory, initializes new blocks with trailers, moves live dirents, writes new blocks first, then inode size, then modified old dirblocks.
- The write order is designed so interruption can leave duplicates but not lost entries, allowing fsck cleanup.

## Opening And Locking
- `tunefs_open()` wraps `ocfs2_open()` with tunefs safety checks:
  - Rejects heartbeat devices, resize-in-progress, and tunefs-in-progress for rw opens.
  - Uses `O_EXCL` for local filesystems.
  - Uses O2CB/O2DLM cluster locking for clustered filesystems.
  - Converts mounted rw volumes to online mode if the operation supports it.
  - Checks dirty journals for offline operations.
  - Opens the mount point for online ioctl operations.
  - Initializes a shared I/O cache when safe.
- `tunefs_close()` closes online descriptors, validates allocators after allocation operations, unlocks local/cluster state, removes private state, and closes the filesystem.

## Integrity Checks
- Allocation operations trigger global bitmap/chain validation on open and again on master close.
- Journal checks collect largest journal size and journal feature bits and reject dirty journals for offline operations.

## Dispatch
- `tunefs_feature_run()` opens a fresh filesystem for a feature, maps special open outcomes into operation flags, runs enable/disable, and closes.
- `tunefs_op_run()` does the same for generic operations.
- `tunefs_feature_main()` and `tunefs_op_main()` support standalone debug executables with common option parsing.

## Dependencies
- OCFS2 filesystem, inode, journal, allocator, DLM, mount, and I/O cache APIs.
- O2CB/O2DLM error tables and cluster stack support.
- `tools-internal` verbose/progress/interactive behavior.
- `libocfs2ne.h` public API and `o2ne_err.h` errors.

## Notes
This file is the safety core for the tunefs feature files. Feature implementations depend on it for clean-journal enforcement, locking, allocator validation, signal cleanup, and online/offline operation routing.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/libocfs2ne.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/libocfs2ne.h -->
# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/libocfs2ne.h

## Purpose
Public header for the `tunefs.ocfs2` helper library and feature/operation plugin framework.

## Main Content
- Defines open flags:
  - `TUNEFS_FLAG_RO`
  - `TUNEFS_FLAG_RW`
  - `TUNEFS_FLAG_ONLINE`
  - `TUNEFS_FLAG_NOCLUSTER`
  - `TUNEFS_FLAG_ALLOCATION`
  - `TUNEFS_FLAG_SKIPCLUSTER`
  - `TUNEFS_FLAG_LARGECACHE`
- Defines `enum tunefs_feature_action`.
- Defines `struct tunefs_feature`, including feature name, feature bits, open flags, enable/disable callbacks, and selected action.
- Provides `DEFINE_TUNEFS_FEATURE_COMPAT`, `DEFINE_TUNEFS_FEATURE_RO_COMPAT`, and `DEFINE_TUNEFS_FEATURE_INCOMPAT`.
- Defines `struct tunefs_operation` and `DEFINE_TUNEFS_OP`.
- Declares shared helpers for initialization, signal blocking, in-progress bits, number parsing, journal sizing, free-space lookup, zeroing clusters, online ioctl, DLM locks, inode scanning, open/close, operation/feature dispatch, and debug main functions.
- Defines `struct tunefs_trailer_context` and declares directory trailer helpers.

## Design Notes
The header documents expected behavior for feature and operation modules: idempotence, `tools_interact()` before writes, quiet normal operation, and use of shared verbose/error/progress APIs.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/libocfs2ne.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/o2cluster.8.in -->
# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/o2cluster.8.in

## Purpose
Manual page template for `o2cluster(8)`.

## Main Content
- Describes `o2cluster` as a utility for changing or listing the cluster stack stamped on an OCFS2 filesystem.
- Documents:
  - `--show-ondisk`
  - `--show-running`
  - `--update[=<clusterstack>]`
  - `--verbose`
  - `--version`
  - `--yes`
  - `--no`
- Explains cluster stack formats:
  - `default`
  - `<stack>,<cluster>,<hbmode>`, e.g. `o2cb,mycluster,global`
- Lists valid stacks: `o2cb`, `pcmk`, `cman`.
- Explains heartbeat modes: `local`, `global`, and `none`.
- Warns that clean journals are used as a safety signal, but there remains a race before updating the on-disk cluster stack.
- Advises running `fsck.ocfs2` after dirty journal scenarios.

## Notes
The section header `.SH "SPECIFYING CLUSTER STACK` is missing a closing quote in the template.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/o2cluster.8.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/o2cluster.c -->
# File Research: sources/local-fs/ocfs2-tools/tunefs.ocfs2/o2cluster.c

## Purpose
Implements `o2cluster`, a utility to list or update the cluster stack descriptor stamped on an OCFS2 filesystem.

## Main Behavior
- Supports tasks:
  - `--show-running`: print active cluster stack.
  - `--show-ondisk <device>`: print cluster stack stored on disk.
  - `--update[=<clusterstack>] <device>`: update on-disk cluster stack, using the running cluster if no argument is supplied.
- `parse_cluster_info()` accepts:
  - `default`
  - `<stack>,<cluster>,<hbmode>`
  - validates stack names, cluster names, and heartbeat modes.
- `fs_open()` opens the device rw with strict compatibility checks and heartbeat-device allowance.
- `journal_check()` scans all journal system inodes and aborts if any journal is dirty.
- `do_update()`:
  - Opens the filesystem.
  - Refuses local/non-clustered filesystems.
  - Refuses dirty journals.
  - Reads current on-disk descriptor.
  - No-ops when requested descriptor already matches.
  - Prompts before changing descriptor.
  - Writes via `ocfs2_set_cluster_desc()`.
- `do_list_ondisk()` refuses local filesystems, then prints descriptor.
- `do_list_active()` initializes O2CB and prints the running descriptor.
- Installs signal handlers and initializes error tables/verbosity in `tool_init()`.

## Dependencies
- OCFS2 open, journal/system inode, bitops, mount/cluster descriptor APIs.
- O2CB cluster stack APIs.
- O2DLM/O2CB/OCFS2 error tables.
- `tools-internal` verbose/progress/interactive helpers.

## Safety Notes
The tool intentionally refuses updates if journals are dirty because it cannot distinguish an active mount from an unrecovered crash without joining the cluster. It still has a documented race between clean-journal check and another node mounting with the old cluster stack.
<!-- END FILE RESEARCH: sources/local-fs/ocfs2-tools/tunefs.ocfs2/o2cluster.c -->