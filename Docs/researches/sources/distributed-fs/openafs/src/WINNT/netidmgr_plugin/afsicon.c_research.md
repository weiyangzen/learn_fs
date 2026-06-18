# sources/distributed-fs/openafs/src/WINNT/netidmgr_plugin/afsicon.c

## Purpose

`afsicon.c` implements the OpenAFS token-state notification icon for NetIDMgr. It creates a hidden message-only window, adds/removes a shell notification icon, handles click/context-menu commands, opens help/release notes, and updates icon/tooltip state based on service or token status.

## Important APIs, types, and functions

Static state includes `message_window_class`, `notifier_window`, and `notification_icon_added`. Helper functions are `get_default_notifier_action`, `get_release_notes`, `handle_select`, `prepare_context_menu`, `handle_context_menu`, `notifier_wnd_proc`, `initialize_if_necessary`, `set_tooltip_and_icon`, `collect_cell_names`, and `set_state_from_ui_thread`. Public functions are `afs_remove_icon` and `afs_icon_set_state`.

## Control flow

`afs_icon_set_state` packages the desired `notification_icon_state` and optional credential set. If the icon already exists, it updates directly; otherwise it requests a NetIDMgr UI-thread callback. The callback initializes the window class/window/icon if necessary, then switches on state. For token reporting, it collects non-expired AFS cell names from the provided credential set and shows either a no-token icon or an OK icon with the cell list. Service-stopped and service-error states use separate icons and localized tooltips.

The hidden window receives `TOKEN_MESSAGE_ID` from the shell. Select/key-select triggers the configured default NetIDMgr action (`KHUI_ACTION_OPEN_APP` or new credentials). Context menu loads `IDR_CTXMENU`, adjusts the default item caption, hides Release Notes if not found, and tracks the popup. Command handling triggers the default action, opens plugin help, or opens `ReleaseNotes.chm` from the OpenAFS client installation path. `afs_remove_icon` deletes the shell icon.

## State and persistence behavior

State is in-process: registered window class atom, message window handle, and whether the shell icon was added. It reads persistent NetIDMgr config `CredWindow\NotificationAction` and HKLM OpenAFS client `CurrentVersion\PathName` for release notes. Tooltip content is generated from live credential expiration and cell attributes, not persisted.

## Dependencies and integration points

The file depends on shell notification APIs, NetIDMgr UI actions and callback scheduling, credential set traversal, AFS credential attributes, localized resources/icons/menus, `afs_html_help`, HTML Help, Shlwapi path helpers, and version resource macro `AFS_VERINFO_BUILD`.

## Risks and edge cases

`afs_icon_set_state` passes a pointer to a stack `state_data` into `khui_request_UI_callback`; correctness depends on that callback being synchronous or copying the data, which is not obvious from this file. `collect_cell_names` concatenates into a fixed 256-character buffer and ignores truncation failures. The release-notes registry string termination uses `cpath[min(cb_data, MAX_PATH - 1)]`, where `cb_data` is bytes for `RegQueryValueEx`, not a wide-character index. `Shell_NotifyIcon(NIM_SETFOCUS)` calls use a mostly empty `NOTIFYICONDATA`, which may not identify the icon on all shell versions.

## Test signals

Tests should verify icon creation/removal, click and keyboard selection, context menu default caption, release-notes discovery, help launch, tooltip content for no tokens and multiple non-expired cells, expired-token filtering, service stopped/error icons, callback behavior before icon creation, and long cell-list truncation.
