<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_browseset.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsapplib/al_browseset.cpp

Purpose: implements the modal fileset browse dialog shell for selecting a volume/fileset name.

Important APIs/types/functions: `AfsAppLib_ShowBrowseFilesetDialog()` launches `IDD_APPLIB_BROWSE_FILESET`. `BrowseSet_DlgProc()` handles dialog initialization, destruction, worker messages, selection, double-click, restart, and enter key. `BrowseSet_OnInitDialog()` configures title/prompt, image list, cell combo, selected fileset, and starts search. `BrowseSet_StartSearch()` clones parameters and creates `BrowseSet_Init_ThreadProc()`. `BrowseSet_OnAddString()` inserts fileset names and stores heap string pointers in list item data. `BrowseSet_EmptyList()` frees those strings.

Control flow: dialog startup populates cell choices and starts a worker. The worker posts start/done notifications; found names would be posted back as `WM_FOUNDNAME` and added to the list. Selecting a list item updates the edit field; OK writes the edit value to `lpp->szFileset`.

State and persistence: per-dialog state is held in the caller's `BROWSESETDLG_PARAMS` and the list item data. The worker receives a heap copy of parameters and deletes it on exit. No durable state.

Dependencies/integration: uses AfsAppLib dialog, listview, image-list, string, and cell-list helpers plus Windows threading/messages.

Risks and test signals: `BrowseSet_Init_ThreadProc()` currently contains no actual fileset enumeration, so the dialog can show an empty list while still enabling manual entry. `CreateThread()` failure is compared with `INVALID_HANDLE_VALUE`, but Windows returns `NULL` on failure. Tests should cover manual entry, empty enumeration, list string cleanup, restart behavior, cell-list disabled mode, and thread failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_browseset.cpp -->
