# sources/distributed-fs/ceph-client/tools/thermal/tmon/tmon.c

## Purpose
`tmon.c` is the entry point and main runtime loop for the Thermal Monitor utility. It handles command-line options, privilege checks, syslog setup, optional daemonization, optional thermal data logging, initialization of sysfs/TUI/controller subsystems, periodic sampling, PID-controller invocation, and cleanup.

## Important APIs, Types, and Functions
The file defines global runtime knobs such as `ticktime`, `no_control`, `time_elapsed`, `target_temp_user`, `dialogue_on`, `tmon_exit`, `target_thermal_zone`, `ctrl_cdev`, `tmon_log`, `event_tid`, and `input_lock`. `usage()` and `version()` terminate after printing help/version text. `prepare_logging()` safely opens `/var/tmp/tmon.log`, rejects symlinks and files not owned by the current user, and writes configuration headers. `tmon_cleanup()` tears down the UI, thread, syslog, log file, control state, and thermal data. `main()` orchestrates the whole utility.

## Control Flow
`main()` requires effective root, parses options (`-c`, `-d`, `-t`, `-T`, `-l`, `-g`, `-z`, etc.), initializes `input_lock`, opens syslog, installs signal handlers, probes thermal sysfs, initializes curses windows, starts the TUI input thread, validates the target thermal zone, then loops until `tmon_exit`. Each loop sleeps `ticktime`, redraws title/sensor windows, samples sysfs data, updates data/cooling views when no dialog is active, increments elapsed time, calls `controller_handler()` using the selected zone temperature, stores PID output in `trec[0].pid_out_pct`, and redraws controls.

## State and Persistence
The process keeps global UI/control state and an optional log file. Daemon mode forks, creates a new session, changes to `/`, applies `umask`, disables TUI, sleeps, then closes standard descriptors. Cleanup always calls `set_ctrl_state(0)` to relax throttling. Signals set `tmon_exit` rather than performing full cleanup in the signal handler.

## Dependencies and Integration Points
`tmon.c` integrates with `sysfs.c` (`probe_thermal_sysfs()`, `update_thermal_data()`, `set_ctrl_state()`), `tui.c` (curses setup and drawing), and the controller implementation through `init_thermal_controller()` and `controller_handler()`. It depends on root access, pthreads, ncurses, syslog, signals, and the Linux thermal sysfs ABI.

## Risks and Edge Cases
`SIGKILL` is listed in the signal handler switch but cannot be caught. `strncpy(ctrl_cdev, optarg, CDEV_NAME_SIZE)` may leave no terminating NUL if the argument is exactly the buffer size. `tmon_cleanup()` exits with status 1 even for normal termination. The sampling loop calculates `target_tz_index` before later fallbacks but does not recompute the index after replacing `target_thermal_zone`, so an out-of-range initial target can leave a stale negative index for the controller path. Daemon mode still initializes curses functions after `disable_tui()` returns early, but cleanup also calls curses functions unconditionally after `set_ctrl_state()`, which can be sensitive if curses was never initialized.

## Test Signals
Exercise option parsing for root/non-root paths, daemon mode, invalid target temperature, sparse thermal zone IDs, target zone fallback, and log-file symlink/ownership checks. Runtime smoke tests should verify signal-triggered exit restores cooling state and that the controller loop calls update/display functions at the requested interval.
