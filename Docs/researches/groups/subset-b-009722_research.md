# Research Group subset-b-009722

This grouped report covers NFS-Ganesha administration, statistics, configuration, CI, hook, epoch, and container helper scripts under `sources/user-network-fs/nfs-ganesha/src/scripts`. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/QtUI/__init__.py -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/QtUI/__init__.py

## Purpose

This package initializer declares the Qt UI submodules exported by `Ganesha.QtUI`. It is part of the Python package installed for the `ganeshactl` graphical administration tools and makes the generated UI modules and table/dialog model modules discoverable through package imports.

## Important APIs, Types, and Functions

The only runtime API is `__all__`, listing `exports_table`, `clients_table`, `ui_log_dialog`, `log_settings`, and `ui_main_window`.

## Control Flow

Importing the package executes no logic beyond binding `__all__`. Consumers import concrete modules directly, such as `Ganesha.QtUI.exports_table.ExportTableModel` or generated `Ui_MainWindow`.

## State and Persistence Behavior

There is no mutable state and no persistence. Package state is limited to module metadata.

## Dependencies and Integration Points

The file integrates with `setup.py.in`, which packages `Ganesha.QtUI`, and with `ganeshactl.py`, which imports generated Qt UI classes and table models from this package.

## Risks and Edge Cases

`__all__` includes generated modules (`ui_log_dialog`, `ui_main_window`) that must be produced during the build from `.ui` files. Missing generated Python UI files will break imports even though this initializer itself succeeds.

## Test Signals

Import smoke tests for `Ganesha.QtUI` and each listed submodule validate package installation and UI generation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/QtUI/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/QtUI/clients_table.py -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/QtUI/clients_table.py

## Purpose

`clients_table.py` implements the Qt table model used by the GUI Clients tab. It adapts `ClientMgr.ShowClients` DBus replies into displayable rows with protocol availability columns and last-stat-update time.

## Important APIs, Types, and Functions

`ClientTableModel(QAbstractTableModel)` exposes `FetchClients`, `FetchClients_done`, Qt model methods (`setData`, `insertRows`, `removeRows`, `rowCount`, `columnCount`, `headerData`, `flags`, `data`), and stores rows in `self.clients`. Headers cover client IP, NFSv3, MNT, NLMv4, RQUOTA, NFSv4.0, NFSv4.1, 9P, and last update.

## Control Flow

Construction stores the DBus manager, subscribes to `clientmgr.show_clients`, and initializes an empty row list. `FetchClients` calls `ClientMgr.ShowClients`; the asynchronous DBus wrapper later emits `show_clients`, invoking `FetchClients_done`. The handler resizes the table if the client count changed, then formats booleans as `yes`/`no`, timestamp tuples through `time.ctime`, and all other cells as strings before calling `setData`.

## State and Persistence Behavior

All state is in memory: `self.clients` holds the rendered cell strings and `self.ts` is initialized but not updated. The model does not persist client data and does not mutate server state.

## Dependencies and Integration Points

It depends on PyQt5 core/table model classes and `QColor`, and on a manager object compatible with `Ganesha.client_mgr.ClientMgr`. It is used by `ganeshactl.py` as the model for `ui.clients`.

## Risks and Edge Cases

The code uses Python 2/PyQt4 idioms (`xrange`, `self.emit(SIGNAL(...))`, `QVariant`) while the scripts are Python 3/PyQt5, so the model is likely to fail at runtime without compatibility shims. The alignment branch checks column `9`, but the header has 9 columns indexed `0..8`, so the last-update column is not aligned as intended. The namedtuple currently includes NFSv4.2 in the manager, while this UI header omits it, so protocol data can be shifted or truncated if row lengths differ from the model column count.

## Test Signals

Useful tests instantiate the model with a fake manager signal, emit client rows of varying lengths, verify row insertion/removal, and check display roles for booleans, timestamps, colors, and alignment. A PyQt5 import/runtime smoke test is important because this file mixes old and new Qt APIs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/QtUI/clients_table.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/QtUI/exports_table.py -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/QtUI/exports_table.py

## Purpose

`exports_table.py` implements the Qt table model used by the GUI Exports tab. It transforms export-manager DBus data into a read-only table of export IDs, paths, protocol availability flags, and last statistics update time.

## Important APIs, Types, and Functions

`ExportTableModel(QAbstractTableModel)` owns `self.exports` and implements `FetchExports`, `FetchExports_done`, `setData`, row insertion/removal, `rowCount`, `columnCount`, `headerData`, `flags`, and `data`. Header columns are export ID, export path, NFSv3, MNT, NLMv4, RQUOTA, NFSv4.0, NFSv4.1, 9P, and last update.

## Control Flow

Construction subscribes to `exportmgr.show_exports`. `FetchExports` calls `ShowExports`; when the asynchronous wrapper emits results, `FetchExports_done` adjusts the row count, formats boolean and timestamp cells, and updates cell data. `data` services Qt display, alignment, background, and foreground roles.

## State and Persistence Behavior

The model stores only rendered table rows in memory. It has no persistence and does not perform server-side changes.

## Dependencies and Integration Points

It depends on PyQt5 and on `Ganesha.export_mgr.ExportMgr`. `ganeshactl.py` sets an instance as the model for the generated `exports` `QTableView`.

## Risks and Edge Cases

The source uses `xrange`, `QVariant`, and old signal emission patterns under a Python 3/PyQt5 shebang ecosystem. The manager's `Export` tuple includes NFSv4.2, but the table header does not; if all tuple elements are iterated, the model may address a column beyond `columnCount`. `setData` indexes `self.exports[row]` before checking bounds, so malformed indexes can raise before returning `False`.

## Test Signals

Fake-manager tests should emit empty, single-row, and resized export lists; assert row-count changes; and validate formatting of ID/path/protocol/time columns. GUI smoke tests should run under the exact PyQt5 version used by packages.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/QtUI/exports_table.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/QtUI/log_settings.py -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/QtUI/log_settings.py

## Purpose

`log_settings.py` implements the GUI log-settings dialog. It presents Ganesha log components in an editable table and pushes changed levels back over DBus.

## Important APIs, Types, and Functions

`DebugLevelDelegate` creates a combo-box editor containing log levels from `log_levels_t`. `LogSettingsModel` fetches component levels through `LogManager.GetAll`, stores `[component, level]` rows, exposes editable column 1, and calls `LogManager.Set` after edits. `LogSetDialog` wires the generated `Ui_LogSettings` dialog, the model, the delegate, and the Done button.

## Control Flow

The dialog constructs a table model and delegate, installs them on `log_levels`, fetches current components, then connects the model's `dataChanged` signal to `updateSetting`. `getComponents_done` sorts returned component names and populates rows without calling `setData`, avoiding accidental writeback. User edits in the level column flow through `DebugLevelDelegate.setModelData`, then `LogSettingsModel.setData`, then `updateSetting`, which calls `Set` and refreshes all components.

## State and Persistence Behavior

Dialog state is transient in `self.log_components`. Persistent effects are remote: edits change live Ganesha DBus log properties. The dialog itself only hides on Done and remains reusable.

## Dependencies and Integration Points

It depends on PyQt5 and generated `Ganesha.QtUI.ui_log_dialog.Ui_LogSettings`. It integrates with `Ganesha.log_mgr.LogManager` in the GUI process and with the server's `org.ganesha.nfsd.log.component` DBus property interface.

## Risks and Edge Cases

The file imports widgets from `QtGui` even though many moved to `QtWidgets` in PyQt5. It uses `xrange`, `QVariant`, and `index.data(...).toString()`, which are PyQt4-era idioms. `removeRows` references `self.log_comp_levels`, a nonexistent attribute, and computes the removal range as `count + count - 1`; removal paths can fail. Any edit immediately writes to the daemon, so validation of level names depends on the combo-box list and DBus backend.

## Test Signals

Tests should use a fake log manager emitting component dictionaries, verify sorted row population, simulate delegate edits, and assert `Set(component, level)` plus refresh calls. Import/UI smoke tests under PyQt5 are high value because several widget APIs are version-sensitive.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/QtUI/log_settings.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/QtUI/ui_log_dialog.ui -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/QtUI/ui_log_dialog.ui

## Purpose

This Qt Designer file defines the Log Settings dialog consumed by `log_settings.py`. It provides the visual container for editing component log levels.

## Important APIs, Types, and Functions

The UI class is `LogSettings`. It contains a `QTableView` named `log_levels` and a `QPushButton` named `log_done`. These object names are the integration API used by generated Python code and `LogSetDialog`.

## Control Flow

At build time, the `.ui` is converted into a Python `Ui_LogSettings` class. At runtime, `LogSetDialog.setupUi` creates the table and button; application code installs the table model/delegate and connects `log_done.clicked` to hide the dialog.

## State and Persistence Behavior

The file describes widget geometry and static text only. It has no data persistence. Server-side log state is handled by `LogSettingsModel`.

## Dependencies and Integration Points

It depends on Qt 4/5 UI compiler compatibility. It is referenced by the generated `Ganesha.QtUI.ui_log_dialog` module and `Ganesha.QtUI.log_settings`.

## Risks and Edge Cases

The layout uses fixed geometry for the button and an intermediate `verticalLayoutWidget`; resizing behavior may be weaker than a fully layout-managed dialog. If the generated Python class name or object names change, `LogSetDialog` will break.

## Test Signals

Build tests should confirm UI code generation. GUI smoke tests should instantiate `Ui_LogSettings`, find `log_levels` and `log_done`, and resize the dialog to verify usable layout.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/QtUI/ui_log_dialog.ui -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/QtUI/ui_main_window.ui -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/QtUI/ui_main_window.ui

## Purpose

This Qt Designer file defines the main NFS-Ganesha GUI window used by `ganeshactl.py`. It provides tabs for exports and clients plus menu actions for DBus connection, administration, logging, views, and help.

## Important APIs, Types, and Functions

The generated class is `Ui_MainWindow`. Important named widgets/actions are `exports`, `clients`, `tabWidget`, `actionDBus_connect`, `actionQuit`, `actionAdd_Client`, `actionRemove_Client`, `actionExports`, `actionLog_Settings`, `actionReset_Grace`, `actionShutdown`, `actionReload`, `actionStatistics`, `actionViewExports`, `actionViewClients`, and `actionAbout`.

## Control Flow

At build time the UI is compiled to Python. At runtime `MainWindow.setupUi` creates the central tab widget, table views, menus, actions, and status bar. `ganeshactl.py` connects action signals to DBus wrapper methods and installs `ExportTableModel` and `ClientTableModel` on the table views.

## State and Persistence Behavior

The UI file contains only static widget configuration. Runtime state lives in table models and DBus wrappers. No persistence is represented here.

## Dependencies and Integration Points

It depends on Qt UI tooling and generated Python packaging. It is tightly coupled to object names expected by `ganeshactl.py`.

## Risks and Edge Cases

The UI still contains some actions that are placeholders or unused, such as `actionLog_Levels`. The scroll-area nesting around table views is more complex than necessary and can affect resizing. Menu/action naming is part of the code contract, so designer edits require matching Python changes.

## Test Signals

Tests should instantiate the generated UI, verify all action/widget names used by `ganeshactl.py` exist, and smoke-test table model installation and resize behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/QtUI/ui_main_window.ui -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/__init__.py -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/__init__.py

## Purpose

This package initializer defines the public `Ganesha` Python management package used by both GUI and command-line administration tools.

## Important APIs, Types, and Functions

The file exposes `admin`, `io_stats`, `export_mgr`, `client_mgr`, and `log_mgr` through `__all__`.

## Control Flow

Importing `Ganesha` performs no dynamic work beyond setting `__all__`; concrete behavior lives in the listed modules.

## State and Persistence Behavior

No runtime state or persistence is defined.

## Dependencies and Integration Points

`setup.py.in` packages `Ganesha`. GUI and wrapper scripts import modules from this package to reach PyQt DBus interfaces, table models, and stats types.

## Risks and Edge Cases

`__all__` does not list newer synchronous helper modules such as `ganesha_mgr_utils` and `glib_dbus_stats`, though they are still importable by full name. Listed `io_stats` is currently broken on import because its namedtuple field declarations are malformed and `Object` is undefined.

## Test Signals

Import smoke tests should cover `import Ganesha` and each named submodule to catch packaging and syntax/runtime import regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/admin.py -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/admin.py

## Purpose

`admin.py` implements the PyQt DBus client for the `org.ganesha.nfsd.admin` interface used by the GUI and older Qt command-line wrapper.

## Important APIs, Types, and Functions

`AdminInterface(QtDBus.QDBusAbstractInterface)` binds a service/path/connection to interface `org.ganesha.nfsd.admin`. It exposes `grace(ipaddr)`, `reload()`, `shutdown()`, and completion handler `admin_done(call)`.

## Control Flow

Each public method issues `asyncCall` to DBus and wraps the returned pending call in `QDBusPendingCallWatcher`. The watcher emits `finished`, invoking `admin_done`. The handler converts DBus errors into `show_status(False, ...)`; successful replies are expected as `(status, msg)` and are emitted through the supplied status signal.

## State and Persistence Behavior

The object keeps only the `show_status` signal reference and DBus interface metadata. Persistent effects are remote daemon actions: grace-period reset, config reload, or daemon shutdown.

## Dependencies and Integration Points

It depends on PyQt5 `QtDBus` and is used by `ganeshactl.py` and `ganesha-admin.py`. It expects the server to own `org.ganesha.nfsd` and expose `/org/ganesha/nfsd/admin`.

## Risks and Edge Cases

The reply conversion uses `argumentAt(...).toPyObject()`, which may not match modern PyQt5 DBus value APIs. There is no timeout, input validation, or argument-count validation. Shutdown and reload are privileged/high-impact operations gated only by the caller UI.

## Test Signals

Use a fake or test DBus service returning success/error tuples and assert emitted `show_status` values. GUI tests should verify grace/reload/shutdown action wiring and error reporting when Ganesha is down.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/admin.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/client_mgr.py -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/client_mgr.py

## Purpose

`client_mgr.py` provides PyQt DBus wrappers for NFS-Ganesha client management and client statistics interfaces.

## Important APIs, Types, and Functions

`Client` is a namedtuple for client IP, protocol availability flags, and last activity time. `ClientMgr(QDBusAbstractInterface)` emits `show_clients` and provides `AddClient`, `RemoveClient`, `ShowClients`, `clientmgr_done`, and `clientshow_done`. `ClientStats` wraps `org.ganesha.nfsd.clientstats` methods `GetNFSv3IO`, `GetNFSv40IO`, `GetNFSv41IO`, and `GetNFSv41Layouts`, though completion handlers are stubs.

## Control Flow

Add/remove/show requests are issued asynchronously over Qt DBus. Add/remove completions emit a status message. `clientshow_done` parses the returned timestamp and client array, converts Qt DBus variants into Python strings, booleans, and timestamp tuples, builds `Client` rows, and emits `show_clients(ts, clients)`.

## State and Persistence Behavior

The wrapper stores only DBus metadata and status signal. Add/remove calls mutate the daemon's runtime client allow/deny state through DBus; show calls are read-only.

## Dependencies and Integration Points

It depends on PyQt5 `QtCore` and `QtDBus`. It feeds `ClientTableModel`, `manage_clients.py`, and `ganeshactl.py`.

## Risks and Edge Cases

Parsing relies on positional DBus reply layouts and PyQt variant conversion methods such as `toULongLong`, `toString`, and `toPyObject`. `Client` includes `HasNFSv42`, while old table/printing code often omits that column. Statistics methods are incomplete because their callbacks are `pass`. There is no validation for IP address inputs or DBus reply arity.

## Test Signals

DBus fixture tests should cover add/remove errors, empty and populated `ShowClients`, NFSv4.2 presence, and malformed replies. Import/runtime tests under PyQt5 should verify conversion APIs still exist.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/client_mgr.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/config_editor.py -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/config_editor.py

## Purpose

`config_editor.py` implements a small parser and editor for NFS-Ganesha configuration blocks. It is used by `ganesha_conf.py` and `knfs2ganesha-exports.py` to set, get, and delete key/value pairs in nested config blocks.

## Important APIs, Types, and Functions

The pyparsing grammar defines `ppblock` as `BLOCKNAME { key=value;... subblocks... }`. `BLOCK` provides `set_keys`, `get_keys`, `del_keys`, and recursive helpers `set_process` and `del_process`. Utility functions include `r3_to_text`, validators for keys/values/block names, `next_subnames`, `block_match`, and `make_r3`. `ArgError` carries validation failures.

## Control Flow

Input text is scanned for blocks. A block descriptor such as `EXPORT Path /x CLIENT Clients *` is validated, then matched against parsed recursive three-element lists `[name, keypairs, subblocks]`. Setting finds or creates the target nested block and updates/appends key pairs. Getting formats all pairs or one requested key. Deleting removes requested keys, and can remove entire `EXPORT` or `CLIENT` blocks when identifying pairs are gone.

## State and Persistence Behavior

The parser/editor is pure over input strings and returns modified text. It does not write files directly. Formatting is regenerated for edited blocks using tab indentation, so comments and original formatting inside edited blocks are not preserved.

## Dependencies and Integration Points

It depends on `pyparsing`, `logging`, `pprint`, `re`, and `sys`. `ganesha_conf.py` handles file I/O and atomic replacement, while `knfs2ganesha-exports.py` shells out to `ganesha_conf` for generated export blocks.

## Risks and Edge Cases

The grammar requires all key/value pairs to precede sub-blocks, while comments note the daemon accepts more flexible ordering. Values cannot contain semicolons. `get_keys` uses `dict.has_key`, which is invalid in Python 3. Several paths call `sys.exit` inside library code, making composition and testing harder. Deletion checks `end_part[0]` without guarding empty suffixes. Reformatting edited blocks can drop comments and reorder whitespace.

## Test Signals

Parser tests should cover nested blocks, case-insensitive matching, `EXPORT`/`CLIENT` identifiers, set/get/delete of keys, whole-block removal, malformed keys/values, comments, and input where key pairs follow subblocks. Python 3 tests should specifically catch `has_key`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/config_editor.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/export_mgr.py -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/export_mgr.py

## Purpose

`export_mgr.py` provides PyQt DBus wrappers for export management and export statistics interfaces.

## Important APIs, Types, and Functions

`Export` is a namedtuple containing export ID/path, protocol availability flags, and last time. `ExportMgr(QDBusAbstractInterface)` exposes `AddExport`, `UpdateExport`, `RemoveExport`, `DisplayExport`, `ShowExports`, and completion handlers. It emits `show_exports` and `display_export`. `ExportStats` wraps `GetNFSv3IO`, `GetNFSv40IO`, `GetNFSv41IO`, and `GetNFSv41Layouts`, with stub handlers.

## Control Flow

Export operations use asynchronous Qt DBus calls. Add/update expect a returned message, remove expects success without payload, display emits ID/full path/pseudo/tag, and show parses a timestamp plus an export array into namedtuples before emitting `show_exports`.

## State and Persistence Behavior

The wrapper stores only interface metadata and status signal references. Add/update/remove mutate the daemon's live export configuration. Show/display are read-only.

## Dependencies and Integration Points

It depends on PyQt5 and feeds `ExportTableModel`, `manage_exports.py`, and `ganeshactl.py`. It expects DBus service `org.ganesha.nfsd`, path `/org/ganesha/nfsd/ExportMgr`, and interfaces `org.ganesha.nfsd.exportmgr`/`exportstats`.

## Risks and Edge Cases

Reply parsing is positional and tied to older Qt variant methods. The namedtuple has NFSv4.2, but table and older print code omit it. `DisplayExport` ignores client detail data in this Qt wrapper, unlike the synchronous helper. Stats callbacks are unimplemented. Export IDs are converted to `int` without range checks.

## Test Signals

Tests should simulate DBus replies for add/update/remove/display/show, including empty export lists and NFSv4.2 data. End-to-end tests with a running test Ganesha DBus service should verify live export changes and UI table updates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/export_mgr.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/ganesha_mgr_utils.py -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/ganesha_mgr_utils.py

## Purpose

`ganesha_mgr_utils.py` is the synchronous DBus utility layer behind the newer `ganesha_mgr.py` command-line tool. It wraps client, export, admin, cache, standard log, and conditional log DBus operations and normalizes results into status/message tuples and namedtuples.

## Important APIs, Types, and Functions

Namedtuples include `Client`, `Export`, `ExportClient`, `IDMapper`, `IDMapperGroup`, and `FileSys`. Classes are `ClientMgr`, `ExportMgr`, `AdminInterface`, `CacheMgr`, `LogManager`, and `CondLogManager`. `_log_component_prop_name` normalizes component names to `COMPONENT_*`.

## Control Flow

Each manager opens `dbus.SystemBus()`, obtains a daemon object, and stores the service/path/interface. Methods call `get_dbus_method`, catch `dbus.exceptions.DBusException`, and return `(False, ex, ...)` on failure. Show/list methods parse DBus arrays into namedtuples. Client/export protocol statistics are converted by JSON round-tripping DBus containers into Python data, then converting nested protocol pairs into dictionaries. Conditional log methods use the `org.ganesha.nfsd.log.conditional` interface for lists, match policy, and client/export enable/disable operations.

## State and Persistence Behavior

Manager instances keep DBus connection/object references. Persistent effects are remote daemon state changes: clients, exports, cache purges, malloc trim settings, log levels, conditional logging targets, and match policy. There is no local persistence.

## Dependencies and Integration Points

The module depends on `dbus`, `json`, `sys`, and `collections.namedtuple`. It is imported by `ganesha_mgr.py` and complements older PyQt wrappers. It uses Ganesha DBus paths `/org/ganesha/nfsd/ClientMgr`, `/ExportMgr`, `/admin`, and `/CacheMgr`.

## Risks and Edge Cases

Constructors catch all exceptions and call `sys.exit`, which prevents library-style error handling. JSON round-tripping assumes DBus values are serializable and can obscure type/range details. Many methods assume exact reply layouts. Conditional log list replies are interpreted as variable-length arrays ending in status and message; backend contract drift can misparse. Export IDs for conditional logging are cast to `dbus.UInt16`, so large IDs may fail or wrap depending on dbus behavior.

## Test Signals

Mock DBus object tests should cover success and `DBusException` for every manager method, protocol dictionaries with missing keys, conditional empty/non-empty lists, log component prefixing, and export ID conversion. Integration tests require a running Ganesha service exposing the expected DBus interfaces.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/ganesha_mgr_utils.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/glib_dbus_stats.py -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/glib_dbus_stats.py

## Purpose

`glib_dbus_stats.py` is the statistics retrieval and formatting library for `ganesha_stats.py`. It calls Ganesha export/client stats DBus methods and exposes text and JSON report objects for global, export, client, protocol, pNFS, FSAL, authentication, and detailed operation counters.

## Important APIs, Types, and Functions

Top-level helpers are `dbus_to_std`, `timestr`, and `report_key_value`. `Report` is the base for JSON-producing report classes. Retrieval classes are `RetrieveExportStats` and `RetrieveClientStats`. Report/parsing classes include `ClientStats`, `ProtocolsStats`, `Client`, `DelegStats`, `ClientIOops`, `ClientAllops`, `Export`, `ExportStats`, `ExportDetails`, `GlobalStats`, `InodeStats`, `FastStats`, `ExportIOv3Stats`, `ExportIOv4Stats`, `ExportIOv41Stats`, `ExportIOv42Stats`, `ExportIOMonStats`, `TotalStats`, `PNFSStats`, `StatsReset`, `StatsStatus`, `DumpFSALStats`, `StatsEnable`, `StatsDisable`, `DumpAuth`, `DumpFULLV3Stats`, and `DumpFULLV4Stats`.

## Control Flow

Retrieval objects bind the system bus and object paths, obtain DBus methods, and return report objects. Report construction stores raw reply tuples and often extracts timestamps/status fields. `Report.report` builds a status header and delegates to `fill_report`; `json` serializes that structure. Text output is implemented through `__str__` on each report. Multi-export commands first list exports and call per-export stats methods, then aggregate results keyed by export ID.

## State and Persistence Behavior

State is in-memory raw DBus replies plus parsed fields. Reset/enable/disable commands mutate daemon statistics counters or collection state remotely. Other commands are read-only.

## Dependencies and Integration Points

It depends on Python `dbus`, `time`, `json`, and `sys`. `ganesha_stats.py` selects report methods from this module. It integrates with `org.ganesha.nfsd.exportstats`, `org.ganesha.nfsd.exportmgr`, `org.ganesha.nfsd.clientstats`, and `org.ganesha.nfsd.clientmgr`.

## Risks and Edge Cases

The module has a large positional parsing surface and uses assertions for type assumptions; optimized Python can skip assertions. `Report._header` has an inner function parameter that is unused and references outer `result`. Some report classes do not call `Report.__init__` and/or do not implement JSON, which is why `ganesha_stats.py` excludes some commands. There are duplicate/fragile counter walks and several unused locals. Backend schema changes or unavailable stats can cause `IndexError`, `StopIteration`, or failed type assertions.

## Test Signals

Unit tests should feed representative DBus-like tuples for every report class and validate both `str()` and `json()` where supported. Integration tests should cover `ganesha_stats` commands against a daemon with stats enabled/disabled, empty exports/clients, and per-export all-export aggregation. Negative tests should include DBus failures and malformed reply shapes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/glib_dbus_stats.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/io_stats.py -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/io_stats.py

## Purpose

`io_stats.py` appears intended to define structured Python representations for basic I/O and pNFS layout statistics returned over DBus. It is an unfinished support module for GUI or wrapper stats handling.

## Important APIs, Types, and Functions

The intended namedtuples are `BasicIO`, `IOReply`, `Layout`, and `pNFSReply`. A placeholder class `IOstat` defines an empty `__init__`.

## Control Flow

There is no functional control flow. Importing the module attempts to create namedtuples and define `IOstat`; constructing `IOstat` does nothing.

## State and Persistence Behavior

No state is stored and no persistence exists.

## Dependencies and Integration Points

It depends on `collections.namedtuple`. `Ganesha.__init__` lists `io_stats` in `__all__`, but no researched caller in this subset uses it directly.

## Risks and Edge Cases

The namedtuple field lists contain unquoted names such as `requested` and `status`, so importing the module raises `NameError`. `IOstat` inherits from undefined `Object`, which would also fail. This module is not usable as written under Python 3.

## Test Signals

A simple `python3 -c 'import Ganesha.io_stats'` import test catches the current failure. Future tests should instantiate each stats tuple with representative counters once field names are corrected.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/io_stats.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/log_mgr.py -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/log_mgr.py

## Purpose

`log_mgr.py` implements the PyQt DBus wrapper for querying and changing Ganesha log component levels through the standard `org.freedesktop.DBus.Properties` interface.

## Important APIs, Types, and Functions

Constants are `ADMIN_OBJECT`, `PROP_INTERFACE`, and `LOGGER_PROPS`. `LogManager(QDBusAbstractInterface)` emits `show_components` and `show_level`; methods are `GetAll`, `GetAll_done`, `Get`, `Get_done`, `Set`, and `Set_done`.

## Control Flow

The wrapper binds to `/org/ganesha/nfsd/admin` using `org.freedesktop.DBus.Properties`. `GetAll` calls `GetAll(LOGGER_PROPS)`, unwraps a DBus map of component names to levels, and emits a Python dict. `Get` emits one level string. `Set` wraps the level in `QDBusVariant` and calls `Set(LOGGER_PROPS, prop, value)`, then emits status.

## State and Persistence Behavior

The object stores only DBus metadata and a status signal. `Set` mutates live server log level properties; no local persistence is maintained.

## Dependencies and Integration Points

It depends on PyQt5 `QtCore` and `QtDBus`. It is used by `LogSettingsModel`, `manage_logger.py`, and `ganeshactl.py`.

## Risks and Edge Cases

Like other Qt DBus wrappers, it uses older `toPyObject`/`toString` conversion patterns. `Set` passes plain strings through `QDBusVariant.setVariant`, which may not create the exact DBus variant type expected by all PyQt5 versions. Property names are not normalized with `COMPONENT_` here, unlike the synchronous helper.

## Test Signals

DBus fixture tests should validate `GetAll` map conversion, `Get` single-level conversion, successful `Set`, and error propagation. GUI tests should verify that editing the log-level table results in the expected DBus property call.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/Ganesha/log_mgr.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/client_stats_9pOps.py -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/client_stats_9pOps.py

## Purpose

This script prints nonzero 9P operation counters for a specific client IP address using the Ganesha client statistics DBus interface.

## Important APIs, Types, and Functions

There are no reusable functions. Top-level code binds `dbus.SystemBus`, gets `/org/ganesha/nfsd/ClientMgr`, resolves `Get9pOpStats` on `org.ganesha.nfsd.clientstats`, validates one positional `client_ipaddr`, iterates `OpNames`, and prints totals.

## Control Flow

After connecting to DBus, the script requires exactly one argument. For each hard-coded 9P op name, it calls `Get9pOpStats(client_ipaddr, opname)`. If the returned status is false it prints the error and stops; otherwise it prints the op name and total when `opstats[3][0]` is nonzero.

## State and Persistence Behavior

The script is read-only and stores no state. It observes live counters from the daemon.

## Dependencies and Integration Points

It depends on Python `dbus` and the Ganesha DBus clientstats interface. It is a standalone diagnostic utility.

## Risks and Edge Cases

The op-name list is hard-coded and must match server-side names. All DBus reply fields are positional. A broad exception around object lookup hides exact connection errors. It performs no IP address validation beyond accepting a string.

## Test Signals

Tests should mock `Get9pOpStats` for zero, nonzero, and error replies and verify printed output. Integration tests require a daemon with 9P stats enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/client_stats_9pOps.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/export_stats_9pOps.py -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/export_stats_9pOps.py

## Purpose

This script prints nonzero 9P operation counters for a specific export ID using the Ganesha export statistics DBus interface.

## Important APIs, Types, and Functions

Top-level code binds `dbus.SystemBus`, gets `/org/ganesha/nfsd/ExportMgr`, resolves `Get9pOpStats` on `org.ganesha.nfsd.exportstats`, validates a numeric export ID, and iterates the same `OpNames` tuple used by the client variant.

## Control Flow

The script exits unless exactly one numeric argument is supplied. It converts the argument to `dbus.UInt16`, calls `Get9pOpStats(export_id, opname)` for each operation, stops on a false status, and prints op totals for nonzero counters.

## State and Persistence Behavior

It is read-only and stores no local state.

## Dependencies and Integration Points

It depends on Python `dbus` and the Ganesha exportstats DBus interface. It is a standalone stats diagnostic.

## Risks and Edge Cases

`dbus.UInt16(sys.argv[1])` relies on dbus-python accepting a string input; explicit `int()` would be safer. Export IDs outside 16-bit range are not checked. The hard-coded op list and positional reply parsing can drift from the server.

## Test Signals

Mock tests should cover usage errors, DBus object lookup failure, zero/nonzero operation counters, false status responses, and export ID conversion boundaries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/export_stats_9pOps.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/fake_recall.py -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/fake_recall.py

## Purpose

`fake_recall.py` is a CBSIM test/diagnostic helper that asks the Ganesha callback simulator to trigger a fake delegation recall for a client ID.

## Important APIs, Types, and Functions

`usage()` prints expected syntax. `main()` parses arguments with `getopt`, connects to `/org/ganesha/nfsd/CBSIM`, prints introspection data, obtains `fake_recall` from `org.ganesha.nfsd.cbsim`, and calls it with `dbus.UInt64(clientid)`.

## Control Flow

The script expects one client identifier, then performs DBus object lookup and method invocation. `getopt.GetoptError` prints usage. The callback simulator response is printed directly.

## State and Persistence Behavior

The script persists nothing locally. It may trigger server-side callback simulator behavior and affect test client/delegation state.

## Dependencies and Integration Points

It depends on `dbus`, `getopt`, and a daemon exposing `org.ganesha.nfsd.cbsim` at `/org/ganesha/nfsd/CBSIM`.

## Risks and Edge Cases

Argument handling is flawed: `getopt.getopt` returns `(opts, args)`, so `clientid = args[0]` stores a list rather than the first remaining argument. Passing that to `dbus.UInt64` likely fails. There is no DBus exception handling around object lookup or method call.

## Test Signals

Argument parser tests should verify a numeric client ID reaches `dbus.UInt64`. DBus mock tests should cover introspection and fake recall success/failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/fake_recall.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/ganesha-admin.py -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/ganesha-admin.py

## Purpose

`ganesha-admin.py` is an older Qt event-loop command-line wrapper for Ganesha admin DBus operations: shutdown, reload, and grace.

## Important APIs, Types, and Functions

`ServerAdmin(QtCore.QObject)` owns an `AdminInterface`, exposes `shutdown`, `reload`, `grace`, and prints results in `status_message`. The main block creates a `QApplication`, installs `DBusQtMainLoop`, opens the system bus, dispatches based on `sys.argv[1]`, and runs the Qt event loop.

## Control Flow

Each command invokes an asynchronous `AdminInterface` method and prints an immediate action message. When the DBus reply arrives, `status_message` prints status/error text and exits the process.

## State and Persistence Behavior

No local persistence exists. Commands mutate remote daemon state through shutdown, reload, or grace-period calls.

## Dependencies and Integration Points

It depends on PyQt5, dbus-python's Qt mainloop integration, and `Ganesha.admin.AdminInterface`.

## Risks and Edge Cases

The script indexes `sys.argv[1]` and `sys.argv[2]` without length checks. It imports `QApplication` from `PyQt5.QtGui`, whereas PyQt5 normally provides it in `QtWidgets`. It has largely overlapping functionality with newer `ganesha_mgr.py`.

## Test Signals

CLI tests should cover missing/unknown commands and grace without IP. DBus mock tests should assert event-loop exit on successful and failed admin replies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/ganesha-admin.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/ganesha_conf.py -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/ganesha_conf.py

## Purpose

`ganesha_conf.py` is a command-line editor for `/etc/ganesha/ganesha.conf` or a file named by `CONFFILE`. It applies block/key operations using `Ganesha.config_editor.BLOCK`.

## Important APIs, Types, and Functions

`modify_file(filename, data)` writes replacement data atomically through a same-directory temporary file and preserves existing ownership/mode when possible. `get_blocks(args)` separates block descriptors from `--key value` or `--key` options. Top-level command handling supports `set`, `get`, and `del`.

## Control Flow

The script parses the opcode, extracts block names and key/value lists, constructs a `BLOCK`, reads the config file, then calls `set_keys`, `get_keys`, or `del_keys`. `get` exits with the retrieved value. `set` and `del` atomically replace the config file with modified text.

## State and Persistence Behavior

This script is a persistent file mutator. It writes to `/etc/ganesha/ganesha.conf` by default and uses `CONFFILE` for testing or generated conversions. Atomic rename protects against partial writes, and fsync is called on the temporary file.

## Dependencies and Integration Points

It depends on `Ganesha.config_editor`, `os`, `sys`, and standard file APIs. `knfs2ganesha-exports.py` drives it as an external command to build generated export configs.

## Risks and Edge Cases

`NamedTemporaryFile` opens in binary mode by default, but `modify_file` writes `str` data, which raises `TypeError` in Python 3 unless the data is bytes or the file is opened in text mode. It uses broad exception handling around stat/chown/chmod. It does not lock the target config file, so concurrent invocations can race. The parser limitations and `has_key` issue in `config_editor.py` affect this script.

## Test Signals

Tests should run with `CONFFILE` pointing to a temp file, cover set/get/del, verify atomic replacement preserves mode, and run under Python 3 to catch text/binary write behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/ganesha_conf.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/ganesha_logrotate_mgr.py -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/ganesha_logrotate_mgr.py

## Purpose

`ganesha_logrotate_mgr.py` manages logrotate configuration and crontab scheduling for Ganesha logs. It can enable, disable, list, change size/rotation settings, and set a custom crontab entry.

## Important APIs, Types, and Functions

Constants define config paths, default cron entry, default size/rotation, and FSAL-specific log paths. `LogRotateManager` provides `get_os_type`, `is_crontab_entry_present`, backup/restore, crontab add/remove, `list_config`, `generate_logrotate_config`, `update_logrotate_config`, `change_config`, `restart_cron_service`, `enable`, `disable`, and `set_crontab`. `show_help` and `main` implement the CLI.

## Control Flow

`main` selects an action from argv. Enabling backs up any existing config, writes a generated config for the selected FSAL log path, and appends a crontab line. Disabling removes cron entries and restores the backup. Changing requires the cron entry to exist, edits `size` and `rotate` lines, and restarts cron. Setting a crontab removes old entries, adds the new one, and forces logrotate.

## State and Persistence Behavior

The script persistently modifies `/etc/logrotate.d/ganesha`, `/etc/logrotate.d/ganesha.default`, user crontab, and cron service state. It may force log rotation immediately.

## Dependencies and Integration Points

It depends on `os`, `sys`, `subprocess`, `platform`, and `shutil`, plus system programs `crontab`, `logrotate`, and `systemctl`. It integrates with distro cron service names and expected Ganesha log paths.

## Risks and Edge Cases

Crontab edits use shell pipelines and broad grep filtering for `/etc/logrotate.d/ganesha`, which can remove unrelated entries containing that path. `set-crontab` accepts arbitrary text and uses shell execution. Writes are not atomic and require root permissions. `platform` is imported but unused. Restarting `cron`/`crond` may fail on non-systemd or differently named services.

## Test Signals

Use temp paths and monkeypatched subprocess calls to test enable/disable/list/change/set-crontab without touching the host. OS-detection tests should cover Ubuntu, RHEL, and other. Integration tests should verify generated logrotate syntax with `logrotate -d`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/ganesha_logrotate_mgr.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/ganesha_mgr.py -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/ganesha_mgr.py

## Purpose

`ganesha_mgr.py` is the main synchronous command-line administration tool for NFS-Ganesha. It wraps client/export management, admin operations, cache views/purges, standard log levels, and conditional logging controls.

## Important APIs, Types, and Functions

Wrapper classes are `ManageClients`, `ShowExports`, `ServerAdmin`, `ManageCache`, `ManageLogs`, and `ManageCondLogs`. Helper exits are `exit_try_help` and `exit_option_not_supported`. The main block defines a large usage string and dispatches commands: `add`, `remove`, `update`, `display`, `purge`, `show`, `grace`, `trim`, `set`, `get`, `getall`, `shutdown`, and `help`.

## Control Flow

At startup, the script constructs all manager wrappers, which open DBus connections. It then parses positional arguments and calls the selected wrapper method. Output is printed directly. Conditional logging commands route to `CondLogManager`; standard log commands route to `LogManager`; admin commands route to `AdminInterface`.

## State and Persistence Behavior

Local state is transient wrapper instances. Remote persistent/runtime effects include adding/removing clients and exports, changing log levels and conditional logging policy/targets, purging caches, toggling malloc trim, grace-period operations, and shutdown.

## Dependencies and Integration Points

It depends on `Ganesha.ganesha_mgr_utils`, Python `os`, `sys`, and `time`, and a live Ganesha DBus service. It supersedes several older single-purpose Qt command-line scripts.

## Risks and Edge Cases

Because all wrappers are constructed before command validation, even `help` requires a working DBus service. Argument parsing is manual and inconsistent. Destructive commands such as shutdown and export removal have no confirmation. A special guard detects likely shell expansion of `*` for conditional client removal, which is useful but narrow. Some print methods omit NFSv4.2 despite data classes containing it.

## Test Signals

CLI tests should cover every command branch, missing arguments, unknown options, conditional `*` guard behavior, and DBus down behavior. Mock utility managers allow command dispatch testing without a daemon; integration tests should cover real DBus calls in a controlled environment.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/ganesha_mgr.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/ganesha_stats.py -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/ganesha_stats.py

## Purpose

`ganesha_stats.py` is the command-line frontend for reading and controlling Ganesha statistics counters over DBus, with optional JSON output for many report types.

## Important APIs, Types, and Functions

`print_usage_exit` renders usage. Top-level parsing handles commands including `global`, `list_clients`, `deleg`, `inode`, `iov3`, `iov4`, `iov41`, `iov42`, `iomon`, `export`, `total`, `fast`, `pnfs`, `fsal`, `reset`, `enable`, `disable`, `status`, `v3_full`, `v4_full`, `auth`, `client_io_ops`, `export_details`, and `client_all_ops`. It uses `RetrieveExportStats` and `RetrieveClientStats` from `Ganesha.glib_dbus_stats`.

## Control Flow

The default command is `global`. A leading `json` switches output mode and shifts the command. The script validates required IPs, export IDs, FSAL names, and stat-type arguments, then creates both export and client retrieval interfaces. It dispatches to the selected retrieval method and prints either `result.json()` or `str(result)`.

## State and Persistence Behavior

Most commands are read-only. `reset`, `enable`, and `disable` mutate server statistics counter state. There is no local persistence.

## Dependencies and Integration Points

It depends on `Ganesha.glib_dbus_stats` and `dbus`. It integrates with multiple Ganesha DBus stats interfaces through that library.

## Risks and Edge Cases

Both retrieval interfaces are constructed for every command, so client DBus availability can affect export-only commands and vice versa. JSON mode excludes `fsal`, `reset`, `enable`, and `disable`, but other classes may still have incomplete JSON behavior if library support drifts. Manual argument parsing uses `isdigit`, so negative export IDs are only represented by omission and non-decimal forms are rejected.

## Test Signals

CLI tests should cover default command, JSON command shifting, usage failures, stat-type validation, and each dispatch branch with mocked retrieval objects. Integration tests should run representative text and JSON commands against a daemon.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/ganesha_stats.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/ganeshactl.py -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/ganeshactl.py

## Purpose

`ganeshactl.py` is the graphical NFS-Ganesha administration tool. It wires the generated main window UI to PyQt DBus wrappers for admin, export, client, and log operations.

## Important APIs, Types, and Functions

`MainWindow(QtGui.QMainWindow)` defines `show_status` and methods for menu actions: `quit`, `connect_gsh`, `add_client`, `remove_client`, `export_mgr`, `logsettings`, `reset_grace`, `shutdown`, `reload`, `stats`, `view_exports`, `view_clients`, `help`, and `status_message`. The main block creates `QApplication`, gets the system bus, shows the window, and runs the event loop.

## Control Flow

Construction loads `Ui_MainWindow`, creates DBus wrappers, creates `LogSetDialog`, connects menu actions, creates export/client table models, and installs them on the table views. User actions either prompt for input, call DBus wrappers, show dialogs, or fetch current table data. DBus status replies update the status bar.

## State and Persistence Behavior

GUI state includes wrapper objects, table models, and the log dialog. Persistent effects are remote DBus operations: add/remove clients, grace, shutdown, reload, and log setting changes.

## Dependencies and Integration Points

It depends on PyQt5, generated UI modules, `Ganesha.admin`, `export_mgr`, `client_mgr`, `log_mgr`, and Qt table/dialog modules. It requires a system bus service `org.ganesha.nfsd`.

## Risks and Edge Cases

The code imports widgets from `QtGui`, but PyQt5 places many widgets in `QtWidgets`. It uses `quit()` rather than application quit. Several menu actions are placeholders. It does not validate IP addresses or protect reload/shutdown beyond a message box. Underlying table/log models contain additional Python 2/PyQt compatibility risks.

## Test Signals

GUI smoke tests should instantiate `MainWindow` with a fake DBus connection or fake wrappers, verify all action connections, and exercise table refreshes. Manual/integration tests should cover DBus error reporting and privileged operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/ganeshactl.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/get_clientids.py -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/get_clientids.py

## Purpose

`get_clientids.py` is a CBSIM diagnostic script that introspects the callback simulator and prints known client IDs.

## Important APIs, Types, and Functions

Top-level code opens `dbus.SystemBus`, gets `/org/ganesha/nfsd/CBSIM`, calls `Introspect` through `dbus.INTROSPECTABLE_IFACE`, resolves `get_client_ids` on `org.ganesha.nfsd.cbsim`, and prints the result.

## Control Flow

The script performs all work at import/execution time with no argument parsing. It prints introspection XML first, then prints the client ID list returned by DBus.

## State and Persistence Behavior

It is read-only and persists nothing.

## Dependencies and Integration Points

It depends on `dbus` and the Ganesha CBSIM DBus object.

## Risks and Edge Cases

There is no exception handling, so DBus absence or method errors produce tracebacks. Printing full introspection data may be noisy for scripts consuming output. It is suitable for manual diagnostics, not stable machine parsing.

## Test Signals

Mock DBus tests should verify method lookup and printed sections. Integration tests require CBSIM support enabled in a Ganesha test instance.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/get_clientids.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/grace_period.py -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/grace_period.py

## Purpose

`grace_period.py` is a small command-line helper that triggers a Ganesha grace period for a supplied client IP address over DBus.

## Important APIs, Types, and Functions

Top-level code reads `sys.argv[1]`, opens `dbus.SystemBus`, gets `/org/ganesha/nfsd/admin`, resolves `grace` on `org.ganesha.nfsd.admin`, and prints the result.

## Control Flow

The script prints `event:ip_addr=...`, connects to DBus, prints "Start grace period.", calls `grace(ipaddr)`, and exits with an error message if DBus object lookup or method call fails.

## State and Persistence Behavior

There is no local persistence. The remote daemon enters a grace behavior for the provided IP/client.

## Dependencies and Integration Points

It depends on `dbus` and the Ganesha admin DBus interface. It may be used by event hooks or operator scripts.

## Risks and Edge Cases

It indexes `sys.argv[1]` without checking argument count. IP addresses are not validated. Error messages hide the underlying DBus exception detail.

## Test Signals

Tests should cover missing argument handling, DBus unavailable behavior, and successful `grace` invocation with a mocked admin object.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/grace_period.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/knfs2ganesha-exports.py -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/knfs2ganesha-exports.py

## Purpose

`knfs2ganesha-exports.py` converts Linux kernel NFS `/etc/exports` entries from stdin into Ganesha `EXPORT`, `FSAL`, and `CLIENT` configuration blocks.

## Important APIs, Types, and Functions

The pyparsing grammar parses export paths, hosts, and host options. Globals `gan_paths` and `export_id` track generated exports. Functions are `process_exports`, `process_opts`, `create_client`, `usage`, and `main`. Supported FSAL names are `gpfs`, `vfs`, and `lustre`.

## Control Flow

`main` parses optional `--fsal`, creates a temporary config file, sets `CONFFILE`, and calls `process_exports`. Each non-comment stdin line is parsed into a path and host option blocks. `process_opts` maps kernel options to Ganesha key/value pairs and rejects unsupported risky options such as `async` and `subtree_check`. `create_client` shells out to `ganesha_conf set` to create or update blocks. The final temp config is printed to stdout.

## State and Persistence Behavior

The converter writes to a temporary file through `ganesha_conf` and prints generated config. It does not modify `/etc/ganesha/ganesha.conf` unless callers redirect output. Global `export_id` increments per unique path.

## Dependencies and Integration Points

It depends on `pyparsing`, `subprocess`, `tempfile`, and the installed `ganesha_conf` command. It reuses `config_editor` indirectly through that command.

## Risks and Edge Cases

Default options with dash/hyphen are explicitly unsupported. Unknown options abort conversion. Shelling out for every block is slower and inherits `ganesha_conf.py` Python 3 write risks. The parser supports quoted paths but has limited host syntax. Export IDs are generated from input order and may not preserve existing IDs.

## Test Signals

Golden-output tests should feed representative `/etc/exports` lines with `ro/rw`, squash, `sec=`, anon IDs, comments, quoted paths, multiple hosts, unsupported options, and each FSAL. Tests should use a temporary `ganesha_conf` or monkeypatch subprocess.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/knfs2ganesha-exports.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/manage_clients.py -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/manage_clients.py

## Purpose

`manage_clients.py` is an older Qt event-loop CLI for adding, removing, and showing Ganesha clients.

## Important APIs, Types, and Functions

`ManageClients(QtCore.QObject)` owns a PyQt `ClientMgr`, emits/receives status, and provides `addclient`, `removeclient`, `showclients`, `proc_clients`, and `status_message`. The main block dispatches `add`, `remove`, and `show`.

## Control Flow

The script creates a `QApplication`, installs `DBusQtMainLoop`, opens the system bus, constructs the wrapper, calls the requested asynchronous DBus method, and enters the event loop. Completion callbacks print results and call `sys.exit`.

## State and Persistence Behavior

No local persistence exists. Add/remove mutate daemon client state; show is read-only.

## Dependencies and Integration Points

It depends on PyQt5, dbus Qt mainloop integration, and `Ganesha.client_mgr.ClientMgr`. It overlaps with `ganesha_mgr.py`.

## Risks and Edge Cases

It indexes argv without length checks. `QApplication` is imported from `PyQt5.QtGui`, which is usually wrong for PyQt5. Printed columns omit NFSv4.2 while the namedtuple includes it. Error and success statuses both go through `status_message` text beginning with `Error:`.

## Test Signals

CLI tests should cover missing/unknown commands, mocked add/remove/show completions, and PyQt5 import smoke. Integration tests can be limited because `ganesha_mgr.py` covers the newer path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/manage_clients.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/manage_exports.py -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/manage_exports.py

## Purpose

`manage_exports.py` is an older Qt event-loop CLI for showing, adding, updating, removing, and displaying Ganesha exports.

## Important APIs, Types, and Functions

`ShowExports(QtCore.QObject)` wraps `ExportMgr` and provides `showexports`, `addexport`, `updateexport`, `removeexport`, `displayexport`, `proc_export`, `proc_exports`, and `status_message`. The main block dispatches commands by argv.

## Control Flow

Like other Qt wrappers, it issues an asynchronous DBus call, enters the Qt event loop, and exits from completion callbacks after printing output. Display and show connect to dedicated export signals; add/update/remove use status callbacks.

## State and Persistence Behavior

No local persistence exists. Add/update/remove mutate live daemon export state; display/show are read-only.

## Dependencies and Integration Points

It depends on PyQt5, dbus Qt mainloop integration, and `Ganesha.export_mgr.ExportMgr`. It is superseded by `ganesha_mgr.py` for broader management.

## Risks and Edge Cases

Arguments are not length-checked before indexing. `QApplication` import location is likely incompatible with PyQt5. Print formatting omits NFSv4.2 even though the export tuple contains it. Export changes are not confirmed.

## Test Signals

Mocked DBus/PyQt tests should exercise every command and callback, including empty export lists and DBus errors. CLI tests should cover malformed invocation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/manage_exports.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/manage_logger.py -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/manage_logger.py

## Purpose

`manage_logger.py` is an older Qt event-loop CLI for getting, setting, and listing Ganesha log component levels.

## Important APIs, Types, and Functions

`ManageLogger(QtCore.QObject)` wraps `LogManager` and provides `get_level`, `set_level`, `getall`, `proc_level`, `proc_components`, and `status_message`. The main block dispatches `get`, `set`, and `getall`.

## Control Flow

The script creates Qt/DBus event-loop state, issues one asynchronous log DBus request, enters the event loop, and exits from the callback after printing the level, component dictionary, or error.

## State and Persistence Behavior

No local persistence exists. `set` mutates live daemon log-level properties; `get`/`getall` are read-only.

## Dependencies and Integration Points

It depends on PyQt5, `DBusQtMainLoop`, and `Ganesha.log_mgr.LogManager`. It overlaps with `ganesha_mgr.py get/set/getall log`.

## Risks and Edge Cases

It indexes argv without validating argument count. `QApplication` import location is likely wrong for PyQt5. It uses the older Qt DBus wrapper, so conversion/API compatibility issues in `log_mgr.py` apply.

## Test Signals

Mocked tests should cover get/set/getall callbacks and error propagation. CLI tests should cover missing args and unknown command handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/manage_logger.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/org.ganesha.nfsd.conf -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/org.ganesha.nfsd.conf

## Purpose

This DBus policy file controls access to the `org.ganesha.nfsd` service on the system bus.

## Important APIs, Types, and Functions

The policy grants user `root` permission to own `org.ganesha.nfsd`, send to that destination, and send to selected interfaces: `org.freedesktop.DBus.Introspectable`, `org.ganesha.nfsd.CBSIM`, and `org.ganesha.nfsd.admin`.

## Control Flow

DBus daemon reads this XML policy at service/policy load time. There is no executable code.

## State and Persistence Behavior

Installed policy persistently affects system bus authorization. It does not maintain runtime state itself.

## Dependencies and Integration Points

It depends on DBus busconfig format and is installed under a DBus system policy directory by packaging/build scripts. It directly impacts whether the Python administration scripts can reach Ganesha interfaces.

## Risks and Edge Cases

The policy shown allows only root. Tools run by non-root users will fail unless additional distro policy exists. It mentions admin and CBSIM but not every interface used by newer tools, so effective access may depend on broader destination send permission or other policy files.

## Test Signals

System integration tests should verify root can own and call the service and non-root behavior matches expected security policy. DBus policy validation can parse the XML against the busconfig DTD.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/org.ganesha.nfsd.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/setup.py.in -->
# sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/setup.py.in

## Purpose

This CMake-substituted setup template packages the `ganeshactl` Python tools and scripts.

## Important APIs, Types, and Functions

The template calls `distutils.core.setup` with package name `ganeshactl`, version `${GANESHA_VERSION}`, package directory `${CMAKE_CURRENT_SOURCE_DIR}`, packages `Ganesha` and `Ganesha.QtUI`, and generated `scripts = [${SCRIPTS_STRING}]`.

## Control Flow

CMake configures this template into a concrete `setup.py`. During build/install, Python executes the setup script to package modules and install script entry files selected by CMake.

## State and Persistence Behavior

It creates build/install artifacts but has no application runtime state.

## Dependencies and Integration Points

It depends on CMake substitutions and Python packaging tooling. `CMakeLists.txt` in the same script area likely supplies `SCRIPTS_STRING` and handles generated UI modules.

## Risks and Edge Cases

`distutils` is deprecated/removed in newer Python environments, so modern builds may need setuptools or PEP 517 tooling. The template assumes generated script names are valid Python list entries. Missing generated UI modules will still package a broken GUI.

## Test Signals

Build tests should configure the template, build/install the package, and import `Ganesha` plus run installed script help paths. Packaging tests under current supported Python versions catch `distutils` issues.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/ganeshactl/setup.py.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/gen_ctdb_epoch.py -->
# sources/user-network-fs/nfs-ganesha/src/scripts/gen_ctdb_epoch.py

## Purpose

`gen_ctdb_epoch.py` generates a cluster-safe 32-bit Ganesha epoch for CTDB environments by combining a CTDB node ID with a per-node generation counter.

## Important APIs, Types, and Functions

`main` increments a generation ID, masks it to 16 bits, reads the CTDB node ID, combines `nodeid << 16 | genid`, and prints it. `get_genid` reads `/var/lib/nfs/ganesha/seq_num`; `put_genid` writes it; `get_nodeid` runs `/usr/bin/ctdb pnn`.

## Control Flow

On execution, `main` reads/updates the generation file and invokes CTDB. Exceptions are caught in the `__main__` block, logged to syslog with traceback, and cause exit status 1.

## State and Persistence Behavior

The persistent state is `/var/lib/nfs/ganesha/seq_num`, storing the last generation number. The script mutates this file on every successful run.

## Dependencies and Integration Points

It depends on `/usr/bin/ctdb`, writable `/var/lib/nfs/ganesha`, Python subprocess APIs, and syslog. It is integrated through startup configuration such as `EPOCH_EXEC`.

## Risks and Edge Cases

There is no file locking despite importing `fcntl`; concurrent invocations can lose increments. If CTDB output is non-numeric, `int(nodeid)` fails. Generation wraps at 16 bits. The generation file write is not atomic or fsynced.

## Test Signals

Tests should mock `ctdb pnn`, use a temporary sequence file, verify initial/multiple/wrap values, and simulate concurrent calls if the script is hardened.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/gen_ctdb_epoch.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/gerrit/checkpatch-to-gerrit-json.py -->
# sources/user-network-fs/nfs-ganesha/src/scripts/gerrit/checkpatch-to-gerrit-json.py

## Purpose

This filter converts `checkpatch.pl` output into Gerrit review JSON comments.

## Important APIs, Types, and Functions

Top-level code reads stdin in groups containing a message and `FILE: path:line:` marker, accumulates `comments` keyed by file, and prints a JSON object with either `comments` and a summary message or `Checkpatch OK`.

## Control Flow

The script repeatedly reads a first line and file-line, stops when the file-line is blank, then appends continuation lines until a blank separator. It extracts filename and line with regex and appends comment dictionaries. At the end it emits JSON to stdout.

## State and Persistence Behavior

Only an in-memory `comments` dict is maintained. There is no persistence.

## Dependencies and Integration Points

It depends on Python `json`, `re`, and `sys`. `gerrit-checkpatch.sh` pipes `checkpatch.pl` output through it into `gerrit review --json`.

## Risks and Edge Cases

The script uses `comments.has_key`, invalid in Python 3, while the shebang is generic `python`. It assumes every issue has a matching `FILE:` line; malformed input can make `filere` `None`. It does not include labels, only comments/message.

## Test Signals

Feed sample checkpatch outputs with one issue, multiple issues per file, multiple files, and no issues. Run under both Python 2 expectations and the repository's supported Python 3 environment to catch `has_key`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/gerrit/checkpatch-to-gerrit-json.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/gerrit/gerrit-checkpatch.sh -->
# sources/user-network-fs/nfs-ganesha/src/scripts/gerrit/gerrit-checkpatch.sh

## Purpose

`gerrit-checkpatch.sh` automates checkpatch review comments for Gerrit/GerritHub patchsets in the NFS-Ganesha project.

## Important APIs, Types, and Functions

Configuration variables define Gerrit server/user/key/project. `input_loop` streams or queries patchsets. `commit_review` submits JSON review output or prints it in dry-run mode. The main pipeline fetches refs, runs `git show --format=email`, pipes through `checkpatch.pl`, converts to JSON, and submits review.

## Control Flow

Options `-n`, `-q`, and `-c` select dry-run, one-shot query, or one-shot cat mode. Stream mode loops forever, reconnecting to `gerrit stream-events`. Each input line supplies `REF COMMIT`; the script fetches the ref and reviews the commit.

## State and Persistence Behavior

It mutates local git fetch state and remote Gerrit review comments. It stores no explicit local state; Gerrit comments are used to avoid duplicate query processing.

## Dependencies and Integration Points

It depends on ssh access to Gerrit, a `gerrit` git remote, `checkpatch.pl`, `gerrit-query.awk`, `gerrit-stream-filter.py`, and `checkpatch-to-gerrit-json.py`.

## Risks and Edge Cases

Hard-coded server/user/key/project limit portability. The loop can repeatedly reconnect and submit if filters fail. It assumes relative path `../checkpatch.pl` from the script directory/current working directory context. Python filter compatibility issues can break review submission.

## Test Signals

Dry-run tests with `-c` and known `REF COMMIT` input should validate generated JSON without remote submission. Query-mode tests can use captured Gerrit query output and AWK filter fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/gerrit/gerrit-checkpatch.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/gerrit/gerrit-query.awk -->
# sources/user-network-fs/nfs-ganesha/src/scripts/gerrit/gerrit-query.awk

## Purpose

`gerrit-query.awk` filters `gerrit query --comments --patch-sets` output to find open patchsets that do not already have a review by the trigger user.

## Important APIs, Types, and Functions

The AWK script tracks `patchSets[curSet]["reviewed"]`, `ref`, and `commit`; `username`; and current patchset number. It prints `ref commit` for unreviewed patchsets when a new `change` starts.

## Control Flow

On `change` lines it flushes accumulated patchsets, printing those without a `reviewed` marker, then resets state. It detects trigger comments when `username` is `ganesha-triggers` and message starts `Patch Set`, records patchset refs/revisions from query output, and supports optional `debug`.

## State and Persistence Behavior

State is in-memory per input stream. There is no persistence.

## Dependencies and Integration Points

It depends on AWK, with comments noting AWK >= 4 for one-shot query use. `gerrit-checkpatch.sh` invokes it.

## Risks and Edge Cases

The script flushes when the next `change` begins, so the last change may not be emitted unless the input format includes a trailing change or EOF handling is added. Parsing is tightly coupled to Gerrit text output formatting.

## Test Signals

Fixture tests with one/multiple changes, reviewed/unreviewed patchsets, and EOF-only final changes should verify emitted refs. Run with the target AWK implementation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/gerrit/gerrit-query.awk -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/gerrit/gerrit-stream-filter.py -->
# sources/user-network-fs/nfs-ganesha/src/scripts/gerrit/gerrit-stream-filter.py

## Purpose

`gerrit-stream-filter.py` filters Gerrit stream-events JSON and emits patchset refs/revisions for patchset-created events in the target project.

## Important APIs, Types, and Functions

Top-level code reads optional project name from argv, parses JSON lines from stdin, filters by `type == patchset-created` and `change.project`, and prints `patchSet.ref patchSet.revision`.

## Control Flow

Malformed JSON lines are skipped. Matching events are optionally debug-printed, then emitted and stdout is flushed for pipeline responsiveness.

## State and Persistence Behavior

No persistent state exists.

## Dependencies and Integration Points

It depends on Python `json` and `sys`. `gerrit-checkpatch.sh` consumes its output in stream mode.

## Risks and Edge Cases

The script assumes all parsed JSON objects have `type`, `change`, and `patchSet` keys; unrelated Gerrit events missing those keys can raise `KeyError`. The shebang is generic `python`, though the code is mostly Python 2/3 compatible due to `unicode` literals only.

## Test Signals

Feed fixtures for matching events, other projects, other event types, malformed JSON, and events missing optional fields. Verify line-buffered output in pipeline mode.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/gerrit/gerrit-stream-filter.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/git_hooks/commit-msg -->
# sources/user-network-fs/nfs-ganesha/src/scripts/git_hooks/commit-msg

## Purpose

This Git commit-msg hook inserts a Gerrit `Change-Id` when missing and appends the author's `Signed-off-by` line when absent.

## Important APIs, Types, and Functions

Shell functions include `add_ChangeId`, `_gen_ChangeIdInput`, `_gen_ChangeId`, and `add_SignOffBy`. `CHANGE_ID_AFTER` controls footer insertion order. `MSG` is the commit message file path from Git.

## Control Flow

`add_ChangeId` strips comments/diffs/signoffs to determine whether there is a meaningful message, respects `gerrit.createChangeId=false`, skips if a Change-Id already exists, generates an ID from tree/parent/author/committer/message data, and uses AWK to insert it into the footer. `add_SignOffBy` derives the author identity and appends it if absent.

## State and Persistence Behavior

It mutates the commit message file in place. It does not change repository files directly.

## Dependencies and Integration Points

It depends on POSIX shell tools, `git`, `sed`, `awk`, and Gerrit review conventions. `install_git_hooks.sh` installs it into `.git/hooks/commit-msg`.

## Risks and Edge Cases

Footer parsing is complex and inherited from older Gerrit hook code. Automatically appending Signed-off-by may surprise contributors if signoff policy changes. It assumes the message file is writable and `git var` identity is configured.

## Test Signals

Hook tests should feed messages with no footer, existing Change-Id, Signed-off-by, issue footers, comment-only messages, and diff trailers, then verify final footer ordering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/git_hooks/commit-msg -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/git_hooks/install_git_hooks.sh -->
# sources/user-network-fs/nfs-ganesha/src/scripts/git_hooks/install_git_hooks.sh

## Purpose

`install_git_hooks.sh` installs repository Git hooks and checkpatch configuration into the current checkout.

## Important APIs, Types, and Functions

Top-level shell logic determines `CURDIR`, `TOPDIR`, and `HOOKDIR`; symlinks `src/scripts/checkpatch.conf` to `.checkpatch.conf`; copies `pre-commit` and `commit-msg` into `.git/hooks`; and marks them executable.

## Control Flow

The script handles macOS by using `greadlink -m`; otherwise it uses `readlink -m`. It resolves the git top-level directory, then performs symlink/copy/chmod operations.

## State and Persistence Behavior

It persistently modifies the local checkout's `.git/hooks` and top-level `.checkpatch.conf` symlink.

## Dependencies and Integration Points

It depends on Bash, `git`, `readlink` or `greadlink`, `ln`, `cp`, and `chmod`. It installs the hooks researched in this subset.

## Risks and Edge Cases

It overwrites existing hooks without backup. The checkpatch symlink target is relative and assumes invocation from a normal repository layout. macOS requires GNU readlink as `greadlink`.

## Test Signals

Run in a temporary git repository and verify hook files and executable bits. Tests should cover preexisting hooks and macOS/Linux path resolution if supported.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/git_hooks/install_git_hooks.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/git_hooks/pre-commit -->
# sources/user-network-fs/nfs-ganesha/src/scripts/git_hooks/pre-commit

## Purpose

This Git pre-commit hook enforces clang-format/checkpatch policy and prompts before committing submodule pointer updates.

## Important APIs, Types, and Functions

`handle_unformatted_file` fails commits unless a rebase is in progress. `check_staged_files` runs `clang-format -style=file --dry-run --Werror -` on staged C/C++ files under `src`. Later top-level logic runs `checkpatch.pl --no-signoff -q -` on the staged diff and checks `.gitmodules` paths for staged submodule updates.

## Control Flow

The hook first checks staged source formatting. It chooses a diff base of `HEAD` or the empty tree, runs checkpatch on the staged diff, then lists modified submodules and prompts on `/dev/tty` before allowing the commit.

## State and Persistence Behavior

It does not modify files; it blocks or allows commits. It reads staged content and repository metadata.

## Dependencies and Integration Points

It depends on Bash, git, clang-format, repository `src/scripts/checkpatch.pl`, `.gitmodules`, and an interactive TTY for submodule prompts.

## Risks and Edge Cases

The staged-file loop uses shell word splitting, so filenames with spaces are unsafe. In non-interactive environments, the submodule prompt can fail or hang. The `grep -F "$SUBMODULES"` command with multi-line pattern content can behave unexpectedly. Rebase detection changes formatting failures into warnings.

## Test Signals

Hook tests should stage formatted/unformatted C files, checkpatch violations, no-submodule and submodule changes, initial commit state, rebase state, and non-interactive commits.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/git_hooks/pre-commit -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/gpfs-epoch/CMakeLists.txt -->
# sources/user-network-fs/nfs-ganesha/src/scripts/gpfs-epoch/CMakeLists.txt

## Purpose

This CMake file builds and installs the GPFS epoch helper script when GPFS FSAL support and Python 3 are enabled.

## Important APIs, Types, and Functions

Within `if(USE_FSAL_GPFS)` and `if(Python3_FOUND)`, it defines `SETUP_PY_IN`, generated `SETUP_PY`, `OUTPUT`, `GPFS_EPOCH_SRCS`, script copy commands, `SCRIPTS_STRING`, `configure_file`, `python_gpfs_epoch` target, and install `execute_process` commands for legacy setup.py or wheel/installer paths.

## Control Flow

CMake strips `.py` from `gpfs-epoch.py` to make an executable script in the build directory, configures `setup.py`, builds either with legacy `setup.py build` or `python -m build --wheel`, and installs via setup.py or `installer`.

## State and Persistence Behavior

It creates build-tree scripts, package metadata, wheel/build artifacts, a stamp file, and install-tree scripts.

## Dependencies and Integration Points

It depends on CMake variables `USE_FSAL_GPFS`, `Python3_EXECUTABLE`, `USE_LEGACY_PYTHON_INSTALL`, `GANESHA_MAJOR_VERSION`, `GANESHA_MINOR_VERSION`, `GANESHA_VERSION`, `CMAKE_INSTALL_PREFIX`, and `LIBEXECDIR`. It packages `gpfs-epoch.py`.

## Risks and Edge Cases

Wheel naming is hard-coded as `gpfs-${GANESHA_MAJOR_VERSION}${GANESHA_MINOR_VERSION}-py3-none-any.whl`, which must match actual build output. The legacy and modern install branches differ in destination handling. Distutils setup template may be dated for current Python packaging.

## Test Signals

CMake configure/build/install tests should cover GPFS enabled/disabled, legacy/non-legacy Python install, wheel file naming, and installed script path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/gpfs-epoch/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/gpfs-epoch/gpfs-epoch.py -->
# sources/user-network-fs/nfs-ganesha/src/scripts/gpfs-epoch/gpfs-epoch.py

## Purpose

`gpfs-epoch.py` generates a cluster-unique Ganesha epoch for GPFS environments by combining the GPFS node ID with a local generation number.

## Important APIs, Types, and Functions

`main`, `get_genid`, `put_genid`, `get_mount`, and `get_nodeid` implement the epoch calculation. `GracePeriodArg` and `KxArgs` are ctypes structures used for the GPFS ioctl. Constants include `epoch_file`, `GPFS_DEVNAMEX`, `kGanesha`, and `OPENHANDLE_GET_NODEID`.

## Control Flow

`main` increments and stores the generation ID, discovers the GPFS node ID via `get_nodeid`, combines the two fields into a 32-bit epoch, and prints it. `get_mount` parses `mount` command output for a GPFS mount point. `get_nodeid` opens `/dev/ss0` and the GPFS mount directory, builds ioctl argument structs, and calls `fcntl.ioctl`.

## State and Persistence Behavior

The persistent state is `/var/lib/nfs/ganesha/gpfs-epoch`, updated on each run. The script also opens GPFS device and mount directory file descriptors.

## Dependencies and Integration Points

It depends on GPFS device `/dev/ss0`, a mounted GPFS filesystem, platform-specific `mount`, `fcntl.ioctl`, ctypes structure layout matching GPFS headers, and syslog for exception reporting. It is installed by the GPFS epoch CMake package.

## Risks and Edge Cases

There is no locking or atomic write for the generation file. `get_mount` may return `None`, causing `os.open(None, ...)`. File descriptors are not explicitly closed. Generation wraps at 16 bits. The ioctl structure is hand-coded and sensitive to platform ABI.

## Test Signals

Unit tests can mock mount output, generation file access, and ioctl return values. Integration tests require GPFS and should verify epoch uniqueness across nodes/restarts and failure logging when GPFS is unavailable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/gpfs-epoch/gpfs-epoch.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/gpfs-epoch/setup.py.in -->
# sources/user-network-fs/nfs-ganesha/src/scripts/gpfs-epoch/setup.py.in

## Purpose

This setup template packages the GPFS epoch helper script for installation.

## Important APIs, Types, and Functions

It calls `distutils.core.setup` with package name `gpfs`, version `${GANESHA_VERSION}`, package directory `${CMAKE_CURRENT_SOURCE_DIR}`, package list `['.']`, and generated scripts list `${SCRIPTS_STRING}`.

## Control Flow

CMake configures the template into `setup.py`; build/install commands execute it directly in legacy mode or use modern wheel tooling around it.

## State and Persistence Behavior

It produces build/install packaging artifacts. It has no application runtime state.

## Dependencies and Integration Points

It depends on CMake substitutions and Python packaging. `gpfs-epoch/CMakeLists.txt` is the direct consumer.

## Risks and Edge Cases

`distutils` is deprecated. `packages = ['.']` is unusual and may not behave as intended with modern packaging tools, though the primary payload is a script. Generated script list correctness depends on CMake.

## Test Signals

Package build tests should run both configured setup.py and wheel build paths, then verify the `gpfs-epoch` script is installed and executable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/gpfs-epoch/setup.py.in -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/nfs-ganesha-config.sh -->
# sources/user-network-fs/nfs-ganesha/src/scripts/nfs-ganesha-config.sh

## Purpose

`nfs-ganesha-config.sh` prepares runtime environment configuration for the systemd Ganesha service by reading distro-specific config files and generating run/default variables.

## Important APIs, Types, and Functions

Shell variables include `CONFIGFILE`, `RUNCONFIG`, `EPOCH_EXEC`, `NODEID_EXEC`, `NOFILE`, `EPOCHVALUE`, `NODEID`, `NOFILE_CONF`, `NUMACTL`, and `NUMAOPTS`. There are no shell functions.

## Control Flow

The script chooses `/etc/sysconfig/ganesha` and `/run/sysconfig/ganesha`, falling back to Debian/Ubuntu paths when the sysconfig directory is absent. If the config file is readable, it sources it, optionally runs epoch/node-ID executables, writes a systemd `LimitNOFILE` drop-in when `NOFILE` is set, reloads systemd, creates the run config directory, and writes the original config plus computed `EPOCH`, `GNODEID`, and NUMA variables.

## State and Persistence Behavior

It writes `/run/sysconfig/ganesha` or `/etc/default/nfs-ganesha` and may write `/lib/systemd/system/nfs-ganesha.service.d/10-nofile.conf`. It may invoke epoch helpers that update their own generation files.

## Dependencies and Integration Points

It depends on POSIX shell, systemd, optional `numactl`, and distro config files. It integrates with systemd service startup and variables consumed by the NFS-Ganesha unit.

## Risks and Edge Cases

The script sources config files directly, so they execute shell code. Several variable expansions are unquoted, making paths with spaces unsafe. Writing a drop-in under `/lib/systemd/system` may conflict with distro packaging expectations. The Debian fallback writes to `/etc/default`, which is persistent rather than `/run`.

## Test Signals

Shell tests should run in a temp root or container with mocked config files, epoch/node commands, numactl, and systemctl. Verify generated environment lines and NOFILE drop-in behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/nfs-ganesha-config.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/podman/Containerfile -->
# sources/user-network-fs/nfs-ganesha/src/scripts/podman/Containerfile

## Purpose

This Containerfile builds a development/test container image from a caller-supplied base image, installs packages, and creates a non-root user matching supplied host UID/GID.

## Important APIs, Types, and Functions

Build args are `IMAGE`, `USER_ID`, and `GROUP_ID`. The file copies `install-packages.sh` to `/tmp`, runs it, removes any existing `ubuntu` user/group, creates group/user `user`, configures passwordless sudo in `/etc/sudoers.d/container`, and switches to `USER user`.

## Control Flow

The build starts from `FROM $IMAGE`, runs package installation as root, adjusts user/group identity, writes sudo policy, and leaves subsequent container commands running as the created user.

## State and Persistence Behavior

The image persists installed packages, the created user/group/home directory, and sudoers file. Runtime container state is not handled here.

## Dependencies and Integration Points

It depends on a valid base image, build args, `install-packages.sh` in the build context, and Linux user-management utilities. It is intended for Podman but is also Dockerfile-like.

## Risks and Edge Cases

Missing build args can make `FROM`, `groupadd`, or `useradd` fail. If the base image lacks `userdel`, `groupdel`, `groupadd`, `useradd`, or sudo support, the build fails. The sudoers file permissions are not explicitly set. Removing `ubuntu` may be harmless but base-image-specific.

## Test Signals

Container build tests should pass representative base images and UID/GID values, verify package installation, user identity, sudoers behavior, and non-root default user.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/scripts/podman/Containerfile -->
