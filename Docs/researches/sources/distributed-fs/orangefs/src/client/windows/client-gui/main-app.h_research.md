# sources/distributed-fs/orangefs/src/client/windows/client-gui/main-app.h

## Purpose
This header declares the wxWidgets application and main window classes for the OrangeFS Windows file browser.

## Important APIs, types, and functions
It defines menu/list ids in `enum ID`, declares `MainApp` with initialization, filesystem setup, cleanup, and getters for file listing/attributes/display dimensions, and declares `MainFrame` with menu objects, window state, local sync path, a `FileListHandler` pointer, and event handlers.

## Control flow
`MainApp::OnInit` is the wx application entry. `MainFrame` declares an event table in the implementation to bind menu and list events to the declared methods.

## State and persistence behavior
The header defines app-owned in-memory state: `fileListing`, root credential, root attributes, mount entries, file count, and display dimensions. `MainFrame` tracks menus, window size, sync path, and list handler. No persistence format is defined.

## Dependencies and integration points
It depends on wxWidgets, C runtime debug allocation headers, `orangefs-client.h`, and `filelisthandler.h`. The mutual include with `filelisthandler.h` creates tight compile-time coupling.

## Risks and edge cases
- Declares copy constructor and assignment for `MainFrame` but does not define them in the implementation shown; accidental use will fail to link.
- Getters return `short int` for counts and dimensions, which can truncate modern display sizes or larger listings.
- `getFileAttrs` returns attributes by value, which is fine for current small structs but can hide lifetime/ownership expectations.
- Header includes implementation-heavy dependencies, increasing rebuild scope.

## Test signals
Compile the GUI with strict warnings and link checks, verify event table ids align with controls, and test large display dimensions and file counts around `short int` limits.
