# sources/distributed-fs/openafs/src/WINNT/client_exp/PropFile.cpp

Purpose: implements the Explorer property page for AFS file metadata, symlink/mountpoint details, cache flushing, and Unix mode bits.

Important APIs/functions: `CPropFile::PropPageProc`, `ShowUnixMode`, `EnableUnixMode`, and `MakeUnixModeString`.

Control flow: initialization handles empty selection, multi-selection, or single item. For a single item it chooses type text from mountpoint/symlink/directory/file flags, shows remove/edit controls as appropriate, loads mode bits, file ID, owner, group, mountpoint/symlink target info, and cell name. Apply serializes checkbox state and calls `SetUnixModeBits`. Button handlers flush files, remove symlink/mountpoint after confirmation, edit mountpoint/symlink using dedicated dialogs, or mark the property sheet changed for mode-bit edits.

State/persistence: pending Unix mode changes live in checkbox state until apply. Persistent effects occur through `SetUnixModeBits`, `Flush`, `RemoveSymlink`, `RemoveMount`, and make/edit dialogs.

Dependencies/integration: relies on `gui2fs` operations, message helpers, mountpoint/symlink dialogs, MFC property sheet notifications, and `TaLocale`.

Risks: the `IDC_EDIT` case falls through to permission-control cases after launching an edit dialog, which may mark the page changed unintentionally. `m_volName` is passed to mountpoint edit but not set in this file. Multi-select still records cell from first item only.

Test signals: file/dir/mountpoint/symlink UI variants, apply mode changes, flush, remove with cancel/confirm, edit flows, multi-select behavior, and fall-through regression around `IDC_EDIT`.
