# Group Research: group_460_gfs2_utils_sources_local_fs_gfs2_utils_gfs2_mkfs_main_mkfs_c_sources_9f20fbad8c85

Scope: `Docs/research_subset_a.md`, source tree `sources/local-fs/gfs2-utils`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/mkfs/main_mkfs.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/mkfs/main_mkfs.c

Primary implementation of `mkfs.gfs2`. It parses CLI options, opens and probes the target device, chooses filesystem geometry, creates journals/resource groups, builds core metadata files, writes the superblock, syncs, and prints the final summary.

Key local types are `struct mkfs_dev`, which stores file descriptor, path, stat data, size, and blkid topology values, and `struct mkfs_opts`, which stores all parsed user options plus "got_*" flags. Global state is limited to `nrgrp` and `mkfs_journals`.

Important entry points and helpers:
- `opts_init`, `opts_get`, `opts_check`, `opt_parse_extended`: default and validate options.
- `test_locking`: validates `lock_dlm`, `lock_gulm`, and `lock_nolock` lock protocol/table combinations.
- `open_dev`, `probe_contents`, `choose_blocksize`: open with `O_EXCL`, use blkid probing, and choose a block size from user input or topology.
- `sbd_init`: fills `struct lgfs2_sbd`, parses/generates UUID, computes constants, validates requested filesystem and journal sizes.
- `rgs_init`, `add_rgrp`, `place_journals`, `place_rgrps`, `place_rgrp`, `zero_gap`: plan and write aligned resource groups and journal files.
- `create_jindex`, `build_per_node`: build journal index and per-node metadata.
- `main`: full mkfs transaction from option parsing to final superblock write.

Dependencies are heavy on `libgfs2` for GFS2 metadata construction, resource group planning/writing, inode creation, journal data, statfs/inum initialization, and superblock output. It also uses `libblkid` for content/topology probing, `libuuid` for UUID handling, gettext for messages, and Linux block discard ioctl support.

Behavioral flow:
1. Initialize locale/gettext and default options.
2. Parse short options and extended `-o` options including `sunit`, `swidth`, `align`, `format`, `root_inherit_jdata`, and hidden `test_topology`.
3. Validate lock table, resource group size, journal count/size, quota change size, and stripe option pairing.
4. Open target device/file exclusively, probe contents/topology unless test topology was supplied, and choose block size.
5. Warn and optionally confirm destructive formatting, then issue discard unless disabled.
6. Place journal resource groups first, then regular resource groups, tracking journal inums for `jindex`.
7. Build master directory, `jindex`, `per_node`, inum/statfs/rindex/quota/root metadata.
8. Set lock protocol/table, initialize inum/statfs state, free metadata/rgrp structures, write the superblock, `fsync`, close, and print results.

Notable edge handling:
- Regular files are accepted and use their file size; block devices use `lseek(SEEK_END)`.
- Requested filesystem size is in filesystem blocks and must fit in the target.
- User journal sizes cannot consume more than half the filesystem after multiplying by journal count.
- `-O` suppresses the confirmation prompt but does not suppress warnings.
- Debug mode prints on-disk metadata structures via `struct_print.c`.

Research notes:
- This file is the central mkfs orchestrator. Most actual on-disk structure creation is delegated to `libgfs2`.
- The file intentionally supports test-only topology injection and `UNITTESTS` exclusion of `main`.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/mkfs/main_mkfs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/mkfs/metafs.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/mkfs/metafs.c

Utility code for temporarily mounting the `gfs2meta` filesystem and taking an administrative flock on it.

Key functions:
- `mount_gfs2_meta`: creates `/tmp/.gfs2meta.XXXXXX`, installs signal handlers, mounts `gfs2meta`, and locks the mount directory.
- `cleanup_metafs`: fsyncs/closes the lock fd, unmounts the temporary mount, removes the temp directory, resets signals, and frees path/context memory.
- `copy_context_opt`: extracts a duplicate of the `context=` mount option from an `mntent`.

Internal helpers:
- `lock_for_admin`: opens the metafs path with `O_RDONLY | O_NOFOLLOW` and takes `LOCK_EX`.
- `setsigs` and `sighandler`: mark `metafs_interrupted` on several signals.

Dependencies include mount/umount syscalls, flock, mntent parsing, gettext, and POSIX signal handling.

Research notes:
- The global `metafs_interrupted` lets callers notice asynchronous interruption while admin operations are active.
- Cleanup only proceeds when `mfs->fd > 0`, so fd `0` would be treated as not mounted/locked.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/mkfs/metafs.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/mkfs/metafs.h -->
# File Research: sources/local-fs/gfs2-utils/gfs2/mkfs/metafs.h

Header for the metafs helper API.

Defines:
- `extern int metafs_interrupted`
- `struct metafs { int fd; char *path; char *context; }`

Exports:
- `mount_gfs2_meta`
- `cleanup_metafs`
- `copy_context_opt`

Research notes:
- `context` is documented as the SELinux-style `context=` mount option and is passed through to the `gfs2meta` mount.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/mkfs/metafs.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/mkfs/progress.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/mkfs/progress.c

Small terminal progress display helper adapted from e2fsprogs.

Key functions:
- `gfs2_progress_init`: initializes spacing/backspace buffers, records max count and digit width, prints an optional message unless quiet.
- `gfs2_progress_update`: once per second, if stdout is a tty, prints `[value/max]` and backspaces over it.
- `gfs2_progress_close`: clears tty progress text and prints an optional final message.

Internal state:
- Static `spaces[44]`, `backspaces[44]`
- Static `last_update`, throttling updates to one per second.

Research notes:
- Quiet mode sets `skip_progress`; non-tty stdout also suppresses live progress updates.
- Used by `main_mkfs.c` while adding journals and building resource groups.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/mkfs/progress.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/mkfs/progress.h -->
# File Research: sources/local-fs/gfs2-utils/gfs2/mkfs/progress.h

Header for the mkfs progress bar helper.

Defines `struct gfs2_progress_bar` with:
- `uint64_t max`
- `int max_digits`
- `int skip_progress`

Exports initialization, update, and close functions.

Research notes:
- The header assumes `uint64_t` is already visible to including files.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/mkfs/progress.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/mkfs/struct_print.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/mkfs/struct_print.c

Debug printer for GFS2 on-disk structures. Callers pass raw on-disk buffers or struct pointers, and functions print big-endian fields converted to CPU order.

Key functions:
- `inum_print`
- `meta_header_print`
- `sb_print`
- `rindex_print`
- `rgrp_print`
- `quota_print`
- `dinode_print`
- `leaf_print`
- `log_header_print`
- `log_descriptor_print`
- `statfs_change_print`
- `quota_change_print`

Implementation uses `print_it` plus `printbe16`, `printbe32`, and `printbe64` macros.

Dependencies include `libgfs2`, endian conversion helpers, `uuid_unparse`, and standard printf formatting.

Research notes:
- `main_mkfs.c` uses `dinode_print`, `rindex_print`, and `statfs_change_print` in debug paths.
- These printers are diagnostic only and do not mutate metadata.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/mkfs/struct_print.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/mkfs/struct_print.h -->
# File Research: sources/local-fs/gfs2-utils/gfs2/mkfs/struct_print.h

Header declaring the GFS2 on-disk debug printer functions.

Exports printers for inum, meta header, superblock, dinode, log header/descriptor, quota, quota change, statfs change, leaf, rindex, and rgrp.

Research notes:
- Comment states the functions expect on-disk data, meaning callers must not pass already CPU-endian transformed copies unless they want misleading output.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/mkfs/struct_print.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/scripts/82-gfs2-withdraw.rules.in -->
# File Research: sources/local-fs/gfs2-utils/gfs2/scripts/82-gfs2-withdraw.rules.in

udev rule template for GFS2 withdraw events.

Behavior:
- On `SUBSYSTEM=="gfs2"` and `ACTION=="offline"`, it runs `/bin/sh @libexecdir@/gfs2_withdraw_helper`.

Research notes:
- `@libexecdir@` is replaced by `gfs2/scripts/Makefile.am`.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/scripts/82-gfs2-withdraw.rules.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/scripts/Makefile.am -->
# File Research: sources/local-fs/gfs2-utils/gfs2/scripts/Makefile.am

Automake packaging for GFS2 helper scripts and udev rule generation.

Installs:
- `gfs2_lockcapture` and `gfs2_trace` as `dist_sbin_SCRIPTS`
- `gfs2_withdraw_helper` as `dist_libexec_SCRIPTS`
- Generated `82-gfs2-withdraw.rules` into `@udevdir@/rules.d`

Build rule:
- Generates `82-gfs2-withdraw.rules` from `.in` by replacing `@libexecdir@`.

Research notes:
- `CLEANFILES` removes the generated udev rule.
- `EXTRA_DIST` includes the rule template.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/scripts/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/scripts/gfs2_lockcapture -->
# File Research: sources/local-fs/gfs2-utils/gfs2/scripts/gfs2_lockcapture

Python diagnostic collector for GFS2 and DLM lock information. It discovers cluster identity, finds mounted GFS2 filesystems, collects DLM/GFS2 debugfs data over repeated runs, captures host/process/log diagnostics, archives the output, and cleans up.

Main data model:
- `ClusterNode`: cluster node name/id, cluster name, and mounted GFS2 filesystem label map.

Important helpers:
- Command helpers: `runCommand`, `runCommandOutput`
- File helpers: `writeToFile`, `mkdirs`, `copyFile`, `copyDirectory`, `backupOutputDirectory`, `archiveData`
- Runtime helpers: `mountFilesystem`, `removePIDFile`, `exitScript`
- Cluster discovery: `getClusterNode`, `getMountedGFS2Filesystems`, `getLabelMapForMountedFilesystems`
- DLM discovery: `parse_dlm_ls`, `getGroupToolDLMLockspaces`, `getDLMLockspaces`, `getVerifiedDLMLockspaceNames`
- Collection: `gatherHostData`, `gatherDiagnosticData`, `gatherOptionalDiagnosticData`, `gatherPidData`, `triggerSysRQEvents`, `gatherLogs`, `gatherDLMLockDumps`, `gatherGFS2LockDumps`
- CLI: `OptionParserExtended`, `ExtendOption`, `__getOptions`

Default paths:
- Debugfs: `/sys/kernel/debug`
- PID file: `/var/run/<script>.pid`
- Output root: `/tmp`
- Per-day output: `<output>/gfs2_lockcapture-YYYY-MM-DD`
- Archive: `<outputdir>-<hostname>.tar.bz2`

CLI supports debug/quiet/no-ask/info, process gathering disable, hidden optional diagnostics, output directory, run count, sleep interval, and selected GFS2 filesystem names.

Behavioral flow:
1. Create logger and PID file, preventing concurrent runs.
2. Discover cluster name/node via `cman_tool` or corosync tools.
3. Match mounted GFS2 filesystems by cluster-prefixed mount labels.
4. Optionally print filesystem info and exit.
5. Ask before process stack/sysrq collection unless disabled.
6. Prepare output directory, mounting debugfs if needed.
7. For each run, gather host info, DLM lock dumps, GFS2 lock dumps, process stacks or sysrq traces, logs, and diagnostics.
8. Sleep between runs.
9. Compress output and remove uncompressed directory if archive succeeds.

Research notes:
- The script is compatibility-oriented and uses old cluster tooling (`cman_tool`, `group_tool`) plus corosync alternatives.
- `ExtendOption.take_action` appears to append the whole comma string once per comma item instead of appending each split item, because it uses `value.strip()` instead of `v.strip()`.
- It may trigger sysrq `t`, so it is operationally invasive.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/scripts/gfs2_lockcapture -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/scripts/gfs2_trace -->
# File Research: sources/local-fs/gfs2-utils/gfs2/scripts/gfs2_trace

Python tool for listing, enabling, disabling, and capturing GFS2 ftrace trace events.

Main classes:
- `FileUtils`: static file read/write helpers.
- `TraceEvent`: wraps one trace event directory and reads/writes `enable`, reads `filter`, `format`, and `id`.
- `TraceEvents`: discovers all event directories under `/sys/kernel/debug/tracing/events/gfs2`.

Default paths:
- Debugfs: `/sys/kernel/debug`
- GFS2 trace events: `/sys/kernel/debug/tracing/events/gfs2`
- Trace pipe: `/sys/kernel/debug/tracing/trace_pipe`
- PID file: `/var/run/<script>.pid`

CLI supports:
- `-l`: list event enable states.
- `-E`: enable all GFS2 trace events.
- `-e`: enable selected comma-separated events.
- `-N`: disable all.
- `-n`: disable selected comma-separated events.
- `-c`: capture `trace_pipe` output to a file, then archive it as `.tar.bz2`.
- `-d`, `-q`: debug/quiet logging.

Behavioral flow:
1. Parse options and configure logger.
2. Create PID file, refusing concurrent execution.
3. Require at least one mounted GFS2 filesystem from `/proc/mounts`.
4. Mount debugfs if not already mounted.
5. Discover trace event directories.
6. Optionally list current states.
7. Apply all-event and selected-event enable/disable operations.
8. If capture requested, read `trace_pipe` until EOF or Ctrl-C, write output file, then bzip2 tar it.
9. Remove PID file and exit.

Research notes:
- The script writes directly to kernel tracing control files and therefore needs suitable privileges.
- `TraceEvent.setEventEnable` only accepts `"0"` or `"1"`.
- `ExtendOption` here correctly appends each split comma value.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/scripts/gfs2_trace -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/scripts/gfs2_withdraw_helper -->
# File Research: sources/local-fs/gfs2-utils/gfs2/scripts/gfs2_withdraw_helper

Shell helper invoked by the GFS2 withdraw udev rule. It is not intended for manual use.

Behavior:
1. Validates udev environment: `SUBSYSTEM=gfs2`, `LOCKPROTO=lock_dlm`, nonempty `DEVPATH`, and `ACTION=offline`.
2. Builds `SYSFS_TOPDIR=/sys$DEVPATH`.
3. Reads device-mapper name from `$SYSFS_TOPDIR/device/dm/name`.
4. Builds `/dev/mapper/$DM_NAME`.
5. Attempts device suspension with `dmsetup suspend`.
6. If `$SYSFS_TOPDIR/lock_module/withdraw` exists, writes `1` to acknowledge withdraw completion.

Research notes:
- The test `if [ -z "$DM_DEV" ]` is suspicious because `DM_DEV` is assigned `/dev/mapper/$DM_NAME`, so it is normally nonempty even when `DM_NAME` is empty. That condition likely prevents suspension in normal cases.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/scripts/gfs2_withdraw_helper -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/tune/Makefile.am -->
# File Research: sources/local-fs/gfs2-utils/gfs2/tune/Makefile.am

Automake definition for the `tunegfs2` utility.

Builds:
- `sbin_PROGRAMS = tunegfs2`
- Sources: `main.c`, `super.c`
- Header: `tunegfs2.h`

Links:
- `gfs2/libgfs2/libgfs2.la`
- `$(LTLIBINTL)`
- `$(uuid_LIBS)`

Conditional:
- Includes `checks.am` when `HAVE_CHECK` is true.

Research notes:
- The tune utility is smaller than mkfs and primarily edits/list superblock fields.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/tune/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/tune/check_tune.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/tune/check_tune.c

Minimal Check framework unit test for `tunegfs2`.

Behavior:
- Defines `test_tune_stub`, which only asserts true.
- Creates suite `main.c`, testcase `tunegfs2`, and runs it with `CK_ENV`.

Research notes:
- This is a build/smoke placeholder, not behavioral coverage for tune operations.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/tune/check_tune.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/tune/checks.am -->
# File Research: sources/local-fs/gfs2-utils/gfs2/tune/checks.am

Automake test wiring for `tunegfs2`.

Defines:
- `TESTS = check_tune`
- `check_PROGRAMS = $(TESTS)`
- `check_tune_SOURCES = $(tunegfs2_SOURCES) check_tune.c`
- Adds `-DUNITTESTS` and `-Wno-unused-function`
- Links with tune dependencies plus Check libraries.

Research notes:
- `UNITTESTS` excludes the real `main` from `gfs2/tune/main.c`.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/tune/checks.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/tune/main.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/tune/main.c

CLI front end for `tunegfs2`, a utility to list and modify selected GFS2 superblock fields.

Global state:
- Static `struct tunegfs2 tunegfs2_struct`
- Static pointer `tfs`

Key functions:
- `parse_mount_options`: parses `lockproto=` and `locktable=` mount-style option fragments.
- `usage`: prints syntax.
- `version`: prints `tunegfs2` version.
- `main`: parses options, opens device, reads superblock, applies requested mutations, writes back if needed, and/or lists fields.

Supported options:
- `-L <label>`: change lock table label form.
- `-U <UUID>`: change filesystem UUID.
- `-l`: list current superblock values, opens read-only.
- `-o <mount options>`: parse `lockproto=` and `locktable=`.
- `-r <version>`: change filesystem format version.
- `-V`, `-h`: version/help.

Dependencies:
- `tunegfs2.h`
- `super.c` operations
- gettext, sysexits, POSIX open/close.

Research notes:
- `-L` cannot be combined with `locktable` from `-o`.
- Writes the superblock only when a mutation option is present.
- `main` is excluded under `UNITTESTS`.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/tune/main.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/tune/super.c -->
# File Research: sources/local-fs/gfs2-utils/gfs2/tune/super.c

Implements `tunegfs2` superblock read, print, modify, and write operations.

Key functions:
- `read_super`: reads the default block-sized superblock from `GFS2_SB_ADDR << GFS2_BASIC_BLOCK_SHIFT`, checks `GFS2_MAGIC`, and null-terminates lock strings.
- `print_super`: prints volume name, UUID, magic, format, block size/shift, root inode, master inode for GFS2, lock protocol, and lock table.
- `write_super`: writes the in-memory superblock back at `sb_start`.
- `change_uuid`: validates and copies UUID.
- `change_lockproto`: accepts only `lock_dlm` or `lock_nolock`, within `GFS2_LOCKNAME_LEN`.
- `change_locktable`: validates length and, for `lock_dlm`, colon structure and filesystem name length.
- `change_format`: parses and validates filesystem format, disallowing regression.

Dependencies:
- `libgfs2` for constants and endian helpers.
- `libuuid` for UUID parse/unparse.
- `sysexits` for return codes.

Research notes:
- `read_super` allocates `tfs->sb`; ownership persists in the `tunegfs2` struct.
- `change_format` permits forward format changes only within `LGFS2_FS_FORMAT_VALID`.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/tune/super.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/tune/tunegfs2.h -->
# File Research: sources/local-fs/gfs2-utils/gfs2/tune/tunegfs2.h

Shared header for `tunegfs2`.

Defines `struct tunegfs2`, carrying:
- Device name, fd, superblock offset, and `struct gfs2_sb *sb`
- Pending string values for UUID, label, table, proto, mount options, format
- Boolean option flags for list, label, UUID, proto, table, and format

Exports:
- `print_super`
- `read_super`
- `write_super`
- `change_uuid`
- `change_lockproto`
- `change_locktable`
- `change_format`

Research notes:
- The API is intentionally stateful around a single mutable `struct tunegfs2`.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/gfs2/tune/tunegfs2.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/po/POTFILES.in -->
# File Research: sources/local-fs/gfs2-utils/po/POTFILES.in

gettext source list for translatable strings.

Includes mkfs, grow, jadd, metafs, tune, and fsck files, including several files in this group:
- `gfs2/mkfs/main_mkfs.c`
- `gfs2/mkfs/metafs.c`
- `gfs2/tune/main.c`
- `gfs2/tune/super.c`
- `gfs2/tune/tunegfs2.h`

Research notes:
- The file controls extraction coverage for translation catalogs.
- Script files in this group are not listed for gettext extraction.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/po/POTFILES.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/tests/Makefile.am -->
# File Research: sources/local-fs/gfs2-utils/tests/Makefile.am

Automake test harness for gfs2-utils.

Defines:
- Test scripts: `fsck.gfs2-tester.sh`, `rgrifieldscheck.sh`, `rgskipcheck.sh`
- Distributed files: autotest inputs, package template, `atlocal.in`
- Generated/cleaned files: `atlocal`, `atconfig`, `testvol`, `gfs2-utils.spec`
- `noinst_PROGRAMS = nukerg`

Builds `nukerg` from `nukerg.c` and links it against `libgfs2` and UUID libs.

Autotest integration:
- `TESTSUITE_AT` includes `testsuite.at`, `mkfs.at`, `fsck.at`, `edit.at`, `tune.at`.
- `check-local` and `installcheck-local` run the generated `testsuite`.
- `package.m4` is generated from package metadata.
- `AUTOM4TE`/`AUTOTEST` create the `testsuite`.

Research notes:
- `AUTOTEST_PATH` for installcheck includes installed sbin, `gfs2/libgfs2`, and tests.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/tests/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/tests/atlocal.in -->
# File Research: sources/local-fs/gfs2-utils/tests/atlocal.in

Autotest local configuration fragment.

Defines:
- `GFS_TGT="@testvol@"`
- `GFS_TGT_SZ=20`
- `GFS_MKFS="mkfs.gfs2 -O -D"`

Provides:
- `gfs_max_blocks(blocksize)`: computes maximum blocks for the test volume size.
- `gfs_tgt_cleanup(flag)`: removes the test volume when requested.
- EXIT trap invoking cleanup.

Research notes:
- Test mkfs defaults force override and debug modes.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/tests/atlocal.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/tests/fsck.gfs2-tester.sh -->
# File Research: sources/local-fs/gfs2-utils/tests/fsck.gfs2-tester.sh

Shell test runner for replaying metadata images through `gfs2_edit restoremeta` and `fsck.gfs2`.

Usage:
- `fsck.gfs2-tester.sh <path> <truncate_size>`
- Reads stdin lines of `<clean|dirty> <path>` metadata cases.

Behavior:
- Validates/touches target device/file.
- Creates timestamped result directory.
- For each case, restores metadata to target.
- For `clean`, runs `fsck.gfs2 -n` and expects success.
- For `dirty`, runs `fsck.gfs2 -y` and expects return code `1`, then `fsck.gfs2 -n` and expects success.
- Removes per-case logs for passing tests.
- Writes failed cases to `fsck.gfs2.fails.in`.

Research notes:
- Designed to destroy target contents.
- Sparse file mode is supported through nonzero `truncate_size`.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/tests/fsck.gfs2-tester.sh -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/tests/gfs2-utils.spec.in -->
# File Research: sources/local-fs/gfs2-utils/tests/gfs2-utils.spec.in

RPM spec template used only for testing, not distro packaging.

Defines package metadata for `gfs2-utils`, build dependencies, source URL, configure/build/install steps, and file list.

Notable behavior:
- Installs only the `gfs2` subtree into buildroot.
- Removes installed `gfs2_trace` and `gfs2_lockcapture`.
- Includes utilities such as `fsck.gfs2`, `gfs2_grow`, `gfs2_jadd`, `mkfs.gfs2`, `gfs2_edit`, `tunegfs2`, `glocktop`, `gfs2_withdraw_helper`, man pages, and udev rule.

Research notes:
- `%global source_date_epoch_from_changelog 0` disables changelog requirement for source date epoch.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/tests/gfs2-utils.spec.in -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/tests/nukerg.c -->
# File Research: sources/local-fs/gfs2-utils/tests/nukerg.c

Test utility that deliberately zeroes selected GFS2 resource group headers and/or rindex entries.

CLI:
- `nukerg -r <num_list>|-i <num_list> /dev/your/device`
- Lists can be comma- or space-separated.
- `*` means all.
- Both `-r` and `-i` may be specified; resource groups are destroyed before rindex entries.

Key functions:
- `parse_uint`, `parse_uint_list`, `parse_ri_list`, `parse_rg_list`, `opts_get`: parse destructive target selections.
- `fill_super_block`: reads GFS2 superblock and master directory through `libgfs2`.
- `read_rindex`: looks up `rindex`, initializes rgrp set, and reads all rindex entries.
- `nuke_rgs`: writes a zeroed `struct gfs2_rgrp` at selected resource group header block offsets.
- `nuke_ris`: writes a zeroed `struct gfs2_rindex` into selected rindex file offsets.
- `main`: validates args, opens device RW, loads metadata, applies destruction, fsyncs and closes.

Dependencies:
- `libgfs2` for superblock, inode, rindex, and rgrp helpers.
- POSIX open/pwrite/fsync/close.

Research notes:
- This is intentionally destructive and exists for corruption/repair tests.
- `parse_rg_list` accepts `str` but calls `parse_uint_list(optarg, ...)`, coupling it to getopt global state.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/tests/nukerg.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/tests/rgrifieldscheck.sh -->
# File Research: sources/local-fs/gfs2-utils/tests/rgrifieldscheck.sh

Shell consistency checker comparing rindex fields against resource group header fields via `gfs2_edit`.

Behavior:
1. Verifies `gfs2_edit -p rg 0` exposes `rg_data0`; exits success if fields are unavailable in old headers.
2. Iterates `gfs2_edit -p rindex`.
3. For `ri_data0`, `ri_data`, and `ri_bitbytes`, maps `ri*` to `rg*`.
4. Reads matching resource group field and compares values.
5. Fails with a diagnostic on mismatch.

Research notes:
- Increments resource group index when `ri_bitbytes` is processed.
- Used as a test script in `tests/Makefile.am`.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/tests/rgrifieldscheck.sh -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/gfs2-utils/tests/rgskipcheck.sh -->
# File Research: sources/local-fs/gfs2-utils/tests/rgskipcheck.sh

Shell checker for `rg_skip` chain consistency.

Behavior:
1. Gets resource group count from `gfs2_edit -p rgcount`.
2. Reads the first resource group address.
3. Iterates through all groups plus a final sentinel.
4. For each group, computes expected skip as current address minus previous address.
5. Verifies previous `rg_skip` equals the expected distance.
6. Requires the last `rg_skip` to be zero.

Research notes:
- Uses `gfs2_edit -p rg <i>` output and simple `grep`/`awk` parsing.
- Used by autotest wiring through `tests/Makefile.am`.
<!-- END FILE RESEARCH: sources/local-fs/gfs2-utils/tests/rgskipcheck.sh -->