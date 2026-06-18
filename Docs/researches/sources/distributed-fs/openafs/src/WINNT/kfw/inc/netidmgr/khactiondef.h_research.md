# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/khactiondef.h

## Purpose

`khactiondef.h` reserves the standard command identifier space used by the NetIDMgr user interface. It is not an implementation header; it is the ABI map that lets menus, toolbar buttons, context menus, keyboard accelerators, pseudo navigation events, and dynamically allocated user actions speak the same integer command language.

## Important APIs, Types, and Functions

- `KHUI_ACTION_BASE` starts the standard action ID bank at `50000`.
- `KHUI_ACTION_*` constants cover built-in commands such as properties, exit, default/search identity selection, password change, new credentials, refresh, layout controls, options panels, help, destroy/renew/import credentials, application open/close, menu activation, and layout reload.
- `KHUI_PACTION_*` constants are pseudo actions for generic UI events: menu, directional movement, enter/escape/OK/cancel/close/delete, extend/toggle selection, paging, selection-all, yes/no variants, remove/keep/discard.
- `KHUI_MENU_*` constants name stock menus and context menus, including main, file, credential, view, options, help, layout, toolbars, identity/token context menus, icon context menus, credential-window header context menu, and columns menu.
- `KHUI_TOOLBAR_STANDARD` identifies the stock toolbar.
- `KHUI_USERACTION_BASE` marks the allocator range for custom actions and `IS_USERACTION(cmd)` tests membership in that range.

## Control Flow

There is no runtime control flow in this header. The control-flow contract is indirect: UI code translates Windows menu and accelerator command IDs into these constants, then dispatches the ID through the action subsystem and message queue. Pseudo actions carry abstract navigation or dialog decisions rather than direct operations, so callers interpret them according to the focused control, active dialog, menu state, or alert response.

## State and Persistence Behavior

The constants are compile-time state. They must remain stable across modules that include `khactiondef.h`, resource scripts that embed command IDs, and any persisted UI configuration that stores command identifiers. Dynamic actions are expected to be allocated at or above `KHUI_USERACTION_BASE`; callers should not assume an upper bound beyond the action manager's own limits.

## Dependencies and Integration Points

This header is pulled into the public UI aggregation header `khuidefs.h` through `khaction.h`. It integrates with alert buttons in `khalerts.h`, action-context based operations in `khnewcred.h` and `khprops.h`, KMQ action messages (`KMSG_ACT_*`) in `khmsgtypes.h`, and menu/toolbar resources in the NetIDMgr executable and plugins.

## Risks and Edge Cases

- IDs are hand-assigned with gaps. Reusing a retired gap can collide with older binaries, resources, or plugin assumptions.
- `IS_USERACTION(cmd)` is a lower-bound test only. A malformed very large command ID will be considered user allocated.
- Pseudo actions do not encode source context. Handlers must validate focus, selection, and mode before treating them as concrete operations.
- The comment "Next menu: 14" is stale relative to later menu constants ending at `KHUI_MENU_COLUMNS`; future edits should rely on the actual definitions.

## Test Signals

- Build resource and accelerator tables against the header to catch command drift.
- Exercise each stock menu/toolbar command and confirm it routes to the intended KMQ or UI operation.
- Create custom actions and confirm every returned ID satisfies `IS_USERACTION`.
- Verify pseudo actions in dialogs, list views, and menus do not trigger destructive commands without context validation.
