<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/trylock.h -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/trylock.h

Purpose: Declares the try-lock stress test entry point.

Important APIs, types, and functions: `main_TryLockTest(HANDLE)` runs the two-thread hierarchy/try-lock test.

Control flow and state: The caller supplies the UI handle used for display updates.

Persistence and dependencies: No persistence. Requires Windows `HANDLE`.

Integration points: Included by the OSI test GUI.

Risks: Implementation uses old-style return declarations; strict compile checks should ensure prototype consistency.

Test signals: Build and GUI invocation smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/trylock.h -->
