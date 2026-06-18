# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afshelp.c

## Purpose

`afshelp.c` resolves and launches the OpenAFS NetIDMgr plugin HTML help file. It builds the full path to `afsplhlp.chm` relative to the plugin module and appends optional topic/postfix strings for callers.

## Important APIs, types, and functions

The file defines static `helpfile[MAX_PATH]` and public `afs_html_help(HWND caller, wchar_t * postfix, UINT cmd, DWORD_PTR data)`.

## Control flow

On first call, `afs_html_help` uses `GetModuleFileNameEx` with `hInstance` to locate the plugin module, strips the file name with `PathRemoveFileSpec`, appends `AFS_HELPFILE`, and caches that base path. On every call it copies the cached base to a larger stack buffer, appends any postfix such as a topic path, and calls `HtmlHelp` with the requested command and data.

## State and persistence behavior

The cached `helpfile` path is process-lifetime mutable state and is not protected by a lock. It does not persist to disk. HTML Help may open external UI state managed by the Windows help subsystem.

## Dependencies and integration points

It depends on `afscred.h`, `shlwapi.h`, `htmlhelp.h`, `psapi.h`, and string-safe APIs. `afsconfigdlg.c` and `afsicon.c` call it for configuration help and notification-menu help topics.

## Risks and edge cases

The comment says it can only be called from the UI thread. The static cache is not thread-safe. In debug builds it asserts that module-path lookup succeeds; in release builds a failure can leave an empty base and still call `HtmlHelp` with a relative/postfix-only path. The combined buffer is `MAX_PATH + MAX_PATH`, so very long postfixes can fail copy/cat silently via `StringCb*` return values that are ignored.

## Test signals

Tests should verify first-call path resolution, repeated-call cache reuse, topic postfix append, missing help file behavior, UI-thread invocation, and help commands used by configuration popups and welcome topics.
