<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/perf.h -->
## sources/distributed-fs/openafs/src/WINNT/client_osi/perf.h

Purpose: Declares the OSI performance test entry point.

Important APIs, types, and functions: `main_PerfTest(HANDLE)` runs the two-thread mutex ping-pong test.

Control flow and state: The caller supplies a window handle for display updates.

Persistence and dependencies: No persistence. Requires Windows `HANDLE`.

Integration points: Included by the OSI test GUI.

Risks: The declaration says `extern int` while the implementation uses old-style implicit return; strict builds should align prototypes.

Test signals: Build warning checks and GUI invocation smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/client_osi/perf.h -->
