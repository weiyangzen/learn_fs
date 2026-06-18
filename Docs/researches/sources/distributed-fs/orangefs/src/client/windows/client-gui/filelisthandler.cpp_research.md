# sources/distributed-fs/orangefs/src/client/windows/client-gui/filelisthandler.cpp

## Purpose
This C++ file implements the wxWidgets list-control helper used by the OrangeFS Windows GUI to display remote file listings and optional columns for size, permissions, and modification time.

## Important APIs, types, and functions
- `FileListHandler::FileListHandler` creates a `wxPanel` and child `wxListCtrl` sized from the global `MAIN_FRAME`.
- `getPrefixString` formats `OrangeFS_size` values into bytes/KB/MB/GB/TB strings.
- `getPermString` converts `OrangeFS_attr.perms` and `objtype` into Unix-style mode text.
- `getTimeString` formats `OrangeFS_attr.mtime` with `ctime`.
- `FileListHandler::addColumn` inserts and populates columns from `MAIN_APP` file names/attributes.
- `FileListHandler::removeColumn` deletes a column and adjusts stored column indexes.
- `FileListHandler::getSyncStatus` is a TODO stub that always returns false.

## Control flow
The main frame constructs the singleton handler, then calls `addColumn("File Name")` during startup. View-menu handlers call `addColumn` or `removeColumn` for optional columns. `addColumn` inserts a wx column, records its id in a `map<wxString,int>`, populates data according to the column name, and resizes all columns evenly. `removeColumn` resolves the id from the map, deletes the wx column, erases the map entry, resizes remaining columns, and decrements hard-coded optional column ids that were to the right of the deleted column.

## State and persistence behavior
State is in-memory GUI state only: `syncPane`, `syncList`, `syncColumnIDs`, and `localStorePath`. It reads global `MAIN_APP`/`MAIN_FRAME` state but does not persist any changes to disk. The sync status path is unimplemented.

## Dependencies and integration points
It depends on wxWidgets list controls, OrangeFS client types exposed through `main-app.h`, and the globals defined in `main-app.cpp`. It is tightly coupled to fixed display column names and `MainApp` getters.

## Risks and edge cases
- The class inherits `wxListCtrl` but actually owns a separate `wxListCtrl`; this can confuse event routing and object lifetime.
- `removeColumn` reads `this->syncColumnIDs[name]` before checking existence, which inserts a default map entry for missing names.
- `getPrefixString` can index past the four-element prefix array for sizes above TB and prints unrounded floats.
- `ctime` includes a trailing newline, which can render oddly in list cells.
- The first-column population uses `InsertItem(this->syncColumnIDs["File Name"], ...)` as item index rather than column index; because the id is zero this works accidentally.
- Destructor manually deletes wx child windows that wxWidgets may already own through parent-child lifetime management.
- `getSyncStatus` always returns false, so the status bar never reports synced files.

## Test signals
Start the GUI with 0, 1, and many file entries; toggle all optional columns in different orders; remove a non-present column; inspect size formatting around 1024 boundaries and very large sizes; verify directory/symlink permissions display correctly; select rows and confirm sync status behavior once implemented.
