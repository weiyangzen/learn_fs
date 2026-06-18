# sources/distributed-fs/coda/coda-src/venus/sighand.h

## Purpose
This header declares the Venus signal handler initialization API and the small set of signal-related globals shared with the main process loop.

## Important APIs, Types, and Functions
It declares `SigInit()`, `TerminateVenus`, and `mount_done`. `TerminateVenus` is the shutdown flag checked by `venus.cc`; `mount_done` is exposed for mount signaling paths.

## Control Flow
Callers invoke `SigInit()` once during startup after logging support is available. Signal handlers then update globals or perform direct cleanup.

## State and Persistence Behavior
No persistent state is declared here. The globals are transient process flags, though handlers that use them may trigger persistent recovery cleanup.

## Dependencies and Integration Points
The header intentionally has no heavy includes. It is included by Venus startup code and any module needing shutdown status.

## Risks and Test Signals
Risk is limited to global-state coupling. Compile tests should confirm all users include the header cleanly, and runtime tests should confirm `TerminateVenus` ends the main loop when termination is routed through the non-immediate path.
