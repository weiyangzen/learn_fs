## sources/distributed-fs/openafs/src/WINNT/afsusrmgr/options.h

Purpose: declares the options dialog launcher.

Important APIs/types/functions: `ShowOptionsDialog(HWND hParent)`.

Control flow: `OnContextCommand(M_OPTIONS)` calls this function with the main window as parent.

State and persistence behavior: implementation edits `gr` restored settings and relies on application quit for registry persistence.

Dependencies and integration points: connected to command menu, help registration for `IDD_OPTIONS`, credential warnings, search behavior, and refresh scheduling.

Risks: single entry point hides which settings are changed; future options need synchronized UI, restored struct, and persistence versioning.

Test signals: compile command handler and verify Options menu opens modal dialog with the expected parent.
