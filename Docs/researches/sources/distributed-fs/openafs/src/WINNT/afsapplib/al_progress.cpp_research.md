## sources/distributed-fs/openafs/src/WINNT/afsapplib/al_progress.cpp

Purpose: Implements `PROGRESSDISPLAY`, a helper object that binds a dialog progress UI to a background worker thread.

Important APIs and functions: Constructors wrap an existing window or create a modeless dialog. Public methods get/set range, progress, operation text, finish message, status, and close the display. `Show` starts `ThreadProc`; `Finish` records status and notifies UI; `OnUpdate` refreshes the progress bar and text. Static `ProgressDisplay_HookProc` handles update and destruction messages.

Control flow: `Init` stores `this` in `DWLP_USER`, installs a subclass hook, initializes critical section/refcount, captures localized text templates, and configures progress range. `Show` increments the reference count, shows the dialog, creates a worker thread, and either pumps messages modally until finished or returns immediately if a finish message is configured. The worker invokes the user callback and calls `Finish`.

State and persistence: Per-object mutable state is protected by `m_cs`: progress range, current progress, operation text, finished flag, status, callback pointer, and refcount. No persistent storage.

Dependencies and integration points: Uses Win32 dialogs, common-control progress bar messages, `subclass.h`, `FormatString`, resource/control IDs from `al_progress.h`, and app allocation macros.

Risks: Worker thread handle is not closed. Destructor assumes `m_hWnd` is valid enough for `SetWindowLongPtr`. `SetProgress` is monotonic and cannot move progress backward. `m_cRef` deletion protocol is subtle because `Close` and `Finish` can both decrement. `Show` creates the thread before checking handle success.

Test signals: Existing-window and created-dialog paths; modal and finish-message modeless modes; worker exceptions; close-before-finish; progress range edge cases; operation text updates from worker thread; destruction cleanup.
