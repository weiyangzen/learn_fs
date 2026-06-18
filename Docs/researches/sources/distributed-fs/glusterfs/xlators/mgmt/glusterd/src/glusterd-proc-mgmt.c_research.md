# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-proc-mgmt.c

Purpose: Provides generic process metadata initialization and PID-file based stop/status helpers for glusterd-managed daemons. It abstracts common service process fields and force-stop behavior used as daemon management is migrated toward `glusterd_proc_t`.

Important APIs and functions: `glusterd_proc_init()` copies process name, pidfile, log directory/file, volfile path, volfile id, and volfile server into a `glusterd_proc_t`. `glusterd_proc_stop()` checks a pidfile, sends the requested signal, optionally waits and escalates to `SIGKILL`, and removes the pidfile. `glusterd_proc_get_pid()` returns the pid found by `gf_is_service_running()`. `glusterd_proc_is_running()` is a boolean status wrapper.

Control flow: Stop first treats an absent/non-running pidfile as success. If the process is running, it sends `sig`; `ESRCH` is success, other kill errors are logged. For non-force stops, it returns after the first signal. For `PROC_STOP_FORCE`, it polls ten times with 100 ms sleeps, temporarily dropping `conf->big_lock` while sleeping, then sends `SIGKILL` if the process still exists.

State and persistence: State is carried in the `glusterd_proc_t` string fields and in service pidfiles. The helper updates persistence only by unlinking pidfiles; it does not update volume/node store files.

Dependencies and integration points: Uses `gf_is_service_running()`, `gf_unlink()`, Gluster logging/messages, `synclock_unlock()`/`synclock_lock()` on the glusterd big lock, POSIX `kill()`, and service pidfile conventions. It parallels older `glusterd_svc_stop()` behavior and is meant for daemon lifecycle code.

Risks: `snprintf()` truncation is not treated as an error when the return value exceeds the destination size; the function only checks negative return values. PID-file semantics can target stale or reused PIDs if `gf_is_service_running()` is fooled. Dropping and reacquiring the big lock during force-stop polling permits state changes by other management work.

Test signals: Stop already-stopped services, graceful stop, force kill after a process ignores SIGTERM, stale pidfile handling, pidfile unlinking, and lock-sensitive stop under concurrent service manager activity.
