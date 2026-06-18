## sources/distributed-fs/openafs/src/WINNT/afsapplib/al_help.cpp

Purpose: Maintains dialog-to-help context registrations and handles `IDHELP`/`WM_HELP` for app-library dialogs.

Important APIs and functions: `AfsAppLib_RegisterHelpFile` sets the global help filename. `AfsAppLib_RegisterHelp` inserts or updates a `DIALOGHELP` entry containing dialog ID, per-control help context array, and overview context ID. `AfsAppLib_HandleHelp` handles command and F1/help messages.

Control flow: On `IDHELP`, it finds the matching dialog record and calls `WinHelp(..., HELP_CONTEXT, idhOverview)`. On `WM_HELP`, it either redirects dialog-level help to the `IDHELP` command or calls `WinHelp(..., HELP_WM_HELP, adwContext)` for a specific child control.

State and persistence: Global `g_szHelpfile`, dynamically grown `g_adh`, and `g_cdh` are process-local. No persistent storage; registrations are expected during app initialization.

Dependencies and integration points: Uses Win32 `WinHelp`, app allocation macro `REALLOC`, and is called by dialog procedures such as credential and bad-credential dialogs before normal message handling.

Risks: No synchronization protects the global registry. `if (g_szHelpfile)` is always true for the static array, so an empty filename can still be passed if registered empty. `WinHelp` is legacy/deprecated and may be unavailable on modern Windows without compatibility components.

Test signals: Register duplicate dialog IDs and confirm updates; test overview help, control help, missing registration fallback, empty help file behavior, and hook procedures that consume messages before help handling.
