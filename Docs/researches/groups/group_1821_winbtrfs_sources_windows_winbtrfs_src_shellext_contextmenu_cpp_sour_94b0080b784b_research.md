# Group Research: group_1821_winbtrfs_sources_windows_winbtrfs_src_shellext_contextmenu_cpp_sour_94b0080b784b

Scope: `Docs/research_subset_a.md`, source tree `sources/windows/winbtrfs`.

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/shellext/contextmenu.cpp -->
# File Research: sources/windows/winbtrfs/src/shellext/contextmenu.cpp

Read status: complete, 1668 lines.

This file implements the WinBtrfs Explorer context-menu extension and the exported `ReflinkCopyW` rundll entry point. It exposes menu actions for creating subvolumes, creating snapshots, sending and receiving subvolumes through elevated helper UIs, and reflink-pasting clipboard file selections.

Key implementation points:
- `BtrfsContextMenu::Initialize` distinguishes selected-item context menus from directory-background menus. For selected files, it scans `CF_HDROP` paths and enables snapshot creation only for Btrfs subvolume roots, identified through `FSCTL_BTRFS_GET_FILE_IDS` with inode `0x100` and `top == false`.
- Directory-background initialization checks create-subdirectory permission and verifies the target is on Btrfs before enabling background commands.
- `QueryContextMenu` inserts localized menu entries. UAC-shield bitmaps are loaded through WIC and attached to elevated send/receive commands.
- `InvokeCommand` dispatches by verb or command id to snapshot creation, new subvolume creation, elevated send/receive GUI launches, or reflink paste.
- Snapshot and subvolume creation use WinBtrfs ioctls `FSCTL_BTRFS_CREATE_SNAPSHOT` and `FSCTL_BTRFS_CREATE_SUBVOL`, with collision-resistant default names.
- The reflink copy path checks source and destination are on the same volume before cloning.

The reflink implementation is the largest behavior in the file:
- `BtrfsContextMenu::reflink_copy` is used by Explorer clipboard paste and handles duplicate destination names.
- `reflink_copy2` is the command-line/rundll variant used by `ReflinkCopyW`.
- Subvolume roots are copied as Btrfs snapshots rather than cloned file trees.
- Special Btrfs inode types such as char/block devices, FIFO, and sockets are recreated via `FSCTL_BTRFS_MKNOD`.
- Regular files are cloned with `FSCTL_DUPLICATE_EXTENTS_TO_FILE` after matching EOF, sparse state, and integrity/checksum settings.
- Directories are recursively copied, excluding `.` and `..`.
- Reparse points are preserved with `FSCTL_GET_REPARSE_POINT` and `FSCTL_SET_REPARSE_POINT`.
- Alternate data streams and Btrfs xattrs are copied after file data/metadata.
- Inode flags and compression type are preserved through `FSCTL_BTRFS_SET_INODE_INFO`.
- On failure after destination creation, it attempts to delete the partial destination with `FileDispositionInformation`.

Important dependencies and integration:
- Uses shared helpers from `shellext.h` and `main.cpp`: `load_string`, `wstring_sprintf`, error classes, `command_line_to_args`, handle wrappers, and `module`.
- Uses WinBtrfs ioctl definitions from `../btrfsioctl.h`.
- Registered by `main.cpp` under `Directory\\Background` and `Folder` context-menu handlers.
- Instantiated by `Factory::CreateInstance` for `FactoryContextMenu`.

Risk and maintenance notes:
- Several paths use `MAX_PATH` buffers, so long-path behavior may be incomplete.
- `GetCommandString` rejects any `idCmd != 0` before later branches for id `1` and `2`, making help text/verbs for nonzero commands unreachable through that code path.
- The code relies on inode `0x100` for subvolume-root detection; an in-file FIXME notes this assumption.
- Many Btrfs control buffers are manually allocated and populated. Most are freed correctly, but this style is sensitive to early throws and length calculations.
- Alternate streams are cast to `uint16_t` size with a comment that Btrfs streams are expected below 64 KB; this assumption should stay documented if stream support changes.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/shellext/contextmenu.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/shellext/contextmenu.h -->
# File Research: sources/windows/winbtrfs/src/shellext/contextmenu.h

Read status: complete, 83 lines.

This header declares `BtrfsContextMenu`, the COM object implementing `IShellExtInit` and `IContextMenu` for WinBtrfs Explorer commands.

Key declarations:
- Constructor initializes the object as ignored until successful initialization, clears `STGMEDIUM` state, clears the UAC icon handle, disables snapshot permission, and increments global `objs_loaded`.
- Destructor releases clipboard/selection `STGMEDIUM` data when owned, deletes the generated UAC bitmap, and decrements `objs_loaded`.
- Implements COM lifetime methods `QueryInterface`, `AddRef`, and `Release`.
- Implements `Initialize`, `QueryContextMenu`, `InvokeCommand`, and `GetCommandString`.
- Private state records selected/background mode, target path, menu suppression, snapshot eligibility, and UAC icon bitmap.
- Private helpers are `reflink_copy` and `get_uac_icon`.

Integration:
- Implemented in `contextmenu.cpp`.
- Created by `Factory::CreateInstance` when the factory type is `FactoryContextMenu`.
- `objs_loaded` is shared with `DllCanUnloadNow` in `main.cpp`.

Risk and maintenance notes:
- Manual COM refcounting starts at zero and depends on factory `QueryInterface` returning the initial reference.
- `STGMEDIUM` ownership is tracked by `stgm_set`; future initialization paths must maintain it carefully to avoid leaks or double release.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/shellext/contextmenu.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/shellext/devices.cpp -->
# File Research: sources/windows/winbtrfs/src/shellext/devices.cpp

Read status: complete, 958 lines.

This file implements elevated device-management dialogs and rundll exports for adding, removing, and resizing devices in a Btrfs filesystem.

Main behavior:
- `find_devices` enumerates disks, volumes, and hidden volumes through SetupAPI device-interface GUIDs.
- It opens devices with NT APIs, collects length, disk/partition number, storage descriptor text, partition layout, mount points, and filesystem identity.
- Filesystem identity is detected by scanning superblock magic definitions from `fs_ident` in `devices.h`.
- Btrfs superblocks contribute filesystem UUID and device UUID for matching devices to mounted Btrfs filesystems.
- Btrfs pseudo-devices named like `\\Device\\Btrfs{...}` are ignored for add-device display.
- `BtrfsDeviceAdd::populate_device_tree` builds the device tree and groups partitions under disks when possible.
- Existing mounted Btrfs filesystems are queried via `IOCTL_BTRFS_QUERY_FILESYSTEMS` to identify multi-device state and drive letters.

Device operations:
- `BtrfsDeviceAdd::AddDevice` confirms destructive use of formatted devices, opens the selected raw device, optionally locks/dismounts/unlocks volumes, and calls `FSCTL_BTRFS_ADD_DEVICE`.
- `RemoveDeviceW` parses `volume|device_id`, enables `SeManageVolumePrivilege`, sends `FSCTL_BTRFS_REMOVE_DEVICE`, and launches a balance UI. It maps `STATUS_CANNOT_DELETE` to a RAID-specific message.
- `BtrfsDeviceResize::do_resize` sends `FSCTL_BTRFS_RESIZE`. If the driver returns `STATUS_MORE_PROCESSING_REQUIRED`, it opens the balance workflow for relocation.
- `ResizeDeviceW` parses `volume|device_id`, enables privilege, and shows the resize dialog.
- `AddDeviceW`, `RemoveDeviceW`, and `ResizeDeviceW` are exported C callbacks intended for elevated `rundll32.exe` invocation.

UI behavior:
- Uses themed dialogs, tree controls, and a slider for resize size in MiB units.
- Add-device OK is enabled only for valid targets: non-partitioned disks or volumes, excluding already multi-device Btrfs members.
- Resize dialog queries `FSCTL_BTRFS_GET_DEVICES` to find current and maximum size for the selected device.

Important dependencies and integration:
- Uses `mountmgr` wrapper from `mountmgr.cpp` to map device names to drive letters.
- Uses `BtrfsBalance` from `balance.h` for post-remove or post-resize relocation.
- Uses `../btrfs.h` and `../btrfsioctl.h` for superblock and ioctl structures.
- Uses shared `format_size`, `load_string`, `wstring_sprintf`, `error_message`, and privilege/error helpers from the shell extension support code.

Risk and maintenance notes:
- Raw device operations require `SeManageVolumePrivilege` and can be destructive. The confirmation for formatted devices is important.
- There appears to be a UUID comparison typo in device matching: it compares `device_list[i].dev_uuid` to itself rather than to the iterated `dev` UUID, so child-device matching may be too broad.
- `find_devices` returns early on the first `SetupDiEnumDeviceInterfaces` failure without destroying the device-info list in that branch.
- Several manual allocations and NT variable-size buffers require careful bounds handling.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/shellext/devices.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/shellext/devices.h -->
# File Research: sources/windows/winbtrfs/src/shellext/devices.h

Read status: complete, 156 lines.

This header defines data structures and classes for the Btrfs device add/resize dialogs.

Key declarations:
- `device` stores PnP path, friendly name, drive letter, detected filesystem type, disk and partition numbers, size, Btrfs filesystem/device UUIDs, and flags for ignore, multi-device, disk, and partition presence.
- `fs_identifier` describes filesystem magic probes by display name, magic bytes, magic length, byte offset inside a 4 KiB buffer, and KiB read offset.
- `fs_ident` is a static table of filesystem signatures compiled from libblkid information. It includes Btrfs magic `_BHRfS_M` at superblock offset 64 KiB plus many common filesystems.
- `BtrfsDeviceAdd` declares dialog, display, and add-device methods plus selected-device state.
- `BtrfsDeviceResize` declares dialog, display, and resize methods plus current device information and pending size.

Integration:
- Implemented in `devices.cpp`.
- Used by exported callbacks `AddDeviceW`, `RemoveDeviceW`, and `ResizeDeviceW`.
- Depends on `../btrfsioctl.h` for `BTRFS_UUID` and `btrfs_device`.

Risk and maintenance notes:
- The header defines `fs_ident` as `const static`, so each translation unit including it gets its own copy. Currently it appears only intended for `devices.cpp`.
- Filesystem detection is magic-based and suitable for warning/display, not a complete validator.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/shellext/devices.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/shellext/factory.cpp -->
# File Research: sources/windows/winbtrfs/src/shellext/factory.cpp

Read status: complete, 94 lines.

This file implements the COM class factory used by the shell extension DLL.

Key behavior:
- `Factory::QueryInterface` supports `IUnknown` and `IClassFactory`.
- `Factory::LockServer` returns `E_NOTIMPL`.
- `Factory::CreateInstance` rejects aggregation with `CLASS_E_NOAGGREGATION`.
- It creates a concrete COM object based on `Factory::type`:
  - `FactoryIconHandler` creates `BtrfsIconOverlay`.
  - `FactoryContextMenu` creates `BtrfsContextMenu`.
  - `FactoryPropSheet` creates `BtrfsPropSheet`.
  - `FactoryVolPropSheet` creates `BtrfsVolPropSheet`.
- For each type, it only creates the object if the requested interface is one of the supported shell interfaces.

Integration:
- Used by `DllGetClassObject` in `main.cpp`, which sets the factory type after allocation.
- Pulls in `iconoverlay.h`, `contextmenu.h`, `propsheet.h`, and `volpropsheet.h`.

Risk and maintenance notes:
- Objects are allocated with refcount zero and returned through their own `QueryInterface`, which supplies the initial reference.
- `LockServer` is unimplemented. Shell usage may tolerate this, but a full COM server implementation typically tracks server locks.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/shellext/factory.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/shellext/factory.h -->
# File Research: sources/windows/winbtrfs/src/shellext/factory.h

Read status: complete, 68 lines.

This header declares the COM `Factory` class and factory type enum.

Key declarations:
- `factory_type` identifies which shell extension object the factory should create.
- `Factory` implements `IClassFactory`.
- Constructor initializes refcount to zero, sets type to `FactoryUnknown`, and increments global `objs_loaded`.
- Destructor decrements `objs_loaded`.
- `AddRef` and `Release` use interlocked operations; `Release` deletes on zero.
- Public `type` is assigned by `DllGetClassObject`.

Integration:
- Implemented in `factory.cpp`.
- Used by `main.cpp` for all registered COM class IDs.
- Shares `objs_loaded` with all shell extension COM classes to support `DllCanUnloadNow`.

Risk and maintenance notes:
- Public mutable `type` is simple but requires callers to set it before use. `DllGetClassObject` does that immediately.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/shellext/factory.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/shellext/iconoverlay.cpp -->
# File Research: sources/windows/winbtrfs/src/shellext/iconoverlay.cpp

Read status: complete, 80 lines.

This file implements the shell icon overlay handler for Btrfs subvolume roots.

Key behavior:
- `BtrfsIconOverlay::QueryInterface` supports `IUnknown` and `IShellIconOverlayIdentifier`.
- `GetOverlayInfo` returns the current module path as the icon source, icon index `0`, and flags for icon file and index.
- `GetPriority` returns priority `0`.
- `IsMemberOf` opens the path without following reparse points and calls `FSCTL_BTRFS_GET_FILE_IDS`.
- A path is considered an overlay member when it is a Btrfs subvolume root: inode `0x100` and `top == false`.

Integration:
- Registered by `main.cpp` under `ShellIconOverlayIdentifiers\\WinBtrfs`.
- Created by `Factory::CreateInstance` for `FactoryIconHandler`.
- Uses `../btrfsioctl.h` for file-id ioctl structures.

Risk and maintenance notes:
- Like context-menu snapshot detection, it assumes subvolume root inode `0x100`.
- Priority `0` competes with other overlay handlers. Windows also limits active overlay handlers, so registration order can affect visibility.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/shellext/iconoverlay.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/shellext/iconoverlay.h -->
# File Research: sources/windows/winbtrfs/src/shellext/iconoverlay.h

Read status: complete, 60 lines.

This header declares `BtrfsIconOverlay`, the COM object implementing `IShellIconOverlayIdentifier`.

Key declarations:
- Constructor initializes refcount and increments `objs_loaded`.
- Destructor decrements `objs_loaded`.
- Implements `QueryInterface`, `AddRef`, `Release`, `GetOverlayInfo`, `GetPriority`, and `IsMemberOf`.
- Stores only a private interlocked refcount.

Integration:
- Implemented in `iconoverlay.cpp`.
- Instantiated through `FactoryIconHandler`.
- Registered by `main.cpp`.

Risk and maintenance notes:
- Manual COM lifetime pattern matches the other shell extension classes.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/shellext/iconoverlay.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/shellext/main.cpp -->
# File Research: sources/windows/winbtrfs/src/shellext/main.cpp

Read status: complete, 780 lines.

This file is the shell extension DLL core. It owns COM class IDs, DLL exports, registry registration, shared formatting/error helpers, command-line parsing, and simple rundll helpers for creating subvolumes and snapshots.

COM and DLL behavior:
- Defines CLSIDs for icon overlay, context menu, file property sheet, and volume property sheet.
- `DllCanUnloadNow` returns `S_OK` when global `objs_loaded` is zero.
- `DllGetClassObject` allocates `Factory`, assigns the requested factory type, and returns the requested factory interface.
- `DllRegisterServer` writes CLSID and shell-extension registry keys for icon overlay, context menus, file/folder property sheets, and drive property sheets.
- `DllUnregisterServer` removes those keys with an in-file recursive `reg_delete_tree` implementation.
- `DllInstall` delegates to register/unregister.
- `DllMain` stores the module handle on process attach.

Shared helpers:
- `set_dpi_aware` dynamically loads `SetProcessDpiAwareness` from `shcore.dll`.
- `format_size` produces localized byte and larger-unit strings with locale grouping.
- `load_string` loads string resources into `std::wstring`.
- `wstring_sprintf` formats wide strings with `_vsnwprintf`.
- `format_message` and `format_ntstatus` convert Win32 and NTSTATUS failures to text.
- UTF-8/UTF-16 conversion helpers support exception messages.
- `string_error`, `last_error`, and `ntstatus_error` wrap localized or system errors for use across the shell extension.
- `error_message` displays localized error message boxes.
- `command_line_to_args` wraps `CommandLineToArgvW`.

Rundll helper exports:
- `CreateSubvolW` parses command-line args and creates a Btrfs subvolume at the requested path using `FSCTL_BTRFS_CREATE_SUBVOL`.
- `CreateSnapshotW` parses source and destination arguments and creates a snapshot using `FSCTL_BTRFS_CREATE_SNAPSHOT`.

Integration:
- Central dependency for all files in this group through `shellext.h` declarations and global `module`.
- Registers the COM classes implemented by `factory.cpp`, `iconoverlay.cpp`, `contextmenu.cpp`, `propsheet.cpp`, and volume property-sheet code outside this group.

Risk and maintenance notes:
- Registry writes use `HKEY_CLASSES_ROOT` and `HKEY_LOCAL_MACHINE`, so registration requires appropriate privileges.
- The custom recursive registry delete is needed for older systems but must be treated carefully because it deletes whole subtrees.
- `wstring_sprintf` uses varargs and `_vsnwprintf`; format-string/resource mismatches can surface as runtime formatting errors.
- Some rundll helper creation paths silently return on failures instead of surfacing errors.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/shellext/main.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/shellext/mappings.cpp -->
# File Research: sources/windows/winbtrfs/src/shellext/mappings.cpp

Read status: complete, 338 lines.

This file implements a standalone mappings dialog for viewing WinBtrfs UID and GID registry mappings.

Key behavior:
- Reads UID mappings from `SYSTEM\\CurrentControlSet\\Services\\btrfs\\Mappings`.
- Reads GID mappings from `SYSTEM\\CurrentControlSet\\Services\\btrfs\\GroupMappings`.
- Registry value names are expected to be SID strings; values are `REG_DWORD` UID/GID numbers.
- Converts SID strings to `PSID` with `ConvertStringSidToSidW`.
- Resolves SIDs to domain/name display values using LSA policy lookup and `LsaLookupSids`.
- Displays mappings in a list view with a tab control switching between UID and GID mappings.
- Exported `MappingsTest` sets DPI awareness and opens the dialog.

Implementation structure:
- Uses small RAII deleters for LSA handles, LSA allocated pointers, registry keys, and local SID allocations.
- `mapping_entry` owns the SID, numeric value, resolved domain/name, and SID use.
- `populate_list` refreshes the list for the selected tab.
- `init_dialog` creates tabs and list columns, then populates the initial view.
- `MappingsDlgProc` handles init, OK/cancel, and tab selection changes.

Integration:
- Depends on shared `module`, `load_string`, `error_message`, and `set_dpi_aware`.
- Uses resource IDs for the dialog, tabs, and list column labels.
- Not tied to COM factory creation; it is an exported rundll-style utility entry.

Risk and maintenance notes:
- The registry open path throws if the mappings key does not exist. If absence is normal, the UI may need an empty-list path.
- Entries whose value type is not `REG_DWORD` are skipped.
- The code ignores unconvertible SID strings.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/shellext/mappings.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/shellext/mountmgr.cpp -->
# File Research: sources/windows/winbtrfs/src/shellext/mountmgr.cpp

Read status: complete, 176 lines.

This file implements a small NT mount manager wrapper.

Key behavior:
- Constructor opens `MOUNTMGR_DEVICE_NAME` with `NtOpenFile` for generic read/write.
- Destructor closes the NT handle with `NtClose`.
- `create_point` builds `MOUNTMGR_CREATE_POINT_INPUT` and sends `IOCTL_MOUNTMGR_CREATE_POINT`.
- `delete_points` builds a `MOUNTMGR_MOUNT_POINT` filter from optional symlink, unique ID, and device name, then sends `IOCTL_MOUNTMGR_DELETE_POINTS`. It retries with the returned output size on `STATUS_BUFFER_OVERFLOW`.
- `query_points` builds the same filter structure and sends `IOCTL_MOUNTMGR_QUERY_POINTS`, resizes to the returned `MOUNTMGR_MOUNT_POINTS::Size`, retries, and converts results to `mountmgr_point` objects.

Integration:
- Used by `devices.cpp` to associate volumes/devices with DOS drive letters.
- Depends on shared `ntstatus_error` from shell extension support.

Risk and maintenance notes:
- `delete_points` and `query_points` duplicate filter-buffer construction logic.
- Offsets and lengths are manually calculated in bytes. Any future addition of fields should preserve Windows structure alignment expectations.
- The `delete_points` signature accepts `unique_id` as `wstring_view`, while `mountmgr_point::unique_id` stores raw bytes as `std::string`; unique IDs may not always be UTF-16 text.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/shellext/mountmgr.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/shellext/mountmgr.h -->
# File Research: sources/windows/winbtrfs/src/shellext/mountmgr.h

Read status: complete, 29 lines.

This header declares the mount manager wrapper and result type.

Key declarations:
- `mountmgr_point` stores a symbolic link, device name, and raw unique ID.
- `mountmgr` owns a mount manager handle and exposes `create_point`, `delete_points`, and `query_points`.
- `query_points` returns a `std::vector<mountmgr_point>`.

Integration:
- Implemented in `mountmgr.cpp`.
- Used by device enumeration logic in `devices.cpp`.

Risk and maintenance notes:
- The class owns a raw `HANDLE` rather than a reusable RAII handle wrapper. Copying is not explicitly disabled, so accidental copies would double-close; current code uses stack instances without copying.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/shellext/mountmgr.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/shellext/propsheet.cpp -->
# File Research: sources/windows/winbtrfs/src/shellext/propsheet.cpp

Read status: complete, 1384 lines.

This file implements the WinBtrfs file/folder property sheet page and the exported standalone `ShowPropSheetW` dialog.

Main responsibilities:
- Adds a property page for Btrfs-selected files and folders.
- Reads Btrfs inode metadata using `FSCTL_BTRFS_GET_INODE_INFO`.
- Displays subvolume ID, inode ID, inode type, size-on-disk, compression ratio, fragmentation, inode flags, compression type, POSIX mode bits, uid, gid, and subvolume read-only state.
- Supports multi-selection by tracking min/max mode, flags, compression type, uid/gid, inode, type, and subvolume values.
- Walks selected directories asynchronously to update aggregate size/compression/fragmentation metrics.

Initialization and data loading:
- `Initialize` accepts only selected-item shell data, reads `CF_HDROP`, calls `load_file_list`, and starts a background search thread if directories need recursive accounting.
- `set_cmdline` provides equivalent initialization for elevated standalone use through `ShowPropSheetW`.
- `check_file` opens each file with `MAXIMUM_ALLOWED`, determines access rights, reads inode info, tracks whether admin relaunch is useful, and accumulates size/allocation/compression metadata.
- `do_search` recursively scans directories using `FindFirstFileW` and opens child files to accumulate Btrfs extent metrics.
- `search_list_thread` drains queued directories and sets `thread` to null when done.

Property editing:
- `change_inode_flag` edits Btrfs inode flags and enforces UI rules around `NODATACOW`, `NODATASUM`, and compression.
- `change_perm_flag`, `change_uid`, and `change_gid` track POSIX metadata edits.
- `apply_changes_file` reopens each target with required permissions and applies:
  - Btrfs inode flags,
  - POSIX mode,
  - uid and gid,
  - compression type,
  - subvolume read-only Windows attribute for subvolume roots.
- `apply_changes` applies pending edits to either the standalone filename or all shell-selected files.
- `open_as_admin` relaunches `ShowPropSheet` through elevated `rundll32.exe`, then reloads state.

UI behavior:
- `init_propsheet` populates controls, tri-state checkboxes for mixed selections, compression-type combo entries, permission bits, uid/gid fields, and optional admin button.
- `set_size_on_disk` formats total on-disk size, compression ratio, and fragmentation ratio. It is called periodically while the background thread is active.
- `SizeDetailsDlgProc` shows per-compression-class size details and refreshes while scanning is still active.
- `PropSheetDlgProc` handles control edits, apply notifications, size-detail links, and timer refreshes.
- `AddPages` creates the Explorer property sheet page and increments the COM object reference if accepted by Explorer.
- `ShowPropSheetW` creates a standalone one-page property sheet for elevated/admin editing.

Integration:
- Declared in `propsheet.h`.
- Created by `Factory::CreateInstance` for `FactoryPropSheet`.
- Registered by `main.cpp` under file and folder property sheet handlers.
- Uses shared helpers from `main.cpp` and Btrfs ioctl structures from `../btrfsioctl.h`.

Risk and maintenance notes:
- The background directory scan updates shared counters and `search_list` without visible synchronization while the UI thread reads them. This can race.
- Destructor does not wait for `thread`; lifetime safety depends on the property sheet staying alive until the scan ends.
- `change_inode_flag` and `change_perm_flag` set `flags_set = ~flag` or `mode_set = ~flag` for indeterminate state, which overwrites the whole mask rather than clearing one bit. This looks suspicious for mixed-selection editing.
- Several selected-file paths use `MAX_PATH`.
- Admin relaunch loops over selected files one at a time and blocks waiting for each elevated process.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/shellext/propsheet.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/winbtrfs/src/shellext/propsheet.h -->
# File Research: sources/windows/winbtrfs/src/shellext/propsheet.h

Read status: complete, 192 lines.

This header declares the Btrfs property sheet COM class and supporting POSIX/Btrfs flag constants.

Key declarations:
- Defines POSIX permission and special mode bits if not already available.
- Defines Btrfs inode flag constants used by the property page, including nodatasum, nodatacow, readonly, nocompress, prealloc, sync, immutable, append, nodump, noatime, dirsync, and compress.
- `BtrfsPropSheet` implements `IShellExtInit` and `IShellPropSheetExt`.
- Constructor initializes COM lifetime state, edit flags, access flags, background scan state, aggregate size counters, sector size, format buffers, and display state.
- Destructor releases selection `STGMEDIUM` if owned and decrements `objs_loaded`.
- Public methods include COM methods plus UI/edit helpers used by dialog procedures.
- Public state is intentionally exposed for dialog procedures, including readonly/access state, size format buffers, scan thread handle, mode/flag masks, inode identifiers, uid/gid, compression state, and mixed-selection flags.
- Private state includes refcount, selection data, edit-change booleans, aggregate size counters, directory search queue, standalone filename, sector size, and file-loading/apply helpers.

Integration:
- Implemented in `propsheet.cpp`.
- Instantiated by `Factory::CreateInstance`.
- Registered by `main.cpp` for `Folder` and `*` property sheet handlers.
- Shares `objs_loaded` for COM unload tracking.

Risk and maintenance notes:
- Many fields are public to simplify dialog callbacks. This keeps code direct but makes invariants harder to enforce.
- Background thread handle and shared aggregate fields are exposed without synchronization primitives.
- Copying is not disabled. COM objects are heap-managed and not copied in current code.
<!-- END FILE RESEARCH: sources/windows/winbtrfs/src/shellext/propsheet.h -->