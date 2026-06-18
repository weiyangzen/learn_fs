# sources/distributed-fs/openafs/src/WINNT/tests/torture/StopStressTest/StopStressTest.c

Purpose: small interactive console controller for a running Windows torture stress test. It signals global named events so other processes can pause, continue, or end.

Important APIs and functions: `main` opens standard input and creates `AfsShutdownEvent`, `AfsPauseEvent`, and `AfsContinueEvent`. `GetConsoleInput` reads console `KEY_EVENT` records and maps `p`, `c`, `e`, and `q` to requests. `ProcessRequest` sets/resets the named events and prevents continue/pause after an end request.

Control flow: the program loops prompting the operator, blocks in `ReadConsoleInput`, exits immediately on `q`, and calls `ProcessRequest` for recognized stress-control commands. End sets shutdown, clears pause, and sets continue so paused workers can notice shutdown.

State and persistence: no file persistence. State is carried by named Win32 manual-reset event objects and a local static `LastRequest`.

Dependencies and integration: integrates with the torture/stress processes by event names only; all participants must agree on `AfsShutdownEvent`, `AfsPauseEvent`, and `AfsContinueEvent`.

Risks and test signals: `CreateEvent` failures are not checked, and `GetConsoleInput` reads only one record despite a 128-record buffer. Good test signals are visible console messages plus worker processes actually pausing, resuming, or shutting down when the events are set.
