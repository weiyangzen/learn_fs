<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/harddog_user.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/harddog_user.c

Purpose: starts and communicates with the host-side `uml_watchdog` helper process for the UML watchdog device.

Important APIs/types/functions: `struct dog_data` carries pipe FDs into `pre_exec()`. Public functions are `start_watchdog()`, `stop_watchdog()`, and `ping_watchdog()`.

Control flow: `start_watchdog()` creates two pipes, wires helper stdin/stdout/stderr in `pre_exec()`, chooses either `-mconsole <socket>` or `-pid <uml-pid>` arguments, runs `/usr/bin/uml_watchdog`, closes unused pipe ends, waits for an initial byte from the helper, and returns input/output FDs to the kernel side. `ping_watchdog()` writes a newline keepalive. `stop_watchdog()` closes both FDs.

State and persistence: only pipe FDs and helper process lifetime are involved. No persistent data is stored.

Dependencies and integration points: depends on UML `os_pipe()`, `run_helper()`, `helper_wait()`, `os_getpid()`, and host executable `/usr/bin/uml_watchdog`.

Risks: helper path is hard-coded. The PID mode comment notes `os_getpid()` is not SMP-correct. Startup synchronization treats EOF and read errors as fatal. File descriptor wiring must avoid leaking unused pipe ends.

Test signals: run with helper installed/missing, with and without mconsole socket, validate startup byte handshake, send repeated keepalives, terminate helper early, and confirm pipe cleanup on failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/harddog_user.c -->
