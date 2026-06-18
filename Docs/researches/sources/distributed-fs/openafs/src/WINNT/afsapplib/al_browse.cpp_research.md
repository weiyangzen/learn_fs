<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_browse.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsapplib/al_browse.cpp

Purpose: implements the modal browse dialog for selecting AFS users or groups, with local KAS enumeration or remote admin-server enumeration.

Important APIs/types/functions: `BROWSEDIALOGPARAMS` stores cell/name selections, browse type, image list, thread state, cell list, and credentials. `AfsAppLib_ShowBrowseDialog()` constructs params and launches `IDD_APPLIB_BROWSE`. `DlgProc_Browse()` handles initialization, list selection, enter key, none checkbox, thread status, and found-name messages. `DlgProc_Browse_StartSearch()` and `StopSearch()` manage the enumeration thread. `DlgProc_Browse_ThreadProc()` chooses remote enumeration when `AfsAppLib_GetAdminServerClientID()` is nonzero, otherwise opens local client/KAS libraries. `EnumeratePrincipalsLocally()` uses KAS principal enumeration; `EnumeratePrincipalsRemotely()` opens a cell and retrieves user properties through `asc_ObjectFindMultiple()` and `asc_ObjectPropertiesGetMultiple()`.

Control flow: dialog startup fills UI text/cell choices, starts a worker thread, and receives `WM_FOUNDNAME` messages containing heap strings to add to the list. Selection updates the edit field. Changing the cell or pressing restart stops the old search and starts a new one.

State and persistence: per-dialog heap state and worker thread state only. No durable persistence. Posted strings are freed after insertion.

Dependencies/integration: depends on AfsAppLib dialog/list helpers, image resources, `al_dynlink` local library loading, KAS/client admin C APIs, remote `asc_*` APIs, credentials handles, and Windows common controls.

Risks and test signals: local enumeration does not visibly filter by `BROWSETYPE`, and remote enumeration always asks for `TYPE_USER`, so group browse behavior may be incomplete. `StopSearch()` may use `TerminateThread()` before enumeration becomes easily stoppable. Tests should cover local vs remote paths, cell changes, none checkbox behavior, cancelled searches, posted string ownership, and user/group browse modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_browse.cpp -->
