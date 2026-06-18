# sources/distributed-fs/openafs/src/WINNT/afsusrmgr/window.h

Purpose: declares main-window entry points for the AFS User Manager UI.

Important APIs/types: exports `Main_DialogProc`, `Main_PrepareTabChild`, `Main_SetMenus`, and `Main_SetViewMenus`. These are used by startup code and tab/list dialogs when selection or view state changes.

State and dependencies: no state in the header; implementation uses globals in `g` and `gr`.

Risks and test signals: callers rely on these functions being safe when main window/tab controls exist. Tests should cover calling menu refresh after list selection changes and preparing explicit or current tab children.
