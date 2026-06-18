# sources/distributed-fs/glusterfs/glusterfsd/src/glusterfsd.c

Purpose: Main executable implementation for `glusterfsd`/`glusterfs`/`glusterd` modes. It parses command-line options, initializes global context and logging, configures FUSE mount options, daemonizes, installs signal handling, loads or fetches volume graphs, starts the I/O framework, and coordinates shutdown.

Important APIs and functions: `main()` is the process entry point. Major internal paths include `parse_opts()`, `parse_cmdline()`, `glusterfs_ctx_defaults_init()`, `logging_init()`, `create_fuse_mount()`, `daemonize()`, `glusterfs_signals_setup()`, `glusterfs_sigwaiter()`, `cleanup_and_exit()`, `volfile_init()`, `glusterfs_process_volfp()`, `glusterfs_volumes_init()`, `main_start()`, `main_terminate()`, `reincarnate()`, and `emancipate()`. Exported functions include `glusterfs_process_volfp()`, `cleanup_and_exit()`, and `emancipate()`.

Control flow: Startup checks memory-accounting flags, creates `glusterfs_ctx_t`, initializes globals/default pools, parses options, handles print-only modes, initializes logging, validates brick-mux mode, creates a FUSE xlator when a mount point is present, daemonizes, then runs `gf_io_run()` with `main_start`/`main_terminate`. `main_start()` initializes memory pools, async threading, OOM score, syncenv, timer wheel, and volumes. Volume initialization starts a local listener, connects to management for remote volfiles, or loads a local volfile. SIGHUP triggers volfile reload/refetch and graph notification; SIGTERM/SIGINT trigger cleanup.

State and persistence: Owns global `glusterfsd_ctx`. Initializes pools, event loop, client table, command-line lists, pidfile, log files, daemon pipe, signal thread, active graph, volfile checksums, and optional FUSE root xlator. Persistent effects include pidfile writes, log file/symlink handling, daemon fork status, FUSE mount setup, and OOM proc-file writes on Linux.

Dependencies and integration: Depends broadly on libglusterfs context, graph, xlator, dict, logging, event, timer, syncop, monitoring, daemon, and I/O APIs plus management functions from `glusterfsd-mgmt.c`. Compile-time macros from `Makefile.am` provide default directories.

Risks: Command-line parsing has many interacting options and precedence rules. Signal cleanup intentionally exits while holding `cleanup_lock`, which is deliberate but fragile. Daemon parent/child synchronization depends on `emancipate()`. Graph reload paths must avoid loading FUSE translators from volfiles and must maintain active graph consistency. Manual allocation and ownership of option strings, xlator options, and FILE pointers require careful cleanup.

Test signals: Needs CLI parsing tests, daemonization/pidfile tests, signal/reload integration tests, local and remote volfile graph tests, FUSE option propagation tests, and process-mode tests. In this subset, build linkage and daemon integration suites are the main signals.
