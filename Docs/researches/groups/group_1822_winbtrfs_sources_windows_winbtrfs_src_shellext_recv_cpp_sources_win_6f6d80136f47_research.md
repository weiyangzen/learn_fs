# Group Research: group_1822_winbtrfs_sources_windows_winbtrfs_src_shellext_recv_cpp_sources_win_6f6d80136f47

Scope: `Docs/research_subset_a.md`, source tree `sources/windows/winbtrfs`.

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/shellext/recv.cpp -->
# File Research: sources/windows/winbtrfs/src/shellext/recv.cpp

## Purpose
Implements WinBtrfs receive support for Btrfs send streams. It provides both GUI and command-line `rundll32` entry points that replay a send stream into a target directory by creating or snapshotting subvolumes, applying filesystem mutations, validating command checksums, and finalizing the received subvolume through WinBtrfs private FSCTLs.

## Main Components
- `BtrfsRecv::Open`: stores the stream path and destination path, chooses GUI progress dialog or quiet mode, and enables hardware CRC32C on x86/x64 when SSE4.2 is available.
- `BtrfsRecv::recv_thread`: opens the send-stream file and destination directory, loops over one or more send streams in the file, and updates dialog state.
- `BtrfsRecv::do_recv`: core stream interpreter. Reads `btrfs_send_header`, validates magic/version, reads each `btrfs_send_command`, verifies CRC32C, dispatches supported send commands, detects truncation, handles cancellation, and calls `FSCTL_BTRFS_RECEIVED_SUBVOL` at completion.
- Command handlers:
  - `cmd_subvol`, `cmd_snapshot`: create the received root with `FSCTL_BTRFS_CREATE_SUBVOL` or `FSCTL_BTRFS_CREATE_SNAPSHOT`, reserve it with `FSCTL_BTRFS_RESERVE_SUBVOL`, open working handles, and cache UUID/transid to path mappings.
  - `cmd_mkfile`: handles regular files, dirs, special nodes, FIFOs, sockets, and symlinks. Symlinks are created as Win32 reparse points and then have POSIX mode set.
  - `cmd_rename`, `cmd_link`, `cmd_unlink`, `cmd_rmdir`: replay namespace changes through Win32 file APIs.
  - `cmd_setxattr`, `cmd_removexattr`: maps most `user.*` xattrs to NTFS alternate data streams, while special xattrs such as `security.NTACL`, `user.DOSATTRIB`, `user.reparse`, and `user.EA` go through `FSCTL_BTRFS_SET_XATTR`.
  - `cmd_write`, `cmd_clone`, `cmd_truncate`: write file data, duplicate extents from clone sources with `FSCTL_DUPLICATE_EXTENTS_TO_FILE`, and resize files.
  - `cmd_chmod`, `cmd_chown`, `cmd_utimes`: apply mode/ownership/timestamps through WinBtrfs inode info FSCTLs or NT file information.
- Exported callbacks:
  - `RecvSubvolGUIW`: GUI entry point; prompts for a send-stream file and receives into the command-line destination.
  - `RecvSubvolW`: quiet command-line entry point; parses stream and destination from command line.

## Data Flow
1. Entry point enables required privileges: `SeManageVolumePrivilege`, `SeSecurityPrivilege`, and `SeRestorePrivilege`.
2. Stream file is opened read-only and destination directory is opened with create permissions.
3. Each stream command’s TLV payload is parsed with `find_tlv`.
4. The command is replayed relative to the current received subvolume path.
5. On success, the received subvolume UUID/generation are committed with `FSCTL_BTRFS_RECEIVED_SUBVOL`.
6. On error, any partially created received subvolume path is made writable and recursively deleted.

## Important Dependencies
- `shellext.h`: Win32/NT prototypes, RAII handles, errors, encoding helpers.
- `recv.h`: class state and declarations.
- `resource.h`: localized error/status IDs.
- `../btrfs.h`, `../btrfsioctl.h`: send-stream structures, Btrfs types, WinBtrfs FSCTL codes.
- `../crc32c.h`: software/hardware CRC32C dispatch.

## Notable Behaviors and Edge Cases
- Stream validation checks magic, version `<= 1`, per-command CRC32C, and payload length against file size.
- `BTRFS_SEND_CMD_UPDATE_EXTENT` is accepted but intentionally ignored.
- Consecutive writes to the same file reuse `lastwritefile`; readonly attributes are temporarily cleared and restored.
- Clone sources are resolved first from an in-memory UUID/transid cache, then via `FSCTL_BTRFS_FIND_SUBVOL`.
- GUI cancellation sets `cancelling`; partial output cleanup still occurs through the common exception path only for thrown failures, while the loop itself exits gracefully when cancellation is noticed.
- Several manually allocated FSCTL request buffers are not consistently freed after successful use, so this file has small process-lifetime leak potential during receive operations.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/shellext/recv.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/shellext/recv.h -->
# File Research: sources/windows/winbtrfs/src/shellext/recv.h

## Purpose
Declares the receive-side shell extension class and helper cache structure used by `recv.cpp`.

## Main Components
- `subvol_cache`: stores a received or discovered subvolume identity:
  - `BTRFS_UUID uuid`
  - `uint64_t transid`
  - `wstring path`
- `BtrfsRecv`: stateful receive controller for GUI and quiet operation.

## Public Interface
- Constructor initializes all handles to invalid/null states, clears paths/cache, and sets counters/flags.
- Destructor clears the clone/subvolume cache.
- `Open(HWND hwnd, const wstring& file, const wstring& path, bool quiet)`: launches receive.
- `recv_thread()`: worker implementation used by GUI thread wrapper or quiet mode.
- `RecvProgressDlgProc(...)`: progress dialog message handler.

## Private Interface
Declares command handlers for all supported Btrfs send stream operations: subvolume, snapshot, create, rename, link, unlink, rmdir, xattr, write, clone, truncate, chmod, chown, and utimes. Also declares TLV lookup, cache insertion, and core `do_recv`.

## State
Tracks stream path, destination path, current subvolume path, active directory/master/write handles, progress dialog handle, received count, current subvolume UUID/transid, cancellation/running flags, and UUID/transid-to-path cache.

## Dependencies
Includes `<shlobj.h>` and `../btrfs.h`; relies on `win_handle` from `shellext.h` in method signatures even though the header itself is normally included after or with `shellext.h`.

## Notable Behavior
The class owns operational state across the entire receive session. It is not designed for concurrent receive operations in the same instance.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/shellext/recv.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/shellext/resource.h -->
# File Research: sources/windows/winbtrfs/src/shellext/resource.h

## Purpose
Central numeric resource ID registry for the WinBtrfs shell extension. It is generated-style Visual C++ resource metadata consumed by `shellbtrfs.rc.in` and C++ code.

## Main Contents
- Icon and dialog IDs:
  - `IDI_ICON1`
  - inode property dialogs: `IDD_PROP_SHEET`, `IDD_SIZE_DETAILS`
  - volume dialogs: `IDD_VOL_PROP_SHEET`, `IDD_VOL_USAGE`
  - balance/device/scrub dialogs: `IDD_BALANCE_OPTIONS`, `IDD_BALANCE`, `IDD_DEVICES`, `IDD_DEVICE_ADD`, `IDD_SCRUB`, `IDD_DEVICE_STATS`
  - send/receive dialogs: `IDD_RECV_PROGRESS`, `IDD_SEND_SUBVOL`
  - resize/drive-letter/mapping dialogs: `IDD_RESIZE`, `IDD_DRIVE_LETTER`, `IDD_MAPPINGS`
- String IDs for:
  - subvolume creation/snapshot menu labels and help.
  - inode type and size formatting.
  - volume usage and RAID/profile labels.
  - balance, scrub, device, resize, and drive-letter messages.
  - receive/send stream status and error text.
  - registry, mount manager, reflink, and mapping errors.
- Control IDs:
  - inode property controls such as `IDC_UID`, `IDC_GID`, permission checkboxes, compression flags.
  - usage/balance/device/scrub controls.
  - receive progress controls `IDC_RECV_PROGRESS`, `IDC_RECV_MSG`.
  - send controls `IDC_STREAM_DEST`, `IDC_PARENT_SUBVOL`, `IDC_CLONE_LIST`.
  - drive-letter and mapping controls.

## Dependencies
Used directly by all shell extension `.cpp` files in this group through `MAKEINTRESOURCEW`, `load_string`, `GetDlgItem`, and message dispatch.

## Notable Behaviors
- Some numeric IDs are intentionally reused for different dialogs, which is normal for Win32 resources because controls are scoped by dialog template.
- The file is generated-style and should be edited carefully, preferably through the resource script or Visual Studio resource tooling when maintaining numeric consistency.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/shellext/resource.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/shellext/scrub.cpp -->
# File Research: sources/windows/winbtrfs/src/shellext/scrub.cpp

## Purpose
Implements the WinBtrfs scrub UI and command callbacks. It queries scrub status, starts/pauses/resumes/stops scrub operations through driver FSCTLs, and displays scrub progress plus detailed recovered/unrecoverable error reports.

## Main Components
- `format_duration`: locale-aware wrapper around `GetDurationFormatEx`.
- `BtrfsScrub::UpdateTextBox`: builds the multiline status/error text from `btrfs_query_scrub`, fetching a larger scrub report buffer when errors exist.
- `BtrfsScrub::RefreshScrubDlg`: queries current scrub state with `FSCTL_BTRFS_QUERY_SCRUB`, updates buttons, progress bar, status text, and error text.
- `StartScrub`: issues `FSCTL_BTRFS_START_SCRUB`; if the driver reports not-ready, checks balance status to report the clearer “balance running” error.
- `PauseScrub`: queries status and sends either `FSCTL_BTRFS_RESUME_SCRUB` or `FSCTL_BTRFS_PAUSE_SCRUB`.
- `StopScrub`: sends `FSCTL_BTRFS_STOP_SCRUB`.
- `ScrubDlgProc`: dialog procedure with startup refresh, 1-second timer refresh, and button handling.
- Exported callbacks:
  - `ShowScrubW`: elevated GUI dialog entry point.
  - `StartScrubW`: quiet start entry point.
  - `StopScrubW`: quiet stop entry point.

## Data Flow
1. The target volume path is stored in `BtrfsScrub::fn`.
2. Each refresh opens the path with `FILE_TRAVERSE` and backup/reparse flags.
3. Scrub status is queried from the driver.
4. UI controls are updated based on `BTRFS_SCRUB_STOPPED`, `BTRFS_SCRUB_RUNNING`, or `BTRFS_SCRUB_PAUSED`.
5. Error entries are walked using their `next_entry` offsets and formatted as parity, metadata, or data errors.

## Important Dependencies
- `shellext.h`: errors, formatting helpers, handles.
- `scrub.h`: class declaration.
- `resource.h`: dialog and string IDs.
- `../btrfsioctl.h`: scrub and balance FSCTL structures/codes.
- Win32 UI APIs, Common Controls progress bars, locale/date/time formatting.

## Notable Behaviors and Edge Cases
- `UpdateTextBox` only allocates the larger report buffer when `num_errors > 0`; otherwise it formats the initial query result.
- Scrub error summaries count recovered versus unrecovered errors while walking the returned linked buffer.
- The progress percentage divides by `total_chunks`; the code assumes the driver provides a nonzero total while scrub is active.
- Quiet `StartScrubW` and `StopScrubW` intentionally ignore most errors after privilege or open failures, matching fire-and-forget command behavior.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/shellext/scrub.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/shellext/scrub.h -->
# File Research: sources/windows/winbtrfs/src/shellext/scrub.h

## Purpose
Declares the `BtrfsScrub` dialog/controller class used by `scrub.cpp`.

## Main Components
- Constructor stores the target drive/path in `fn`.
- Public `ScrubDlgProc` handles dialog messages.
- Private helpers refresh state, render scrub text, and start/pause/stop scrub.

## State
- `wstring fn`: target volume/path.
- `uint32_t status`: last known scrub status.
- `uint64_t chunks_left`: last known remaining chunk count.
- `uint32_t num_errors`: last known error count.

## Dependencies
Includes Windows APIs plus `../btrfs.h` and `../btrfsioctl.h`.

## Notable Behavior
The class caches prior status/chunk/error values so dialog refreshes can avoid unnecessary text and control updates.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/shellext/scrub.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/shellext/send.cpp -->
# File Research: sources/windows/winbtrfs/src/shellext/send.cpp

## Purpose
Implements Btrfs send-stream export for WinBtrfs subvolumes. It provides a GUI dialog and quiet command-line entry point that ask the driver to generate a send stream, then write a Btrfs send header, driver-provided command buffer data, and final END command to a destination file.

## Main Components
- `BtrfsSend::Thread`: GUI worker thread for stream generation.
  - Opens the source subvolume.
  - Builds `btrfs_send_subvol` with optional parent and clone handles.
  - Starts send with `FSCTL_BTRFS_SEND_SUBVOL`.
  - Writes `btrfs_send_header`.
  - Repeatedly reads send data with `FSCTL_BTRFS_READ_SEND_BUFFER`.
  - Appends a fixed checksum END command.
  - Deletes partial destination file on failure.
- `StartSend`: validates dialog input, disables controls, collects clone listbox entries, starts worker thread.
- `Browse`: save-file picker for destination stream.
- `BrowseParent`, `AddClone`: folder pickers rooted at the same volume as the source subvolume; validate selected folders are Btrfs subvolumes using `FSCTL_BTRFS_GET_FILE_IDS`.
- `RemoveClone`: removes selected clone source from the listbox.
- `SendDlgProc`: dialog procedure for write/cancel/browse/incremental/clone controls.
- `SendSubvolGUIW`: elevated GUI entry point.
- `send_subvol`: non-GUI stream writer used by quiet mode.
- `SendSubvolW`: quiet command-line entry point; parses `-p parent`, repeated `-c clone`, source subvolume, and output file.

## Data Flow
1. Entry point enables `SeManageVolumePrivilege`.
2. Source subvolume and optional parent/clone subvolumes are opened read-only for attributes.
3. Driver send is initialized with `FSCTL_BTRFS_SEND_SUBVOL`.
4. Output file receives the send header, all generated command chunks, and an END command.
5. On failure after output open, the output file is marked for deletion.

## Important Dependencies
- `shellext.h`: NT FSCTL declarations, errors, helpers.
- `send.h`: class state and declarations.
- `resource.h`: dialog/control/string IDs.
- `../btrfs.h`, `../btrfsioctl.h`: send stream and FSCTL definitions.
- Shell folder browser APIs for parent/clone selection.

## Notable Behaviors and Edge Cases
- If `FSCTL_BTRFS_SEND_SUBVOL` returns invalid parameter, GUI mode checks whether source and parent subvolumes are readonly and reports specific errors.
- GUI cancel uses `TerminateThread`, then closes active handles and deletes a partial stream if possible. This is abrupt and can bypass normal worker cleanup.
- Quiet `send_subvol` has less detailed error reporting and does not perform the same readonly-specific diagnostics.
- The END command checksum is hard-coded as `0x9dc96c50`, matching the zero-length Btrfs send END command.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/shellext/send.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/shellext/send.h -->
# File Research: sources/windows/winbtrfs/src/shellext/send.h

## Purpose
Declares the `BtrfsSend` GUI/controller class for exporting Btrfs send streams.

## Main Components
- Constructor initializes send state, destination buffer, handles, source path, and incremental flag.
- Destructor frees the heap send buffer if present.
- Public methods:
  - `Open(HWND hwnd, WCHAR* path)`: opens the send dialog for a source subvolume.
  - `SendDlgProc`: dialog message handler.
  - `Thread`: worker implementation.
- Private methods:
  - `StartSend`, `Browse`, `BrowseParent`, `AddClone`, `RemoveClone`.

## State
- `started`: whether a send is active.
- `incremental`: whether a parent subvolume is required.
- `file[MAX_PATH]`: destination stream path.
- `closetext[255]`: original Cancel/Close button text.
- `dirh`, `stream`, `thread`: active handles.
- `hwnd`: owning dialog.
- `subvol`: source subvolume path.
- `buf`: send buffer allocated in worker.
- `clones`: selected clone source paths.

## Dependencies
Includes `../btrfs.h`; requires declarations from `shellext.h` and Win32 headers in implementation context.

## Notable Behavior
The class is stateful and dialog-oriented. It keeps live handles as members so cancellation can close/delete the active operation from the UI thread.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/shellext/send.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/shellext/shellbtrfs.rc.in -->
# File Research: sources/windows/winbtrfs/src/shellext/shellbtrfs.rc.in

## Purpose
CMake-templated Windows resource script for `shellbtrfs.dll`. It defines the shell extension icon, version metadata, dialog layouts, manifest, and English UK localized strings.

## Main Resource Areas
- Includes `resource.h` from the configured CMake source directory.
- Icon:
  - `IDI_ICON1` uses `subvol.ico`.
- Version block:
  - Uses `@PROJECT_VERSION_MAJOR@`, `@PROJECT_VERSION_MINOR@`, and `@PROJECT_VERSION_PATCH@`.
  - Identifies product as WinBtrfs and original filename as `shellbtrfs.dll`.
- Dialog templates:
  - `IDD_PROP_SHEET`: inode properties, POSIX permissions, flags, compression, subvolume readonly, admin open.
  - `IDD_SIZE_DETAILS`: inline/uncompressed/ZLIB/LZO/Zstd size details.
  - `IDD_VOL_PROP_SHEET`: volume UUID plus usage, balance, devices, scrub, and drive-letter actions.
  - `IDD_VOL_USAGE`: multiline usage report with refresh.
  - `IDD_BALANCE_OPTIONS`, `IDD_BALANCE`: balance filters/options/status controls.
  - `IDD_DEVICES`, `IDD_DEVICE_ADD`, `IDD_DEVICE_STATS`: device list, add tree, stats/reset.
  - `IDD_SCRUB`: scrub progress/status/info controls.
  - `IDD_RECV_PROGRESS`: receive progress dialog.
  - `IDD_SEND_SUBVOL`: send stream destination, incremental parent, clone list controls.
  - `IDD_RESIZE`: device resize slider/status.
  - `IDD_DRIVE_LETTER`: drive-letter combo dialog.
  - `IDD_MAPPINGS`: UID/GID mapping list tabs.
- Manifest:
  - Embeds `shellbtrfs.manifest`.
- String tables:
  - User-facing menu/help text.
  - Inode type and size strings.
  - Usage/profile/RAID labels.
  - Balance, device, scrub, send, receive, resize, mount manager, and mapping messages/errors.

## Important Dependencies
- `resource.h` numeric IDs must match the dialogs and strings defined here.
- C++ files call `load_string(module, IDS_...)` for these localized messages.
- Dialog procedures rely on the control IDs and layouts defined here.

## Notable Behaviors
- The file is source-templated rather than raw `.rc`; CMake substitutes paths and version fields.
- Dialogs use classic Win32 resource templates and fixed dialog units.
- This file is the localization source for many detailed error messages emitted by the send/receive/scrub/volume property code.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/shellext/shellbtrfs.rc.in -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/shellext/shellext.h -->
# File Research: sources/windows/winbtrfs/src/shellext/shellext.h

## Purpose
Shared shell extension header providing Windows target definitions, NT API declarations, fallback structure definitions, Btrfs constants, RAII handle wrappers, and common helper/error declarations.

## Main Contents
- Windows target setup:
  - `WINVER` and `_WIN32_WINNT` set to Windows 10.
  - `ISOLATION_AWARE_ENABLED`, `STRSAFE_NO_DEPRECATE`.
- NTSTATUS constants used across shell extension code, including success, buffer overflow, EOF, not ready, cannot delete, and not found.
- Btrfs block/profile flags:
  - data/system/metadata and RAID profile flags including RAID1C3/RAID1C4.
- Btrfs inode type constants used by shell operations.
- `funcname` macro mapped to compiler-specific function name macro.
- NT native declarations:
  - `NtReadFile`, `NtSetEaFile`, `NtSetSecurityObject`, `NtFsControlFile`, `NtQueryInformationFile`, `NtSetInformationFile`, `NtQueryVolumeInformationFile`.
- Compatibility definitions for non-MSVC builds:
  - `DUPLICATE_EXTENTS_DATA`
  - integrity information buffers
- `REPARSE_DATA_BUFFER` definition and `SYMLINK_FLAG_RELATIVE`.

## Utility Classes
- `win_handle`: RAII wrapper using `CloseHandle`.
- `fff_handle`: RAII wrapper using `FindClose`.
- `nt_handle`: RAII wrapper using `NtClose`.
- `string_error`, `last_error`, `ntstatus_error`: exception types carrying formatted messages.
- `global_lock`: RAII wrapper around `GlobalLock`/`GlobalUnlock`.

## Shared Helpers Declared
- `format_size`
- `set_dpi_aware`
- `format_message`
- `format_ntstatus`
- `load_string`
- `wstring_sprintf`
- `command_line_to_args`
- `utf8_to_utf16`
- `error_message`

## Dependencies
Includes Windows/NT headers, C++ strings/vectors/stdint, and WinBtrfs headers `../btrfs.h` and `../btrfsioctl.h`.

## Notable Behavior
This header is the compatibility and convenience layer that lets the shell extension call lower-level NT APIs and WinBtrfs private FSCTLs while keeping most implementation files concise.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/shellext/shellext.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/shellext/volpropsheet.cpp -->
# File Research: sources/windows/winbtrfs/src/shellext/volpropsheet.cpp

## Purpose
Implements the Btrfs volume property sheet for Explorer. It exposes volume UUID, usage reporting, balance, devices, scrub, device stats reset, device add/remove/resize launchers, and drive-letter changes.

## Main Components
- COM integration:
  - `BtrfsVolPropSheet::QueryInterface`
  - `Initialize`: accepts a single Explorer-selected path, opens it, verifies WinBtrfs by querying devices, queries UUID, and creates `BtrfsBalance`.
  - `AddPages`: registers `IDD_VOL_PROP_SHEET` as a property page.
  - `ReplacePage`: no-op success.
- Usage reporting:
  - `FormatUsage`: converts `btrfs_usage` and `btrfs_device` buffers into text similar to Linux `btrfs fi usage`, including device totals, allocated/unallocated space, data/metadata ratios, profile sections, and per-device allocations.
  - `RefreshUsage`, `UsageDlgProc`, `ShowUsage`.
- Device management display:
  - `RefreshDevList`: queries devices and usage, populates a list view with ID, description, readonly, size, allocated, and allocation percent.
  - `DeviceDlgProc`: handles refresh, add/remove/resize launchers, stats dialog, and selection-sensitive button state.
  - `ShowDevices`.
- Device stats:
  - `StatsDlgProc`: displays per-device write/read/flush/corruption/generation stats.
  - `ResetStats`: launches elevated `rundll32` `ResetStats` action and refreshes device data.
  - Exported `ResetStatsW`: parses `volume|devid`, enables privilege, and sends `FSCTL_BTRFS_RESET_STATS`.
- Privileged action launchers:
  - `ShowScrub`: runs elevated `ShowScrub`.
  - `ShowChangeDriveLetter`: runs elevated `ShowChangeDriveLetter`.
  - Device add/remove/resize are also launched through elevated `rundll32.exe` commands.
- Main property dialog:
  - `PropSheetDlgProc`: initializes UUID display, readonly state, shield icons, and routes button clicks to usage/balance/devices/scrub/drive-letter actions.
- Drive-letter change:
  - `BtrfsChangeDriveLetter`: lists unused drive letters with mount manager queries, deletes the old DOS device symlink, creates the new one, and attempts rollback on failure.
  - Exported `ShowChangeDriveLetterW`.

## Data Flow
1. Explorer passes the selected item through `IDataObject`/`CF_HDROP`.
2. The selected path is opened with backup/reparse flags.
3. WinBtrfs driver FSCTLs provide devices, UUID, and usage.
4. Dialog actions either open local modal dialogs or spawn elevated `rundll32.exe shellbtrfs.dll,<Action> ...` helpers.
5. Device mutations and stats reset are followed by device list refreshes.

## Important Dependencies
- `shellext.h`: Win32/NT helpers, errors, RAII handles.
- `volpropsheet.h`: class declarations.
- `balance.h`, `scrub.h`: related volume operations.
- `mountmgr.h`: drive-letter mount point manipulation.
- `resource.h`: dialog/control/string IDs.
- WinBtrfs FSCTLs: `GET_DEVICES`, `GET_UUID`, `GET_USAGE`, `RESET_STATS`.

## Notable Behaviors and Edge Cases
- Device/usage buffers grow in 1024-byte increments up to eight retries on `STATUS_BUFFER_OVERFLOW`.
- `devices` is reused as class state; several refresh paths replace it and free old data.
- `FormatUsage` assumes metadata allocation totals are nonzero when computing metadata ratio.
- Device IDs are displayed as strings and later parsed with `_wtoi`, which truncates to integer width and may be fragile for very large `uint64_t` device IDs.
- Elevated commands concatenate paths and IDs into `rundll32` parameters; paths containing command separators used internally, especially `|`, could be problematic.
- Drive-letter change only supports root drive paths of the form `X:\`.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/shellext/volpropsheet.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/shellext/volpropsheet.h -->
# File Research: sources/windows/winbtrfs/src/shellext/volpropsheet.h

## Purpose
Declares the Explorer volume property sheet COM class and drive-letter dialog helper.

## Main Components
- `BtrfsVolPropSheet`: implements `IShellExtInit` and `IShellPropSheetExt`.
  - Constructor initializes COM refcount-related state, increments global loaded object count, and clears device/balance state.
  - Destructor releases storage medium, frees device buffer, decrements global loaded object count, and deletes balance helper.
  - Implements `QueryInterface`, `AddRef`, `Release`, `Initialize`, `AddPages`, and `ReplacePage`.
  - Declares methods for usage, device list, scrub, drive-letter, device stats, and stats reset workflows.
- Public state used by dialogs:
  - `btrfs_device* devices`
  - `bool readonly`
  - `BtrfsBalance* balance`
  - `BTRFS_UUID uuid`
  - `bool uuid_set`
- Private state:
  - COM reference count.
  - `ignore` flag determining whether to add the page.
  - Explorer `STGMEDIUM`.
  - selected path `fn`.
  - active stats device ID.
- `BtrfsChangeDriveLetter`: helper for the drive-letter modal dialog.
  - Stores parent window, target volume path, and available letters.
  - Provides `show`, `DlgProc`, and private `do_change`.

## Dependencies
Includes Shell interfaces, WinBtrfs ioctl/header files, and related shell extension headers `balance.h` and `scrub.h`.

## Notable Behavior
`BtrfsVolPropSheet` is a COM object with manual reference counting and global DLL lifetime integration through `objs_loaded`. Dialog procedures access the object through `GWLP_USERDATA` and operate directly on its shared state.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/shellext/volpropsheet.h -->