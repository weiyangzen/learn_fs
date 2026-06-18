# sources/distributed-fs/orangefs/src/client/windows/client-gui/filelisthandler.h

## Purpose
This header declares the singleton `FileListHandler` GUI helper and the list-control id used by the OrangeFS Windows file browser.

## Important APIs, types, and functions
`FileListHandler` publicly exposes `getInstance`, destructor, `addColumn`, `removeColumn`, `displayFileStatus`, `processListCtrlDoubleClick`, and `getSyncStatus`. It privately owns `syncList`, `syncPane`, `syncColumnIDs`, and `localStorePath`; copy and assignment are private no-op definitions.

## Control flow
Consumers call `FileListHandler::getInstance`, which lazily allocates the singleton via a private constructor. `MainFrame` owns and deletes the singleton pointer during destruction.

## State and persistence behavior
All state is process-local wxWidgets UI state. `localStorePath` is declared for future sync storage behavior but is not used by the implementation in this subset.

## Dependencies and integration points
It includes wxWidgets, C++ streams/maps, and `main-app.h`, while `main-app.h` also includes this header. Include guards prevent infinite include expansion, but the circular dependency contributes to tight coupling. Windows builds optionally include ATL time support.

## Risks and edge cases
- Singleton allocation is not thread-safe and has no reset method.
- Public methods `displayFileStatus` and `processListCtrlDoubleClick` are declared but not defined in the implementation shown, which can cause link errors if used.
- Using declarations in a header (`using std::...`) leak names into all include consumers.
- `LIST_CTRL_SYNC` is set to `0x1`, which can collide with other wx ids.

## Test signals
Build the GUI and confirm no unresolved symbols for declared methods. Exercise singleton construction/destruction across app startup/shutdown and verify event ids do not collide with main-frame menu/list ids.
