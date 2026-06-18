## sources/distributed-fs/openafs/src/WINNT/afsapplib/al_messages.h

Purpose: Centralizes custom `WM_USER` message IDs used by the app library for cross-thread UI requests, background task completion, credential changes, and dialog control.

Important APIs and definitions: Defines `WM_COVER_WINDOW`, `WM_CREATE_ERROR_DIALOG`, `WM_ENDTASK`, `WM_EXPIRED_CREDENTIALS`, `WM_CLOSE_DIALOG`, `WM_PERMTAB_REFRESH`, and `WM_REFRESHED_CREDENTIALS`, with comments documenting expected `WPARAM`/`LPARAM` payloads.

Control flow: This header has no execution logic. It reserves a message range starting at `WM_USER + 0x200` and allows modules such as error handling, task queue, cover dialogs, and credential code to communicate without hard-coded local constants.

State and persistence: None.

Dependencies and integration points: Included transitively via `afsapplib.h` by UI modules. It must stay consistent with message handlers in `al_error.cpp`, `al_task.cpp`, `al_creds.cpp`, cover-window code, and permission tabs.

Risks: Message IDs are library-private but still occupy the receiving window's `WM_USER` namespace, so embedding in foreign controls/windows could collide. Payload comments must remain accurate because the compiler cannot enforce `LPARAM` pointer ownership.

Test signals: Static checks for unique message IDs; integration tests for posted heap payload lifetime and handlers for each documented message.
