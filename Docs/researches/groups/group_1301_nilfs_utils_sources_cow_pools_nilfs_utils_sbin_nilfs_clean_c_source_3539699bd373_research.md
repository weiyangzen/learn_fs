# Group Research: group_1301_nilfs_utils_sources_cow_pools_nilfs_utils_sbin_nilfs_clean_c_source_3539699bd373

Scope: `Docs/research_subset_a.md` includes `sources/cow-pools/nilfs-utils`.  
Files read completely: 5 files, 8,556 total lines.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/nilfs-clean.c -->
# File Research: sources/cow-pools/nilfs-utils/sbin/nilfs-clean.c

## Purpose
`nilfs-clean.c` implements the `nilfs-clean` command, a CLI controller for NILFS2 garbage collection/cleaner service behavior. It can run cleaner work, query status, suspend/resume, reload configuration, stop, or shut down the cleaner.

## Main Interfaces
- Includes NILFS userland APIs from `nilfs.h`, `nilfs_cleaner.h`, `parser.h`, and `util.h`.
- Uses `nilfs_cleaner_open`, `nilfs_cleaner_run`, `nilfs_cleaner_get_status`, `nilfs_cleaner_suspend`, `nilfs_cleaner_resume`, `nilfs_cleaner_reload`, `nilfs_cleaner_stop`, and `nilfs_cleaner_shutdown`.
- Opens the raw filesystem through `nilfs_open` only for speed auto-adjustment.

## Command Model
Supported commands are encoded in `clean_cmd`:
- `NILFS_CLEAN_CMD_RUN`: default cleaner run request.
- `NILFS_CLEAN_CMD_INFO`: print `idle`, `running`, `suspended`, or unknown status.
- `NILFS_CLEAN_CMD_SUSPEND`
- `NILFS_CLEAN_CMD_RESUME`
- `NILFS_CLEAN_CMD_RELOAD`
- `NILFS_CLEAN_CMD_STOP`
- `NILFS_CLEAN_CMD_SHUTDOWN`

Options include:
- `-b` / `--break` / `--stop`: stop running cleaner.
- `-c [conffile]` / `--reload[=CONFFILE]`: reload cleaner config.
- `-l` / `--status`: status query.
- `-p SECONDS`: protection period via `nilfs_parse_protection_period`.
- `-m COUNT[%]`: minimum reclaimable blocks, absolute or percent.
- `-S COUNT[/SECONDS]`: cleaner speed, as segments per interval.
- `-q`, `-r`, `-s`, `-v`, `-V`, `-h`.

## Core Behavior
- `main` installs `nilfs_clean_logger` into `nilfs_cleaner_logger`, parses options, handles version output, validates an optional device/node argument with `stat`, and calls `nilfs_do_clean`.
- `nilfs_do_clean` opens a cleaner queue, temporarily installs signal handlers for `SIGINT`, `SIGTERM`, and `SIGHUP`, dispatches the selected request, then closes the cleaner handle.
- Signal interruption uses `sigsetjmp`/`siglongjmp` through `nilfs_clean_escape`.
- `nilfs_clean_do_run` builds `struct nilfs_cleaner_args` with one pass, interval, segments per clean, optional protection period, and optional minimum reclaimable threshold.

## GC Speed Handling
- Default target GC throughput is `1.28 GiB/s`.
- If `-S` did not set `nsegments_per_clean`, `nilfs_clean_adjust_speed` opens the device read-only/raw, reads block size and blocks per segment, derives bytes per segment, and converts the default throughput into segments per cleaner call.
- Result is clamped to `[1, 32]` segments per call.
- If layout data cannot be read or arithmetic would overflow, fallback is `16` segments per call.

## Parsing Details
- `nilfs_clean_parse_gcspeed` accepts `COUNT`, `COUNT/SECONDS`, and fractional interval syntax such as `COUNT/0.5`.
- `nilfs_clean_parse_min_reclaimable` accepts `COUNT` or `COUNT%`, rejects percentages above 100, and stores the unit separately.
- Invalid or overflowing values terminate with diagnostics.

## Notable Risks and Edge Cases
- The logger filter suppresses messages with priority `>= LOG_INFO`; the `verbose` branch also suppresses priorities greater than `LOG_INFO`, so verbose mode does not obviously enable informational logging from this wrapper.
- `strtod` fractional interval conversion stores nanoseconds through floating-point arithmetic; small precision effects are possible but low impact.
- `nsegments_per_clean` from `-S` is not clamped to the same min/max range as auto-adjusted values.
- The command allows no device argument, leaving device discovery to `nilfs_cleaner_open`.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/nilfs-clean.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/nilfs-resize.c -->
# File Research: sources/cow-pools/nilfs-utils/sbin/nilfs-resize.c

## Purpose
`nilfs-resize.c` implements online NILFS2 filesystem resizing. It supports growing a mounted filesystem up to the block device size and shrinking by evacuating in-use segments from the truncated range before issuing the NILFS resize ioctl.

## Main Interfaces
- NILFS APIs: `nilfs_open`, `nilfs_close`, `nilfs_get_layout`, `nilfs_get_sustat`, `nilfs_set_alloc_range`, `nilfs_resize`, `nilfs_sync`, `nilfs_freeze`, `nilfs_thaw`, `nilfs_lock_cleaner`, `nilfs_unlock_cleaner`.
- Segment/GC APIs: `nilfs_get_suinfo`, `nilfs_suinfo_*`, `nilfs_segment_is_protected`, `nilfs_reclaim_segment`, `nilfs_delete_checkpoint`.
- Mount/device APIs: `check_mount`, `BLKGETSIZE64`.
- Runs only on mounted block devices; offline resizing is explicitly not supported.

## Command Options
- `-h`: usage.
- `-v`: verbose messages.
- `-y` / `--yes` / `--assume-yes`: skip confirmation prompts.
- `-V`: version.
- Positional arguments: `device [size]`.
- Size suffixes: `s`, `K`, `M`, `G`, `T`, `P`.

## Global State
Important globals include:
- `devsize`: actual block device size from `BLKGETSIZE64`.
- `layout`: `struct nilfs_layout` for current filesystem geometry.
- `sustat`: segment usage statistics.
- `trunc_start`, `trunc_end`: segment range being truncated.
- Fixed batch buffers: `suinfo[256]`, `segnums[256]`.
- Shrink cleaner pacing: `nsegments_per_clean = 2`, `clean_interval = 100ms`.
- Progress bar state printed to stderr.

## Control Flow
1. `main` parses options and validates the block device.
2. It reads device size, parses optional target size, aligns target size down to sector size, and checks mount status.
3. `nilfs_resize_online` opens NILFS raw/read-write/GC-lock capable, loads layout, syncs, and dispatches:
   - `nilfs_extend_online` when `newsize > layout.devsize`.
   - `nilfs_shrink_online` when `newsize < layout.devsize`.
4. Success prints `Done.`; failure prints `Aborted.`.

## Extend Path
`nilfs_extend_online`:
- Prints old and new sizes.
- Prompts unless `-y`.
- Locks the cleaner while blocking `SIGINT` and `SIGTERM`.
- Calls `nilfs_resize(nilfs, newsize)`.
- Unlocks cleaner and restores signal mask.

This is comparatively direct because no segment evacuation is required.

## Shrink Path
`nilfs_shrink_online` is the core of the file:
- Computes the new secondary superblock offset with `NILFS_SB2_OFFSET_BYTES(newsize)`.
- Converts the target size into a target segment count.
- Checks that enough free space remains after shrink using reserved segment calculations.
- Prompts unless `-y`.
- Calls `nilfs_set_alloc_range(nilfs, 0, newsize)` to prevent new allocations past the target boundary.
- Counts in-use segments in the truncation range and optionally initializes a progress bar.
- Reclaims/moves segments from the truncation range.
- Locks the cleaner and calls `nilfs_resize`.
- Retries on `EBUSY` after reloading layout and segment stats.
- Restores allocation range on failure.

## Segment Movement
Segment evacuation is built from smaller helpers:
- `nilfs_resize_find_movable_segments`: finds reclaimable and unprotected segments, allowing empty/scrapped segments immediately.
- `nilfs_resize_find_active_segments`: finds active non-error segments and optionally totals their used blocks.
- `nilfs_resize_find_reclaimable_segments`: finds dirty, non-error, non-active reclaimable segments.
- `nilfs_resize_move_segments`: calls `nilfs_reclaim_segment` in small batches, updates progress for moved segments in the truncation range, and sleeps between batches.
- `nilfs_resize_verify_failure`: distinguishes protected segments from unreclaimable segments after partial GC failures.
- `nilfs_resize_reclaim_nibble`: fallback strategy that tries the target range, then earlier segments, then log cursor updates, then forced filesystem updates.
- `nilfs_resize_reclaim_range`: overall shrink reclamation loop.

## Active Segment Handling
When active log-writer segments block shrink:
- `nilfs_resize_move_out_active_segments` retries active eviction up to several times.
- If no movable segment can be found, `nilfs_resize_try_update_log_cursor` syncs, freezes, and thaws to converge superblock log cursors.
- If active segments remain, `nilfs_resize_prod_fs` creates a temporary `.nilfs-balloon-<pid>` file in the filesystem root, writes random/fallback pseudo-random data, syncs, unlinks it, deletes checkpoints created during the operation, and syncs again.

## Safety Measures
- Cleaner lock protects final resize operations.
- `SIGINT` and `SIGTERM` are blocked around cleaner lock and balloon-file critical sections.
- Allocation range is restored if shrink fails after range limitation.
- Confirmation is required by default.
- The command refuses unmounted devices because offline resizing is unsupported.
- Progress display is kept separate from diagnostics with `msg`.

## Notable Risks and Edge Cases
- Size parsing shifts `uint64_t` values for suffixes but does not explicitly detect overflow after shifting.
- `nilfs_resize_parse_options` accepts option string characters `M` and `P` that are not handled in the switch.
- The shrink retry loop uses `retry < 4`, while comments describe fewer retries.
- Balloon filename is PID-based and created in the filesystem root with `O_CREAT | O_TRUNC`; collision is unlikely but not impossible.
- Fallback random data uses `rand()` intentionally because cryptographic randomness is unnecessary.
- The implementation is deeply tied to NILFS segment semantics and kernel resize ioctl support; `ENOTTY` gets a specific unsupported-kernel message.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/nilfs-resize.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/nilfs-tune.c -->
# File Research: sources/cow-pools/nilfs-utils/sbin/nilfs-tune.c

## Purpose
`nilfs-tune.c` implements `nilfs-tune`, a utility for displaying and modifying NILFS superblock tunables such as label, UUID, commit interval, segment creation block threshold, and selected feature flags.

## Main Interfaces
- Includes NILFS on-disk definitions through `linux/nilfs2_ondisk.h`.
- Uses `nilfs_sb_read`, `nilfs_sb_write`, `nilfs_feature2string`, and `nilfs_edit_feature`.
- Uses `check_mount` to prevent dangerous writes to mounted filesystems unless forced.

## Options and Modes
Usage modes:
- `nilfs-tune -l device`: display superblock information.
- `nilfs-tune [-f] [-i interval] [-m block_max] [-L volume_name] [-O [^]feature[,...]] [-U UUID] device`: modify fields.
- `nilfs-tune [-h|-V]`.

Option effects:
- `-l`: display current superblock data.
- `-f`: force write operations even if mounted.
- `-i`: set commit interval.
- `-m`: set block count threshold for segment creation.
- `-L`: set volume label, truncating to the fixed on-disk field size.
- `-O`: edit allowed feature bits.
- `-U`: set UUID.
- `-V`: version.

## Data Model
`struct nilfs_tune_options` carries:
- Open flags (`O_RDONLY` or `O_RDWR`).
- Display flag.
- Superblock write mask.
- Force flag.
- Tunable values.
- Label buffer.
- UUID bytes.
- Feature edit string.

The mask uses NILFS superblock field masks such as:
- `NILFS_SB_COMMIT_INTERVAL`
- `NILFS_SB_BLOCK_MAX`
- `NILFS_SB_LABEL`
- `NILFS_SB_UUID`
- `NILFS_SB_FEATURES`

## Display Behavior
`show_nilfs_sb` prints:
- Volume name and UUID.
- Magic and revision.
- Feature flags.
- State, OS type, block size, timestamps.
- Mount counts.
- Reserve UID/GID with name lookup.
- Inode/DAT/checkpoint/segment usage sizes.
- Segment count, device size, first data block, blocks per segment.
- Reserved segment percentage.
- Last checkpoint, last block address, last sequence.
- Free block count.
- Commit interval and segment creation block limit.
- CRC fields.

Filesystem check interval display code exists but is disabled with `#if 0`.

## Feature Editing
- Only `NILFS_FEATURE_COMPAT_RO_BLOCK_COUNT` is allowed in the read-only compatible feature set.
- `ok_features` and `clear_ok_features` both allow only that feature.
- Invalid feature edits report whether a feature is not allowed to be set or cleared.

## Write Flow
`modify_nilfs`:
1. Opens the device read-only or read-write depending on requested operation.
2. Reads the superblock.
3. Warns about unknown incompatible or read-only-compatible features.
4. Applies requested field changes in memory.
5. Writes superblocks with `nilfs_sb_write` if the mask is nonzero.
6. Displays the resulting superblock if `-l` was requested.

`main` blocks write operations on mounted filesystems unless `-f` is supplied, warning that mounted tuning can cause severe damage.

## Notable Risks and Edge Cases
- Numeric parsing for `-i` and `-m` uses `atol` without strong validation, range checking, or negative rejection before storing into unsigned 32-bit fields.
- The device is taken as `argv[argc - 1]` after option parsing, so the command assumes the final argument is the device.
- Label truncation is intentional and may omit a terminating NUL on disk.
- UUID parsing expects exactly canonical 36-character lowercase/uppercase hex plus hyphens layout.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/sbin/nilfs-tune.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/scripts/Makefile.am -->
# File Research: sources/cow-pools/nilfs-utils/scripts/Makefile.am

## Purpose
This Automake fragment declares script distribution behavior for the `scripts` directory.

## Contents
The file contains:
```make
dist_noinst_SCRIPTS = checkpatch.pl
```

## Build Meaning
- `checkpatch.pl` is included in distribution tarballs.
- It is not installed by `make install`.
- The script is treated as a developer/maintainer helper rather than runtime user command.

## Dependencies
No local build rules, conditionals, or generated outputs are defined here.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/scripts/Makefile.am -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs-utils/scripts/checkpatch.pl -->
# File Research: sources/cow-pools/nilfs-utils/scripts/checkpatch.pl

## Purpose
`checkpatch.pl` is a NILFS-utils-adapted copy of Linux kernel `checkpatch.pl`, version `0.32`, used to check patch or source-file style. It reports typed errors, warnings, and optional strict checks, with experimental auto-fix support.

## Command-Line Interface
Important options:
- `--patch` / default: treat inputs as unified diffs.
- `-f` / `--file`: treat inputs as regular source files by running `diff -u /dev/null <file>`.
- `--tree`, `--root`: enable kernel-tree-aware checks.
- `--no-signoff`: skip Signed-off-by requirement.
- `--subjective` / `--strict`: enable extra `CHECK` diagnostics.
- `--types`, `--ignore`, `--show-types`: filter or label report types.
- `--max-line-length`
- `--min-conf-desc-length`
- `--fix`, `--fix-inplace`: experimental rewriting.
- `--ignore-perl-version`
- `--debug`
- `--test-only`
- `--quiet`, `--terse`, `--emacs`, `--summary`, `--mailback`.

## Configuration and Inputs
- Reads `.checkpatch.conf` from current directory, `$HOME`, or `.scripts`.
- Loads spelling corrections from `scripts/spelling.txt` relative to the script path when present.
- Requires Perl `5.10.0` for full regex-based checks, unless overridden.
- In file mode, opens a pipe to `diff -u /dev/null $filename`.
- In patch mode, reads each file or stdin into `@rawlines`, then processes each input independently.

## Main Processing Phases
1. Build large regex grammars for identifiers, types, attributes, constants, operators, declarations, and kernel annotations.
2. Optionally seed CamelCase exceptions from kernel include files.
3. Pre-scan input lines:
   - Track hunk line numbers.
   - Sanitize strings and comments into placeholders.
   - Preserve raw lines for exact output and fixes.
4. Process hunk and commit-log lines:
   - Maintain real file and real line state.
   - Track commit message versus patch body.
   - Annotate expression/operator context.
   - Emit typed reports.
5. Print report summary.
6. Optionally write experimental fixed output.

## Reporting Model
- `ERROR(type, msg)`: increments error count and marks input unclean.
- `WARN(type, msg)`: increments warning count and marks input unclean.
- `CHK(type, msg)`: emitted only in strict/check mode.
- Reports are filtered by `--types`, `--ignore`, and `--test-only`.
- `--emacs` changes prefixes to file/line style.

## Fix Mode
When `--fix` or `--fix-inplace` is enabled:
- The script tracks line replacements, insertions, and deletions.
- It can fix selected whitespace, brace, pointer, comment, spelling, macro, and API style issues.
- Non-inplace mode writes `<input>.EXPERIMENTAL-checkpatch-fixes`.
- The script explicitly warns not to trust generated fixes without inspection.

## Major Check Categories
Patch metadata:
- Missing or malformed Signed-off-by lines.
- Duplicate signatures.
- Non-standard signature tags.
- Commit ID formatting.
- Old stable address.
- Gerrit Change-Id.
- MAINTAINERS updates for added/moved/deleted files.
- UTF-8 and charset issues.
- Spelling mistakes.
- FSF mailing address boilerplate.

File and build metadata:
- Executable permissions on non-script source files.
- Kconfig help length and deprecated `EXPERIMENTAL`/`boolean`.
- Deprecated Makefile variables such as `EXTRA_CFLAGS`.
- Device tree compatible string documentation when tree context is available.
- Patch corruption/wrapping.

C and source style:
- Long lines.
- Missing EOF newline.
- Tabs, indentation, leading spaces, spaces before tabs.
- Parenthesis alignment and conditional indentation.
- Missing blank lines after declarations.
- Multiple blank lines.
- Switch/case indentation.
- Brace placement for functions, structs, unions, enums, `if`, `else`, `while`, and macros.
- C99 `//` comments.
- Spacing around operators, commas, semicolons, parentheses, brackets, and braces.
- Function pointer declaration spacing.
- Pointer `*` placement.
- Misordered C type specifiers.
- New typedefs.
- Function declarations without `void`.
- Multiple assignments.
- Assignment in conditionals.
- Trailing statements after conditionals/cases.
- Unnecessary parentheses.
- Return parentheses and void returns.
- Labels indentation.

Kernel/API-oriented checks:
- `printk` level usage and preference for `pr_*`/`dev_*`.
- Deprecated `DEFINE_PCI_DEVICE_TABLE`.
- `LINUX_VERSION_CODE`.
- `volatile`.
- `sizeof` misuse.
- `memset` suspicious arguments.
- Allocation patterns such as `kmalloc_array`, `kcalloc`, `krealloc` arg reuse.
- `sscanf` return checking and `kstrto*` preference.
- `jiffies` comparison helpers.
- Memory barriers and locks without comments.
- `__init` attribute placement.
- `__FUNCTION__`, `__DATE__`, `__TIME__`, `__TIMESTAMP__`.
- `yield`, `in_atomic`, lockdep misuse.
- World-writable debugfs/device attributes.
- Non-octal permission constants.

Macro checks:
- Multi-statement macros should use `do { } while (0)`.
- Complex macro values should be parenthesized.
- Single-statement `do while` macros are discouraged.
- Macro trailing semicolons.
- Flow control in macros.
- Unnecessary line continuations.
- `BIT()` macro preference for `1 << n`.

## NILFS-Utils Context
Although distributed with NILFS-utils, the script remains heavily kernel-oriented. Many checks reference kernel paths, APIs, docs, and conventions. In this repository it functions as a maintainer style gate for C patches, not as runtime NILFS functionality.

## Notable Risks and Edge Cases
- File mode invokes `diff` through a string pipe using the filename, so untrusted filenames could be problematic.
- Debug option handling uses `eval` on debug keys.
- Some tree-aware checks shell out to `git`, `find`, and `grep`.
- The grammar is regex-based and can produce false positives or miss complex C constructs.
- Advanced matching depends on Perl version.
- Experimental fixes can rewrite code incorrectly by design; the script warns about this.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs-utils/scripts/checkpatch.pl -->