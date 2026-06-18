# Group Research: group_240_bcachefs_tools_sources_cow_pools_bcachefs_tools_src_commands_timesta_a52771b86e54

Scope checked against `Docs/research_subset_a.md`. All listed files were read completely, totaling 6,025 source lines.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/timestats.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/commands/timestats.rs

Implements the `bcachefs timestats` command for one-shot, JSON, and interactive terminal display of kernel time statistics exposed through `/sys/fs/bcachefs/<fs>/time_stats_json`, `internal/btree_trans_stats_json`, and per-device latency JSON files.

Key structures mirror kernel JSON: `DurationStats`, `EwmaStats`, `TimeStats`, and `BtreeTransFnStats`. Runtime display groups stats into `FsSnapshot` sections across three pages: base operation stats, btree transaction stats, and per-device I/O latency.

Major behavior:
- Resolves either all mounted bcachefs sysfs directories or one filesystem via `BcachefsHandle::open`.
- Reads `time_stats_json`, partitioning names beginning with `blocked_` into a "Slowpath" section.
- Optionally reads device latency stats from `dev-*/io_latency_stats_read_json` and `io_latency_stats_write_json`.
- Emits raw JSON with a map of filesystem label to stat name to `TimeStats`.
- Uses `run_tui` and `crossterm` for an interactive alternate-screen UI with sorting, paging, reverse sort, pause, interval changes, and mean-vs-EWMA view switching.

Notable implementation details:
- `fmt_duration` uses coarse integer unit conversion and chooses larger units only when the value is at least 10 units.
- `sort_entries` sorts numeric columns descending by default; name sorts lexicographically.
- Interactive device stats are collected only while on the devices page to reduce sysfs cost.
- Non-interactive mode is selected by `--once` or when stdout is not a terminal.

Potential concerns:
- `SortBy::col_index` names do not map cleanly to displayed columns after `DurTotal`: the table has duration mean/stddev then frequency mean/stddev, while variants are `MeanSince`, `MeanRecent`, `StddevSince`, `StddevRecent`. The active `View` decides mean vs recent, so these CLI names may be misleading.
- Interactive collection uses `collect_stats(...).unwrap_or_default()`, so transient read/parse failures can silently clear the display instead of surfacing an error.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/timestats.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/top.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/commands/top.rs

Implements `bcachefs top`, a live performance counter viewer with one-shot/non-interactive output, an interactive TUI, per-device I/O rates, and tracepoint drill-down for selected counters.

Major components:
- `read_counters` builds a flexible `bch_ioctl_query_counters` buffer and issues `BCH_IOCTL_QUERY_COUNTERS`.
- `read_device_io` parses `dev-*/io_done` JSON into read/write byte totals by device and data type.
- Formatting routes counters through `fmt_counter`, converting sector counters to bytes when appropriate.
- `TopState` stores baseline, mount-time, and previous samples for rate/total/mount columns.
- `TraceView` creates a per-process tracefs instance, filters the selected `bcachefs:<counter>` tracepoint to the current filesystem name, tails `trace_pipe`, and supports pause, scrollback, and stacktrace triggers.

Interactive behavior:
- Base page lists active persistent counters whose value changed since mount.
- Devices page lists per-device read/write totals and rates.
- Enter on a counter starts live trace view if tracefs is available and permissions allow it.
- Sampling is deliberately decoupled from keypresses so scrolling does not reset rate calculations.

Non-interactive behavior:
- Takes an initial baseline sample, sleeps `delay`, then prints `count` frames.
- Defaults to one frame for `--once` or non-terminal stdout.

Notable implementation details:
- Trace instance path is `instances/bcachefs-top-<pid>`.
- `Drop` disables the trace event and removes the tracefs instance.
- Non-blocking trace reads are bounded to avoid a hot tracepoint hanging the UI.
- Counter display uses `COUNTERS` metadata from bindgen, including stable IDs and sector flags.

Potential concerns:
- `read_counters` trusts kernel-returned `actual_nr` for reading the same allocation; if a buggy kernel returns more than requested, the vector read could go beyond the initialized counter region.
- Trace setup assumes generated tracepoint names match persistent counter names exactly.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/top.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/unpoison.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/commands/unpoison.rs

Implements `bcachefs unpoison`, a dangerous recovery command that clears poison flags on file extents through a manually encoded `_IOW(0xbc, 68, struct bch_ioctl_unpoison)` ioctl.

Behavior:
- Requires `--yes-i-understand`; otherwise prints a detailed warning and exits with status 1.
- Accepts file path, sector-aligned byte offset, and sector-aligned length.
- If length is zero, rounds the file size up to 512-byte sectors.
- Opens the file read/write and calls `libc::ioctl` with `BchIoctlUnpoison`.
- Reports the cleared range on success.

Important safety context:
- The file-level documentation and CLI help emphasize that unpoisoning can make corrupt data invisible once a valid checksum exists over corrupted bytes.
- The command recommends `bcachefs data-read --no-poison-check` before proceeding.

Potential concerns:
- Ioctl encoding is duplicated locally instead of using `wrappers::ioctl::bch_ioc_w`, though the formula matches.
- The command exits directly for missing confirmation rather than returning an error, which is consistent with command UX but less library-friendly.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/unpoison.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/wait_devices.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/commands/wait_devices.rs

Implements `bcachefs wait-devices`, which blocks until every device in a multi-device filesystem has appeared and is initialized in udev.

Behavior:
- Accepts only `UUID=<uuid>` or `OLD_BLKID_UUID=<uuid>` device strings via `device_scan::parse_uuid_equals`.
- Builds a udev monitor for block events and an initial enumerator for initialized bcachefs block devices.
- Tracks expected `number_of_devices` and observed device indices in `WaitInitialized`.
- Reads superblocks silently from matching devices to validate UUID, device index, and member count.
- Processes add/change/remove events until the set of unique device indices equals `number_of_devices`.

Multipath handling:
- Uses `device_scan::should_skip_multipath_component` to ignore underlying multipath component devices.

Error handling:
- Invalid device strings and inconsistent superblock `number_of_devices` values are hard errors.
- Devices whose superblock disappears with `ENOENT` are ignored.
- Invalid `dev_idx >= number_of_devices` is warned and skipped.

Potential concerns:
- There is no timeout or degraded-mode exit; the command can wait indefinitely if a device never appears.
- The filtering expression only rejects devices with a different parsed UUID; a device with missing/unparseable `ID_FS_UUID` reaches superblock probing, which may be intentional for robustness.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/wait_devices.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/copy_fs.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/copy_fs.rs

Implements the Rust replacement for copying or migrating a POSIX directory tree into a bcachefs filesystem. It is used by `format --source` and `bcachefs migrate`.

Primary state:
- `MigrateType::{Copy, Migrate}` controls whether file data is copied or existing physical extents are linked.
- `CopyFsState` tracks migration parameters, extent ranges, verbosity, file/input/write/link counters, and hardlink mapping.

Metadata operations:
- Constructs `qstr` and `subvol_inum` values for bcachefs C APIs.
- Creates or updates files with `bch2_create_trans`, `bch2_dirent_lookup`, and `bch2_fsck_write_inode`.
- Replaces mismatching directory entries with recursive removal.
- Preserves uid, gid, mode, rdev, timestamps, symlinks, xattrs, sparse layout, and hardlinks.
- Skips root `lost+found`, `.` and `..`, and, during migrate, the bcachefs backing inode itself.

Data copy/migration:
- Copy mode uses `copy_sync_file_data`, SEEK_DATA/SEEK_HOLE, bcachefs reads, and mismatch detection to avoid rewriting identical aligned blocks.
- Migrate mode uses FIEMAP to link suitable physical extents with `rust_link_data`, copying extents that are unknown, encoded, not aligned, inline, or inside the reserved bcachefs superblock area.
- Tracks linked physical ranges, then creates `old_migrated_filesystem` and links holes to reserve old filesystem space.
- Symlink contents are written as bcachefs file data after punching old content.

Directory traversal:
- Reads source entries with `rustix::fs::Dir`, collects `fstatat` metadata without following symlinks, sorts by type/name, deletes destination entries not present in the source, and recurses into directories.
- Uses `fchdir` before processing child entries, matching the C conversion style but making current-directory state process-global.

Important edge cases:
- Xattrs are best-effort: listing failure is silently ignored, unsupported namespaces are skipped, and individual value read failures are skipped.
- FIEMAP unknown extents trigger an `fsync` and a second FIEMAP pass.
- Unaligned logical or physical extents are fatal in migrate mode.
- `reserve_old_fs_space` assumes device 0 and uses `nbuckets * bucket_size` for total sector coverage.

Potential concerns:
- Several operations call `CString::new(...).unwrap()`, which can panic on interior NULs from host paths/xattrs.
- `copy_data` performs a single `pread` into the requested slice and does not loop for short reads.
- `copy_sync_file_data` accumulates `i_sectors_delta` from punch operations but does not apply it to `dst.bi_sectors`, unlike other punch/write paths.
- `ranges_sort_merge` merges overlapping ranges but not immediately adjacent ranges (`end == next.start` is merged because of `>=`, so adjacency at exact boundary is merged only when `end >= start`, which includes equality).
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/copy_fs.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/device_multipath.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/device_multipath.rs

Provides helpers for identifying device-mapper multipath holder devices from a block device path.

Core behavior:
- Converts a block device `st_rdev` to `/sys/dev/block/<major>:<minor>`.
- Walks `holders/` entries, considering only `dm-*`.
- Reads `/sys/block/dm-*/dm/uuid` and treats `mpath-*`, `partN-mpath-*`, and nested `partN-partM-mpath-*` UUIDs as multipath.
- Resolves the preferred path as `/dev/mapper/<dm name>` if it exists, else `/dev/dm-N`.
- Recurses upward to find the topmost multipath holder with a maximum depth of 8.
- Exposes `warn_multipath_component` for user-facing warnings.

Tests cover:
- Sysfs attribute trimming and missing attributes.
- Missing/non-block input paths.
- Accepted and rejected multipath UUID forms.

Potential concerns:
- Tests do not mock full holder traversal because that depends on real block-device metadata/sysfs.
- The implementation picks the first matching holder returned by `read_dir`; if multiple holders exist, ordering is filesystem-dependent.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/device_multipath.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/device_scan.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/device_scan.rs

Implements bcachefs member-device discovery for mounting/opening, with udev first and whole-block scan fallback.

Core functions:
- `read_super_silent` reads a superblock with `noexcl`, `nochanges`, and `no_version_check`.
- `should_skip_multipath_component` filters multipath component devices via udev property or sysfs holder detection.
- `get_devices_by_uuid_udev` queries initialized block devices tagged `ID_FS_TYPE=bcachefs` and matching `ID_FS_UUID`.
- `get_all_block_devnodes` uses udev and falls back to `/proc/partitions` when udev is missing or empty.
- `read_sbs_matching_uuid` probes candidate devices and returns matching superblock handles.
- `scan_sbs` handles colon-separated explicit devices, UUID strings, and normal device paths.
- `open_scan` expands a single member path into all discovered members before `Fs::open`.
- `bch2_scan_devices` is a C ABI bridge returning a colon-joined device string.

Multipath behavior:
- Discovery filters component paths, but explicit user-provided paths are honored with warnings.
- The udev rule in this group sets the same multipath skip policy for enumeration.

Fallback strategy:
- If udev finds fewer devices than the first found superblock says are expected, it falls back to scanning all block devices.
- Without udev, `/proc/partitions` gives basic device enumeration.

Potential concerns:
- `/proc/partitions` fallback only includes `/dev/<name>` paths that already exist; systems with unusual device node layouts may be missed.
- When udev returns some devices but no readable superblock, expected count is zero and fallback proceeds only because the code does not early return unless `sbs.len() >= expected`; with zero expected and zero sbs this condition is true if reached inside non-empty udev path? In the current code, `expected` becomes 0 and `sbs.len() >= expected` returns true, so an unreadable udev result set could return empty instead of falling back.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/device_scan.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/dump_stack.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/dump_stack.rs

Exports `bch2_demangle` as a C ABI helper for demangling Rust/C++ Itanium-style symbol names.

Behavior:
- Accepts input C string and output buffer.
- Returns 0 on null pointers, zero output length, or invalid UTF-8.
- Uses `rustc_demangle::demangle` with `{:#}` formatting to suppress legacy Rust hash suffixes.
- Copies at most `out_len - 1` bytes and NUL-terminates.
- Returns bytes written, excluding the NUL.

Potential concerns:
- The function is unsafe and trusts the C caller that input and output buffers are valid for the specified lengths.
- It returns 0 for invalid UTF-8, which is also a valid result for an empty demangled string.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/dump_stack.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/http.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/http.rs

Starts a per-process tiny HTTP server over a Unix socket to expose bcachefs userspace sysfs/debugfs content.

Core behavior:
- `bch2_start_http_lazy` is `#[no_mangle]` and called from C-side debugfs/kobject shims.
- Chooses `/run/bcachefs/<pid>.sock` for root or `$XDG_RUNTIME_DIR/bcachefs/<pid>.sock` / `/run/user/<uid>/bcachefs/<pid>.sock` for non-root.
- Spawns a server thread using `tiny_http::Server::http_unix`.
- GET requests call C `sysfs_read_or_html_dirlist` into a `Printbuf`; failures return HTTP 403.
- Non-GET requests return HTTP 405.

Fork/exit handling:
- Tracks the PID that started the server so forked children can start a new socket.
- Registers `pthread_atfork` child handler to call startup after fork.
- Registers `atexit` cleanup to remove the current PID socket.
- Uses a mutex and atomics to keep initialization idempotent per process.

Potential concerns:
- URL handling uses `split_once('/').unwrap()`, so a malformed URL without `/` would panic, although HTTP request URLs normally include a leading slash.
- Socket bind failure is printed but not returned to callers.
- Stale sockets after crashes are intentionally not removed automatically.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/http.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/key.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/key.rs

Manages bcachefs passphrases and kernel keyring integration for encrypted filesystems.

Core concepts:
- `BCH_KEY_MAGIC` identifies plaintext/decrypted filesystem keys.
- `sb_is_encrypted` checks whether a superblock crypt field contains an encrypted passphrase-protected key.
- `unencrypted_key` wraps a raw key as a plaintext `bch_encrypted_key`.
- `Keyring` selects session, user, or user-session keyring IDs.
- `UnlockPolicy` controls fail, wait, ask, or stdin passphrase acquisition.

Key handling:
- `KeyHandle::new` validates a passphrase against the superblock, then adds the derived passphrase key to the selected kernel keyring under `bcachefs:<uuid>`.
- `new_from_search` checks session, user, and user-session keyrings.
- `wait_for_unlock` polls once per second until a key appears.

Passphrase acquisition:
- `Passphrase` is `ZeroizeOnDrop` and stores a `CString`.
- Terminal input disables echo with `rustix::termios`.
- Non-terminal stdin reads one line.
- `/dev/null` stdin triggers `systemd-ask-password` fallback.
- New passphrases can be prompted twice and compared.
- Passphrase files are read into `Zeroizing<String>`.

Crypto operations:
- Passphrase derivation calls C `derive_passphrase`.
- `check` decrypts the superblock key with `bch2_chacha20` and validates magic.
- `encrypt_key` encrypts a filesystem key with a passphrase-derived key.

Potential concerns:
- `CString` rejects interior NULs; passphrases containing NUL cannot be used.
- `systemd-ask-password` output is wrapped directly in `CString`; trailing newline handling differs from stdin/file paths.
- `wait_for_unlock` has no timeout or cancellation beyond process interruption.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/key.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/logging.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/logging.rs

Configures process-wide logging through `env_logger`.

Behavior:
- Maps verbosity 0/1/2/3+ to warn/info/debug/trace.
- Honors `BCACHEFS_LOG` environment filtering through `parse_env`.
- Controls color via `WriteStyle::Always` or `Never`.
- Formats records as `[LEVEL file:line] message`.
- Uses `owo_colors` to color log level by severity.

Potential concerns:
- Calls `.init()`, which panics if a logger has already been initialized elsewhere in the process.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/logging.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/qcow2.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/qcow2.rs

Implements a minimal QCOW2 v2 sparse image writer and reader, used by dump/undump style workflows.

Range helpers:
- `range_add`, `ranges_roundup`, `ranges_sort_merge`, and `ranges_sort` maintain sparse byte ranges.
- Ranges are rounded to block boundaries and merged before writing.

I/O helpers:
- `pread_exact` and `pwrite_all` loop until complete and retry `EINTR`.
- `file_size_fd` handles regular files and block devices using `BLKGETSIZE64`.

Writer:
- `Qcow2Image::new` calculates L1/L2 table sizes from input size and QCOW block size.
- `write_buf` writes raw data at the current output offset and maps each source block through L2 entries.
- `flush_l2` writes pending L2 tables and records them in L1 with `QCOW_OFLAG_COPIED`.
- `write_ranges` reads selected source ranges block by block and writes only those blocks.
- `finish` flushes L2, writes L1, then writes the big-endian QCOW2 header.

Reader:
- `qcow2_to_raw` validates magic/version, truncates output to image size, reads L1/L2 tables, and writes mapped blocks back to raw positions.
- Sparse/unmapped blocks remain holes or zeros depending on output filesystem behavior.

Limitations:
- Supports QCOW2 version 2 only.
- Does not implement refcount tables, snapshots, backing files, compression, encryption, or extended headers.
- The header sets refcount metadata to zero, making this a specialized internal sparse container rather than a general-purpose QCOW2 implementation.

Potential concerns:
- `Qcow2Image::new` asserts block size is a power of two rather than returning an error.
- `finish` advances `offset` by rounded L1 size but writes only unpadded L1 bytes; this is fine as final metadata but leaves unwritten padding implicit.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/qcow2.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/rust_to_c.h -->
# File Research: sources/cow-pools/bcachefs-tools/src/rust_to_c.h

A placeholder C header with only an include guard.

Current content:
- Defines `_BCACHEFS_TOOLS_RUST_TO_C_H`.
- Contains no declarations.

Purpose:
- Likely reserved for Rust-to-C exported function declarations or generated bindings integration.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/rust_to_c.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/util.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/util.rs

Provides shared Rust utility helpers for aligned I/O buffers, human-readable formatting, file sizing, flag parsing, and TUI setup.

Key utilities:
- `AlignedBuf` allocates zeroed 4096-byte-aligned memory and exposes it as `[u8]`.
- `parse_human_size` delegates to C `bch2_strtoull_h`.
- `fmt_bytes_human`, `fmt_sectors_human`, and `fmt_num_human` format byte/sector/count values.
- `file_size` returns regular file size or block device size via `BLKGETSIZE64`.
- `read_flag_list` delegates C flag-list parsing and returns a Rust error on unknown flags.
- `run_tui` enables raw mode, enters the alternate screen, hides cursor, runs a closure, then restores terminal state.

Potential concerns:
- `AlignedBuf::new` asserts allocation success and does not handle zero-size layouts specially.
- `run_tui` restores terminal state after the closure returns, but panics inside the closure would skip restoration.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/util.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/wrappers/accounting.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/wrappers/accounting.rs

Wraps filesystem accounting ioctl support and re-exports bindgen accounting helpers.

Core behavior:
- Adds `BcachefsHandle::query_accounting(type_mask)`.
- Builds a flexible buffer with `QueryAccountingHeader` followed by u64 accounting data.
- Issues `BCH_IOCTL_QUERY_ACCOUNTING` as `_IOW(0xbc, 21, QueryAccountingHeader)`.
- Retries with doubled buffer size on `ERANGE`.
- Returns `ENOTTY` for old kernels without the ioctl.
- Parses accounting bkey records into `AccountingEntry { pos, counters }`.

Parsing details:
- Assumes bkey header is 5 u64s and `bpos` starts at byte offset 20.
- Uses kernel module version to decide whether `bpos` needs byte swapping for pre-big-endian-disk-accounting metadata.
- Stops on zero `key_u64s`, too-small entries, or entries extending past the buffer.

Potential concerns:
- Raw bkey layout parsing is tightly coupled to kernel struct layout and endianness assumptions.
- Counter u64s are read as native endian without additional swabbing, which may be correct for ioctl output but should remain aligned with kernel ABI.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/wrappers/accounting.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/wrappers/bdev.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/wrappers/bdev.rs

Provides Rust replacements for low-level block-device utilities formerly in C.

Functions:
- `get_size` returns block-device size via `BLKGETSIZE64` or regular file `st_size`.
- `get_blocksize_physical_hint` returns physical block size via `BLKPBSZGET` or `st_blksize`.
- `fd_to_dev_model` reads model/backing file information from sysfs.
- `fd_to_dev_serial` reads serial number from sysfs.
- `nonrot` uses `BLKROTATIONAL` ioctl to detect non-rotational devices.
- `open_device` maps `BLK_OPEN_*` flags to POSIX `open` flags, including `O_DIRECT`, `O_EXCL`, and `O_CREAT`.
- `blkid_check` calls a C helper for filesystem probing.

Potential concerns:
- `get_size` and `get_blocksize_physical_hint` ignore ioctl return values and may return zero on failure.
- `open_device` initializes flags to 0 if no read/write mode is supplied, which means an accidental default can become `O_RDONLY`-like behavior on Linux.
- Helper `fstat` exits the process via `super_io::die` instead of returning a recoverable error.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/wrappers/bdev.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/wrappers/handle.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/wrappers/handle.rs

Defines `BcachefsHandle`, an RAII handle to a mounted bcachefs filesystem with ioctl and sysfs fds, plus high-level wrappers for subvolume, disk, superblock, and device-usage ioctls.

Opening paths:
- UUID string: opens `/sys/fs/bcachefs/<uuid>`, reads `minor`, then opens `/dev/bcachefs<minor>-ctl`.
- Mounted path: detects via `BCH_IOCTL_QUERY_UUID`, uses `FS_IOC_GETFSSYSFSPATH` or UUID fallback to open sysfs.
- Block device: reads `/sys/dev/block/<major>:<minor>/bcachefs` symlink to infer filesystem UUID and dev index.
- Fallback file/device path: reads the superblock to infer user UUID, then opens the mounted filesystem by name.

Ioctl compatibility:
- `v2_v1_ioctl!` tries newer v2 ioctls with an 8192-byte error buffer and falls back to v1 on `ENOTTY`.
- On v2 errors, prints the kernel-provided error message if present.

Supported operations:
- `create_subvolume`, `delete_subvolume`, and `snapshot_subvolume`.
- `disk_add`, `disk_remove`, `disk_online`, `disk_offline`, `disk_set_state`.
- `disk_resize` and `disk_resize_journal`.
- `read_super` via `BCH_IOCTL_READ_SUPER`, growing buffer on `ERANGE`.
- `sb_version`.
- `dev_usage`, with v2 flex-array parsing and v1 fallback.

Device usage helpers:
- `DevUsage` exposes capacity, hidden sectors, used sectors, used buckets, and typed data-type iteration.
- Caps iteration at known `BCH_DATA_NR` to avoid interpreting more kernel-returned types than userspace knows.

Potential concerns:
- `open_via_superblock` calls `bch2_free_super` on a handle obtained from Rust wrapper APIs; this depends on ownership expectations matching exactly.
- `read_super` starts at 4096 bytes and grows to under 1 MiB; unusually large superblocks beyond that fail.
- UUID parsing/formatting is implemented manually and accepts only canonical 32 hex digits with optional dashes.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/wrappers/handle.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/wrappers/ioctl.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/wrappers/ioctl.rs

Provides const helpers for encoding bcachefs ioctl numbers.

Functions:
- `bch_ioc_w<T>(nr)` computes `_IOW(0xbc, nr, T)`.
- `bch_ioc_wr<T>(nr)` computes `_IOWR(0xbc, nr, T)`.

Use:
- Shared by command and wrapper modules that manually issue bcachefs ioctls with Rust-defined struct layouts.

Potential concerns:
- Direction/type/number constants are Linux ioctl ABI-specific.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/wrappers/ioctl.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/wrappers/mod.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/wrappers/mod.rs

Declares wrapper submodules and provides two shared helpers.

Exports:
- `accounting`, `bdev`, `handle`, `ioctl`, `sb_display`, `super_io`, and `sysfs`.

Helpers:
- `bch_err_str` converts a bcachefs error code to a lossy Rust string via C `bch2_err_str`.
- `SbLockGuard` is an RAII wrapper around the bcachefs superblock pthread mutex.
- `sb_lock` locks `fs->sb_lock.lock` and returns the guard.

Potential concerns:
- `sb_lock` is unsafe and assumes the `bch_fs` pointer and embedded mutex layout are valid.
- `pthread_mutex_lock` return value is ignored.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/wrappers/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/wrappers/sb_display.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/wrappers/sb_display.rs

Rust replacement for C `bch2_sb_to_text_with_names`, designed to avoid allocator mismatches when scanning devices for display.

Core behavior:
- Builds `UUID=<uuid>` from the superblock user UUID.
- Uses `device_scan::scan_sbs` to find matching device superblocks.
- Prints normal superblock fields via C `bch2_sb_to_text`, excluding member fields so Rust can print members with names.
- For each alive member in members_v1 and/or members_v2, prints device index, path, model, optional serial number, and C member detail text.
- Supports `field_only` by delegating to `__bch2_sb_field_to_text`.

Important implementation detail:
- Scanned superblock handles remain in a Rust `Vec` and are dropped by Rust, avoiding the previous pattern where Rust-allocated memory was freed by C `kvfree`.

Potential concerns:
- `field_only` transmutes a `u32` to `bch_sb_field_type`; invalid values rely on C lookup behavior.
- Missing devices are displayed as `(not found)`, but the rest of the member still prints.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/wrappers/sb_display.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/wrappers/super_io.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/wrappers/super_io.rs

Implements Rust superblock read/write helpers compatible with C expectations.

Core functions:
- `die` prints an error and exits.
- `borrowed_file` wraps a raw fd in `ManuallyDrop<File>` so it is not closed.
- `vstruct_bytes_sb` computes fixed superblock size plus variable u64 payload.
- `bch2_super_write` writes the superblock to every layout offset, handling the special default offset/layout co-write case for large physical block sizes, then fsyncs.
- `__bch2_super_read` reads and validates a superblock at a sector offset, allocates with `libc::malloc`, and returns a C-freeable pointer.
- `sb_layout_init` initializes primary/backup superblock layout positions.

Layout details:
- Uses bcachefs magic constants for legacy bcache and bcachefs.
- Default superblock size is 2048 sectors.
- Adds an end-of-device backup superblock only for default superblock start and when `no_sb_at_end` is false.
- Aligns non-default positions to block-size sectors.

Potential concerns:
- Many errors terminate the process instead of returning `Result`, matching C behavior but limiting composability.
- `round_up` assumes power-of-two alignment.
- `__bch2_super_read` trusts `u64s` after the initial magic check to allocate the variable-sized structure.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/wrappers/super_io.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/wrappers/sysfs.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/wrappers/sysfs.rs

Provides sysfs and mount-table helper functions for mounted bcachefs filesystems.

Functions:
- `dev_name_from_sysfs` resolves `dev-N/block` symlink to a block device name, falling back to the sysfs directory name for offline devices.
- `sysfs_path_from_fd` resolves `/proc/self/fd/<fd>` for a sysfs fd.
- `read_sysfs_u64` parses a sysfs attribute as `u64`.
- `read_sysfs_fd_str` reads a small string attribute relative to a directory fd.
- `bcachefs_kernel_version` reads `/sys/module/bcachefs/parameters/version`, returning 0 if unavailable.
- `dev_mounted` parses `/proc/mounts`, handling colon-separated bcachefs device lists, and compares device identities.
- `sysfs_write_str` best-effort writes a string to an attribute relative to sysfs fd.
- `fs_get_devices` enumerates `dev-N` directories, reading device name, label, and durability.

Potential concerns:
- `read_sysfs_fd_str` reads at most 256 bytes and does not loop; adequate for current short attributes.
- `dev_mounted` splits mount device fields on `:`, which works for bcachefs device lists but could interact poorly with escaped mount fields or unusual path names.
- `sysfs_write_str` ignores all write errors.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/wrappers/sysfs.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/udev/64-bcachefs.rules -->
# File Research: sources/cow-pools/bcachefs-tools/udev/64-bcachefs.rules

Defines udev rules for bcachefs block devices.

Behavior:
- Applies only to non-remove block events where `ID_FS_TYPE=bcachefs` and `SYSTEMD_READY` is not `0`.
- Sets `UDISKS_AUTO=0` to discourage udisks from automatically mounting bcachefs filesystems.
- Skips multipath component devices when `DM_MULTIPATH_DEVICE_PATH=1`.
- Adds a per-member UUID symlink under `disk/by-uuid/` using `ID_FS_UUID_SUB_ENC` when available.

Security/operational intent:
- The udisks setting does not remove filesystem attack surface, but prevents unattended automount in locked-session scenarios.
- Multipath filtering aligns with Rust-side scanning behavior so enumeration prefers the dm-multipath map, not underlying paths.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/udev/64-bcachefs.rules -->