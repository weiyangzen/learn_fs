# Group Research: group_1820_winbtrfs_sources_windows_winbtrfs_src_send_c_sources_windows_winbtr_4d4c175c861c

Scope confirmed against `Docs/research_subset_a.md`. All four listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/send.c -->
# File Research: sources/windows/winbtrfs/src/send.c

## Purpose

`send.c` implements WinBtrfs subvolume send support. It builds Btrfs send-stream commands for a read-only subvolume, optionally comparing it against a parent snapshot for incremental sends, and exposes the generated stream through a buffered asynchronous kernel worker.

## Main State

The central `send_context` ties together:

- Filesystem state: `Vcb`, target `root`, optional `parent`, optional clone roots.
- Output stream buffer: `data`, `datalen`, `buffer_event`, and `send_info`.
- Directory/path tracking:
  - `send_dir` records inode, parent, name, timestamps, dummy/orphan status, and deleted children.
  - `orphan` tracks temporary names used while rename/delete ordering is resolved.
  - `ref` stores current and old inode references.
  - `pending_rmdir` delays directory removal until children have been processed.
- Per-inode accumulation in `lastinode`:
  - inode metadata, old metadata, current path, orphan/dir pointers
  - current/old refs
  - current/old extent lists

The file uses `MAX_SEND_WRITE` of 48 KiB and a 1 MiB `SEND_BUFFER_LENGTH`; the allocation gives extra space for write command overhead.

## Send Command Encoding

Low-level helpers build the stream format:

- `send_command()` reserves a `btrfs_send_command` with a command id and zero checksum.
- `send_add_tlv()` appends typed-length-value fields.
- `send_command_finish()` fills command length and CRC32C checksum.
- `send_add_tlv_path()`, `find_path_len()`, and `find_path()` construct slash-separated paths from tracked directory parents.
- `send_subvol_header()` emits either `BTRFS_SEND_CMD_SUBVOL` or `BTRFS_SEND_CMD_SNAPSHOT`, including target UUID/transid and parent clone UUID/transid when applicable.

Metadata command helpers emit `CHOWN`, `CHMOD`, `UTIMES`, `TRUNCATE`, `UNLINK`, and `RMDIR`.

## Path, Ref, and Orphan Handling

The implementation has substantial ordering logic to make generated operations replayable:

- `get_orphan_name()` generates unique temporary root-level names of the form `o<inode>-<generation>-<index>`, checking current and parent roots for collisions.
- `find_send_dir()` locates or creates `send_dir` records, using parent snapshot refs when available and dummy orphan paths otherwise.
- `send_inode_ref()` and `send_inode_extref()` parse `INODE_REF` and `INODE_EXTREF` items into current or old ref lists.
- `found_path()` resolves an orphaned inode by renaming it into its real path, or links another name to the existing path.
- `look_for_collision()` checks the parent snapshot for path collisions before renames/links.
- `make_file_orphan()` renames colliding files/directories to temporary orphan names or records deleted non-directory children.
- `flush_refs()` compares current and old refs, handles new paths, deletes old paths, moves/renames directories, delays non-empty directory removals, and emits parent directory timestamp restoration when needed.

This logic is necessary because Btrfs tree item order does not always match a safe replay order for directory renames and deletions.

## Inode Processing

`send_inode()` initializes `lastinode` from an `INODE_ITEM`, detects deletes, records new-vs-existing state, and emits creation commands for new objects:

- `MKSOCK`
- `SYMLINK`
- `MKNOD`
- `MKDIR`
- `MKFIFO`
- `MKFILE`

For symlinks, `send_read_symlink()` reads inline extent data and adds `BTRFS_SEND_TLV_PATH_LINK`. New objects are first created under orphan names, then moved or linked into final paths after refs are known.

`finish_inode()` flushes refs and extents, emits truncate/chown/chmod/utimes for non-deleted inodes, frees accumulated extent/ref state, and processes pending directory removals whose last child inode has now passed.

## Extent Handling

File data is accumulated through `send_extent_data()` and emitted by `flush_extents()`.

Key behavior:

- It validates extent item sizes, compression, encryption, and encoding.
- It skips symlink extent data.
- It records non-empty inline and regular extents for current and parent roots.
- For incremental sends, `add_ext_holes()` inserts sparse hole extents and `sync_ext_cutoff_points()` splits current/old extents so comparable ranges align.
- `divide_ext()` splits inline or regular extents at a requested logical length.
- `try_clone()` and `try_clone_edr()` inspect extent backrefs and clone roots to emit `BTRFS_SEND_CMD_CLONE` when a matching sector-aligned source extent can be found.
- Inline uncompressed data is emitted directly.
- Inline compressed data is decompressed before sending.
- Regular sparse extents are emitted as zero-filled writes.
- Regular uncompressed extents are read from disk with checksums unless `BTRFS_INODE_NODATASUM` is set.
- Regular compressed extents are read, decompressed using zlib/LZO/ZSTD helpers, then emitted in write chunks.

Unsupported or unknown compression/encryption/encoding paths return errors rather than generating a questionable stream.

## Xattrs

`send_xattr()` emits xattr changes after refs have been flushed so a valid path exists:

- Current-only xattrs become `BTRFS_SEND_CMD_SET_XATTR`.
- Parent-only xattrs become `BTRFS_SEND_CMD_REMOVE_XATTR`.
- Current+parent xattrs are compared by name and value; only changed, added, or removed xattrs produce commands.
- Xattrs are parsed from `DIR_ITEM` payloads with truncation checks.

## Worker Thread

`send_thread()` is the asynchronous producer.

Main flow:

1. Increments send operation counters for target, parent, and clone roots.
2. Acquires the tree lock exclusively, flushes subvolume FCBs, writes pending filesystem state if needed, frees cached trees, then downgrades to shared.
3. Traverses the target root and, for incremental sends, the parent root in key order.
4. Uses `skip_to_difference()` when both traversals are in the same tree block.
5. Dispatches by item type:
   - `TYPE_INODE_ITEM` -> `send_inode`
   - `TYPE_INODE_REF` -> `send_inode_ref`
   - `TYPE_INODE_EXTREF` -> `send_inode_extref`
   - `TYPE_EXTENT_DATA` -> `send_extent_data`
   - `TYPE_XATTR_ITEM` -> `send_xattr`
6. Calls `finish_inode()` when moving to the next inode.
7. Periodically releases the tree lock and signals the reader when the send buffer exceeds the threshold.
8. On completion or error, signals the buffer, stores status, frees all context state, removes the send from `Vcb->send_ops`, decrements counters, and terminates the system thread.

`wait_for_flush()` handles the producer/consumer handshake, preserves traversal keys, reacquires the tree lock, and verifies the read-only subvolume did not change while the lock was released.

## Public Entry Points

- `send_subvol(...)`
  - Validates the file object, target is a subvolume root, caller has `SE_MANAGE_VOLUME_PRIVILEGE`, and target/parent/clone roots are read-only unless the volume itself is read-only.
  - Accepts optional parent and clone handles, including 32-bit process handle layouts on Win64.
  - Allocates `send_context`, stream buffer, and `send_info`.
  - Emits the subvolume/snapshot header immediately.
  - Starts `send_thread()` and links the send operation to the CCB and VCB.
- `read_send_buffer(...)`
  - Requires `SE_MANAGE_VOLUME_PRIVILEGE`.
  - Waits for producer data, copies up to caller length, shifts remaining bytes if partially consumed, and signals the producer when the buffer is drained.
  - Returns stored failure status or `STATUS_END_OF_FILE` when no send remains.

## Integration

This file depends on core WinBtrfs tree traversal, item parsing, extent backref parsing, checksum loading, compression decompression, disk reads, FCB flushing, locking, and IOCTL-facing `send_info` state defined elsewhere in the driver. It is the bridge between on-disk Btrfs metadata and the userspace-readable Btrfs send protocol stream.

## Notable Risks and Edge Cases

- Correctness depends heavily on read-only roots remaining stable; the code explicitly treats key changes after buffer flush as internal errors.
- The path/orphan logic is complex and stateful; replay correctness relies on maintaining sorted orphan/dir/pending-rmdir lists.
- Many allocations happen while generating a send stream; low-memory paths usually return `STATUS_INSUFFICIENT_RESOURCES` but must unwind partially accumulated state.
- Clone detection is opportunistic. If no valid clone source is found, data is sent as writes.
- Compressed extents are decompressed before send writes; unsupported compression returns `STATUS_NOT_IMPLEMENTED`.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/send.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/sha256.c -->
# File Research: sources/windows/winbtrfs/src/sha256.c

## Purpose

`sha256.c` provides a compact standalone SHA-256 implementation used by WinBtrfs. The file notes it is public-domain code from `amosnier/sha-2` and includes a FIXME for possible x86 SHA extension acceleration.

## Main Contents

- SHA-256 round constants `k[64]`.
- `struct buffer_state`
  - tracks input pointer, remaining length, total length, whether the `0x80` padding byte has been emitted, and whether the final length block has been emitted.
- `right_rot()`
  - 32-bit rotate-right helper for SHA-256 bit operations.
- `init_buf_state()`
  - initializes the padding/input iterator.
- `calc_chunk()`
  - produces successive 64-byte chunks from input.
  - Copies full input chunks directly.
  - For final chunks, appends `0x80`, zero padding, and the big-endian 64-bit bit length.
  - Returns an integer used as a boolean to indicate whether a chunk was produced.
- `calc_sha256(uint8_t* hash, const void* input, size_t len)`
  - public function that computes the 32-byte digest.

## Algorithm Details

`calc_sha256()` initializes the standard eight SHA-256 hash words and processes 512-bit chunks. It uses a 16-word rolling message schedule instead of a full 64-word array to reduce stack use. For each round it computes the standard SHA-256 `S0`, `S1`, `ch`, `maj`, `temp1`, and `temp2` values and updates the eight working variables.

At the end, it writes the digest in big-endian byte order.

## Limitations

- The input must already be resident in memory; the implementation is not streaming across external file/data sources.
- Input length is expressed in bytes only. It does not support non-byte-aligned bit strings.
- The stored bit length is derived from `size_t`; practical behavior for inputs whose bit length exceeds what the platform size can represent is not extended beyond this simple implementation.
- No hardware acceleration is implemented in this file.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/sha256.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/shellext/balance.cpp -->
# File Research: sources/windows/winbtrfs/src/shellext/balance.cpp

## Purpose

`balance.cpp` implements the WinBtrfs shell extension UI and elevated command callbacks for Btrfs balance operations. It lets users configure balance filters, start balance, pause/resume balance, stop balance, and monitor progress through WinBtrfs FSCTLs.

## Balance Operation Launching

`BtrfsBalance::StartBalance()`:

- Builds a `btrfs_start_balance` structure from data, metadata, and system option sets.
- Enables or disables each option group based on dialog checkboxes.
- Serializes the binary request into a hex string.
- Relaunches the shell extension DLL through `rundll32.exe` using `ShellExecuteExW` with `lpVerb = "runas"` for elevation.
- Calls the exported `StartBalanceW` callback in the elevated process.
- Updates dialog state to running: disables main checkboxes/start, enables pause/cancel/progress.

`PauseBalance()` and `StopBalance()` use the same elevated `rundll32.exe` pattern, targeting `PauseBalanceW` and `StopBalanceW`.

Binary serialization helpers:

- `hex_digit()` and `serialize()` turn request bytes into wide-character hex.
- `from_hex_digit()` and `unserialize()` decode the elevated command-line payload back into `btrfs_start_balance`.

## Status Refresh

`BtrfsBalance::RefreshBalanceDlg()` opens the target path with backup/reparse flags and calls `FSCTL_BTRFS_QUERY_BALANCE`.

It updates UI based on status:

- Stopped:
  - disables pause/cancel/progress
  - enables option selection when not readonly
  - displays no balance, cancelled, complete, or failed messages
  - handles special text for remove-device and shrink-device flows
- Running or paused:
  - disables option selection
  - syncs checked data/metadata/system boxes from queried options
  - updates progress range and position from `total_chunks` and `chunks_left`
  - changes progress state for paused vs running
  - displays standard, removal, or shrinking progress text

The class tracks `cancelling`, `removing`, `shrinking`, and previous `balance_status` to avoid redundant UI resets and choose the correct localized messages.

## Option Saving

`BtrfsBalance::SaveBalanceOpts()` writes UI selections into one of:

- `data_opts`
- `metadata_opts`
- `system_opts`

Supported balance filters/options include:

- profiles: single, dup, RAID0, RAID1, RAID10, RAID5, RAID6, RAID1C3, RAID1C4
- device id
- physical/device range
- virtual range
- limit range
- stripe count range
- usage range
- conversion target
- soft conversion flag

The function validates start/end ordering for range-like filters and throws localized string errors if an end value is below its start value.

## Options Dialog

`BtrfsBalance::BalanceOptsDlgProc()` owns the balance options dialog.

On `WM_INITDIALOG` it:

- Selects the correct option set based on `opts_type`.
- Uses queried live options instead of stored options if balance is already running.
- Populates the device combo from the `btrfs_device` list.
- Populates the conversion combo from profile types, restricting RAID levels based on the number of writable devices.
- Initializes all checkboxes, spinners, edit fields, and enabled/disabled states.
- Disables editing while a balance is already running or paused.

On checkbox clicks it enables or disables dependent controls for each option category. On OK it either closes immediately for a running balance or calls `SaveBalanceOpts()` for an editable configuration.

`stub_BalanceOptsDlgProc()` stores and retrieves the `BtrfsBalance*` pointer through `GWLP_USERDATA` and forwards messages to the instance method.

## Main Balance Dialog

`BtrfsBalance::BalanceDlgProc()` owns the main balance dialog.

On initialization it:

- Clears option structures.
- Initializes remove/shrink status flags from constructor inputs.
- Calls `RefreshBalanceDlg(..., true)`.
- Applies readonly disabling.
- Adds UAC shield icons to start/pause/cancel buttons.
- Starts a one-second timer for status refresh.

Command handling covers:

- OK/cancel closing
- data/metadata/system checkbox changes
- option dialog buttons
- start, pause/resume, and cancel buttons

`stub_BalanceDlgProc()` is the instance forwarding thunk for the dialog procedure.

## Device Discovery

`BtrfsBalance::ShowBalance()`:

- Frees any old device list.
- Opens the target path.
- Calls `FSCTL_BTRFS_GET_DEVICES`, growing the buffer on `STATUS_BUFFER_OVERFLOW` up to a bounded retry count.
- Determines whether all devices are readonly.
- Shows the balance dialog with the populated state.

The device list is later used for device filters and conversion availability.

## Elevated Callback Exports

The file exports three `extern "C"` `CALLBACK` functions intended for `rundll32.exe`:

- `StartBalanceW`
  - Parses `<volume> <hex-request>` from the command line.
  - Enables `SeManageVolumePrivilege`.
  - Opens the volume/path.
  - Calls `FSCTL_BTRFS_START_BALANCE`.
  - If start returns `STATUS_DEVICE_NOT_READY`, queries scrub status and reports a scrub-running message when applicable.
- `PauseBalanceW`
  - Enables `SeManageVolumePrivilege`.
  - Opens the volume/path.
  - Queries balance status.
  - Calls `FSCTL_BTRFS_RESUME_BALANCE` if paused, or `FSCTL_BTRFS_PAUSE_BALANCE` if running.
- `StopBalanceW`
  - Enables `SeManageVolumePrivilege`.
  - Opens the volume/path.
  - Queries balance status.
  - Calls `FSCTL_BTRFS_STOP_BALANCE` if running or paused.

All callbacks catch exceptions and display shell-extension error messages.

## Integration

This file integrates the shell extension resource IDs, localized string loading, Win32 dialog APIs, elevation via ShellExecute/rundll32, `NtFsControlFile`, and WinBtrfs private IOCTL structures from `btrfsioctl.h`.

## Notable Details

- The elevated command channel serializes raw request bytes as hex on the command line; no separate IPC channel is used.
- Options are intentionally non-editable once a balance is running; live queried options are shown instead.
- The conversion profile list is constrained by writable device count.
- `unserialize()` assumes hex-like input and does not reject invalid characters explicitly; command input is generated internally by `serialize()`.
- `StartBalance()` waits for the elevated process to exit, so the UI thread blocks during the privileged FSCTL dispatch, though the balance itself is a kernel operation.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/shellext/balance.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/shellext/balance.h -->
# File Research: sources/windows/winbtrfs/src/shellext/balance.h

## Purpose

`balance.h` declares the `BtrfsBalance` shell-extension class used to display and control WinBtrfs balance operations.

## Public Interface

- `BtrfsBalance(const wstring& drive, bool RemoveDevice = false, bool ShrinkDevice = false)`
  - Stores the target drive/path.
  - Records whether the dialog was opened from remove-device or shrink-device workflows.
  - Initializes `devices` to `nullptr` and `removing` to false.
- `void ShowBalance(HWND hwndDlg)`
  - Entry point that gathers device information and opens the main balance dialog.
- `INT_PTR CALLBACK BalanceDlgProc(...)`
  - Instance dialog procedure for the main balance dialog.
- `INT_PTR CALLBACK BalanceOptsDlgProc(...)`
  - Instance dialog procedure for the per-category options dialog.

## Private Methods

The class privately owns helpers for:

- `ShowBalanceOptions()` - opens the option dialog for data, metadata, or system balance options.
- `SaveBalanceOpts()` - reads dialog controls into `btrfs_balance_opts`.
- `StartBalance()` - launches elevated start operation.
- `RefreshBalanceDlg()` - queries current balance status and updates UI.
- `PauseBalance()` - launches elevated pause/resume operation.
- `StopBalance()` - launches elevated stop operation.

## State Fields

The class stores:

- `balance_status`
- three option structures: `data_opts`, `metadata_opts`, `system_opts`
- active option category `opts_type`
- latest queried balance state `bqb`
- state booleans: `cancelling`, `removing`, `shrinking`, `readonly`
- target path `fn`
- device list pointer `devices`
- constructor context flags `called_from_RemoveDevice` and `called_from_ShrinkDevice`

## Integration

The header depends on Windows types and WinBtrfs IOCTL structures from `../btrfsioctl.h`. Implementation lives in `balance.cpp`, with static dialog thunks forwarding Win32 dialog messages into these instance methods.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/shellext/balance.h -->