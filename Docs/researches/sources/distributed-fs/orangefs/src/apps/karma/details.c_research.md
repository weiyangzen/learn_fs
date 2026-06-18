# sources/distributed-fs/orangefs/src/apps/karma/details.c

## Purpose
`details.c` implements Karma's server details table. It presents per-server management statistics in a sortable GTK tree view, including server address, RAM, uptime, handles, space, and server type. The same generic table builder is reused by the status-page server popup.

## Important APIs, Types, and Functions
The public setup/update functions are `gui_details_setup()`, `gui_details_update()`, `gui_details_view_new()`, and `gui_details_view_fill()`. Static state stores the main details list/view and column objects. `gui_details_view_new()` creates a `GtkListStore` with columns aligned to the `GUI_DETAILS_*` enum in `karma.h`, creates `GtkTreeViewColumn` objects, and optionally attaches custom sort functions. `gui_details_view_fill()` computes unit divisors from max values, updates column titles with units, detaches the model, clears/refills rows, and reattaches it. `gui_details_view_insert()` formats one `PVFS_mgmt_server_stat`. Sort helpers compare numeric strings via `strtod()` and text via `strcmp()`.

## Control Flow
The details page is created once during notebook construction. Every status timer tick calls `gui_details_update()`, which delegates to `gui_details_view_fill()` for all servers. Status double-click popups call `gui_details_view_new()` and `gui_details_view_fill()` with a one-element server index list.

## State and Persistence
State is in GTK widgets/models and static initialization flags. No persistent storage is used. The model is rebuilt on each update rather than incrementally patched, which keeps logic simple but discards selection/scroll position.

## Dependencies and Integration Points
The file depends on GTK2, `struct PVFS_mgmt_server_stat`, unit helpers from `units.c`, enum layout from `karma.h`, and status popup code from `status.c`. Its column names must stay aligned with `GUI_DETAILS_*` enum values, as the comment warns.

## Risks and Edge Cases
`gtk_list_store_new()` is called with a fixed column type list that assumes memory-usage columns are enabled; if `__KARMA_DISABLE_MEM_USAGE__` changes the enum count, this area needs careful compile/runtime verification. Numeric formatting uses 12-byte buffers per field; very large formatted values may truncate. The function assumes `s_stat_ct > 0` in practice but does not assert before max scans. Rebuilding the model every refresh can be expensive for large server counts. Sorting numeric display strings is unit-normalized per refresh, so sort behavior is only meaningful within the current unit scale.

## Test Signals
Feed synthetic server stats with varying RAM/space/handle maxima and verify column unit labels and row values. Test sortable columns for numeric order. Compile and run with and without `__KARMA_DISABLE_MEM_USAGE__`. Exercise details updates with zero, one, and many servers and status popup rendering for selected server indices.
