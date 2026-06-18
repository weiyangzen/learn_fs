# sources/distributed-fs/ceph-client/include/trace/events/watchdog.h

Purpose: Defines watchdog device tracepoints for start, ping, stop, and timeout changes.

Important APIs/types/functions: `watchdog_template` backs `watchdog_start`, `watchdog_ping`, and `watchdog_stop`; `watchdog_set_timeout` records old/new timeout state for a `watchdog_device`.

Control flow: Watchdog core or drivers emit events during lifecycle operations. Assignments copy watchdog id, status, timeout, and operation-specific values.

State/persistence: Watchdog device state is not changed here; trace buffers retain operation snapshots.

Dependencies/integration: Includes `linux/watchdog.h` and tracepoints; useful for watchdog core and driver debugging.

Risks: Watchdog paths may be time-critical. Trace overhead must not delay pings, and timeout units must remain clear.

Test signals: Enable `watchdog:*` and run watchdog start/ping/stop/timeout tests, checking trace order against driver callbacks.
