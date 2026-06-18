## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/command.cpp

Purpose: central command dispatcher for menus, context menus, accelerator commands, and keyboard-navigation behavior in the Account Manager UI.

Important APIs/types/functions: `OnRightClick`, `ShowContextMenu`, and `OnContextCommand` route user gestures. Command handlers include `Command_OnView`, `Command_OnShowActions`, `Command_OnRefresh`, `Command_OnUnlock`, `Command_OnProperties`, `Command_OnMembership`, `Command_OnChangePassword`, `Command_OnRename`, `Command_OnCreateUser`, `Command_OnCreateGroup`, `Command_OnCreateMachine`, and `Command_OnDelete`. Keyboard handlers emulate dialog behavior for tab, control-tab, return, context-menu, escape, and properties keys.

Control flow: right-clicks first collect the selected `ASIDLIST` from `Display_GetSelectedList`; header clicks open the column menu, while item/list clicks open user/group/machine menus. `OnContextCommand` switches on `resource.h` command IDs and forwards work to dialogs, async tasks, help, or display refresh logic. Selection-sensitive operations inspect `asc_ObjectTypeGet_Fast` and dispatch only homogeneous selections to user/group/machine property, membership, rename, delete, or password workflows.

State and persistence behavior: modifies restored UI state through `gr.fShowActions`, per-tab view structures, and icon-view settings. Mutating commands generally allocate task parameter objects or pass ASID lists to `StartTask`, leaving state refresh to task completion and display layers.

Dependencies and integration points: depends on `display.cpp` for selection and view changes, `creds.cpp` for cell/credential dialogs, user/group/machine modules for object dialogs, `action.cpp` for the operations window, `cell_prop.cpp` and `options.cpp` for application dialogs, and WinHelp/AfsAppLib for help flows.

Risks: ownership of `LPASIDLIST` is path-sensitive; handlers pass lists to dialogs/tasks or free them when unused. Mixed selections intentionally no-op after freeing the list, which can appear unresponsive. `Command_OnKey_Return` posts a double-click notification to the focused control's parent and assumes the focus window is a valid notification source.

Test signals: cover every menu and context-menu ID for no selection, single selection, multi-selection, mixed user/group/machine selection, and keyboard accelerators. Verify that disabled context-menu items (`M_CPW`, `M_RENAME`) match multi-selection constraints and that list/header right-clicks open the correct menu.
