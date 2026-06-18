<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/toolbox.h -->
# sources/distributed-fs/openafs/src/WINNT/afssvrcfg/toolbox.h

## Purpose
Declares the shared UI helper API and `ENABLE_STATE` enum for configuration dialogs.

## Important APIs, Types, And Functions
Defines `ES_DISABLE`, `ES_ENABLE`, and `ES_TOGGLE`; declares wrappers for enablement, elapsed time, text, updates, checkbox/listbox/up-down controls, resource strings, bolding, and message boxes.

## Control Flow
No runtime flow; it provides declarations, defaults, and inline conveniences such as `GetWndTextLength` and `MakeBold(HWND, UINT)`.

## State And Persistence
No state declared.

## Dependencies And Integration Points
Requires Win32/TCHAR context and `cchRESOURCE`; used widely by `afssvrcfg` dialogs.

## Risks And Edge Cases
`ShowWnd` is declared twice. The header `SetCheck` takes `BOOL`, while implementation accepts `int`; three-state checkbox callers rely on compatibility.

## Test Signals
Compilation and three-state checkbox behavior are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afssvrcfg/toolbox.h -->
