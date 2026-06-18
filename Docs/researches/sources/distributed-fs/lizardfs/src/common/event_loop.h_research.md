# sources/distributed-fs/lizardfs/src/common/event_loop.h

Purpose: declares the global event-loop API and exit state machine.

Important APIs/types/functions: `ExitingStatus` enum, globals `gExitingStatus` and `gReloadRequested`, registration functions for destruct/can-exit/want-exit/reload/poll/each-loop, timer registration/change/unregister APIs in seconds and milliseconds, nonblocking poll request, termination/reload triggers, loop run/release/destruct, and time accessors.

Control flow: callers register callbacks before `eventloop_run`, then interact through termination/reload/time APIs during runtime.

State and persistence: declares global state owned by `event_loop.cc`; no persistent data.

Dependencies and integration: includes `poll.h` or Winsock types and standard containers. It is used by long-running LizardFS processes as a central scheduler.

Risks: C function-pointer API limits capture/context and pushes state to globals. The exposed globals allow external mutation outside API invariants.

Test signals: no direct tests in this subset.
