<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_cover.cpp -->
# sources/distributed-fs/openafs/src/WINNT/afsapplib/al_cover.cpp

Purpose: implements AfsAppLib cover windows: lightweight child/sibling dialogs that hide a window or its client area and display descriptive text plus an optional button.

Important APIs/types/functions: `COVERPARAMS` carries client-vs-window mode, target window, description, and button text. `AfsAppLib_CoverClient()` and `AfsAppLib_CoverWindow()` uncover any existing cover, clone parameters, and either call `OnCoverWindow()` directly or post `WM_COVER_WINDOW` to the main UI window. `AfsAppLib_Uncover()` removes covers. `OnCoverWindow()` creates or destroys cover dialogs identified by `dwCOVER_SIGNATURE`. `Cover_DialogProc()` initializes controls, hides covered child windows using `WS_EX_HIDDENBYCOVER`, resizes the cover, restores children on destroy, and forwards optional button clicks to the parent.

Control flow: callers request cover/uncover from any thread. If a main window exists, work is marshaled to that UI thread. Cover creation hides target content and positions the cover over the same rectangle. Uncover searches child dialogs for the signature and destroys the cover.

State and persistence: no global state beyond the resize table. Temporary cloned strings and params are freed after cover creation. Hidden child state is marked in extended window style bits until cover destroy.

Dependencies/integration: depends on AfsAppLib main-window hook, dialog helpers, resize helpers, Windows child/sibling window relationships, and cover resources/control ids.

Risks and test signals: `WS_EX_HIDDENBYCOVER` uses a high extended-style bit that could collide with platform-defined styles. Uncover logic treats invisible target windows as sibling-cover cases. Tests should cover client-area and whole-window cover modes, optional button forwarding, resize behavior, multiple cover/uncover cycles, child visibility restoration, and cross-thread posting through the main window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/afsapplib/al_cover.cpp -->
