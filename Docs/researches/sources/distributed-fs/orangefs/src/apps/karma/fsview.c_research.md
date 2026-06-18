# sources/distributed-fs/orangefs/src/apps/karma/fsview.c

## Purpose
`fsview.c` implements the modal file-system selection dialog for Karma. It displays the configured filesystems discovered by `comm.c` and lets the user switch the active monitored filesystem.

## Important APIs, Types, and Functions
The public entry point is `gui_fsview_popup()`. It creates a `GtkTreeView`, defines columns for mount point, contact server, filesystem name, and fsid, binds the view to global `gui_comm_fslist`, sets browse-only selection, and packs the view into a GTK dialog. `gui_fsview_response()` handles OK/CANCEL/close responses; on OK, it extracts `GUI_FSLIST_SERVER`, `GUI_FSLIST_FSNAME`, and `GUI_FSLIST_FSID` from the selected row and calls `gui_comm_set_active_fs()`.

## Control Flow
The dialog is opened from the File menu. It does not create its own data model; it views the shared list store. On successful selection, active filesystem switching happens before the dialog is destroyed. CANCEL simply destroys the dialog.

## State and Persistence
No persistent state is written. Runtime state consists of transient dialog widgets and a reference to the shared `gui_comm_fslist`. The active filesystem state is changed indirectly in `comm.c`.

## Dependencies and Integration Points
This file depends on GTK2, `main_window`, `gui_comm_fslist`, `GUI_FSLIST_*` enum values, and `gui_comm_set_active_fs()`. It is integrated through `menu.c` via the "Select file system" menu action.

## Risks and Edge Cases
The code assumes `gui_comm_fslist` has already been initialized. No default row is explicitly selected, so pressing OK with no selection is a no-op. The fsid is stored as `G_TYPE_INT`, which can be unsafe if `PVFS_fs_id` exceeds `gint` width on some platforms. Dialog content is added directly to the dialog vbox without a scrolled window, which may be awkward with many filesystems.

## Test Signals
Open the dialog with zero, one, and many configured filesystems. Verify OK with selected rows calls `gui_comm_set_active_fs()` with the displayed values. Test CANCEL and window close. Include fsid range/type checks if platform definitions change.
