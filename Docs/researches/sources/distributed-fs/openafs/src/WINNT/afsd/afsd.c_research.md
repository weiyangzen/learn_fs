# sources/distributed-fs/openafs/src/WINNT/afsd/afsd.c

## Purpose
`afsd.c` is the Win32 GUI-style entry point and minimal window host for the OpenAFS Windows cache manager process. It sets panic handling, initializes the hidden AFSD window class/instance, starts core AFS client subsystems, and runs the Windows message loop.

## Important APIs, types, and functions
Important globals include `main_inst`, `main_wnd`, `main_statusText`, `main_rect`, `afsd_logp`, `hAFSDWorkerThread`, `DoTerminate`, and `WaitToTerminate`. Functions are `afsd_notifier`, `WinMain`, `InitClass`, `InitInstance`, and `MainWndProc`.

`afsd_notifier` is registered with `osi_InitPanic`. `WinMain` installs the unhandled exception filter, enables debug allocation behavior in debug builds, registers/creates the window, and dispatches messages. `InitInstance` calls `afsi_start`, `afsd_InitCM`, `afsd_InitDaemons`, and `afsd_InitSMB`.

## Control flow
Startup enters `WinMain`, configures debug behavior when `_DEBUG` is defined, registers the `AFSDWinClass` window class, creates the main window, computes text metrics for a status rectangle, installs `afsd_notifier`, starts lower-level subsystems, initializes the cache manager, daemon threads, and SMB interface, then shows the window minimized without activation. The main loop runs until `PostQuitMessage`.

The window procedure blocks attempts to open the window via `WM_QUERYOPEN`, delegates commands to the default window procedure, clears paint invalidation on `WM_PAINT`, and on `WM_DESTROY` stops RPC server listening and posts quit.

## State and persistence behavior
This file initializes process-global runtime state but does not directly write persistent configuration. Downstream initialization functions read configuration and initialize cache, daemon, SMB, and RPC state. Panic handling forces AFSD and buffer traces before process exit, making diagnostic state visible through the tracing subsystem.

## Dependencies and integration points
The file depends on Win32 windowing, RPC management, the OSI layer, AFSD initialization headers, SMB initialization, tracing (`afsd_ForceTrace`, `buf_ForceTrace`), and many globals declared in `afsd.h`. It is the UI-subsystem entry point for the Windows cache manager and coordinates with service-oriented pieces in adjacent files.

## Risks and edge cases
Panic handling displays a modal message box and exits the process, which is useful interactively but risky in service or unattended contexts. `sprintf` into fixed buffers assumes short file paths in panic text. Initialization failures call `osi_panic`, so partial subsystem startup cleanup depends on panic/exit behavior. The window is hidden/minimized and refuses open, so diagnostics through UI are intentionally minimal. Inline `_asm int 3h` is architecture/compiler-specific debug behavior.

## Test signals
Tests should verify startup success and failure paths for `afsd_InitCM`, `afsd_InitDaemons`, and `afsd_InitSMB`; message handling for `WM_QUERYOPEN`, `WM_PAINT`, and `WM_DESTROY`; panic notifier trace forcing; and debug command-line allocation break parsing in debug builds. Integration smoke tests should assert that cache manager, daemon, SMB/RDR, and RPC state are initialized as expected after `InitInstance`.
