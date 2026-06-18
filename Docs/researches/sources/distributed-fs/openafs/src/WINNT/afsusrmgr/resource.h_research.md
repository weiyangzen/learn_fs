## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/resource.h

Purpose: generated-style resource ID registry for strings, icons, bitmaps, accelerators, menus, dialogs, controls, and command IDs used by the Account Manager.

Important APIs/types/functions: defines `IDS_*` strings for titles, column names, actions, help messages, errors, account permissions, delete/create/property text, and machine/user/group labels. Defines `IDI_*`, `IDB_*`, `ACCEL_MAIN`, `MENU_*`, `IDD_*`, `IDC_*`, and `M_*` command IDs. Private control IDs cover main tab/list controls, property dialogs, create/delete dialogs, browse dialogs, credentials, options, and search.

Control flow: most modules switch on `M_*` command IDs from menus/buttons/accelerators; dialog procs address controls with `IDC_*`; help registration maps `IDD_*` and `IDC_*` IDs to help contexts.

State and persistence behavior: no runtime state, but numeric IDs are persistent build-time contracts across `.rc`, help maps, menus, accelerators, and code.

Dependencies and integration points: included broadly by application headers and generated resource compilation. It is central to `command.cpp`, `helpfunc.cpp`, tab dialogs, property dialogs, and options.

Risks: duplicate numeric IDs are normal in dialog-local control spaces but risky if reused in the same dialog or command context. Changing resource IDs without updating help maps and command switches breaks UI behavior silently. `_APS_NEXT_*` values must stay coherent for resource editor use.

Test signals: full resource compile, menu command routing for every `M_*`, context help for every registered dialog, dialog smoke tests checking each referenced control exists, and accelerator tests for keyboard command IDs.
