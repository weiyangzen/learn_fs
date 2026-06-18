## sources/distributed-fs/openafs/src/WINNT/afsapplib/al_progress.h

Purpose: Declares the `PROGRESSDISPLAY` class and the control IDs expected by progress dialog templates.

Important APIs and types: Exports `PROGRESSDISPLAY` with constructors, `GetProgressDisplay`, range/progress accessors, operation text accessors, `SetFinishMessage`, `Show`, `Close`, `GetStatus`, and `GetWindow`. Defines `IDC_OPERATION`, `IDC_PROGRESS`, and `IDC_PROGRESSTEXT`.

Control flow: No runtime logic; the header defines the callback signature accepted by `Show` and documents modal versus modeless behavior.

State and persistence: Declares private fields for finished/status state, critical section, refcount, dialog ownership, callback data, range/progress, and UI text buffers.

Dependencies and integration points: Includes `TaLocale.h` and `subclass.h`; requires dialog templates to provide the declared control IDs and a callback matching `DWORD CALLBACK fn(LPPROGRESSDISPLAY, LPARAM)`.

Risks: The private method declarations include qualified names inside the class (`void PROGRESSDISPLAY::OnUpdate`) which is non-standard in modern C++ compilers. The class self-deletes through private destructor/refcount behavior, making ownership easy to misuse.

Test signals: Compile with target compiler; verify dialog templates contain required IDs; test client code that stores pointers after `Close`/finish.
