# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khaction.h

## Purpose

This header declares NetIDMgr UI action, menu, accelerator, and action-context APIs. It describes how commands are represented, how custom menus and plugin actions are created, and how the current credential/identity selection context is captured and passed to actions.

## Important APIs, Types, and Functions

- `khui_action` describes standard and custom actions: command ID, action type, optional name, internal icon/string/help resource indices, custom caption/tooltip/listener/user data, and state.
- Action types and states include trigger/toggle types and enabled, disabled, checked, hot, and deleted states.
- `khui_action_ref` points to actions by command ID or direct action pointer and carries menu flags such as submenu, separator, by-reference, and default.
- `khui_menu_def` describes menus associated with an action or ad-hoc command, with constant or allocated item lists.
- Menu APIs include `khui_menu_create`, `khui_menu_dup`, `khui_menu_delete`, `khui_menu_insert_action`, `khui_menu_remove_action`, `khui_menu_get_size`, `khui_menu_get_action`, and `khui_find_menu`.
- `khui_scope` classifies UI selection as none, identity, credential type, group, or single credential.
- `khui_header` and `khui_action_context` represent outline group headers, selected identity/credential/type, selected credential set, selected count, and optional parameter data.
- Context APIs include `khui_context_set`, `khui_context_set_ex`, `khui_context_set_indirect`, `khui_context_get`, `khui_context_create`, `khui_context_release`, `khui_context_reset`, `khui_context_refresh`, and `khui_context_cursor_filter`.
- Action APIs include `khui_action_trigger`, `khui_find_action`, `khui_action_create`, `khui_action_delete`, `khui_action_get_data`, `khui_find_named_action`, `khui_enable_actions`, `khui_enable_action`, `khui_check_radio_action`, and `khui_check_action`.
- Accelerator helpers include `khui_get_cmd_accel_string` and, under `NOEXPORT`, global accelerator initialization.

## Control Flow

Menus are created or duplicated, populated with action references, and later rendered or traversed by UI code. Custom actions are created with captions, tooltips, user data, type, and an optional message subscription; triggering posts or dispatches an action message to the listener. UI selection changes call `khui_context_set()` or `_set_ex()`, which holds referenced identity/credential objects, extracts selected credentials from a source set, and updates side effects such as action enabled/checked state. Actions can be triggered with an explicit context or the current context.

## State and Persistence Behavior

The action system maintains registered actions, menu associations, global/current UI context, held identity/credential references, selected credential sets, and action state bits. Custom menu definitions created by `khui_menu_create()` or `khui_menu_dup()` are caller-owned and must be deleted. Custom action listeners are retained by the action system and released when no longer needed. No persistent storage is declared here, although named actions must not collide with configuration node names.

## Dependencies and Integration Points

The header depends on NetIDMgr types from surrounding includes, KCDB handles/credential types, message subscriptions, and Windows UI resources under `_WIN32` or internal `NOEXPORT` sections. It integrates the credential database with NetIDMgr menus, toolbar actions, context menus, keyboard accelerators, and plugin-defined commands.

## Risks

- Menu definitions are explicitly not thread-safe; concurrent modification can corrupt item arrays or invalidate returned references.
- Context setters should only be called from the UI thread.
- `khui_menu_get_action()` returns references invalidated by later menu modifications.
- Context structures returned by `khui_context_get()` must not be modified before release because release uses them to drop holds.
- Custom action deletion marks action contents invalid; plugins should delete only during unload and avoid triggering stale command IDs.
- Listener ownership is transferred: callers should not release the subscription after passing it to `khui_action_create()`.

## Test Signals

Tests should cover menu create/duplicate/delete, insertion/removal at specific indices and append behavior, separator/submenu/default flags, size and item retrieval invalidation rules, action create/delete/find-by-name/user-data, enable/check/radio state transitions, context set/get/release/reset with held identity and credential handles, cursor filtering against selected credential sets, and action trigger dispatch to a test subscription.
