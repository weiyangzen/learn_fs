# Group Research: group_239_bcachefs_tools_sources_cow_pools_bcachefs_tools_src_commands_fsck_rs_df69d76b89e0

Scope: `Docs/research_subset_a.md`, source tree `sources/cow-pools/bcachefs-tools`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/fsck.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/commands/fsck.rs

## Purpose
Implements `bcachefs fsck`, covering online fsck against mounted filesystems, in-kernel offline fsck, and userspace offline fsck fallback. It builds the fsck mount-option set, decides whether kernel fsck is required based on metadata-version compatibility, discovers all members of a multi-device filesystem, and splices interactive fsck I/O between the kernel-provided fd and the terminal.

## Main Interfaces
- CLI struct: `FsckCli`
- Command export: `CMD = typed_cmd!("fsck", ...)`
- Key handlers:
  - `cmd_fsck`
  - `fsck_online`
  - `run_userspace_fsck`
  - `should_use_kernel_fsck`
  - `splice_fd_to_stdinout`

## Behavior
- `-p`/`-a` auto-repair exits successfully immediately, matching system fsck behavior where no interactive check is needed.
- Builds default options: `degraded`, `fsck`, `fix_errors=ask`, `read_only`, and `noreconcile_enabled`.
- Omits the default `fsck` option if the user explicitly supplies `recovery_passes`, so the requested pass set is not widened by kernel defaults.
- Applies `-y`, `-n`, `--ratelimit_errors`, `-v`, and extra `-o` options by appending mount options.
- Runs online fsck when the only target is a directory/mountpoint or when any supplied device is detected as mounted through sysfs.
- For a single offline device, scans superblocks to expand to the full member-device list.
- Uses kernel offline fsck when explicitly requested or when userspace and kernel metadata versions make kernel fsck preferable.
- For non-block-device image paths, allocates temporary loop devices with `losetup --show -f` for kernel offline fsck.
- Falls back to userspace fsck if kernel offline setup fails and the user did not explicitly force kernel mode.

## Dependencies and Coupling
- Uses ioctl constants for `BCH_IOCTL_FSCK_OFFLINE` and `BCH_IOCTL_FSCK_ONLINE`.
- Uses `BcachefsHandle` for online fsck handles.
- Uses `device_scan::scan_sbs` and `device_scan::open_scan` for member discovery and userspace opening.
- Uses `find_multipath_holder` and `warn_multipath_component` to warn about multipath component devices.
- Uses `Fs::open` and superblock version data to choose kernel vs userspace fsck.
- Uses `Printbuf` for metadata-version messages and fsck error output.

## Important Implementation Notes
- `splice_fd_to_stdinout` switches stdin and the fsck fd to nonblocking mode and polls both directions, so kernel fsck can ask questions interactively.
- The kernel fsck fd’s close return value is treated as the fsck exit status.
- The offline ioctl payload is manually allocated because the C struct has a flexible array member for device pointers.
- CString lifetimes are preserved in `c_devs` while the ioctl is issued.
- Loop devices are freed before result handling after the ioctl call.

## Risks and Edge Cases
- `setnonblocking` unwraps `fcntl` calls; failure panics.
- `is_blockdev` returns `true` on metadata errors, so missing or inaccessible paths are treated as block devices until later failure.
- The manual flexible-array allocation assumes 8-byte alignment and bindgen layout compatibility.
- Kernel/user metadata-version selection is subtle and should be kept aligned with upstream bcachefs compatibility policy.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/fsck.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/fusemount.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/commands/fusemount.rs

## Purpose
Implements `bcachefs fusemount`, a FUSE filesystem bridge over bcachefs internal btree and inode operations. It allows mounting bcachefs without kernel filesystem support, using `fuser` callbacks backed by C/Rust bcachefs bindings.

## Main Interfaces
- CLI struct: `Cli`
- Command export: `CMD = typed_cmd!("fusemount", ...)`
- FUSE implementation type: `BcachefsFs`
- Main command handler: `cmd_fusemount`
- Thread setup helpers:
  - `ensure_thread_init`
  - `RcuGuard`

## Behavior
- Scans member superblocks with `scan_sbs`, opens the filesystem with `nostart`, then starts the filesystem after daemonization decisions.
- Implements FUSE callbacks for lookup, getattr, setattr, readlink, mknod, mkdir, unlink, rmdir, symlink, rename, hardlink, open, read, write, readdir, statfs, and create.
- Maps FUSE inode `1` to bcachefs root inode `4096` in subvolume `1`; all other inode numbers pass through.
- Translates bcachefs inode metadata into `fuser::FileAttr`.
- Reads and writes file data using aligned buffers and bcachefs async read/write helpers through `block_on`.
- Handles unaligned writes with read-modify-write of partial start/end blocks.
- In foreground mode, initializes shrinkers, starts the filesystem, then calls `fuser::mount2`.
- In daemon mode, forks before thread creation, uses a pipe to signal parent readiness from the FUSE `init` callback, redirects child stderr to `/tmp/bcachefs-fuse.log`, then starts the filesystem and mounts.

## Dependencies and Coupling
- Heavy coupling to C shim functions:
  - `rust_fuse_lookup`
  - `rust_fuse_setattr`
  - `rust_fuse_create`
  - `rust_fuse_unlink`
  - `rust_fuse_rename`
  - `rust_fuse_link`
  - `rust_fuse_readdir`
  - `rust_fuse_update_inode_after_write`
  - `rust_bch2_fs_usage_read_short`
  - `rust_fuse_count_inodes`
  - thread-local current/RCU setup helpers.
- Uses `Fs::borrow_raw` and deliberately `mem::forget`s the opened `Fs` so `BcachefsFs::destroy` owns shutdown.
- Uses `AlignedBuf` for O_DIRECT/block-aligned data I/O.

## Important Implementation Notes
- Each FUSE worker thread calls `ensure_thread_init`, establishing bcachefs `current` and URCU registration. `RcuGuard` unregisters on thread exit.
- Negative lookup caching returns an empty entry for ENOENT instead of just `reply.error`.
- Symlink creation creates an inode, writes NUL-terminated target data, then re-reads inode state.
- `statfs` computes available blocks from short usage accounting and counts inodes through a C helper.
- Mount subtype uses `MountOption::CUSTOM("subtype=bcachefs")` because direct root mount syscalls may drop `Subtype`.

## Risks and Edge Cases
- The inode mapping is hardcoded to subvolume `1`, so snapshot subvolumes with colliding inode numbers cannot be represented correctly in a single FUSE mount.
- Many callbacks print debug output unconditionally to stderr.
- FUSE daemon mode writes logs to a fixed `/tmp/bcachefs-fuse.log`.
- `destroy` calls `bch2_fs_exit` directly on the raw pointer; ownership discipline depends on the earlier `mem::forget`.
- The code assumes block-size alignment and correct behavior from the C shim wrappers.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/fusemount.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/image.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/commands/image.rs

## Purpose
Implements `bcachefs image` subcommands for creating and updating compact bcachefs filesystem images from directory trees. It uses a temporary metadata device so user data can be written sequentially to the primary image, then migrates metadata back and optionally strips allocation information for small read-only images.

## Main Interfaces
- Command group export: `CMD`
- Subcommands:
  - `CMD_CREATE = raw_cmd!("create", ...)`
  - `CMD_UPDATE = typed_cmd!("update", ...)`
- Key functions:
  - `cmd_image_create`
  - `cmd_image_update`
  - `image_create_inner`
  - `image_update_inner`
  - `finish_image`
  - `move_btree`
  - `print_image_usage`

## Behavior
- `image create` manually parses format, filesystem, device, encryption, label, UUID, version, force, quiet, verbose, and source options.
- Creates two devices: the primary image for user data and a temporary `.metadata` image for journal/btree metadata.
- Formats the filesystem with device data-allowed masks so data and metadata are segregated.
- Copies a source directory into the filesystem with `copy_fs`.
- Finishes by moving btree nodes to the primary image, reading usage, truncating the image to used buckets, removing the temporary device from the superblock, enabling journal on primary, marking resize-on-mount, and setting `BCH_FEATURE_small_image`.
- `image update` grows an existing image, adds a temporary metadata device, moves btrees to it, deletes xattrs, copies source content, then runs the same finishing path.
- Supports encrypted images, passphrase files, `--no_passphrase`, explicit format version, UUID, labels, replicas, and deferred options requiring an open filesystem.
- Defaults image format version to the minimum of tool current version and loaded kernel bcachefs metadata version when the kernel reports one.

## Dependencies and Coupling
- Uses `format_util::format` and `format_for_device_add`.
- Uses `copy_fs::{CopyFsState, copy_fs}` for directory-tree import/update.
- Uses `MovingContext::move_data_btree` and a C-compatible predicate to migrate btree nodes.
- Uses disk accounting wrappers and raw C accounting printers for image usage reports.
- Uses `strip_fs_alloc` external C symbol for allocation-info stripping during `finish_image`.
- Uses `DevOpts`, bdev wrappers, superblock field resizing, and raw bcachefs superblock mutation.

## Important Implementation Notes
- `count_input_size` recursively sums allocated blocks and skips `lost+found`.
- Temporary metadata devices are removed from the filesystem view by setting `(*fs.raw).devs[1] = null_mut()` and shrinking `members_v2` to one member.
- `finish_image` calls `fs.read_only()` before deriving final bucket usage and truncating.
- Compression and replicas accounting are printed through `Printbuf`.
- Update mode deletes xattrs because they will be recreated from the source tree.
- Both create and update use a 64 MiB minimum temporary metadata size to ensure enough journal capacity.

## Risks and Edge Cases
- Several superblock and device-array mutations are raw and layout-sensitive.
- `fs_opt_strs.set` stores pointers to temporary `CString`s in a loop; correctness depends on `set` copying or owning the string.
- Cleanup on create failure removes all `device_paths`, including the primary image.
- Update mode grows the destination image before later operations; failures after growth may leave the file enlarged.
- The fixed assumption that temporary metadata is device index `1` is central to finishing.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/image.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/journal_rewind_info.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/commands/journal_rewind_info.rs

## Purpose
Implements `bcachefs journal_rewind_info`, a diagnostic command that reports the safe journal rewind window and lists flush entries that can be used as rewind targets.

## Main Interfaces
- CLI struct: `Cli`
- Command export: `CMD = typed_cmd!("journal_rewind_info", ...)`
- Key helpers:
  - `JournalEntries`
  - `jset_datetime`
  - `jset_rewind_limit`
  - `entry_payload_le64`
  - `fmt_secs`

## Behavior
- Opens devices read-only with no recovery, no changes, severe degraded tolerance, continue-on-error, retained recovery info, and full journal-only reading.
- Collects C journal replay entries through `rust_collect_journal_entries`.
- Finds the latest journal entry by sequence number.
- Reads that entry’s `rewind_limit` payload to determine the oldest safe rewind sequence.
- Falls back to the lowest sequence present if the latest entry lacks a rewind-limit subentry.
- Lists flush entries in `[floor_seq, latest_seq]`, including datetimes when available.
- `-n 0` prints all candidates; positive `-n` prints the most recent N candidates.
- Prints candidate count and total entries in the rewind window.

## Dependencies and Coupling
- Shares a `JournalEntries` RAII wrapper pattern with `list_journal.rs`.
- Depends on raw jset entry layout because bindgen does not expose datetime/rewind-limit payload structs.
- Uses `jset_entries`, `entry_type`, and `jset_no_flush` from journal bindings.
- Uses `chrono::Utc` for timestamp formatting.

## Important Implementation Notes
- `entry_payload_le64` reads the first payload u64 from byte offset 8 of `jset_entry`.
- Only flush entries are considered rewind targets.
- Output is built as a string, then printed once.

## Risks and Edge Cases
- Raw payload reads assume the C `jset_entry` layout and payload endianness.
- If journal collection returns no entries, the command fails.
- If the latest entry lacks rewind-limit data, fallback is conservative but may overstate safety depending on old formats.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/journal_rewind_info.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/key.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/commands/key.rs

## Purpose
Implements encryption key management commands: unlocking an encrypted filesystem, setting/changing a passphrase, and removing passphrase protection from an encrypted filesystem.

## Main Interfaces
- Commands:
  - `CMD_UNLOCK`
  - `CMD_SET_PASSPHRASE`
  - `CMD_REMOVE_PASSPHRASE`
- CLI structs:
  - `UnlockCli`
  - `SetPassphraseCli`
  - `RemovePassphraseCli`
- Key helpers:
  - `parse_device_list`
  - `open_nostart`
  - `open_and_verify`
  - `set_crypt_key`

## Behavior
- `unlock` reads a device superblock, verifies it is encrypted, optionally exits after `--check`, then adds the key to the selected keyring.
- Unlock can read passphrase from a file or prompt interactively.
- On incorrect passphrase, unlock retries up to two additional interactive attempts.
- `set-passphrase` opens an unmounted filesystem with `nostart`, verifies current encryption state, prompts for a new passphrase twice, encrypts the raw key, revokes the old key, and writes the superblock.
- `remove-passphrase` verifies the current key and writes an unencrypted key into the crypt field.
- Device arguments for passphrase operations can be multiple paths or one colon-separated list.

## Dependencies and Coupling
- Uses `crate::key` primitives: `Passphrase`, `KeyHandle`, `Keyring`, `sb_is_encrypted`, and `unencrypted_key`.
- Uses `sb_io::read_super` for direct superblock reads and `device_scan::open_scan` for multi-device operations.
- Mutates `bch_sb_field_crypt` via `sb_field_get_mut`.
- Calls `bch2_revoke_key` when setting a new passphrase.

## Important Implementation Notes
- `open_and_verify` handles both passphrase-protected and `--no_passphrase` encrypted filesystems.
- `set_crypt_key` is unsafe and documents that the caller must hold the superblock lock, though callers rely on single-threaded nostart mutation and `fs.write_super`.

## Risks and Edge Cases
- Incorrect-passphrase detection matches error string contents.
- The safety comment for `set_crypt_key` is stricter than what callers visibly enforce with a lock.
- `unlock --check` fails if not encrypted and succeeds if encrypted, without validating a passphrase.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/key.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/kill_btree_node.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/commands/kill_btree_node.rs

## Purpose
Implements `bcachefs kill_btree_node`, a debug/testing command that intentionally corrupts selected btree nodes on disk by overwriting block-sized regions with zeroes.

## Main Interfaces
- CLI struct: `KillBtreeNodeCli`
- Command export: `CMD = typed_cmd!("kill_btree_node", ...)`
- Key helpers:
  - `parse_kill_node`
  - `cmd_kill_btree_node`

## Behavior
- Accepts one or more node specs as `btree:level:idx`, with default level `0` and index `0` if omitted.
- Opens the filesystem read-only through `device_scan::open_scan`.
- Iterates btree nodes at the requested btree and level.
- Finds the Nth matching node, then overwrites each matching pointer replica with a zeroed aligned block.
- Optional `--dev` restricts corruption to one device index; otherwise all replicas are targeted.
- Errors if no nodes are specified or a requested node index is not found.

## Dependencies and Coupling
- Uses `BtreeNodeIter`, `BtreeTrans`, `BkeySC`, and extent pointer extraction via `bkey_ptrs`.
- Uses raw block-device fd from `ca.disk_sb.bdev.bd_fd`.
- Depends on block size from `(*fs.raw).opts.block_size`.

## Important Implementation Notes
- Uses `posix_memalign` because bcachefs block-device fds may be opened with O_DIRECT.
- Writes one block of zeroes at `ptr.offset() << 9`.
- Frees the aligned buffer on normal completion and on not-found failure.

## Risks and Edge Cases
- This is deliberately destructive.
- Partial or failed `pwrite` only logs an error and continues.
- The node spec parser expects numeric/parsable btree IDs according to bindgen parser behavior.
- A panic or unexpected early return before explicit free could leak the aligned buffer.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/kill_btree_node.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/list.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/commands/list.rs

## Purpose
Implements `bcachefs list`, a read-only debug command for listing btree metadata contents, btree node formats, btree node keys, or raw on-disk node representations.

## Main Interfaces
- CLI struct: `Cli`
- Mode enum: `Mode`
- Command export: `CMD = typed_cmd!("list", ...)`
- Listing helpers:
  - `list_keys`
  - `list_btree_formats`
  - `list_btree_nodes`
  - `list_nodes_ondisk`

## Behavior
- Opens devices read-only, no changes, no exclusive lock, no recovery, with degraded and error-continue behavior.
- Optional `--fsck` enables recovery and fixes errors before listing.
- `keys` mode walks btree keys at a selected btree/level/range and optional bkey type.
- `formats` mode prints btree node format details.
- `nodes` mode prints btree node keys.
- `nodes-ondisk` prints raw on-disk node text.
- If the start snapshot is zero, key listing uses `ALL_SNAPSHOTS`.
- Uses `-b`, `-s`, `-e`, `-l`, and `-k` to select btree, range, level, and bkey type.

## Dependencies and Coupling
- Uses bcachefs bindgen parser types for `btree_id`, `bch_bkey_type`, and `bpos`.
- Uses `BtreeIter`, `BtreeNodeIter`, and transaction wrappers.
- Uses `logging::setup` for verbosity/color configuration.

## Important Implementation Notes
- Iteration stops once key/node position exceeds the requested end position.
- Node modes iterate from requested level up to `BTREE_MAX_DEPTH`.
- Output is plain text suitable for debugging and diffing.

## Risks and Edge Cases
- `--fsck` uses `fix_errors=yes`, so a command named `list` can cause repair behavior when requested.
- Large ranges can produce very large output.
- The command depends on textual formatting from bcachefs C/Rust wrappers remaining stable enough for tooling.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/list.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/list_journal.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/commands/list_journal.rs

## Purpose
Implements `bcachefs list_journal`, a detailed journal inspection command with sequence filtering, missing-range reporting, transaction/log/key filters, blacklisted-entry handling, and optional key value printing.

## Main Interfaces
- CLI struct: `Cli`
- Command export: `CMD = typed_cmd!("list_journal", ...)`
- Key types:
  - `JournalEntries`
  - `JournalFilter`
  - `TransactionMsgFilter`
  - `TransactionKeyFilter`
- Major helpers:
  - `journal_replay_print`
  - `print_one_entry`
  - `parse_seq_range`
  - `parse_sign`
  - `entry_matches_range`
  - `should_print_transaction`

## Behavior
- Opens devices in read-only, no-recovery, no-change, degraded, continue-on-error, journal-only mode.
- Supports reading all entries, dirty-only entries, a count of recent entries, or a specific sequence/range.
- Reports missing journal ranges using `bch2_journal_entry_missing_range`.
- Can include or suppress blacklisted entries.
- Can restrict output to flush entries, datetime entries, headers only, log-containing transactions, btree IDs, transaction log patterns, or key ranges.
- Can print offsets of journal subentries and suppress bkey values.
- In unfiltered mode, prints journal headers and all matching entries.
- In filtered mode, identifies transaction boundaries and prints only matching transactions, optionally printing all headers.

## Dependencies and Coupling
- Uses journal helpers from `bch_bindgen::journal`.
- Uses `bbpos_range_parse` and bkey range matching logic.
- Uses C text renderers:
  - `bch2_journal_ptrs_to_text`
  - `bch2_prt_jset_entry_type`
  - `bch2_btree_id_level_to_text`
  - `bch2_bkey_to_text`
  - `bch2_journal_entry_to_text`
- Uses `read_flag_list` with `__bch2_btree_ids`.

## Important Implementation Notes
- Blacklisted entries are printed with leading spaces converted to `*` at line starts, preserving visual distinction.
- Log filtering excludes internal subsystem markers: rebalance, reconcile, copygc, promote.
- Key range matching intentionally collapses start to end to match the C behavior noted in the source.
- `-n` computes max sequence from collected entries because `journal.seq` is not available in read-journal-only mode.

## Risks and Edge Cases
- Transaction boundary logic depends on jset entry ordering and classification helpers.
- Filter behavior is subtle where positive and negative key ranges combine.
- `star_start_of_lines` is custom formatting logic and may not cover every leading-space case.
- Large journals can consume memory in collected C replay arrays and Rust vectors.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/list_journal.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/migrate.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/commands/migrate.rs

## Purpose
Implements in-place migration from an existing mounted filesystem to bcachefs, plus the follow-up `migrate-superblock` command that installs default superblock locations after validation.

## Main Interfaces
- Raw command export: `CMD_MIGRATE`
- Typed command export: `CMD_MIGRATE_SUPERBLOCK`
- Main functions:
  - `cmd_migrate`
  - `migrate_fs`
  - `migrate_superblock`
  - `reserve_new_fs_space`
  - `mark_unreserved_space`
  - `add_default_sb_layout`

## Behavior
- `migrate` requires `-f <filesystem-root>`.
- Verifies the path is a filesystem mount root via `/proc/self/mountinfo`.
- Resolves the underlying block device using `/sys/dev/block/<major>:<minor>`.
- Creates/reserves a `bcachefs` metadata file inside the old filesystem, using fallocate and FIEMAP.
- Formats a bcachefs filesystem in the reserved extents, with superblocks located inside those extents rather than default offsets.
- Marks all unreserved space as no-use so old filesystem data is protected.
- Starts the new filesystem, sets `BCH_FEATURE_no_default_sb`, copies the old filesystem tree into bcachefs, exits, and reopens read-only to run a basic fsck/open check.
- Prints instructions for mounting by explicit `sb=` offset and later running `migrate-superblock`.
- `migrate-superblock` reads the migrated superblock at an explicit offset, adds default layout entries, zeros the start of disk to remove old superblock data, reopens bcachefs, clears `no_default_sb`, marks new superblock buckets, starts the fs, then applies layout changes.

## Dependencies and Coupling
- Uses `fiemap` crate to discover reserved physical extents.
- Uses raw C helper `rust_set_bit` to mark buckets no-use.
- Uses `copy_fs::copy_fs` with migrate-specific state.
- Uses format utilities for picking block/bucket sizes and formatting.
- Uses `super_io::__bch2_super_read` and superblock layout wrappers.

## Important Implementation Notes
- Reserved metadata file size starts at device size and halves on ENOSPC down to 10% of device size.
- FIEMAP extents must be aligned to the selected block size.
- Default superblock layout reserves sector `BCH_SB_SECTOR` and the following superblock-size offset.
- `migrate_superblock` sets `BCH_FS_may_upgrade_downgrade` manually because fs init already ran before clearing `no_default_sb`.

## Risks and Edge Cases
- This is highly invasive and depends on correct physical extent reporting by the source filesystem.
- `path_is_fs_root` compares raw mountinfo mountpoint strings and does not unescape mountinfo path escaping.
- Marking no-use buckets relies on accurate extent and device-size calculations.
- Superblock migration zeros the beginning of the disk before reopening bcachefs.
- `migrate_superblock` calls `add_default_sb_layout` before and after opening; the first validates/readies the buffer, the second mutates the live per-device superblock.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/migrate.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/mod.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/commands/mod.rs

## Purpose
Defines the central bcachefs command framework: command metadata, typed/raw command macros, group command dispatch, clap CLI construction, module declarations, and top-level command grouping.

## Main Interfaces
- Types:
  - `CmdDef`
  - `CmdKind`
  - `GroupDef`
- Macros:
  - `typed_cmd!`
  - `raw_cmd!`
- Public functions:
  - `dispatch`
  - `build_cli`
  - `defers_shrinkers`
- Command table:
  - `COMMAND_GROUPS`

## Behavior
- `typed_cmd!` wraps a clap `Parser` type and handler into a `CmdDef`.
- `raw_cmd!` wraps manual argv parsers into a `CmdDef`.
- `CmdDef::dispatch` handles typed, raw, and group commands.
- Group commands dispatch to children by name or alias, otherwise print group help.
- `build_cli` constructs a clap command with all top-level subcommands.
- `defers_shrinkers` returns true for `mount` and `fusemount`.
- Defines a synthetic `fs` command group and an inline `version` command.

## Dependencies and Coupling
- Declares all command modules in this directory.
- Command grouping is the single registry used by dispatch/help.
- Relies on each module exporting expected `CMD` constants.
- Version command reads `../../version.h` at compile time.

## Important Implementation Notes
- Group child dispatch passes `argv[1..]`, making the child subcommand name become argv[0].
- Group help exits success for no subcommand or help request, failure for unknown subcommands.
- Aliases are stored per command and checked in both dispatch and group child matching.

## Risks and Edge Cases
- Any command missing from `COMMAND_GROUPS` is not reachable even if its module exists.
- `clap_command` for raw commands has minimal argument metadata.
- The command table manually controls user-visible organization and can drift from module additions.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/mount.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/commands/mount.rs

## Purpose
Implements `bcachefs mount`, including device discovery by UUID/device string, encrypted filesystem unlocking, kernel module probing, mount-option splitting, direct kernel mount, and delegation to FUSE mounting for `-t bcachefs.fuse`.

## Main Interfaces
- CLI struct: `Cli`
- Command export: `CMD`
- Key functions:
  - `mount`
  - `cmd_mount_inner`
  - `mount_inner`
  - `parse_mountflag_options`
  - `handle_unlock`
  - `check_bcachefs_module`

## Behavior
- Splits comma-separated mount options into Linux mount flags and bcachefs-specific options.
- Scans superblocks and joins member devices into the mount source string.
- Detects encrypted superblocks and unlocks using explicit policy, passphrase file, keyring search, or prompt.
- If mountpoint is absent, performs discovery/unlock but does not call `mount`.
- Calls `libc::mount` with filesystem type `bcachefs`.
- If write mount fails with `EACCES` or `EROFS`, retries read-only.
- If `--type bcachefs.fuse` is requested, constructs a `fusemount::Cli` and calls `cmd_fusemount`.
- Logs failure and hints when the bcachefs module was not loaded.

## Dependencies and Coupling
- Uses `device_scan::scan_sbs` and `joined_device_str`.
- Uses `KeyHandle`, `Keyring`, `Passphrase`, and `UnlockPolicy`.
- Uses `bch2_sb_is_encrypted` C helper.
- Delegates FUSE path to `commands::fusemount`.
- Uses `logging::setup` for color/verbosity.

## Important Implementation Notes
- Mount flags recognized include standard VFS flags and ignored userspace/fstab-only options.
- Unknown mount options are passed through to bcachefs as filesystem-specific option string.
- `CString`s are held in local bindings through the `mount` syscall.
- `check_bcachefs_module` attempts `modprobe bcachefs`.

## Risks and Edge Cases
- FUSE mode uses an empty mountpoint string if none is supplied, likely causing a later mount failure.
- Mountinfo and device scanning behavior live outside this file.
- The `fs_type` argument is accepted but only special-cases `bcachefs.fuse`; normal path always mounts as `bcachefs`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/mount.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/opts.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/commands/opts.rs

## Purpose
Provides shared option-table utilities for command-line handling of bcachefs filesystem/device/format options exposed from the C option table.

## Main Interfaces
- Public helpers:
  - `opts_usage_str`
  - `bch_option_args`
  - `bch_opt_lookup_negated`
  - `bch_opt_lookup`
  - `bch_option_names`
  - `bch_options_from_matches`
- Crate helper:
  - `parse_opt_val`

## Behavior
- Iterates `bch2_opt_table` entries by flag filter while skipping hidden options.
- Generates formatted usage text with option type hints, string choices, and help text.
- Builds clap `Arg`s dynamically for matching bcachefs options.
- Handles boolean options with optional values and hidden negated forms such as `--nofoo`/`--no-foo`.
- Extracts selected option/value pairs from clap matches.
- Looks up option IDs by name through C `bch2_opt_lookup`.
- Parses option values with `bch2_opt_parse`, returning `None` when the option needs an open filesystem and must be deferred.

## Dependencies and Coupling
- Coupled directly to `bch_bindgen::opts::opt_table`, `c::bch2_opt_table`, and option flag/type enums.
- Uses `Printbuf` to capture C parse errors.
- Used by commands such as `image`, `migrate`, and `set_option`.

## Important Implementation Notes
- `leak` intentionally leaks dynamically generated strings to satisfy clap’s `'static` argument-name/alias requirements.
- `bch_opt_lookup_negated` accepts both `no_foo` and `nofoo` prefixes, then verifies the target option is boolean.
- `parse_opt_val` calls C parser with null filesystem context.

## Risks and Edge Cases
- Runtime-generated clap args depend on stable option table contents at startup.
- Leaked strings are process-lifetime allocations by design.
- Negated option naming can be ambiguous for option names naturally beginning with `no`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/opts.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/reconcile.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/commands/reconcile.rs

## Purpose
Implements `bcachefs reconcile` command group for viewing and waiting on background reconcile accounting work.

## Main Interfaces
- Command group export: `CMD`
- Subcommands:
  - `CMD_STATUS`
  - `CMD_WAIT`
- CLI structs:
  - `StatusCli`
  - `WaitCli`
- Main helpers:
  - `reconcile_status_to_text`
  - `reconcile_wait_tui`
  - `reconcile_wait_headless`

## Behavior
- `status` opens a mounted filesystem, queries reconcile accounting, prints scan-pending state, per-type data/metadata work, and appends kernel `reconcile_status` sysfs text when available.
- `wait` triggers `internal/trigger_reconcile_wakeup`, then polls until selected reconcile work types are complete.
- In interactive terminals, wait mode uses an alternate-screen TUI with live updates and exits on `q`, Esc, or Ctrl-C.
- In non-interactive mode, wait mode sleeps one second between polls and produces no progress output.
- Default status types include all reconcile types; default wait types exclude `Pending`.

## Dependencies and Coupling
- Uses `BcachefsHandle` for mounted filesystem access.
- Uses sysfs files:
  - `reconcile_scan_pending`
  - `reconcile_status`
  - `internal/trigger_reconcile_wakeup`
- Uses accounting query mask `BCH_DISK_ACCOUNTING_reconcile_work`.
- Uses `DiskAccountingKind::ReconcileWork` decoding and `prt_reconcile_type`.

## Important Implementation Notes
- Per-type counters are stored as `[data_sectors, metadata_sectors]`.
- Output uses `Printbuf` tab-stop alignment and human-readable sector units.
- TUI uses crossterm and `run_tui` wrapper.

## Risks and Edge Cases
- Missing sysfs files are treated as zero or skipped depending on file.
- Headless wait has no timeout or status output.
- `event::poll(Duration::ZERO)` drains extra terminal input after a key event.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/reconcile.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/recover_super.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/commands/recover_super.rs

## Purpose
Implements `bcachefs recover-super`, which recovers damaged or overwritten superblocks either by scanning a device for backup superblocks or by rebuilding a member superblock from another member’s superblock.

## Main Interfaces
- CLI struct: `RecoverSuperCli`
- Command export: `CMD = typed_cmd!("recover-super", ...)`
- Key functions:
  - `cmd_recover_super`
  - `recover_from_scan`
  - `recover_from_member`
  - `probe_one_super`
  - `probe_sb_range`
  - `validate_sb`

## Behavior
- Supports explicit device size, explicit probe offset, scan length, source member device plus target dev index, `--yes`, and verbose scanning.
- Scanning mode probes a specific offset when given, otherwise scans from the beginning and end of the device.
- Candidate superblocks are validated with `bch2_sb_validate`.
- Chooses the candidate with the most recent member last-mount time.
- Member-copy mode reads a source filesystem superblock, validates dev index, deletes journal fields, sets target `dev_idx`, and reinitializes the superblock layout for the target device size.
- Prints the recovered superblock text before prompting.
- Writes the recovered superblock when `--yes` is set or the user confirms.
- Runs `udevadm trigger --settle <device>` after writing.
- Warns that member-copy recovery removes the journal and requires fsck.

## Dependencies and Coupling
- Uses custom extern declaration for `bch2_sb_validate` because bindgen enum typing does not accept raw `0`.
- Uses `super_io` magic constants, `vstruct_bytes_sb`, `sb_layout_init`, and `bch2_super_write`.
- Uses C field deletion for journal and journal_v2 fields.
- Uses `Printbuf::sb_to_text`.

## Important Implementation Notes
- Buffer-to-superblock conversion is unsafe and assumes adequate alignment and size.
- Scan offsets are 512-byte aligned.
- Scanning validates magic before computing variable structure length.
- `recover_from_member` copies the source C-allocated superblock into an owned byte buffer before the handle drops.

## Risks and Edge Cases
- `recover_from_scan` computes `dev_size - scan_len`; if scan length exceeds device size this can underflow.
- Candidate validation mutates the buffer through `bch2_sb_validate`.
- The final user prompt uses C `ask_yn`.
- Member-copy mode intentionally removes journal fields, changing recovery requirements.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/recover_super.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/recovery_pass.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/commands/recovery_pass.rs

## Purpose
Implements `bcachefs recovery-pass`, a superblock-editing command for listing, scheduling, and descheduling required recovery passes.

## Main Interfaces
- CLI struct: `RecoveryPassCli`
- Command export: `CMD = typed_cmd!("recovery-pass", ...)`
- Main handler: `cmd_recovery_pass`

## Behavior
- Parses `--set` and `--unset` recovery pass flag lists using the C recovery-pass name table.
- Converts pass masks to stable on-disk numbering before modifying the superblock extension field.
- Opens the filesystem with `nostart`.
- Gets or creates the `bch_sb_field_ext` field.
- Updates `recovery_passes_required[0]` by clearing unset bits and setting requested bits.
- Writes the superblock if changes were requested.
- Prints scheduled recovery passes using the C bitflag printer, or `(none)`.

## Dependencies and Coupling
- Uses `read_flag_list` with `c::bch2_recovery_passes`.
- Uses C conversions:
  - `bch2_recovery_passes_to_stable`
  - `bch2_recovery_passes_from_stable`
- Uses `sb_field_get_minsize` and `wrappers::sb_lock`.

## Important Implementation Notes
- The lock guard is explicitly dropped before formatting output.
- Only the first u64 of `recovery_passes_required` is modified.

## Risks and Edge Cases
- Multiword recovery-pass masks would require extending beyond `[0]`.
- The command writes superblock state directly and assumes the filesystem is not started.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/recovery_pass.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/scrub.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/commands/scrub.rs

## Purpose
Implements `bcachefs scrub`, which starts checksum/data scrub operations through a filesystem ioctl and displays per-device progress, corrected errors, and uncorrected errors.

## Main Interfaces
- CLI struct: `Cli`
- Command export: `CMD = typed_cmd!("scrub", ...)`
- Key types/functions:
  - `ScrubDev`
  - `start_scrub`
  - `read_data_event`
  - `sigint_handler`
  - `scrub`

## Behavior
- Supports `--metadata` to scrub only btree metadata; otherwise scrubs all data types.
- Opens a mounted filesystem or device through `BcachefsHandle`.
- Reads sysfs device list and determines whether the handle targets a specific device or the whole filesystem.
- Starts one scrub operation per target device via `BCH_IOCTL_DATA_OP_scrub`.
- Reads fixed-size progress events from returned fds.
- Prints a live table with checked, corrected, uncorrected, total, percent, and current rate/status.
- Rewrites progress lines in place using ANSI cursor movement.
- Handles SIGINT by setting an atomic flag and exits with bit `1`.
- Sets exit code bit `2` if any errors were corrected and bit `4` if any uncorrected errors were found.

## Dependencies and Coupling
- Uses `bch_ioctl_data` and raw ioctl number `BCH_IOCTL_DATA_NR = 10`.
- Uses manual raw parsing for blocklisted `bch_ioctl_data_event` layout.
- Uses sysfs helpers `fs_get_devices` and `sysfs_path_from_fd`.
- Uses human-format helpers for bytes/sectors.

## Important Implementation Notes
- `DATA_EVENT_SIZE` is fixed at 128 bytes, matching the packed C event layout documented in the file.
- Progress rate is computed from sector delta and elapsed nanoseconds.
- Non-progress event types keep the device active and print zero rate.
- Closing/removing `progress_fd` marks a device complete or offline depending on returned status.

## Risks and Edge Cases
- Manual event parsing is ABI-sensitive.
- `libc::signal` installs a simple handler; only atomic store is performed, which is appropriate.
- Terminal line rewriting assumes a terminal-like output even when stdout is redirected.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/scrub.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/set_option.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/commands/set_option.rs

## Purpose
Implements `bcachefs set-fs-option`, allowing filesystem and device options to be changed either online through sysfs or offline by editing superblock options.

## Main Interfaces
- Command export: `CMD = raw_cmd!("set-fs-option", ...)`
- Main functions:
  - `set_option_cmd`
  - `cmd_set_option`
  - `set_option_online`
  - `set_option_offline`
  - `name_to_dev_idx`

## Behavior
- Dynamically builds clap arguments for all filesystem/device options using `bch_option_args`.
- Requires at least one device path and at least one option.
- Detects online mode if any supplied device is mounted through sysfs.
- Online mode opens the first device as a mounted filesystem handle, verifies additional devices are members by UUID, then writes fs options to `options/<name>` and device options to `dev-<idx>/<name>`.
- Offline mode opens devices with `nostart`, parses option values with filesystem context, runs pre-set hooks, and writes fs/device values into the superblock.
- Device option targeting can be explicit with `--dev-idx` or inferred from supplied device names.

## Dependencies and Coupling
- Uses shared option helpers from `commands::opts`.
- Uses `BcachefsHandle` and sysfs write helpers for online changes.
- Uses C functions:
  - `bch2_opt_parse`
  - `bch2_opt_hook_pre_set`
  - `bch2_opt_set_sb`
- Uses raw `(*fs.raw).devs` traversal for device lookup.

## Important Implementation Notes
- Online device-scoped writes open each device to discover its device index, then write through the first filesystem handle’s sysfs fd.
- Offline `name_to_dev_idx` compares the bcachefs device name field, not necessarily the path.
- Errors for individual invalid/unsupported options are printed and processing continues.

## Risks and Edge Cases
- If any device is mounted, the command treats the whole operation as online.
- Offline device inference by internal device name may not match user-supplied paths.
- Online writes ignore return values from `sysfs_write_str`.
- Superblock writes are not followed by an explicit `fs.write_super()` in this file after offline option mutation, so persistence depends on wrapper/drop behavior or C side effects.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/set_option.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/strip_alloc.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/commands/strip_alloc.rs

## Purpose
Implements `bcachefs strip-alloc`, which strips allocation information from a clean filesystem for read-only/small-image use, with a capacity guard for reconstruction limits.

## Main Interfaces
- CLI struct: `Cli`
- Command export: `CMD = typed_cmd!("strip-alloc", ...)`
- Main handler: `cmd_strip_alloc`

## Behavior
- Opens supplied devices with `nostart`.
- If the filesystem is not clean, starts recovery, drops the fs handle, and loops to reopen.
- Computes total capacity across devices from `nbuckets * bucket_size`.
- Refuses to strip allocation info if total capacity exceeds 1 TiB.
- Calls C helper `rust_strip_alloc_do(fs.raw)` to perform the strip.
- Prints the first device path being stripped.

## Dependencies and Coupling
- Uses `device_scan::open_scan`.
- Uses raw `(*fs.raw).sb.clean`.
- Uses `bch2_fs_start` for recovery and `rust_strip_alloc_do` for stripping.
- Uses `fs.dev_get` and device member metadata for capacity calculation.

## Important Implementation Notes
- The loop retries after recovery until the filesystem opens clean.
- Capacity is computed in bytes by shifting bucket sectors by 9.

## Risks and Edge Cases
- The loop can repeat if recovery does not leave the filesystem clean.
- The 1 TiB limit is hardcoded based on allocation-info reconstruction capability.
- Recovery is triggered even though the command otherwise opens with `nostart`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/strip_alloc.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/subvolume.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/commands/subvolume.rs

## Purpose
Implements `bcachefs subvolume` command group for creating, deleting, snapshotting, listing subvolumes, and listing snapshot usage/tree information.

## Main Interfaces
- CLI struct: `Cli`
- Subcommand enum: `Subcommands`
- Command export: `CMD = typed_cmd!("subvolume", ..., aliases: ["subvol"], ...)`
- Core helpers:
  - `bcachefs_ioctl`
  - `bcachefs_flex_ioctl`
  - `subvol_readdir`
  - `subvol_to_path`
  - `query_snapshot_tree`
  - `compute_subvol_sizes`
  - listing/printing helpers for flat, tree, and JSON output.

## Behavior
- `create` creates one or more subvolumes at target paths.
- `delete` canonicalizes and deletes target subvolumes.
- `snapshot` creates a COW snapshot, optionally read-only, with optional source path.
- `list` supports flat, recursive, tree, JSON, snapshot inclusion, read-only filtering, and sorting by name/size/time.
- `list-snapshots` supports tree, flat, JSON, read-only filtering, and sorting for flat output.
- Uses kernel ioctls for subvolume listing, subvolume ID to path, and snapshot tree usage.
- Calculates cumulative subvolume size by walking from each snapshot node up through ancestors.
- Formats flags, timestamps, human-readable sizes, snapshot-parent relationships, and nested children.

## Dependencies and Coupling
- Uses `BcachefsHandle` for create/delete/snapshot operations.
- Uses ioctl numbers:
  - `BCH_IOCTL_SUBVOLUME_LIST = 31`
  - `BCH_IOCTL_SUBVOLUME_TO_PATH = 32`
  - `BCH_IOCTL_SNAPSHOT_TREE_USAGE = 33`
- Uses bindgen ioctl structs:
  - `bch_ioctl_snapshot_node`
  - `bch_ioctl_subvol_dirent`
  - `bch_ioctl_subvol_readdir`
- Uses `serde_json` for JSON output and `chrono::Local` for timestamps.

## Important Implementation Notes
- `FlexArrayIoctl` abstracts retrying flexible-array ioctls when the kernel returns `ERANGE`.
- `subvol_readdir` parses variable-length records from a 64 KiB buffer.
- Tree output uses Unicode branch characters.
- Snapshot tree output handles `ENOTTY` by printing that the ioctl is unsupported and returning success.
- Relative create targets are resolved against current directory before opening the containing filesystem.

## Risks and Edge Cases
- `subvol_to_path` uses a fixed 4096-byte buffer.
- Recursive collection ignores errors opening nested subvolumes in `collect_entries`, but JSON recursion propagates errors.
- Tree output uses Unicode despite most Rust files being ASCII.
- `SortBy::Time` is ignored for snapshot flat output.
- Ioctl struct definitions and numbers must match kernel ABI exactly.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/subvolume.rs -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/super_cmd.rs -->
# File Research: sources/cow-pools/bcachefs-tools/src/commands/super_cmd.rs

## Purpose
Implements `bcachefs show-super`, which prints bcachefs superblock information from a device, with field filtering and layout display support.

## Main Interfaces
- CLI struct: `ShowSuperCli`
- Command export: `CMD = typed_cmd!("show-super", ...)`
- Main handler: `cmd_show_super`

## Behavior
- Supports `--fields` with comma-separated superblock field names or `all`.
- Supports `--field-only` for scripting a single field without a header.
- Supports `--layout` to print superblock layout.
- Opens the device with `noexcl`, `nochanges`, `no_version_check`, and `nostart`.
- Iterates online members and prints each per-device superblock.
- By default prints `ext`, `members_v1` or `members_v2`, and `errors` fields.
- Uses `sb_to_text_with_names` to format selected fields.

## Dependencies and Coupling
- Uses C flag parsers:
  - `bch2_read_flag_list`
  - `match_string`
- Uses `bch2_sb_fields` table.
- Uses `Fs::open` and `for_each_online_member`.
- Uses per-device `ca.disk_sb.sb`, not filesystem-level `c->disk_sb.sb`.

## Important Implementation Notes
- The file documents why per-device superblocks are used: filesystem-level copies omit fields such as magic and layout.
- Help flag is manually enabled with `disable_help_flag = true` plus an explicit hidden field.

## Risks and Edge Cases
- Invalid field names are fatal.
- Output can include multiple member superblocks when multiple devices are online.
- Field bitmask is u32, so it assumes field IDs fit that width.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/src/commands/super_cmd.rs -->