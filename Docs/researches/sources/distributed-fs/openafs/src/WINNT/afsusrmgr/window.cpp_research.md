# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/window.cpp

Purpose: implements the main AFS User Manager dialog, tab host, and dynamic menu state.

Important APIs and control flow: `Main_DialogProc` installs `g.hMain`, handles show/activation/credential/refresh/action messages, routes completed update tasks to display handlers, and delegates commands to context command handling. `Main_OnInitDialog` restores the saved main window rectangle, creates the tab control image list and tab items, subclasses the tab control, sizes the child area, selects the last tab, and registers action listening. `Main_PrepareTabChild` destroys the old tab child and creates the new Users/Groups/Machines dialog. `Main_SetMenus` and `Main_SetViewMenus` enable, check, and radio-select operations based on current selection and tab view mode.

State and dependencies: uses global runtime/preferences (`g.hMain`, `g.idCell`, `gr.rMain`, `gr.iTabLast`, view settings, action-window flag). Dependencies include user/group/machine tab procs, command/action/credential/display helpers, Windows tab controls, resize helpers, and admin action listen APIs.

Risks and test signals: tab index and `aTABS` ordering must match `TABTYPE` expectations. Menu enablement depends on `Display_GetSelectedList` and cached object type. Tests should cover startup restoration, tab switching, resize forwarding, credentials messages, completed update tasks, and menu state for user/group/machine selections.
