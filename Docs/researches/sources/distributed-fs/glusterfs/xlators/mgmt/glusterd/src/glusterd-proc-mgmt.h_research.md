# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-proc-mgmt.h

Purpose: Declares the generic glusterd daemon process descriptor and lifecycle helper interface.

Important APIs and types: `enum proc_flags` names start/stop modes: `PROC_NONE`, `PROC_START`, `PROC_START_NO_WAIT`, `PROC_STOP`, and `PROC_STOP_FORCE`. `struct glusterd_proc_` stores process name, pidfile, log paths, volfile path/server, and volfile id. Declared functions are `glusterd_proc_init()`, `glusterd_proc_stop()`, and `glusterd_proc_is_running()`.

Control flow: The header contains no executable control flow. Its flags drive process lifecycle decisions in implementation code.

State and persistence: The struct mirrors runtime and filesystem paths for a managed process; the persistent artifact is the pidfile referenced by `pidfile`.

Dependencies and integration points: Requires standard constants such as `NAME_MAX` and `PATH_MAX` to be visible from including context. It integrates with glusterd service management and process lifecycle helpers.

Risks: The header does not declare `glusterd_proc_get_pid()` even though the C file defines it, limiting external use or risking missing-prototype warnings depending on build flags. Fixed-size char buffers make truncation behavior an integration concern.

Test signals: Build coverage for process-management callers and lifecycle tests using initialized `glusterd_proc_t` objects validate this interface.
