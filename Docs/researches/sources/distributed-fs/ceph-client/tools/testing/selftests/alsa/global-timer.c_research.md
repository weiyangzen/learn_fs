# sources/distributed-fs/ceph-client/tools/testing/selftests/alsa/global-timer.c

Purpose: helper executable for `utimer-test` that opens a global ALSA timer, counts async tick callbacks for a timeout, and prints the total.

Important APIs/types/functions: global `ticked`; `async_callback()` increments it; `bind_to_timer()` constructs `hw:CLASS=...,DEV=...,SUBDEV=...`, opens timer nonblocking, sets auto-start/ticks, registers async handler, starts timer, busy-waits until timeout, then stops/closes; `main()` parses device/subdevice/timeout.

Control flow: line-buffer stdout, parse arguments, bind to requested timer, print "Timer has started", wait for ticks, print "Total ticks count".

State and persistence: in-process tick counter only; no files.

Dependencies/integration: libasound timer API and SIGIO async delivery. Invoked by `utimer-test` via `popen()`.

Risks and test signals: busy-wait loop consumes CPU. `perror("Usage: ...")` is semantically wrong because no errno is set. Failure to open/configure timer exits nonzero and causes parent test failure.
