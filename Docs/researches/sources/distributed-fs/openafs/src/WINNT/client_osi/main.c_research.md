## sources/distributed-fs/openafs/src/WINNT/client_osi/main.c

Purpose: Provides the Win32 GUI harness for OSI lock/performance/trylock tests.

Important APIs/functions: `WinMain` runs app initialization and the message loop. `InitApplication` registers the window class; `InitInstance` creates the main window, initializes the debug RPC system, and computes display geometry. `MainWndProc` handles menu commands for tests and lock debugging. `main_ClearDisplay` and `main_ForceDisplay` update the text screen.

Control flow/state: Global window/instance handles, `main_screenText`, `screenRect`, and `lineHeight` store UI state. Menu commands synchronously run tests and repaint the status area.

Dependencies/integration: Uses Win32 GDI/window APIs, OSI debug initialization, and test modules `basic`, `perf`, and `trylock`.

Risks/tests: Long-running tests execute on the UI thread, blocking normal message processing. `main_ForceDisplay` deletes a stock brush, which is unsafe. Test menu command dispatch, debug on/off lock type selection, repaint behavior, repeated tests, and RPC debug initialization failures.
