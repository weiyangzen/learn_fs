# sources/distributed-fs/lizardfs/src/common/event_loop.cc

Purpose: implements the global single-threaded event loop used by daemon-style LizardFS components.

Important APIs/types/functions: global `gExitingStatus`, `gReloadRequested`, lists of poll/time/destruct/can-exit/want-exit/reload/each-loop handlers, `eventloop_run`, registration functions, time registration/change/unregister, `eventloop_want_to_terminate`, `eventloop_want_to_reload`, and `eventloop_updatetime`.

Control flow: each loop builds poll descriptors by calling registered `desc` callbacks, polls for up to 50 ms or nonblocking once, updates time, serves poll callbacks, runs each-loop callbacks, handles clock jumps, fires due timers, reloads config after the current iteration, and progresses graceful exit from `kWantExit` to `kCanExit` to `kDoExit`.

State and persistence: global in-memory callback lists and atomic current time values. No persistence. It is not designed for multiple independent loop instances.

Dependencies and integration: depends on `event_loop.h`, `cfg_reload`, `Exception`, `massert`, syslog, `poll` or `tcppoll`. It is a core integration point for modules that register periodic, IO, cleanup, reload, and shutdown handlers.

Risks: global mutable state makes tests and reentrancy hard. Callback registration/unregistration is not synchronized. Timer handles are raw addresses into a `std::list`; unregistering unknown handles aborts. Exceptions are caught only in destruct/reload callbacks, not poll/timer/each-loop callbacks.

Test signals: no direct tests in subset; daemon integration tests are needed for lifecycle, timers, and shutdown sequencing.
