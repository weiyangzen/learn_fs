# sources/distributed-fs/ceph-client/tools/verification/rv/src/rv.c

Purpose: `rv.c` is the top-level CLI for the runtime verification tool.

Important functions: `stop_rv()` sets a process-global stop flag on SIGINT/SIGTERM. `should_stop()` exposes that flag. `rv_list()` parses `rv list [-h] [container]` and calls `ikm_list_monitors()`. `rv_mon()` validates `rv mon monitor [options]`, calls `ikm_run_monitor()`, and reports missing monitors. `usage()` prints global help. `main()` enforces root, dispatches commands, and installs signal handlers for monitor execution.

Control flow and integration: `main()` dispatches only `list` and `mon`. Subcommands exit directly. `rv_mon()` is written to support multiple monitor implementations by accumulating run results, currently only in-kernel monitors.

State and dependencies: state is the static `stop_session` flag. Dependencies include root privileges, in-kernel monitor support, and generated `VERSION` from the Makefile. Risks include subcommands exiting rather than returning, negative return from `ikm_run_monitor()` still contributing to `run` truthiness in some paths, and no non-root degraded mode. Test signals are help text, root check, monitor-not-found errors, and signal-driven shutdown.
