# sources/distributed-fs/ceph-client/tools/perf/builtin-daemon.c

Purpose: implements `perf daemon`, a config-driven supervisor for long-running `perf record` sessions. It can start a daemon, list sessions, send `SIGUSR2`, stop the daemon, and ping session control FIFOs.

Important APIs, types, and functions: `struct daemon_session` stores session name, run arguments, base directory, control FIFO path, child pid, state, and start time. `struct daemon` stores config/base paths, sessions, output, perf executable path, signal fd, and daemon start time. Config parsing uses `session_config()`, `server_config()`, and `client_config()`. Session lifecycle uses `daemon_session__run()`, `daemon_session__control()`, `daemon_session__kill()`, `daemon__reconfig()`, and cleanup helpers. IPC uses `setup_server_socket()`, `setup_client_socket()`, `handle_server_socket()`, and command handlers for list, signal, stop, and ping. `__cmd_start()` runs the server loop; `send_cmd()` implements clients.

Control flow: start resolves config, loads sessions, optionally daemonizes, locks `BASE/lock`, creates Unix control socket, watches config directory with inotify, blocks SIGCHLD into signalfd, and polls socket/config/signal fds. Reconfiguration marks existing sessions for kill, reloads config, starts changed sessions as `perf record --control=fifo:control,ack`, and removes deleted sessions. Client commands load base config, connect to `BASE/control`, write a fixed-size `union cmd`, and stream the response.

State and persistence: persistent runtime state lives under daemon base: `lock`, daemon `output`, Unix `control` socket, and per-session directories with `output`, `control`, and `ack` FIFOs. It reads perf config files and writes session output logs. Child `perf record` processes produce their normal data outputs in session directories.

Dependencies and integration points: uses perf config APIs, `perf_exe()`, `cmd_record` via exec, fdarray polling, inotify, Unix sockets, signalfd, fork/setsid, FIFOs, lock files, and signal handling.

Risks: command IPC sends raw `union cmd`, so client/server ABI must match. `daemon_session__run()` builds a command string then `argv_split()`s it, making quoting in config `run` values important. Several child error paths return instead of `_exit()`, though final exec failure exits. Base path length is limited by Unix socket path size. Reconfig kills and restarts changed sessions, so config edits can interrupt recording.

Test signals: start foreground and background with temporary base/config, list normal and CSV formats, ping all and missing sessions, signal one/all sessions, stop daemon, edit config to add/change/remove sessions, simulate child exit, verify lock exclusion, and inspect FIFO ack timeout behavior.
