# sources/distributed-fs/lizardfs/src/main/main.cc

Purpose: generic daemon entrypoint and lifecycle framework used by LizardFS services such as `mfsmaster`.

Important APIs/types/functions: `RunMode` command states; `initialize`, `initialize_early`, `initialize_late` run module tables; `set_syslog_ident`, `main_configure_debug_log`, `main_reload`; signal pipe handlers; `changeugid`; PAM session helpers; `FileLock` for process coordination; `makedaemon`; `createpath`; `makePidFile`; `main`.

Control flow: `main` parses flags and start/stop/restart/reload/test/kill/isalive commands, optionally daemonizes, loads config, configures logging, adjusts resource limits/PAM/nice/memory lock, drops privileges, changes to `DATA_PATH`, initializes module tables, handles lock-file semantics, then runs the event loop. Signal handlers write small control bytes to a pipe so the event loop can request exit/reload or gentle kill safely.

State and persistence: creates/removes `.APPNAME.lock` in the data directory, can write a pid file, changes process uid/gid, umask, syslog identity, resource limits, and working directory. It registers event-loop reload/destruct callbacks and closes PAM/session resources at exit.

Dependencies and integration: depends on config, event loop, logging, CRC initialization, module init tables from `init.h`, platform/PAM/systemd support, and `APPNAME`/path macros from build configuration.

Risks: lock handling mixes process control with locking and sends signals to owners. Daemonization closes inherited descriptors and uses a pipe to report startup failure. Recursive module initialization failures propagate only as status/logs. Some legacy comments and broad globals make behavior sensitive to compile-time macros.

Test signals: no direct unit tests in this subset; behavior is exercised by daemon startup/integration tests and service scripts.
